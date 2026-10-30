"""Original acoustic jazz trio, one 108 BPM clock for the entire episode.

Twenty-one complete bars, a short coda and release; the score does not know scene boundaries.
The opening sustains A6/9 under the three existing A/C#/B whistle notes.
SoundFont: selected MIT FluidR3 piano, acoustic bass and brush-kit samples.
"""
from __future__ import annotations
import ctypes
import ctypes.util
import hashlib
import json
import math
from pathlib import Path
import struct
import numpy as np

SR=48000
BPM=108.
GRID_ORIGIN=.30
SOUNDFONT=Path(__file__).resolve().parents[1]/'assets/FluidR3_MOU_trio.sf2'
# Filled after verified subset creation; no unverified font is loaded.
SF2_SHA='c8c326b595c4cf49a5aa58c920ecb27b645deb025652938e7db8b6795eca5fe2'
TRACKS={
 'basse':{'program':32,'bank':0,'channel':0,'gain':.55,'pan':47,'instrument':'FluidR3 acoustic double bass'},
 'accords':{'program':0,'bank':0,'channel':1,'gain':1.80,'pan':60,'instrument':'FluidR3 Yamaha grand piano — left-hand comp'},
 'melodie':{'program':0,'bank':0,'channel':2,'gain':1.0,'pan':68,'instrument':'FluidR3 Yamaha grand piano — right-hand motif'},
 'balais':{'program':40,'bank':128,'channel':9,'gain':.65,'pan':77,'instrument':'FluidR3 brush kit'},
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
    """A-major spaced jazz form with sparse comp and a two-feel/walking bass."""
    duration=float(specification['duration']);bpm=float(specification.get('bpm',BPM))
    assert bpm==BPM,'The composed tempo preserves the existing108BPM cooking clock'
    beat=60./bpm;score=[];rng=np.random.default_rng(230803)
    voicings=[(59,61,64,66),(57,61,64),(57,62,66),(56,62,66),
              (56,61,64),(53,59,63),(57,61,64),(56,62,66),
              (56,61,64),(57,61,64),(57,62,66),(56,62,66),
              (57,62,66),(56,61,62,66),(56,61,64),(57,61,64,66)]
    roots=[45,42,47,40,45,37,42,40,45,42,47,40,47,40,45,45]
    voicings=voicings*2;roots=roots*2
    voicings[21]=(57,61,64,66);roots[21]=45
    patterns=[((0.,.82),(1.58,.76),(3.,.70)),
              ((.58,.95),(2.,1.10)),
              ((0.,1.15),(2.58,.92)),
              ((.58,.80),(2.,.78),(3.58,.30))]
    def add(track,g,pitch,beats,velocity,jitter=True,absolute_onset=None):
        if g<0:return
        offset=float(rng.uniform(-.008,.008)) if jitter and g>0 else 0.
        onset=max(0.,GRID_ORIGIN+g*beat+offset) if absolute_onset is None else float(absolute_onset)
        if onset>=duration-.04:return
        length=min(float(beats)*beat,duration-onset-.035)
        if length<.025:return
        velocity=max(8,min(90,round(velocity)))
        score.append({'track':track,'instrument':TRACKS[track]['instrument'],
          'bar_index':int(g//4),'global_beat':round(g,9),'start':round(onset,9),
          'duration':round(length,9),'midi_note':int(pitch),'velocity':int(velocity)})
    # One soft introductory chord/bass: existing whistle is rhythmically free
    # against a held harmony, without a competing slower drum pattern.
    for j,note in enumerate(voicings[0]):add('accords',j*.008,note,4.55,38-j,jitter=False,absolute_onset=j*.007)
    add('basse',0.,45,3.45,50,jitter=False,absolute_onset=0.)
    add('basse',3.,52,.90,43)
    add('balais',3.,51,.48,13)
    for bar in range(1,22):
        base=bar*4.;root=roots[bar];ending=bar==21
        dynamic=(.97,1.0,.94,1.03)[bar%4]
        if ending:
            for j,note in enumerate(voicings[bar]):add('accords',base+j*.01,note,3.70,40-j,jitter=False)
            add('basse',base,45,3.78,54,jitter=False)
            add('balais',base,51,.62,12)
            continue
        for attack,length in patterns[bar%4]:
            for j,note in enumerate(voicings[bar]):
                add('accords',base+attack+j*.012,note,length,
                    (42 if attack<1 else 38)*dynamic-j*2)
        if bar in (3,7,11,14,19,20):
            bass=(root,root+7,root+9,roots[bar+1]-1)
            for k,note in enumerate(bass):add('basse',base+k,note,.88,(55,50,52,48)[k]*dynamic)
        else:
            add('basse',base,root,1.95,55*dynamic)
            add('basse',base+2.,root+7,1.90,49*dynamic)
        # The groove belongs to musical bars, never to a visual cut or wash.
        for pos in (0.,1.,2.,3.):add('balais',base+pos,51,.70,16+(1 if pos in (0.,2.) else -1))
        for pos in (1.,3.):
            add('balais',base+pos,38,.55,23 if pos==3. else 21)
            add('balais',base+pos,44,.40,12)
        add('balais',base,36,.55,18)
        if bar%4==3:add('balais',base+3.58,38,.24,13)
    # Separated right-hand phrases, with genuine rests. No copied tune.
    phrases={
      2:[(.58,69,.45,48),(1.58,73,.58,45),(3.,71,.65,44)],
      3:[(.58,69,1.10,43)],
      5:[(1.,73,.50,46),(2.58,71,.45,42),(3.58,69,.32,40)],
      6:[(.58,66,.70,42),(2.,69,1.05,44)],
      8:[(.58,69,.50,47),(1.58,71,.50,45),(2.58,73,.60,43)],
      9:[(1.,76,.70,43),(2.58,73,.70,40)],
      11:[(.58,74,.60,44),(2.,73,.60,42),(3.,71,.55,40)],
      13:[(1.,71,.55,43),(2.58,69,.55,40)],
      14:[(.58,73,.70,42),(2.,69,1.25,40)],
      16:[(.58,69,.60,44),(2.,73,.75,42)],
      18:[(1.,74,.60,43),(2.58,73,.60,41)],
      20:[(.58,71,.60,42),(2.,69,1.30,40)],
    }
    for bar,phrase in phrases.items():
        for pos,pitch,length,velocity in phrase:add('melodie',bar*4.+pos,pitch,length,velocity)
    score.sort(key=lambda e:(e['start'],e['track'],e['midi_note']))
    # A previous noteoff must never cancel a newer gate at the same pitch.
    by_voice={}
    for e in score:
        key=(e['track'],e['midi_note']);previous=by_voice.get(key)
        if previous is not None:
            previous['duration']=round(min(previous['duration'],e['start']-previous['start']-.009),9)
            assert previous['duration']>.02
        by_voice[key]=e
    return score


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


def _brush_texture(lib,n,raw_body_rms):
    """A continuous brush circle made from the actual short brush recording.

    One fixed level relative to the music, independent of scenes. Windowed
    grains overlap to avoid one-shot gaps; no synthetic hiss is substituted.
    """
    note={'start':0.,'duration':.4,'midi_note':38,'velocity':72}
    source=_render_track(lib,'balais',[note],0.,.45)
    source=source-source.mean(axis=0)
    grain_n=round(.105*SR);hop=round(.035*SR)
    window=np.hanning(grain_n)[:,None];rng=np.random.default_rng(230871)
    result=np.zeros((n,2))
    for start in range(0,n,hop):
        source_start=int(rng.integers(round(.012*SR),round(.065*SR)))
        grain=source[source_start:source_start+grain_n]*window
        k=min(grain_n,n-start);result[start:start+k]+=grain[:k]
    times=np.arange(n)/SR
    # A circular brushing gesture has modest musical pulsation, never a mute.
    result*= (.94+.06*np.sin(2*np.pi*(BPM/60.)*times))[:,None]
    intro=np.clip((times-1.85)/.35,0.,1.);intro=intro*intro*(3.-2.*intro)
    result*=intro[:,None]*_envelope(n,.035,.22)[:,None]
    rms=float(np.sqrt(np.mean(result[3*SR:-SR]**2)))
    result*=raw_body_rms*10.**(-9./20.)/max(rms,1e-12)
    return result


def _music_bus_gain(signal):
    """Fixed gentle2:1 stereo-linked RMS compressor, independent of pictures."""
    n=len(signal);hop=round(.005*SR);window=round(.025*SR)
    power=np.mean(signal*signal,axis=1);prefix=np.r_[0.,np.cumsum(power)]
    offsets=np.arange(0,n,hop);smooth_db=[];previous=0.
    threshold=-36.;ratio=2.;knee=6.
    for at in offsets:
        a=max(0,int(at)-window);b=min(n,int(at)+hop)
        level=10.*math.log10(max((prefix[b]-prefix[a])/max(1,b-a),1e-20))
        over=level-threshold
        if over<=-knee/2.:reduction=0.
        elif over>=knee/2.:reduction=(1./ratio-1.)*over
        else:reduction=(1./ratio-1.)*(over+knee/2.)**2/(2.*knee)
        constant=.015 if reduction<previous else .24
        coeff=math.exp(-hop/(constant*SR))
        previous=coeff*previous+(1.-coeff)*reduction;smooth_db.append(previous)
    gain_db=np.interp(np.arange(n),offsets,np.asarray(smooth_db))
    return 10.**(gain_db/20.),{'ratio':ratio,'threshold_dbfs':threshold,'knee_db':knee,
        'detector':'stereo-linked RMS25ms','attack_seconds':.015,'release_seconds':.24,
        'control_step_seconds':.005,'gain_reduction_min_db':float(gain_db.min()),
        'scene_dependent':False,'dynamic_normalization':False}


def render_background(length,specification,seed=None):
    del seed
    assert SOUNDFONT.is_file() and hashlib.sha256(SOUNDFONT.read_bytes()).hexdigest()==SF2_SHA
    lib=_api();score=compose({'duration':float(length),'bpm':BPM})
    n=round(length*SR);tracks={}
    for track in TRACKS:
        notes=[e for e in score if e['track']==track]
        tracks[track]=_render_track(lib,track,notes,0.,length)*_envelope(n,.035,.22)[:,None]
    raw=sum(tracks.values());a=round(2.*SR);b=round((length-.4)*SR)
    rms=float(np.sqrt(np.mean(raw[a:b]**2)))
    tracks['balais']+=_brush_texture(lib,n,rms)
    raw=sum(tracks.values());rms=float(np.sqrt(np.mean(raw[a:b]**2)))
    calibration=10.**(-31.5/20.)/max(rms,1e-12)
    raw_tracks={name:signal*calibration for name,signal in tracks.items()}
    reference=sum(raw_tracks.values())
    bus_gain,bus_parameters=_music_bus_gain(reference)
    for name in raw_tracks:raw_tracks[name]*=bus_gain[:,None]
    compressed=sum(raw_tracks.values())
    makeup=10.**(-31.5/20.)/max(float(np.sqrt(np.mean(compressed[a:b]**2))),1e-12)
    for name in raw_tracks:raw_tracks[name]*=makeup
    bus_parameters['fixed_makeup_linear']=makeup
    reference=sum(raw_tracks.values());gain=gain_envelope(length,specification)
    treated={name:signal*gain[:,None] for name,signal in raw_tracks.items()}
    signal=sum(treated.values())
    parameters={
      'original_score':True,'style':'discreet acoustic jazz trio','bpm':BPM,'meter_beats':4,
      'complete_bars':21,'short_coda_start_seconds':GRID_ORIGIN+84.*60./BPM,'global_clock_origin_seconds':GRID_ORIGIN,'tonal_center':'A major: A6/9, F#m7, Bm7, E9/13, C#7 turnaround',
      'notes':score,'instruments':TRACKS,'continuous_global_clock':True,'visual_cut_restarts':0,
      'score_inputs':['duration','bpm'],'frame_or_action_dependent_notes':False,
      'swing_offbeat_ratio':.58,'humanized_onsets_max_seconds':.008,'humanization_seed':230803,
      'opening':'Sustained A6/9 and A bass; no regular percussion pattern until2.522s, under existing A5/C#6/B5 whistle',
      'composition_character':'two-feel bass with six walking turnaround bars; sparse alternating comp patterns; separated piano phrases',
      'one_global_music_calibration':calibration,'fixed_music_bus_compression':bus_parameters,'continuous_brush_texture':{'source':'FluidR3 brush38 atvelocity72, overlapped windowed grains','seed':230871,'relative_rms_db_to_unducked_music':-9.,'intro_fade_seconds':[1.85,2.20]},'target_unducked_music_body_rms_dbfs':-31.5,
      'duck_db':float(specification['duck_db']),'duck_intervals':specification['duck_intervals'],
      'duck_attack_seconds':float(specification['duck_attack_seconds']),'duck_release_seconds':float(specification['duck_release_seconds']),
      'duck_gain_min':float(gain.min()),'duck_gain_max':float(gain.max()),'same_pitch_gate_overlaps':0,
      'chorus':False,'light_room_reverb':{'room_size':.20,'damping':.55,'width':.65,'level':.10},
      'fluidsynth_version':lib.fluid_version_str().decode(),
      'soundfont':{'file':'assets/'+SOUNDFONT.name,'sha256':SF2_SHA,'license':'MIT, selected FluidR3 samples; see bundled notice/provenance'},
      'limits':'New composed/sample-rendered proposal. No audio listening or perceptual-comfort claim.'}
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
