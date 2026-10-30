"""V25 full sound: soft piano/bass bed and documented recorded-paper textures.

Only the musical bed is calibrated to its lower target. Whole-film gain stays
+3.50dB; no loudness normalization or per-scene gain is applied. Source method
and licence evidence are retained. Numerical checks do not constitute hearing.
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

EP=Path(__file__).resolve().parents[1]
OUT=EP/'audio'
TIMELINE=EP/'chronologie.json'
SR=48000
DELIVERY_GAIN_DB=3.5


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

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    timeline_bytes=TIMELINE.read_bytes();timeline=json.loads(timeline_bytes)
    duration=float(timeline['duration']);assert duration==43.;n=round(duration*SR)
    reference_path=OUT/'provenance_reference_v24.json'
    reference=json.loads(reference_path.read_text())
    assert reference['duration_seconds']==43. and reference['delivery_gain_db']==DELIVERY_GAIN_DB
    foley_path=EP/'sources/foley.py';music_path=EP/'sources/music.py'
    foley=load_module('mou_recorded_paper_v25',foley_path)
    generated,recording_provenance=foley.cues(timeline,reference['events'])
    replacements={meta['replaces_event'] for meta,signal in generated}
    assert len(replacements)==31
    events=[];retained=[];references={reference_path.relative_to(OUT).as_posix():sha(reference_path)}
    for event in reference['events']:
        if event['kind']=='background_music' or event['name'] in replacements:continue
        source=OUT/event['file'];assert sha(source)==event['sha256'],('Retained V24 PCM changed',source)
        data=pcm(source);assert len(data)==event['samples']
        copied={**event,'origin':'V24 nonpaper cue, unchanged PCM/start/duration/delivery gain'}
        events.append(copied);retained.append(copied);references[event['file']]=event['sha256']
    assert len(retained)==26
    paper=[]
    for metadata,data in generated:
        path=OUT/'foley_v25'/f"{metadata['name']}.wav";write_pcm(path,data)
        event={**metadata,'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),
               'start_sample':round(metadata['start']*SR),'samples':len(data),'duration':len(data)/SR,
               'end_seconds':metadata['start']+len(data)/SR,
               'stage':'recording excerpt adapted locally, postmix PCM before unchanged fixed delivery gain',
               'actual_metrics':metric(data)}
        assert event['end_seconds']<=40.25;events.append(event);paper.append(event)
    music=load_module('mou_soft_bed_v25',music_path)
    specification={'duration':duration,'bpm':108.,'duck_intervals':[c['sink'] for c in timeline['cycles']],
                   'duck_db':-1.,'duck_attack_seconds':.6,'duck_release_seconds':.8}
    signal,parameters,tracks,unducked=music.render_background(duration,specification)
    music_data=np.rint(signal*32767.).astype(np.int32)
    write_pcm(OUT/'musique_v25.wav',music_data)
    stems=[]
    for name,values in tracks.items():
        path=OUT/f'jazz_{name}_v25.wav';write_pcm(path,np.rint(values*32767.).astype(np.int32))
        stems.append({'track':name,'file':path.name,'sha256':sha(path),'actual_metrics':metric(pcm(path))})
    write_pcm(OUT/'jazz_sans_baisse_v25.wav',np.rint(unducked*32767.).astype(np.int32))
    parameters.update(stems=stems,music_source_sha256=sha(music_path),
                      unattenuated_file='jazz_sans_baisse_v25.wav',
                      unattenuated_sha256=sha(OUT/'jazz_sans_baisse_v25.wav'))
    reference_levels_path=OUT/'reference_levels_v23_v24.json'
    reference_levels=json.loads(reference_levels_path.read_text());references[reference_levels_path.name]=sha(reference_levels_path)
    body=music_data[2*SR:round(42.3*SR)].astype(float)/32768.
    current_rms_dbfs=db(np.sqrt(np.mean(body*body)))
    parameters['measured_music_body_rms_dbfs_pcm']=current_rms_dbfs
    parameters['reference_level_comparison']={revision:{**values,
        'v25_minus_reference_rms_db':current_rms_dbfs-values['rms_dbfs']} for revision,values in reference_levels.items()}
    parameters['reference_level_comparison_note']='Different calmer orchestration; differences are measured RMS levels, not proof of perceived softness.'
    music.write_midi(OUT/'partition_v25.mid',parameters['notes'])
    atomic_json(OUT/'partition_v25.json',parameters)
    music_event={'name':'musique_v25','kind':'background_music','file':'musique_v25.wav','start':0.,
                 'duration':duration,'start_sample':0,'samples':n,'end_seconds':duration,
                 'sha256':sha(OUT/'musique_v25.wav'),'actual_metrics':metric(music_data),
                 'stage':'new soft piano/bass score, postmix PCM before unchanged fixed+3.50dB gain',
                 'score_json':'partition_v25.json','score_midi':'partition_v25.mid'}
    events.append(music_event);events.sort(key=lambda e:(e['start_sample'],e['name']))
    assert len(events)==58
    summed=np.zeros((n,2),dtype=np.int32)
    for event in events:
        data=pcm(OUT/event['file']).astype(np.int32);a=event['start_sample'];b=a+len(data)
        assert b<=n and len(data)==event['samples'];summed[a:b]+=data
    assert np.abs(summed).max()<32767
    before=np.rint(summed*fade(n)[:,None]).astype(np.int32)
    gain=10.**(DELIVERY_GAIN_DB/20.);mix=np.rint(before*gain).astype(np.int32)
    write_pcm(OUT/'mix.wav',mix)
    assert not mix[0].any() and not mix[-1].any()
    write_pcm(OUT/'test_fin_v25.wav',mix[35*SR:]);assert len(pcm(OUT/'test_fin_v25.wav'))==384000
    solo=np.rint(np.rint(music_data*fade(n)[:,None])*gain).astype(np.int32)
    write_pcm(OUT/'jazz_seul_complet.wav',solo);write_pcm(OUT/'jazz_seul_15s.wav',solo[:15*SR])
    mp3(OUT/'jazz_seul_15s.wav',OUT/'jazz_seul_15s.mp3')
    write_pcm(OUT/'extrait_mix_v25.wav',mix[round(10.25*SR):round(17.25*SR)])
    mp3(OUT/'extrait_mix_v25.wav',OUT/'extrait_mix_v25.mp3')
    foreground=[e for e in events if e['kind'] not in ('background_music','frying')]
    assert all(e['end_seconds']<=40.25 for e in foreground)
    assert all(sha(OUT/name)==digest for name,digest in references.items())
    assert TIMELINE.read_bytes()==timeline_bytes
    limitations='No model listening is available. Levels, source evidence and source-defined attacks are technical facts; softness, comfort, material identity and comic success require listening/viewing judgement.'
    source_hash=sha(__file__);timeline_hash=hashlib.sha256(timeline_bytes).hexdigest()
    audit={'episode':'03','revision':'V25 soft piano/bass bed and recorded-paper adaptations',
           'duration_seconds':duration,'sample_rate':SR,'channels':2,'bit_depth':16,
           'samples_per_channel':n,'expected_video_frames':1032,'fps':24,
           'source_sha256':source_hash,'music_source_sha256':sha(music_path),'foley_source_sha256':sha(foley_path),
           'chronologie_sha256':timeline_hash,'mix_sha256':sha(OUT/'mix.wav'),
           'event_count':len(events),'retained_v24_nonpaper_events':len(retained),
           'recorded_paper_event_count':len(paper),'recorded_paper_events':paper,
           'reference_sources_unchanged':references,'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':gain,
           'global_normalization_mode':'No whole-film loudness normalization; original fixed+3.50dB delivery gain',
           'delivery_target_lufs':None,'historical_master_reapplied':False,
           'pregain_metrics':metric(before),'mix_metrics':metric(mix),'input_loudness':loudness(OUT/'mix.wav'),
           'clipped_samples':0,'background_music':parameters,
           'paper_palette_status':'Proposed V25 material; earlier short trial not accepted or represented as approved',
           'recording_source_provenance':recording_provenance,
           'synthetic_elements_retained':['water','tap','knife','cooking','salt','whistle'],
           'retained_synthetic_elements_status':'Existing softened processed V24 cues; no verified recorded replacements added',
           'reaction_foreground_silence_40_25_to43':True,
           'test_final_file':'test_fin_v25.wav','test_final_sha256':sha(OUT/'test_fin_v25.wav'),
           'test_final_seconds':[35.,43.],'excerpt_file':'extrait_mix_v25.mp3','excerpt_seconds':[10.25,17.25],
           'limits':limitations}
    provenance={'title':timeline['titre'],'duration_seconds':duration,'sample_rate':SR,'channels':2,
                'source_sha256':source_hash,'music_source_sha256':sha(music_path),'foley_source_sha256':sha(foley_path),
                'chronologie_sha256':timeline_hash,'tools':['Python','NumPy','wave','FFmpeg','FluidSynth','MIT FluidR3 subset'],
                'events':events,'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':gain,'delivery_target_lufs':None,
                'bank_levels':'Sum only listed PCM events at start_sample; global8/35ms edge fade then round; fixed+3.50dB gain then round. No per-scene normalization.',
                'raw_source_provenance':'provenance_reference_v24.json','background_music':parameters,
                'recording_source_provenance':'assets/paper_recordings/provenance.json',
                'paper_palette_status':audit['paper_palette_status'],'new_voice_or_jingles':False,'no_speech':True,
                'reproduction':'.venv/bin/python -B episodes/03/cuisine_v25/sources/son.py','limits':limitations}
    atomic_json(OUT/'provenance.json',provenance);atomic_json(EP/'controle/audit_son.json',audit)
    atomic_json(EP/'controle/audit_audio_v25.json',audit)
    print(json.dumps({key:audit[key] for key in ('duration_seconds','event_count','retained_v24_nonpaper_events',
          'recorded_paper_event_count','mix_sha256','delivery_gain_db','mix_metrics','input_loudness')},indent=2))
    print(json.dumps({'music_body_rms_dbfs':current_rms_dbfs,'reference_level_comparison':parameters['reference_level_comparison']},indent=2))


if __name__=='__main__':main()

