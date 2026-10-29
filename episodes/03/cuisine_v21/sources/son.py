"""Encore une feuille — bruitages originaux et partition avec instruments libres.

Synthèse locale Python/NumPy/wave : eau sous pression, papier, cuisine et
sifflement initial ; partition originale rendue avec FluidSynth/TimGM6mb. La musique
reste continue, avec une baisse douce au lavabo pour laisser entendre l’eau.
La chronologie et ses notes communes règlent bouche, rythme et son.

V21 garde le mix V20 exact jusqu'à40,5s. Sa nouvelle fin prolonge la même
partition globale, avec la calibration précédente, et ajoute un seul
frottement de tissu. Le raccord précède l'ancienne sortie de la musique.
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
MUSIC_PEAK_DBFS = -23.5  # V15 nominal event reference; actual fixed gain is below.
MUSIC_COMMON_SCALE = 1.0  # Music calibrates once against a global RMS target.
MIX_GAIN_DB = {'water':-9., 'hand_water':-7., 'paper_pull':-2.,
               'paper_tear':-3., 'paper_wipe':-5., 'paper_crumple':-3.,
               'paper_land':-3.}
MASTER_GAIN_EXACT = 2.124210976406158
BASE_MIX_SHA256 = '8ddc8746a5ec7ae7d5914a29245eb1033982029c2e1b3b4fd1b7cb415ac5874a'
FLOOR_SEED = 3041672
# Retained sound identities stay independent of the new event order.  The
# fifth (tiny) ritual keeps the old fourth ritual's grain seeds and timbres.
LEGACY_PREFIX = ('cuisson', 'remuage_debut', 'cuillere_posee', 'contact_tomate',
                 'carotte_coupe_1', 'carotte_coupe_2', 'couteau_pose',
                 'contact_manche_propre')
RITUAL_SUFFIXES = ('robinet_ouvre', 'eau', 'robinet_ferme', 'main_sous_eau',
                  'papier_deroule', 'papier_dechire', 'essuie_main',
                  'papier_froisse', 'papier_lache', 'poubelle_impact')
LEGACY_NAMES = (LEGACY_PREFIX
                + tuple(f'c{i}_{suffix}' for i in range(1, 5) for suffix in RITUAL_SUFFIXES)
                + ('sifflement_p1_n1', 'sifflement_p1_n2', 'sifflement_p1_n3',
                   'musique_cuisine'))


def event_seed(event):
    """Stable V12 seeds, with separate identities for the added salt ritual."""
    name = event['name']
    if name == 'c5_papier_sol':
        return FLOOR_SEED
    if name.startswith('c5_'):
        name = 'c4_'+name.split('_', 1)[1]
    elif name.startswith('c4_') and not event['kind'].startswith('tiny_'):
        suffix = name.split('_', 1)[1]
        return SEED+(52+RITUAL_SUFFIXES.index(suffix))*137
    if name in LEGACY_NAMES:
        return SEED+LEGACY_NAMES.index(name)*137
    return SEED+{'sel_pince': 62, 'sel_saupoudre': 63}[name]*137


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
        # A fuller low/mid jet and denser basin splashes convey pressure.
        # The air layer is deliberately soft and rolled off before harsh hiss.
        body = band_noise(n, 85., 1550., seed)
        air = band_noise(n, 850., 4050., seed+11)
        basin = band_noise(n, 65., 460., seed+23)
        modulation = .89+.055*np.sin(math.tau*5.7*t+.5)+.04*np.sin(math.tau*9.3*t)
        signal = (.77*body+.18*air+.16*basin)*modulation
        signal += .24*grains(n, seed+100, 42., 180., 3400., .012)
        attack, release = .012, .009
        params = {'body_band_hz': [85, 1550], 'air_band_hz': [850, 4050],
                  'basin_band_hz': [65, 460], 'micro_splashes_per_second': 42,
                  'event_gain_change_db_vs_v5': 4.,
                  'intention': 'jet généreux sous pression et eau qui frappe le bassin, sans sifflement aigu'}
    elif kind == 'hand_water':
        pressure = .42+.58*np.sin(math.pi*u*3.)**2
        signal = band_noise(n, 150., 2500., seed)*pressure
        signal += .58*grains(n, seed+100, 36., 220., 3500., .012)
        params = {'band_hz': [150, 2500], 'splashes_per_second': 36,
                  'event_gain_change_db_vs_v5': 4.,
                  'intention': 'main sous le jet puissant, clapotis denses dans le bassin'}
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
    elif kind == 'tiny_paper_pull':
        # Only a small remaining flap moves, followed by quiet discovery.
        pressure = np.sin(math.pi*u)**1.1
        signal = band_noise(n, 420., 2700., seed)*pressure
        signal += .12*grains(n, seed+100, 16., 800., 3300., .003)
        attack, release = .006, .025
        params = {'band_hz': [420, 2700], 'folds_per_second': 16,
                  'intention': 'dernier petit bout, bref déroulage sans grande bande'}
    elif kind == 'tiny_paper_tear':
        signal = band_noise(n, 850., 4300., seed)*np.exp(-u*2.8)
        signal += .22*grains(n, seed+100, 42., 1100., 4500., .002)
        attack, release = .0007, .012
        params = {'band_hz': [850, 4300], 'fibre_bursts_per_second': 42,
                  'intention': 'petite rupture de fibres du dernier morceau'}
    elif kind == 'tiny_paper_wipe':
        pressure = (.82*np.exp(-((u-.27)/.10)**2)
                    +.71*np.exp(-((u-.73)/.11)**2))
        signal = band_noise(n, 340., 2600., seed)*pressure
        signal += .045*grains(n, seed+100, 9., 850., 3000., .003)*pressure
        attack, release = .012, .025
        params = {'band_hz': [340, 2600], 'pressure_peaks_fraction': [.27, .73],
                  'pressure_widths_fraction': [.10, .11], 'folds_per_second': 9,
                  'intention': 'deux frottements précautionneux avec un minuscule bout'}
    elif kind == 'tiny_paper_crumple':
        signal = .12*band_noise(n, 600., 3100., seed)*np.sin(math.pi*u)
        signal += grains(n, seed+100, 27., 800., 3800., .003)
        attack, release = .004, .025
        params = {'base_band_hz': [600, 3100], 'folds_per_second': 27,
                  'intention': 'quelques plis seulement, petite boulette'}
    elif kind == 'tiny_paper_flight':
        signal = band_noise(n, 500., 2500., seed)*np.sin(math.pi*u)**1.5
        params = {'band_hz': [500, 2500],
                  'intention': 'déplacement d’air presque imperceptible du petit bout'}
    elif kind == 'tiny_paper_land':
        # Small high-mid paper contact on the old pile: no large-ball thud.
        signal = band_noise(n, 380., 2100., seed)*np.exp(-t/.009)
        signal += .18*band_noise(n, 850., 3100., seed+11)*np.exp(-t/.005)
        attack, release = .0004, .012
        params = {'body_band_hz': [380, 2100], 'fold_band_hz': [850, 3100],
                  'intention': 'minuscule impact sur les papiers déjà accumulés'}
    elif kind == 'tiny_paper_floor':
        # A damped, broad paper contact without a hard click or tonal sting.
        signal = band_noise(n, 160., 1600., seed)*np.exp(-t/.014)
        signal += .14*band_noise(n, 700., 2700., seed+11)*np.exp(-t/.006)
        attack, release = .0005, .020
        params = {'body_band_hz': [160, 1600], 'fold_band_hz': [700, 2700],
                  'body_decay_seconds': .014, 'fold_decay_seconds': .006,
                  'intention': 'petit papier froissé qui retombe au sol, contact mat sans effet comique ajouté'}
    elif kind == 'salt_pinch':
        pressure = np.sin(math.pi*u)**1.2
        signal = .13*band_noise(n, 700., 3800., seed)*pressure
        signal += .30*grains(n, seed+100, 24., 1600., 5700., .0025)*pressure
        attack, release = .004, .016
        params = {'noise_band_hz': [700, 3800], 'grain_density_per_second': 24,
                  'intention': 'petite pincée sèche de sel prise dans le bol, sans clic ajouté'}
    elif kind == 'salt_sprinkle':
        pressure = np.sin(math.pi*u)**.8
        signal = .05*band_noise(n, 1000., 4700., seed)*pressure
        signal += .42*grains(n, seed+100, 29., 1800., 6200., .002)*pressure
        attack, release = .008, .024
        params = {'air_band_hz': [1000, 4700], 'grain_density_per_second': 29,
                  'grain_decay_seconds': .002,
                  'intention': 'grains de sel légers et secs versés dans la poêle, sans carillon explicatif'}
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


def make_whistle(length, frequency_hz, seed):
    """Breathy human-like whistle, with original pitch and no recorded voice.

    The tone has a dominant fundamental, a soft air layer, an initial scoop,
    continuous phase, small irregular pitch drift and delayed vibrato. Smooth
    breath-shaped attacks/releases avoid the hard edges of an electronic beep.
    """
    n = max(2, round(length*SR))
    t = np.arange(n)/SR
    rng = np.random.default_rng(seed)
    nodes = np.arange(0., length+.06, .03)
    jitter = np.interp(t, nodes, rng.normal(0., 2.2, len(nodes)))
    delayed = smooth((t-.075)/.09)
    vibrato = 5.2*np.sin(math.tau*5.05*t+.15)*delayed
    scoop = -48.*np.exp(-t/.032)
    tail = -13.*smooth((t-max(.03,length-.07))/.07)
    cents = scoop+jitter+vibrato+tail
    frequency = float(frequency_hz)*2.**(cents/1200.)
    phase = math.tau*np.cumsum(frequency)/SR
    fundamental = np.sin(phase)
    tone = fundamental+.026*np.sin(2.*phase+.2)+.006*np.sin(3.*phase)
    pressure_nodes = rng.uniform(.94,1.04,len(nodes))
    pressure = np.interp(t,nodes,pressure_nodes)
    air = band_noise(n, 800., 4300., seed+41)
    signal = (tone+.065*air)*pressure
    signal -= signal.mean()
    signal *= envelope(n,.020,min(.035,length*.25))
    params = {'fundamental_hz':float(frequency_hz),
              'initial_scoop_cents':-48., 'scoop_time_seconds':.032,
              'vibrato_hz':5.05, 'vibrato_depth_cents':5.2,
              'pitch_jitter_std_cents':2.2, 'jitter_node_spacing_seconds':.03,
              'air_band_hz':[800,4300], 'air_amplitude':.065,
              'attack_seconds':.020,'release_seconds':min(.035,length*.25),
              'source':'original local synthesis, no tune or sample imported',
              'intention':'petite phrase sifflée gaie et soufflée pendant la cuisine'}
    return signal,params


def make_background_music(length, specification, seed):
    """Original score, using the bundled GPL TimGM6mb instrument bank."""
    import importlib.util
    module_path=Path(__file__).with_name('music.py')
    spec=importlib.util.spec_from_file_location('mou_music_v17',module_path)
    music=importlib.util.module_from_spec(spec);spec.loader.exec_module(music)
    signal,parameters,tracks,unattenuated=music.render_background(length,specification,seed)
    # These editable stems retain their relative arrangement levels. Their
    # common scale is exactly the background-music event's pre-master scale.
    scale=MUSIC_COMMON_SCALE
    stems=[]
    for name,data in tracks.items():
        path=OUT/f'musique_{name}.wav'
        stereo_stem=np.column_stack((data,data))*scale
        write_wave(path,stereo_stem)
        stems.append({'file':path.name,'sha256':sha(path),
                      'track':name,'stage':'pre-master, same common scale as musique_cuisine.wav',
                      'peak_dbfs':db(float(np.abs(stereo_stem).max())),
                      'samples':len(data)})
    gain=music.gain_envelope(length,specification)
    reference=np.column_stack((unattenuated,unattenuated))*scale
    reference_path=OUT/'musique_sans_baisse.wav'
    write_wave(reference_path,reference)
    parameters['unattenuated_reference']={'file':reference_path.name,'sha256':sha(reference_path),'stage':'same calibrated music level, before sink-only attenuation'}
    parameters['effective_specification']=specification
    parameters['stems']=stems
    parameters['stem_common_linear_scale']=scale
    parameters['music_common_scale']=MUSIC_COMMON_SCALE
    parameters['single_global_music_calibration']=True
    parameters['music_source_sha256']=sha(module_path)
    return signal,parameters


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
    add('remuage_debut', 'stir', 0., cooking.get('stir_end', 2.2), -23., -.35)
    add('cuillere_posee', 'wood_contact', cooking['spoon_down'], .10, -23., -.2)
    add('contact_tomate', 'tomato_contact', cooking['tomato_contact'], .11, -23., .18)
    for i, contact in enumerate(carrot['cut_times'], 1):
        add(f'carotte_coupe_{i}', 'carrot_chop', contact, .095, -15.-.5*(i-1), .23)
    add('couteau_pose', 'knife_setdown', carrot['knife_set_down'], .105, -23., .23)
    add('contact_manche_propre', 'wood_contact', cooking['clean_handle'], .10, -20., -.2)
    salt = timeline['salt']
    start, end = salt['pinch']
    add('sel_pince', 'salt_pinch', start, end-start, -30., .1)
    start, end = salt['sprinkle']
    add('sel_saupoudre', 'salt_sprinkle', start, end-start, -29., -.25)
    for cycle in timeline['cycles']:
        i = cycle['id']
        tiny = bool(cycle.get('tiny', False))
        start, end = cycle['water']
        add(f'c{i}_robinet_ouvre', 'tap', start, .075, -21., -.6, i)
        add(f'c{i}_eau', 'water', start, end-start, -11.5, -.55, i)
        add(f'c{i}_robinet_ferme', 'tap', end, .075, -21.5, -.6, i)
        start, end = cycle['wash']
        add(f'c{i}_main_sous_eau', 'hand_water', start, end-start, -17., -.55, i)
        start, end = cycle['pull']
        add(f'c{i}_papier_deroule', 'tiny_paper_pull' if tiny else 'paper_pull',
            start, min(.18, end-start) if tiny else end-start,
            -28. if tiny else -20.+.3*(i-1), .4, i)
        add(f'c{i}_papier_dechire', 'tiny_paper_tear' if tiny else 'paper_tear',
            cycle['tear'], .055 if tiny else .145, -25. if tiny else -13., .35, i)
        start, end = cycle['wipe']
        add(f'c{i}_essuie_main', 'tiny_paper_wipe' if tiny else 'paper_wipe',
            start, end-start, -28. if tiny else -20., .05, i)
        start, end = cycle['crumple']
        add(f'c{i}_papier_froisse', 'tiny_paper_crumple' if tiny else 'paper_crumple',
            start, min(.15, end-start) if tiny else end-start, -30. if tiny else -17., -.05, i)
        start, end = cycle['release'], cycle['land']
        add(f'c{i}_papier_lache', 'tiny_paper_flight' if tiny else 'paper_flight',
            start, min(.13 if tiny else .36, end-start-.035), -38. if tiny else -26., -.35, i)
        add(f'c{i}_poubelle_impact', 'tiny_paper_land' if tiny else 'paper_land',
            end, .07 if tiny else .20, -31. if tiny else -15.5-1.25*(i-1), -.45, i)
    # Append after the existing Foley bank so its seeds and timbres stay fixed.
    for index,note in enumerate(timeline['whistle_notes'],1):
        add(f'sifflement_p{note["phrase"]}_n{index}', 'whistle',
            note['start'],note['end']-note['start'],-19.5,0.)
        events[-1].update({'frequency_hz':float(note['frequency_hz']),
                          'phrase':int(note['phrase']),
                          'end':float(note['end'])})
    # Append the music last so every retained Foley/whistle keeps its seed.
    add('musique_cuisine','background_music',0.,timeline['duration'],MUSIC_PEAK_DBFS,0.)
    return events


def legacy_full_synthesis():
    """Original pre-V20 synthesis retained as editable source documentation.

    The V20 entry point below deliberately uses the included frozen mix instead
    of recalculating cooking perspective gains for the changed final camera.
    """
    timeline_bytes = TIMELINE.read_bytes()
    timeline = json.loads(timeline_bytes)
    assert timeline['version'] == 6 and len(timeline['cycles']) == 5
    duration = float(timeline['duration'])
    assert duration > 0. and timeline['fps'] == 24
    OUT.mkdir(parents=True, exist_ok=True)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    n = round(duration*SR)
    mix = np.zeros((n, 2))
    events = events_for(timeline)
    metadata = []
    music_spec={**timeline['background_music'],'duration':duration,'windows':[[0.,duration]],
                'intention':'Une partition jazz sur une grille régulière, indépendante des plans, avec baisse légère sous l’eau.',
                'duck_intervals':[cycle['sink'] for cycle in timeline['cycles']],
                'duck_db':-1.5,'duck_attack_seconds':.5,'duck_release_seconds':.7,
                'target_music_rms_dbfs_after_master':-31.,'master_gain_linear':MASTER_GAIN_EXACT}
    absolute_time = np.arange(n)/SR
    for event in events:
        seed = event_seed(event)
        softness = float(event['cycle']-1) if event['kind'] == 'paper_land' else 0.
        if event['kind']=='whistle':
            mono,parameters=make_whistle(event['duration'],event['frequency_hz'],seed)
        elif event['kind']=='background_music':
            mono,parameters=make_background_music(event['duration'],music_spec,seed)
        else:
            mono, parameters = make_sound(event['kind'], event['duration'], seed, softness)
        signal = (np.column_stack((mono,mono))*MUSIC_COMMON_SCALE if event['kind']=='background_music'
                  else stereo(mono,event['peak_dbfs'],event['pan']))
        if event['kind'] == 'frying':
            # Preserve the original frying perspective and final reduction.
            # The newly continuous music is mixed separately.
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
            parameters['final_hold_frying_reduction_seconds'] = [final_start, final_end]
            parameters['final_hold_gain'] = .55
        start = round(event['start']*SR)
        end = start+len(signal)
        assert start >= 0 and end <= n, event
        mix_gain_db=float(MIX_GAIN_DB.get(event['kind'],0.))
        mix[start:end] += signal*10.**(mix_gain_db/20.)
        path = OUT/(event['name']+'.wav')
        write_wave(path, signal)
        peak = float(np.abs(signal).max())
        threshold = max(2./32768., peak*.01)
        above = np.flatnonzero(np.max(np.abs(signal), axis=1) > threshold)
        metadata.append({**event, 'file': path.name, 'seed': seed,
            'mix_gain_db':mix_gain_db,
            'start_sample': start, 'samples': len(signal), 'end_seconds': end/SR,
            'first_above_one_percent_seconds': (start+int(above[0]))/SR if len(above) else None,
            'peak_dbfs_measured': db(peak), 'parameters': parameters,
            'sha256': sha(path)})
    used_whistles={e['file'] for e in metadata if e['kind']=='whistle'}
    for obsolete in OUT.glob('sifflement_*.wav'):
        if obsolete.name not in used_whistles:
            obsolete.unlink()
    # One common, fixed gain brings sparse Foley to a useful playback level,
    # preserving its dynamics and leaving four decibels for the AAC encode.
    assert np.isfinite(mix).all() and float(np.abs(mix).max()) < .89
    premaster_peak = float(np.abs(mix).max())
    # Fixed V15 gain protects all 63 original Foley/whistle levels. Music
    # now exists throughout the episode, so there is no silent exterior
    # region from which to infer a new normalization gain.
    master_gain=MASTER_GAIN_EXACT
    reference_premaster_peak=10.**(-4./20.)/MASTER_GAIN_EXACT
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
    assert all(e['kind'] in ('frying','background_music')
               or e['start']+e['duration'] <= hold_start for e in metadata)
    cuts = [e for e in metadata if e['kind'] == 'carrot_chop']
    assert [e['start'] for e in cuts] == timeline['carrot']['cut_times']
    assert all(abs(e['first_above_one_percent_seconds']-e['start']) < .003 for e in cuts)
    salt_events = [e for e in metadata if e['kind'].startswith('salt_')]
    assert len(salt_events) == 2
    for event, field in zip(salt_events, ('pinch', 'sprinkle')):
        start, end = timeline['salt'][field]
        assert event['start'] == start and abs(event['end_seconds']-end) < 1./SR
        assert event['end_seconds'] <= timeline['cycles'][3]['sink'][0]
    tiny_cycles = [c['id'] for c in timeline['cycles'] if c.get('tiny')]
    assert tiny_cycles == [5]
    tiny_events = [e for e in metadata if e['kind'].startswith('tiny_')]
    assert len(tiny_events) == 6
    reveal = timeline['cycles'][-1]['reveal']
    assert all(e['kind'] in ('frying','background_music') or e['start']+e['duration'] <= reveal[0]+.06
               or e['start'] >= reveal[1] for e in metadata)
    whistles=[e for e in metadata if e['kind']=='whistle']
    assert len(whistles)==len(timeline['whistle_notes'])
    assert len(whistles)==3 and sorted({e['phrase'] for e in whistles})==[1]
    first_wash_start=timeline['cycles'][0]['sink'][0]
    for event in whistles:
        assert 0.<=event['start']<event['end_seconds']<=first_wash_start,event
        assert all(event['end_seconds']<=c['sink'][0] or event['start']>=c['sink'][1]
                   for c in timeline['cycles']),event
        assert abs(event['end_seconds']-event['end'])<=1./SR
    music=next(e for e in metadata if e['kind']=='background_music')
    with wave.open(str(OUT/music['file']),'rb') as stream:
        music_pcm=np.frombuffer(stream.readframes(n),'<i2').reshape(-1,2)
    music_windows=[[0.,duration]]
    music_mask=np.ones(n,dtype=bool)
    interval_presence=[]
    for cycle in timeline['cycles']:
        for name in ('sink','wash','wipe','throw','zoom'):
            start,end=cycle[name]
            segment=music_pcm[round(start*SR):round(end*SR)]
            assert segment.any(),(cycle['id'],name,'music unexpectedly absent')
            interval_presence.append({'cycle':cycle['id'],'phase':name,'rms_dbfs_pre_master':db(float(np.sqrt(np.mean((segment.astype(np.float64)/32768.)**2))))})
    assert music_pcm[round(timeline['final'][0]*SR):].any()
    audit = {'episode': '03', 'title': timeline['titre'], 'timeline_version': 6,
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
        'salt_events': [{k:e[k] for k in ('name', 'kind', 'start', 'duration',
                                        'end_seconds', 'first_above_one_percent_seconds', 'seed')}
                        for e in salt_events],
        'seed_identity': 'V12 sound-name seeds retained; old tiny cycle4 mapped to cycle5; salt ritual and grains have separate deterministic seeds.',
        'final_hold_seconds': [hold_start, hold_end],
        'final_hold_rms_dbfs': db(float(np.sqrt(np.mean(pause**2)))),
        'final_hold_cooking_only':False, 'final_hold_music_present':True,
        'tiny_paper_cycle': 5,
        'tiny_paper_events': [{k:e[k] for k in ('name','kind','start','duration','peak_dbfs')}
                              for e in tiny_events],
        'reveal_seconds_without_explanatory_cue': reveal,
        'rhythm':timeline['rhythm'],
        'opening_stir_seconds':[0.,timeline['cooking_events'].get('stir_end',2.2)],
        'first_wash_start_seconds':first_wash_start,
        'whistle_phrase_count':1,'whistle_note_count':len(whistles),
        'whistle_notes':[{k:e[k] for k in ('name','phrase','start','end','frequency_hz',
                                          'first_above_one_percent_seconds')} for e in whistles],
        'whistles_only_during_cooking':True,
        'whistles_only_before_first_wash':True,
        'last_whistle_end_seconds':max(e['end_seconds'] for e in whistles),
        'background_music':{'event_file':music['file'],'bpm':timeline['background_music']['bpm'],
                            'windows_seconds':music_windows,'peak_dbfs_before_master':music['peak_dbfs_measured'],
                            'outside_window_nonzero_samples':int(np.count_nonzero(music_pcm[~music_mask])),
                            'all_washing_wiping_throwing_and_final_music_silent':False,
                            'continuous_music':True,'sink_duck_db':-1.5,
                            'music_present_action_intervals':interval_presence,
                            'parameters':music['parameters']},
        'water_event_gain_change_db_vs_v5':4.,
        'first_and_last_pcm_frame_silent': True,
        'no_background_music':False,'original_background_music':True,
        'no_external_music':True,'no_speech':True,
        'no_recorded_voice':True,'character_synthetic_whistle':True,
        'no_external_samples': False, 'original_foley_and_whistle':True,
        'third_party_instrument_bank':'TimGM6mb GPL-2; bundled assets and credits', 'mix_sha256': sha(OUT/'mix.wav'),
        'source_sha256': sha(__file__),
        'music_source_sha256':sha(Path(__file__).with_name('music.py')),
        'mix_stage_gain_db_by_kind':MIX_GAIN_DB,
        'master_gain_linear_exact':master_gain,
        'reference_premaster_peak_exact':reference_premaster_peak,
        'master_reference':'fixed V15 value 2.124210976406158; no new global normalization',
        'chronologie_sha256': hashlib.sha256(timeline_bytes).hexdigest(),
        'limits': 'Contrôles numériques PCM et concordance avec les événements prévus. Pas d’écoute humaine, de contrôle haut-parleur mobile ni de validation des contacts dans la vidéo par ce rapport.'}
    provenance = {'title': timeline['titre'], 'timeline_version': 6,
        'provenance': 'Effets, trois notes sifflées initiales et partition de fond originaux. Bruitages et sifflement synthétisés localement comme V14. Nouvelle partition rendue hors ligne par FluidSynth avec la banque d’instruments tierce TimGM6mb sous GPL-2, incluse et créditée dans assets. Aucun morceau, boucle musicale ou service à crédits importé. Sifflement uniquement avant le premier lavage ; musique continue pendant tout l’épisode, avec baisse légère de 3 dB au lavabo, puis retour progressif au niveau normal. Aucun dialogue.',
        'tools': ['Python (PSF)', 'NumPy (BSD-3-Clause)', 'wave (bibliothèque standard)', 'FluidSynth (LGPL-2.1)', 'TimGM6mb instrument data (GPL-2)'],
        'sample_rate': SR, 'channels': 2, 'bit_depth': 16, 'duration_seconds': duration,
        'master_gain_db': audit['master_gain_db'],
        'event_bank_levels': 'WAV individuels conservés avant réglage de mix. Appliquer à chaque événement son mix_gain_db, sommer aux start_sample, appliquer master_gain_db puis enveloppe globale attaque8ms/sortie35ms.',
        'mix_stage_gain_db_by_kind':MIX_GAIN_DB,
        'chronologie_sha256': audit['chronologie_sha256'], 'source_sha256': audit['source_sha256'],
        'events': metadata,'rhythm':timeline['rhythm'],
        'whistle_notes':timeline['whistle_notes'],
        'background_music':audit['background_music'],
        'no_background_music':False,'original_background_music':True,
        'no_external_music':True,'no_speech':True,
        'no_recorded_voice':True,'character_synthetic_whistle':True,
        'reproduction': '.venv/bin/python -B episodes/03/cuisine_v17/sources/son.py',
        'limits': audit['limits']}
    assert TIMELINE.read_bytes() == timeline_bytes, 'chronologie changed while synthesizing'
    atomic_json(OUT/'provenance.json', provenance)
    atomic_json(AUDIT, audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


def read_pcm(path):
    with wave.open(str(path), 'rb') as source:
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (SR, 2, 2)
        return np.frombuffer(source.readframes(source.getnframes()), '<i2').reshape(-1, 2).copy()


def write_pcm(path, pcm):
    """Write integer PCM without a float round-trip or gain change."""
    assert pcm.ndim == 2 and pcm.shape[1] == 2
    fd, name = tempfile.mkstemp(prefix='.'+path.name, suffix='.tmp', dir=path.parent)
    os.close(fd)
    try:
        with wave.open(name, 'wb') as output:
            output.setnchannels(2); output.setsampwidth(2); output.setframerate(SR)
            output.writeframes(pcm.astype('<i2').tobytes())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def v20_patch_main():
    """Add one original floor contact to the unchanged, bundled V19 mix."""
    timeline_bytes = TIMELINE.read_bytes()
    timeline = json.loads(timeline_bytes)
    overflow = timeline.get('overflow')
    assert overflow, 'V20 requires the approved overflow timeline before sound rendering'
    reference_path = OUT/'mix_reference_v19.wav'
    assert sha(reference_path) == BASE_MIX_SHA256, 'The frozen V19 mix changed'
    base = read_pcm(reference_path)
    duration = float(timeline['duration'])
    assert len(base) == round(duration*SR) == 1968000
    reference_provenance = json.loads((OUT/'provenance_reference_v19.json').read_text())
    audit = json.loads((OUT/'audit_reference_v19.json').read_text())
    # Frozen provenance is input evidence; verify every retained editable WAV.
    retained = {e['file']:e['sha256'] for e in reference_provenance['events']}
    params = reference_provenance['background_music']['parameters']
    retained.update({s['file']:s['sha256'] for s in params['stems']})
    retained[params['unattenuated_reference']['file']] = params['unattenuated_reference']['sha256']
    assert all(sha(OUT/name) == expected for name, expected in retained.items()), 'A retained sound changed'
    # All 64 pre-existing events keep their timing, pan, gain and duration.
    planned = events_for(timeline)
    previous = reference_provenance['events']
    assert len(planned) == len(previous) == 64
    fields = ('name', 'kind', 'start', 'duration', 'peak_dbfs', 'pan', 'cycle')
    assert all(all(a.get(k) == b.get(k) for k in fields) for a,b in zip(planned, previous))
    when = float(overflow['floor_land'])
    event = {'name':'c5_papier_sol', 'kind':'tiny_paper_floor', 'start':when,
             'duration':.12, 'peak_dbfs':-37.5, 'pan':-.35, 'cycle':5}
    mono, parameters = make_sound(event['kind'], event['duration'], FLOOR_SEED)
    signal = stereo(mono, event['peak_dbfs'], event['pan'])
    cue_path = OUT/(event['name']+'.wav')
    write_wave(cue_path, signal)  # Same pre-master bank convention as V19.
    start = round(when*SR); end = start+len(signal)
    assert 0 <= start < end <= len(base)
    global_envelope = envelope(len(base), .008, .035)[start:end, None]
    delta = np.rint(signal*MASTER_GAIN_EXACT*global_envelope*32767.).astype(np.int32)
    result = base.astype(np.int32)
    result[start:end] += delta
    assert np.max(np.abs(result)) < 32767, 'Clipping after the floor addition'
    write_pcm(OUT/'mix.wav', result)
    actual = read_pcm(OUT/'mix.wav')
    assert np.array_equal(actual[:start], base[:start])
    assert np.array_equal(actual[end:], base[end:])
    assert np.array_equal(actual[start:end].astype(np.int32)-base[start:end], delta)
    peak = float(np.abs(signal).max())
    above = np.flatnonzero(np.max(np.abs(signal),axis=1) > max(2./32768.,peak*.01))
    item = {**event, 'file':cue_path.name, 'seed':FLOOR_SEED, 'mix_gain_db':0.,
            'start_sample':start, 'samples':len(signal), 'end_seconds':end/SR,
            'first_above_one_percent_seconds':(start+int(above[0]))/SR,
            'peak_dbfs_measured':db(peak), 'parameters':parameters, 'sha256':sha(cue_path),
            'render_stage':'pre-master bank; rounded post-master contribution added to the frozen V19 PCM'}
    normalized = actual.astype(np.float64)/32768.
    hold_start,hold_end = timeline['final_hold']
    audit.update(title=timeline['titre'], event_count=65,
                 peak_dbfs=db(float(np.abs(normalized).max())),
                 rms_dbfs_left_right=[db(float(x)) for x in np.sqrt(np.mean(normalized**2,axis=0))],
                 dc_mean_left_right=normalized.mean(axis=0).tolist(),
                 clipped_samples=0, mix_sha256=sha(OUT/'mix.wav'),
                 source_sha256=sha(__file__),
                 chronologie_sha256=hashlib.sha256(timeline_bytes).hexdigest(),
                 final_hold_seconds=[hold_start,hold_end],
                 final_hold_rms_dbfs=db(float(np.sqrt(np.mean(normalized[round(hold_start*SR):round(hold_end*SR)]**2)))),
                 floor_contact={k:item[k] for k in ('name','kind','start','duration','end_seconds',
                                                    'first_above_one_percent_seconds','peak_dbfs','seed')},
                 baseline_mix_reference={'file':reference_path.name,'sha256':BASE_MIX_SHA256,
                                         'operation':'integer PCM addition, no rerender or normalization',
                                         'unchanged_outside_seconds':[when,end/SR]})
    audit['tiny_paper_events'] = audit['tiny_paper_events'] + [
        {k:item[k] for k in ('name','kind','start','duration','peak_dbfs')}]
    audit['seed_identity'] += ' New floor contact uses separate fixed seed 3041672.'
    provenance = reference_provenance.copy()
    provenance.update(title=timeline['titre'], chronologie_sha256=audit['chronologie_sha256'],
                      source_sha256=audit['source_sha256'], events=previous+[item],
                      provenance=reference_provenance['provenance'].replace('de 3 dB','de 1,5 dB')
                        +' V20 : seul un contact original de papier au sol est ajouté au mix PCM V19 conservé ; '
                         'musique, dosage, tous les anciens bruitages et impact du tas à 39,1 s sont intacts.',
                      reproduction='.venv/bin/python -B episodes/03/cuisine_v20/sources/son.py',
                      event_bank_levels='Les 64 événements de référence décrivent le mix V19 inclus dans '
                        'mix_reference_v19.wav ; ne pas les sommer à nouveau au mix de base. '
                        'Le nouveau c5_papier_sol.wav est fourni pré-master comme les autres banques. '
                        'Pour reproduire exactement V20 : synthétiser sa contribution, appliquer le '
                        'master fixe et l’enveloppe globale, arrondir en PCM16 puis additionner ces '
                        'entiers au mix de référence aux start_sample. Aucune normalisation globale.',
                      baseline_mix_reference=audit['baseline_mix_reference'])
    delta_frames = np.flatnonzero(np.any(actual != base, axis=1))
    report = {'passed':True, 'duration_seconds':duration, 'sample_rate':SR,
              'base_mix_sha256':BASE_MIX_SHA256, 'mix_sha256':audit['mix_sha256'],
              'music_source_sha256':sha(Path(__file__).with_name('music.py')),
              'retained_sound_files_byte_identical':retained,
              'retained_event_count':64, 'new_event':item,
              'changed_frame_count':len(delta_frames),
              'first_changed_second':float(delta_frames[0]/SR),
              'last_changed_second':float(delta_frames[-1]/SR),
              'identical_pcm_before_and_after_cue':True, 'integer_addition_reproduces_exact_mix':True,
              'no_clipping':True, 'peak_dbfs':audit['peak_dbfs'],
              'limits':audit['limits']}
    assert TIMELINE.read_bytes() == timeline_bytes, 'Timeline changed while rendering sound'
    atomic_json(OUT/'provenance.json', provenance)
    atomic_json(AUDIT, audit)
    atomic_json(EP/'controle/audit_son_chute_v20.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('retained_sound_files_byte_identical','new_event')},
                     ensure_ascii=False, indent=2))


def _original_v20_pcm(reference):
    """Recreate V20 from bundled V19 PCM and the exact original floor cue."""
    mono, parameters = make_sound('tiny_paper_floor', .12, FLOOR_SEED)
    signal = stereo(mono, -37.5, -.35)
    start = round(39.85*SR); end = start+len(signal)
    old_envelope = envelope(len(reference), .008, .035)[start:end, None]
    result = reference.astype(np.int32)
    result[start:end] += np.rint(signal*MASTER_GAIN_EXACT*old_envelope*32767.).astype(np.int32)
    return result.astype('<i2')


def _continued_music(duration, specification, calibration):
    """Render the same global score, keeping the previous fixed calibration."""
    import importlib.util
    path = Path(__file__).with_name('music.py')
    spec = importlib.util.spec_from_file_location('mou_fixed_jazz_continuation', path)
    music = importlib.util.module_from_spec(spec); spec.loader.exec_module(music)
    assert sha(music.SOUNDFONT) == music.SF2_SHA
    lib = music._api()
    score = music.compose({'duration':duration, 'bpm':specification['bpm']})
    n = round(duration*SR)
    reference = np.zeros(n)
    for track in music.TRACKS:
        notes = [e for e in score if e['track'] == track]
        reference += music._render_track(lib, track, notes, 0., duration)
    reference *= music._envelope(n, .02, .22)*calibration
    signal = reference*music.gain_envelope(duration, specification)
    return np.column_stack((signal, signal)), score, lib.fluid_version_str().decode()


def _cloth_sound(length):
    """One soft original cotton friction, without a paper-tear transient."""
    n = round(length*SR); u = np.arange(n)/n
    signal = band_noise(n, 120., 2200., 3041809)
    signal *= np.sin(np.pi*u)**1.6
    signal *= envelope(n, .028, .05)
    return stereo(signal, -35., -.05)


def main():
    """Extend only the ending, without recomposing or renormalizing the mix."""
    timeline_bytes = TIMELINE.read_bytes(); timeline = json.loads(timeline_bytes)
    duration = float(timeline['duration']); assert duration == 44.5
    OUT.mkdir(parents=True, exist_ok=True); AUDIT.parent.mkdir(parents=True, exist_ok=True)
    reference_path = OUT/'mix_reference_v19.wav'
    assert sha(reference_path) == BASE_MIX_SHA256
    reference = read_pcm(reference_path)
    assert reference.shape == (1968000,2)
    baseline = _original_v20_pcm(reference)
    baseline_sha = hashlib.sha256(baseline.tobytes()).hexdigest()
    assert baseline_sha == 'ef140d9ececf58d36b85dee3645b1e2a58f41dea988877b469d644728c128ab0', 'V20 PCM reconstruction differs'
    provenance19 = json.loads((OUT/'provenance_reference_v19.json').read_text())
    audit19 = json.loads((OUT/'audit_reference_v19.json').read_text())
    previous = provenance19['events']
    params = provenance19['background_music']['parameters']
    retained = {e['file']:e['sha256'] for e in previous}
    retained.update({e['file']:e['sha256'] for e in params['stems']})
    retained[params['unattenuated_reference']['file']] = params['unattenuated_reference']['sha256']
    assert all(sha(OUT/name) == expected for name,expected in retained.items())
    floor_mono,_ = make_sound('tiny_paper_floor', .12, FLOOR_SEED)
    floor_signal = stereo(floor_mono,-37.5,-.35)
    assert np.array_equal(read_pcm(OUT/'c5_papier_sol.wav'),np.rint(floor_signal*32767.).astype('<i2'))
    retained['c5_papier_sol.wav'] = sha(OUT/'c5_papier_sol.wav')

    start_time, end_time = 40.5, 40.75
    start, end = round(start_time*SR), round(end_time*SR)
    n = round(duration*SR)
    calibration = float(params['global_calibration_linear'])
    music_spec = {**params['effective_specification'], 'duration':duration,
                  'windows':[[0.,duration]]}
    music, score, fluid_version = _continued_music(duration, music_spec, calibration)
    old_music = read_pcm(OUT/'musique_cuisine.wav').astype(np.float64)/32767.
    # Future notes and a longer ending cannot alter the prior synthesized signal.
    music_prefix = np.rint(music[:start]*32767.).astype('<i2')
    old_music_pcm = read_pcm(OUT/'musique_cuisine.wav')
    assert np.array_equal(music_prefix, old_music_pcm[:start]), 'Continuation changed the musical prefix'
    old_global = envelope(len(baseline), .008, .035)[:,None]
    old_music_post = old_music*MASTER_GAIN_EXACT*old_global
    old_residual = baseline.astype(np.float64)/32767.-old_music_post

    # The quiet cooking texture continues with new original noise. It is not
    # a musical loop, and its mix level retains the previous final0.55 gain.
    length = duration-start_time
    frying, _ = make_sound('frying', length, 3041946)
    frying = stereo(frying, -31., -.2)*.55
    new_music = music[start:]*MASTER_GAIN_EXACT
    new_residual = frying*MASTER_GAIN_EXACT
    new_global = envelope(n, .008, .035)[start:,None]
    new_music *= new_global; new_residual *= new_global
    result = np.zeros((n,2), dtype=np.int32)
    result[:start] = baseline[:start]
    span = end-start
    u = np.linspace(0.,1.,span)
    weight = smooth(u)[:,None]
    angle = weight*math.pi/2.
    # Coherent, phase-aligned music uses a linear blend (no +3dB boost).
    # Independent low cooking noise uses equal-power weights.
    seam = ((1.-weight)*old_music_post[start:end] + weight*new_music[:span]
            + np.cos(angle)*old_residual[start:end] + np.sin(angle)*new_residual[:span])
    tail = new_music+new_residual
    tail[:span] = seam
    result[start:] = np.rint(tail*32767.).astype(np.int32)

    # The gesture includes approach/retraction; sound follows cloth contact only.
    wipe_start,wipe_end = map(float,timeline['ending_apron']['cloth_contact'])
    cloth = _cloth_sound(wipe_end-wipe_start)
    a,b = round(wipe_start*SR), round(wipe_end*SR)
    result[a:b] += np.rint(cloth*MASTER_GAIN_EXACT*envelope(n,.008,.035)[a:b,None]*32767.).astype(np.int32)
    assert np.abs(result).max() < 32767 and not result[0].any() and not result[-1].any()
    write_pcm(OUT/'mix.wav', result)
    actual = read_pcm(OUT/'mix.wav')
    assert np.array_equal(actual[:start],baseline[:start])

    write_wave(OUT/'musique_extension_v21.wav', music[start:])
    write_wave(OUT/'cuisson_extension_v21.wav', frying)
    write_wave(OUT/'tablier_essuie.wav', cloth)
    floor_event = {'name':'c5_papier_sol','kind':'tiny_paper_floor','start':39.85,
                   'duration':.12,'peak_dbfs':-37.5,'pan':-.35,'cycle':5,
                   'seed':FLOOR_SEED,'file':'c5_papier_sol.wav','sha256':sha(OUT/'c5_papier_sol.wav')}
    new_events = [floor_event,
        {'name':'musique_extension_v21','kind':'background_music_continuation','start':start_time,
         'duration':length,'file':'musique_extension_v21.wav','sha256':sha(OUT/'musique_extension_v21.wav'),
         'render_stage':'pre-master, fixed original calibration; crossfade recipe required'},
        {'name':'cuisson_extension_v21','kind':'frying_continuation','start':start_time,
         'duration':length,'file':'cuisson_extension_v21.wav','sha256':sha(OUT/'cuisson_extension_v21.wav'),
         'seed':3041946,'render_stage':'pre-master at retained final0.55 perspective level'},
        {'name':'tablier_essuie','kind':'cloth_wipe','start':wipe_start,'duration':wipe_end-wipe_start,
         'peak_dbfs':-35.,'pan':-.05,'seed':3041809,'file':'tablier_essuie.wav',
         'sha256':sha(OUT/'tablier_essuie.wav'),'render_stage':'pre-master addition'}]
    recipe = {'baseline':'Bundled V19 PCM plus exact original39.85s floor cue = V20.',
              'prefix_pcm_identical_until_seconds':start_time,
              'crossfade_seconds':[start_time,end_time],
              'music_blend':'Linear smoothstep of phase-aligned old/new music, fixed calibration.',
              'frying_blend':'Equal-power of the old residual and new low cooking texture.',
              'after_crossfade':'Continued global score + low cooking texture, same fixed master.',
              'cloth_wipe_seconds':[wipe_start,wipe_end],
              'new_final_master_fade_seconds':[duration-.035,duration],
              'no_new_global_normalization':True}
    normalized = actual.astype(np.float64)/32768.
    music_active = music*MASTER_GAIN_EXACT
    windows = []
    for t in np.arange(40.25,44.15,.02):
        segment = music_active[round(t*SR):round((t+.1)*SR)]
        windows.append({'start':round(float(t),3),'rms_dbfs':float(20.*np.log10(max(np.sqrt(np.mean(segment**2)),1.e-15)))})
    minimum = min(e['rms_dbfs'] for e in windows)
    assert minimum > -55., ('Unexpected music hole', minimum)
    differences = np.abs(np.diff(actual.astype(np.int32),axis=0))
    seam_jumps = {str(t):int(differences[round(t*SR)-1].max()) for t in (start_time,end_time)}
    neighborhood = differences[round(40.2*SR):round(41.*SR)]
    assert max(seam_jumps.values()) < max(20.,float(np.quantile(neighborhood,.999))*2.)
    background = {**provenance19['background_music'],
                  'windows_seconds':[[0.,duration]],
                  'effective_duration_seconds':duration,
                  'reference_event_file':'musique_cuisine.wav',
                  'continuation_event_file':'musique_extension_v21.wav',
                  'parameters':{**params,'notes':score,'windows_seconds':[[0.,duration]],
                                'effective_specification':music_spec,
                                'global_calibration_linear':calibration,'calibration_recomputed':False,
                                'fluidsynth_version':fluid_version,'extension_starts_seconds':start_time,
                                'extension_file':'musique_extension_v21.wav','music_source_sha256':sha(Path(__file__).with_name('music.py'))}}
    audit = {**audit19,'title':timeline['titre'],'duration_seconds':duration,
             'samples_per_channel':n,'event_count':len(previous)+len(new_events),
             'source_sha256':sha(__file__),'chronologie_sha256':hashlib.sha256(timeline_bytes).hexdigest(),
             'mix_sha256':sha(OUT/'mix.wav'),'peak_dbfs':db(float(np.abs(normalized).max())),
             'rms_dbfs_left_right':[db(float(v)) for v in np.sqrt(np.mean(normalized**2,axis=0))],
             'clipped_samples':0,'final_hold_seconds':timeline['final_hold'],
             'final_hold_rms_dbfs':db(float(np.sqrt(np.mean(normalized[round(timeline['final_hold'][0]*SR):]**2)))),
             'background_music':background,'mix_recipe':recipe,
             'limits':'Numerical and source checks only; no listening, phone playback or audience approval claimed.'}
    provenance = {**provenance19,'title':timeline['titre'],'duration_seconds':duration,
                  'source_sha256':audit['source_sha256'],'chronologie_sha256':audit['chronologie_sha256'],
                  'events':previous+new_events,'background_music':background,'mix_recipe':recipe,
                  'event_bank_levels':'Reference banks plus added tail assets; do not sum all WAVs. Follow mix_recipe or run son.py.',
                  'reproduction':'.venv/bin/python -B episodes/03/cuisine_v21/sources/son.py',
                  'provenance':'Original Foley/whistle and global jazz score with credited GPL TimGM6mb samples. Exact V20 PCM prefix, same score and calibration continued; one original cloth friction. No speech or imported musical loop.',
                  'limits':audit['limits']}
    report = {'status':'passed','duration_seconds':duration,'source_sha256':audit['source_sha256'],
              'chronologie_sha256':audit['chronologie_sha256'],'mix_sha256':audit['mix_sha256'],
              'baseline_v20_pcm_sha256':baseline_sha,'identical_pcm_prefix_seconds':start_time,
              'old_music_pcm_prefix_exact':True,'old_fixed_calibration':calibration,
              'music_source_byte_unchanged_sha256':sha(Path(__file__).with_name('music.py')),
              'retained_wavs_byte_identical':retained,'mix_recipe':recipe,
              'music_100ms_windows_step20ms':windows,'minimum_music_100ms_rms_dbfs':minimum,
              'crossfade_boundary_jump_lsb':seam_jumps,'no_clipping':True,
              'peak_dbfs':audit['peak_dbfs'],'limits':audit['limits']}
    assert TIMELINE.read_bytes() == timeline_bytes, 'Timeline changed during sound rendering'
    atomic_json(OUT/'provenance.json',provenance); atomic_json(AUDIT,audit)
    atomic_json(EP/'controle/audit_audio_v21.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('retained_wavs_byte_identical','music_100ms_windows_step20ms')},indent=2))


if __name__ == '__main__':
    main()
