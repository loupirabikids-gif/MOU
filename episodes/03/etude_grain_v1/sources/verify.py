"""Independent checks for the five-second silent grain study.

--prepare writes provisional geometry evidence only, never a final QA verdict.
Default execution requires the finished HD export and checks fresh Cairo images
against decoded video; no PNG frame cache is read by this checker.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image, ImageDraw

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p / 'mou_rig.py').is_file())
WORK = EP / 'work/qa_grain'
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
SAMPLES = (11, 18, 24, 48, 55, 67, 75, 98, 103, 104, 106, 111, 114, 119)
NS = '{http://www.w3.org/2000/svg}'
LIMITS = ('Contrôles de sources, géométrie et images décodées. Aucune écoute, '
          'approbation artistique, reconnaissance publique des intentions ou réussite comique certifiée.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name('.' + path.name)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def command(args):
    return subprocess.check_output(args, stderr=subprocess.PIPE)


def load_study():
    spec = importlib.util.spec_from_file_location('qa_grain_study', EP / 'sources/etude.py')
    study = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = study
    spec.loader.exec_module(study)
    return study


def matrix(text):
    result = np.eye(3)
    for name, raw in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)', text):
        v = [float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?', raw)]
        m = np.eye(3)
        if name == 'matrix':
            a, b, c, d, e, f = v
            m = np.array([[a, c, e], [b, d, f], [0., 0., 1.]])
        elif name == 'translate':
            m[0, 2] = v[0]
            m[1, 2] = v[1] if len(v) == 2 else 0.
        elif name == 'scale':
            m[0, 0], m[1, 1] = v[0], v[-1]
        elif name == 'rotate':
            a = math.radians(v[0]); c, s = math.cos(a), math.sin(a)
            m = np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])
            if len(v) == 3:
                x, y = v[1:]
                m[0, 2], m[1, 2] = x-c*x+s*y, y-s*x-c*y
        else:
            raise AssertionError(('unsupported transform', name))
        result = result @ m
    return result


def ancestors(root, node):
    parents = {c: p for p in root.iter() for c in p}
    chain = [node]
    while chain[-1] is not root:
        chain.append(parents[chain[-1]])
    return list(reversed(chain))


def world_matrix(root, node):
    out = np.eye(3)
    for element in ancestors(root, node):
        out = out @ matrix(element.get('transform', ''))
    return out


def layer(root, node, fill_only=False):
    """Retain the emitted ancestor transforms, removing unrelated scene art."""
    out = ET.Element(NS + 'svg', {'viewBox': root.get('viewBox')})
    parent = out
    for element in ancestors(root, node)[1:-1]:
        parent = ET.SubElement(parent, NS + 'g',
                               {k: v for k, v in element.attrib.items() if k == 'transform'})
    element = copy.deepcopy(node)
    if fill_only:
        element.set('stroke', 'none')
    parent.append(element)
    return ET.tostring(out)


def alpha(root, node, fill_only=False, width=540):
    raw = cairosvg.svg2png(bytestring=layer(root, node, fill_only),
                          output_width=width, output_height=round(width * 16/9))
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))[:, :, 3] > 127


def independent_grip(side, meta):
    """Canonical endpoint/tangent interpolation, independent of the grip solver."""
    if side == 'left':
        down, hip, fold = (70., 341., 76., 367.), (40., 344., 118., 356.), (119., 386., 178., 389.)
    else:
        down, hip, fold = (332., 340., 325., 367.), (361., 344., 283., 356.), (281., 386., 225., 389.)
    h, c = meta['hips'], meta['clasp']
    values = [(a + (b-a)*h)*(1-c) + z*c for a, b, z in zip(down, hip, fold)]
    px, py, x, y = values
    dx, dy = x-px, y-py
    length = math.hypot(dx, dy)
    depth = meta.get('grip_depth', 16.)
    return np.array([x+depth*dx/length, y+depth*dy/length, 1.])


def source_checks(final=False):
    baseline = json.loads((EP / 'controle/baseline.json').read_text())
    assert digest(ROOT / 'mou_rig.py') == baseline['mou_rig.py'] == RIG_SHA
    verified, absent = {}, []
    for name, expected in baseline.items():
        path = ROOT / name
        if path.is_file():
            assert digest(path) == expected, ('protected original changed', name)
            verified[name] = expected
        else:
            absent.append(name)
    for name in ('sink.py', 'mitten.py'):
        assert digest(EP / 'sources' / name) == baseline['episodes/03/cuisine_v30/sources/' + name]
    frozen = {}
    if final:
        manifest = json.loads((EP / 'controle/gel_final.json').read_text())
        assert manifest['sha256'] == digest(EP / 'MOU_Le_grain_5s_muet.mp4')
        for path, expected in manifest['sources'].items():
            p = Path(path)
            # Resolve the original workspace paths inside a portable root.
            if not p.is_file():
                p = ROOT / p.relative_to('/workspace/MOU')
            assert digest(p) == expected, ('source changed after render', path)
            frozen[str(p.relative_to(ROOT))] = expected
        assert all(str((EP/'sources'/name).relative_to(ROOT)) in frozen
                   for name in ('etude.py', 'intentions.py'))
    current = {p.name: digest(p) for p in sorted((EP / 'sources').glob('*.py'))}
    return {'canonical_rig_sha256': RIG_SHA, 'protected_originals_verified': verified,
            'protected_originals_absent_in_portable_copy': absent,
            'approved_sink_and_mitten_unchanged': True,
            'render_frozen_visual_dependencies': frozen, 'current_python_sources': current}


def geometry_checks(study):
    import mou_rig as rig
    records, face_masks, grain_masks, sink, spoons = [], [], [], [], []
    max_grip_error = 0.
    native_count = 0
    for index in range(120):
        t = index/24
        state = study.state_at(t)
        svg = study.svg_at(t)
        root = ET.fromstring(svg)
        ids = [e.get('id') for e in root.iter() if e.get('id')]
        assert len(ids) == len(set(ids)), (index, 'duplicate IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)', svg)), (index, 'missing reference')
        hands = [e for e in root.iter() if e.get('data-part') == 'hand']
        wide = t < 4.3
        assert len(hands) == (2 if wide else 1), (index, 'visible hand count')
        assert not any(e.tag.endswith('text') for e in root.iter()), (index, 'unexpected text')
        images = [e for e in root.iter() if e.tag.endswith('image')]
        assert len(images) == int(wide), (index, 'unexpected caption image')
        if wide:
            assert images[0].get('href') == 'data:image/png;base64,' + study.R.costume.hat_name()
            for hand in hands:
                side = hand.get('data-side'); meta = state['arm_meta'][side]
                expected = next(e for e in ET.fromstring(rig._arm(side, meta['hips'], meta['clasp'])).iter()
                                if e.get('data-part') == 'hand')
                shoulder = (105., 291.) if side == 'left' else (297., 291.)
                def distal(element):
                    return [p for p in (tuple(map(float, pair)) for pair in
                            re.findall(r'(-?[\d.]+) (-?[\d.]+)', element.get('d')))
                            if math.dist(p, shoulder) > 24.]
                a, b = distal(expected), distal(hand)
                assert len(a) == len(b) and all(math.dist(p, q) < .003 for p, q in zip(a, b)), (index, side, 'non-native contour')
                actual = (world_matrix(root, hand) @ independent_grip(side, meta))[:2]
                error = math.dist(actual, state['hands'][side])
                assert error < .003, (index, side, 'declared hand differs from emitted native grip', error)
                max_grip_error = max(max_grip_error, error); native_count += 1
            spoon = next(e for e in root.iter() if e.get('id') == 'cuillere-cuisine')
            assert bool(state['spoon_held']) == (1.98 <= t < 3.34)
            if state['spoon_held']:
                line = next(e for e in spoon if e.tag.endswith('path'))
                values = list(map(float, re.findall(r'-?[\d.]+', line.get('d'))))
                bowl, butt = np.array(values[:2]), np.array(values[2:])
                direction = (butt-bowl)/np.linalg.norm(butt-bowl)
                emitted_grip = butt-28.*direction
                vector = emitted_grip-bowl
                error = math.dist(emitted_grip, state['hands']['left'])
                assert error < .003, (index, 'spoon handle misses true native grip', error)
                assert math.dist(vector, (131., -33.)) < .003, (index, 'spoon changes length or direction', vector)
                hand = next(e for e in hands if e.get('data-side') == 'left')
                hand_mask = alpha(root, hand, True)
                vx, vy, vw, vh = map(float, root.get('viewBox').split())
                px, py = round((emitted_grip[0]-vx)*540/vw), round((emitted_grip[1]-vy)*960/vh)
                assert hand_mask[py, px], (index, 'spoon grip outside actual mitten contour')
                spoons.append({'frame': index, 'time': t, 'emitted_grip': emitted_grip.tolist(),
                               'emitted_bowl': bowl.tolist(), 'grip_error_world_px': error,
                               'bowl_to_grip_length': float(np.linalg.norm(vector))})
            arms = next(e for e in root.iter() if e.get('id') == 'mou-bras')
            amask = alpha(root, arms)
            face = next(e for e in root.iter() if e.get('id') == 'face')
            eyes = [e for e in face if e.get('fill') == '#FFFDFD']
            assert len(eyes) == 2, (index, 'two eye contours missing')
            mouth = next(e for e in face if e.get('id') == 'mouth')
            regions = eyes + [list(mouth)[0]]
            overlaps = [int((amask & alpha(root, e)).sum()) for e in regions]
            assert not any(overlaps), (index, 'arms mask eyes or mouth', overlaps)
            face_masks.append({'frame': index, 'time': t, 'overlap_pixels_540': overlaps})
        else:
            g = study.R.sink.geometry_at(study.sink_clock(t), state, study.A)
            assert hands[0].get('d') == g['mitten_outline_d'] + ' Z'
            assert hands[0].get('data-hand-region') == 'approved-rounded-thumb'
            contact_error = math.dist(g['tip'], g['tap_target']) if g['phase'] == 'open_tap' else None
            if contact_error is not None:
                assert contact_error < .003, (index, 'tap contact miss', contact_error)
            sink.append({'frame': index, 'time': t, 'phase': g['phase'], 'lever': g['lever'],
                         'water': g['water_on'], 'tip': g['tip'], 'tap_contact_error': contact_error})
        attached = next((e for e in root.iter() if e.get('id') == 'grain-sel'), None)
        carried = next((e for e in root.iter() if e.get('id') == 'grain-emporte'), None)
        assert (attached is not None) == (.72 <= t < 4.65), (index, 'attached grain missing')
        assert (carried is not None) == (4.65 <= t < 4.84), (index, 'jet departure interval')
        if attached is not None:
            grain = next(e for e in attached if e.tag.endswith('path'))
            hand = next(e for e in hands if not wide or e.get('data-side') == 'left')
            gm, hm = alpha(root, grain, True), alpha(root, hand, True)
            outside = int((gm & ~hm).sum()); area = int(gm.sum())
            assert area > 0 and outside == 0, (index, 'grain white body outside mitten', outside, area)
            grain_masks.append({'frame': index, 'white_pixels_540': area, 'outside_mitten_pixels': outside})
        if carried is not None:
            grain = next(e for e in carried if e.tag.endswith('path'))
            gm = alpha(root, grain, True)
            assert gm.any(), (index, 'grain disappears outside view')
            centre = (world_matrix(root, grain) @ np.array([0., 0., 1.]))[:2]
            assert g['water_on'] and 90. <= centre[0] <= 114. and 1069. <= centre[1] <= 1174., (index, 'departure outside water jet', centre)
        records.append({'frame': index, 'time': t, 'hands': len(hands), 'unique_ids': len(ids),
                        'svg_sha256': hashlib.sha256(svg.encode()).hexdigest()})
    assert any(e['phase'] == 'open_tap' and e['lever'] > .5 for e in sink)
    assert any(e['phase'] == 'rinse_tip' and e['water'] for e in sink)
    held = [s['emitted_grip'] for s in spoons if 2.55 <= s['time'] < 3.1]
    hold_span = max(math.dist(p, held[0]) for p in held)
    assert hold_span < .003, ('hand does not stop after attempted stirring', hold_span)
    stirring = [s['emitted_bowl'] for s in spoons if s['time'] < 2.55]
    assert math.dist(stirring[0], stirring[-1]) > 40., 'no actual stirring movement'
    return {'svg_frames': 120, 'wide_frames': 104, 'sink_frames': 16,
            'native_wide_arm_contours_compared': native_count,
            'max_declared_vs_emitted_grip_error_world_px': max_grip_error,
            'grain_containment_masks_540': grain_masks,
            'arms_vs_eyes_and_mouth_masks_540': face_masks,
            'spoon_actual_svg_contacts': spoons, 'spoon_hold_span_world_px': hold_span,
            'sink_actual_emitted_geometry': sink,
            'sink_note': 'Contacts use emitted approved insert geometry; inherited wide-shot hands metadata is not the insert contour.',
            'frames': records}


def video_checks(path):
    data = json.loads(command(['ffprobe', '-v', 'error', '-count_frames', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    assert len(data['streams']) == 1, 'silent export must have one video stream and no audio'
    v = data['streams'][0]
    assert v['codec_type'] == 'video' and v['codec_name'] == 'h264' and v['pix_fmt'] == 'yuv420p'
    assert (v['width'], v['height']) == (1080, 1920)
    assert Fraction(v['r_frame_rate']) == Fraction(v['avg_frame_rate']) == 24
    assert int(v['nb_read_frames']) == int(v['nb_frames']) == 120
    assert abs(float(v['duration'])-5.) < .001 and abs(float(data['format']['duration'])-5.) < .001
    command(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-i', str(path), '-f', 'null', '-'])
    return {'file': path.name, 'sha256': digest(path), 'bytes': path.stat().st_size,
            'dimensions': [1080, 1920], 'frames': 120, 'fps': 24, 'seconds': 5,
            'audio_streams': 0, 'full_decode_without_errors': True}


def decoded_checks(study, path):
    expression = '+'.join(f'eq(n\\,{i})' for i in SAMPLES)
    raw = command(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-filter_threads', '2',
                   '-i', str(path), '-vf', 'select=' + expression, '-fps_mode', 'passthrough',
                   '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    assert len(raw) == len(SAMPLES)*1080*1920*3
    frames = np.frombuffer(raw, np.uint8).reshape(len(SAMPLES), 1920, 1080, 3)
    sheet = Image.new('RGB', (1080, 525*7), '#FFF8ED')
    stats = []
    for j, (index, decoded) in enumerate(zip(SAMPLES, frames)):
        t = index/24
        svg = study.svg_at(t)
        fresh_raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=1080, output_height=1920)
        fresh_im = Image.open(io.BytesIO(fresh_raw)).convert('RGB')
        fresh = np.asarray(fresh_im)
        diff = np.abs(fresh.astype(np.int16)-decoded.astype(np.int16))
        mean = float(diff.mean())
        assert mean < 2., (index, 'HD differs from fresh Cairo rendering', mean)
        root = ET.fromstring(svg)
        view = list(map(float, root.get('viewBox').split()))
        rois = {'whole': [0, 0, 1080, 1920]}
        if t < 4.3:
            rois['face'] = [250, 620, 700, 1080]
        grain = next((e for e in root.iter() if e.get('id') in ('grain-sel', 'grain-emporte')), None)
        if grain is not None:
            x, y = (world_matrix(root, grain) @ np.array([0., 0., 1.]))[:2]
            x, y = (x-view[0])*1080/view[2], (y-view[1])*1920/view[3]
            radius = 45 if t < 4.3 else 80
            rois['grain'] = [max(0, int(x-radius)), max(0, int(y-radius)), min(1080, int(x+radius)), min(1920, int(y+radius))]
        roi_stats = {}
        for name, (x0, y0, x1, y1) in rois.items():
            values = diff[y0:y1, x0:x1]
            error = float(values.mean())
            assert error < 4., (index, name, 'local stale frame or visual mismatch', error)
            roi_stats[name] = {'bounds': [x0, y0, x1, y1], 'mean_absolute_channel_error': error}
        Image.fromarray(decoded).save(WORK / f'hd_{index:03d}.png')
        fresh_im.save(WORK / f'fresh_{index:03d}.png')
        tile = Image.fromarray(decoded).resize((540, 960), Image.Resampling.LANCZOS)
        tile = tile.resize((270, 480), Image.Resampling.LANCZOS)
        x, y = (j % 2)*540, (j//2)*525
        sheet.paste(tile, (x, y+25))
        comparison = fresh_im.resize((270, 480), Image.Resampling.LANCZOS)
        sheet.paste(comparison, (x+270, y+25))
        ImageDraw.Draw(sheet).text((x+5, y+5), f'{index:03d} / {t:.3f}s — HD | Cairo frais', fill='#382035')
        stats.append({'frame': index, 'time': t, 'regions': roi_stats,
                      'fresh_png_sha256': hashlib.sha256(fresh_raw).hexdigest()})
    sheet.save(WORK / 'HD_vs_Cairo_frais.png')
    return {'samples': stats, 'sample_count': len(SAMPLES), 'png_cache_read': False,
            'comparison_sheet': 'work/qa_grain/HD_vs_Cairo_frais.png'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    study = load_study()
    before = {p.name: digest(p) for p in (EP/'sources').glob('*.py')}
    report = {'status': 'preparation_only' if args.prepare else 'passed',
              'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'limits': LIMITS,
              'sources': source_checks(not args.prepare), 'geometry': geometry_checks(study)}
    if args.prepare:
        write_json(WORK / 'preparation.json', report)
        print('Provisional geometry complete; final HD QA not executed.')
        return
    movie = EP / 'MOU_Le_grain_5s_muet.mp4'
    report['video'] = video_checks(movie)
    report['decoded_hd'] = decoded_checks(study, movie)
    assert before == {p.name: digest(p) for p in (EP/'sources').glob('*.py')}, 'source changed during QA'
    write_json(EP / 'controle/QA.json', report)
    text = (f'QA technique passée sur `{movie.name}`.\n\n'
            f'SHA-256 : `{report["video"]["sha256"]}`.\n\n'
            '120 SVG : 104 larges avec deux bras/moufles natifs, 16 inserts avec une seule moufle approuvée ; '
            'identifiants uniques et références résolues. Rig canonique et originaux protégés inchangés. '
            'Les grips déclarés sont recalculés depuis les contrôles canoniques et les transformations SVG émises.\n\n'
            '94 masques à 540 px : corps blanc du grain entièrement dans la vraie moufle avant détachement. '
            '104 masques bras/yeux/bouche sans recouvrement. '
            '33 images de reprise : manche réellement saisi dans la moufle, distance cuilleron/grip '
            'constante de 135,0926 px, demi-remuage puis arrêt de la main avant la repose. '
            'Le levier s’ouvre avant le rinçage ; le grain quitte la moufle dans le jet, reste visible dans le champ '
            'pendant son départ puis disparaît. Aucun texte explicatif ; seul le logo MOU de la toque est embarqué.\n\n'
            'MP4 : 1080 × 1920, 5 s, 24 images/s, 120 images, aucune piste audio ; décodage intégral sans erreur. '
            '14 images HD décodées comparées à des SVG/Cairo frais, avec mesures locales visage/grain et inserts/fin. '
            'Aucune image du cache PNG utilisée. Preuves privées : `work/qa_grain/`.\n\n'
            'Le lavabo est contrôlé par sa géométrie réellement émise ; les champs hands hérités du plan large '
            'ne servent pas à certifier le contact de cet insert.\n\n' + LIMITS + '\n')
    (EP/'controle/QA.md').write_text(text)
    print(json.dumps({'status': 'passed', 'video_sha256': report['video']['sha256'],
                      'svg_frames': 120, 'fresh_decoded_hd_samples': len(SAMPLES)}))


if __name__ == '__main__':
    main()
