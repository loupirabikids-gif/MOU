"""V24: V23 jazz lowered4dB, local paper Foley, unchanged fixed delivery gain.

Included PCM references stay read-only. No loudness target, recomposition,
network, voice generation or per-scene restart. Measures are not listening.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import wave
import numpy as np

EP=Path(__file__).resolve().parents[1];OUT=EP/'audio';TIMELINE=EP/'chronologie.json'
SR=48000;MUSIC_REDUCTION_DB=-4.;DELIVERY_GAIN_DB=3.5;MUSIC_FADE_SECONDS=.6
REFERENCE_MUSIC_SHA='31b1eb935a51e7a93b02812b9bde5d2e0809094dbc048010a9f4fa9dabf13e38'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w') as output:output.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert(source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,signal):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);data=np.asarray(signal,dtype=np.int32)
    assert data.ndim==2 and data.shape[1]==2 and np.abs(data).max()<32767
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent);os.close(fd)
    try:
        with wave.open(temp,'wb') as target:
            target.setnchannels(2);target.setsampwidth(2);target.setframerate(SR);target.writeframes(data.astype('<i2').tobytes())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def fade(n,attack=.008,release=.035):
    env=np.ones(n);a=min(n,max(2,round(attack*SR)));b=min(n,max(2,round(release*SR)))
    env[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2;env[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return env


def db(value):return float(20.*np.log10(max(float(value),1e-12)))


def metric(signal):
    data=np.asarray(signal,dtype=float)/32768.
    return {'rms_dbfs':db(np.sqrt(np.mean(data*data))),'peak_dbfs':db(np.abs(data).max()),
            'clipped_samples':int(np.count_nonzero(np.abs(np.asarray(signal,dtype=np.int32))>=32767))}


def loudness(path):
    log=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af',
        'loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode()
    values=json.loads(re.findall(r'\{[\s\S]*?\}',log)[-1]);return {k:v for k,v in values.items() if k.startswith('input_')}


def mp3(source,destination):
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-c:a','libmp3lame','-b:a','192k',str(destination)],check=True)


def main():
    timeline_bytes=TIMELINE.read_bytes();timeline=json.loads(timeline_bytes)
    duration=float(timeline['duration']);assert duration==43.;n=round(duration*SR)
    reference_path=OUT/'reference_v23/provenance.json';reference=json.loads(reference_path.read_text())
    assert reference['duration_seconds']==48.25 and reference['delivery_gain_db']==DELIVERY_GAIN_DB
    references={reference_path.relative_to(OUT).as_posix():sha(reference_path)};events=[];omitted=[]
    for event in reference['events']:
        if event['kind']=='background_music':continue
        if event['start']>=duration:
            omitted.append({'name':event['name'],'start':event['start'],'reason':'Old apron scene removed; outside new43s episode'});continue
        source=OUT/event['file'];assert sha(source)==event['sha256'],('V23 cue changed',source)
        data=pcm(source);assert len(data)==event['samples'] and event['start_sample']+len(data)<=n
        references[event['file']]=event['sha256'];events.append(dict(event,origin='V23 processed cue, unchanged PCM/start/duration'))
    assert len(events)==39
    music_source=OUT/'reference_v23/musique_v23.wav';assert sha(music_source)==REFERENCE_MUSIC_SHA
    references[music_source.relative_to(OUT).as_posix()]=REFERENCE_MUSIC_SHA
    raw_music=pcm(music_source)[:n].astype(np.float64);env=np.ones(n);tail=round(MUSIC_FADE_SECONDS*SR)
    env[-tail:]*=np.cos(np.linspace(0,np.pi/2,tail))**2
    music_signal=np.rint(raw_music*10.**(MUSIC_REDUCTION_DB/20.)*env[:,None]).astype(np.int32)
    write_pcm(OUT/'musique_v24.wav',music_signal)
    music={'name':'musique_v24','kind':'background_music','file':'musique_v24.wav','start':0.,
           'duration':duration,'start_sample':0,'samples':n,'end_seconds':duration,'sha256':sha(OUT/'musique_v24.wav'),
           'source_file':music_source.relative_to(OUT).as_posix(),'source_sha256':REFERENCE_MUSIC_SHA,
           'stage':'post-mix PCM before fixed+3.50dB delivery gain','reduction_db_relative_to_v23':MUSIC_REDUCTION_DB,
           'ending_fade':{'start_seconds':duration-MUSIC_FADE_SECONDS,'end_seconds':duration,'samples':tail,
                          'curve':'cos(linspace(0,pi/2,n))**2'},'original_wash_attenuation_unchanged':True,
           'actual_metrics':metric(music_signal)}
    events.append(music)
    spec=importlib.util.spec_from_file_location('mou_foley_v24',Path(__file__).with_name('foley.py'))
    foley=importlib.util.module_from_spec(spec);spec.loader.exec_module(foley);additions=[]
    for meta,data in foley.cues(timeline):
        target=OUT/'foley_v24'/f"{meta['name']}.wav";write_pcm(target,data)
        event={**meta,'file':target.relative_to(OUT).as_posix(),'sha256':sha(target),
               'start_sample':round(meta['start']*SR),'samples':len(data),'duration':len(data)/SR,
               'end_seconds':meta['start']+len(data)/SR,'stage':'original local synthesis, post-mix PCM before fixed delivery gain',
               'actual_metrics':metric(data)}
        assert event['end_seconds']<=40.25;events.append(event);additions.append(event)
    events.sort(key=lambda e:(e['start_sample'],e['name']));assert len(events)==58
    summed=np.zeros((n,2),dtype=np.int32)
    for event in events:
        data=pcm(OUT/event['file']).astype(np.int32);start=event['start_sample'];end=start+len(data)
        assert end<=n and len(data)==event['samples'];summed[start:end]+=data
    assert np.abs(summed).max()<32767
    before=np.rint(summed*fade(n)[:,None]).astype(np.int32);gain=10.**(DELIVERY_GAIN_DB/20.)
    mix=np.rint(before*gain).astype(np.int32);write_pcm(OUT/'mix.wav',mix)
    assert not mix[0].any() and not mix[-1].any()
    write_pcm(OUT/'test_fin_v24.wav',mix[round(40.25*SR):]);assert len(pcm(OUT/'test_fin_v24.wav'))==132000
    solo=np.rint(music_signal*gain).astype(np.int32);write_pcm(OUT/'jazz_seul_complet.wav',solo)
    write_pcm(OUT/'jazz_seul_15s.wav',solo[:15*SR]);mp3(OUT/'jazz_seul_15s.wav',OUT/'jazz_seul_15s.mp3')
    excerpt=round(11.25*SR);write_pcm(OUT/'extrait_bruitages_v24.wav',mix[excerpt:excerpt+15*SR])
    mp3(OUT/'extrait_bruitages_v24.wav',OUT/'extrait_bruitages_v24.mp3')
    source_hash=sha(__file__);foley_hash=sha(Path(__file__).with_name('foley.py'));timeline_hash=hashlib.sha256(timeline_bytes).hexdigest()
    body=slice(round(.3*SR),round(42.3*SR))
    observed=db(np.sqrt(np.mean(music_signal[body].astype(float)**2))/np.sqrt(np.mean(raw_music[body]**2)))
    assert abs(observed-MUSIC_REDUCTION_DB)<.002
    assert all(sha(OUT/name)==h for name,h in references.items());assert TIMELINE.read_bytes()==timeline_bytes
    limits='Technical source, timing, PCM and level checks only; model cannot listen in this session.'
    parameters={'composition':'Original V23 acoustic jazz trio, retained PCM,108BPM','new_composition':False,
                'music_source_sha256':sha(Path(__file__).with_name('music.py')),'reference_pcm':music['source_file'],
                'reference_sha256':REFERENCE_MUSIC_SHA,'reduction_db':MUSIC_REDUCTION_DB,
                'measured_reduction_db_before_fade':observed,'fade':music['ending_fade'],
                'partition_json':'partition_v23.json','partition_midi':'partition_v23.mid','scene_restarts':False}
    audit={'episode':'03','revision':'V24 quieter jazz and original paper Foley,43s','duration_seconds':duration,
           'sample_rate':SR,'channels':2,'bit_depth':16,'samples_per_channel':n,'expected_video_frames':1032,'fps':24,
           'source_sha256':source_hash,'foley_source_sha256':foley_hash,'chronologie_sha256':timeline_hash,
           'mix_sha256':sha(OUT/'mix.wav'),'event_count':len(events),'retained_v23_non_music_events':39,
           'new_event_count':len(additions),'new_events':additions,'omitted_events':omitted,
           'reference_sources_unchanged':references,'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':gain,
           'global_normalization_mode':'No loudness target; unchanged fixed+3.50dB delivery gain',
           'delivery_target_lufs':None,'historical_master_reapplied':False,'mix_metrics':metric(mix),
           'pregain_metrics':metric(before),'input_loudness':loudness(OUT/'mix.wav'),'clipped_samples':0,
           'background_music':parameters,'reaction_foreground_silence_40_25_to43':True,
           'test_final_file':'test_fin_v24.wav','test_final_sha256':sha(OUT/'test_fin_v24.wav'),
           'test_final_seconds':[40.25,43.],'excerpt_file':'extrait_bruitages_v24.mp3','excerpt_seconds':[11.25,26.25],
           'limits':limits}
    provenance={'title':timeline['titre'],'duration_seconds':duration,'sample_rate':SR,'channels':2,
                'source_sha256':source_hash,'foley_source_sha256':foley_hash,'chronologie_sha256':timeline_hash,
                'tools':['Python','NumPy','wave','FFmpeg'],'events':events,'omitted_events':omitted,
                'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':gain,'delivery_target_lufs':None,
                'bank_levels':'Sum only listed PCM at start_sample, multiply global8/35ms edge fade and round, then multiply delivery_gain_linear and round. No per-scene normalization.',
                'raw_source_provenance':'reference_v23/provenance.json','background_music':parameters,
                'new_voice_or_jingles':False,'no_speech':True,
                'reproduction':'.venv/bin/python -B episodes/03/cuisine_v24/sources/son.py','limits':limits}
    atomic_json(OUT/'provenance.json',provenance);atomic_json(EP/'controle/audit_son.json',audit)
    atomic_json(EP/'controle/audit_audio_v24.json',audit)
    print(json.dumps({k:audit[k] for k in ('duration_seconds','event_count','retained_v23_non_music_events',
          'new_event_count','mix_sha256','delivery_gain_db','mix_metrics','input_loudness')},indent=2))


if __name__=='__main__':main()
