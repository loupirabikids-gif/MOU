"""Check reordered cooking continuity against the delivered V11.

Run with the project Python from a Git checkout containing the baseline commit.
This audit reads the emitted scene states and SVG, independently of PNG caches.
It does not claim perceptual listening or audience comprehension.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
BASE = '0e74c619b2791cd813aae4200ebb790bd301286c'
FPS, FRAMES = 24, 840


def digest(data):
    return hashlib.sha256(data).hexdigest()


def historical(name):
    return subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def definitions(source):
    return {n.name: ast.dump(n, include_attributes=False)
            for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}


def near(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1.e-10, abs_tol=1.e-7)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(near(a[k], b[k]) for k in a)
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        return len(a) == len(b) and all(near(x, y) for x, y in zip(a, b))
    return a == b


def old_frame(index):
    # Chronological comparison chosen independently from the new timeline:
    # approved carrot performance moves earlier, ordinal ritual two shifts,
    # approved tomato performance moves later; all other action stays put.
    if 324 <= index < 396:
        return index+156
    if 396 <= index < 516:
        return index-36
    if 516 <= index < 552:
        return index-192
    return index


def baseline_renderer(folder):
    names = ['mou_rig.py', 'fonts/DejaVuSans-Bold.ttf',
             'episodes/03/test_remuer/sources/animation.py',
             'episodes/03/decor/MOU_cuisine_decor.svg',
             'episodes/03/cuisine_v6/chronologie.json']
    names += ['episodes/03/cuisine_v6/sources/'+n
              for n in ('animation.py', 'art.py', 'render.py')]
    for name in names:
        path = folder/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(historical(name))
    return load(folder/'episodes/03/cuisine_v6/sources/render.py', 'v11_order_baseline_renderer')


def main():
    report_path = EP/'controle/audit_ordre_v12.json'
    report = {'status': 'in_progress', 'baseline_commit': BASE,
              'scope': 'Scene state, native performance preservation and prop continuity; no PNG cache, audio listening or audience validation.'}
    try:
        tracked = [ROOT/'mou_rig.py', ROOT/'fonts/DejaVuSans-Bold.ttf',
                   ROOT/'episodes/03/test_remuer/sources/animation.py',
                   EP/'chronologie.json']
        tracked += [EP/'sources'/n for n in ('animation.py', 'art.py', 'render.py')]
        frozen = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in tracked}
        preserved = {}
        for name in ('mou_rig.py', 'fonts/DejaVuSans-Bold.ttf',
                     'episodes/03/test_remuer/sources/animation.py',
                     'episodes/03/cuisine_v6/sources/art.py'):
            value = (ROOT/name).read_bytes()
            assert value == historical(name), ('unrequested model/art change', name)
            preserved[name] = digest(value)
        old_defs = definitions(historical('episodes/03/cuisine_v6/sources/animation.py'))
        new_defs = definitions((EP/'sources/animation.py').read_text())
        native = ['controls', 'native_grip', 'world_grip', 'solve_arm',
                  'arm_linear_transform', '_connect_left_root', 'soften_left_root', 'draw_arm']
        assert all(old_defs[name] == new_defs[name] for name in native), 'native arm geometry changed'
        timeline = json.loads((EP/'chronologie.json').read_text())
        assert (timeline['duration'], timeline['fps'], timeline['dimensions']) == (35., 24, [1080, 1920])
        cycles = timeline['cycles']
        assert [c['id'] for c in cycles] == [1, 2, 3, 4]
        assert cycles[1]['trigger'] == 'découper une carotte'
        assert cycles[2]['trigger'] == 'ajouter une tomate'
        assert [c['trigger_start'] for c in cycles] == [0., 13.5, 21.5, 27.]
        assert timeline['carrot']['cut_times'] == [14.55, 15.25]
        assert timeline['cooking_events']['tomato_contact'] == 22.3
        assert timeline['background_music']['windows'] == [[0., 7.75], [13.5, 16.5], [21.5, 23.], [27., 28.]]
        current = load(EP/'sources/render.py', 'v12_order_current_renderer')
        acting_keys = ('shot', 'phase', 'actor_transform', 'hands', 'arm_meta',
                       'torso', 'arms', 'pose', 'spoon', 'spoon_held',
                       'water', 'lever', 'wet_hand', 'look_target')
        counts, stocks, cuts, same_svg, mapped_performances = [], [], [], [], 0
        camera_matches, paper_samples, flying_samples = 0, 0, 0
        with tempfile.TemporaryDirectory(prefix='mou_order_baseline_', dir='/tmp') as folder:
            old = baseline_renderer(Path(folder))
            for index in range(FRAMES):
                t, ref_t = index/FPS, old_frame(index)/FPS
                state, before = current.animation.scene_state(t), old.animation.scene_state(ref_t)
                for key in acting_keys:
                    assert near(state[key], before[key]), ('mapped native performance differs', index, key)
                mapped_performances += 1
                assert near(current.camera_at(t, state), old.camera_at(ref_t, before)), ('camera differs from preserved performance', index)
                camera_matches += 1
                counts.append(state['bin_count'])
                stocks.append(float(state['roll']['remaining']))
                cuts.append(int(state['carrot']['cuts']))
                expected_count = sum(t >= c['land'] for c in cycles)
                assert state['bin_count'] == expected_count, ('ordinal bin count', index)
                expected_cuts = sum(t >= q for q in (14.55, 15.25))
                assert state['carrot']['cuts'] == expected_cuts, ('carrot cut persistence', index)
                assert bool(state['tomato_added']) == (t >= 22.3), ('tomato enters pan early/late', index)
                if t < 21.72:
                    assert state['tomato'] == current.animation.TOMATO_START, ('tomato disappears from dish early', index)
                elif t >= 22.3:
                    assert state['tomato'] is None, ('tomato duplicated after landing', index)
                if t >= 15.95:
                    assert not state['carrot']['knife_held'], ('knife not parked after cut', index)
                if state['paper'] is not None:
                    ordinal = state['cycle']
                    assert state['paper']['cycle'] == ordinal
                    assert state['paper']['r'] == (47., 53., 59., 22.)[ordinal-1]
                    paper_samples += 1
                if state['flying_ball'] is not None:
                    assert state['flying_ball']['r'] == (47., 53., 59., 22.)[state['cycle']-1]
                    flying_samples += 1
                svg = current.svg_at(t)
                tree = ET.fromstring(svg)
                assert sum(e.attrib.get('data-part') == 'hand' for e in tree.iter()) == 2, ('hand count', index)
                if not 324 <= index < 552:
                    assert svg == old.svg_at(t), ('scene outside reorder window differs', index)
                    same_svg.append(index)
        assert counts == sorted(counts) and counts[0] == 0 and counts[-1] == 4
        assert stocks == sorted(stocks, reverse=True) and stocks[0] == 1. and stocks[-1] == 0.
        assert cuts == sorted(cuts) and cuts[0] == 0 and cuts[-1] == 2
        assert len(same_svg) == 612
        assert frozen == {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in tracked}, 'source changed during audit'
        report.update(status='passed', tested_sources_sha256=frozen,
            preserved_files_sha256=preserved, preserved_native_arm_functions=native,
            scenes={'frames': FRAMES, 'mapped_native_performance_frames': mapped_performances,
                    'mapped_native_fields': list(acting_keys), 'camera_matches': camera_matches,
                    'untouched_full_svg_frames': len(same_svg),
                    'untouched_windows_seconds': [[0., 13.5], [23., 35.]],
                    'carrot_before_tomato': True, 'all_frames_have_two_hands': True},
            continuity={'bin_count_monotonic': True, 'bin_count_first_last': [counts[0], counts[-1]],
                        'roll_stock_monotonic_decreasing': True, 'roll_stock_first_last': [stocks[0], stocks[-1]],
                        'carrot_cuts_persist': True, 'cut_times_seconds': [14.55, 15.25],
                        'knife_parked_after_seconds': 15.95, 'tomato_on_dish_until_pickup_seconds': 21.72,
                        'tomato_added_seconds': 22.3, 'ordinal_paper_radius_samples': paper_samples,
                        'ordinal_flying_ball_radius_samples': flying_samples,
                        'radii_by_ritual': [47., 53., 59., 22.]},
            limits='Numeric/XML continuity and exact preserved scene/performance comparisons; actual encoded films require separate decode checks and independent visual critique.')
    except Exception as error:
        report.update(status='failed', error=f'{type(error).__name__}: {error}')
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        raise
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
