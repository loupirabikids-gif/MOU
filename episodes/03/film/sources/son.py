"""Encore une feuille — bruitages originaux, reproductibles et sans ressources externes.

Synthèse locale Python/NumPy/wave : eau, papier, petits contacts et cuisson.
La chronologie commune fixe les trois lavages, déchirures et jets. Les sons
individuels et leurs paramètres restent consultables dans ../audio/.
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
TIMELINE = EP.parent / 'chronologie.json'
OUT = EP / 'audio'
AUDIT = EP / 'controle' / 'audit_son.json'
SR = 48000
SEED = 3032600


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def smooth(value):
    value = np.clip(value, 0., 1.)
    return value*value*(3.-2.*value)


def envelope(n, attack=.006, release=.015):
    a = min(n, max(2, round(attack*SR)))
    r = min(n, max(2, round(release*SR)))
    env = np.ones(n, dtype=np.float64)
    env[:a] *= np.sin(np.linspace(0., math.pi/2., a))**2
    env[-r:] *= np.cos(np.linspace(0., math.pi/2., r))**2
    return env


def band_noise(n, low, high, seed):
    """Bruit à bords spectraux doux ; pas de boucle ou d'échantillon importé."""
    data = np.random.default_rng(seed).standard_normal(n)
    frequencies = np.fft.rfftfreq(n, 1./SR)
    mask = (1.-np.exp(-(frequencies/low)**4))*np.exp(-(frequencies/high)**4)
    signal = np.fft.irfft(np.fft.rfft(data)*mask, n)
    return signal/max(float(np.sqrt(np.mean(signal**2))), 1.e-12)


def grains(n, seed, density, low=450., high=4200., decay=.007):
    """Plis ou micro-impacts irréguliers, indépendants du bruit de fond."""
    rng = np.random.default_rng(seed)
    result = np.zeros(n)
    count = max(1, round(n/SR*density))
    for _ in range(count):
        length = min(n, max(8, round(rng.uniform(.007, .025)*SR)))
        start = int(rng.integers(0, max(1, n-length+1)))
        air = band_noise(length, low, high, int(rng.integers(0, 2**31)))
        e = np.exp(-np.arange(length)/(SR*decay))
        e *= envelope(length, .0005, min(.006, length/SR*.3))
        result[start:start+length] += air*e*rng.uniform(.35, 1.)
    return result


