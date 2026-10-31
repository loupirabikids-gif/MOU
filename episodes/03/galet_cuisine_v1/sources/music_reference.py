"""Original restrained nylon-guitar bossa for MOU's unchanged V26 pictures.

One global syncopated score evolves through quiet variants, mild tuning/rubato
and a gradual tempo change. It stops exactly at32s; one short falling guitar
note at36.25s precedes the final held pose. No claim of listening is made.
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
SOUNDFONT=Path(__file__).resolve().parents[1]/'assets/FluidR3_MOU_bossa.sf2'
SF2_SHA='fa64be8254db1fbe0ffde1121beb14aae96d4fe0f7f485a82ebee1768276936f'
TARGET_BODY_RMS_DBFS=-41.5
CUT_SECONDS=32.
STING_START=36.25
STING_END=36.75
TRACKS={
    'guitare':{'program':24,'bank':0,'channel':2,'gain':1.,'pan':61,
               'instrument':'FluidR3 Nylon String Guitar; syncopated finger chords and thumb'},
    'basse':{'program':32,'bank':0,'channel':1,'gain':.6,'pan':65,
             'instrument':'FluidR3 Acoustic Bass; restrained root/fifth bossa support'},
}


def _smooth(value):
    value=max(0.,min(1.,float(value)))
    return value*value*(3.-2.*value)


def tempo_at(t):
    return 108.+4.*max(0.,min(1.,(float(t)-20.75)/10.9))


def beat_at(t):
    t=float(t)
    if t<=20.75:return t*1.8
    dt=min(t,31.65)-20.75
    beats=20.75*1.8+1.8*dt+(4./10.9)*dt*dt/120.
    if t>31.65:beats+=(t-31.65)*(112./60.)
    return beats


def time_at_beat(value):
    lo,hi=0.,40.
    for _ in range(48):
        mid=(lo+hi)/2.
        if beat_at(mid)<value:lo=mid
        else:hi=mid
    return (lo+hi)/2.


def _api():
    lib=ctypes.CDLL(ctypes.util.find_library('fluidsynth') or 'libfluidsynth.so.3')
    signatures={
      'new_fluid_settings':(ctypes.c_void_p,[]),'delete_fluid_settings':(None,[ctypes.c_void_p]),
      'fluid_settings_setnum':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_double]),
      'fluid_settings_setint':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int]),
      'new_fluid_synth':(ctypes.c_void_p,[ctypes.c_void_p]),'delete_fluid_synth':(None,[ctypes.c_void_p]),
      'fluid_synth_sfload':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int]),
      'fluid_synth_program_select':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
      'fluid_synth_cc':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
      'fluid_synth_pitch_bend':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),
      'fluid_synth_noteon':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int]),
      'fluid_synth_noteoff':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),
      'fluid_synth_write_float':(ctypes.c_int,[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int]),
      'fluid_version_str':(ctypes.c_char_p,[]),
    }
    for name,(result,args) in signatures.items():
        fn=getattr(lib,name);fn.restype=result;fn.argtypes=args
    return lib


def _envelope(n,attack=.016,release=.035):
    result=np.ones(n,dtype=np.float64)
    a=min(n,max(2,round(attack*SR)));b=min(n,max(2,round(release*SR)))
    result[:a]*=np.sin(np.linspace(0,math.pi/2,a))**2
    result[-b:]*=np.cos(np.linspace(0,math.pi/2,b))**2
    return result


def compose(specification):
    duration=float(specification['duration']);assert duration==38.
    # Original A-major harmony, compatible with the original opening whistle.
    changes=[('A6/9',45,(57,59,61,66)),('Amaj9',45,(56,59,61,64)),
       ('F#m7',42,(57,61,64,68)),('Bm9',47,(57,61,62,66)),
       ('E13',40,(56,61,62,66)),('A6',45,(57,61,64,66)),
       ('C#m7',37,(56,59,61,64)),('F#m9',42,(57,61,64,68)),
       ('Bm9',47,(57,61,62,66)),('E13',40,(56,61,62,66)),
       ('Amaj9',45,(56,59,61,64)),('F#9',42,(58,61,64,68)),
       ('Bm7',47,(57,62,66,69)),('E9sus',40,(57,59,62,66)),
       ('A6/9',45,(57,59,61,66)),('A6',45,(57,61,64,66))]
    # Two-bar straight-eighth bossa comping; bass/nylon thumb anchor beats1/3.
    patterns=((0.,1.5,2.5),(.5,1.5,3.),(0.,1.5,2.5,3.5),(.5,1.5,3.))
    notes=[]
    def add(track,bar,beat,pitch,gate_beats,velocity,channel,role,cents=0.,delay=0.):
        start=max(0.,time_at_beat(beat)+delay)
        if start>=31.82:return
        duration_note=min(time_at_beat(beat+gate_beats)-time_at_beat(beat),31.96-start)
        if duration_note<=.025:return
        notes.append({'track':track,'instrument':TRACKS[track]['instrument'],
            'bar_index':bar,'global_beat':round(beat,9),'start':round(start,9),
            'duration':round(duration_note,9),'midi_note':int(pitch),'velocity':int(velocity),
            'channel':channel,'role':role,'harmony':changes[bar%len(changes)][0],
            'tempo_bpm_at_start':tempo_at(start),'detune_cents':round(cents,6),
            'additional_attack_seconds':.016 if track=='guitare' else .040,
            'release_tail_seconds':.20 if track=='guitare' else .25})
    for bar in range(16):
        harmony,root,chord=changes[bar%len(changes)]
        if time_at_beat(bar*4.)>=31.82:break
        onset=time_at_beat(bar*4.)
        late=_smooth((onset-20.75)/9.)
        drift=2.5*_smooth((onset-8.)/12.)+7.5*late
        for pulse,offset in enumerate(patterns[bar%len(patterns)]):
            nominal=bar*4.+offset;clock=time_at_beat(nominal)
            # Deliberate tiny hesitation at the existing23s turn, not a new loop.
            hesitation=.048 if bar==10 and pulse==1 else 0.
            micro=(.004+.010*late)*math.sin(bar*1.71+pulse*2.13)
            tuning=drift*math.sin(bar*.79+pulse*.67)
            ordered=chord if (bar+pulse)%2==0 else tuple(reversed(chord))
            strum=.010+.003*late
            for j,pitch in enumerate(ordered):
                add('guitare',bar,nominal,pitch,.64 if pulse==0 else .52,
                    34+(j+bar+pulse)%5,j+2,'syncopated_finger_chord',tuning,
                    delay=hesitation+micro+j*strum)
        for offset,pitch in ((0.,root),(2.,root+7)):
            add('basse',bar,bar*4.+offset,pitch,1.85,34+bar%3,1,'root_or_fifth',
                cents=.6*late*math.sin(bar))
            # A quiet nylon thumb is part of guitar playing, not an extra track.
            add('guitare',bar,bar*4.+offset,root+12 if offset==0 else root+19,
                .75,26+(bar%3),0,'nylon_thumb',cents=drift*.25)
    # One written phrase pickup fills the isolated19.5--20s decay, without
    # removing the other bossa rests or applying any time-varying gain.
    for note in notes:
        if note['track']=='basse' and abs(note['global_beat']-34.)<1.e-8:
            note['duration']=round(time_at_beat(34.94)-note['start'],9)
            note['release_tail_seconds']=.15
    add('basse',8,35.,42,1.,29,1,'single_phrase_pickup_Fsharp2_to_E2',cents=0.)
    notes.append({'track':'guitare','instrument':TRACKS['guitare']['instrument'],
        'bar_index':None,'global_beat':beat_at(STING_START),'start':STING_START,
        'duration':.29,'midi_note':64,'velocity':31,'channel':6,
        'role':'single_falling_closing_note','harmony':'E over remembered A6',
        'tempo_bpm_at_start':tempo_at(STING_START),'detune_cents':6.,
        'pitch_curve_cents':[[0.,6.],[.12,0.],[.29,-18.]],
        'additional_attack_seconds':.024,'release_tail_seconds':.21})
    return sorted(notes,key=lambda e:(e['start'],e['track'],e['midi_note']))


def gain_envelope(length,specification):
    n=round(length*SR);times=np.arange(n)/SR;gain=np.ones(n)
    depth=10.**(float(specification.get('duck_db',-.6))/20.)
    attack=float(specification.get('duck_attack_seconds',.6));release=float(specification.get('duck_release_seconds',.8))
    for start,end in specification.get('duck_intervals',[]):
        a=np.clip((times-(start-attack))/attack,0.,1.);b=np.clip((end+release-times)/release,0.,1.)
        gain*=1.-(1.-depth)*(a*a*(3.-2.*a))*(b*b*(3.-2.*b))
    return gain


def _render_note(lib,note):
    spec=TRACKS[note['track']];channel=note['channel']
    settings=lib.new_fluid_settings();assert settings
    lib.fluid_settings_setnum(settings,b'synth.sample-rate',float(SR))
    lib.fluid_settings_setnum(settings,b'synth.gain',.4)
    lib.fluid_settings_setint(settings,b'synth.reverb.active',1)
    lib.fluid_settings_setint(settings,b'synth.chorus.active',0)
    lib.fluid_settings_setnum(settings,b'synth.reverb.room-size',.18)
    lib.fluid_settings_setnum(settings,b'synth.reverb.damp',.65)
    lib.fluid_settings_setnum(settings,b'synth.reverb.width',.60)
    lib.fluid_settings_setnum(settings,b'synth.reverb.level',.08)
    lib.fluid_settings_setint(settings,b'synth.polyphony',32)
    lib.fluid_settings_setint(settings,b'synth.cpu-cores',1)
    synth=lib.new_fluid_synth(settings);assert synth
    try:
        sfid=lib.fluid_synth_sfload(synth,str(SOUNDFONT).encode(),0);assert sfid>=0
        assert lib.fluid_synth_program_select(synth,channel,sfid,spec['bank'],spec['program'])==0
        lib.fluid_synth_cc(synth,channel,10,spec['pan']);lib.fluid_synth_cc(synth,channel,91,26)
        # Default pitch sensitivity is explicitly fixed to two semitones.
        for cc,value in ((101,0),(100,0),(6,2),(38,0),(101,127),(100,127)):
            lib.fluid_synth_cc(synth,channel,cc,value)
        span=note['duration']+note['release_tail_seconds'];n=round(span*SR)
        left=np.zeros(n,np.float32);right=np.zeros(n,np.float32);position=0
        def until(target):
            nonlocal position
            target=min(n,max(position,target))
            if target>position:
                lib.fluid_synth_write_float(synth,target-position,left.ctypes.data,position,1,right.ctypes.data,position,1)
                position=target
        def bend(cents):
            lib.fluid_synth_pitch_bend(synth,channel,max(0,min(16383,round(8192+cents*8192/200.))))
        bend(note['detune_cents']);lib.fluid_synth_noteon(synth,channel,note['midi_note'],note['velocity'])
        events=[(note['duration'],'off',0)]
        curve=note.get('pitch_curve_cents')
        if curve:
            for t in np.arange(.01,note['duration']+.0001,.01):
                cents=float(np.interp(t,[p[0] for p in curve],[p[1] for p in curve]));events.append((float(t),'bend',cents))
        for t,kind,value in sorted(events):
            until(round(t*SR))
            if kind=='bend':bend(value)
            else:lib.fluid_synth_noteoff(synth,channel,note['midi_note'])
        until(n)
        clip=np.column_stack((left,right)).astype(np.float64)*spec['gain']
        return clip*_envelope(n,note['additional_attack_seconds'],.05)[:,None]
    finally:
        lib.delete_fluid_synth(synth);lib.delete_fluid_settings(settings)


def render_background(length,specification,seed=None):
    del seed
    assert float(length)==38.
    assert SOUNDFONT.is_file() and hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest()==SF2_SHA
    score=compose({'duration':length});lib=_api();n=round(length*SR)
    tracks={name:np.zeros((n,2),dtype=np.float64) for name in TRACKS}
    for note in score:
        clip=_render_note(lib,note);start=round(note['start']*SR);count=min(n-start,len(clip))
        tracks[note['track']][start:start+count]+=clip[:count]
    a,b=round(.5*SR),round(31.5*SR);balance={}
    for name,signal in tracks.items():
        rms=float(np.sqrt(np.mean(signal[a:b]**2)));relative=1. if name=='guitare' else 10.**(-9./20.)
        factor=relative/max(rms,1e-12);tracks[name]*=factor;balance[name]=factor
    raw=sum(tracks.values());rms=float(np.sqrt(np.mean(raw[a:b]**2)))
    calibration=10.**(TARGET_BODY_RMS_DBFS/20.)/max(rms,1e-12)
    for name in tracks:tracks[name]*=calibration
    cut=round(CUT_SECONDS*SR);fade=round(.006*SR)
    for name,signal in tracks.items():
        signal[cut-fade:cut]*=np.cos(np.linspace(0,math.pi/2,fade))[:,None]**2
        signal[cut:round(STING_START*SR)]=0.
        signal[round(STING_END*SR):]=0.
        # The closing note is the only musical content after the hard cut.
        if name=='basse':signal[cut:]=0.
    reference=sum(tracks.values()).copy();gain=gain_envelope(length,specification)
    treated={name:signal*gain[:,None] for name,signal in tracks.items()}
    intro=np.sin(np.linspace(0,math.pi/2,round(.012*SR)))**2
    for value in treated.values():value[:len(intro)]*=intro[:,None]
    signal=sum(treated.values())
    assert np.count_nonzero(signal[cut:round(STING_START*SR)])==0
    assert np.count_nonzero(signal[round(STING_END*SR):])==0
    parameters={'original_score':True,'style':'restrained original nylon-guitar bossa nova',
        'bpm':BPM,'meter_beats':4,'global_clock_origin_seconds':0.,
        'tonal_center':'A major; original sixth/ninth, minor seventh and dominant voicings',
        'notes':score,'instruments':TRACKS,'continuous_global_clock':True,'visual_cut_restarts':0,
        'tempo_map':[{'seconds':round(t,3),'bpm':tempo_at(t)} for t in np.arange(0,32.0001,.5)],
        'tempo_change_start_seconds':20.75,'tempo_change_end_seconds':31.65,'tempo_range_bpm':[108.,112.],
        'guitar_syncopation_patterns_beats':[list(p) for p in ((0.,1.5,2.5),(.5,1.5,3.),(0.,1.5,2.5,3.5),(.5,1.5,3.))],
        'hesitated_chord_delay_seconds':.048,'hesitated_chord_bar_index':10,
        'single_composed_pickup':{'global_beat':35.,'start':time_at_beat(35.),'note':42,'instrument':'basse','purpose':'Connect the single19.5--20s decay into the E13 phrase, without filling every bossa rest'},
        'guitar_detune_cents_range':[min(e['detune_cents'] for e in score if e['track']=='guitare' and e['role']!='single_falling_closing_note'),max(e['detune_cents'] for e in score if e['track']=='guitare' and e['role']!='single_falling_closing_note')],
        'closing_note':{'start':STING_START,'end':STING_END,'pitch_curve_cents':[[0.,6.],[.12,0.],[.29,-18.]]},
        'hard_music_cut_seconds':CUT_SECONDS,'cut_edge_fade_seconds':.006,
        'music_zero_intervals_seconds':[[32.,STING_START],[STING_END,38.]],
        'drums_or_brushes':False,'new_voice':False,'per_track_constant_balance':balance,
        'bass_rms_relative_to_guitar_db':-9.,'one_global_music_calibration':calibration,
        'target_unducked_music_body_rms_dbfs':TARGET_BODY_RMS_DBFS,
        'body_measurement_seconds':[.5,31.5],
        'actual_unducked_body_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(reference[a:b]**2)))),
        'duck_db':float(specification.get('duck_db',-.6)),
        'duck_intervals':specification.get('duck_intervals',[]),
        'duck_attack_seconds':float(specification.get('duck_attack_seconds',.6)),
        'duck_release_seconds':float(specification.get('duck_release_seconds',.8)),
        'duck_gain_min':float(gain.min()),'duck_gain_max':float(gain.max()),
        'velocity_range':[min(e['velocity'] for e in score),max(e['velocity'] for e in score)],
        'fluidsynth_version':lib.fluid_version_str().decode(),
        'soundfont':{'file':'assets/'+SOUNDFONT.name,'sha256':SF2_SHA,'license':'MIT; bundled FluidR3 notice'},
        'dynamic_normalization':False,'composition_character':'straight-eighth syncopated finger chords, alternating nylon thumb and root/fifth acoustic bass; quiet progressive microtiming/tuning variation',
        'limits':'No listening available. Score, soundfont identity, actual sample waveforms and numerical level/cut checks do not prove perceived comfort or humour.'}
    return signal,parameters,treated,reference


def write_midi(path,score,bpm=BPM):
    """Write the evolving score, per-string bends and tempo map to MIDI type1."""
    del bpm
    def vlq(value):
        value=max(0,int(value));result=[value&127];value>>=7
        while value:result.insert(0,(value&127)|128);value>>=7
        return bytes(result)
    tracks=[];events=[]
    # Dense tempo metadata approximates the analytic clock; PCM is authoritative.
    for t in np.arange(0,38.0001,.1):
        tempo=round(60000000/tempo_at(t));tick=round(beat_at(t)*480)
        events.append((tick,b'\xff\x51\x03'+tempo.to_bytes(3,'big')))
    data=b'\x00\xff\x58\x04\x04\x02\x18\x08';last=0
    for tick,message in events:data+=vlq(tick-last)+message;last=tick
    tracks.append(data+b'\x00\xff\x2f\x00')
    for name,spec in TRACKS.items():
        events=[];channels=sorted({e['channel'] for e in score if e['track']==name})
        label=name.encode();data=b'\x00\xff\x03'+vlq(len(label))+label
        for channel in channels:
            data+=b'\x00'+bytes((0xb0+channel,0,spec['bank']))+b'\x00'+bytes((0xc0+channel,spec['program']))
            for cc,value in ((101,0),(100,0),(6,2),(38,0),(101,127),(100,127)):
                data+=b'\x00'+bytes((0xb0+channel,cc,value))
        for e in score:
            if e['track']!=name:continue
            channel=e['channel'];a=round(beat_at(e['start'])*480);b=round(beat_at(e['start']+e['duration'])*480)
            bend=max(0,min(16383,round(8192+e['detune_cents']*8192/200.)))
            events.append((a,0,bytes((0xe0+channel,bend&127,(bend>>7)&127))))
            events.append((a,2,bytes((0x90+channel,e['midi_note'],e['velocity']))))
            events.append((b,1,bytes((0x80+channel,e['midi_note'],0))))
            if e.get('pitch_curve_cents'):
                curve=e['pitch_curve_cents']
                for dt in np.arange(.01,e['duration']+.0001,.01):
                    cents=float(np.interp(dt,[p[0] for p in curve],[p[1] for p in curve]))
                    bend=max(0,min(16383,round(8192+cents*8192/200.)))
                    events.append((round(beat_at(e['start']+dt)*480),0,bytes((0xe0+channel,bend&127,(bend>>7)&127))))
        last=0
        for tick,order,message in sorted(events,key=lambda x:(x[0],x[1])):
            data+=vlq(tick-last)+message;last=tick
        tracks.append(data+b'\x00\xff\x2f\x00')
    output=b'MThd'+struct.pack('>IHHH',6,1,len(tracks),480)
    for data in tracks:output+=b'MTrk'+struct.pack('>I',len(data))+data
    Path(path).write_bytes(output)
