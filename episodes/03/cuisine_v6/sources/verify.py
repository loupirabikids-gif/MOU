"""Contrôle les exports réels d'Encore une feuille et des images hors cache.

À lancer après le rendu final : ce programme ne fabrique aucun plan, n'appelle
pas le cache et ne remplace pas la critique artistique du montage.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction
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
import wave

import cairosvg
import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
W, H, FPS, DURATION, NFRAMES = 1080, 1920, 24, 30., 720
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
SAMPLE_TIMES = (.4, .75, 1.05, 1.45, 2.58, 3.6, 4.5, 6.8, 8.3, 8.7, 9.0, 9.15, 11.0, 14.85,
                15.2, 15.5, 15.7, 16.05, 16.75, 17.5, 18.7, 20.6, 21.85, 22.15, 22.3, 22.5,
                23.6, 24.8, 25.4, 26.3, 27.2, 28.25, 29.6)
MEAN_ERROR_LIMIT = 3.0


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            output.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def command(args):
    return subprocess.check_output(args, stderr=subprocess.PIPE)


def probe(path):
    return json.loads(command(['ffprobe', '-v', 'error', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', str(path)]))


def check_video(path, sound):
    data = probe(path)
    videos = [s for s in data['streams'] if s['codec_type'] == 'video']
    audios = [s for s in data['streams'] if s['codec_type'] == 'audio']
    assert len(videos) == 1 and len(audios) == int(sound), (str(path), 'stream count')
    assert len(data['streams']) == 1+int(sound), (str(path), 'unexpected stream')
    video = videos[0]
    assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p', video
    assert (video['width'], video['height']) == (W, H), video
    assert Fraction(video['r_frame_rate']) == FPS, video['r_frame_rate']
    assert Fraction(video['avg_frame_rate']) == FPS, video['avg_frame_rate']
    assert int(video['nb_read_frames']) == NFRAMES, video['nb_read_frames']
    assert int(video['nb_frames']) == NFRAMES, video['nb_frames']
    assert abs(float(video['duration'])-DURATION) < .001, video['duration']
    assert abs(float(data['format']['duration'])-DURATION) < .05, data['format']['duration']
    if sound:
        audio = audios[0]
        assert audio['codec_name'] == 'aac', audio
        assert (int(audio['sample_rate']), int(audio['channels'])) == (48000, 2), audio
        assert abs(float(audio['duration'])-DURATION) < .025, audio['duration']
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2',
        '-i', str(path), '-map', '0', '-f', 'null', '-'], check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return {'path': str(path.relative_to(ROOT)), 'file_sha256': digest(path),
            'size_bytes': path.stat().st_size, 'full_decode_without_errors': True,
            'streams': [{k: s[k] for k in ('codec_type', 'codec_name', 'width', 'height',
                'pix_fmt', 'r_frame_rate', 'avg_frame_rate', 'nb_frames', 'nb_read_frames',
                'duration', 'sample_rate', 'channels') if k in s} for s in data['streams']]}


def bitstream_digest(path):
    # Strip the MP4 container. The compressed H264 stream must be identical
    # after the AAC mux, not merely similar after decompression.
    raw = command(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
        '-c:v', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'h264', '-'])
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def load_renderer():
    path = EP/'sources/render.py'
    spec = importlib.util.spec_from_file_location('papier_verified_renderer', path)
    renderer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = renderer
    spec.loader.exec_module(renderer)
    return renderer


def source_checks():
    manifest_path = EP/'controle/sources_final.json'
    manifest = json.loads(manifest_path.read_text())
    frozen = manifest['sha256']
    assert frozen, 'final source manifest is empty'
    for name, expected in frozen.items():
        assert digest(Path(name)) == expected, (name, 'changed since final rendering')
    # All current scene authors must be covered by the render-time freeze.
    required = [EP/'sources'/name for name in ('animation.py', 'art.py', 'render.py')]
    required.append(EP/'chronologie.json')
    assert {str(p) for p in required}.issubset(frozen), 'incomplete final source freeze'
    assert digest(ROOT/'mou_rig.py') == RIG_SHA, 'canonical rig changed'
    # New acting may change native controls/rotation; the native arm drawing,
    # solver and previously corrected local shoulder join remain identical.
    baseline = EP.parent/'film/sources/animation.py'
    def definitions(path):
        tree = ast.parse(path.read_text())
        return {node.name: ast.dump(node, include_attributes=False)
                for node in tree.body if isinstance(node, ast.FunctionDef)}
    previous, current = definitions(baseline), definitions(EP/'sources/animation.py')
    preserved = ['controls', 'native_grip', 'world_grip', 'solve_arm',
                 'arm_linear_transform', '_connect_left_root', 'soften_left_root', 'draw_arm']
    for name in preserved:
        assert previous[name] == current[name], (name, 'native articulation altered')
    reference = json.loads((EP.parent/'test_remuer/controle/audit_structure.json').read_text())
    decor = reference['decor_files_unchanged']
    for name, expected in decor.items():
        assert digest(EP.parent/'decor'/name) == expected, (name, 'approved decor changed')
    timeline = json.loads((EP/'chronologie.json').read_text())
    assert (timeline['duration'], timeline['fps'], timeline['dimensions']) == (DURATION, FPS, [W, H])
    sound = json.loads((EP/'controle/audit_son.json').read_text())
    assert digest(EP/'sources/son.py') == sound['source_sha256'], 'sound source changed since synthesis'
    assert digest(EP/'audio/mix.wav') == sound['mix_sha256'], 'mix differs from sound audit'
    assert digest(EP/'chronologie.json') == sound['chronologie_sha256'], 'sound audit needs refresh for current timeline'
    return {'rig_sha256': RIG_SHA, 'native_arm_functions_identical_to_previous': preserved,
            'approved_decor_unchanged': decor,
            'render_frozen_sources': frozen, 'sound_source_sha256': sound['source_sha256'],
            'sound_audit_mix_sha256': sound['mix_sha256']}


def audio_check(video):
    path = EP/'audio/mix.wav'
    with wave.open(str(path), 'rb') as source:
        n = source.getnframes()
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (48000, 2, 2)
        assert n == round(48000*DURATION), (n, 'WAV duration')
        pcm = np.frombuffer(source.readframes(n), '<i2').reshape(-1, 2)
    clipped = int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767))
    assert clipped == 0, 'clipped PCM samples'
    reference = pcm.astype(np.float64)/32768.
    raw = command(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video),
        '-map', '0:a:0', '-t', str(DURATION), '-ar', '48000', '-ac', '2',
        '-c:a', 'pcm_f32le', '-f', 'f32le', '-'])
    decoded = np.frombuffer(raw, '<f4').reshape(-1, 2)
    assert decoded.shape == reference.shape, (decoded.shape, reference.shape, 'AAC coverage')
    assert np.isfinite(decoded).all() and float(np.abs(decoded).max()) < .999, 'clipped or invalid decoded AAC'
    # Detect attaching an old or offset sound mix. Lossy AAC is not expected
    # to reproduce each PCM sample; correspondence is assessed over the signal.
    a, b = reference.ravel(), decoded.astype(np.float64).ravel()
    correlation = float(np.dot(a, b)/math.sqrt(float(np.dot(a, a))*float(np.dot(b, b))))
    relative_rmse = float(np.sqrt(np.mean((a-b)**2))/np.sqrt(np.mean(a*a)))
    assert correlation > .90, ('AAC does not match current WAV', correlation)
    def db(v):
        return round(20.*math.log10(v), 6) if v else None
    return {'wav_sha256': digest(path), 'duration_seconds': n/48000.,
            'sample_rate': 48000, 'channels': 2, 'bits': 16,
            'wav_clipped_samples': clipped,
            'wav_peak_dbfs': db(float(np.abs(reference).max())),
            'decoded_aac_peak_dbfs': db(float(np.abs(decoded).max())),
            'wav_vs_decoded_aac_correlation_without_offset': correlation,
            'wav_vs_decoded_aac_relative_rmse': relative_rmse,
            'first_and_last_wav_frame_silent': bool(not pcm[0].any() and not pcm[-1].any())}


def decoded_samples(video, indices):
    select = 'select='+ '+'.join(f'eq(n\\,{index})' for index in indices)
    raw = command(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2', '-i', str(video),
        '-map', '0:v:0', '-vf', select, '-fps_mode', 'passthrough',
        '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    expected = len(indices)*W*H*3
    assert len(raw) == expected, ('unexpected decoded sample count', len(raw), expected)
    return np.frombuffer(raw, np.uint8).reshape(len(indices), H, W, 3)


def bbox_screen(rectangle, viewbox):
    x0, y0, x1, y1 = rectangle
    vx, vy, vw, vh = viewbox
    left, right = math.floor((x0-vx)*W/vw), math.ceil((x1-vx)*W/vw)
    top, bottom = math.floor((y0-vy)*H/vh), math.ceil((y1-vy)*H/vh)
    return [max(0, left), max(0, top), min(W, right), min(H, bottom)]


def fresh_image_checks(renderer, video):
    indices = sorted({min(NFRAMES-1, round(t*FPS)) for t in SAMPLE_TIMES})
    actual_frames = decoded_samples(video, indices)
    results, failures = [], []
    for index, actual in zip(indices, actual_frames):
        t = index/FPS
        svg = renderer.svg_at(t).encode()
        # Direct CairoSVG call, no rendered PNG, cached file or render_job.
        fresh_png = cairosvg.svg2png(bytestring=svg, output_width=W, output_height=H)
        fresh = np.asarray(Image.open(io.BytesIO(fresh_png)).convert('RGB'))
        assert fresh.shape == (H, W, 3)
        difference = np.abs(fresh.astype(np.int16)-actual.astype(np.int16))
        full_error = float(difference.mean())
        if full_error >= MEAN_ERROR_LIMIT:
            failures.append({'frame': index, 'roi': 'full_frame', 'mean_error': full_error})
        state = renderer.animation.scene_state(t)
        viewbox = renderer.camera_at(t, state)
        regions = {'faucet': (72, 1004, 247, 1169), 'bin': (40, 1410, 290, 1805),
                   'carrot_and_knife': (450, 1160, 820, 1415),
                   'paper_roll': (780, 1060, 965, 1368)}
        ax, ay, scale = state['actor_transform']
        regions['mouth'] = (ax+165.*scale, ay+290.*scale,
                            ax+245.*scale, ay+350.*scale)
        regions['apron'] = (ax+140.*scale, ay+335.*scale,
                            ax+280.*scale, ay+415.*scale)
        for side, (hx, hy) in state['hands'].items():
            regions['hand_'+side] = (hx-70., hy-70., hx+70., hy+70.)
        for side, (sx, sy) in renderer.animation.SHOULDERS.items():
            sx, sy = ax+sx*scale, ay+sy*scale
            regions['shoulder_'+side] = (sx-60., sy-60., sx+60., sy+60.)
        errors = {}
        for name, rectangle in regions.items():
            box = bbox_screen(rectangle, viewbox)
            left, top, right, bottom = box
            if right-left < 12 or bottom-top < 12:
                errors[name] = {'visible': False}
                continue
            error = float(difference[top:bottom, left:right].mean())
            errors[name] = {'visible': True, 'pixel_bbox': box,
                            'mean_abs_rgb_error_0_255': round(error, 6)}
            if error >= MEAN_ERROR_LIMIT:
                failures.append({'frame': index, 'roi': name, 'mean_error': error})
        results.append({'frame': index, 'time_seconds': t, 'shot': state['shot'],
            'phase': state.get('phase'), 'fresh_svg_sha256': hashlib.sha256(svg).hexdigest(),
            'fresh_png_sha256': hashlib.sha256(fresh_png).hexdigest(),
            'full_frame_mean_abs_rgb_error_0_255': round(full_error, 6), 'regions': errors})
    return {'samples': results, 'threshold_mean_abs_rgb_error_0_255': MEAN_ERROR_LIMIT,
            'failures': failures,
            'method': 'Frames decoded from final MP4 versus direct current SVG/CairoSVG render, independently of PNG cache. Clipped hand/faucet/bin regions are measured only when visible.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', type=Path, default=EP/'MOU_Encore_une_feuille.mp4')
    parser.add_argument('--silent', type=Path, default=EP/'MOU_Encore_une_feuille_muette.mp4')
    parser.add_argument('--report', type=Path, default=EP/'controle/audit_final.json')
    args = parser.parse_args()
    args.video, args.silent, args.report = (p.resolve() for p in (args.video, args.silent, args.report))
    report = {'status': 'in_progress', 'scope': 'final exports only',
        'dimensions': [W, H], 'fps': FPS, 'duration_seconds': DURATION,
        'expected_frames': NFRAMES,
        'limits': 'Technical deliverable, source freeze and cache checks. No claim of human listening, continuous viewing, comic success or user approval.'}
    atomic_json(args.report, report)
    try:
        tracked = [EP/'sources'/name for name in ('animation.py', 'art.py', 'render.py', 'son.py', 'verify.py')]
        tracked += [EP/'chronologie.json', ROOT/'mou_rig.py']
        before = {str(path): digest(path) for path in tracked}
        report['source_integrity'] = source_checks()
        report['sound_video'] = check_video(args.video, True)
        report['silent_video'] = check_video(args.silent, False)
        sound_bits, silent_bits = bitstream_digest(args.video), bitstream_digest(args.silent)
        assert sound_bits == silent_bits, 'sound and silent video bitstreams differ'
        report['identical_compressed_video_bitstreams'] = sound_bits
        report['audio'] = audio_check(args.video)
        renderer = load_renderer()
        report['uncached_frame_checks'] = fresh_image_checks(renderer, args.video)
        assert not report['uncached_frame_checks']['failures'], report['uncached_frame_checks']['failures']
        assert before == {str(path): digest(path) for path in tracked}, 'source changed during verification'
        report['tested_sources_sha256'] = before
        report['status'] = 'passed'
        atomic_json(args.report, report)
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        atomic_json(args.report, report)
        raise
    print(json.dumps({'status': report['status'], 'report': str(args.report),
        'frames': NFRAMES, 'duration_seconds': DURATION,
        'uncached_frame_samples': len(report['uncached_frame_checks']['samples']),
        'audio_correlation': report['audio']['wav_vs_decoded_aac_correlation_without_offset'],
        'sound_video_sha256': report['sound_video']['file_sha256'],
        'silent_video_sha256': report['silent_video']['file_sha256']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
