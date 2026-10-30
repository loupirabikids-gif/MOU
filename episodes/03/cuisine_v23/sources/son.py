"""MOU V23: a new acoustic-jazz trio with the restrained V22 Foley bank.

Reference WAVs stay read-only. Processed WAVs have their new family mix levels;
never apply the historical master again. A single whole-film delivery gain
sets comparable integrated loudness. Measurements are not listening approval.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import wave
import numpy as np

EP=Path(__file__).resolve().parents[1]
OUT=EP/'audio'
TIMELINE=EP/'chronologie.json'
SR=48000
MASTER_REFERENCE=2.124210976406158
DELIVERY_LUFS=-25.
MUSIC_SOURCE_SHA='52cfda878f65995d894af2a3e83749eed10573a747524d3e2ee54b695cbf2141'
FLOOR_SOURCE_SHA='de06fe4cc6d3b30b8a8c5bf771d3845e5546aa55b7ac5879d635b6b62d19fe5e'
REMOVED_KINDS={'hand_water','paper_wipe','tiny_paper_wipe','paper_crumple',
               'tiny_paper_crumple','paper_flight','tiny_paper_flight','stir','salt_pinch'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def db(value):return float(20.*np.log10(max(float(value),1e-12)))


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def pcm(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,signal):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    assert signal.ndim==2 and signal.shape[1]==2
    data=np.asarray(signal,dtype=np.int32);assert np.abs(data).max()<32767
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent);os.close(fd)
    try:
        with wave.open(temp,'wb') as f:
            f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(data.astype('<i2').tobytes())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def write_float(path,signal):
    assert np.isfinite(signal).all() and float(np.abs(signal).max())<.99
    write_pcm(path,np.rint(signal*32767.).astype(np.int32))


def fade(n,attack=.008,release=.035):
    env=np.ones(n)
    a=min(n,max(2,round(attack*SR)));b=min(n,max(2,round(release*SR)))
    env[:a]*=np.sin(np.linspace(0.,np.pi/2.,a))**2
    env[-b:]*=np.cos(np.linspace(0.,np.pi/2.,b))**2
    return env


def soft_filter(signal,cutoff,attack,release):
    n=len(signal);freq=np.fft.rfftfreq(n,1./SR)
    response=(1.-np.exp(-(freq/90.)**4))/np.sqrt(1.+(freq/float(cutoff))**8)
    return np.fft.irfft(np.fft.rfft(signal)*response,n)*fade(n,attack,release)


def peak_level(signal,peak_dbfs):
    return signal*10.**(peak_dbfs/20.)/max(float(np.abs(signal).max()),1e-12)


def stereo(mono,pan=0.):
    angle=(pan+1.)*np.pi/4.
    return mono[:,None]*np.array([math.cos(angle),math.sin(angle)])[None,:]*math.sqrt(2.)


def metric(signal):
    data=np.asarray(signal,dtype=float)
    if np.issubdtype(np.asarray(signal).dtype,np.integer):data=data/32768.
    mono=data.mean(axis=1);spec=np.abs(np.fft.rfft(mono*np.hanning(len(mono))))**2
    freq=np.fft.rfftfreq(len(mono),1./SR);energy=max(float(spec.sum()),1e-30)
    rms=float(np.sqrt(np.mean(data*data)));peak=float(np.abs(data).max())
    return {'rms_dbfs':db(rms),'peak_dbfs':db(peak),'crest_db':db(peak/max(rms,1e-12)),
            'energy_fraction_2_6khz':float(spec[(freq>=2000)&(freq<6000)].sum()/energy)}


def loudness(path):
    log=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),
        '-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode()
    values=json.loads(re.findall(r'\{[\s\S]*?\}',log)[-1])
    return {k:v for k,v in values.items() if k.startswith('input_')}


def processed_event(event):
    """One cue at its final level, without an extra master downstream."""
    source=OUT/event['file'];raw=pcm(source).astype(float)/32767.
    mono=raw.mean(axis=1);kind=event['kind']
    settings={
        'water':(2400.,.035,.055,-21.,-.08),
        'tap':(1800.,.002,.020,-26.,-.05),
        'paper_pull':(2600.,.025,.045,-24.,.05),
        'paper_tear':(2200.,.006,.025,-22.,.05),
        'tiny_paper_pull':(2400.,.015,.025,-30.,.05),
        'tiny_paper_tear':(2400.,.003,.015,-29.,.05),
        'paper_land':(1500.,.002,.025,-26.,-.05),
        'tiny_paper_land':(1700.,.002,.015,-31.,-.05),
        'carrot_chop':(2400.,.0025,.020,-21.5,.05),
        'knife_setdown':(2100.,.002,.025,-28.,.05),
        'tomato_contact':(1900.,.004,.025,-27.,.03),
        'wood_contact':(1800.,.003,.025,-28.,0.),
        'salt_sprinkle':(2600.,.012,.040,-32.,.03),
    }
    if kind=='whistle':
        result=soft_filter(mono,2600.,.005,.015)*MASTER_REFERENCE*10.**(-10./20.)
        settings_used={'lowpass_hz':2600.,'attack_seconds':.005,'release_seconds':.015,
                       'gain_db_relative_to_old_postmaster':-10.,'pan':0.}
        result=stereo(result)
    else:
        cutoff,attack,release,peak,pan=settings[kind]
        result=peak_level(stereo(soft_filter(mono,cutoff,attack,release),pan),peak)
        settings_used={'lowpass_hz':cutoff,'attack_seconds':attack,'release_seconds':release,
                       'target_postmix_peak_dbfs':peak,'pan':pan}
    path=OUT/'processed_v22'/event['file'];write_float(path,result)
    actual=metric(pcm(path))
    peak=np.abs(result).max()
    active=np.flatnonzero(np.abs(result).max(axis=1)>max(2./32768.,peak*.01))
    return {**event,'source_file':event['file'],'source_sha256':sha(source),
            'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),
            'stage':'post-mix PCM; add directly, no historical master',
            'render_stage':'post-mix PCM; no old master or source mix gain downstream',
            'source_mix_gain_db':event.get('mix_gain_db',0.),'mix_gain_db':0.,
            'source_peak_dbfs':event.get('peak_dbfs'),'peak_dbfs':actual['peak_dbfs'],
            'peak_dbfs_measured':actual['peak_dbfs'],'source_pan':event.get('pan'),
            'pan':settings_used['pan'],'source_parameters':event.get('parameters'),
            'parameters':settings_used,'processing':settings_used,'actual_metrics':actual,
            'first_above_one_percent_seconds':float(event['start'])+int(active[0])/SR,
            'start_sample':round(float(event['start'])*SR),'samples':len(result),
            'duration':len(result)/SR,'end_seconds':float(event['start'])+len(result)/SR}


def music_track(duration,timeline):
    path=Path(__file__).with_name('music.py');assert sha(path)==MUSIC_SOURCE_SHA
    spec=importlib.util.spec_from_file_location('mou_v23_jazz',path)
    music=importlib.util.module_from_spec(spec);spec.loader.exec_module(music)
    specification={'duration':duration,'bpm':music.BPM,'duck_intervals':[c['sink'] for c in timeline['cycles']],
                   'duck_db':-1.5,'duck_attack_seconds':.6,'duck_release_seconds':.8}
    signal,parameters,tracks,unducked=music.render_background(duration,specification)
    target=OUT/'musique_v23.wav';write_float(target,signal)
    stems=[]
    for name,values in tracks.items():
        dest=OUT/f'jazz_{name}_v23.wav';write_float(dest,values)
        stems.append({'track':name,'file':dest.name,'sha256':sha(dest),'actual_metrics':metric(pcm(dest))})
    reference=OUT/'jazz_sans_baisse_v23.wav';write_float(reference,unducked)
    parameters['stems']=stems
    parameters['unattenuated_file']=reference.name
    parameters['unattenuated_sha256']=sha(reference)
    parameters['music_source_sha256']=MUSIC_SOURCE_SHA
    music.write_midi(OUT/'partition_v23.mid',parameters['notes'])
    atomic_json(OUT/'partition_v23.json',parameters)
    n=round(duration*SR);win=round(.1*SR);hop=round(.02*SR)
    a=round(2.*SR);b=round((duration-.3)*SR)
    rms=[db(np.sqrt(np.mean(signal[i:i+win]**2))) for i in range(a,b-win,hop)]
    parameters['rolling_100ms_body_min_dbfs']=min(rms)
    parameters['rolling_100ms_body_p95_minus_p05_db']=float(np.percentile(rms,95)-np.percentile(rms,5))
    assert min(rms)>-58.,'Unexpected near-silence in the music body'
    event={'name':'musique_v23','kind':'background_music','file':target.name,'start':0.,
           'duration':duration,'start_sample':0,'samples':n,'end_seconds':duration,
           'stage':'post-mix PCM; single global music calibration, then one whole-film gain downstream',
           'sha256':sha(target),'actual_metrics':metric(pcm(target))}
    return event,parameters


def background_frying():
    source=OUT/'cuisson.wav';signal=pcm(source).astype(float)/32767.
    signal=signal[:round(40.25*SR)]*MASTER_REFERENCE*10.**(-4./20.)
    tail=round(.20*SR);signal[-tail:]*=np.cos(np.linspace(0,np.pi/2,tail))[:,None]**2
    path=OUT/'cuisson_v22.wav';write_float(path,signal)
    return {'name':'cuisson_v22','kind':'frying','file':path.name,'source_file':source.name,
            'source_sha256':sha(source),'sha256':sha(path),'start':0.,'duration':len(signal)/SR,
            'start_sample':0,'samples':len(signal),'end_seconds':len(signal)/SR,
            'gain_db_relative_to_old_postmaster':-4.,'tail_fade_seconds':.20,
            'stage':'post-mix PCM; no frying under ending reactions','actual_metrics':metric(pcm(path))}


def floor_contact(when):
    source=OUT/'c5_papier_sol.wav';assert sha(source)==FLOOR_SOURCE_SHA
    mono=pcm(source).astype(float).mean(axis=1)/32767.
    signal=peak_level(stereo(soft_filter(mono,1500.,.002,.025),-.04),-34.)
    path=OUT/'processed_v22/c5_papier_sol.wav';write_float(path,signal)
    return {'name':'c5_papier_sol','kind':'tiny_paper_floor','file':path.relative_to(OUT).as_posix(),
            'source_file':source.name,'source_sha256':sha(source),'sha256':sha(path),
            'start':when,'duration':len(signal)/SR,'start_sample':round(when*SR),
            'samples':len(signal),'end_seconds':when+len(signal)/SR,
            'stage':'post-mix PCM','processing':{'lowpass_hz':1500.,'peak_dbfs':-34.},
            'actual_metrics':metric(pcm(path))}


def cloth_contact(interval):
    a,b=map(float,interval);n=round((b-a)*SR);u=np.arange(n)/n
    rng=np.random.default_rng(3041809);noise=rng.standard_normal(n)
    freq=np.fft.rfftfreq(n,1./SR)
    shape=(1.-np.exp(-(freq/120.)**4))*np.exp(-(freq/2000.)**4)
    mono=np.fft.irfft(np.fft.rfft(noise)*shape,n)
    mono*=np.sin(np.pi*u)**1.6*fade(n,.04,.06)
    signal=peak_level(stereo(mono),-29.5)
    path=OUT/'tablier_v22.wav';write_float(path,signal)
    return {'name':'tablier_v22','kind':'cloth_wipe','file':path.name,'start':a,
            'duration':len(signal)/SR,'start_sample':round(a*SR),'samples':n,'end_seconds':b,
            'sha256':sha(path),'stage':'post-mix PCM, original local cotton-friction synthesis',
            'seed':3041809,'processing':{'band_hz':[120,2000],'attack_seconds':.04,
                                       'release_seconds':.06,'peak_dbfs':-29.5},
            'actual_metrics':metric(pcm(path))}


def main():
    timeline_bytes=TIMELINE.read_bytes();timeline=json.loads(timeline_bytes)
    duration=float(timeline['duration']);assert duration==48.25
    OUT.mkdir(exist_ok=True);(OUT/'processed_v22').mkdir(exist_ok=True)
    original=json.loads((OUT/'provenance_reference_v19.json').read_text())
    references={'c5_papier_sol.wav':FLOOR_SOURCE_SHA}
    events=[];removed=[]
    for event in original['events']:
        kind=event['kind'];reason=None
        if kind in ('frying','background_music'):continue
        if kind in REMOVED_KINDS:reason='Remove repetitive layer; visible action stays unchanged'
        elif kind=='paper_land' and event.get('cycle') in (2,3,4):reason='Reserve landing accents for first example and final consequence'
        if reason:
            removed.append({'name':event['name'],'kind':kind,'original_start':event['start'],'reason':reason});continue
        assert sha(OUT/event['file'])==event['sha256'],'Active raw Foley changed'
        references[event['file']]=event['sha256']
        events.append(processed_event(event))
    fry=next(e for e in original['events'] if e['kind']=='frying')
    references[fry['file']]=fry['sha256']
    assert all(sha(OUT/name)==h for name,h in references.items()),'Active raw bank changed'
    music,music_parameters=music_track(duration,timeline)
    events+=[background_frying(),music,floor_contact(float(timeline['overflow']['floor_land'])),
             cloth_contact(timeline['professional_ending']['cloth_contact'])]
    n=round(duration*SR);summed=np.zeros((n,2),dtype=np.int32)
    for event in events:
        data=pcm(OUT/event['file']).astype(np.int32);a=event['start_sample'];b=a+len(data)
        assert b<=n and len(data)==event['samples'];summed[a:b]+=data
    assert np.abs(summed).max()<32767,'Unexpected sum overload'
    before_gain=np.rint(summed*fade(n,.008,.035)[:,None]).astype(np.int32)
    measure_path=OUT/'.pregain_measure_v23.wav'
    write_pcm(measure_path,before_gain)
    before_loudness=loudness(measure_path)
    measure_path.unlink()
    delivery_gain_db=DELIVERY_LUFS-float(before_loudness['input_i'])
    delivery_gain=10.**(delivery_gain_db/20.)
    mix=np.rint(before_gain*delivery_gain).astype(np.int32)
    assert np.abs(mix).max()<32767,'Fixed delivery gain would clip'
    write_pcm(OUT/'mix.wav',mix)
    decoded=pcm(OUT/'mix.wav');assert np.array_equal(decoded,mix)
    assert not decoded[0].any() and not decoded[-1].any()
    test_start=round(40.25*SR);write_pcm(OUT/'test_fin_8s.wav',decoded[test_start:])
    # Music-only examples use the exact same delivery gain as the full mix.
    solo=np.rint(pcm(OUT/'musique_v23.wav').astype(np.float64)*delivery_gain).astype(np.int32)
    write_pcm(OUT/'jazz_seul_complet.wav',solo)
    write_pcm(OUT/'jazz_seul_15s.wav',solo[:15*SR])
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(OUT/'jazz_seul_15s.wav'),'-c:a','libmp3lame','-b:a','192k',str(OUT/'jazz_seul_15s.mp3')],check=True)
    assert len(pcm(OUT/'test_fin_8s.wav'))==8*SR
    foreground=np.zeros(n,dtype=np.uint8)
    for e in events:
        if e['kind'] in ('frying','background_music'):continue
        foreground[e['start_sample']:e['start_sample']+e['samples']]+=1
    a,b=map(lambda v:round(v*SR),timeline['professional_ending']['cloth_contact'])
    assert not foreground[test_start:a].any() and not foreground[b:].any()
    assert foreground[a:b].max()==1
    windows=[]
    for start in np.arange(2.,duration-.5,.25):
        seg=decoded[round(start*SR):round((start+.25)*SR)].astype(float)/32768.
        windows.append(db(np.sqrt(np.mean(seg*seg))))
    final_loudness=loudness(OUT/'mix.wav')
    assert abs(float(final_loudness['input_i'])-DELIVERY_LUFS)<.08
    music_parameters['jazz_only_excerpt']={'file':'jazz_seul_15s.wav','sha256':sha(OUT/'jazz_seul_15s.wav'),'start':0.,'duration':15.,'same_gain_as_film':True}
    source_hash=sha(__file__);timeline_hash=hashlib.sha256(timeline_bytes).hexdigest()
    audit={'episode':'03','revision':'V23 acoustic-jazz trio with restrained V22 Foley','duration_seconds':duration,
           'sample_rate':SR,'channels':2,'bit_depth':16,'samples_per_channel':n,
           'expected_video_frames':round(duration*timeline['fps']),'fps':timeline['fps'],
           'source_sha256':source_hash,'chronologie_sha256':timeline_hash,'mix_sha256':sha(OUT/'mix.wav'),
           'event_count':len(events),'removed_event_count':len(removed),'removed_events':removed,
           'reference_sources_unchanged':references,
           'processed_bank_stage':'New family mix levels, before the one fixed delivery gain; no historical master downstream',
           'master_gain_db':0.,'historical_master_reapplied':False,
           'global_normalization_mode':'one fixed whole-film gain, no per-scene or dynamic normalization',
           'delivery_target_lufs':DELIVERY_LUFS,'delivery_gain_db':delivery_gain_db,
           'delivery_gain_linear':delivery_gain,'before_delivery_gain_loudness':before_loudness,
           'pregain_metrics':metric(before_gain),'clipped_samples':0,
           'mix_metrics':metric(decoded),'input_loudness':final_loudness,
           'rolling_250ms_body_p95_minus_p05_db':float(np.percentile(windows,95)-np.percentile(windows,5)),
           'foreground_scheduled_occupancy_fraction':float(np.mean(foreground>0)),
           'foreground_2plus_layers_fraction':float(np.mean(foreground>=2)),
           'water_layers':1,'separate_hand_water_layer':False,
           'background_music':music_parameters,'cloth_contact_seconds':timeline['professional_ending']['cloth_contact'],
           'reaction_foreground_silence_before_and_after_cloth':True,
           'test_8s_file':'test_fin_8s.wav','test_8s_sha256':sha(OUT/'test_fin_8s.wav'),
           'limits':'Numerical recipe and spectral/loudness/source checks. No listening or perceptual comfort certification.'}
    provenance={'title':timeline['titre'],'duration_seconds':duration,'sample_rate':SR,'channels':2,
                'tools':['Python','NumPy','wave','FFmpeg','FluidSynth','MIT FluidR3 subset'],
                'source_sha256':source_hash,'chronologie_sha256':timeline_hash,'events':events,
                'removed_events':removed,'raw_source_provenance':'provenance_reference_v19.json',
                'bank_levels':'Only listed events participate. Sum their PCM at start_sample; apply endpoint envelope8/35ms and round, then apply the one delivery_gain_linear and round. Never sum historical WAVs or apply the old master again.',
                'delivery_gain_db':delivery_gain_db,'delivery_gain_linear':delivery_gain,
                'delivery_target_lufs':DELIVERY_LUFS,
                'score':'New original spaced A-major acoustic jazz trio at108BPM on0.30s beat origin, twenty-one bars plus coda; one global clock. MIT FluidR3 sample subset with bundled source/license provenance.',
                'background_music':music_parameters,'no_speech':True,'new_voice_or_jingles':False,
                'reproduction':'.venv/bin/python -B episodes/03/cuisine_v23/sources/son.py','limits':audit['limits']}
    assert TIMELINE.read_bytes()==timeline_bytes,'Timeline changed during sound rendering'
    atomic_json(OUT/'provenance.json',provenance)
    atomic_json(EP/'controle/audit_son.json',audit)
    atomic_json(EP/'controle/audit_audio_v23.json',audit)
    print(json.dumps({k:audit[k] for k in ('duration_seconds','event_count','removed_event_count','mix_sha256','mix_metrics','input_loudness','delivery_gain_db','rolling_250ms_body_p95_minus_p05_db')},indent=2))


if __name__=='__main__':main()
