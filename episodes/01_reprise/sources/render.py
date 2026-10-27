"""Le retardateur — nouvelle scène SVG, moteur CairoSVG/FFmpeg réutilisé.

Les fichiers sont résolus depuis ce module. Aucun média de episodes/01 n'est
lu ou réécrit. Le personnage animé et le cliché appellent le même rig adapté.
"""
from pathlib import Path
import argparse
import base64
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

ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from animation import pose_at, motion_at, character_at, intention_at, deformation_at
from mou_rig import PALETTE
import cairosvg
from PIL import Image, ImageDraw, ImageFont

TIMELINE = json.loads((EP/'chronologie.json').read_text())
REVISION = int(TIMELINE['revision'])
FPS = int(TIMELINE['fps'])
DURATION = float(TIMELINE['duree_secondes'])
NFRAMES = round(FPS*DURATION)
W, H = TIMELINE['width'], TIMELINE['height']
FLASH = float(TIMELINE['flash_time'])
FILE_STEM = TIMELINE['file_stem']
PHOTO_START = float(TIMELINE['photo_hold']['start'])
PHOTO_END = float(TIMELINE['photo_hold']['end'])
INK = PALETTE['outline']
BG = PALETTE['background']
SAMPLES = [0, .9, 2.25, 4.5, 5.5, 143/FPS, FLASH, 147/FPS,
           7.25, 8.75, 9.75, 10.75, 279/FPS, 289/FPS, 12.75]
PHOTO = None
CACHE_VERSION = 'svg-atomic-copy-retardateur-v1'
CHAR_X, CHAR_FEET, CHAR_SCALE = 540., 1540., 2.85


def smooth(x):
    x = max(0., min(1., float(x)))
    return x*x*(3-2*x)


def isolated(fragment, prefix):
    """Rename IDs and references together, without cascading replacements."""
    ids = re.findall(r'\bid="([^"]+)"', fragment)
    mapping = {old: f'{prefix}-{old}' for old in ids}
    fragment = re.sub(r'\bid="([^"]+)"',
                      lambda m: f'id="{mapping[m[1]]}"', fragment)
    return re.sub(r'url\(#([^)]*)\)',
                  lambda m: f'url(#{mapping.get(m[1],m[1])})', fragment)


def puppet(t, prefix):
    return isolated(character_at(pose_at(t), uid=prefix), prefix)


def photo_svg():
    """Fit the exact captured state, without cropping bumps or mittens."""
    avatar = puppet(FLASH, 'photo')
    measurement = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="1240" '
                   f'viewBox="-80 -60 560 620">{avatar}</svg>')
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=measurement.encode()))).convert('RGBA')
    bbox = im.getchannel('A').getbbox()
    assert bbox is not None
    left, top, right, bottom = [bbox[0]/2-80, bbox[1]/2-60,
                                bbox[2]/2-80, bbox[3]/2-60]
    scale = min(432/(right-left), 610/(bottom-top))
    cx, cy = (left+right)/2, (top+bottom)/2
    shadow_y = 372+(bottom-cy)*scale+9
    # Conserver le cadrage précédent lorsque seuls les bras sont rétablis.
    framing = TIMELINE.get('photo_framing')
    if framing:
        scale, cx, cy, shadow_y = (float(framing[k]) for k in ('scale','cx','cy','shadow_y'))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="744" '
            f'viewBox="0 0 480 744"><rect width="480" height="744" fill="#E1D1F2"/>'
            f'<ellipse cx="240" cy="{shadow_y:.5f}" rx="205" ry="12" fill="#CBB4E0"/>'
            f'<g transform="translate(240 372) scale({scale:.8f}) '
            f'translate({-cx:.5f} {-cy:.5f})">{avatar}</g></svg>')


def prepare_photo():
    global PHOTO
    vector = photo_svg()
    # The result is shown at 812px wide in the final frame. Render at 2x its
    # authored size so this insert never magnifies a lower-resolution raster.
    data = cairosvg.svg2png(bytestring=vector.encode(), output_width=960, output_height=1488)
    (EP/'sources/photo_capturee.svg').write_text(vector, encoding='utf-8')
    (EP/'sources/photo_capturee.png').write_bytes(data)
    PHOTO = base64.b64encode(data).decode()
    return PHOTO


def tap_geometry(t):
    """One cropped continuous arm, reaching the shutter at .90 seconds."""
    offset = 260*(1-smooth((t-.08)/.82))
    return [(1130+offset, 2080+offset), (1130+offset, 1770+offset),
            (780+offset, 1495+offset), (614+offset, 1464+offset)]


