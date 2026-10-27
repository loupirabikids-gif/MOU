"""MOU vert : test continu du rig, rendu SVG/Python/FFmpeg.

Ce test de jeu n'est pas un épisode ni une validation auprès d'un public.
Les mouvements et les sons sont calculés localement, sans génération vidéo.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import argparse
import html
import json
import math
import subprocess
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from mou_rig import character_fragment, PALETTE

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output'
FRAMES = ROOT / 'work' / 'frames'
FPS = 24
DURATION = 9
WIDTH, HEIGHT = 576, 1024
BG = '#F0E9FB'
INK = '#2B0A24'


def clamp(x, lo=0, hi=1):
    return max(lo, min(hi, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


NEUTRAL = dict(arm_hips=0., arm_clasp=0., eye_open_l=1., eye_open_r=1.,
               pupil_x=0., pupil_y=0., brow_l=0., brow_r=0., brow_raise=0.,
               smile=0., mouth_open=0., laugh=0., lift_l=0., lift_r=0.)


def state(**changes):
    return dict(NEUTRAL, **changes)


KEYS = [
    (0.0, state()),
    (0.35, state()),
    (0.75, state(pupil_x=-.8, pupil_y=-.15)),
    (1.05, state(pupil_x=-.8, pupil_y=-.15)),
    (1.45, state(pupil_x=.8, pupil_y=-.15)),
    (1.75, state(pupil_x=.8, pupil_y=-.15)),
    (2.00, state()),
    (2.70, state(arm_hips=1., eye_open_l=.52, eye_open_r=.52,
                 pupil_x=-.8, brow_l=.15, brow_r=-.8, brow_raise=.2, smile=.8)),
    (3.55, state(arm_hips=1., eye_open_l=.52, eye_open_r=.52,
                 pupil_x=-.8, brow_l=.15, brow_r=-.8, brow_raise=.2, smile=.8)),
    (4.30, state(arm_hips=.85, eye_open_l=.88, eye_open_r=.88,
                 brow_l=-1., brow_r=-1., brow_raise=-.5, smile=-1.)),
    (5.35, state(arm_hips=.85, eye_open_l=.88, eye_open_r=.88,
                 brow_l=-1., brow_r=-1., brow_raise=-.5, smile=-1.)),
    (6.15, state(arm_clasp=1., eye_open_l=.08, eye_open_r=.08,
                 brow_raise=.7, smile=1., mouth_open=1., laugh=1., lift_r=10.)),
    (7.90, state(arm_clasp=1., eye_open_l=.08, eye_open_r=.08,
                 brow_raise=.7, smile=1., mouth_open=1., laugh=1., lift_r=10.)),
    (8.65, state()),
    (9.00, state()),
]


def pose_at(t):
    for (ta, a), (tb, b) in zip(KEYS, KEYS[1:]):
        if ta <= t <= tb:
            u = smooth((t - ta) / (tb - ta))
            p = {k: a[k] + (b[k] - a[k]) * u for k in NEUTRAL}
            break
    else:
        p = dict(KEYS[0 if t < 0 else -1][1])
    # Un vrai clignement commun aux deux yeux, sans changement de modèle.
    blink = 1 - .995 * math.exp(-((t - 1.90) / .065) ** 2)
    p['eye_open_l'] *= blink
    p['eye_open_r'] *= blink
    # Petits à-coups volontairement localisés dans le rire.
    chuckle = max(0., math.sin((t - 6.12) * math.tau * 2.5)) * p['laugh']
    p['lift_r'] += chuckle * 3
    return p, chuckle


def label_at(t):
    if t < 2.0:
        return 'REGARD ET CLIGNEMENT'
    if t < 3.85:
        return 'FRIME'
    if t < 5.70:
        return 'COLÈRE'
    if t < 8.30:
        return 'FOU RIRE'
    return 'RETOUR AU NEUTRE'


def svg_at(t, title=True):
    p, chuckle = pose_at(t)
    sx, sy = 1 + .024 * chuckle, 1 - .020 * chuckle
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
              f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
              f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>']
    if title:
        pieces += [f'<text x="288" y="116" text-anchor="middle" '
                   f'font-family="DejaVu Sans,sans-serif" font-weight="bold" '
                   f'font-size="54" fill="{INK}">MOU</text>',
                   f'<text x="288" y="155" text-anchor="middle" '
                   f'font-family="DejaVu Sans,sans-serif" font-size="15" '
                   f'letter-spacing="2" fill="{INK}">TEST DU MODÈLE ARTICULÉ</text>',
                   f'<text x="288" y="924" text-anchor="middle" '
                   f'font-family="DejaVu Sans,sans-serif" font-size="22" '
                   f'font-weight="bold" fill="{INK}">{html.escape(label_at(t))}</text>']
    pieces += ['<ellipse cx="288" cy="814" rx="175" ry="15" fill="#D4C3E8"/>',
               f'<g id="character" transform="translate(288 814) '
               f'scale({1.35*sx:.6f} {1.35*sy:.6f}) translate(-200 -450)">',
               character_fragment(p, uid='mou'), '</g>', '</svg>']
    return ''.join(pieces)


def render(i):
    cairosvg.svg2png(bytestring=svg_at(i/FPS).encode(),
                    write_to=str(FRAMES / f'{i:04d}.png'))


def audit_structure():
    max_change = 0.
    previous = None
    for i in range(FPS * DURATION):
        p, _ = pose_at(i / FPS)
        root = ET.fromstring(svg_at(i / FPS))
        ids = [n.attrib['id'] for n in root.iter() if 'id' in n.attrib]
        assert len(ids) == len(set(ids)), f'ID doublé à {i/FPS:.3f}s'
        hands = [n for n in root.iter() if n.attrib.get('data-part') == 'hand']
        assert len(hands) == 2, f'{len(hands)} mains à {i/FPS:.3f}s'
        assert {n.attrib.get('data-side') for n in hands} == {'left', 'right'}
        assert 'arm-left' in ids and 'arm-right' in ids
        assert all(math.isfinite(v) for v in p.values())
        if previous:
            max_change = max(max_change, max(abs(p[k]-previous[k]) for k in NEUTRAL
                                           if not k.startswith('lift_')))
        previous = p
    same_neutral = svg_at(0, title=False) == svg_at((FPS*DURATION-1)/FPS, title=False)
    assert same_neutral, 'Le personnage ne retrouve pas son neutre de départ.'
    return dict(frames=FPS*DURATION, duration_seconds=DURATION,
                fps=FPS, two_hands_each_frame=True, two_arm_groups_each_frame=True,
                unique_svg_ids=True, finite_parameters=True,
                returns_to_same_neutral=same_neutral,
                max_normalized_parameter_step=round(max_change, 4))


def make_sound():
    sr = 48000
    sound = np.zeros(sr*DURATION)
    rng = np.random.default_rng(2710)
    def add(start, length, low, high, volume=.04, noise=0.):
        n = int(length * sr)
        phase = np.cumsum(np.linspace(low, high, n)) / sr
        env = np.sin(np.linspace(0, math.pi, n)) ** 2
        signal = (np.sin(phase*math.tau) + noise*rng.normal(size=n)) * env * volume
        j = int(start*sr)
        stop = min(j+n, len(sound))
        sound[j:stop] += signal[:stop-j]
    add(1.89, .08, 430, 300, .027)
    add(2.67, .12, 500, 760, .04)
    add(4.22, .16, 130, 70, .045, .12)
    for j, t in enumerate([6.24, 6.64, 7.04, 7.44, 7.84]):
        add(t, .12, 250+j*8, 410+j*6, .027)
    add(8.6, .10, 250, 180, .025)
    assert np.max(np.abs(sound)) < .9
    with wave.open(str(OUT/'sons_du_test.wav'), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((sound*32767).astype('<i2').tobytes())


def make_board():
    samples = [('NEUTRE', .15), ('REGARD', 1.45), ('FRIME', 3.1),
               ('COLÈRE', 4.8), ('FOU RIRE', 6.9), ('RETOUR', 8.85)]
    board = Image.new('RGB', (1200, 1180), BG)
    d = ImageDraw.Draw(board)
    local_font = ROOT/'fonts'/'DejaVuSans-Bold.ttf'
    system_font = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    font = ImageFont.truetype(str(local_font if local_font.exists() else system_font), 22)
    for j, (label, t) in enumerate(samples):
        im = Image.open(FRAMES/f'{round(t*FPS):04d}.png').convert('RGB')
        im = im.crop((20, 310, 556, 842))
        im.thumbnail((365, 490))
        x = (j%3)*400 + (400-im.width)//2
        y = (j//3)*590 + 15
        board.paste(im, (x, y))
        d.text(((j%3)*400+200, (j//3)*590+515), label, font=font, fill=INK, anchor='mm')
        d.text(((j%3)*400+200, (j//3)*590+551), f'{t:.2f} s', font=font, fill=INK, anchor='mm')
    board.save(OUT/'MOU_controle_des_poses.png')
    for label, t in samples:
        (OUT/f'MOU_{label.lower()}.svg').write_text(svg_at(t, title=False), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true')
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True); FRAMES.mkdir(parents=True, exist_ok=True)
    report = audit_structure()
    if args.preview:
        for t in [.15, 1.45, 3.1, 4.8, 6.9, 8.85]:
            render(round(t*FPS))
        make_board()
        print(json.dumps(report))
        return
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(render, range(FPS*DURATION)))
    make_sound()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS),
                    '-i', str(FRAMES/'%04d.png'), '-i', str(OUT/'sons_du_test.wav'),
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
                    '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart',
                    '-shortest', str(OUT/'MOU_verification_9_secondes.mp4')], check=True)
    make_board()
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
                      '-show_entries', 'stream=codec_type,width,height:format=duration',
                      '-of', 'json', str(OUT/'MOU_verification_9_secondes.mp4')]))
    video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert (video['width'], video['height']) == (WIDTH, HEIGHT)
    assert abs(float(probe['format']['duration']) - DURATION) < .05
    assert any(s['codec_type'] == 'audio' for s in probe['streams'])
    report['export'] = probe
    (OUT/'controles_automatiques.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
