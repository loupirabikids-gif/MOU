"""Encore une feuille — bruitages originaux, reproductibles et sans ressources externes.

Synthèse locale Python/NumPy/wave : eau, papier, petits contacts et cuisson.
La chronologie commune fixe les quatre lavages, déchirures et jets. Les sons
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
TIMELINE = EP / 'chronologie.json'
OUT = EP / 'audio'
AUDIT = EP / 'controle' / 'audit_son.json'
SR = 48000
SEED = 3032904


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


def make_sound(kind, length, seed, softness=0.):
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
        body_high = 1500./(1.+.20*softness)
        fold_high = 4200./(1.+.14*softness)
        body = band_noise(n, 75., body_high, seed)*np.exp(-t/.031)
        folds = band_noise(n, 650., fold_high, seed+11)*np.exp(-t/.018)
        signal = body+(.20-.025*softness)*folds
        j = round(.033*SR)
        if j < n:
            signal[j:] += .22*band_noise(n-j, 200., 2200., seed+22)*np.exp(-np.arange(n-j)/(SR*.025))
        attack, release = .0003, .015
        params = {'body_band_hz': [75, body_high], 'fold_band_hz': [650, fold_high],
                  'paper_cushioning_step': softness,
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
    elif kind == 'carrot_chop':
        # A brief crisp vegetable edge over the low wooden-board contact.
        # Damped/noisy components avoid a synthetic beep or metallic alarm.
        board = band_noise(n, 90., 1900., seed)*np.exp(-t/.019)
        crunch = band_noise(n, 850., 4900., seed+11)*np.exp(-t/.010)
        wood = (.16*np.sin(math.tau*370.*t)*np.exp(-t/.014)
                + .07*np.sin(math.tau*610.*t)*np.exp(-t/.009))
        signal = .78*board+.27*crunch+wood
        attack, release = .00025, .012
        params = {'board_band_hz': [90, 1900], 'vegetable_band_hz': [850, 4900],
                  'wood_resonances_hz': [370, 610],
                  'intention': 'tac bref du couteau traversant la carotte sur la planche'}
    elif kind == 'knife_setdown':
        board = band_noise(n, 110., 2100., seed)*np.exp(-t/.017)
        blade = (.10*np.sin(math.tau*1370.*t)*np.exp(-t/.011)
                 +.045*np.sin(math.tau*2230.*t)*np.exp(-t/.007))
        signal = board+blade
        attack, release = .0004, .012
        params = {'body_band_hz': [110, 2100], 'blade_resonances_hz': [1370, 2230],
                  'intention': 'petit contact du couteau posé, sans longue sonnerie'}
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
    cooking = timeline['cooking_events']
    carrot = timeline['carrot']
    add('cuisson', 'frying', 0., timeline['duration'], -31., -.2)
    add('remuage_debut', 'stir', 0., 2.2, -23., -.35)
    add('cuillere_posee', 'wood_contact', cooking['spoon_down'], .10, -23., -.2)
    add('contact_tomate', 'tomato_contact', cooking['tomato_contact'], .11, -23., .18)
    for i, contact in enumerate(carrot['cut_times'], 1):
        add(f'carotte_coupe_{i}', 'carrot_chop', contact, .095, -15.-.5*(i-1), .23)
    add('couteau_pose', 'knife_setdown', carrot['knife_set_down'], .105, -23., .23)
    add('contact_manche_propre', 'wood_contact', cooking['clean_handle'], .10, -20., -.2)
    for cycle in timeline['cycles']:
        i = cycle['id']
        start, end = cycle['water']
        add(f'c{i}_robinet_ouvre', 'tap', start, .075, -21., -.6, i)
        add(f'c{i}_eau', 'water', start, end-start, -15.5, -.55, i)
        add(f'c{i}_robinet_ferme', 'tap', end, .075, -21.5, -.6, i)
        start, end = cycle['wash']
        add(f'c{i}_main_sous_eau', 'hand_water', start, end-start, -21., -.55, i)
        start, end = cycle['pull']
        add(f'c{i}_papier_deroule', 'paper_pull', start, end-start, -20.+.3*(i-1), .4, i)
        add(f'c{i}_papier_dechire', 'paper_tear', cycle['tear'], .145, -13., .35, i)
        start, end = cycle['wipe']
        add(f'c{i}_essuie_main', 'paper_wipe', start, end-start, -20., .05, i)
        start, end = cycle['crumple']
        add(f'c{i}_papier_froisse', 'paper_crumple', start, end-start, -17., -.05, i)
        start, end = cycle['release'], cycle['land']
        add(f'c{i}_papier_lache', 'paper_flight', start, min(.36, end-start-.035), -26., -.35, i)
        add(f'c{i}_poubelle_impact', 'paper_land', end, .20, -15.5-1.25*(i-1), -.45, i)
    return events


def main():
    timeline_bytes = TIMELINE.read_bytes()
    timeline = json.loads(timeline_bytes)
    assert timeline['version'] == 4 and len(timeline['cycles']) == 4
    duration = float(timeline['duration'])
    assert duration == 29. and timeline['fps'] == 24
    OUT.mkdir(parents=True, exist_ok=True)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    n = round(duration*SR)
    mix = np.zeros((n, 2))
    events = events_for(timeline)
    metadata = []
    absolute_time = np.arange(n)/SR
    for index, event in enumerate(events):
        seed = SEED+index*137
        softness = float(event['cycle']-1) if event['kind'] == 'paper_land' else 0.
        mono, parameters = make_sound(event['kind'], event['duration'], seed, softness)
        signal = stereo(mono, event['peak_dbfs'], event['pan'])
        if event['kind'] == 'frying':
            # Room perspective drops at sink/bin close-ups. The final hold
            # retains only this subdued cooking layer: no explanatory cue.
            gain = np.ones(n)
            for cycle in timeline['cycles']:
                for interval, factor in [(cycle['sink'], .23), (cycle['zoom'], .3)]:
                    a, b = interval
                    inside = smooth((absolute_time-a)/.07)*(1.-smooth((absolute_time-b)/.07))
                    gain *= 1.-(1.-factor)*inside
            final_start, final_end = timeline['final_hold']
            final_quiet = smooth((absolute_time-final_start)/.08)
            gain *= 1.-.45*final_quiet
            signal *= gain[:, None]
            parameters['perspective_gain_sink'] = .23
            parameters['perspective_gain_bin'] = .3
            parameters['final_hold_cooking_only_seconds'] = [final_start, final_end]
            parameters['final_hold_gain'] = .55
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
    hold_start, hold_end = timeline['final_hold']
    pause = decoded[round(hold_start*SR):round(hold_end*SR)]
    assert all(e['kind'] == 'frying' or e['start']+e['duration'] <= hold_start for e in metadata)
    cuts = [e for e in metadata if e['kind'] == 'carrot_chop']
    assert [e['start'] for e in cuts] == timeline['carrot']['cut_times']
    assert all(abs(e['first_above_one_percent_seconds']-e['start']) < .003 for e in cuts)
    audit = {'episode': '03', 'title': timeline['titre'], 'timeline_version': 4,
        'duration_seconds': len(pcm)/SR, 'samples_per_channel': n, 'sample_rate': SR,
        'channels': 2, 'bit_depth': 16, 'event_count': len(events),
        'peak_dbfs': db(float(np.abs(decoded).max())),
        'premaster_peak_dbfs': db(premaster_peak), 'master_gain_db': db(master_gain),
        'rms_dbfs_left_right': [db(float(x)) for x in np.sqrt(np.mean(decoded**2, axis=0))],
        'dc_mean_left_right': decoded.mean(axis=0).tolist(), 'clipped_samples': clipped,
        'water_intervals': water_checks, 'landing_onsets': landing_checks,
        'tear_onsets': tear_checks,
        'carrot_cut_onsets': [{'scheduled_seconds': e['start'],
                              'onset_seconds': e['first_above_one_percent_seconds']} for e in cuts],
        'final_hold_seconds': [hold_start, hold_end],
        'final_hold_rms_dbfs': db(float(np.sqrt(np.mean(pause**2)))),
        'final_hold_cooking_only': True,
        'first_and_last_pcm_frame_silent': True, 'no_music': True, 'no_voice': True,
        'no_external_samples': True, 'mix_sha256': sha(OUT/'mix.wav'),
        'source_sha256': sha(__file__), 'chronologie_sha256': hashlib.sha256(timeline_bytes).hexdigest(),
        'limits': 'Contrôles numériques PCM et concordance avec les événements prévus. Pas d’écoute humaine, de contrôle haut-parleur mobile ni de validation des contacts dans la vidéo par ce rapport.'}
    provenance = {'title': timeline['titre'], 'timeline_version': 4,
        'provenance': 'Tous les effets sont originaux, synthétisés localement par bruit filtré, micro-grains, enveloppes et faibles résonances. Aucun son téléchargé, musique, voix ou service externe.',
        'tools': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard)'],
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16, 'duration_seconds': duration,
        'master_gain_db': audit['master_gain_db'],
        'event_bank_levels': 'WAV individuels avant gain commun. Sommation aux start_sample, gain master_gain_db puis enveloppe globale attaque 8ms/sortie35ms reproduisent le mix.',
        'chronologie_sha256': audit['chronologie_sha256'], 'source_sha256': audit['source_sha256'],
        'events': metadata, 'no_music': True, 'no_voice': True,
        'reproduction': '.venv/bin/python -B episodes/03/carotte_v4/sources/son.py',
        'limits': audit['limits']}
    assert TIMELINE.read_bytes() == timeline_bytes, 'chronologie changed while synthesizing'
    atomic_json(OUT/'provenance.json', provenance)
    atomic_json(AUDIT, audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
