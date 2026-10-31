"""Re-export the original MOU V28, removing only its two cooking cues.

Read the delivered PCM cues rather than resynthesizing any sound. Preserve
their timing, original master fade and fixed delivery gain. Copy H.264 as-is.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
BASE = ROOT / 'episodes/03/cuisine_v28'
REMOVED = {'cuisson_progressive_v27', 'dernier_tsss_poele_v27'}
EXPECTED_PCM_SHA = '8f06edd457bca66d39a7079107d80a56f6b738fd660d7488818d4b5708d9e809'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_pcm(path, rate):
    with wave.open(str(path), 'rb') as stream:
        assert (stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) == (rate, 2, 2)
        return np.frombuffer(stream.readframes(stream.getnframes()), '<i2').reshape(-1, 2).astype(np.int64)


def write_pcm(path, signal, rate):
    assert np.abs(signal).max() < 32767
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes(signal.astype('<i2').tobytes())


def video_digest(path):
    raw = subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
        '-c:v', 'copy', '-f', 'hash', '-hash', 'sha256', '-'])
    return raw.decode().strip()


def main():
    manifest = BASE / 'audio/provenance.json'
    meta = json.loads(manifest.read_text())
    rate = meta['sample_rate']
    frames = round(meta['duration_seconds'] * rate)
    events = meta['events']
    assert len(events) == 63
    assert {e['name'] for e in events if e['kind'] in ('frying', 'last_pan_sizzle')} == REMOVED
    source_video = BASE / 'MOU_Encore_une_feuille.mp4'
    protected = [manifest, BASE / 'audio/mix.wav', ROOT / 'mou_rig.py']
    protected += list(BASE.glob('*.mp4')) + list(BASE.glob('*.zip'))
    protected += [BASE / 'audio' / e['file'] for e in events]
    frozen = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    original_sum = np.zeros((frames, 2), dtype=np.int64)
    retained_sum = np.zeros_like(original_sum)
    removed_sum = np.zeros_like(original_sum)
    retained = []
    removed = []
    for event in events:
        path = BASE / 'audio' / event['file']
        assert sha(path) == event['sha256'], event['name']
        signal = read_pcm(path, rate)
        assert signal.shape == (event['samples'], 2)
        start = event['start_sample']
        end = start + len(signal)
        original_sum[start:end] += signal
        record = {k: event[k] for k in ('name', 'kind', 'file', 'sha256', 'start_sample', 'samples')}
        if event['name'] in REMOVED:
            removed_sum[start:end] += signal
            removed.append(record)
        else:
            retained_sum[start:end] += signal
            retained.append(record)
    assert len(retained) == 61 and len(removed) == 2

    # Exactly the global 8/35 ms edge envelope used in delivered V28 son.py.
    envelope = np.ones(frames)
    attack, release = round(.008 * rate), round(.035 * rate)
    envelope[:attack] *= np.sin(np.linspace(0, np.pi / 2, attack)) ** 2
    envelope[-release:] *= np.cos(np.linspace(0, np.pi / 2, release)) ** 2

    def master(signal):
        before = np.rint(signal * envelope[:, None]).astype(np.int32)
        return np.rint(before * meta['delivery_gain_linear']).astype(np.int32)

    original = read_pcm(BASE / 'audio/mix.wav', rate)
    assert sha(BASE / 'audio/mix.wav') == meta['mix_sha256']
    assert np.array_equal(master(original_sum), original), 'Original mix is not reproduced exactly'
    revised = master(retained_sum)
    unaffected = np.all(removed_sum == 0, axis=1)
    assert np.array_equal(revised[unaffected], original[unaffected])
    pcm_sha = hashlib.sha256(revised.astype('<i2').tobytes()).hexdigest()
    assert pcm_sha == EXPECTED_PCM_SHA, 'Independent audio audit does not match'
    for a, b in ((32., 32.5), (37.25, 38.)):
        assert not revised[round(a * rate):round(b * rate)].any()

    private = ROOT / 'work/cuisine_v28_sans_cuisson'
    private.mkdir(parents=True, exist_ok=True)
    wav = private / 'mix_sans_cuisson.wav'
    write_pcm(wav, revised, rate)
    output = HERE / 'MOU_Encore_une_feuille_sans_cuisson.mp4'
    fd, name = tempfile.mkstemp(prefix='.rendu-', suffix='.mp4', dir=HERE)
    os.close(fd)
    try:
        subprocess.run([
            'ffmpeg', '-y', '-v', 'error', '-i', str(source_video), '-i', str(wav),
            '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy', '-c:a', 'aac',
            '-b:a', '160k', '-t', str(meta['duration_seconds']),
            '-movflags', '+faststart', name], check=True)
        assert video_digest(name) == video_digest(source_video)
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', name]))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        assert (video['width'], video['height'], video['r_frame_rate'], video['nb_frames']) == (1080, 1920, '24/1', '912')
        assert float(video['duration']) == float(audio['duration']) == 38.
        assert int(audio['sample_rate']) == rate
        subprocess.run(['ffmpeg', '-v', 'error', '-i', name, '-f', 'null', '-'], check=True)
        assert frozen == {str(p.relative_to(ROOT)): sha(p) for p in protected}
        os.replace(name, output)
    finally:
        if os.path.exists(name):
            os.unlink(name)

    report = {
        'base': str(BASE.relative_to(ROOT)),
        'base_release_commit': '45718cec9580e30a5f84ab21a9ae71dcd3a465a5',
        'character': 'Original MOU with continuous arms, not Galet',
        'removed_events': removed, 'retained_events': retained,
        'retained_cue_pcm_gains_and_timing_unchanged': True,
        'original_mix_reconstructed_bit_exact': True,
        'pcm_unchanged_outside_removed_contributions': True,
        'fixed_delivery_gain_db': meta['delivery_gain_db'],
        'new_normalization': False, 'global_edge_fade_ms': [8, 35],
        'wav_sha256': sha(wav), 'pcm_sha256': pcm_sha,
        'independent_audit_pcm_match': True,
        'clipped_pcm_samples': int(np.count_nonzero(np.abs(revised) >= 32767)),
        'exact_silences_s': [[32., 32.5], [37.25, 38.]],
        'identical_video_stream': video_digest(output),
        'video': {'width': 1080, 'height': 1920, 'fps': 24, 'frames': 912, 'seconds': 38},
        'aac': {'bitrate_requested': 160000, 'sample_rate': rate, 'channels': 2},
        'output': {'file': output.name, 'sha256': sha(output), 'bytes': output.stat().st_size},
        'original_files_preserved': True, 'source_sha256': frozen,
        'limits': 'Numerical and stream checks; no model listening or artistic quality claim.'}
    (HERE / 'CONTROLE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('output', 'identical_video_stream', 'independent_audit_pcm_match', 'original_files_preserved')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
