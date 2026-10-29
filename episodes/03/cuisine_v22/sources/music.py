"""One original jazz accompaniment on a single global 108 BPM clock.

The score knows only duration and tempo. Visual cuts, cooking windows and
washing intervals cannot affect a note, phrase or voice. Only the final gain
envelope receives washing intervals. Instruments: bundled GPL-2 TimGM6mb.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import hashlib
import math
from pathlib import Path
import numpy as np

SR=48000
SOUNDFONT=Path(__file__).resolve().parents[1]/'assets/TimGM6mb.sf2'
SF2_SHA='c5378b62028c920cb11e4803327983fee2f2cdff5dc89c708e39da417e51c854'
TRACKS={
    'basse':{'program':32,'bank':0,'channel':0,'gain':.72,'instrument':'acoustic_double_bass'},
    'accords':{'program':4,'bank':0,'channel':1,'gain':.95,'instrument':'electric_piano_1'},
    'ponctuations':{'program':0,'bank':0,'channel':2,'gain':.36,'instrument':'gentle_acoustic_piano'},
    'percussions':{'program':40,'bank':128,'channel':9,'gain':.25,'instrument':'soft_brush_kit'},
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
    """Musical form only: 4/4 bars, light swing, and an eight-bar A-major cycle."""
    duration=float(specification['duration'])
    beat=60./float(specification['bpm'])
    score=[]
    # The same harmonic form runs across the whole film, irrespective of edits.
    voicings=((57,61,64,66),(57,61,64,66),(57,62,66,69),(57,62,66,69),
              (57,59,62,66),(56,62,66,68),(57,61,64,66),(56,62,66,68))
    walking=((45,49,52,54),(45,47,49,52),(50,54,57,54),(50,49,47,45),
             (47,50,54,52),(52,56,59,56),(45,49,52,54),(52,50,49,47))
    responses=((64,66,64,61),(66,69,66,62),(66,64,62,61),(64,61,59,61))
    swing=.58
    def add(track,global_beat,pitch,beats,velocity):
        onset=float(global_beat)*beat
        if onset>=duration-.035:return
        length=min(float(beats)*beat,duration-onset-.005)
        if length<.02:return
        score.append({'window':1,'track':track,'instrument':TRACKS[track]['instrument'],
                      'bar_index':int(global_beat//4),
                      'global_beat':round(float(global_beat),9),
                      'start':round(onset,9),'duration':round(length,9),
                      'midi_note':int(pitch),'velocity':int(velocity)})
    # Sustained instrument releases overlap audibly, but consecutive same-pitch
    # MIDI gates do not overlap: a previous noteoff cannot cancel a newer note.
    add('accords',0.,61,.45,35)
    add('accords',0.,64,.45,33)
    add('accords',0.,66,.45,31)
    for bar in range(math.ceil(duration/(4.*beat))):
        harmony=bar%8;base=bar*4
        for position in range(4):
            g=base+position
            add('basse',g,walking[harmony][position],.94,
                (61,55,59,54)[position])
            # Interlocking comp on the same swung offbeat every pulse; no
            # sparse handmade inserts or level changes at action contacts.
            for j,pitch in enumerate(voicings[harmony]):
                add('accords',g+swing,pitch,.98,
                    (42,37,41,36)[position]-j*2)
            add('percussions',g,38,.44,29 if position%2 else 31)
            add('percussions',g+swing,42,.24,22)
            if position in (0,2):add('percussions',g,36,.35,28)
        # A modest two-bar call/answer after the unmodified opening whistle.
        # Melodic rests do not stop the bass, chords or brushes.
        if bar>=1 and bar%2==1:
            phrase=responses[(bar//2)%len(responses)]
            for position,pitch,velocity in zip((.58,1.58,2.,3.58),phrase,(46,41,44,39)):
                add('ponctuations',base+position,pitch,.34,velocity)
    return sorted(score,key=lambda e:(e['start'],e['track'],e['midi_note']))


def gain_envelope(length,specification):
    """Slow, light ducking; this envelope never edits the musical score."""
    n=round(float(length)*SR);times=np.arange(n)/SR
    gain=np.ones(n,dtype=np.float64)
    depth=10.**(float(specification.get('duck_db',-3.))/20.)
    attack=float(specification.get('duck_attack_seconds',.5))
    release=float(specification.get('duck_release_seconds',.7))
    for start,end in specification['duck_intervals']:
        entry=np.clip((times-(float(start)-attack))/attack,0.,1.)
        exit=np.clip((float(end)+release-times)/release,0.,1.)
        entry=entry*entry*(3.-2.*entry);exit=exit*exit*(3.-2.*exit)
        gain*=1.-(1.-depth)*entry*exit
    return gain


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
    del seed
    assert SOUNDFONT.is_file()
    assert hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest()==SF2_SHA
    lib=_api();score=compose({'duration':float(length),'bpm':float(specification['bpm'])})
    n=round(float(length)*SR)
    raw_tracks={}
    for track in TRACKS:
        notes=[event for event in score if event['track']==track]
        # MIDI overlap is a separate event-scheduling error, not musical glue.
        gates={}
        for event in notes:
            previous=gates.get(event['midi_note'],-1.)
            assert event['start']>=previous-1e-8,(track,event['midi_note'],'overlapping note gates')
            gates[event['midi_note']]=event['start']+event['duration']
        raw_tracks[track]=_render_track(lib,track,notes,0.,float(length))*_envelope(n,.02,.22)
    raw=sum(raw_tracks.values())
    # A single constant calibration, independent of washing intervals. It is
    # never recalculated per shot and cannot pump around an action or cut.
    a=min(n-1,round(2.*SR));b=max(a+1,n-round(.5*SR))
    rms=float(np.sqrt(np.mean(raw[a:b]**2)))
    target_post=float(specification.get('target_music_rms_dbfs_after_master',-31.))
    master=float(specification.get('master_gain_linear',2.124210976406158))
    calibration=10.**(target_post/20.)/(master*max(rms,1e-12))
    for track in raw_tracks:raw_tracks[track]*=calibration
    reference=sum(raw_tracks.values())
    envelope=gain_envelope(length,specification)
    tracks={track:data*envelope for track,data in raw_tracks.items()}
    signal=reference*envelope
    parameters={'source':'Original global jazz score rendered locally by FluidSynth with the bundled third-party GPL-2 TimGM6mb instrument bank.',
        'intention':'Accompagnement jazz régulier sur une grille unique ; aucun ancien raccord de partition, niveau stable et baisse légère sous l’eau.',
        'bpm':float(specification['bpm']),'meter_beats':4,'tonal_center':'A major, A6/D6/Bm7/E9 eight-bar form',
        'style':'discreet cartoon jazz','swung_eighth_ratio':.58,
        'notes':score,'instruments':TRACKS,'windows_seconds':[[0.,float(length)]],
        'continuous_score':True,'one_global_clock':True,'visual_cut_restarts':0,
        'render_sessions_per_instrument':1,'composition_inputs':['duration','bpm'],
        'frame_or_action_dependent_notes':False,'same_pitch_midi_gate_overlaps':0,
        'fluidsynth_version':lib.fluid_version_str().decode(),
        'soundfont':{'file':'assets/TimGM6mb.sf2','sha256':SF2_SHA,'license':'GPL-2; see bundled notices'},
        'global_calibration_linear':calibration,
        'calibration_body_seconds':[a/SR,b/SR],
        'target_music_rms_dbfs_after_master':target_post,
        'raw_body_rms_dbfs_after_master':20.*math.log10(float(np.sqrt(np.mean(reference[a:b]**2)))*master),
        'duck_db':float(specification['duck_db']),'duck_intervals':specification['duck_intervals'],
        'duck_attack_seconds':float(specification['duck_attack_seconds']),
        'duck_release_seconds':float(specification['duck_release_seconds']),
        'duck_gain_min':float(envelope.min()),'duck_gain_max':float(envelope.max()),
        'ducking_never_mutes':bool(envelope.min()>0.),
        'window_attack_seconds':.02,'window_release_seconds':.22,
        'no_new_melody_before_seconds':4.*60./float(specification['bpm']),
        'chorus':False,'reverb_tail_seconds':0.}
    return signal,parameters,tracks,reference
