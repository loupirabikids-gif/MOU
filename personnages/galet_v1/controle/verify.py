"""Independent SVG/raster and encoded-video checks for the Galet prototype.

The production contract is supplied after the producer is frozen. Contact is
measured from isolated emitted silhouettes, not from a producer's success flag.
This tool does not assess artistic quality or imply any audio listening.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image


def digest(path):
    with Path(path).open('rb') as src:
        return hashlib.file_digest(src, 'sha256').hexdigest()


def load_module(path):
    path = Path(path).resolve()
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('galet_qa_fresh_producer', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def isolated_svg(svg, ids):
    """Keep requested emitted components with ancestors, defs and transforms."""
    selected = set(ids)
    root = ET.fromstring(svg)

    def prune(node, inherited=False):
        name = node.tag.rsplit('}', 1)[-1]
        if name in ('defs', 'style') or inherited or node.get('id') in selected:
            return copy.deepcopy(node)
        result = ET.Element(node.tag, node.attrib)
        for child in node:
            kept = prune(child)
            if kept is not None:
                result.append(kept)
        if len(result) or node is root:
            return result
        return None

    present = {node.get('id') for node in root.iter()}
    missing = selected - present
    assert not missing, f'Missing SVG IDs: {sorted(missing)}'
    output = prune(root)
    # A CSS background is not part of an isolated component's silhouette.
    output.attrib.pop('style', None)
    return ET.tostring(output, encoding='unicode')


def silhouette(svg, ids, dimensions):
    w, h = dimensions
    raw = cairosvg.svg2png(bytestring=isolated_svg(svg, ids).encode(),
                          output_width=w, output_height=h)
    pixels = np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))
    return pixels[:, :, 3] >= 32


def bounds(mask):
    ys, xs = np.nonzero(mask)
    assert len(xs), 'Empty rendered silhouette'
    return [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]


def boundary(mask):
    inside = mask.copy()
    for axis in (0, 1):
        inside &= np.roll(mask, 1, axis) & np.roll(mask, -1, axis)
    inside[0] = inside[-1] = False
    inside[:, 0] = inside[:, -1] = False
    return np.argwhere(mask & ~inside).astype(float)


def gap(first, second):
    if np.any(first & second):
        return 0.0
    a, b = boundary(first), boundary(second)
    assert len(a) and len(b), 'Cannot measure contact with empty shape'
    best = float('inf')
    for start in range(0, len(a), 256):
        differences = a[start:start + 256, None, :] - b[None, :, :]
        best = min(best, float(np.sum(differences ** 2, axis=2).min()))
    return float(best ** .5)


def svg_transform(text):
    result = np.eye(3)
    for name, raw in re.findall(r'([a-zA-Z]+)\(([^)]*)\)', text or ''):
        values = [float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', raw)]
        matrix = np.eye(3)
        if name == 'translate':
            matrix[:2, 2] = values[0], values[1] if len(values) > 1 else 0.
        elif name == 'scale':
            matrix[0, 0] = values[0]
            matrix[1, 1] = values[1] if len(values) > 1 else values[0]
        elif name == 'rotate':
            angle = np.deg2rad(values[0]); c, s = np.cos(angle), np.sin(angle)
            matrix[:2, :2] = [[c, -s], [s, c]]
            if len(values) == 3:
                pivot = np.array(values[1:3])
                matrix[:2, 2] = pivot - matrix[:2, :2] @ pivot
        elif name == 'matrix':
            a, b, c, d, e, f = values
            matrix = np.array([[a, c, e], [b, d, f], [0., 0., 1.]])
        else:
            raise AssertionError(f'Unreviewed SVG transform: {name}')
        result = result @ matrix
    return result


def fresh_rgb(svg, dimensions):
    raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=dimensions[0],
                          output_height=dimensions[1])
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))


def decoded_frames(video, indices, dimensions):
    expression = 'select=' + '+'.join(f'eq(n\\,{i})' for i in indices)
    raw = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-threads', '2', '-filter_threads', '2',
        '-i', str(video), '-vf', expression, '-fps_mode', 'passthrough',
        '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    w, h = dimensions
    result = np.frombuffer(raw, dtype=np.uint8).reshape(len(indices), h, w, 3)
    return dict(zip(indices, result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, required=True,
                        help='Frozen producer/video/geometry contract JSON')
    parser.add_argument('--report', type=Path,
                        default=Path(__file__).with_name('QA.json'))
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    base = args.contract.resolve().parent
    resolve = lambda value: (base / value).resolve()
    source_files = [resolve(p) for p in contract['source_files']]
    frozen = {str(p): digest(p) for p in source_files}
    repository = next(p for p in base.parents if (p / 'mou_rig.py').is_file())
    production_freeze = json.loads(resolve(contract['source_freeze']).read_text())
    frozen_production = {**production_freeze['sources_sha256'],
                         **production_freeze['historical_mou_sha256']}
    assert all(digest(repository / path) == value for path, value in frozen_production.items()), \
        'Frozen producer or historical MOU file changed before QA'
    video = resolve(contract['video'])
    producer = load_module(resolve(contract['producer']))
    svg_at = getattr(producer, contract.get('svg_function', 'svg_at'))
    dimensions = tuple(contract.get('dimensions', [1080, 1920]))
    fps = int(contract.get('fps', 24))
    duration = float(contract['duration'])
    count = round(fps * duration)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of',
        'json', str(video)]))
    visual = [s for s in probe['streams'] if s['codec_type'] == 'video']
    assert len(visual) == 1
    visual = visual[0]
    assert [visual['width'], visual['height']] == list(dimensions)
    assert int(visual['nb_frames']) == count
    assert visual['r_frame_rate'] == f'{fps}/1'
    assert abs(float(probe['format']['duration']) - duration) < .05
    assert not any(s['codec_type'] == 'audio' for s in probe['streams']), 'Expected silent video'
    subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-i', str(video),
                    '-f', 'null', '-'], check=True)
    ids = contract['ids']
    wanted = set(ids['hands'] + ids['feet'] + ids['eyes'] + ids['pupils'] + [ids['crumb']])
    measured = []
    final_signatures = []
    owners = []
    foot_signatures = {key: set() for key in ids['feet']}
    hand_scale_determinants = {key: [] for key in ids['hands']}
    for i in range(count):
        svg = svg_at(i / fps)
        root = ET.fromstring(svg)
        emitted = [n.get('id') for n in root.iter() if n.get('id')]
        assert len(emitted) == len(set(emitted)), (i, 'Duplicate SVG IDs')
        assert wanted.issubset(emitted), (i, 'Missing character components')
        present = set(emitted)
        assert all(ref in present for ref in re.findall(r'url\(#([^)]*)\)', svg))
        assert sum(n.get('data-part') == 'floating-mitten' for n in root.iter()) == 2
        assert sum(n.get('data-part') == 'foot' for n in root.iter()) == 2
        assert not any(n.get('data-part') == 'arm' or (n.get('id') or '').startswith('arm-')
                       for n in root.iter()), (i, 'Unexpected arm')
        owner = next(n.get('data-owner') for n in root.iter() if n.get('id') == ids['crumb'])
        expected_owner = 'left' if i / fps < contract['transfer_time'] else 'right'
        assert owner == expected_owner, (i, 'Wrong crumb owner metadata')
        owners.append(owner)
        by_id = {node.get('id'): node for node in root.iter() if node.get('id')}
        parents = {child: parent for parent in root.iter() for child in parent}
        for foot_id in ids['feet']:
            node = by_id[foot_id]
            chain = []
            parent = parents.get(node)
            while parent is not None:
                chain.append({k: v for k, v in parent.attrib.items()
                              if k in ('transform', 'viewBox', 'width', 'height', 'opacity')})
                parent = parents.get(parent)
            signature = ET.tostring(node) + json.dumps(chain, sort_keys=True).encode()
            foot_signatures[foot_id].add(hashlib.sha256(signature).hexdigest())
        for hand_id in ids['hands']:
            matrix = svg_transform(by_id[hand_id].get('transform'))
            hand_scale_determinants[hand_id].append(abs(float(np.linalg.det(matrix[:2, :2]))))
        if i >= round(contract['hold_start'] * fps):
            final_signatures.append(hashlib.sha256(isolated_svg(svg, contract['hold_ids']).encode()).hexdigest())
    assert len(set(final_signatures)) == 1, 'Final held components still change'
    assert all(len(values) == 1 for values in foot_signatures.values()), 'Grounded feet still move'
    for key, values in hand_scale_determinants.items():
        assert max(values) - min(values) < 1.e-9, (key, 'Mitten scaling changes')
    transfer_matrices = []
    for delta in (-1.e-6, 1.e-6):
        tree = ET.fromstring(svg_at(contract['transfer_time'] + delta))
        node = next(n for n in tree.iter() if n.get('id') == ids['crumb'])
        transfer_matrices.append(svg_transform(node.get('transform')))
    transfer_position_jump = float(np.linalg.norm(
        transfer_matrices[1][:2, 2] - transfer_matrices[0][:2, 2]))
    transfer_orientation_jump = float(np.max(np.abs(
        transfer_matrices[1][:2, :2] - transfer_matrices[0][:2, :2])))
    assert transfer_position_jump < .001 and transfer_orientation_jump < 1.e-5, \
        ('Crumb teleports or turns abruptly at owner change', transfer_position_jump,
         transfer_orientation_jump)
    for sample in contract['contact_samples']:
        i = round(sample['time'] * fps)
        svg = svg_at(i / fps)
        crumb = silhouette(svg, [ids['crumb']], dimensions)
        crumb_bounds = bounds(crumb)
        assert min(crumb_bounds[2] - crumb_bounds[0], crumb_bounds[3] - crumb_bounds[1]) >= 20, \
            (i, 'Crumb rendered below the phone-legibility size target', crumb_bounds)
        hands = [silhouette(svg, [hand], dimensions) for hand in ids['hands']]
        gaps = [gap(crumb, hand) for hand in hands]
        owner = int(sample['owner'])
        assert gaps[owner] <= sample.get('max_gap', 3), (i, 'Crumb detached from intended hand', gaps)
        if 'min_other_gap' in sample:
            assert gaps[1 - owner] >= sample['min_other_gap'], (i, 'Hand transfer is not spatially separated', gaps)
        if sample.get('hands_contact'):
            assert gap(*hands) <= sample.get('max_hand_gap', 3), (i, 'No actual hand contact')
        if sample.get('both_hands_touch_crumb'):
            assert max(gaps) <= sample.get('max_gap', 3), (i, 'No two-sided contact at transfer', gaps)
        measured.append({'frame': i, 'time': i / fps, 'crumb_bounds': crumb_bounds,
                         'crumb_hand_gap_pixels': gaps, 'hand_hand_gap_pixels': gap(*hands)})
    indices = sorted({min(count - 1, round(t * fps)) for t in contract['image_samples']})
    decoded = decoded_frames(video, indices, dimensions)
    images = []
    for i in indices:
        svg = svg_at(i / fps)
        reference = fresh_rgb(svg, dimensions)
        difference = np.abs(reference.astype(float) - decoded[i].astype(float))
        components = silhouette(svg, ids['hands'] + [ids['crumb']], dimensions)
        global_error = float(difference.mean())
        contact_error = float(difference[components].mean())
        assert global_error < 4 and contact_error < 6, (i, global_error, contact_error)
        eye_checks = []
        for eye_id, pupil_id in zip(ids['eyes'], ids['pupils']):
            eye = silhouette(svg, [eye_id], dimensions)
            pupil = silhouette(svg, [pupil_id], dimensions)
            outside = int(np.count_nonzero(pupil & ~eye))
            assert outside == 0, (i, pupil_id, 'Pupil outside eye aperture', outside)
            obscured = int(np.count_nonzero(components & eye))
            assert obscured == 0, (i, eye_id, 'Hand or crumb covers eye aperture', obscured)
            eye_checks.append({'eye': eye_id, 'pupil': pupil_id,
                               'pupil_pixels_outside_aperture': outside,
                               'hand_crumb_overlap_aperture_pixels': obscured})
        images.append({'frame': i, 'time': i / fps, 'mean_abs_rgb_error': global_error,
                       'hands_crumb_mean_abs_rgb_error': contact_error,
                       'pupil_aperture_checks': eye_checks})
    assert frozen == {str(p): digest(p) for p in source_files}, 'Production changed during QA'
    assert all(digest(repository / path) == value for path, value in frozen_production.items()), \
        'Frozen producer or historical MOU file changed during QA'
    report = {'status': 'passed', 'scope': 'Independent geometric, raster and encoding checks; no artistic or audience approval.',
              'dimensions': list(dimensions), 'fps': fps, 'duration': duration,
              'frames': count, 'silent': True, 'source_sha256': frozen,
              'frozen_production_and_history_sha256': frozen_production,
              'checker_sha256': digest(Path(__file__)),
              'contract_sha256': digest(args.contract),
              'video_sha256': digest(video), 'all_svg_frames_checked': count,
              'final_hold_frames': len(final_signatures), 'contacts': measured,
              'crumb_owner_changes': sum(a != b for a, b in zip(owners, owners[1:])),
              'transfer_emitted_geometry_jump': {'position_pixels': transfer_position_jump,
                                                 'linear_matrix_max_delta': transfer_orientation_jump,
                                                 'sampling_offset_seconds': 1.e-6},
              'feet_pose_counts': {key: len(values) for key, values in foot_signatures.items()},
              'mitten_svg_scale_determinants': {key: [min(values), max(values)]
                                              for key, values in hand_scale_determinants.items()},
              'fresh_encoded_image_comparisons': images,
              'limits': 'No continuous viewing, listening or emotional-recognition claim. Critique is separate.'}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'report': str(args.report),
                      'frames': count, 'contacts': len(measured), 'images': len(images)}))


if __name__ == '__main__':
    main()
