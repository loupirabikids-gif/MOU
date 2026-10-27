"""MOU 01 — La dernière retouche : sept événements originaux, sans voix.

Synthèse locale Python/NumPy, 48 kHz stéréo PCM16. Les trois bips sont
identiques ; les frottements n'annoncent jamais le ratage. La dernière
traction continue visuellement dans un tiers de seconde de vrai silence.
Les durées indiquées comme 83/167/208 ms sont arrondies : les sources utilisent
respectivement 2/4/5 images à 24 i/s et donc un nombre entier d'échantillons.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sons'
SR = 48000
SEEDS = {'retouche_legere': 4101, 'retouche_finale': 4102,
         'mains_baissent': 4103, 'obturateur': 4104}


def raised_envelope(n: int, attack: float, release: float) -> np.ndarray:
    """Raccords progressifs au silence, sans clic numérique aux limites."""
    env = np.ones(n, dtype=np.float64)
    a = min(n, max(2, round(attack * SR)))
    r = min(n, max(2, round(release * SR)))
    env[:a] *= np.sin(np.linspace(0, math.pi / 2, a)) ** 2
    env[-r:] *= np.cos(np.linspace(0, math.pi / 2, r)) ** 2
    return env


def band_noise(n: int, low: float, high: float, seed: int) -> np.ndarray:
    """Bruit à fenêtre spectrale douce, sans dépendance SciPy."""
    data = np.random.default_rng(seed).standard_normal(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    mask = (1 - np.exp(-(freqs / low) ** 4)) * np.exp(-(freqs / high) ** 4)
    filtered = np.fft.irfft(np.fft.rfft(data) * mask, n)
    return filtered / max(float(np.sqrt(np.mean(filtered ** 2))), 1e-12)


def timer(length: float) -> np.ndarray:
    n = round(length * SR)
    t = np.arange(n) / SR
    tone = np.sin(math.tau * 880 * t) + .12 * np.sin(math.tau * 1760 * t)
    return tone * np.exp(-2.3 * t / length) * raised_envelope(n, .004, .015)


def rubbing(length: float, seed: int, low: float, high: float) -> np.ndarray:
    n = round(length * SR)
    # Frottement souple, non vocal et sans glissando de défaite.
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    return band_noise(n, low, high, seed) * env


def shutter() -> np.ndarray:
    """Clic de 80 ms : transitoire 8 ms, contacts mécaniques +24/+48 ms."""
    n = round(.080 * SR)
    result = np.zeros(n)
    rng = np.random.default_rng(SEEDS['obturateur'])
    for offset, length, gain, resonance in [(0., .008, 1., 1900),
                                          (.024, .014, .48, 1150),
                                          (.048, .018, .27, 740)]:
        j = round(offset * SR)
        m = round(length * SR)
        t = np.arange(m) / SR
        # Each component has its own deterministic seed drawn from seed4104.
        noise = band_noise(m, 650, 7200, int(rng.integers(0, 2**31)))
        pulse = .78 * noise + .22 * np.sin(math.tau * resonance * t)
        pulse *= np.exp(-4.5 * t / length) * raised_envelope(m, .0003, .002)
        result[j:j+m] += gain * pulse
    return result


def stereo(mono: np.ndarray, pan: float, peak_dbfs: float) -> np.ndarray:
    weights = np.sqrt([(1 - pan) / 2, (1 + pan) / 2])
    signal = mono[:, None] * weights[None, :]
    signal -= signal.mean(axis=0, keepdims=True)
    signal *= raised_envelope(len(mono), .0002, .001)[:, None]
    signal *= 10 ** (peak_dbfs / 20) / max(float(np.max(np.abs(signal))), 1e-12)
    return signal


def write_wave(path: Path, data: np.ndarray) -> None:
    assert data.ndim == 2 and data.shape[1] == 2
    assert np.isfinite(data).all() and np.max(np.abs(data)) < 1
    pcm = np.round(data * 32767).astype('<i2')
    fd, temp_name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    os.close(fd)
    try:
        with wave.open(temp_name, 'wb') as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes(pcm.tobytes())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def write_json(path: Path, value: dict) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def db(value: float) -> float | None:
    return round(20 * math.log10(value), 3) if value > 0 else None


def read_pcm(path: Path) -> np.ndarray:
    with wave.open(str(path), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate()) == (2, 2, SR)
        return np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').reshape(-1, 2)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    timeline_path = ROOT / 'chronologie.json'
    timeline = json.loads(timeline_path.read_text(encoding='utf-8'))
    duration = float(timeline['duree_secondes'])
    fps = int(timeline['fps'])
    flash = float(timeline['flash_time'])
    assert round(flash * fps) == timeline['flash_frame']
    assert SR % fps == 0
    countdown = {e['number']: float(e['time']) for e in timeline['countdown']}
    silence = timeline['audio_silence_before_flash']
    silence_start = float(silence['start'])
    photo_start, photo_end = [float(timeline['photo_hold'][k]) for k in ('start', 'end')]
    # Onsets for timer3/2/1 come from the common timeline. Mechanical effects
    # use agreed frame coordinates so they remain exact at sample precision.
    beep = timer(2 / fps)
    events = []
    for number in (3, 2, 1):
        events.append((f'timer_{number}', countdown[number], beep.copy(), 0., -16.,
                       {'type': 'sinus_harmonique', 'frequency_hz': 880,
                        'harmonic_hz': 1760, 'harmonic_relative_gain': .12,
                        'duration_seconds': len(beep) / SR}))
    events += [
        ('retouche_legere', 86 / fps,
         rubbing(5 / fps, SEEDS['retouche_legere'], 230, 1700), .10, -27.,
         {'type': 'bruit_filtre_en_cloche', 'band_hz': [230, 1700],
          'duration_seconds': 5 / fps, 'seed': SEEDS['retouche_legere']}),
        ('retouche_finale', 142 / fps,
         rubbing(4 / fps, SEEDS['retouche_finale'], 230, 1800), .10, -24.,
         {'type': 'bruit_filtre_en_cloche', 'band_hz': [230, 1800],
          'duration_seconds': 4 / fps, 'seed': SEEDS['retouche_finale']}),
        ('obturateur', flash, shutter(), 0., -6.,
         {'type': 'transitoire_et_deux_contacts_mecaniques',
          'main_transient_seconds': .008, 'secondary_offsets_seconds': [.024, .048],
          'duration_seconds': .08, 'seed': SEEDS['obturateur']}),
        ('mains_baissent', 236 / fps,
         rubbing(4 / fps, SEEDS['mains_baissent'], 220, 1400), .10, -29.,
         {'type': 'froissement_discret', 'band_hz': [220, 1400],
          'duration_seconds': 4 / fps, 'seed': SEEDS['mains_baissent']}),
    ]
    events.sort(key=lambda e: e[1])
    mix = np.zeros((round(duration * SR), 2), dtype=np.float64)
    manifest = {
        'episode': 'MOU 01 — ' + timeline['titre'], 'revision': timeline['revision'],
        'revision_note': 'Sept événements : trois bips identiques, deux frottements de retouche, un déclencheur et un froissement de mains. Aucun son de ratage ni accent de honte.',
        'provenance': 'Créations procédurales originales synthétisées localement par sources/son.py ; aucun échantillon, enregistrement, service ni banque externe.',
        'outils': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard Python)'],
        'voice': False, 'continuous_music': False,
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16,
        'duration_seconds': duration, 'random_seeds': SEEDS,
        'chronologie_sha256': hashlib.sha256(timeline_path.read_bytes()).hexdigest(),
        'synchronisation': {'fps': fps, 'flash_frame': timeline['flash_frame'],
                            'flash_sample': round(flash * SR),
                            'durations': '83/167/208 ms arrondis ; 2/4/5 images exactes à 24 i/s'},
        'events': [], 'unused_bank': [],
        'limite': 'Contrôle numérique uniquement ; aucune écoute humaine sur appareil mobile n’est revendiquée.',
    }
    for name, start, mono, pan, peak_dbfs, parameters in events:
        signal = stereo(mono, pan, peak_dbfs)
        j = round(start * SR)
        stop = j + len(signal)
        assert stop <= len(mix)
        mix[j:stop] += signal
        write_wave(OUT / (name + '.wav'), signal)
        manifest['events'].append({
            'name': name, 'file': name + '.wav', 'start_seconds': start,
            'start_sample': j, 'end_seconds': stop / SR, 'samples': len(signal),
            'pan': pan, 'peak_dbfs': db(float(np.max(np.abs(signal)))),
            'parameters': parameters,
        })
    # Historical WAVs remain in the repository as a bank, never in this mix.
    active = {name + '.wav' for name, *_ in events} | {'mix.wav'}
    for p in sorted(OUT.glob('*.wav')):
        if p.name not in active:
            manifest['unused_bank'].append({
                'file': p.name, 'used_in_mix': False,
                'reason': 'Banque historique V1–V3 conservée, non régénérée ni utilisée par le mix V4.',
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    assert len(events) == 7
    assert np.isfinite(mix).all()
    assert not mix[round(silence_start * SR):round(flash * SR)].any()
    assert not mix[round(photo_start * SR):round(photo_end * SR)].any()
    assert 10 ** (-7 / 20) <= float(np.max(np.abs(mix))) <= 10 ** (-5 / 20)
    write_wave(OUT / 'mix.wav', mix)
    pcm = read_pcm(OUT / 'mix.wav')
    assert len(pcm) == round(duration * SR)
    decoded = pcm.astype(np.float64) / 32768
    timers = [read_pcm(OUT / f'timer_{n}.wav') for n in (3, 2, 1)]
    assert all(np.array_equal(timers[0], t) for t in timers[1:])
    assert all(round(countdown[n] * SR) - round(countdown[n+1] * SR) == SR for n in (2, 1))
    click_sample = round(flash * SR)
    click_window = np.abs(decoded[click_sample:click_sample+round(.02 * SR)]).max(axis=1)
    onset_sample = click_sample + int(np.argmax(click_window > .005))
    assert abs(onset_sample - click_sample) < round(.002 * SR)
    audit = {
        'revision': timeline['revision'], 'frames': len(decoded),
        'duration_seconds': len(decoded) / SR,
        'peak_dbfs': db(float(np.max(np.abs(decoded)))),
        'rms_dbfs_left_right': [db(float(v)) for v in np.sqrt(np.mean(decoded ** 2, axis=0))],
        'dc_mean_left_right': decoded.mean(axis=0).tolist(),
        'clipped_samples': int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767)),
        'silence_before_flash': {'start_seconds': silence_start, 'end_seconds': flash,
                                'exact_pcm_silence': not bool(pcm[round(silence_start * SR):click_sample].any())},
        'photo_hold_silent': {'start_seconds': photo_start, 'end_seconds': photo_end,
                             'exact_pcm_silence': not bool(pcm[round(photo_start * SR):round(photo_end * SR)].any())},
        'flash_frame': timeline['flash_frame'], 'flash_sample': click_sample,
        'decoded_click_onset_sample': onset_sample,
        'decoded_click_onset_seconds': onset_sample / SR,
        'timer_wavs_identical': True, 'timer_interval_samples': SR,
        'event_count': len(events),
        'mix_sha256': hashlib.sha256((OUT / 'mix.wav').read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'reproduction': 'Depuis la racine MOU : .venv/bin/python episodes/01/sources/son.py',
        'limite': 'Contrôles numériques PCM et synchronisation ; sans écoute sur appareil mobile ni test public.',
    }
    assert audit['clipped_samples'] == 0
    write_json(OUT / 'provenance_et_parametres.json', manifest)
    write_json(OUT / 'audit_son.json', audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
