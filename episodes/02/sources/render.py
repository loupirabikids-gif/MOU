"""Le torchon — scène SVG locale, moteur CairoSVG/FFmpeg réutilisé.

Le module d'animation fournit ensemble MOU et le tissu, dans le bon ordre
des couches. Aucun dessin ni média des épisodes précédents n'est modifié.
"""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import textwrap
import xml.etree.ElementTree as ET

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animation import pose_at, motion_at, character_at, contact_at, intention_at
from mou_rig import PALETTE, _arm
import cairosvg
from PIL import Image, ImageDraw, ImageFont

TIMELINE = json.loads((EP/'chronologie.json').read_text(encoding='utf-8'))
REVISION = int(TIMELINE['revision'])
FPS = int(TIMELINE['fps'])
DURATION = float(TIMELINE['duree_secondes'])
NFRAMES = round(FPS*DURATION)
W, H = int(TIMELINE['width']), int(TIMELINE['height'])
FILE_STEM = TIMELINE['file_stem']
INK, BG = PALETTE['outline'], PALETTE['background']
SAMPLES = [0., 1.5, 2.5, 5., 6.5, 7.25, 7.5, 7.75, 8.25,
           9.25, 9.75, 10.5, 11.25, 11.5, (NFRAMES-1)/FPS]
CACHE_VERSION = 'svg-atomic-copy-torchon-v1'
CHAR_X, CHAR_FEET, CHAR_SCALE = 540., 1600., 3.0


def isolated(fragment, prefix):
    """Rename IDs and references together, without cascading replacements."""
    ids = re.findall(r'\bid="([^"]+)"', fragment)
    mapping = {old: f'{prefix}-{old}' for old in ids}
    fragment = re.sub(r'\bid="([^"]+)"',
                      lambda m: f'id="{mapping[m[1]]}"', fragment)
    return re.sub(r'url\(#([^)]*)\)',
                  lambda m: f'url(#{mapping.get(m[1],m[1])})', fragment)


def puppet(t, prefix='main'):
    return isolated(character_at(pose_at(t), uid=prefix), prefix)


def scene_character(t, prefix='main'):
    m = motion_at(t)
    return (f'<g id="{prefix}-scene-character" transform="'
            f'translate({CHAR_X+m.get("dx",0.):.6f} {CHAR_FEET+m.get("dy",0.):.6f}) '
            f'scale({CHAR_SCALE*m.get("sx",1.):.6f} {CHAR_SCALE*m.get("sy",1.):.6f}) '
            f'translate(-200 -450)">{puppet(t,prefix)}</g>')


def svg_at(t):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="{BG}"/>'
            f'<text x="78" y="174" font-family="DejaVu Sans" font-weight="bold" '
            f'font-size="76" letter-spacing="-5" fill="{INK}">MOU</text>'
            '<text x="82" y="219" font-family="DejaVu Sans" font-size="22" '
            'letter-spacing="3" fill="#7A5D80">02 / LE TORCHON</text>'
            '<path d="M90 1645 V875 C90 530 310 415 540 415 '
            'C770 415 990 530 990 875 V1645 Z" fill="#E8DBF4"/>'
            '<ellipse cx="540" cy="1650" rx="890" ry="125" fill="#E3D5EF"/>'
            '<ellipse cx="540" cy="1615" rx="355" ry="25" fill="#CCB7E0"/>'
            + scene_character(t) + '</svg>')


def render_job(args):
    i, scale, out = args
    data = svg_at(i/FPS).encode()
    key = hashlib.sha256(CACHE_VERSION.encode()+data+str(scale).encode()).hexdigest()
    cache = EP/'cache'/f'{key}.png'
    dest = Path(out)/f'{i:04d}.png'
    if not cache.exists():
        raw = cairosvg.svg2png(bytestring=data, output_width=round(W*scale),
                              output_height=round(H*scale))
        tmp = cache.with_name(f'{key}.{os.getpid()}.tmp')
        tmp.write_bytes(raw)
        tmp.replace(cache)
    cached = cache.read_bytes()
    if not dest.exists() or dest.read_bytes() != cached:
        tmp = dest.with_name(f'.{dest.name}.{os.getpid()}.tmp')
        tmp.write_bytes(cached)
        tmp.replace(dest)
    return i


def board(frames, out):
    b = Image.new('RGB', (1500, 1800), BG)
    d = ImageDraw.Draw(b)
    font = ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'), 13)
    for j,t in enumerate(SAMPLES):
        t = round(t*FPS)/FPS
        im = Image.open(Path(frames)/f'{round(t*FPS):04d}.png').convert('RGB')
        im.thumbnail((294, 523))
        x = (j%5)*300+(300-im.width)//2
        y = (j//5)*600
        b.paste(im, (x,y))
        d.text(((j%5)*300+12,y+530), f'{t:.3f} s', font=font, fill=INK)
        for k,line in enumerate(textwrap.wrap(intention_at(t), width=32)[:2]):
            d.text(((j%5)*300+12,y+551+17*k), line, font=font, fill=INK)
    b.save(out)


def framing_bounds():
    """Measure the entire puppet+tissue beyond the output edges to detect cuts."""
    bounds = {}
    for t in SAMPLES:
        t = round(t*FPS)/FPS
        vector = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W+400}" '
                  f'height="{H+400}" viewBox="-200 -200 {W+400} {H+400}">'
                  + scene_character(t, 'bounds') + '</svg>')
        im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=vector.encode()))).convert('RGBA')
        bbox = im.getchannel('A').getbbox()
        assert bbox is not None
        box = [v-200 for v in bbox]
        assert 0 < box[0] < box[2] < W and 250 < box[1] < box[3] < H, (t,'clipped puppet or cloth',box)
        bounds[str(round(t,6))] = box
    return bounds