def make_sound(kind, length, seed):
    n = max(2, round(length*SR))
    t = np.arange(n)/SR
    u = t/length
    rng = np.random.default_rng(seed)
    attack, release = .005, min(.018, length*.18)
    if kind == 'frying':
        signal = .45*band_noise(n, 500., 4700., seed)
        signal *= .6+.13*np.sin(math.tau*.83*t+.2)+.12*np.sin(math.tau*1.91*t)
        signal += .5*grains(n, seed+100, 13., 900., 5900., .004)
        params = {'band_hz': [500, 4700], 'pops_per_second': 13,
                  'intention': 'cuisson douce, aucun gros crépitement de friture'}
    elif kind == 'stir':
        friction = band_noise(n, 160., 2100., seed)
        pressure = .18+.82*np.sin(math.pi*(u*2.3+.1))**4
        signal = friction*pressure + .12*grains(n, seed+100, 8., 250., 2400., .009)
        params = {'band_hz': [160, 2100], 'pressure_cycles': 2.3,
                  'intention': 'cuillère en bois qui glisse doucement dans la poêle'}
    elif kind == 'tap':
        body = band_noise(n, 180., 2800., seed)*np.exp(-t/.015)
        resonance = np.sin(math.tau*730.*t)*np.exp(-t/.012)
        signal = body+.16*resonance
        attack, release = .0004, .01
        params = {'noise_band_hz': [180, 2800], 'resonance_hz': 730,
                  'resonance_decay_seconds': .012,
                  'intention': 'petit clic mat de commande de robinet'}
    elif kind == 'water':
        # Low/mid turbulence gives body; the high layer is rolled off well
        # before sibilant white noise. Modulation is irregular and shallow.
        body = band_noise(n, 160., 1800., seed)
        hiss = band_noise(n, 1000., 5100., seed+11)
        modulation = .82+.10*np.sin(math.tau*3.1*t+.5)+.06*np.sin(math.tau*7.3*t)
        signal = (.72*body+.28*hiss)*modulation
        signal += .13*grains(n, seed+100, 20., 320., 3500., .009)
        attack, release = .018, .009
        params = {'body_band_hz': [160, 1800], 'air_band_hz': [1000, 5100],
                  'micro_splashes_per_second': 20,
                  'intention': 'petit filet d’eau, sans bruit blanc agressif'}
    elif kind == 'hand_water':
        pressure = .3+.7*np.sin(math.pi*u*3.)**2
        signal = band_noise(n, 200., 2800., seed)*pressure
        signal += .45*grains(n, seed+100, 23., 340., 3800., .01)
        params = {'band_hz': [200, 2800], 'splashes_per_second': 23,
                  'intention': 'main qui se tourne sous le filet, petits clapotis'}
    elif kind == 'paper_pull':
        pressure = .25+.75*np.sin(math.pi*u/2.)**.7
        signal = band_noise(n, 260., 4100., seed)*pressure
        signal += .25*grains(n, seed+100, 25., 700., 5400., .004)
        params = {'band_hz': [260, 4100], 'folds_per_second': 25,
                  'intention': 'longue bande de papier déroulée et tendue'}
    elif kind == 'paper_tear':
        pressure = .65+.35*np.sin(math.pi*u)
        signal = band_noise(n, 600., 6000., seed)*pressure*np.exp(-u*.8)
        signal += .8*grains(n, seed+100, 100., 1000., 6300., .003)
        attack, release = .0007, .018
        params = {'band_hz': [600, 6000], 'fibre_bursts_per_second': 100,
                  'intention': 'courte déchirure de fibres, pas claquement mécanique'}
    elif kind == 'paper_wipe':
        pressure = (.12+.86*np.exp(-((u-.25)/.15)**2)
                    + .71*np.exp(-((u-.7)/.17)**2))
        signal = band_noise(n, 230., 3700., seed)*pressure
        signal += .17*grains(n, seed+100, 18., 700., 4300., .007)
        params = {'band_hz': [230, 3700], 'pressure_peaks_fraction': [.25, .7],
                  'intention': 'deux frottements feutrés sur la main'}
    elif kind == 'paper_crumple':
        pressure = .25+.75*np.sin(math.pi*u)**.6
        signal = .2*band_noise(n, 220., 3500., seed)*pressure
        signal += grains(n, seed+100, 65., 450., 5500., .006)
        params = {'base_band_hz': [220, 3500], 'folds_per_second': 65,
                  'intention': 'papier comprimé en grosse boulette'}
    elif kind == 'paper_flight':
        pressure = np.sin(math.pi*u)**1.4
        signal = band_noise(n, 160., 2800., seed)*pressure
        params = {'band_hz': [160, 2800], 'intention': 'air déplacé discret après le lâcher'}
    elif kind == 'paper_land':
        # Mostly low/mid broad impact and two small folds. No bass boom or
        # ringing rim that would turn a soft ball into a hard object.
        body = band_noise(n, 75., 1500., seed)*np.exp(-t/.031)
        folds = band_noise(n, 650., 4200., seed+11)*np.exp(-t/.018)
        signal = body+.20*folds
        j = round(.033*SR)
        if j < n:
            signal[j:] += .22*band_noise(n-j, 200., 2200., seed+22)*np.exp(-np.arange(n-j)/(SR*.025))
        attack, release = .0003, .015
        params = {'body_band_hz': [75, 1500], 'fold_band_hz': [650, 4200],
                  'secondary_fold_offset_seconds': .033,
                  'intention': 'impact souple de papier dans une petite poubelle'}
    elif kind == 'tomato_contact':
        signal = band_noise(n, 100., 1700., seed)*np.exp(-t/.018)
        signal += .12*band_noise(n, 500., 2800., seed+11)*np.exp(-t/.009)
        attack, release = .0008, .015
        params = {'band_hz': [100, 1700], 'intention': 'petit contact mou de tomate'}
    elif kind == 'wood_contact':
        signal = band_noise(n, 140., 2200., seed)*np.exp(-t/.019)
        signal += .08*np.sin(math.tau*410.*t)*np.exp(-t/.014)
        attack, release = .0005, .015
        params = {'band_hz': [140, 2200], 'intention': 'contact de moufle sur manche en bois'}
    else:
        raise ValueError(kind)
    signal -= signal.mean()
    signal *= envelope(n, attack, release)
    return signal, params


def stereo(signal, peak_dbfs, pan):
    # Equal power with no interchannel delay; the contact time stays exact.
    angle = (pan+1.)*math.pi/4.
    output = signal[:, None]*np.array([math.cos(angle), math.sin(angle)])[None, :]
    output *= 10.**(peak_dbfs/20.)/max(float(np.abs(output).max()), 1.e-12)
    return output


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.'+path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_wave(path, data):
    assert data.ndim == 2 and data.shape[1] == 2 and np.isfinite(data).all()
    assert float(np.abs(data).max()) < .99
    pcm = np.round(data*32767.).astype('<i2')
    fd, name = tempfile.mkstemp(prefix='.'+path.name, suffix='.tmp', dir=path.parent)
    os.close(fd)
    try:
        with wave.open(name, 'wb') as stream:
            stream.setnchannels(2)
            stream.setsampwidth(2)
            stream.setframerate(SR)
            stream.writeframes(pcm.tobytes())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def db(value):
    return round(20.*math.log10(value), 3) if value else None


