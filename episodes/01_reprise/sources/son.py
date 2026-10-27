"""Le retardateur — neuf événements originaux, dont deux hé soufflés.

Synthèse locale Python/NumPy. Tap, éclat de vanité, trois bips identiques,
souffle, déclencheur et deux vocalisations aspirées. La chute, la photo et la
dernière demi-seconde restent silencieuses.
Les noyaux de bruit/son reprennent les sources locales du projet MOU ; aucun
échantillon ni service de production externe n'intervient.
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
SEEDS = {'tap': 6101, 'souffle': 6102, 'obturateur': 6104,
         'he_1': 6131, 'he_2': 6132}


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


def tap() -> np.ndarray:
    """Contact doux sur écran, distinct du clic mécanique de photographie."""
    length = .045
    n = round(length * SR)
    t = np.arange(n) / SR
    noise = band_noise(n, 320, 2400, SEEDS['tap'])
    rounded = .75 * noise + .25 * np.sin(math.tau * 240 * t)
    return rounded * np.exp(-3.8 * t / length) * raised_envelope(n, .002, .014)


def vanity_glint() -> np.ndarray:
    """Deux tintements brefs accompagnent l'éclat visible, sans mélodie."""
    length = .20
    n = round(length * SR)
    result = np.zeros(n)
    for start, freq, gain in [(0., 1480., 1.), (.048, 2210., .65)]:
        j = round(start * SR)
        t = np.arange(n-j) / SR
        bell = np.sin(math.tau * freq * t)
        bell += .20 * np.sin(math.tau * freq * 2.73 * t)
        bell *= np.exp(-t / .033) * raised_envelope(len(t), .0025, .025)
        result[j:] += gain * bell
    return result * raised_envelope(n, .0025, .025)


def breath() -> np.ndarray:
    """Souffle d'air non vocal de200ms ; aucune syllabe ni annonce de chute."""
    length = .20
    n = round(length * SR)
    t = np.arange(n) / SR
    air = band_noise(n, 180, 2100, SEEDS['souffle'])
    env = np.sin(math.pi * t / length) ** 1.6
    return air * env * raised_envelope(n, .016, .05)