def audit():
    rig_hash = hashlib.sha256((ROOT/'mou_rig.py').read_bytes()).hexdigest()
    assert rig_hash == '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    for i in range(NFRAMES):
        t = i/FPS
        p = pose_at(t)
        avatar = character_at(p, uid='original-arms')
        for side in ('left','right'):
            assert _arm(side,p['arm_hips'],p['arm_clasp']) in avatar, (t,'original arm path changed')
        data = svg_at(t)
        root = ET.fromstring(data)
        ids = [e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids) == len(set(ids)), (t,'duplicate IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',data)), (t,'missing clip reference')
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter()) == 2, (t,'hand count')
        assert all(math.isfinite(v) for v in p.values() if isinstance(v,(int,float))), (t,'nonfinite pose')
        assert 0 <= p['lift_l'] <= 20 and 0 <= p['lift_r'] <= 20
        assert 'data:image' not in data and '<image ' not in data, (t,'unexpected raster input')
    final_start = float(TIMELINE['final_hold']['start'])
    last = svg_at(final_start)
    assert all(svg_at(i/FPS)==last for i in range(round(final_start*FPS),NFRAMES)), 'final hold moves'
    contacts = {str(round(t,6)):contact_at(t) for t in SAMPLES}
    json.dumps(contacts,allow_nan=False)
    report = {'revision':REVISION,'file_stem':FILE_STEM,
              'original_rig_sha256':rig_hash,'original_rig_unchanged':True,
              'original_arm_paths_exact_all_frames':True,
              'frames':NFRAMES,'fps':FPS,'duration':DURATION,
              'unique_ids_all_frames':True,'two_hands_in_model_all_frames':True,
              'all_clip_references_resolved':True,'entirely_vector_scene':True,
              'scene_character_transform':{'x':CHAR_X,'feet_y':CHAR_FEET,'scale':CHAR_SCALE},
              'bounds_final_resolution':framing_bounds(),
              'contact_samples':contacts,
              'final_pose_hold_seconds':DURATION-final_start,
              'limits':'Structure and exact source paths verified; contact geometry measurements are provided by animation and visual readability requires review of rendered images.'}
    (EP/'controle/audit_structure.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', action='store_true')
    ap.add_argument('--stills', action='store_true')
    ap.add_argument('--workers', type=int, default=3)
    args = ap.parse_args()
    (EP/'cache').mkdir(exist_ok=True)
    (EP/'controle').mkdir(exist_ok=True)
    report = audit()
    scale = .5 if args.preview else 1.
    frames = EP/'frames'/('preview' if args.preview else 'final')
    frames.mkdir(parents=True,exist_ok=True)
    indices = sorted({round(t*FPS) for t in SAMPLES}) if args.stills else range(NFRAMES)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(render_job,[(i,scale,str(frames)) for i in indices]))
    for i in indices:
        key = hashlib.sha256(CACHE_VERSION.encode()+svg_at(i/FPS).encode()+str(scale).encode()).hexdigest()
        dest = frames/f'{i:04d}.png'
        assert dest.stat().st_nlink == 1, (i,'shared frame inode')
        assert dest.read_bytes() == (EP/'cache'/f'{key}.png').read_bytes(), (i,'cache mismatch')
    board(frames,EP/'controle'/('planche_preview.png' if args.preview else 'planche_finale.png'))
    if args.stills:
        print(json.dumps({'stills':len(indices),'frames_audited':NFRAMES,'revision':REVISION},ensure_ascii=False))
        return
    tag = 'premier_montage' if args.preview else FILE_STEM
    mute, full = EP/f'{tag}_muet.mp4', EP/f'{tag}.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(frames/'%04d.png'),
                    '-frames:v',str(NFRAMES),'-c:v','libx264','-threads','3','-preset','medium',
                    '-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mute)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(mute),'-i',str(EP/'sons/mix.wav'),
                    '-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k',
                    '-t',str(DURATION),'-movflags','+faststart',str(full)],check=True)
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
                                              '-show_format','-of','json',str(full)]))
    (EP/'controle'/f'probe_{tag}.json').write_text(json.dumps(probe,indent=2)+'\n')
    print(json.dumps({'file':str(full),'revision':REVISION,'frames':NFRAMES,
                      'dimensions':[round(W*scale),round(H*scale)]},ensure_ascii=False))


if __name__ == '__main__':
    main()