def tap_arm(t):
    from mou_rig import _cubic, _tangent
    controls = tap_geometry(t)
    left, right = [], []
    for i in range(65):
        u = i/64
        x, y = _cubic(controls, u)
        tx, ty = _tangent(controls, u)
        radius = 42+33*smooth((u-.75)/.25)
        left.append((x-ty*radius, y+tx*radius))
        right.append((x+ty*radius, y-tx*radius))
    ex, ey = controls[-1]
    tx, ty = _tangent(controls, 1.)
    tip = [(ex+(-ty*math.cos(math.pi*j/24)+tx*math.sin(math.pi*j/24))*75,
            ey+(tx*math.cos(math.pi*j/24)+ty*math.sin(math.pi*j/24))*75)
           for j in range(1, 25)]
    boundary = left+tip+list(reversed(right[:-1]))
    d = 'M'+' L'.join(f'{x:.3f} {y:.3f}' for x,y in boundary)
    return (f'<g id="tap-arm"><path data-part="hand" data-side="left" '
            f'd="{d} Z" fill="{PALETTE["skin"]}"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="20.8" '
            'stroke-linejoin="round" stroke-linecap="round"/></g>')


def phone_insert(result=False, t=0):
    # Exactly the same phone and integrated stand in opening and result insert.
    a = [f'<g id="phone"><ellipse cx="540" cy="1798" rx="260" ry="18" fill="#CCB7E0"/>',
         f'<path d="M505 1670 V1760 H408 Q390 1760 390 1784 H690 '
         f'Q690 1760 672 1760 H575 V1670 Z" fill="#77627F" stroke="{INK}" '
         'stroke-width="12" stroke-linejoin="round"/>',
         f'<rect x="190" y="220" width="700" height="1480" rx="90" fill="{INK}"/>',
         '<rect x="209" y="239" width="662" height="1442" rx="72" fill="#644565"/>',
         '<rect x="226" y="325" width="628" height="1255" rx="30" fill="#E1D1F2"/>',
         '<circle cx="540" cy="278" r="16" fill="#B9A4CC"/>',
         '<circle cx="540" cy="278" r="7" fill="#251029"/>']
    if result:
        assert PHOTO is not None, 'prepare_photo must precede result composition'
        a += ['<rect x="242" y="378" width="596" height="940" rx="8" fill="#FFFDFD"/>',
              f'<image x="250" y="390" width="580" height="899" '
              f'href="data:image/png;base64,{PHOTO}"/>',
              '<rect x="491" y="1457" width="98" height="64" rx="10" fill="#FFFDFD"/>',
              f'<path d="M503 1507 L528 1481 L552 1502 L572 1489" '
              f'fill="none" stroke="{INK}" stroke-width="6"/>']
    else:
        a += [f'<path d="M415 605 H475 L493 580 H573 L594 605 H665 V770 H415 Z" '
              f'fill="none" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>',
              f'<circle cx="540" cy="690" r="50" fill="none" stroke="{INK}" stroke-width="14"/>',
              f'<circle cx="540" cy="1030" r="107" fill="none" stroke="{INK}" stroke-width="10"/>',
              f'<path d="M521 898 H559 M540 898 V919 M611 944 L627 928" '
              f'fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>',
              f'<text x="540" y="1081" text-anchor="middle" fill="{INK}" '
              'font-family="DejaVu Sans" font-weight="bold" font-size="142">5</text>',
              '<circle cx="540" cy="1450" r="92" fill="none" stroke="#FFFDFD" stroke-width="10"/>',
              f'<circle cx="540" cy="1450" r="72" '
              f'fill="{PALETTE["skin"] if t>=.90 else "#FFFDFD"}"/>',
              tap_arm(t)]
    return ''.join(a)+'</g>'


def vanity_glint(t):
    # Brief non-anatomical sparkle synchronized to the 2.20s audio accent.
    u = (t-2.10)/.20
    if not 0 < u < 1:
        return ''
    k = math.sin(math.pi*u)**.65
    return (f'<g id="vanity-glint" transform="translate(925 620) scale({k:.5f})">'
            f'<path d="M0 -27 Q4 -4 27 0 Q4 4 0 27 Q-4 4 -27 0 Q-4 -4 0 -27Z" '
            f'fill="#FFF8CF" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/></g>')


