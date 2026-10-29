"""Original discreet cartoon-jazz cooking score, rendered offline by FluidSynth/TimGM6mb.

No tune or loop is imported. The instrument bank is third-party GPL-2 data;
see ../assets/TimGM6mb_COPYRIGHT.txt. No audio device or paid service is used.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import math
from pathlib import Path

import numpy as np

SR = 48000
SOUNDFONT = Path(__file__).resolve().parents[1]/'assets/TimGM6mb.sf2'
SF2_SHA = 'c5378b62028c920cb11e4803327983fee2f2cdff5dc89c708e39da417e51c854'
TRACKS = {
    'basse': {'program': 32, 'bank': 0, 'channel': 0, 'gain': .90,
              'instrument': 'acoustic_double_bass'},
    'accords': {'program': 4, 'bank': 0, 'channel': 1, 'gain': .65,
               'instrument': 'electric_piano_1'},
    'ponctuations': {'program': 0, 'bank': 0, 'channel': 2, 'gain': .42,
               'instrument': 'gentle_acoustic_piano'},
    'percussions': {'program': 40, 'bank': 128, 'channel': 9, 'gain': .28,
                   'instrument': 'soft_brush_kit'},
}


def _api():
    lib = ctypes.CDLL(ctypes.util.find_library('fluidsynth') or 'libfluidsynth.so.3')
    signatures = {
        'new_fluid_settings': (ctypes.c_void_p, []),
        'delete_fluid_settings': (None, [ctypes.c_void_p]),
        'fluid_settings_setnum': (ctypes.c_int, [ctypes.c_void_p,ctypes.c_char_p,ctypes.c_double]),
        'fluid_settings_setint': (ctypes.c_int, [ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int]),
        'new_fluid_synth': (ctypes.c_void_p,[ctypes.c_void_p]),
        'delete_fluid_synth': (None,[ctypes.c_void_p]),
        'fluid_synth_sfload': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int]),
        'fluid_synth_program_select': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
        'fluid_synth_cc': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
        'fluid_synth_noteon': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
        'fluid_synth_noteoff': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),
        'fluid_synth_write_float': (ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),
        'fluid_version_str': (ctypes.c_char_p,[]),
    }
    for name,(result,args) in signatures.items():
        fn=getattr(lib,name);fn.restype=result;fn.argtypes=args
    return lib


def _envelope(n, attack=.012, release=.012):
    result=np.ones(n,dtype=np.float64)
    a=min(n,max(2,round(attack*SR)));b=min(n,max(2,round(release*SR)))
    result[:a]*=np.sin(np.linspace(0.,math.pi/2.,a))**2
    result[-b:]*=np.cos(np.linspace(0.,math.pi/2.,b))**2
    return result


def compose(specification):
    """Short responses with their own endings, rather than a restarted loop."""
    beat=60./float(specification['bpm'])
    windows=specification['windows']
    score=[]
    # Each instrument leaves room around important visible cooking contacts.
    contact_holes=((14.55,.12),(15.25,.12),(15.95,.10),(22.30,.12))
    def note(window,track,local,pitch,beats,velocity):
        start,end=map(float,windows[window])
        local=float(local)
        # Written light swing, only on eighth-note upbeats of the piano and
        # brushes; visual-action/Foley timings are never moved.
        if track in ('ponctuations','percussions'):
            grid=local/beat;whole=math.floor(grid);fraction=grid-whole
            if abs(fraction-.5)<.045:local=(whole+.585)*beat
        absolute=start+local
        if absolute>=end-.11:return
        if track=='percussions' and any(abs(absolute-x)<radius for x,radius in contact_holes):return
        if track in ('ponctuations','percussions') and 27.65<=absolute<=28.55:return
        if track=='ponctuations' and absolute<1.75:return
        duration=min(float(beats)*beat,end-.07-absolute)
        if duration<.035:return
        score.append({'window':window+1,'track':track,'instrument':TRACKS[track]['instrument'],
                      'start':round(absolute,9),'duration':round(duration,9),
                      'midi_note':int(pitch),'velocity':int(velocity)})
    def chord(window,local,pitches,beats,velocity):
        for i,pitch in enumerate(pitches):note(window,'accords',local,pitch,beats,velocity-i*2)

    # Intro: the existing A5-C#6-B5 whistle has the melody until 1.75 seconds.
    # A6/9 and D6 colours give the later small piano response a clear home.
    bass_a=((0.,45,.64,66),(1.,49,.55,53),(2.,52,.55,59),
            (3.,47,.48,51),(4.,50,.61,63),(5.,54,.53,54),
            (6.,52,.53,57),(7.,49,.49,52))
    for bar in range(2):
        for pos,pitch,duration,velocity in bass_a:
            local=(bar*8.+pos)*beat
            if local>7.12:continue
            note(0,'basse',local,pitch,duration,velocity-(4 if bar else 0))
    for local,pitches,dur,vel in (
        (0.,(61,66,71),.65,43),(.98,(61,64,69),.36,35),
        (2.08,(62,66,69),.48,42),(3.12,(61,64,69),.42,38),
        (4.50,(61,66,71),.50,41),(5.58,(62,66,69),.38,39),
        (6.72,(61,64,69),.48,42)):
        chord(0,local,pitches,dur,vel)
    for local,pitch,dur,vel in (
        (1.84,64,.23,59),(2.12,66,.18,45),(2.67,64,.22,54),
        (3.51,61,.20,50),(3.79,59,.20,42),
        (4.61,61,.20,54),(5.03,64,.22,58),(5.72,66,.20,44),
        (6.27,64,.22,52),(6.83,61,.23,53)):
        note(0,'ponctuations',local,pitch,dur,vel)
    for beat_number in range(14):
        local=beat_number*beat
        if local>7.08:break
        note(0,'percussions',local,36 if beat_number%4==0 else 38,.20,
             29 if beat_number%4==0 else 25)
        if beat_number%2==1:
            time=(beat_number+.5)*beat+.009
            if time<7.12:note(0,'percussions',time,42,.10,19)

    # Carrot: a short answer with actual gaps around both knife impacts.
    for local,pitch,dur,vel in ((0.,45,.45,75),(.56,52,.23,59),(1.39,50,.29,68),(2.61,45,.24,65)):
        note(1,'basse',local,pitch,dur,vel)
    for local,pitches in ((.18,(61,66,71)),(.72,(62,66,69)),(2.05,(61,64,69))):
        chord(1,local,pitches,.35,40)
    for local,pitch in ((.30,64),(.58,66),(1.73,64),(2.58,61)):
        note(1,'ponctuations',local,pitch,.19,49)
    for local,pitch,vel in ((0.,36,44),(.29,42,28),(.56,38,24),(.84,42,24),
                            (1.39,36,36),(1.68,42,25),(2.05,42,23),(2.62,38,22)):
        note(1,'percussions',local,pitch,.10,vel)

    # Tomato: recognizable two-note reply, with a hole around the throw.
    for local,pitch,dur,vel in ((0.,45,.42,72),(1.12,52,.23,59)):
        note(2,'basse',local,pitch,dur,vel)
    chord(2,.04,(61,66,71),.40,40)
    for local,pitch in ((.28,64),(.55,61),(1.14,57)):
        note(2,'ponctuations',local,pitch,.18,47)
    for local,pitch,vel in ((0.,36,39),(.29,42,25),(.57,38,23),(1.12,42,22)):
        note(2,'percussions',local,pitch,.10,vel)

    # Salt: held accompaniment, no new sharp music attacks during the grains.
    note(3,'basse',0.,45,.55,68);note(3,'basse',.55,52,.24,54)
    note(3,'basse',1.66,45,.20,58)
    chord(3,.08,(61,66,71),.90,37);chord(3,1.65,(61,64,69),.20,31)
    note(3,'ponctuations',.27,64,.20,44);note(3,'ponctuations',1.69,61,.15,38)
    note(3,'percussions',.01,36,.10,34);note(3,'percussions',.29,42,.10,23)

    # Last clean-handle touch: intentionally abbreviated one-second return.
    note(4,'basse',0.,45,.35,61);chord(4,.04,(61,66,69),.35,35)
    note(4,'ponctuations',.28,61,.18,45);note(4,'ponctuations',.54,57,.16,38)
    note(4,'percussions',.01,36,.10,30)
    return sorted(score,key=lambda e:(e['start'],e['track'],e['midi_note']))


def _render_track(lib, track, notes, start, end):
    spec=TRACKS[track];settings=lib.new_fluid_settings()
    assert settings
    lib.fluid_settings_setnum(settings,b'synth.sample-rate',float(SR))
    lib.fluid_settings_setnum(settings,b'synth.gain',.45)
    lib.fluid_settings_setint(settings,b'synth.reverb.active',0)
    lib.fluid_settings_setint(settings,b'synth.chorus.active',0)
    lib.fluid_settings_setint(settings,b'synth.polyphony',64)
    lib.fluid_settings_setint(settings,b'synth.cpu-cores',1)
    synth=lib.new_fluid_synth(settings);assert synth
    try:
        sfid=lib.fluid_synth_sfload(synth,str(SOUNDFONT).encode(),0);assert sfid>=0
        assert lib.fluid_synth_program_select(synth,spec['channel'],sfid,spec['bank'],spec['program'])==0
        lib.fluid_synth_cc(synth,spec['channel'],10,64)
        lib.fluid_synth_cc(synth,spec['channel'],91,0)
        lib.fluid_synth_cc(synth,spec['channel'],93,0)
        count=round((end-start)*SR)
        events=[]
        for event in notes:
            onset=max(0,round((event['start']-start)*SR))
            off=min(count,round((event['start']+event['duration']-start)*SR))
            events.append((onset,1,event));events.append((off,0,event))
        events.sort(key=lambda v:(v[0],v[1]))
        left=np.zeros(count,dtype=np.float32);right=np.zeros(count,dtype=np.float32)
        position=0
        def render_until(target):
            nonlocal position
            target=min(count,max(position,target))
            if target>position:
                lib.fluid_synth_write_float(synth,target-position,
                    left.ctypes.data,position,1,right.ctypes.data,position,1)
                position=target
        for offset,on,event in events:
            render_until(offset)
            if on:lib.fluid_synth_noteon(synth,spec['channel'],event['midi_note'],event['velocity'])
            else:lib.fluid_synth_noteoff(synth,spec['channel'],event['midi_note'])
        render_until(count)
        result=(left.astype(np.float64)+right.astype(np.float64))*.5*spec['gain']
        return result
    finally:
        lib.delete_fluid_synth(synth);lib.delete_fluid_settings(settings)


def render_background(length,specification,seed):
    del seed  # Deterministic written score; no imported randomized loop.
    assert SOUNDFONT.is_file(),f'Missing GPL instrument bank: {SOUNDFONT}'
    assert hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest()==SF2_SHA
    lib=_api();score=compose(specification)
    n=round(float(length)*SR)
    tracks={name:np.zeros(n,dtype=np.float64) for name in TRACKS}
    for wi,(start,end) in enumerate(specification['windows'],1):
        a,b=round(start*SR),round(end*SR)
        for track in tracks:
            notes=[event for event in score if event['window']==wi and event['track']==track]
            if notes:tracks[track][a:b]=_render_track(lib,track,notes,start,end)*_envelope(b-a)
    # Smooth dips protect the unchanged whistle and small cooking transients.
    times=np.arange(n)/SR
    gain=np.ones(n)
    ducks=[(.25,1.78,.72), (14.43,14.69,.63),(15.13,15.39,.63),
           (15.85,16.08,.68),(22.18,22.44,.64),(27.60,28.60,.55)]
    for start,end,factor in ducks:
        attack=np.clip((times-start)/.035,0.,1.);attack=attack*attack*(3.-2.*attack)
        release=np.clip((end-times)/.055,0.,1.);release=release*release*(3.-2.*release)
        gain*=1.-(1.-factor)*attack*release
    for track in tracks:tracks[track]*=gain
    signal=sum(tracks.values())
    mask=np.zeros(n,dtype=bool)
    for start,end in specification['windows']:mask[round(start*SR):round(end*SR)]=True
    assert not np.any(signal[~mask])
    parameters={'source':'Original score rendered locally by FluidSynth using the third-party GPL-2 TimGM6mb instrument bank; no tune or loop imported.',
        'intention':'Jazz cartoon discret en la majeur : contrebasse acoustique, accords électriques doux, petites réponses de piano et balais légers ; léger swing, respirations et arrêts comiques.',
        'bpm':float(specification['bpm']),'meter_beats':4,'tonal_center':'A major / A6 and D6 colours',
        'style':'discreet cartoon jazz','swung_eighth_ratio':.585,
        'windows_seconds':specification['windows'],'window_attack_seconds':.012,
        'window_release_seconds':.012,'reverb_tail_seconds':0.,'chorus':False,
        'fluidsynth_version':lib.fluid_version_str().decode(),
        'soundfont':{'file':'assets/TimGM6mb.sf2','sha256':SF2_SHA,'license':'GPL-2; see bundled copyright and license files'},
        'instruments':TRACKS,'notes':score,
        'protective_ducks_seconds_gain':[list(d) for d in ducks],
        'no_new_melody_before_seconds':1.75,
        'maximum_abs_sample_outside_windows':0.,
        'restart_motif_on_each_cooking_return':False,
        'short_individually_composed_cooking_responses':True}
    return signal,parameters,tracks
