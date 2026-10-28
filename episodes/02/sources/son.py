"""Le torchon — six sons de tissu originaux, générés localement.

Python/NumPy/wave uniquement pour la synthèse ; FFmpeg peut contrôler l'AAC.
Aucun échantillon, voix, musique, TTS ou service de production externe.
Les événements et silences viennent de ../chronologie.json.
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

EP = Path(__file__).resolve().parents[1]
OUT = EP / 'sons'
SR = 48000
SEEDS = {'prise_tissu': 7201, 'traction_1': 7202, 'traction_2': 7203,
         'envol_tissu': 7204, 'flap': 7205, 'revelation': 7206}


def envelope(n, attack=.004, release=.012):
    a, r = min(n, max(2, round(attack*SR))), min(n, max(2, round(release*SR)))
    env = np.ones(n, dtype=np.float64)
    env[:a] *= np.sin(np.linspace(0, math.pi/2, a))**2
    env[-r:] *= np.cos(np.linspace(0, math.pi/2, r))**2
    return env


def band_noise(n, low, high, seed):
    data = np.random.default_rng(seed).standard_normal(n)
    f = np.fft.rfftfreq(n, 1/SR)
    mask = (1-np.exp(-(f/low)**4))*np.exp(-(f/high)**4)
    signal = np.fft.irfft(np.fft.rfft(data)*mask, n)
    return signal/max(float(np.sqrt(np.mean(signal**2))), 1e-12)


def grains(n, seed, count, gain=1.):
    """Petits plis irréguliers de tissu ; aucune résonance tonale."""
    rng = np.random.default_rng(seed)
    signal = np.zeros(n)
    for _ in range(count):
        length = min(n, int(rng.uniform(.005, .018)*SR))
        start = int(rng.integers(0, max(1, n-length)))
        air = band_noise(length, 600., 5100., int(rng.integers(0, 2**31)))
        env = envelope(length, .0008, min(.008, length/SR*.5))
        env *= np.exp(-np.arange(length)/(SR*.005))
        signal[start:start+length] += air*env*rng.uniform(.3, 1.)*gain
    return signal


def make_sound(kind, length, seed):
    n = round(length*SR)
    t = np.arange(n)/SR
    u = t/length
    if kind == 'cloth_grip':
        base = band_noise(n, 270., 3100., seed)
        signal = .55*base*np.sin(math.pi*u)**1.5 + .40*grains(n, seed+100, 5)
        params = {'band_hz': [270, 3100], 'fold_grains': 5,
                  'intention': 'prise courte et mate d’une lisière de tissu'}
    elif kind == 'cloth_pull':
        base = band_noise(n, 180., 3300., seed)
        # Two irregular friction stresses, not a musical or elastic sweep.
        pressure = (.18 + .80*np.exp(-((u-.25)/.19)**2)
                    + .55*np.exp(-((u-.65)/.14)**2))
        signal = base*pressure + .38*grains(n, seed+100, max(6, round(length*22)))
        params = {'band_hz': [180, 3300], 'pressure_lobes_fraction': [.25, .65],
                  'fold_grains': max(6, round(length*22)),
                  'intention': 'frottement de coton tendu, irrégulier et sans ressort'}
    elif kind == 'cloth_swish':
        air = band_noise(n, 140., 4300., seed)
        pressure = np.sin(math.pi*u/2)**1.6
        signal = air*pressure*envelope(n, .012, .012)
        params = {'band_hz': [140, 4300], 'crescendo': True,
                  'intention': 'air déplacé par le tissu depuis la libération jusqu’au contact'}
    elif kind == 'cloth_flap':
        # Soft low/mid broadband impact; main transient starts at the event
        # boundary. The secondary fold remains inside the120ms clip.
        low = band_noise(n, 65., 1400., seed)
        crisp = band_noise(n, 700., 4200., seed+17)
        main = (.88*low+.12*crisp)*np.exp(-t/.019)
        j = round(.023*SR)
        secondary = np.zeros(n)
        secondary[j:] = band_noise(n-j, 180., 2600., seed+28)*np.exp(-np.arange(n-j)/(SR*.025))
        signal = main+.25*secondary
        params = {'main_band_hz': [65, 1400], 'crinkle_band_hz': [700, 4200],
                  'main_decay_seconds': .019, 'secondary_fold_offset_seconds': .023,
                  'attack_seconds': .0003,
                  'intention': 'un FLAP mat de tissu sur le visage, pas un coup dur'}
    elif kind == 'cloth_reveal':
        base = band_noise(n, 200., 2600., seed)
        pressure = np.sin(math.pi*u)**1.2
        pressure *= .55+.25*np.sin(math.tau*2.3*u+.6)**2
        signal = .65*base*pressure + .16*grains(n, seed+100, 10)
        params = {'band_hz': [200, 2600], 'fold_grains': 10,
                  'intention': 'deux mains abaissent doucement le tissu ; pas d’accent émotionnel'}
    else:
        raise ValueError(kind)
    attack = .0003 if kind == 'cloth_flap' else .004
    signal -= signal.mean()
    signal *= envelope(n, attack, min(.025, length*.18))
    return signal, params


def to_stereo(signal, peak_dbfs):
    # A centred close prop, deliberately dual mono : no delayed spatial
    # effect that could blur the contact or leak into a silent hold.
    out = np.repeat(signal[:, None], 2, axis=1)
    out *= 10**(peak_dbfs/20)/max(float(np.abs(out).max()), 1e-12)
    return out


def write_wave(path, data):
    assert data.ndim == 2 and data.shape[1] == 2
    assert np.isfinite(data).all() and np.abs(data).max() < .99
    pcm = np.round(data*32767).astype('<i2')
    fd, name = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    os.close(fd)
    try:
        with wave.open(name, 'wb') as f:
            f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes(pcm.tobytes())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def write_json(path, data):
    fd, name = tempfile.mkstemp(prefix=path.name+'.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def read_wave(path):
    with wave.open(str(path), 'rb') as f:
        assert (f.getframerate(), f.getnchannels(), f.getsampwidth()) == (SR, 2, 2)
        return np.frombuffer(f.readframes(f.getnframes()), '<i2').reshape(-1, 2)


def db(value):
    return round(20*math.log10(value), 3) if value else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    path = EP/'chronologie.json'
    timeline = json.loads(path.read_text())
    duration, fps = float(timeline['duree_secondes']), int(timeline['fps'])
    assert SR % fps == 0
    mix = np.zeros((round(SR*duration), 2), dtype=np.float64)
    events = []
    for item in timeline['audio_events']:
        name, start, length = item['name'], float(item['start']), float(item['duration'])
        mono, params = make_sound(item['kind'], length, SEEDS[name])
        signal = to_stereo(mono, float(item['peak_dbfs']))
        j = round(start*SR); end = j+len(signal)
        assert end <= len(mix)
        mix[j:end] += signal
        write_wave(OUT/(name+'.wav'), signal)
        events.append({**item, 'file': name+'.wav', 'seed': SEEDS[name],
                       'start_sample': j, 'samples': len(signal), 'end_seconds': end/SR,
                       'peak_dbfs_measured': db(float(np.abs(signal).max())), 'parameters': params})
    assert len(events) == 6
    assert np.abs(mix).max() < .99
    write_wave(OUT/'mix.wav', mix)
    pcm = read_wave(OUT/'mix.wav')
    decoded = pcm.astype(float)/32768.
    silences = []
    for entry in timeline['silences']:
        section = pcm[round(entry['start']*SR):round(entry['end']*SR)]
        assert not section.any()
        silences.append({**entry, 'exact_pcm_silence': True})
    flap_sample = round(timeline['flap_time']*SR)
    section = np.abs(decoded[flap_sample:flap_sample+round(.03*SR)]).max(axis=1)
    assert section.max() > .1
    onset = (flap_sample+int(np.argmax(section>.005)))/SR
    assert abs(onset-timeline['flap_time']) < .003
    audit = {'episode': '02', 'revision': timeline['revision'],
             'duration_seconds': len(pcm)/SR, 'sample_rate': SR,
             'channels': 2, 'bit_depth': 16, 'event_count': len(events),
             'peak_dbfs': db(float(np.abs(decoded).max())),
             'rms_dbfs_left_right': [db(float(v)) for v in np.sqrt(np.mean(decoded**2, axis=0))],
             'dc_mean_left_right': decoded.mean(axis=0).tolist(),
             'clipped_samples': int(np.count_nonzero(np.abs(pcm.astype(np.int32))>=32767)),
             'flap_scheduled_seconds': timeline['flap_time'],
             'flap_onset_seconds': round(onset, 6),
             'silences': silences, 'no_music': True, 'no_voice': True,
             'mix_sha256': hashlib.sha256((OUT/'mix.wav').read_bytes()).hexdigest(),
             'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'limits': 'Contrôles numériques PCM, pas d’écoute humaine, mobile ni test public.'}
    assert audit['clipped_samples'] == 0
    manifest = {'episode': 'MOU — Le torchon', 'revision': timeline['revision'],
                'provenance': 'Six effets procéduraux originaux synthétisés localement par Python/NumPy. Noyaux de bruit filtré et enveloppes repris du savoir-faire local MOU ; aucune ressource sonore externe.',
                'outils': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard)'],
                'sample_rate': SR, 'channels': 2, 'bit_depth': 16,
                'duration_seconds': duration, 'chronologie_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'random_seeds': SEEDS, 'voice': False, 'continuous_music': False,
                'events': events, 'silences': silences,
                'reproduction': '.venv/bin/python episodes/02/sources/son.py',
                'limits': audit['limits']}
    write_json(OUT/'audit_son.json', audit)
    write_json(OUT/'provenance_et_parametres.json', manifest)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