def svg_at(t):
    a = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{BG}"/>']
    if not PHOTO_START <= t < PHOTO_END:
        a += [f'<text x="78" y="174" font-family="DejaVu Sans" font-weight="bold" '
              f'font-size="76" letter-spacing="-5" fill="{INK}">MOU</text>',
              '<text x="82" y="219" font-family="DejaVu Sans" font-size="22" '
              'letter-spacing="3" fill="#7A5D80">01 / LE RETARDATEUR</text>']
    if t < 1.:
        a.append(phone_insert(False, t))
    elif PHOTO_START <= t < PHOTO_END:
        a.append('<g id="result-closeup" transform="translate(540 960) scale(1.4) '
                 'translate(-540 -960)">'+phone_insert(True, t)+'</g>')
    else:
        m = motion_at(t)
        a += ['<path d="M110 1600 V880 C110 520 320 410 540 410 '
              'C760 410 970 520 970 880 V1600 Z" fill="#E8DBF4"/>',
              '<ellipse cx="540" cy="1580" rx="880" ry="125" fill="#E3D5EF"/>',
              '<ellipse cx="540" cy="1548" rx="352" ry="25" fill="#CCB7E0"/>',
              f'<g id="character" transform="translate({CHAR_X+m.get("dx",0):.5f} '
              f'{CHAR_FEET+m.get("dy",0):.5f}) scale({CHAR_SCALE*m.get("sx",1):.6f} '
              f'{CHAR_SCALE*m.get("sy",1):.6f}) translate(-200 -450)">{puppet(t,"main")}</g>',
              vanity_glint(t)]
        if t < FLASH:
            a.append('<path d="M92 438 V310 H220 M860 310 H988 V438 '
                     'M92 1530 V1658 H220 M860 1658 H988 V1530" fill="none" '
                     'stroke="#AA8DBF" stroke-width="8" stroke-linecap="round"/>')
            digit = next((str(e['number']) for e in TIMELINE['countdown']
                          if e['time'] <= t < e['time']+1), None)
            if digit:
                a += [f'<circle cx="885" cy="379" r="87" fill="{INK}"/>',
                      f'<text x="885" y="418" text-anchor="middle" fill="#FFFDFD" '
                      f'font-family="DejaVu Sans" font-weight="bold" font-size="110">{digit}</text>']
    if FLASH <= t < FLASH+3/FPS:
        op = [.94, .65, .22][min(2, round((t-FLASH)*FPS))]
        a.append(f'<rect id="flash" width="{W}" height="{H}" fill="#FFFDF9" opacity="{op}"/>')
    return ''.join(a)+'</svg>'


def render_job(args):
    i, scale, out = args
    data = svg_at(i/FPS).encode()
    key = hashlib.sha256(CACHE_VERSION.encode()+data+str(scale).encode()).hexdigest()
    cache = EP/'cache'/f'{key}.png'
    dest = Path(out)/f'{i:04d}.png'
    if not cache.exists():
        raw = cairosvg.svg2png(bytestring=data, output_width=round(W*scale), output_height=round(H*scale))
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