def events_for(timeline):
    events = []
    def add(name, kind, start, duration, peak, pan, cycle=None):
        events.append({'name': name, 'kind': kind, 'start': float(start),
                       'duration': round(float(duration), 9), 'peak_dbfs': peak,
                       'pan': pan, 'cycle': cycle})
    add('cuisson', 'frying', 0., timeline['duration'], -26., -.2)
    add('remuage_debut', 'stir', 0., 2.6, -23., -.35)
    add('remuage_reprise', 'stir', 25., 1., -24., -.35)
    add('contact_tomate', 'tomato_contact', 10.45, .11, -23., .18)
    add('contact_manche_propre', 'wood_contact', 17.6, .10, -20., -.2)
    for cycle in timeline['cycles']:
        i = cycle['id']
        start, end = cycle['water']
        add(f'c{i}_robinet_ouvre', 'tap', start, .075, -21., -.6, i)
        add(f'c{i}_eau', 'water', start, end-start, -15.5, -.55, i)
        add(f'c{i}_robinet_ferme', 'tap', end, .075, -21.5, -.6, i)
        start, end = cycle['wash']
        add(f'c{i}_main_sous_eau', 'hand_water', start, end-start, -21., -.55, i)
        start, end = cycle['pull']
        add(f'c{i}_papier_deroule', 'paper_pull', start, end-start, -20., .4, i)
        add(f'c{i}_papier_dechire', 'paper_tear', cycle['tear'], .145, -13., .35, i)
        start, end = cycle['wipe']
        add(f'c{i}_essuie_main', 'paper_wipe', start, end-start, -20., .05, i)
        start, end = cycle['crumple']
        add(f'c{i}_papier_froisse', 'paper_crumple', start, end-start, -17., -.05, i)
        start, end = cycle['release'], cycle['land']
        add(f'c{i}_papier_lache', 'paper_flight', start, min(.36, end-start-.035), -26., -.35, i)
        add(f'c{i}_poubelle_impact', 'paper_land', end, .20, -16.+.5*i, -.45, i)
    return events


