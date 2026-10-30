"""Original soft piano/bass jazz bed, one 108 BPM grid, no melody or percussion.

Medium-register linked rolled harmonies, two-feel bass, individually softened note
attacks. One music-only RMS calibration; no frame-dependent score or restart.
"""
from __future__ import annotations
import ctypes
import ctypes.util
import hashlib
import math
from pathlib import Path
import struct
import numpy as np

SR=48000
BPM=108.
GRID_ORIGIN=.30
SOUNDFONT=Path(__file__).resolve().parents[1]/'assets/FluidR3_MOU_trio.sf2'
SF2_SHA='c8c326b595c4cf49a5aa58c920ecb27b645deb025652938e7db8b6795eca5fe2'
TARGET_BODY_RMS_DBFS=-41.5
TRACKS={
 'basse':{'program':32,'bank':0,'channel':0,'gain':.55,'pan':54,'instrument':'FluidR3 acoustic double bass, soft two-feel'},
 'accords':{'program':0,'bank':0,'channel':1,'gain':1.,'pan':64,'instrument':'FluidR3 Yamaha grand piano, held medium-register jazz chords'},
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
    duration=float(specification['duration']);beat=60./BPM;notes=[]
    assert float(specification.get('bpm',BPM))==BPM
    voicings=[(59,61,66),(57,61,64),(57,62,66),(56,62,66),
              (56,61,64),(53,59,63),(57,61,64),(56,62,66),
              (56,61,64),(57,61,64),(57,62,66),(56,62,66),
              (57,62,66),(56,61,66),(56,61,64),(57,61,66)]
    roots=[45,42,47,40,45,37,42,40,45,42,47,40,47,40,45,45]
    def add(track,bar,start,pitch,gate_beats,velocity):
        if start>=duration-.25:return
        length=min(gate_beats*beat,max(.025,duration-start-.1))
        notes.append({'track':track,'instrument':TRACKS[track]['instrument'],
                      'bar_index':bar,'global_beat':round((start-GRID_ORIGIN)/beat,9),
                      'start':round(start,9),'duration':round(length,9),
                      'midi_note':pitch,'velocity':velocity,
                      'additional_attack_seconds':.110 if track=='accords' else .060})
    for bar in range(math.ceil(duration/(4.*beat))):
        onset=0. if bar==0 else GRID_ORIGIN+bar*4.*beat
        if onset>=duration-.7:break
        final=onset+4.*beat>=duration-.7
        chord=(57,61,66) if final else voicings[bar%len(voicings)]
        root=45 if final else roots[bar%len(roots)]
        # Soft two-beat comping prevents the long natural piano decay from
        # becoming a repeated near-silence. This is fixed composition, not a
        # detector, scene-dependent gate or gain applied after the mix.
        for pulse in (0,1):
            when=onset if pulse==0 else GRID_ORIGIN+(bar*4.+2.)*beat
            for j,pitch in enumerate(chord):
                add('accords',bar,when+j*.17,pitch,3.3 if bar==0 and pulse==0 else 2.85,25+(bar+j+pulse)%3)
        add('basse',bar,onset,root,3.95 if bar==0 else 1.92,31+bar%3)
        if bar>0:add('basse',bar,onset+2.*beat,root+7,1.92,30+bar%3)
    return sorted(notes,key=lambda e:(e['start'],e['track'],e['midi_note']))


def gain_envelope(length,specification):
    n=round(float(length)*SR);times=np.arange(n)/SR;gain=np.ones(n)
    depth=10.**(float(specification.get('duck_db',-1.5))/20.)
    attack=float(specification.get('duck_attack_seconds',.6));release=float(specification.get('duck_release_seconds',.8))
    for start,end in specification['duck_intervals']:
        entry=np.clip((times-(start-attack))/attack,0.,1.)
        leave=np.clip((end+release-times)/release,0.,1.)
        entry=entry*entry*(3.-2.*entry);leave=leave*leave*(3.-2.*leave)
        gain*=1.-(1.-depth)*entry*leave
    return gain

def _render_track(lib,track,notes,start,end):
    spec=TRACKS[track];settings=lib.new_fluid_settings();assert settings
    lib.fluid_settings_setnum(settings,b'synth.sample-rate',float(SR))
    lib.fluid_settings_setnum(settings,b'synth.gain',.40)
    lib.fluid_settings_setint(settings,b'synth.reverb.active',1)
    lib.fluid_settings_setint(settings,b'synth.chorus.active',0)
    lib.fluid_settings_setnum(settings,b'synth.reverb.room-size',.20)
    lib.fluid_settings_setnum(settings,b'synth.reverb.damp',.55)
    lib.fluid_settings_setnum(settings,b'synth.reverb.width',.65)
    lib.fluid_settings_setnum(settings,b'synth.reverb.level',.10)
    lib.fluid_settings_setint(settings,b'synth.polyphony',64)
    lib.fluid_settings_setint(settings,b'synth.cpu-cores',1)
    synth=lib.new_fluid_synth(settings);assert synth
    try:
        sfid=lib.fluid_synth_sfload(synth,str(SOUNDFONT).encode(),0);assert sfid>=0
        assert lib.fluid_synth_program_select(synth,spec['channel'],sfid,spec['bank'],spec['program'])==0
        lib.fluid_synth_cc(synth,spec['channel'],10,spec['pan'])
        lib.fluid_synth_cc(synth,spec['channel'],91,34)
        lib.fluid_synth_cc(synth,spec['channel'],93,0)
        count=round((end-start)*SR);left=np.zeros(count,np.float32);right=np.zeros(count,np.float32)
        events=[]
        for e in notes:
            events.append((max(0,round((e['start']-start)*SR)),1,e))
            events.append((min(count,round((e['start']+e['duration']-start)*SR)),0,e))
        events.sort(key=lambda v:(v[0],v[1]));position=0
        def until(target):
            nonlocal position
            target=min(count,max(position,target))
            if target>position:
                lib.fluid_synth_write_float(synth,target-position,left.ctypes.data,position,1,right.ctypes.data,position,1)
                position=target
        for offset,on,e in events:
            until(offset)
            if on:lib.fluid_synth_noteon(synth,spec['channel'],e['midi_note'],e['velocity'])
            else:lib.fluid_synth_noteoff(synth,spec['channel'],e['midi_note'])
        until(count)
        return np.column_stack((left,right)).astype(np.float64)*spec['gain']
    finally:
        lib.delete_fluid_synth(synth);lib.delete_fluid_settings(settings)

def render_background(length,specification,seed=None):
    del seed
    assert SOUNDFONT.is_file() and hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest()==SF2_SHA
    score=compose({'duration':length,'bpm':BPM});lib=_api();n=round(length*SR)
    tracks={name:np.zeros((n,2),dtype=np.float64) for name in TRACKS}
    for note in score:
        local=dict(note,start=0.)
        span=min(note['duration']+(.65 if note['track']=='accords' else .40),length-note['start'])
        clip=_render_track(lib,note['track'],[local],0.,span)
        clip*=_envelope(len(clip),note['additional_attack_seconds'],.15)[:,None]
        start=round(note['start']*SR);count=min(len(clip),n-start)
        tracks[note['track']][start:start+count]+=clip[:count]
    a=round(2.*SR);b=round((length-.7)*SR)
    balance={}
    for name,signal in tracks.items():
        rms=float(np.sqrt(np.mean(signal[a:b]**2)))
        relative=1. if name=='accords' else 10.**(-8./20.)
        factor=relative/max(rms,1e-12);tracks[name]*=factor;balance[name]=factor
    raw=sum(tracks.values());rms=float(np.sqrt(np.mean(raw[a:b]**2)))
    calibration=10.**(TARGET_BODY_RMS_DBFS/20.)/max(rms,1e-12)
    for name in tracks:tracks[name]*=calibration
    reference=sum(tracks.values());gain=gain_envelope(length,specification)
    ending=np.ones(n);tail=round(.6*SR);ending[-tail:]*=np.cos(np.linspace(0,np.pi/2,tail))**2
    treated={name:values*gain[:,None]*ending[:,None] for name,values in tracks.items()}
    signal=sum(treated.values())
    parameters={'original_score':True,'style':'soft medium-register piano and double-bass jazz bed',
                'bpm':BPM,'meter_beats':4,'global_clock_origin_seconds':GRID_ORIGIN,
                'tonal_center':'A major, sixth/ninth and minor-seventh colours',
                'notes':score,'instruments':TRACKS,'continuous_global_clock':True,
                'visual_cut_restarts':0,'frame_or_action_dependent_notes':False,
                'score_inputs':['duration','bpm'],'melody_line':False,'drums_or_brushes':False,
                'composition_character':'soft rolled three-note piano harmony every two beats; restrained two-feel bass, no walking line',
                'opening':'A6/9 colour under original A5/C#6/B5 whistle; no new whistle',
                'note_attack_seconds':{'accords':.110,'basse':.060},
                'velocity_range':[min(e['velocity'] for e in score),max(e['velocity'] for e in score)],
                'per_track_constant_balance':balance,'bass_rms_relative_to_piano_db':-8.,
                'one_global_music_calibration':calibration,'target_unducked_music_body_rms_dbfs':TARGET_BODY_RMS_DBFS,
                'body_measurement_seconds':[2.,length-.7],
                'actual_unducked_body_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(reference[a:b]**2)))),
                'duck_db':float(specification['duck_db']),'duck_intervals':specification['duck_intervals'],
                'duck_attack_seconds':float(specification['duck_attack_seconds']),
                'duck_release_seconds':float(specification['duck_release_seconds']),
                'duck_gain_min':float(gain.min()),'duck_gain_max':float(gain.max()),
                'ending_fade_seconds':[length-.6,length],
                'regular_chord_gate_beats':2.85,'opening_chord_gate_beats':3.3,'piano_legato_overlap_seconds':.4722222222,'comping_interval_beats':2.,'piano_chord_voice_stagger_seconds':.17,'fixed_music_bus_compression':False,'dynamic_normalization':False,
                'fluidsynth_version':lib.fluid_version_str().decode(),
                'soundfont':{'file':'assets/'+SOUNDFONT.name,'sha256':SF2_SHA,'license':'MIT FluidR3 subset, bundled notice'},
                'limits':'Composed/sample-rendered proposal with softened attacks and lower measured level. No listening or perceptual softness claim.'}
    return signal,parameters,treated,reference


def write_midi(path,score,bpm=BPM):
    def vlq(v):
        v=max(0,int(v));out=[v&127];v>>=7
        while v:out.insert(0,(v&127)|128);v>>=7
        return bytes(out)
    beat=60./bpm;tracks=[]
    tempo=round(60000000/bpm)
    meta=b'\x00\xff\x51\x03'+tempo.to_bytes(3,'big')+b'\x00\xff\x58\x04\x04\x02\x18\x08'+b'\x00\xff\x2f\x00'
    tracks.append(meta)
    for name,spec in TRACKS.items():
        channel=spec['channel'];events=[]
        for e in score:
            if e['track']!=name:continue
            a=round(e['start']/beat*480);b=round((e['start']+e['duration'])/beat*480)
            events.append((a,1,bytes((0x90+channel,e['midi_note'],e['velocity']))))
            events.append((b,0,bytes((0x80+channel,e['midi_note'],0))))
        events.sort(key=lambda e:(e[0],e[1]));label=name.encode()
        data=b'\x00\xff\x03'+vlq(len(label))+label
        data+=b'\x00'+bytes((0xb0+channel,0,spec['bank']&127))+b'\x00'+bytes((0xc0+channel,spec['program']))
        last=0
        for tick,on,message in events:data+=vlq(tick-last)+message;last=tick
        data+=b'\x00\xff\x2f\x00';tracks.append(data)
    output=b'MThd'+struct.pack('>IHHH',6,1,len(tracks),480)
    for data in tracks:output+=b'MTrk'+struct.pack('>I',len(data))+data
    Path(path).write_bytes(output)