def audit():
    from mou_rig import _arm
    rig_hash = hashlib.sha256((ROOT/'mou_rig.py').read_bytes()).hexdigest()
    assert rig_hash == '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    fixed_feet = None
    for i in range(NFRAMES):
        t = i/FPS
        p = pose_at(t)
        original_avatar = character_at(p, uid='original-arms')
        for side in ('left', 'right'):
            assert _arm(side, p['arm_hips'], p['arm_clasp']) in original_avatar, (t, 'arm drawing changed')
        data = svg_at(t)
        root = ET.fromstring(data)
        ids = [e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids) == len(set(ids)), (t,'duplicate IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)', data)), (t,'missing clip')
        avatar = ET.fromstring('<svg>'+puppet(t,'audit')+'</svg>')
        hands = [e for e in avatar.iter() if e.attrib.get('data-part') == 'hand']
        assert len(hands) == 2, (t,'puppet hands')
        assert all(math.isfinite(v) for v in p.values())
        assert p['lift_l'] == 0 and p['lift_r'] == 0
        motion = motion_at(t)
        assert all(abs(motion.get(k,default)-default)<1e-10
                   for k,default in [('dx',0.),('dy',0.),('sx',1.),('sy',1.)]), (t,'global feet drift')
        feet = [ET.tostring(e) for e in avatar.iter()
                if e.attrib.get('id') in {'audit-foot-l','audit-foot-r'}]
        assert len(feet) == 2
        if fixed_feet is None:
            fixed_feet = feet
        assert feet == fixed_feet, (t,'feet changed')
        warp = next((e for e in avatar.iter() if e.attrib.get('id') == 'audit-body-warp'),None)
        d = deformation_at(p)
        warped = any(abs(d[k]-v)>1e-10 for k,v in [('sx',1.),('sy',1.),('skew',0.)])
        assert (warp is not None) == warped, (t,'body warp group')
        if warp is not None:
            children = {e.attrib.get('id') for e in warp.iter()}
            assert {'audit-body','audit-arm-left','audit-arm-right','audit-face'} <= children
            assert not {'audit-foot-l','audit-foot-r'} & children
        expected = 1 if t < 1. else 0 if PHOTO_START <= t < PHOTO_END else 2
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter()) == expected
        if t < FLASH:
            assert 'data:image/png' not in data
    assert [e['frame'] for e in TIMELINE['countdown']] == [24,48,72,96,120]
    assert TIMELINE['countdown'][-1]['time']+1 == FLASH
    assert pose_at(FLASH-1/FPS) != pose_at(FLASH), 'fall must reach extreme at capture'
    confident = deformation_at(pose_at(3.5))
    collapsed = deformation_at(pose_at(FLASH))
    assert confident['sy'] >= 1.08 and collapsed['sy'] <= .75
    assert confident['sy']-collapsed['sy'] >= .35
    fall = [deformation_at(pose_at(i/FPS))['sy']
            for i in range(round(5.75*FPS), TIMELINE['flash_frame']+1)]
    assert all(b <= a+1e-10 for a,b in zip(fall,fall[1:])), 'rebound before click'
    assert all(y > collapsed['sy']+1e-10 for y in fall[:-1]), 'extreme reached before click'
    captured = pose_at(FLASH)
    final = pose_at(TIMELINE['reaction']['final_hold_start'])
    for p in (captured, final):
        assert p['eye_open_l'] >= .95 and .55 <= p['eye_open_r'] <= .80
        assert p['cross'] >= .95 and p['nervous'] >= .95
        assert p['surprise'] == 0 and p['grimace'] == 0
    for i in range(TIMELINE['flash_frame'], round(TIMELINE['capture_hold']['end']*FPS)):
        assert pose_at(i/FPS) == captured, (i, 'capture pose not held')
    assert all(pose_at(i/FPS) == final for i in range(round(12.5*FPS), NFRAMES))
    from mou_rig import _tangent
    controls = tap_geometry(.90)
    tx,ty = _tangent(controls,1.)
    tip = (controls[-1][0]+75*tx,controls[-1][1]+75*ty)
    tap_error = math.dist(tip,(540,1450))
    assert tap_error < 1
    report = {'revision':REVISION,'file_stem':FILE_STEM,
              'original_rig_sha256':rig_hash,'original_rig_unchanged':True,
              'original_arm_paths_exact_all_frames':True,
              'frames':NFRAMES,'fps':FPS,'duration':DURATION,
              'flash_frame':TIMELINE['flash_frame'],'photo_pose_time':FLASH,
              'photo_sha256':hashlib.sha256((EP/'sources/photo_capturee.png').read_bytes()).hexdigest(),
              'unique_ids_all_frames':True,'two_hands_in_puppet_all_frames':True,
              'visible_hand_count_matches_framing':True,'feet_geometry_fixed_all_frames':True,
              'feet_excluded_from_body_warp':True,'feet_grounded_world':True,
              'body_arms_face_deform_together':True,
              'all_clip_references_resolved':True,'countdown_regular_seconds':True,
              'last_digit_held_until_flash':True,'no_portrait_before_flash':True,
              'confidence_vertical_scale':confident['sy'],'capture_vertical_scale':collapsed['sy'],
              'first_extreme_at_click':True,'tap_tip_error_pixels':tap_error,
              'capture_pose_hold_frames':round((TIMELINE['capture_hold']['end']-FLASH)*FPS),
              'capture_and_final_cross_eyed_nervous_smile':True,
              'final_pose_hold_seconds':DURATION-TIMELINE['reaction']['final_hold_start'],
              'limits':'Structure et source partagée ; lisibilité des intentions et raccords jugée séparément sur rendu.'}
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
    prepare_photo()
    report = audit()
    scale = .5 if args.preview else 1
    frames = EP/'frames'/('preview' if args.preview else 'final')
    frames.mkdir(parents=True,exist_ok=True)
    indices = sorted({round(t*FPS) for t in SAMPLES}) if args.stills else range(NFRAMES)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(render_job,[(i,scale,str(frames)) for i in indices]))
    for i in indices:
        data = svg_at(i/FPS).encode()
        key = hashlib.sha256(CACHE_VERSION.encode()+data+str(scale).encode()).hexdigest()
        dest = frames/f'{i:04d}.png'
        assert dest.stat().st_nlink == 1, (i,'shared frame inode')
        assert dest.read_bytes() == (EP/'cache'/f'{key}.png').read_bytes(), (i,'cache mismatch')
    board(frames,EP/'controle'/('planche_preview.png' if args.preview else 'planche_finale.png'))
    if args.stills:
        print(json.dumps(report,ensure_ascii=False))
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
    print(json.dumps({'file':str(full),**report},ensure_ascii=False))

if __name__ == '__main__':
    main()