def main():
    timeline_bytes = TIMELINE.read_bytes()
    timeline = json.loads(timeline_bytes)
    assert timeline['version'] == 2 and len(timeline['cycles']) == 3
    duration = float(timeline['duration'])
    assert duration == 26. and timeline['fps'] == 24
    OUT.mkdir(parents=True, exist_ok=True)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    n = round(duration*SR)
    mix = np.zeros((n, 2))
    events = events_for(timeline)
    metadata = []
    absolute_time = np.arange(n)/SR
    for index, event in enumerate(events):
        seed = SEED+index*137
        mono, parameters = make_sound(event['kind'], event['duration'], seed)
        signal = stereo(mono, event['peak_dbfs'], event['pan'])
        if event['kind'] == 'frying':
            # The room perspective drops at sink/bin close-ups. A real short
            # hold precedes the compulsive third ritual, without a music cue.
            gain = np.ones(n)
            for cycle in timeline['cycles']:
                for interval, factor in [(cycle['sink'], .23), (cycle['zoom'], .3)]:
                    a, b = interval
                    inside = smooth((absolute_time-a)/.07)*(1.-smooth((absolute_time-b)/.07))
                    gain *= 1.-(1.-factor)*inside
            pause = smooth((absolute_time-17.98)/.05)*(1.-smooth((absolute_time-18.50)/.05))
            gain *= 1.-.94*pause
            signal *= gain[:, None]
            parameters['perspective_gain_sink'] = .23
            parameters['perspective_gain_bin'] = .3
            parameters['hesitation_duck_seconds'] = [17.98, 18.55]
        start = round(event['start']*SR)
        end = start+len(signal)
        assert start >= 0 and end <= n, event
        mix[start:end] += signal
        path = OUT/(event['name']+'.wav')
        write_wave(path, signal)
        peak = float(np.abs(signal).max())
        threshold = max(2./32768., peak*.01)
        above = np.flatnonzero(np.max(np.abs(signal), axis=1) > threshold)
        metadata.append({**event, 'file': path.name, 'seed': seed,
            'start_sample': start, 'samples': len(signal), 'end_seconds': end/SR,
            'first_above_one_percent_seconds': (start+int(above[0]))/SR if len(above) else None,
            'peak_dbfs_measured': db(peak), 'parameters': parameters,
            'sha256': sha(path)})
    # One common, fixed gain brings sparse Foley to a useful playback level,
    # preserving its dynamics and leaving four decibels for the AAC encode.
    assert np.isfinite(mix).all() and float(np.abs(mix).max()) < .89
    premaster_peak = float(np.abs(mix).max())
    master_gain = 10.**(-4./20.)/premaster_peak
    mix *= master_gain
    mix *= envelope(n, .008, .035)[:, None]
    write_wave(OUT/'mix.wav', mix)
    with wave.open(str(OUT/'mix.wav'), 'rb') as stream:
        assert (stream.getnframes(), stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) == (n, SR, 2, 2)
        pcm = np.frombuffer(stream.readframes(n), '<i2').reshape(-1, 2)
    decoded = pcm.astype(np.float64)/32768.
    clipped = int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767))
    assert clipped == 0 and not pcm[0].any() and not pcm[-1].any()
    water_checks, landing_checks, tear_checks = [], [], []
    by_name = {e['name']: e for e in metadata}
    for cycle in timeline['cycles']:
        i = cycle['id']
        water = by_name[f'c{i}_eau']
        assert water['start'] == cycle['water'][0]
        assert abs(water['end_seconds']-cycle['water'][1]) < 1./SR
        water_checks.append({'cycle': i, 'scheduled': cycle['water'],
            'rendered': [water['start_sample']/SR, water['end_seconds']],
            'first_above_one_percent_seconds': water['first_above_one_percent_seconds']})
        land = by_name[f'c{i}_poubelle_impact']
        assert land['start'] == cycle['land']
        assert abs(land['first_above_one_percent_seconds']-cycle['land']) < .003
        landing_checks.append({'cycle': i, 'scheduled_seconds': cycle['land'],
            'onset_seconds': land['first_above_one_percent_seconds']})
        tear = by_name[f'c{i}_papier_dechire']
        assert tear['start'] == cycle['tear']
        tear_checks.append({'cycle': i, 'scheduled_seconds': cycle['tear'],
            'onset_seconds': tear['first_above_one_percent_seconds']})
    pause = decoded[round(18.05*SR):round(18.48*SR)]
    audit = {'episode': '03', 'title': timeline['titre'], 'timeline_version': 2,
        'duration_seconds': len(pcm)/SR, 'samples_per_channel': n, 'sample_rate': SR,
        'channels': 2, 'bit_depth': 16, 'event_count': len(events),
        'peak_dbfs': db(float(np.abs(decoded).max())),
        'premaster_peak_dbfs': db(premaster_peak), 'master_gain_db': db(master_gain),
        'rms_dbfs_left_right': [db(float(x)) for x in np.sqrt(np.mean(decoded**2, axis=0))],
        'dc_mean_left_right': decoded.mean(axis=0).tolist(), 'clipped_samples': clipped,
        'water_intervals': water_checks, 'landing_onsets': landing_checks,
        'tear_onsets': tear_checks,
        'hesitation_18_05_to_18_48_rms_dbfs': db(float(np.sqrt(np.mean(pause**2)))),
        'first_and_last_pcm_frame_silent': True, 'no_music': True, 'no_voice': True,
        'no_external_samples': True, 'mix_sha256': sha(OUT/'mix.wav'),
        'source_sha256': sha(__file__), 'chronologie_sha256': hashlib.sha256(timeline_bytes).hexdigest(),
        'limits': 'Contrôles numériques PCM et concordance avec les événements prévus. Pas d’écoute humaine, de contrôle haut-parleur mobile ni de validation des contacts dans la vidéo par ce rapport.'}
    provenance = {'title': 'MOU — Encore une feuille', 'timeline_version': 2,
        'provenance': 'Tous les effets sont originaux, synthétisés localement par bruit filtré, micro-grains, enveloppes et faibles résonances. Aucun son téléchargé, musique, voix ou service externe.',
        'tools': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard)'],
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16, 'duration_seconds': duration,
        'master_gain_db': audit['master_gain_db'],
        'event_bank_levels': 'Les WAV individuels sont avant le gain commun du mix ; leur sommation suivie de master_gain_db reproduit le mix.',
        'chronologie_sha256': audit['chronologie_sha256'], 'source_sha256': audit['source_sha256'],
        'events': metadata, 'no_music': True, 'no_voice': True,
        'reproduction': '.venv/bin/python episodes/03/film/sources/son.py',
        'limits': audit['limits']}
    assert TIMELINE.read_bytes() == timeline_bytes, 'chronologie changed while synthesizing'
    atomic_json(OUT/'provenance.json', provenance)
    atomic_json(AUDIT, audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
