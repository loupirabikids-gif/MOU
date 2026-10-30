"""V26 sound: a continuous restrained jazz score and explicitly timed Foley.

All production is local with Python/NumPy/FFmpeg/FluidSynth. Recorded paper
adaptations retain their licences and source distinctions. Other kitchen
sounds are previously synthesized, softened MOU assets, not new recordings.
A fixed gain is used at delivery; no scene-dependent master normalization.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import wave
import numpy as np

EP=Path(__file__).resolve().parents[1]
OUT=EP/'audio'
TIMELINE=EP/'chronologie.json'
SR=48000
DELIVERY_GAIN_DB=3.5
LIMITS='No model listening is available. Numerical levels, timing and source evidence do not establish perceived comfort, material realism or comic success.'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w') as target:target.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,signal):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=np.asarray(signal,dtype=np.int32)
    assert data.ndim==2 and data.shape[1]==2 and np.abs(data).max()<32767
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent);os.close(fd)
    try:
        with wave.open(temp,'wb') as target:
            target.setnchannels(2);target.setsampwidth(2);target.setframerate(SR)
            target.writeframes(data.astype('<i2').tobytes())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def fade(n,attack=.008,release=.035):
    env=np.ones(n);a=min(n,max(2,round(attack*SR)));b=min(n,max(2,round(release*SR)))
    env[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    env[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return env


def db(value):return float(20*np.log10(max(float(value),1e-12)))


def metric(signal):
    data=np.asarray(signal,dtype=np.float64)/32768.
    return {'rms_dbfs':db(np.sqrt(np.mean(data*data))),
            'peak_dbfs':db(np.abs(data).max()),
            'clipped_samples':int(np.count_nonzero(np.abs(np.asarray(signal,dtype=np.int32))>=32767))}


def loudness(path):
    log=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af',
        'loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode()
    return {k:v for k,v in json.loads(re.findall(r'\{[\s\S]*?\}',log)[-1]).items() if k.startswith('input_')}


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module


def source_bank():
    """Materialize one minimal, hashed input bank from the initially copied V25 assets.

    Subsequent renders, including a cold extracted ZIP, use only this local bank.
    The old event manifest is not required after materialization.
    """
    manifest=OUT/'source_bank_v26.json'
    if not manifest.exists():
        old=OUT/'provenance_reference_v24.json';reference=json.loads(old.read_text())
        names={'cuisson_v22','cuillere_posee','carotte_coupe_1','carotte_coupe_2',
               'couteau_pose','contact_tomate','sel_saupoudre'}
        names.update(f'sifflement_p1_n{j}' for j in (1,2,3))
        for cycle in (1,2,3,5):names.update(f'c{cycle}_{suffix}' for suffix in ('eau','robinet_ouvre','robinet_ferme'))
        events={}
        for event in reference['events']:
            if event['name'] not in names:continue
            source=OUT/event['file'];assert sha(source)==event['sha256']
            target=OUT/'raw_bank'/f"{event['name']}.wav";target.parent.mkdir(exist_ok=True)
            target.write_bytes(source.read_bytes())
            events[event['name']]={**event,'file':target.relative_to(OUT).as_posix(),
                                  'origin':'Previously synthesized and softened MOU kitchen asset, copied before V26 retiming'}
        assert set(events)==names
        papers=[{k:e[k] for k in ('name','kind','sha256','cycle') if k in e}
                for e in reference['events'] if 'paper' in e['kind']]
        bank={'source_manifest_sha256':sha(old),'source_revision':'V24 event metadata retained by V25',
              'raw_events':events,'paper_reference_events':papers,
              'note':'Only raw_events have PCM inputs here; paper references identify the former cues but are regenerated from the licensed paper recordings.'}
        atomic_json(manifest,bank)
    bank=json.loads(manifest.read_text())
    for event in bank['raw_events'].values():assert sha(OUT/event['file'])==event['sha256']
    return bank


def fixed_asset(data,target_rms=None,peak_cap=None,gain_db=0.,duration=None,offset=0.,attack=.008,release=.035):
    """One offline gain per physical cue type, with no mix detector or pumping."""
    signal=np.asarray(data,dtype=np.float64)/32768.
    if duration is not None:
        start=round(offset*SR);n=round(duration*SR)
        assert start+n<=len(signal),(len(signal),start,n)
        signal=signal[start:start+n].copy()
    else:signal=signal.copy()
    signal*=fade(len(signal),attack,release)[:,None]
    rms=float(np.sqrt(np.mean(signal*signal)));peak=float(np.abs(signal).max())
    factor=10.**(gain_db/20.)
    if target_rms is not None:factor*=10.**(target_rms/20.)/max(rms,1e-12)
    if peak_cap is not None:factor=min(factor,10.**(peak_cap/20.)/max(peak,1e-12))
    return np.rint(signal*factor*32768.).astype(np.int32),{'offline_gain_db':db(factor),
        'target_rms_dbfs':target_rms,'peak_cap_dbfs':peak_cap,'source_offset_seconds':offset,
        'attack_seconds':attack,'release_seconds':release,'resample_or_stretch':False,
        'normalization_scope':'Fixed single cue/type gain; no whole-mix or scene-dependent detector'}


def gap_metrics(data,start,end):
    signal=np.asarray(data,dtype=np.int32)[round(start*SR):round(end*SR)]
    zero=(np.max(np.abs(signal),axis=1)==0)
    edges=np.diff(np.r_[False,zero,False].astype(np.int8));a=np.flatnonzero(edges==1);b=np.flatnonzero(edges==-1)
    longest=float((b-a).max()/SR) if len(a) else 0.
    windows=[metric(signal[k:k+SR//2])['rms_dbfs'] for k in range(0,len(signal)-SR//2+1,SR//2)]
    return {'interval':[start,end],'longest_digital_zero_seconds':longest,
            'half_second_rms_dbfs':windows,'half_second_range_db':max(windows)-min(windows),
            'half_second_p05_p95_dbfs':np.percentile(windows,[5,95]).tolist(),
            'note':'Finite-window RMS describes the waveform, not perceived musical continuity.'}


def measure_motion_sync(timeline):
    source=EP/'sources';sys.path.insert(0,str(source))
    animation=load_module('mou_sound_motion_v26',source/'animation.py')
    hashes={name:sha(source/name) for name in ('animation.py','performance.py','jeu_visage.py')}
    method='240 actual V26 world hand states per wipe; gradient of right-minus-left; local maxima after first32% approach and before94%, separated by >=20% of action duration; numerical only'
    result={'source_hashes':hashes,'cycles':{},'method':method}
    for cycle in timeline['cycles']:
        a,b=cycle['wipe'];times=np.linspace(a,b,240,endpoint=False);delta=[]
        for t in times:
            state=animation.scene_state(float(t))
            delta.append(np.array(state['hands']['right'])-np.array(state['hands']['left']))
        speed=np.linalg.norm(np.gradient(np.array(delta),times,axis=0),axis=1)
        candidates=[i for i in range(1,len(times)-1) if speed[i]>=speed[i-1] and speed[i]>speed[i+1] and a+.32*(b-a)<times[i]<b-.06*(b-a)]
        selected=[]
        for i in sorted(candidates,key=lambda i:speed[i],reverse=True):
            if all(abs(times[i]-times[j])>=.20*(b-a) for j in selected):selected.append(i)
            if len(selected)==2:break
        assert len(selected)==2,(cycle['id'],'two real friction maxima not found')
        selected.sort()
        result['cycles'][str(cycle['id'])]={'action_interval':[a,b],
            'centres_seconds':[float(times[i]) for i in selected],
            'relative_speed_pixels_per_second':[float(speed[i]) for i in selected],'method':method}
    assert hashes=={name:sha(source/name) for name in hashes},'Animation sources changed during Foley measurement'
    atomic_json(OUT/'motion_sync_v26.json',result)
    return result


def main():
    timeline_bytes=TIMELINE.read_bytes();timeline=json.loads(timeline_bytes)
    duration=float(timeline['duration']);assert duration==38.;n=round(duration*SR)
    bank=source_bank();raw=bank['raw_events'];events=[]
    motion=measure_motion_sync(timeline)
    def add(name,kind,start,data,metadata):
        path=OUT/'cues_v26'/f'{name}.wav';write_pcm(path,data)
        event={'name':name,'kind':kind,'file':path.relative_to(OUT).as_posix(),
               'start':float(start),'start_sample':round(start*SR),'duration':len(data)/SR,
               'samples':len(data),'end_seconds':float(start)+len(data)/SR,
               'sha256':sha(path),'actual_metrics':metric(data),**metadata}
        assert event['end_seconds']<=duration
        events.append(event)
    def asset(source_name,name,kind,start,target_rms=None,peak_cap=None,gain_db=0.,duration=None,offset=0.,attack=.008,release=.035,**metadata):
        source=raw[source_name];data,processing=fixed_asset(pcm(OUT/source['file']),target_rms,peak_cap,gain_db,duration,offset,attack,release)
        add(name,kind,start,data,{'source_bank_key':source_name,'source_sha256':source['sha256'],
            'source_method':'Previously synthesized/softened MOU asset, not recorded Foley',
            'processing':processing,**metadata})
    # A low cooking bed ends with the food; no dramatic stinger is added.
    cooking,processing=fixed_asset(pcm(OUT/raw['cuisson_v22']['file']),target_rms=-48.,peak_cap=-35.,duration=33.25,attack=.04,release=1.75)
    add('cuisson_v26','frying',0.,cooking,{'source_bank_key':'cuisson_v22','source_sha256':raw['cuisson_v22']['sha256'],'processing':processing,'source_method':'Existing original synthesis','fade_out_seconds':[31.5,33.25]})
    for j,start in ((1,.3),(2,.855556),(3,1.411111)):
        asset(f'sifflement_p1_n{j}',f'sifflement_n{j}_v26','whistle',start,gain_db=-6.,attack=.020,release=.025,opening_only=True)
    asset('cuillere_posee','cuillere_posee_v26','wood_contact',2.70,gain_db=-1.)
    for c in timeline['cycles']:
        cycle=c['id'];source_cycle=5 if cycle==4 else cycle;a,b=c['water'];length=b-a
        source_name=f'c{source_cycle}_eau';available=len(pcm(OUT/raw[source_name]['file']))/SR
        offset=max(0.,min(.08,(available-length)/2.))
        asset(source_name,f'c{cycle}_eau_v26','water',a,target_rms=-39.,peak_cap=-25.,duration=length,offset=offset,attack=.035,release=.055,cycle=cycle,sync={'action_interval':c['water']})
        for suffix,start in (('ouvre',a),('ferme',b)):
            asset(f'c{source_cycle}_robinet_{suffix}',f'c{cycle}_robinet_{suffix}_v26','tap',start,target_rms=-45.,peak_cap=-29.,attack=.003,release=.02,cycle=cycle)
    for j,start in enumerate(timeline['carrot']['cut_times'],1):
        asset(f'carotte_coupe_{j}',f'carotte_coupe_{j}_v26','carrot_chop',start,gain_db=-2.,attack=.004,release=.025)
    asset('couteau_pose','couteau_pose_v26','knife_setdown',timeline['carrot']['knife_park'],gain_db=-1.5)
    asset('contact_tomate','contact_tomate_v26','tomato_contact',timeline['cooking_events']['tomato_contact'],target_rms=-44.,peak_cap=-32.)
    a,b=timeline['salt']['sprinkle'];asset('sel_saupoudre','sel_saupoudre_v26','salt_sprinkle',a,target_rms=-47.,peak_cap=-34.,duration=b-a,attack=.015,release=.035)
    foley=load_module('mou_paper_v26',EP/'sources/foley.py')
    papers,recording_provenance=foley.cues(timeline,bank['paper_reference_events'])
    for meta,data in papers:
        add(meta['name'],meta['kind'],meta['start'],data,{key:value for key,value in meta.items() if key not in ('name','kind','start','duration')})
    music=load_module('mou_music_v26',EP/'sources/music.py')
    specification={'duration':duration,'bpm':108.,'duck_intervals':[c['sink'] for c in timeline['cycles']],
                   'duck_db':-.6,'duck_attack_seconds':.6,'duck_release_seconds':.8}
    signal,parameters,tracks,unducked=music.render_background(duration,specification)
    music_data=np.rint(signal*32767.).astype(np.int32);write_pcm(OUT/'musique_v26.wav',music_data)
    stems=[]
    for name,values in tracks.items():
        path=OUT/'stems_v26'/f'{name}.wav';write_pcm(path,np.rint(values*32767.).astype(np.int32))
        stems.append({'track':name,'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),'actual_metrics':metric(pcm(path))})
    parameters['stems']=stems
    parameters['continuity_measurements']=gap_metrics(music_data,2.,duration-.7)
    music.write_midi(OUT/'partition_v26.mid',parameters['notes']);atomic_json(OUT/'partition_v26.json',parameters)
    events.append({'name':'musique_v26','kind':'background_music','file':'musique_v26.wav','start':0.,
        'start_sample':0,'duration':duration,'samples':n,'end_seconds':duration,'sha256':sha(OUT/'musique_v26.wav'),
        'actual_metrics':metric(music_data),'stage':'Music-only fixed calibration before fixed delivery gain'})
    events.sort(key=lambda e:(e['start_sample'],e['name']))
    summed=np.zeros((n,2),dtype=np.int32)
    for event in events:
        data=pcm(OUT/event['file']).astype(np.int32);a=event['start_sample'];b=a+len(data)
        assert b<=n and len(data)==event['samples'];summed[a:b]+=data
    before=np.rint(summed*fade(n)[:,None]).astype(np.int32)
    mix=np.rint(before*10.**(DELIVERY_GAIN_DB/20.)).astype(np.int32);write_pcm(OUT/'mix.wav',mix)
    write_pcm(OUT/'test_fin_v26.wav',mix[30*SR:]);assert len(pcm(OUT/'test_fin_v26.wav'))==8*SR
    foreground=[e for e in events if e['kind'] not in ('background_music','frying')]
    assert all(e['end_seconds']<=30.25 for e in foreground)
    assert all(e['end_seconds']<=33.25 for e in events if e['kind']!='background_music')
    assert not mix[0].any() and not mix[-1].any()
    assert parameters['continuity_measurements']['longest_digital_zero_seconds']<.1
    source_hashes={p.name:sha(p) for p in (EP/'sources/son.py',EP/'sources/music.py',EP/'sources/foley.py')}
    timeline_hash=hashlib.sha256(timeline_bytes).hexdigest()
    scene_levels=[]
    for name,a,b in [('cuisine',.2,2.6),('lavage1',3.9,5.35),('lavage2',11.3,12.4),('lavage3',16.5,17.45),('lavage4',23.25,24.2),('hesitation',21.95,22.45),('final',35.75,37.25)]:
        scene_levels.append({'scene':name,'interval':[a,b],'mix':metric(mix[round(a*SR):round(b*SR)]),'music_before_master':metric(music_data[round(a*SR):round(b*SR)])})
    provenance={'title':timeline['titre'],'revision':26,'duration_seconds':duration,'sample_rate':SR,'channels':2,
        'source_sha256':source_hashes['son.py'],'music_source_sha256':source_hashes['music.py'],'foley_source_sha256':source_hashes['foley.py'],
        'chronologie_sha256':timeline_hash,'source_bank_file':'source_bank_v26.json','source_bank_sha256':sha(OUT/'source_bank_v26.json'),
        'motion_sync_file':'motion_sync_v26.json','motion_sync_sha256':sha(OUT/'motion_sync_v26.json'),
        'events':events,'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':10.**(DELIVERY_GAIN_DB/20.),'delivery_target_lufs':None,
        'bank_levels':'Sum listed cue PCM at start_sample; global8/35ms edge fade then round; fixed+3.50dB gain then round. No scene or whole-film loudness normalization.',
        'background_music':parameters,'recording_source_provenance':'assets/paper_recordings/provenance.json',
        'no_speech':True,'new_voice_or_jingles':False,'foreground_ends_before':30.25,'kitchen_bed_ends':33.25,
        'synthetic_elements_retained':['water','tap','knife','cooking','salt','whistle','tomato','spoon'],
        'reproduction':'.venv/bin/python -B episodes/03/cuisine_v26/sources/son.py','limits':LIMITS}
    atomic_json(OUT/'provenance.json',provenance)
    audit={'revision':26,'duration_seconds':duration,'sample_rate':SR,'channels':2,'samples_per_channel':n,
        'expected_video_frames':912,'fps':24,'source_hashes':source_hashes,'chronologie_sha256':timeline_hash,
        'mix_sha256':sha(OUT/'mix.wav'),'test_final_sha256':sha(OUT/'test_fin_v26.wav'),'test_final_seconds':[30.,38.],
        'motion_sync':motion,'motion_sync_sha256':sha(OUT/'motion_sync_v26.json'),
        'event_count':len(events),'paper_event_count':len(papers),'recording_source_provenance':recording_provenance,
        'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_target_lufs':None,'global_normalization_mode':'Fixed gain only; no live scene normalization',
        'pregain_metrics':metric(before),'mix_metrics':metric(mix),'input_loudness':loudness(OUT/'mix.wav'),
        'background_music':parameters,'scene_levels':scene_levels,'clipped_samples':0,'limits':LIMITS}
    atomic_json(EP/'controle/audit_son.json',audit);atomic_json(EP/'controle/audit_audio_v26.json',audit)
    assert TIMELINE.read_bytes()==timeline_bytes,'Timeline changed during sound render'
    print(json.dumps({'mix':str(OUT/'mix.wav'),'seconds':duration,'events':len(events),'paper_events':len(papers),
        'music_continuity':{key:parameters['continuity_measurements'][key] for key in ('longest_digital_zero_seconds','half_second_range_db','half_second_p05_p95_dbfs')},'mix_metrics':metric(mix),'loudness':audit['input_loudness']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
