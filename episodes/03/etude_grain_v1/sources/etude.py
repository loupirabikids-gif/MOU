"""A five-second silent acting study: one grain becomes an absurd priority.

Three composed attitudes, held thoughts and one deliberate capitulation.
All arm contours and the sink mitten come from the existing original MOU.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import cairosvg
from PIL import Image, ImageDraw, ImageFont

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p / 'mou_rig.py').is_file())
sys.path.insert(0, str(EP / 'sources'))
spec = importlib.util.spec_from_file_location('grain_reference', EP / 'sources/reference_renderer.py')
R = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = R
spec.loader.exec_module(R)
import intentions

A, ART = R.animation, R.art
FPS, DURATION, W, H = 24, 5., 1080, 1920
HOLD = (465., 1195.)
PARK_GRIP = (468., 1275.)
PARK_BOWL = (337., 1308.)
RIGHT = (770., 1240.)
END = (140., 1135.)
VIEW = (25., 220., 1000., 1777.777777778)
POSE_TIMES = (.45, 2.15, 4.10)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def progress(t, a, b):
    return max(0., min(1., (t - a) / max(1e-9, b - a)))


def ease(u):
    return u * u * (3. - 2. * u)


def point(a, b, u):
    return tuple(x + (y - x) * u for x, y in zip(a, b))


def profile(a, b, amount):
    p, q = intentions.body_profile(a), intentions.body_profile(b)
    return {key: p[key] + (q[key] - p[key]) * amount for key in p}


def sink_clock(t):
    if t < 4.45:
        return 3.65 + .25 * progress(t, 4.30, 4.45)
    if t < 4.60:
        return 3.90 + .28 * progress(t, 4.45, 4.60)
    return 4.18 + (t - 4.60)


def spoon_at(t):
    if not 1.98 <= t < 3.34:
        return None
    if t < 2.55:
        u = ease(progress(t, 1.98, 2.55))
        # Half a small, real stirring arc inside the pan; constant spoon length.
        end, control = (282., 1292.), (310., 1277.)
        bowl = tuple((1-u)**2*PARK_BOWL[k] + 2*(1-u)*u*control[k] + u*u*end[k] for k in (0, 1))
    elif t < 3.10:
        bowl = (282., 1292.)
    else:
        bowl = point((282., 1292.), PARK_BOWL, ease(progress(t, 3.10, 3.34)))
    return {'bowl': bowl, 'grip': (bowl[0] + 131., bowl[1] - 33.)}


def state_at(t):
    t = max(0., min(5., float(t)))
    if t >= 4.30:
        clock = sink_clock(t)
        state = A.scene_state(clock)
        state.update(study_time=t, study_phase='lavage_du_seul_grain', reference_clock=clock)
        return state
    source = 20.12 + .48 * ease(progress(t, 0., .75))
    clock = A._source_at(source)
    state = copy.deepcopy(A._reference._base_scene_state(clock))
    state.update(study_time=t, reference_clock=clock, shot='wide',
                 water=False, lever=0., paper=None, spoon=None, spoon_held=False,
                 wet_hand=False, bin_count=0, flying_ball=None, floor_ball=None,
                 whistle={'amount': 0.}, actor_transform=(80., 380., 2.3))
    # One actual seasoning gesture, then a stable hand held away from the face.
    initial = A._reference._base_scene_state(A._source_at(20.60))['hands']['left']
    if t < .80:
        left = tuple(state['hands']['left'])
    elif t < 1.30:
        left = point(initial, HOLD, ease(progress(t, .80, 1.30)))
    elif t < 1.50:
        left = HOLD
    elif t < 1.98:
        left = point(HOLD, PARK_GRIP, ease(progress(t, 1.50, 1.98)))
    elif t < 3.34:
        left = spoon_at(t)['grip']
    else:
        # Swing below the shoulder, within the original arm's physical reach.
        u = ease(progress(t, 3.34, 4.30))
        control = (300., 1380.)
        left = tuple((1-u)**2 * PARK_GRIP[k] + 2*(1-u)*u*control[k] + u*u*END[k] for k in (0, 1))
    A._solve_targets(state, {'left': left, 'right': RIGHT})
    state['lock_world_hands'] = ['left']
    state['salt'] = {**state.get('salt', {}), 'active': t < .80}
    state['roll'] = A._stock_at(0.)
    state['carrot'] = {**state.get('carrot', {}), 'cuts': 0, 'knife_held': False}
    if t < .90:
        face = intentions.face_params('assurance')
        body = intentions.body_profile('assurance')
        phase = 'assurance'
    elif t < 1.05:
        u = ease(progress(t, .90, 1.05))
        face = intentions.blend_params('assurance', 'resistance', u)
        body = profile('assurance', 'resistance', u)
        phase = 'remarque_le_grain'
    elif t < 3.10:
        face = intentions.face_params('resistance')
        body = intentions.body_profile('resistance')
        phase = 'resistance'
    elif t < 3.30:
        u = ease(progress(t, 3.10, 3.30))
        face = intentions.blend_params('resistance', 'cede', u)
        body = profile('resistance', 'cede', u)
        phase = 'decision'
    else:
        face = intentions.face_params('cede')
        body = intentions.body_profile('cede')
        phase = 'cede'
    state = A._performance.apply(t, state, A,
        direction=(body['scale_y'], body['angle_deg'], phase))
    state['spoon'] = spoon_at(t)
    state['spoon_held'] = state['spoon'] is not None
    grain = grain_anchor(state)
    pan = (293., 1305.)
    if t < .82:
        target = pan
    elif t < 1.18:
        target = point(pan, grain, ease(progress(t, .82, .98)))
    elif t < 1.45:
        target = point(grain, pan, ease(progress(t, 1.18, 1.45)))
    elif t < 2.70:
        target = pan  # Deliberately turn attention back to cooking.
    elif t < 2.90:
        target = point(pan, grain, ease(progress(t, 2.70, 2.90)))
    elif t < 3.30:
        target = grain
    else:
        target = point(grain, (102., 1125.), ease(progress(t, 3.30, 3.50)))
    params = {key: value for key, value in state['pose'].items() if not key.startswith('_mouth_')}
    params.update(face)
    native_target = A._performance.inverse_world(target, state)
    A.look_at(params, native_target, state['actor_transform'])
    fragment = R.animation._jeu_visage.visage.face_fragment(params, 'mou-grain-visage')
    start = state['torso'].index('<g id="face"')
    state['torso'] = state['torso'][:start] + fragment
    state.update(pose=params, study_phase=phase, grain=grain, look_target=target,
                 body_profile=body, grain_present=t >= .72)
    return state


def grain_anchor(state):
    meta = state['arm_meta']['left']
    raw = A.world_grip('left', meta['hips'], meta['clasp'], meta['rotation'],
                       state['actor_transform'], 7.)
    return A._performance.forward_world(raw, state)


def grain_svg(x, y, width=24., uid='grain-sel'):
    k = width / 24.
    return (f'<g id="{uid}" transform="translate({x:.7f} {y:.7f}) scale({k:.7f})">'
            '<ellipse cx="2" cy="5" rx="12" ry="7" fill="#777447" opacity=".24"/>'
            '<path d="M-10 -5 Q-3 -11 7 -7 L12 3 Q6 10 -5 7 L-12 2 Z" '
            'fill="#FFFDF3" stroke="#766E76" stroke-width="2.3" stroke-linejoin="round"/>'
            '<path d="M-5 -4 L4 -4" fill="none" stroke="#FFFFFF" stroke-width="2.5"/>'
            '</g>')


def svg_at(t):
    state = state_at(t)
    if t >= 4.30:
        clock = sink_clock(t)
        svg = R.sink.svg_at(clock, state, A, ART, R.DEFS, R.BACKGROUND, W, H)
        g = R.sink.geometry_at(clock, state, A)
        x, y = g['tip']
        if t < 4.65:
            extra = grain_svg(x + 10., y - 3., 16.8)
        elif t < 4.84:
            u = progress(t, 4.65, 4.84)
            extra = grain_svg(104., y + 4. + 50. * u, 16.8 * (1. - .6*u), 'grain-emporte')
        else:
            extra = ''
        return svg.replace('</svg>', extra + '</svg>')
    x, y, scale = state['actor_transform']
    tr = f'translate({x} {y}) scale({scale})'
    affine = state['performance_affine_svg']
    body = (f'<g id="mou-corps" transform="{tr}">' + state['grounded_feet']
            + f'<g data-performance="upper-body" transform="{affine}">'
            + state['torso'] + R.costume.costume_svg(state) + '</g></g>')
    arms = (f'<g id="mou-bras" transform="{tr}">'
            f'<g data-performance="native-arms" transform="{affine}">{state["arms"]}</g></g>')
    parts = [R.DEFS, R.FLOOR_EXTENSION, R.BACKGROUND, ART.lever_svg(0.), body,
             R.GROUPS['ilot-cuisine'], R.PROPS_WITHOUT_ROLL, ART.roll_svg(state['roll']),
             R.cooking_fx.food_svg(1., state, ART), ART.tomato_dish_svg(occupied=False),
             ART.tomato_svg(*A.TOMATO_START),
             ART.spoon_svg(state['spoon']['grip'], state['spoon']['bowl']) if state['spoon'] else ART.parked_spoon_svg(),
             ART.carrot_svg(state.get('carrot')),
             ART.salt_svg(state.get('salt'), state['reference_clock'], layer='bowl'), arms]
    # A few falling grains establish seasoning; only ONE remains on the mitten.
    for j, start in enumerate((.12, .25, .38, .51)):
        u = progress(t, start, start + .24)
        if start <= t < start + .24:
            hx, hy = state['hands']['left']
            gx, gy = point((hx, hy + 8.), (293. + 13.*j, 1305.), u)
            parts.append(f'<ellipse cx="{gx:.5f}" cy="{gy:.5f}" rx="3" ry="4" fill="#FFFDF3" stroke="#B5A7AA" stroke-width="1"/>')
    if state['grain_present']:
        parts.append(grain_svg(*state['grain']))
    parts.append(ART.bin_svg(0, None, None))
    vb = ' '.join(str(v) for v in VIEW)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="{vb}">' + ''.join(parts) + '</svg>'


def render_frame(job):
    index, scale, folder = job
    svg = svg_at(index / FPS).encode()
    key = hashlib.sha256(svg + str(scale).encode()).hexdigest()
    cache = EP / 'cache' / (key + '.png')
    if not cache.exists():
        atomic(cache, cairosvg.svg2png(bytestring=svg, output_width=round(W*scale), output_height=round(H*scale)))
    target = Path(folder) / f'{index:05d}.png'
    atomic(target, cache.read_bytes())
    return index


def poses():
    labels = ['1 — Assurance', '2 — Résister', '3 — Céder']
    sheet = Image.new('RGB', (1620, 1020), '#FFF8ED')
    font = ImageFont.truetype(str(ROOT / 'fonts/DejaVuSans-Bold.ttf'), 24)
    for i, (t, name) in enumerate(zip(POSE_TIMES, ('01_assurance', '02_resistance', '03_cede'))):
        svg = svg_at(t)
        raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
        atomic(EP / f'{name}.png', raw)
        atomic(EP / f'{name}.svg', svg.encode())
        im = Image.open(io.BytesIO(raw)).convert('RGB').resize((540, 960), Image.Resampling.LANCZOS)
        sheet.paste(im, (i*540, 0))
        ImageDraw.Draw(sheet).text((i*540+18, 973), labels[i], fill='#382035', font=font)
    buffer = io.BytesIO()
    sheet.save(buffer, 'PNG')
    atomic(EP / 'MOU_trois_poses.png', buffer.getvalue())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--poses', action='store_true')
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    visual_sources = [p for p in (EP / 'sources').glob('*.py')
                      if p.name not in ('verify.py', 'package.py')]
    visual_sources += [EP/'chronologie.json', EP/'chronologie_reference_v25.json',
                       EP/'assets/Nunito-wght.ttf', ROOT/'mou_rig.py',
                       ROOT/'episodes/03/test_remuer/sources/animation.py',
                       ROOT/'episodes/03/decor/MOU_cuisine_decor.svg']
    frozen = {str(p): digest(p) for p in visual_sources}
    if args.poses:
        poses()
        print('Three full-scene key poses rendered', flush=True)
        return
    scale = .5 if args.preview else 1.
    tag = 'animatique' if args.preview else 'final'
    folder = EP / 'frames' / tag
    folder.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        for count, _ in enumerate(pool.map(render_frame, [(i, scale, str(folder)) for i in range(120)]), 1):
            if count % 24 == 0:
                print(f'{tag}: {count}/120', flush=True)
    assert frozen == {str(p): digest(p) for p in visual_sources}
    output = EP / ('MOU_Le_grain_animatique_muette.mp4' if args.preview else 'MOU_Le_grain_5s_muet.mp4')
    temporary = output.with_name('.' + output.name)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', '24', '-i', str(folder/'%05d.png'),
                    '-frames:v', '120', '-c:v', 'libx264', '-threads', '3', '-preset', 'medium',
                    '-crf', '12' if args.preview else '8', '-pix_fmt', 'yuv420p', '-an',
                    '-movflags', '+faststart', str(temporary)], check=True)
    os.replace(temporary, output)
    atomic(EP / 'controle' / f'gel_{tag}.json', (json.dumps({'sources': frozen, 'output': output.name,
           'sha256': digest(output), 'seconds': 5, 'frames': 120, 'fps': 24,
           'dimensions': [round(W*scale), round(H*scale)], 'audio_streams': 0}, indent=2)+'\n').encode())
    print(json.dumps({'output': str(output), 'sha256': digest(output)}), flush=True)


if __name__ == '__main__':
    main()