def nervous_he(length: float, index: int) -> np.ndarray:
    """Petit /hɛ/ aspiré, synthèse originale source-filtre, sans voix tierce.

    Une expiration initiale précède une voyelle courte et peu voisée. Les
    résonances ɛ donnent une couleur vocale plutôt qu'un bip. La deuxième
    tentative descend légèrement et s'éteint plus vite, sans rire expansif.
    """
    n = round(length * SR)
    t = np.arange(n) / SR
    start_f0 = 214. if index == 1 else 202.
    f0 = start_f0 - 19. * t / length
    f0 += 1.8 * np.sin(math.tau * 8.7 * t)
    phase = math.tau * np.cumsum(f0) / SR
    formants = [(620., 105., 1.), (1780., 145., .68), (2500., 190., .32)]

    def response(freq):
        # Smooth Lorentzian resonances preserve aspiration between harmonics.
        return sum(gain / (1. + ((freq-centre)/bandwidth)**2)
                   for centre, bandwidth, gain in formants)

    voice = np.zeros(n, dtype=np.float64)
    for harmonic in range(1, 33):
        freq = harmonic * f0
        amplitude = response(freq) / harmonic ** .95
        voice += amplitude * np.sin(harmonic * phase - .17 * harmonic)
    voice /= max(float(np.sqrt(np.mean(voice ** 2))), 1e-12)
    air = band_noise(n, 140., 4300., SEEDS[f'he_{index}'])
    freqs = np.fft.rfftfreq(n, 1 / SR)
    air = np.fft.irfft(np.fft.rfft(air) * response(freqs), n)
    air /= max(float(np.sqrt(np.mean(air ** 2))), 1e-12)
    # Initial unvoiced /h/ (about35ms), then breathy ɛ with no hard attack.
    voiced_gate = np.clip((t-.028)/.030, 0., 1.)
    voiced_gate = voiced_gate ** 2 * (3.-2.*voiced_gate)
    envelope = np.sin(math.pi * t / length) ** 1.3
    envelope *= np.exp(-1.1 * t / length)
    aspiration = .80 * np.exp(-t/.070) + .24
    return ((.72 * voice * voiced_gate + aspiration * air) * envelope
            * raised_envelope(n, .012, .055))


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
    beep = timer(2 / fps)
    events = [
        ('tap_ecran', .90, tap(), 0., -24.,
         {'type': 'contact_ecran_mat', 'duration_seconds': .045,
          'band_hz': [320, 2400], 'resonance_hz': 240, 'seed': SEEDS['tap']}),
        ('vanite_eclat', 2.20, vanity_glint(), .10, -20.,
         {'type': 'deux_tintements', 'fundamentals_hz': [1480, 2210],
          'second_offset_seconds': .048, 'duration_seconds': .20}),
        ('souffle', 5.20, breath(), 0., -23.,
         {'type': 'souffle_air_non_vocal', 'band_hz': [180, 2100],
          'duration_seconds': .20, 'seed': SEEDS['souffle']}),
        ('obturateur', flash, shutter(), 0., -6.,
         {'type': 'transitoire_et_deux_contacts_mecaniques',
          'main_transient_seconds': .008, 'secondary_offsets_seconds': [.024, .048],
          'duration_seconds': .08, 'seed': SEEDS['obturateur']}),
    ]
    for number in (3, 2, 1):
        events.append((f'timer_{number}', countdown[number], beep.copy(), 0., -16.,
                       {'type': 'sinus_harmonique', 'frequency_hz': 880,
                        'harmonic_hz': 1760, 'harmonic_relative_gain': .12,
                        'duration_seconds': len(beep) / SR}))
    for index, event in enumerate(timeline['reaction']['laughs'], 1):
        events.append((f'he_nerveux_{index}', float(event['start']),
                       nervous_he(float(event['duration']), index), 0.,
                       -20.5 if index == 1 else -22.,
                       {'type': 'vocalisation_procedurale_h_e_ouvert_aspire',
                        'phonetic_intention': 'hɛ', 'duration_seconds': event['duration'],
                        'f0_start_hz': 214 if index == 1 else 202,
                        'f0_fall_hz': 19, 'aspiration_before_voicing_seconds': .028,
                        'formants_hz': [620, 1780, 2500],
                        'formant_bandwidths_hz': [105, 145, 190],
                        'seed': SEEDS[f'he_{index}'],
                        'acting': 'petit rire nerveux soufflé ; deuxième tentative plus faible'}))
    events.sort(key=lambda e: e[1])
    mix = np.zeros((round(duration * SR), 2), dtype=np.float64)
    manifest = {
        'episode': 'MOU — ' + timeline['titre'] + ' — nouvelle réalisation',
        'revision': timeline['revision'],
        'revision_note': 'Les sept bruitages avant et pendant le clic sont conservés. Deux hé aspirés brefs accompagnent exactement les micro-secousses de fin prévues par la chronologie ; photo et dernière demi-seconde silencieuses.',
        'provenance': 'Créations procédurales originales synthétisées localement par sources/son.py. Noyaux de synthèse issus des sources locales MOU ; aucun échantillon, enregistrement, service ni banque externe.',
        'outils': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard Python)'],
        'voice': True,
        'voice_description': 'Deux vocalisations hɛ originales synthétisées par source-filtre NumPy ; ni enregistrement humain, ni TTS, ni modèle vocal téléchargé. Intention hé soufflé, naturel vocal non garanti par un contrôle numérique.',
        'continuous_music': False,
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16,
        'duration_seconds': duration, 'random_seeds': SEEDS,
        'chronologie_sha256': hashlib.sha256(timeline_path.read_bytes()).hexdigest(),
        'synchronisation': {'fps': fps, 'flash_frame': timeline['flash_frame'],
                            'flash_sample': round(flash * SR),
                            'timer_duration_frames': 2,
                            'timer_interval_samples': SR,
                            'coordination': 'Appui0,90s et éclat2,20s convenus avec le réalisateur ; revue du montage distincte dans controle/.'},
        'events': [], 'unused_bank': [],
        'limite': 'Contrôle numérique uniquement ; aucune écoute humaine ni sur appareil mobile revendiquée.',
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
    active = {name + '.wav' for name, *_ in events} | {'mix.wav'}
    for p in sorted(OUT.glob('*.wav')):
        if p.name not in active:
            manifest['unused_bank'].append({'file': p.name, 'used_in_mix': False,
                                           'reason': 'Effet non retenu dans ce montage.',
                                           'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    assert len(events) == 9
    assert np.isfinite(mix).all()
    assert not mix[round(silence_start * SR):round(flash * SR)].any()
    assert not mix[round(photo_start * SR):round(photo_end * SR)].any()
    assert not mix[round(5.75 * SR):round(flash * SR)].any()
    final_start = float(timeline['reaction']['final_hold_start'])
    final_end = float(timeline['reaction']['final_hold_end'])
    assert not mix[round(final_start * SR):round(final_end * SR)].any()
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
        'episode': '01_reprise', 'revision': timeline['revision'],
        'frames': len(decoded), 'duration_seconds': len(decoded) / SR,
        'peak_dbfs': db(float(np.max(np.abs(decoded)))),
        'rms_dbfs_left_right': [db(float(v)) for v in np.sqrt(np.mean(decoded ** 2, axis=0))],
        'dc_mean_left_right': decoded.mean(axis=0).tolist(),
        'clipped_samples': int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767)),
        'silence_before_flash': {'start_seconds': silence_start, 'end_seconds': flash,
                                'exact_pcm_silence': not bool(pcm[round(silence_start * SR):click_sample].any())},
        'silent_fall_5_75_to_6': not bool(pcm[round(5.75 * SR):click_sample].any()),
        'photo_hold_silent': {'start_seconds': photo_start, 'end_seconds': photo_end,
                             'exact_pcm_silence': not bool(pcm[round(photo_start * SR):round(photo_end * SR)].any())},
        'flash_frame': timeline['flash_frame'], 'flash_sample': click_sample,
        'decoded_click_onset_sample': onset_sample,
        'decoded_click_onset_seconds': onset_sample / SR,
        'timer_wavs_identical': True, 'timer_interval_samples': SR,
        'event_count': len(events),
        'laughs': [{'start_seconds': event['start'], 'duration_seconds': event['duration'],
                    'start_frame': round(event['start'] * fps),
                    'start_sample': round(event['start'] * SR),
                    'peak_dbfs': db(float(np.max(np.abs(read_pcm(OUT / f'he_nerveux_{i}.wav').astype(float)/32768))))}
                   for i, event in enumerate(timeline['reaction']['laughs'], 1)],
        'final_hold_silent': {'start_seconds': final_start, 'end_seconds': final_end,
                              'exact_pcm_silence': not bool(pcm[round(final_start * SR):round(final_end * SR)].any())},
        'mix_sha256': hashlib.sha256((OUT / 'mix.wav').read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'reproduction': 'Depuis la racine MOU : .venv/bin/python episodes/01_reprise/sources/son.py',
        'limite': 'Contrôles numériques PCM et synchronisation ; aucune écoute humaine sur appareil mobile ni test public.',
    }
    assert audit['clipped_samples'] == 0
    write_json(OUT / 'provenance_et_parametres.json', manifest)
    write_json(OUT / 'audit_son.json', audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
