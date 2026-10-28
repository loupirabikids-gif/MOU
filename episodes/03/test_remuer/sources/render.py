"""Render the four-second silent stirring study in the approved kitchen.

The approved SVG is read as artwork, without importing or rerunning its source.
MOU keeps the approved placement; only animation.py supplies the gesture.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
DECOR = EP.parent / 'decor'
SOURCE = EP / 'sources' / 'animation.py'
sys.path.insert(0, str(ROOT))
from mou_rig import _arm, character_fragment

_spec = importlib.util.spec_from_file_location('mou_remuer_animation', SOURCE)
animation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(animation)
actor_layers_at = animation.actor_layers_at
spoon_geometry_at = animation.spoon_geometry_at
pose_at, contact_at = animation.pose_at, animation.contact_at
intention_at, motion_at = animation.intention_at, animation.motion_at

W, H, FPS, DURATION = 1080, 1920, 24, 4.0
NFRAMES = 96
SAMPLES = [i / FPS for i in (0, 8, 17, 26, 35, 44, 52, 61, 70, 79, 88, 95)]
CHAR_X, CHAR_Y, CHAR_SCALE = 80.0, 380.0, 2.3
ACTOR_TRANSFORM = 'translate(80.0000 380.0000) scale(2.3000)'
CACHE_VERSION = 'remuer-full-svg-atomic-v1'
FILE_STEM = 'MOU_test_remuer'
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
DECOR_HASHES = {
    'MOU_cuisine_decor.png': '3148c402d57d24c1dc8ef5c5731aa2c07346c3d03fcade74e84c9a7e7ec2f585',
    'MOU_cuisine_decor.svg': '7e5292c066a8bdafca4ae42586fbf89ca62f6a45dcbca468bf9b748f19da2d49',
    'calques/accessoires_cuisine.svg': '696a466f0e2cead08dc8d22f4dbf154845e23f61805f75c69058abb7c59242a0',
    'calques/fond_cuisine.svg': '6a1fbe07858592ea7fec969022319d1eb48236965ab4bc8028056df68786d9dc',
    'calques/ilot_cuisine.svg': '4427ee12e9d8e38b0251e89d4425ec39d644b865b96454f9d28dea35a74497f4',
    'calques/accessoires_cuisine.png': 'b34f43d32eb19e5a39dfcd8560243286b75f69d26dc515009f4ecf02ef40e968',
    'calques/fond_cuisine.png': '1021d2067980154b2beb8899b44161c2309c77a86b8680bf513160476b83d44b',
    'calques/ilot_cuisine.png': 'd0f38a8bc0f77183fe73da340586f1eb5de1e36c10049bc499ca95fb304669ec',
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write(path, data):
    """Replace each artifact using its own bytes and inode, never a hard link."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f'.{path.name}.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(handle, 'wb') as output:
            output.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, data):
    atomic_write(path, (json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode())


ET.register_namespace('', 'http://www.w3.org/2000/svg')
_approved = ET.fromstring((DECOR / 'MOU_cuisine_decor.svg').read_text())
_serialize = lambda element: ET.tostring(element, encoding='unicode')
DECOR_DEFS = _serialize(next(element for element in _approved if element.tag.endswith('defs')))
DECOR_GROUPS = {element.attrib['id']: _serialize(element)
                for element in _approved if 'id' in element.attrib}
assert set(DECOR_GROUPS) == {'fond-cuisine', 'ilot-cuisine', 'accessoires-cuisine'}


def document(parts):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">' + ''.join(parts) + '</svg>')


def actorlayers(t, uid='mou-remuer'):
    """Expose the local torso and original arms used in the actual composition."""
    return actor_layers_at(t, uid=uid)


def svg_at(t):
    layers = actorlayers(t)
    assert layers.get('transform', ACTOR_TRANSFORM) == ACTOR_TRANSFORM
    behind = (f'<g id="mou-arriere" transform="{ACTOR_TRANSFORM}">'
              + layers['torso'] + layers['arms_back'] + '</g>')
    front = (f'<g id="mou-bras-premier-plan" transform="{ACTOR_TRANSFORM}">'
             + layers['arms_front'] + '</g>')
    return document([DECOR_DEFS, DECOR_GROUPS['fond-cuisine'], behind,
                     DECOR_GROUPS['ilot-cuisine'], DECOR_GROUPS['accessoires-cuisine'],
                     spoon_geometry_at(t)['svg'], front])


def raster(data, scale=1.0):
    return cairosvg.svg2png(bytestring=data.encode() if isinstance(data, str) else data,
                           output_width=round(W * scale), output_height=round(H * scale))


def cache_key(data, scale):
    # Full scene bytes include every changing input and layer ordering.
    return hashlib.sha256(CACHE_VERSION.encode() + b'\0' + str(scale).encode()
                          + b'\0' + data).hexdigest()


def render_job(args):
    i, scale, output, *cache_override = args
    output = Path(output)
    cache_dir = Path(cache_override[0]) if cache_override else EP / 'cache'
    data = svg_at(i / FPS).encode()
    cached = cache_dir / f'{cache_key(data, scale)}.png'
    destination = output / f'{i:04d}.png'
    if not cached.exists():
        atomic_write(cached, raster(data, scale))
    raw = cached.read_bytes()
    if not destination.exists() or destination.read_bytes() != raw:
        atomic_write(destination, raw)
    assert destination.stat().st_nlink == 1, (i, 'shared frame inode')
    assert destination.read_bytes() == cached.read_bytes(), (i, 'cache copy mismatch')
    return i


def board(frames, output):
    columns, tile_w, tile_h = 4, 270, 510
    result = Image.new('RGB', (columns * tile_w, 3 * tile_h), '#FFF4E5')
    draw = ImageDraw.Draw(result)
    font = ImageFont.truetype(str(ROOT / 'fonts/DejaVuSans-Bold.ttf'), 15)
    for j, t in enumerate(SAMPLES):
        frame = Image.open(Path(frames) / f'{round(t * FPS):04d}.png').convert('RGB')
        frame.thumbnail((270, 480), Image.Resampling.LANCZOS)
        x, y = (j % columns) * tile_w, (j // columns) * tile_h
        result.paste(frame, (x + (tile_w - frame.width) // 2, y))
        draw.text((x + 12, y + 485), f'{t:.3f} s · image {round(t * FPS):02d}',
                  font=font, fill='#382035')
    buffer = io.BytesIO()
    result.save(buffer, format='PNG')
    atomic_write(output, buffer.getvalue())


def audit(output=None):
    """Verify the actual vector inputs; visual judgment remains a separate review."""
    assert (FPS, DURATION, NFRAMES) == (animation.FPS, animation.DURATION, 96)
    assert digest(ROOT / 'mou_rig.py') == RIG_SHA, 'native rig changed'
    for name, expected in DECOR_HASHES.items():
        assert digest(DECOR / name) == expected, (name, 'approved decor changed')
    restored = Image.open(io.BytesIO(raster(document([DECOR_DEFS,
        DECOR_GROUPS['fond-cuisine'], DECOR_GROUPS['ilot-cuisine'],
        DECOR_GROUPS['accessoires-cuisine']])))).convert('RGBA')
    original = Image.open(DECOR / 'MOU_cuisine_decor.png').convert('RGBA')
    assert np.array_equal(np.asarray(restored), np.asarray(original)), 'decor import changes pixels'
    lengths, rotations, interior_norms = [], [], []
    for i in range(NFRAMES):
        t, uid = i / FPS, 'mou-remuer'
        p, c, layers = pose_at(t), contact_at(t), actorlayers(t, uid)
        canonical = character_fragment(p, uid=uid)
        for side in ('left', 'right'):
            fragment = _arm(side, p['arm_hips'], p['arm_clasp'])
            assert canonical.count(fragment) == 1
            canonical = canonical.replace(fragment, '', 1)
        assert layers['torso'] == canonical, (i, 'torso or feet changed')
        assert layers['arms_back'] == '', (i, 'unexpected rear arm')
        assert layers.get('transform', ACTOR_TRANSFORM) == ACTOR_TRANSFORM
        assert motion_at(t)['translate'] == (CHAR_X, CHAR_Y)
        assert motion_at(t)['scale'] == CHAR_SCALE
        assert c['left_clasp'] == animation.LEFT_CLASP
        expected_arms = {'left': _arm('left', 0., c['left_clasp']),
                         'right': _arm('right', 0., 1.)}
        for side, fragment in expected_arms.items():
            assert layers['arms_front'].count(fragment) == 1, (i, side, 'native arm changed')
        front = ET.fromstring('<g>' + layers['arms_front'] + '</g>')
        articulation = next(e for e in front if e.attrib.get('id') == 'left-shoulder-articulation')
        rotation = re.fullmatch(r'rotate\(([-\d.]+) 105 291\)', articulation.attrib['transform'])
        assert rotation and abs(float(rotation[1]) - c['left_rotation_deg']) < 1e-8
        assert len(articulation) == 1 and articulation[0].attrib['id'] == 'arm-left'
        assert front[-1].attrib['id'] == 'arm-right', (i, 'right arm moved')
        data = svg_at(t)
        for fragment in expected_arms.values():
            assert data.count(fragment) == 1, (i, 'duplicated native arm')
        root = ET.fromstring(data)
        ids = [e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids) == len(set(ids)), (i, 'duplicate IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)', data)), (i, 'unresolved reference')
        assert sum(e.attrib.get('data-part') == 'hand' for e in root.iter()) == 2, (i, 'hand count')
        assert 'data:image' not in data and '<image ' not in data, (i, 'unexpected raster artwork')
        assert all(math.isfinite(v) for v in p.values() if isinstance(v, (int, float)))
        assert p['lift_l'] == p['lift_r'] == 0., (i, 'feet moved')
        for name, fragment in DECOR_GROUPS.items():
            assert data.count(fragment) == 1, (i, name, 'approved group changed')
        spoon = spoon_geometry_at(t)
        assert data.count(spoon['svg']) == 1, (i, 'spoon changed at composition')
        measured = math.dist(c['grip'], c['bowl'])
        assert abs(measured - c['spoon_length']) < 1e-7, (i, 'spoon contact length')
        lengths.append(measured)
        rotations.append(c['left_rotation_deg'])
        cx, cy = c['pan_interior']['center']
        rx, ry = c['pan_interior']['radii']
        norm = ((c['bowl'][0] - cx) / rx) ** 2 + ((c['bowl'][1] - cy) / ry) ** 2
        assert norm < 1., (i, 'bowl centre outside pan')
        interior_norms.append(norm)
    assert max(lengths) - min(lengths) < 1e-7, 'spoon changes length'
    contacts = {f'{t:.6f}': contact_at(t) for t in SAMPLES}
    report = {
        'dimensions': [W, H], 'fps': FPS, 'duration_seconds': DURATION, 'frames': NFRAMES,
        'audio': False, 'original_rig_sha256': RIG_SHA,
        'animation_source_sha256': digest(SOURCE), 'renderer_source_sha256': digest(__file__),
        'decor_files_unchanged': DECOR_HASHES, 'decor_import_pixel_identical': True,
        'actor_transform': ACTOR_TRANSFORM, 'torso_and_feet_native_all_frames': True,
        'two_canonical_arm_fragments_exact_once_all_frames': True,
        'left_clasp': animation.LEFT_CLASP, 'right_clasp': 1.,
        'left_shoulder_rotation_degrees': [min(rotations), max(rotations)],
        'two_hands_all_frames': True, 'unique_ids_all_frames': True,
        'all_clip_references_resolved': True, 'entirely_vector_artwork': True,
        'spoon_grip_to_bowl_length_pixels': [min(lengths), max(lengths)],
        'maximum_pan_interior_normalized_squared_radius': max(interior_norms),
        'composition_back_to_front': ['approved background', 'native torso', 'approved island',
            'approved props', 'world spoon', 'native arms'],
        'pan_rim_extra_occlusion': False, 'contact_samples': contacts,
        'limits': 'Native source geometry and contacts verified. Natural movement, grip readability and depth require review of the rendered video.',
    }
    if output is not None:
        write_json(output, report)
    return report


def encode_video(frames, destination, scale):
    destination = Path(destination)
    handle, temporary = tempfile.mkstemp(prefix=f'.{destination.stem}.', suffix='.mp4', dir=destination.parent)
    os.close(handle)
    try:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-framerate', str(FPS),
            '-i', str(Path(frames) / '%04d.png'), '-map', '0:v:0', '-an',
            '-frames:v', str(NFRAMES), '-c:v', 'libx264', '-threads', '3',
            '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-map_metadata', '-1', '-movflags', '+faststart', temporary], check=True)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
            '-show_format', '-of', 'json', temporary]))
        assert len(probe['streams']) == 1, 'unexpected extra stream'
        video = probe['streams'][0]
        assert video['codec_type'] == 'video' and video['codec_name'] == 'h264'
        assert video['pix_fmt'] == 'yuv420p'
        assert [video['width'], video['height']] == [round(W * scale), round(H * scale)]
        assert video['r_frame_rate'] == f'{FPS}/1' and int(video['nb_frames']) == NFRAMES
        assert abs(float(video['duration']) - DURATION) < 1e-6
        os.replace(temporary, destination)
        probe['format']['filename'] = str(destination)
        return probe
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true', help='540 × 960 instead of 1080 × 1920')
    parser.add_argument('--stills', action='store_true', help='render the 12 contact-sheet frames only')
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    assert args.workers > 0
    control = EP / 'controle'
    control.mkdir(parents=True, exist_ok=True)
    source_hashes = (digest(SOURCE), digest(__file__))
    audit(control / 'audit_structure.json')
    scale, tag = (.5, 'preview') if args.preview else (1., 'final')
    frames = EP / 'frames' / tag
    frames.mkdir(parents=True, exist_ok=True)
    indices = sorted({round(t * FPS) for t in SAMPLES}) if args.stills else list(range(NFRAMES))
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(render_job, [(i, scale, str(frames)) for i in indices]))
    assert source_hashes == (digest(SOURCE), digest(__file__)), 'source changed while rendering'
    for i in indices:
        data = svg_at(i / FPS).encode()
        destination = frames / f'{i:04d}.png'
        assert destination.stat().st_nlink == 1
        assert destination.read_bytes() == (EP / 'cache' / f'{cache_key(data, scale)}.png').read_bytes()
    board(frames, control / ('planche_preview.png' if args.preview else 'planche_finale.png'))
    if args.stills:
        print(json.dumps({'stills': len(indices), 'frames_audited': NFRAMES,
                          'dimensions': [round(W * scale), round(H * scale)]}))
        return
    destination = EP / ('test_remuer_apercu.mp4' if args.preview else FILE_STEM + '.mp4')
    probe = encode_video(frames, destination, scale)
    write_json(control / f'probe_{tag}.json', probe)
    print(json.dumps({'file': str(destination), 'frames': NFRAMES, 'fps': FPS,
                      'duration': DURATION, 'audio': False,
                      'dimensions': [round(W * scale), round(H * scale)]}))


if __name__ == '__main__':
    main()
