"""V30: preserve MOU's sounds, omit cooking and lower only the music by 6 dB.

The local hashed PCM bank is sufficient after initial bootstrapping. Production
uses Python/NumPy and WAV only; no synthesis, voice changes, AGC or normalization.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import wave

import numpy as np

EP = Path(__file__).resolve().parents[1]
OUT = EP / 'audio'
SR = 48000
SECONDS = 38.
SAMPLES = round(SR * SECONDS)
MUSIC_GAIN_DB = -6.
MUSIC_GAIN = 10. ** (MUSIC_GAIN_DB / 20.)
DELIVERY_GAIN_DB = 3.5
DELIVERY_GAIN = 10. ** (DELIVERY_GAIN_DB / 20.)
REMOVED = {'cuisson_progressive_v27', 'dernier_tsss_poele_v27'}
EXPECTED_NO_COOKING_PCM = '8f06edd457bca66d39a7079107d80a56f6b738fd660d7488818d4b5708d9e809'
LIMITS = ('No model listening is available. Timing, levels and exact PCM comparisons '
          'do not establish perceived audibility, comfort, naturalness or comic success.')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pcm_sha(signal):
    return hashlib.sha256(np.asarray(signal, dtype='<i2').tobytes()).hexdigest()


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as target:
            target.write(data)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_json(path, value):
    atomic_bytes(path, (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode())


def pcm(path):
    with wave.open(str(path), 'rb') as stream:
        assert (stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) == (SR, 2, 2)
        return np.frombuffer(stream.readframes(stream.getnframes()), '<i2').reshape(-1, 2).astype(np.int64)


def write_pcm(path, signal):
    signal = np.asarray(signal)
    assert signal.shape == (SAMPLES, 2) and np.abs(signal).max() < 32767
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    os.close(fd)
    try:
        with wave.open(name, 'wb') as stream:
            stream.setnchannels(2)
            stream.setsampwidth(2)
            stream.setframerate(SR)
            stream.writeframes(signal.astype('<i2').tobytes())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def envelope():
    result = np.ones(SAMPLES)
    attack, release = round(.008 * SR), round(.035 * SR)
    result[:attack] *= np.sin(np.linspace(0., np.pi / 2., attack)) ** 2
    result[-release:] *= np.cos(np.linspace(0., np.pi / 2., release)) ** 2
    return result


def master(signal):
    before = np.rint(np.asarray(signal) * envelope()[:, None]).astype(np.int32)
    return np.rint(before * DELIVERY_GAIN).astype(np.int32)


def bootstrap(base):
    """One-time input materialization; main() never needs the old episode."""
    base = Path(base).resolve()
    original_manifest = base / 'audio/provenance.json'
    meta = json.loads(original_manifest.read_text())
    assert (meta['sample_rate'], meta['channels'], meta['duration_seconds']) == (SR, 2, SECONDS)
    assert meta['delivery_gain_linear'] == DELIVERY_GAIN
    events = meta['events']
    assert len(events) == 63
    assert {e['name'] for e in events if e['kind'] in ('frying', 'last_pan_sizzle')} == REMOVED
    protected = [original_manifest, base / 'audio/mix.wav']
    protected += [base / 'audio' / e['file'] for e in events]
    frozen = {str(p): sha(p) for p in protected}
    original_sum = np.zeros((SAMPLES, 2), dtype=np.int64)
    retained_sum = np.zeros_like(original_sum)
    kept = []
    for event in events:
        source = base / 'audio' / event['file']
        assert sha(source) == event['sha256'], event['name']
        signal = pcm(source)
        assert signal.shape == (event['samples'], 2)
        a = event['start_sample']
        original_sum[a:a + len(signal)] += signal
        if event['name'] in REMOVED:
            continue
        retained_sum[a:a + len(signal)] += signal
        destination = OUT / 'inputs/cues' / source.name
        atomic_bytes(destination, source.read_bytes())
        kept.append({**event, 'file': destination.relative_to(OUT).as_posix(),
                     'v28_file': event['file'], 'input_pcm_unchanged': True})
    assert len(kept) == 61
    assert sha(base / 'audio/mix.wav') == meta['mix_sha256']
    assert np.array_equal(master(original_sum), pcm(base / 'audio/mix.wav'))
    assert pcm_sha(master(retained_sum)) == EXPECTED_NO_COOKING_PCM
    assert frozen == {str(p): sha(p) for p in protected}

    atomic_bytes(OUT / 'inputs/provenance_v28.json', original_manifest.read_bytes())
    supporting = []
    for name in ('partition_v27.json', 'partition_v27.mid'):
        source = base / 'audio' / name
        destination = OUT / 'inputs' / name
        atomic_bytes(destination, source.read_bytes())
        supporting.append({'file': destination.relative_to(OUT).as_posix(), 'sha256': sha(destination)})
    index = {
        'version': 1, 'source_episode': 'cuisine_v28',
        'source_release_commit': '45718cec9580e30a5f84ab21a9ae71dcd3a465a5',
        'original_manifest_file': 'inputs/provenance_v28.json',
        'original_manifest_sha256': sha(original_manifest),
        'events': kept, 'supporting_files': supporting,
        'removed': [{k: e[k] for k in ('name', 'kind', 'start', 'duration', 'sha256')}
                    for e in events if e['name'] in REMOVED],
        'bootstrap_verification': {
            'original_63_cues_reproduce_delivered_mix_exactly': True,
            'original_mix_wav_sha256': meta['mix_sha256'],
            'no_cooking_pcm_sha256': EXPECTED_NO_COOKING_PCM,
            'old_episode_inputs_unchanged': True},
        'licenses': [
            'assets/FluidR3_README.md', 'assets/NOTICE_FluidR3_COPYRIGHT.txt',
            'assets/FluidSynth_COPYRIGHT.txt', 'assets/paper_recordings/provenance.json',
            'assets/vocal_sources/provenance.json', 'assets/vocal_sources/CC0_LICENSE.txt'],
        'source_methods': {
            'music': 'Original score rendered through FluidSynth/FluidR3; partition and bank notices retained.',
            'water_whistle_utensils': 'Previously synthesized/softened MOU material, retained unchanged.',
            'paper': 'Recorded free materials adapted in V27; source notices and original processing retained.',
            'voice': 'Existing CC0 creature/breath adaptations; original author and recording method unverified.'},
        'limits': LIMITS}
    write_json(OUT / 'input_bank.json', index)


def db(value):
    value = float(value)
    return 20. * math.log10(value) if value > 0. else None


def rms(signal):
    data = np.asarray(signal, dtype=np.float64)
    return float(np.sqrt(np.mean(data * data)))


def metrics(signal):
    signal = np.asarray(signal)
    return {'rms_dbfs': db(rms(signal) / 32768.),
            'peak_dbfs': db(np.abs(signal).max() / 32768.),
            'clipped_samples': int(np.count_nonzero(np.abs(signal) >= 32767))}


def energy_anchor(signal, start):
    power = np.mean(np.asarray(signal, dtype=np.float64) ** 2, axis=1)
    window = round(.008 * SR)
    trace = np.sqrt(np.convolve(power, np.ones(window) / window, mode='valid'))
    peak = int(np.argmax(trace)) + window // 2
    onset = int(np.flatnonzero(trace >= .1 * trace.max())[0]) + window // 2
    centroid = float(np.sum(np.arange(len(signal)) * power) / np.sum(power))
    return {'peak_rms_8ms_seconds': start + peak / SR,
            'threshold_10pct_rms_seconds': start + onset / SR,
            'energy_centroid_seconds': start + centroid / SR,
            'method': '8ms sliding RMS / 10% of maximum; numeric anchors, not a listening assessment.'}


def main():
    index_path = OUT / 'input_bank.json'
    index = json.loads(index_path.read_text())
    events = index['events']
    assert len(events) == 61 and not any(e['name'] in REMOVED for e in events)
    assert sum(e['kind'] == 'background_music' for e in events) == 1
    assert sum(e['kind'] == 'mou_nonverbal' for e in events) == 5
    protected = [Path(__file__).resolve(), index_path]
    protected += [OUT / e['file'] for e in events]
    protected += [OUT / index['original_manifest_file']]
    protected += [OUT / item['file'] for item in index['supporting_files']]
    protected += [EP / name for name in index['licenses']]
    frozen = {str(p.relative_to(EP)): sha(p) for p in protected}
    assert sha(OUT / index['original_manifest_file']) == index['original_manifest_sha256']
    sums = {kind: np.zeros((SAMPLES, 2), dtype=np.int64)
            for kind in ('music_before', 'music', 'voice', 'foley_and_air')}
    voice_anchors = []
    for event in events:
        path = OUT / event['file']
        assert sha(path) == event['sha256'], event['name']
        data = pcm(path)
        assert data.shape == (event['samples'], 2)
        a = event['start_sample']
        b = a + len(data)
        assert 0 <= a < b <= SAMPLES
        if event['kind'] == 'background_music':
            sums['music_before'][a:b] += data
            sums['music'][a:b] += np.rint(data * MUSIC_GAIN).astype(np.int64)
        elif event['kind'] == 'mou_nonverbal':
            sums['voice'][a:b] += data
            voice_anchors.append({'name': event['name'], 'start': event['start'], 'duration': event['duration'],
                                  'intended_expression': event.get('intended_expression'),
                                  **energy_anchor(data, event['start'])})
        else:
            sums['foley_and_air'][a:b] += data
    before = master(sums['music_before'] + sums['voice'] + sums['foley_and_air'])
    assert pcm_sha(before) == EXPECTED_NO_COOKING_PCM
    mix = master(sums['music'] + sums['voice'] + sums['foley_and_air'])
    music_zero = np.all(sums['music_before'] == 0, axis=1)
    assert np.array_equal(before[music_zero], mix[music_zero])
    assert np.abs(mix).max() < 32767
    for a, b in ((32., 32.5), (37.25, 38.)):
        assert not mix[round(a * SR):round(b * SR)].any()
    write_pcm(OUT / 'mix.wav', mix)
    stems = []
    for name in ('music', 'voice', 'foley_and_air'):
        data = master(sums[name])
        path = OUT / 'stems' / f'{name}.wav'
        write_pcm(path, data)
        stems.append({'name': name, 'file': path.relative_to(OUT).as_posix(),
                      'sha256': sha(path), 'metrics': metrics(data),
                      'stage': 'Fixed delivery gain and original edge fade included; no independent normalization.'})

    ratios = []
    for voice in voice_anchors:
        a = round(voice['start'] * SR)
        b = a + round(voice['duration'] * SR)
        v = rms(sums['voice'][a:b])
        old = rms(sums['music_before'][a:b])
        new = rms(sums['music'][a:b])
        ratio = {'name': voice['name'], 'interval_seconds': [a / SR, b / SR],
                 'voice_rms_dbfs_before_master': db(v / 32768.),
                 'jazz_rms_dbfs_before': db(old / 32768.),
                 'jazz_rms_dbfs_after': db(new / 32768.),
                 'voice_pcm_and_gain_unchanged': True,
                 'jazz_is_silent': old == 0.}
        if old:
            ratio.update(voice_to_jazz_db_before=db(v / old), voice_to_jazz_db_after=db(v / new),
                         improvement_db=db(old / new),
                         gain_before_quantization_db=MUSIC_GAIN_DB)
            assert abs(ratio['improvement_db'] - 6.) < .02
        else:
            ratio.update(voice_to_jazz_db_before=None, voice_to_jazz_db_after=None,
                         improvement_db=None,
                         note='No music in this interval originally or now; a ratio to silence is not reported.')
            assert np.array_equal(before[a:b], mix[a:b])
        ratios.append(ratio)
    # Separate delivery-rounded stems differ by <=2 LSB from rounding their sum once.
    stem_sum = sum(master(sums[k]) for k in ('music', 'voice', 'foley_and_air'))
    stem_residual = int(np.abs(stem_sum - mix).max())
    assert stem_residual <= 3
    assert frozen == {str(p.relative_to(EP)): sha(p) for p in protected}
    provenance = {
        'revision': 30, 'title': 'Original MOU — no cooking, softer music',
        'duration_seconds': SECONDS, 'sample_rate': SR, 'channels': 2,
        'input_bank': 'input_bank.json', 'input_bank_sha256': sha(index_path),
        'removed_events': index['removed'], 'events': events,
        'additional_mix_gain': {'background_music_db': MUSIC_GAIN_DB,
                               'all_other_kinds_db': 0., 'constant_through_episode': True,
                               'cue_gain_quantization': 'round existing music PCM times 10**(-6/20) once before summing'},
        'delivery_gain_db': DELIVERY_GAIN_DB, 'delivery_gain_linear': DELIVERY_GAIN,
        'global_edge_fade_ms': [8, 35], 'new_ducking': False, 'new_normalization': False,
        'existing_music_dynamics': 'Retained as baked into original music PCM, including the old gentle wash dip.',
        'unchanged_voice_count': 5, 'retained_event_count': 61,
        'bootstrap_verification': index['bootstrap_verification'],
        'prior_no_cooking_pcm_sha256': EXPECTED_NO_COOKING_PCM,
        'pcm_identical_where_original_music_is_zero': True,
        'voice_music_ratios': ratios, 'voice_anchors': voice_anchors,
        'mix_sha256': sha(OUT / 'mix.wav'), 'mix_pcm_sha256': pcm_sha(mix),
        'mix_metrics': metrics(mix), 'stems': stems,
        'stem_sum_max_abs_residual_lsb': stem_residual,
        'stem_sum_note': 'Each stem receives the same master rounding; summing them may differ by a few LSB from rounding the summed mix once.',
        'exact_zero_intervals_seconds': [[32., 32.5], [37.25, 38.]],
        'source_sha256': frozen, 'reproduction': 'python sources/son.py', 'limits': LIMITS}
    write_json(OUT / 'provenance.json', provenance)
    write_json(OUT / 'gel_son.json', {
        'source_sha256': sha(__file__), 'input_bank_sha256': sha(index_path),
        'inputs_sha256': frozen, 'mix_sha256': provenance['mix_sha256'],
        'mix_pcm_sha256': provenance['mix_pcm_sha256'],
        'stems': {item['file']: item['sha256'] for item in stems},
        'provenance_sha256': sha(OUT / 'provenance.json'),
        'limits': LIMITS})
    print(json.dumps({'mix': str(OUT / 'mix.wav'), 'retained_events': 61, 'removed_cooking_events': 2,
                      'music_gain_db': MUSIC_GAIN_DB, 'mix_sha256': provenance['mix_sha256'],
                      'voice_music_improvements_db': [r['improvement_db'] for r in ratios],
                      'clipped_samples': provenance['mix_metrics']['clipped_samples']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bootstrap-from', type=Path, help='Initialize the local bank once from the preserved V28 folder.')
    args = parser.parse_args()
    if args.bootstrap_from is not None:
        assert not (OUT / 'input_bank.json').exists(), 'Input bank already exists; use it without bootstrapping.'
        bootstrap(args.bootstrap_from)
    main()
