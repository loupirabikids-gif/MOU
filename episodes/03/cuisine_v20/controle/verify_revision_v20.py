"""Independent checks of the approved V20 costume and paper overflow revision.

This does not manufacture frames, change audio, or claim perceptual listening.
External V19/study comparisons are explicitly marked unavailable in a standalone
archive; internal checks still run and real failures are never skipped.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS = EP.parent/'cuisine_v19'
STUDY = EP.parent/'etudes_costume/chef_v1/MOU_chef_cuisine.png'
EXPECTED_RIG = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
EXPECTED_COSTUME = '39bd95eb065c632c16d345f244ba21d66a08e0395cbbbf4bc0cd8e4f952938bb'
EXPECTED_BASE_MIX = '8ddc8746a5ec7ae7d5914a29245eb1033982029c2e1b3b4fd1b7cb415ac5874a'
PRESERVED_FIELDS = ('torso', 'arms', 'pose', 'hands', 'actor_transform')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def pcm(path):
    with wave.open(str(path), 'rb') as source:
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (48000, 2, 2)
        return np.frombuffer(source.readframes(source.getnframes()), '<i2').reshape(-1, 2)


def ball_vertices(art, ball):
    """Read actual rendered path and affine transform instead of assuming a radius."""
    element = ET.fromstring(art._ball(ball['x'], ball['y'], ball['r'],
                                      ball['rotation'], ball['visual_seed']))
    transform = element.attrib['transform']
    tx, ty, degrees, sx, sy = map(float, re.findall(r'-?\d+(?:\.\d+)?', transform))
    values = list(map(float, re.findall(r'-?\d+(?:\.\d+)?', element[0].attrib['d'])))
    ca, sa = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return [(tx+ca*sx*x-sa*sy*y, ty+sa*sx*x+ca*sy*y)
            for x,y in zip(values[::2], values[1::2])]


def point_edge_distance(p, a, b):
    vx, vy = b[0]-a[0], b[1]-a[1]
    u = max(0., min(1., ((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)))
    return math.hypot(p[0]-a[0]-u*vx, p[1]-a[1]-u*vy)


def polygon_gap(a, b):
    return min(point_edge_distance(p, q, b[(j+1)%len(b)])
               for p in a for j,q in enumerate(b))


def scene_checks(renderer):
    timeline = renderer.TIMELINE
    frames = round(renderer.DURATION*renderer.FPS)
    previous_path = PREVIOUS/'sources/render.py'
    previous = module('revision_reference_v19', previous_path) if previous_path.is_file() else None
    counts, compared, sink_frames, visible, contact_frames = [], 0, 0, [], []
    fourth = {'x':renderer.art.BIN_CENTRES[3][0], 'y':renderer.art.BIN_CENTRES[3][1],
              'r':renderer.art.BIN_RADII[3], 'rotation':renderer.art.BIN_ROTATIONS[3],
              'visual_seed':renderer.art.BIN_VISUAL_SEEDS[3]}
    heap = ball_vertices(renderer.art, fourth)
    assert min(y for x,y in heap) < 1450., 'Heap does not extend above the rim'
    for i in range(frames):
        t = i/renderer.FPS
        state = renderer.animation.scene_state(t)
        counts.append(state['bin_count'])
        camera = renderer.camera_at(state['t'],state)
        vx,vy,vw,vh = camera
        assert vx >= -1.e-8 and vy >= -1.e-8 and vx+vw <= 1080.+1.e-8 and vy+vh <= 1920.+1.e-8, (t,camera,'Camera exits the approved decor')
        if previous:
            old = previous.animation.scene_state(t)
            for key in PRESERVED_FIELDS:
                assert state[key] == old[key], (t, key, 'Character acting changed')
            compared += 1
            if state['shot'] == 'sink':
                assert renderer.svg_at(t) == previous.svg_at(t), (t, 'Sink insert changed')
                sink_frames += 1
        ball = state.get('flying_ball') or state.get('floor_ball')
        if t >= timeline['cycles'][-1]['release']:
            assert ball and ball['id'] == 5 and ball['r'] == 22. and ball['visual_seed'] == 4
            vertices = ball_vertices(renderer.art, ball)
            vx, vy, vw, vh = camera
            bbox = [min(p[0] for p in vertices), min(p[1] for p in vertices),
                    max(p[0] for p in vertices), max(p[1] for p in vertices)]
            assert bbox[0]-3 >= vx and bbox[1]-3 >= vy and bbox[2]+3 <= vx+vw and bbox[3]+3 <= vy+vh, (t, bbox, 'Clipped final paper')
            visible.append(i)
            if state.get('overflow_phase') == 'heap_contact':
                gap = min(polygon_gap(vertices,heap), polygon_gap(heap,vertices))
                assert gap < .001, (t, gap, 'Rendered contours do not contact')
                contact_frames.append({'frame':i,'time':t,'contour_gap_world_units':gap})
        if t >= timeline['overflow']['settle']:
            assert state['bin_count'] == 4 and state.get('flying_ball') is None
            assert (state['floor_ball']['x'],state['floor_ball']['y']) == (325.,1805.)
        if 39.5 <= t < 40.25:
            assert state['shot'] == 'bin', (t, 'Close-up ends before the outcome')
        if t >= 40.25:
            assert state['shot'] == 'wide'
    assert counts == sorted(counts) and counts[-1] == 4
    assert len(contact_frames) == 2, contact_frames
    return {'frames':frames, 'external_v19_comparison': 'passed' if previous else 'unavailable',
            'character_frames_identical':compared, 'character_fields':list(PRESERVED_FIELDS),
            'sink_svg_frames_identical':sink_frames, 'final_bin_count':4,
            'fifth_paper_persistent_on_floor':True, 'final_paper_visible_frames':len(visible),
            'actual_svg_contour_contact_frames':contact_frames,
            'heap_above_rim':True, 'closeup_persists_to_seconds':40.25,
            'all_camera_viewports_inside_approved_decor':True}


def audio_checks():
    audio = EP/'audio'
    base_path = audio/'mix_reference_v19.wav'
    assert sha(base_path) == EXPECTED_BASE_MIX, 'Bundled baseline mix differs from V19'
    base, current = pcm(base_path), pcm(audio/'mix.wav')
    assert base.shape == current.shape == (1968000,2)
    a,b = round(39.85*48000), round(39.97*48000)
    assert np.array_equal(base[:a],current[:a])
    assert np.array_equal(base[b:],current[b:])
    assert not np.array_equal(base[a:b],current[a:b]), 'Floor cue is absent'
    provenance = json.loads((audio/'provenance_reference_v19.json').read_text())
    required = {e['file']:e['sha256'] for e in provenance['events']}
    parameters = provenance['background_music']['parameters']
    required.update({e['file']:e['sha256'] for e in parameters['stems']})
    required[parameters['unattenuated_reference']['file']] = parameters['unattenuated_reference']['sha256']
    for name,expected in required.items():
        assert sha(audio/name) == expected, (name, 'Retained sound changed')
        if (PREVIOUS/'audio'/name).is_file():
            assert sha(PREVIOUS/'audio'/name) == expected
    sound = module('independent_sound_v20', EP/'sources/son.py')
    event = next(e for e in json.loads((audio/'provenance.json').read_text())['events'] if e['name']=='c5_papier_sol')
    mono,_ = sound.make_sound(event['kind'],event['duration'],event['seed'])
    signal = sound.stereo(mono,event['peak_dbfs'],event['pan'])
    envelope = sound.envelope(len(base), .008, .035)[a:b,None]
    delta = np.rint(signal*sound.MASTER_GAIN_EXACT*envelope*32767.).astype(np.int32)
    assert np.array_equal(current[a:b].astype(np.int32)-base[a:b].astype(np.int32),delta)
    assert int(np.abs(current.astype(np.int32)).max()) < 32767
    changed = np.flatnonzero(np.any(base != current,axis=1))
    return {'baseline_mix_sha256':sha(base_path), 'current_mix_sha256':sha(audio/'mix.wav'),
            'identical_outside_seconds':[39.85,39.97], 'retained_wav_count':len(required),
            'retained_wavs_sha256':required, 'floor_contribution_reconstructed_exactly':True,
            'first_changed_second':float(changed[0]/48000),
            'last_changed_second':float(changed[-1]/48000),'no_clipping':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true',help='Also decode both actual final MP4 files.')
    args = parser.parse_args()
    report = {'status':'running','scope':'independent revision checks',
              'limits':'Numerical/source checks and native still comparison; no audio listening or audience test.',
              'corrected_pre_final_issue': {
                  'observed_failure_times_seconds':[38.916666666666664,38.958333333333336],
                  'observed_failure':'The final paper crossed above the original bin close-up viewport.',
                  'correction':'Only the last bin close-up uses maximum zoom 2.5 and centre (220,1536); preceding bin shots retain their original camera. The centre also keeps the viewport inside the approved decor.',
                  'verification':'All actual SVG contour vertices, with a 3-unit stroke margin, must remain in the current viewport on every final-paper frame. All camera viewports must remain in the approved decor.'}}
    destination = EP/'controle/audit_revision_v20.json'
    inputs = list((EP/'sources').glob('*.py'))+[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'audio/mix.wav']
    frozen = {str(p):sha(p) for p in inputs}
    try:
        renderer = module('revision_current_v20',EP/'sources/render.py')
        assert sha(ROOT/'mou_rig.py') == EXPECTED_RIG
        actual_costume = hashlib.sha256(renderer.costume.costume_svg().encode()).hexdigest()
        assert actual_costume == EXPECTED_COSTUME
        report['rig_sha256'] = EXPECTED_RIG
        report['approved_costume_svg_sha256'] = actual_costume
        fresh = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=renderer.svg_at(4.).encode()))).convert('RGB')
        if STUDY.is_file():
            approved = Image.open(STUDY).convert('RGB')
            assert fresh.size == approved.size and np.array_equal(np.asarray(fresh),np.asarray(approved)), 'Approved kitchen study differs from frame4s'
            report['approved_study_pixels_identical_at_4s'] = True
        else:
            report['approved_study_pixels_identical_at_4s'] = 'unavailable: external study not bundled'
        report['scene'] = scene_checks(renderer)
        report['audio'] = audio_checks()
        report['final_mp4_full_decode'] = 'not requested'
        if args.final:
            tested = []
            for name in ('MOU_Encore_une_feuille.mp4','MOU_Encore_une_feuille_muette.mp4'):
                path = EP/name
                subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(path),
                                '-map','0','-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                tested.append({'file':name,'sha256':sha(path),'full_decode_without_errors':True})
            report['final_mp4_full_decode'] = tested
        assert frozen == {str(p):sha(p) for p in inputs}, 'A production input changed during QA'
        report['production_inputs_unchanged'] = frozen
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed';report['error'] = f'{type(error).__name__}: {error}'
        destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        raise
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(destination),
                      'character_frames_identical':report['scene']['character_frames_identical'],
                      'sink_frames_identical':report['scene']['sink_svg_frames_identical'],
                      'contour_contact_frames':report['scene']['actual_svg_contour_contact_frames'],
                      'audio_identical_outside_seconds':report['audio']['identical_outside_seconds']},indent=2))


if __name__ == '__main__':
    main()
