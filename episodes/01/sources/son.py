"""Sons originaux de MOU 01 — synthèse locale, sans banque ni enregistrement tiers.

Reproduire depuis n'importe quel dossier :
    /workspace/MOU/.venv/bin/python /workspace/MOU/episodes/01/sources/son.py

La chronologie de référence est ../chronologie.json. Les instants exprimés
ci-dessous sont convertis en indices entiers à 48 kHz ; aucune opération
n'étire les sons. Les accents laissent de vrais silences au montage.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'sons'
SR = 48000
DURATION = 14.0
SEED = 2710202601


def raised_envelope(n: int, attack: float, release: float) -> np.ndarray:
    """Raccords doux au silence, sans clic numérique aux limites."""
    env = np.ones(n, dtype=np.float64)
    a = min(n, max(2, round(attack * SR)))
    r = min(n, max(2, round(release * SR)))
    env[:a] *= np.sin(np.linspace(0, math.pi / 2, a)) ** 2
    env[-r:] *= np.cos(np.linspace(0, math.pi / 2, r)) ** 2
    return env


def band_noise(n: int, low: float, high: float, rng: np.random.Generator) -> np.ndarray:
    """Bruit filtré par une fenêtre spectrale douce ; pas de dépendance SciPy."""
    data = rng.standard_normal(n)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    mask = (1 - np.exp(-(freqs / low) ** 4)) * np.exp(-(freqs / high) ** 4)
    filtered = np.fft.irfft(np.fft.rfft(data) * mask, n)
    rms = np.sqrt(np.mean(filtered ** 2))
    return filtered / max(rms, 1e-12)


def oscillator(freq: np.ndarray) -> np.ndarray:
    return np.sin(math.tau * np.cumsum(freq) / SR)


def timer(freq: float, length: float) -> np.ndarray:
    n = round(length * SR)
    t = np.arange(n) / SR
    # Deux harmoniques retenues : timbre doux de petit appareil, pas une alarme.
    tone = np.sin(math.tau * freq * t) + .11 * np.sin(math.tau * 2 * freq * t)
    decay = np.exp(-2.6 * t / length)
    return tone * decay * raised_envelope(n, .004, .018)


def breath(rng: np.random.Generator) -> np.ndarray:
    length = .50
    n = round(length * SR)
    t = np.arange(n) / SR
    # Souffle non vocal : frottement d'air large et doux, sans syllabe.
    air = band_noise(n, 180, 2100, rng)
    envelope = np.sin(math.pi * t / length) ** 1.6
    return air * envelope * raised_envelope(n, .045, .09)


def vanity_glint() -> np.ndarray:
    """Éclat de satisfaction, court et léger : deux tintements sans mélodie."""
    length = .20
    n = round(length * SR)
    result = np.zeros(n)
    for start, freq, gain in [(0.0, 1480, 1.0), (.048, 2210, .65)]:
        j = round(start * SR)
        u = np.arange(n-j) / SR
        bell = np.sin(math.tau * freq * u)
        bell += .20 * np.sin(math.tau * freq * 2.73 * u)
        bell *= np.exp(-u / .033) * raised_envelope(len(u), .0025, .025)
        result[j:] += gain * bell
    return result * raised_envelope(n, .0025, .025)


def elastic_release() -> np.ndarray:
    """Détente corporelle descendante : souple, non vocale, sans gros impact."""
    length = .47
    n = round(length * SR)
    t = np.arange(n) / SR
    # La chute initiale de hauteur suit l'abandon de la pose ; la petite
    # oscillation finale accompagne le tassement du même corps articulé.
    freq = 66 + 245 * np.exp(-t / .115)
    freq += 12 * np.sin(math.tau * 7 * t) * np.exp(-t / .24)
    tone = oscillator(freq) + .22 * oscillator(freq * 2)
    return tone * np.exp(-2.5 * t / length) * raised_envelope(n, .012, .09)


def shutter(rng: np.random.Generator) -> np.ndarray:
    n = round(.155 * SR)
    t = np.arange(n) / SR
    result = np.zeros(n)
    # Double contact très court : un clic principal, puis la fermeture feutrée.
    for offset, gain in [(0.0, 1.0), (.037, .52)]:
        j = round(offset * SR)
        m = n - j
        u = np.arange(m) / SR
        noise = band_noise(m, 650, 7000, rng)
        snap = .68 * noise * np.exp(-u / .0055)
        snap += .32 * oscillator(1700 * np.exp(-u / .009) + 270) * np.exp(-u / .011)
        snap *= raised_envelope(m, .00035, .008)
        result[j:] += snap * gain
    # Pas de réverbération longue : la lecture de la photo reste au calme.
    return result * raised_envelope(n, .00035, .015)


def embarrassment() -> np.ndarray:
    length = .45
    n = round(length * SR)
    t = np.arange(n) / SR
    # Petite ponctuation descendante, feutrée ; aucune imitation de parole.
    freq = 230 - 110 * (t / length) + 7 * np.sin(math.tau * 6 * t)
    tone = oscillator(freq) + .08 * oscillator(freq * 2.01)
    return tone * np.exp(-3.0 * t / length) * raised_envelope(n, .018, .10)


def fabric(rng: np.random.Generator) -> np.ndarray:
    n = round(.12 * SR)
    t = np.arange(n) / SR
    return band_noise(n, 260, 1600, rng) * np.sin(math.pi * t / .12) ** 2


def stereo(mono: np.ndarray, pan: float, peak_dbfs: float) -> np.ndarray:
    # Centrage continu, panoramique modéré : portable en écoute mono.
    weights = np.sqrt([(1 - pan) / 2, (1 + pan) / 2])
    signal = mono[:, None] * weights[None, :]
    signal -= signal.mean(axis=0, keepdims=True)
    # Conserver un raccord nul aux limites après suppression du faible DC.
    signal *= raised_envelope(len(mono), .0002, .001)[:, None]
    signal *= 10 ** (peak_dbfs / 20) / max(np.max(np.abs(signal)), 1e-12)
    return signal


def write_wave(path: Path, data: np.ndarray) -> None:
    assert data.ndim == 2 and data.shape[1] == 2
    assert np.isfinite(data).all() and np.max(np.abs(data)) < 1
    pcm = np.round(data * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())


def db(value: float) -> float | None:
    return round(20 * math.log10(value), 3) if value > 0 else None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    timeline = json.loads((ROOT / 'chronologie.json').read_text(encoding='utf-8'))
    assert timeline['duree_secondes'] == DURATION
    assert timeline['flash_time'] == 6.5
    rng = np.random.default_rng(SEED)
    # name, start, mono data, pan, peak dBFS, fabrication parameters
    events = [
        ('pose_froissement', .72, fabric(rng), .25, -29,
         {'type': 'bruit_filtre', 'band_hz': [260, 1600], 'duration': .12}),
        ('vanite_eclat', 1.30, vanity_glint(), .25, -19,
         {'type': 'double_tintement_bref', 'fundamentals_hz': [1480, 2210],
          'second_tintement_seconds': .048, 'duration': .20}),
        ('timer_3', 2.0, timer(620, .13), -.35, -15,
         {'type': 'sinus_harmonique', 'fundamental_hz': 620, 'duration': .13}),
        ('timer_2', 3.1, timer(740, .115), -.35, -14.5,
         {'type': 'sinus_harmonique', 'fundamental_hz': 740, 'duration': .115}),
        ('timer_1', 4.2, timer(880, .15), -.35, -14,
         {'type': 'sinus_harmonique', 'fundamental_hz': 880, 'duration': .15}),
        ('souffle', 5.30, breath(rng), .25, -21,
         {'type': 'souffle_non_vocal', 'band_hz': [180, 2100], 'duration': .50}),
        ('detente_elastique', 5.30, elastic_release(), .25, -16.5,
         {'type': 'glissando_elastique_descendant_non_vocal',
          'frequency_hz': [311, 70], 'duration': .47,
          'intention': 'abandon exagéré de la belle pose ; accompagne le souffle'}),
        ('obturateur', 6.5, shutter(rng), -.35, -6,
         {'type': 'double_clic', 'second_contact_seconds': .037, 'duration': .155}),
        ('gene', 10.1, embarrassment(), .20, -19,
         {'type': 'accent_elastique_descendant', 'frequency_hz': [230, 120], 'duration': .45}),
    ]
    mix = np.zeros((round(DURATION * SR), 2), dtype=np.float64)
    manifest = {
        'episode': 'MOU 01 — Le retardateur',
        'revision': 2,
        'revision_note': 'Ajout d’un éclat de vanité à 1,30 s et d’une détente élastique à 5,30 s ; bips, clic, souffle et ponctuation finale conservés.',
        'provenance': 'Tous les effets sont des créations procédurales originales synthétisées localement par sources/son.py. Aucun échantillon, enregistrement, service ni banque externe.',
        'outils': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard Python)'],
        'voice': False, 'continuous_music': False,
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16,
        'duration_seconds': DURATION, 'random_seed': SEED,
        'synchronisation': 'Instants exacts de chronologie.json ; conversion en indices entiers 48 kHz. Le flash est image 156 à 24 i/s, échantillon 312000.',
        'events': [],
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
            'start_sample': j, 'end_seconds': stop / SR,
            'pan': pan, 'peak_dbfs': db(float(np.max(np.abs(signal)))),
            'parameters': parameters,
        })
    peak = float(np.max(np.abs(mix)))
    rms = np.sqrt(np.mean(mix ** 2, axis=0))
    assert 10 ** (-7 / 20) <= peak <= 10 ** (-4 / 20)
    assert not mix[round(6.0 * SR):round(6.5 * SR)].any()
    assert np.isfinite(mix).all()
    write_wave(OUT / 'mix.wav', mix)
    # Audit relu sur le WAV réellement livré, incluant la quantification PCM.
    with wave.open(str(OUT / 'mix.wav'), 'rb') as f:
        assert (f.getnchannels(), f.getsampwidth(), f.getframerate(), f.getnframes()) == (2, 2, SR, round(SR * DURATION))
        pcm = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').reshape(-1, 2)
    decoded = pcm.astype(np.float64) / 32768
    audit = {
        'revision': 2,
        'frames': len(decoded), 'duration_seconds': len(decoded) / SR,
        'peak_dbfs': db(float(np.max(np.abs(decoded)))),
        'rms_dbfs_left_right': [db(float(v)) for v in np.sqrt(np.mean(decoded ** 2, axis=0))],
        'dc_mean_left_right': decoded.mean(axis=0).tolist(),
        'clipped_samples': int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767)),
        'silence_before_flash_6_0_to_6_5': not bool(pcm[round(6.0 * SR):round(6.5 * SR)].any()),
        'flash_sample': round(6.5 * SR),
        'vanity_glint_sample': round(1.30 * SR),
        'elastic_release_sample': round(5.30 * SR),
        'event_count': len(events),
        'reproduction': 'Depuis la racine MOU : .venv/bin/python episodes/01/sources/son.py',
        'limite': 'Contrôle numérique et intention de mixage ; aucun test d’écoute sur appareil mobile réel.',
    }
    assert audit['clipped_samples'] == 0
    (OUT / 'provenance_et_parametres.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (OUT / 'audit_son.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
