"""V27 sound: evolving nylon-guitar bossa, physical Foley and brief vocal proposals.

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


def punctuation(data,start):
    """One absolute-time cut shared by every event and stem, before PCM rounding."""
    signal=np.asarray(data,dtype=np.float64).copy()
    times=float(start)+np.arange(len(signal))/SR
    gate=np.ones(len(signal))
    # Six milliseconds immediately before the intended sharp32s stop avoid
    # an unrelated digital click. The half-second itself remains exact zero.
    before=(times>=31.994)&(times<32.)
    gate[before]*=np.cos((times[before]-31.994)/.006*np.pi/2.)**2
    gate[(times>=32.)&(times<32.5)]=0.
    restart=(times>=32.5)&(times<32.508)
    gate[restart]*=np.sin((times[restart]-32.5)/.008*np.pi/2.)**2
    tail=(times>=37.218)&(times<37.25)
    gate[tail]*=np.cos((times[tail]-37.218)/.032*np.pi/2.)**2
    gate[times>=37.25]=0.
    return signal*gate[:,None]


def _freeze_reference():
    """Retain metadata only, so cold regeneration needs no older episode."""
    path=OUT/'reference_events_v26.json'
    if not path.exists():
        original=json.loads((OUT/'provenance.json').read_text())
        assert original['revision']==26,'First run requires the copied V26 provenance'
        kept=[{k:e[k] for k in ('name','kind','start','duration','samples','sha256')}
              for e in original['events'] if e['kind'] not in ('frying','background_music')]
        assert len(kept)==46
        atomic_json(path,{'source_revision':26,'source_provenance_sha256':sha(OUT/'provenance.json'),
                         'events':kept,'method':'Metadata snapshot; only hashes used, no V26 folder input required.'})
    return json.loads(path.read_text())


def _music_contract(data):
    """Validate the new score's true cut, isolated note and quiet final hold."""
    array=np.asarray(data)
    quiet=np.ones(len(array),bool);quiet[:32*SR]=False
    quiet[round(36.25*SR):round(36.75*SR)]=False
    assert not array[quiet].any(),'Music outside pre32s score and the36.25s final note'
    assert np.abs(array[round(36.25*SR):round(36.75*SR)]).max()>0,'Final guitar note missing'
    return {'score_end_s':32.,'music_zero_except_final_note_after32':True,
            'final_note_allowed_s':[36.25,36.75],
            'last_body_hold_music_zero_s':[37.25,38.]}


def main():
    timeline_bytes=TIMELINE.read_bytes();timeline=json.loads(timeline_bytes)
    duration=float(timeline['duration']);assert duration==38.;n=round(duration*SR)
    assert all((EP/'sources'/name).is_file() for name in ('music.py','foley_supplement.py','vocal.py'))
    source_paths=[EP/'sources'/name for name in ('son.py','music.py','foley.py','foley_supplement.py','vocal.py')]
    frozen={p.name:sha(p) for p in source_paths}
    old_reference=_freeze_reference();reference={e['name']:e for e in old_reference['events']}
    bank=source_bank();raw=bank['raw_events'];events=[];equivalence=[]
    motion=measure_motion_sync(timeline)
    atomic_json(OUT/'motion_sync_v27.json',motion)
    category_data={name:np.zeros((n,2),dtype=np.int64) for name in ('effets','voix','ambiance','musique')}

    def add(name,kind,start,data,metadata,category='effets',float_input=False,v26_reference_name=None):
        assert re.fullmatch(r'[A-Za-z0-9_-]+',name),name
        source=np.asarray(data,dtype=np.float64)
        assert source.ndim==2 and source.shape[1]==2 and np.isfinite(source).all(),name
        if not float_input:source=source/32768.
        treated=punctuation(source,float(start))
        quantized=np.rint(treated*32768.).astype(np.int32)
        path=OUT/'cues_v27'/f'{name}.wav';write_pcm(path,quantized)
        event={**metadata,'name':name,'kind':kind,'file':path.relative_to(OUT).as_posix(),
               'start':float(start),'start_sample':round(float(start)*SR),
               'duration':len(quantized)/SR,'samples':len(quantized),
               'end_seconds':float(start)+len(quantized)/SR,'sha256':sha(path),
               'actual_metrics':metric(quantized),'stem_category':category,
               'absolute_punctuation_applied':True}
        assert 0<=event['start_sample'] and event['start_sample']+len(quantized)<=n,name
        events.append(event)
        a=event['start_sample'];category_data[category][a:a+len(quantized)]+=quantized
        if v26_reference_name:
            prior=reference[v26_reference_name]
            same=event['sha256']==prior['sha256'] and abs(event['start']-prior['start'])<1e-8
            assert same,('Retained V26 cue changed',name,prior['sha256'],event['sha256'])
            equivalence.append({'current':name,'reference':v26_reference_name,'pcm_and_timing_unchanged':True,
                                'sha256':event['sha256']})
        return event

    def asset(source_name,name,kind,start,target_rms=None,peak_cap=None,gain_db=0.,duration=None,offset=0.,attack=.008,release=.035,**metadata):
        item=raw[source_name]
        data,processing=fixed_asset(pcm(OUT/item['file']),target_rms,peak_cap,gain_db,duration,offset,attack,release)
        return add(name,kind,start,data,{'source_bank_key':source_name,'source_sha256':item['sha256'],
            'source_method':'Previously synthesized/softened MOU asset, not newly recorded Foley',
            'processing':processing,**metadata},v26_reference_name=name.replace('_v27','_v26'))

    # All praised water/tap/utensil sounds keep their exact V26 cue PCM and timing.
    for j,start in ((1,.3),(2,.855556),(3,1.411111)):
        asset(f'sifflement_p1_n{j}',f'sifflement_n{j}_v27','whistle',start,gain_db=-6.,attack=.020,release=.025,opening_only=True)
    asset('cuillere_posee','cuillere_posee_v27','wood_contact',2.70,gain_db=-1.)
    for c in timeline['cycles']:
        cycle=c['id'];source_cycle=5 if cycle==4 else cycle;a,b=c['water'];length=b-a
        source_name=f'c{source_cycle}_eau';available=len(pcm(OUT/raw[source_name]['file']))/SR
        offset=max(0.,min(.08,(available-length)/2.))
        asset(source_name,f'c{cycle}_eau_v27','water',a,target_rms=-39.,peak_cap=-25.,duration=length,offset=offset,attack=.035,release=.055,cycle=cycle,sync={'action_interval':c['water']})
        for suffix,start in (('ouvre',a),('ferme',b)):
            asset(f'c{source_cycle}_robinet_{suffix}',f'c{cycle}_robinet_{suffix}_v27','tap',start,target_rms=-45.,peak_cap=-29.,attack=.003,release=.02,cycle=cycle)
    for j,start in enumerate(timeline['carrot']['cut_times'],1):
        asset(f'carotte_coupe_{j}',f'carotte_coupe_{j}_v27','carrot_chop',start,gain_db=-2.,attack=.004,release=.025)
    asset('couteau_pose','couteau_pose_v27','knife_setdown',timeline['carrot']['knife_park'],gain_db=-1.5)
    asset('contact_tomate','contact_tomate_v27','tomato_contact',timeline['cooking_events']['tomato_contact'],target_rms=-44.,peak_cap=-32.)
    a,b=timeline['salt']['sprinkle']
    asset('sel_saupoudre','sel_saupoudre_v27','salt_sprinkle',a,target_rms=-47.,peak_cap=-34.,duration=b-a,attack=.015,release=.035)
    foley=load_module('mou_paper_v27',EP/'sources/foley.py')
    papers,recording_provenance=foley.cues(timeline,bank['paper_reference_events'])
    for meta,data in papers:
        add(meta['name'],meta['kind'],meta['start'],data,
            {key:value for key,value in meta.items() if key not in ('name','kind','start','duration')},
            v26_reference_name=meta['name'])
    assert len(equivalence)==46

    supplement=load_module('mou_foley_supplement_v27',EP/'sources/foley_supplement.py')
    extra=supplement.cues(timeline,sr=SR)
    assert sum(meta.get('replaces_kind')=='frying' for meta,data in extra)==1,'One cooking replacement required'
    for meta,data in extra:
        category='ambiance' if meta['kind']=='room_ambience' else 'effets'
        add(meta['name'],meta['kind'],meta['start'],data,meta,category=category,float_input=True)

    vocal=load_module('mou_vocal_v27',EP/'sources/vocal.py')
    voices=vocal.cues(timeline,sr=SR);assert len(voices)==5
    for meta,data in voices:
        add(meta['name'],meta['kind'],meta['start'],data,meta,category='voix',float_input=True)

    music=load_module('mou_music_v27',EP/'sources/music.py')
    specification={'duration':duration,'bpm':108.,'duck_intervals':[c['sink'] for c in timeline['cycles']],
                   'duck_db':-.6,'duck_attack_seconds':.6,'duck_release_seconds':.8}
    signal,parameters,tracks,unducked=music.render_background(duration,specification)
    contract=_music_contract(signal)
    music_event=add('musique_v27','background_music',0.,signal,
        {'score_json':'partition_v27.json','score_midi':'partition_v27.mid',
         'stage':'Original nylon-guitar/bass score; fixed music-only calibration before unchanged delivery gain'},
        category='musique',float_input=True)
    music_data=pcm(OUT/music_event['file']).astype(np.int32)
    write_pcm(OUT/'musique_v27.wav',music_data)
    stems=[]
    for name,values in tracks.items():
        path=OUT/'stems_v27'/f'{name}.wav'
        write_pcm(path,np.rint(punctuation(values,0.)*32768.).astype(np.int32))
        stems.append({'track':name,'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),
                      'actual_metrics':metric(pcm(path)),'before_fixed_delivery_gain':True})
    parameters['stems']=list(stems);parameters['cut_contract']=contract
    parameters['precut_continuity_measurements']=gap_metrics(music_data,2.,31.8)
    music.write_midi(OUT/'partition_v27.mid',parameters['notes'])
    atomic_json(OUT/'partition_v27.json',parameters)
    for name in ('effets','voix','ambiance'):
        path=OUT/'stems_v27'/f'{name}.wav';write_pcm(path,category_data[name])
        stems.append({'track':name,'file':path.relative_to(OUT).as_posix(),'sha256':sha(path),
                      'actual_metrics':metric(pcm(path)),'before_fixed_delivery_gain':True})

    # A compact audition keeps exactly the five proposed cues, at their film gain.
    audition=np.zeros((round(5.5*SR),2),dtype=np.int32);audition_meta=[]
    voice_events=[e for e in events if e['kind']=='mou_nonverbal']
    for j,event in enumerate(voice_events):
        data=pcm(OUT/event['file']).astype(np.int32);start=round((j+.15)*SR)
        audition[start:start+len(data)]=data
        audition_meta.append({'start':start/SR,'film_start':event['start'],'name':event['name'],
                              'intended_expression':event.get('intended_expression'),'file':event['file']})
    audition=np.rint(audition*10.**(DELIVERY_GAIN_DB/20.)).astype(np.int32)
    write_pcm(OUT/'audition_voix_v27.wav',audition)
    atomic_json(OUT/'audition_voix_v27.json',{'duration_s':5.5,'events':audition_meta,
        'limits':'Audition of unlistened-to library adaptations, not verified natural human acting or wordlessness.'})

    events.sort(key=lambda event:(event['start_sample'],event['name']))
    summed=sum(category_data.values())
    before=np.rint(summed*fade(n)[:,None]).astype(np.int32)
    gain=10.**(DELIVERY_GAIN_DB/20.)
    mix=np.rint(before*gain).astype(np.int32)
    write_pcm(OUT/'mix.wav',mix)
    write_pcm(OUT/'test_fin_v27.wav',mix[30*SR:]);assert len(pcm(OUT/'test_fin_v27.wav'))==8*SR
    cut_a,cut_b=32*SR,round(32.5*SR);hold_a=round(37.25*SR)
    assert not mix[cut_a:cut_b].any(),'The requested half-second silence is not exact'
    assert not mix[hold_a:].any(),'Sound continues after final held pose begins'
    assert not mix[0].any() and not mix[-1].any()
    assert all(not values[cut_a:cut_b].any() and not values[hold_a:].any()
               for values in category_data.values()),'One stem breaks punctuation'
    _music_contract(music_data)
    assert all(pcm(OUT/e['file']).shape==(e['samples'],2) for e in events)
    source_hashes={p.name:sha(p) for p in source_paths}
    assert source_hashes==frozen,'A sound source changed during synthesis'
    assert TIMELINE.read_bytes()==timeline_bytes,'Timeline changed during synthesis'
    scene_levels=[]
    for name,a,b in [('cuisine',.2,2.6),('lavage1',3.9,5.35),('lavage2',11.3,12.4),
                     ('lavage3',16.5,17.45),('lavage4',23.25,24.2),('hesitation',21.95,22.45),
                     ('choc',31.5,32.),('silence',32.,32.5),('deception',32.5,33.25),
                     ('fierte',35.,35.75),('final_hold',37.25,38.)]:
        scene_levels.append({'scene':name,'interval':[a,b],'mix':metric(mix[round(a*SR):round(b*SR)]),
                             'music_before_master':metric(music_data[round(a*SR):round(b*SR)])})
    punctuation_metadata={'absolute_cut_s':32.,'precut_fade_ms':6.,'total_zero_interval_s':[32.,32.5],
        'exact_zero_samples_per_channel':cut_b-cut_a,'restart_edge_ms':8.,
        'terminal_silence_interval_s':[37.25,38.],'terminal_edge_ms':32.,
        'method':'Absolute-time envelope applied to each cue before quantization; no scene normalization.'}
    provenance={'title':'Just cooking. Mostly washing. — V27 audio revision','revision':27,
        'duration_seconds':duration,'sample_rate':SR,'channels':2,'source_sha256':source_hashes['son.py'],
        'source_hashes':source_hashes,'music_source_sha256':source_hashes['music.py'],
        'foley_source_sha256':source_hashes['foley.py'],'chronologie_sha256':sha(TIMELINE),
        'source_bank_file':'source_bank_v26.json','source_bank_sha256':sha(OUT/'source_bank_v26.json'),
        'reference_events_file':'reference_events_v26.json','reference_events_sha256':sha(OUT/'reference_events_v26.json'),
        'motion_sync_file':'motion_sync_v26.json','motion_sync_sha256':sha(OUT/'motion_sync_v26.json'),
        'events':events,'mix_sha256':sha(OUT/'mix.wav'),'stems':stems,'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_gain_linear':gain,'delivery_target_lufs':None,
        'bank_levels':'Sum listed post-punctuation PCM cues at start_sample; 8/35ms global edge fade then round; fixed+3.50dB gain then round. No scene/master loudness normalization.',
        'background_music':parameters,'retained_v26_cues':equivalence,'replaced_v26_kind':['frying','background_music'],
        'paper_recording_provenance':'assets/paper_recordings/provenance.json',
        'vocal_sources_provenance':'assets/vocal_sources/provenance.json',
        'no_speech_intended':True,'vocal_semantics_verified_by_listening':False,'new_vocal_proposals':True,
        'no_detector_alarm':True,'visuals_changed':False,'punctuation':punctuation_metadata,
        'reproduction':'.venv/bin/python -B episodes/03/cuisine_v27/sources/son.py','limits':LIMITS}
    atomic_json(OUT/'provenance.json',provenance)
    audit={'revision':27,'duration_seconds':duration,'sample_rate':SR,'channels':2,'samples_per_channel':n,
        'expected_video_frames':912,'fps':24,'source_hashes':source_hashes,'chronologie_sha256':sha(TIMELINE),
        'mix_sha256':sha(OUT/'mix.wav'),'test_final_sha256':sha(OUT/'test_fin_v27.wav'),
        'test_final_seconds':[30.,38.],'event_count':len(events),'paper_event_count':len(papers),
        'vocal_event_count':len(voices),'supplemental_event_count':len(extra),
        'retained_v26_event_count':len(equivalence),'retained_v26_pcm_and_timing':equivalence,
        'delivery_gain_db':DELIVERY_GAIN_DB,'delivery_target_lufs':None,'global_normalization_mode':'Fixed+3.50dB gain only',
        'punctuation':punctuation_metadata,'pregain_metrics':metric(before),'mix_metrics':metric(mix),
        'input_loudness':loudness(OUT/'mix.wav'),'background_music':parameters,'scene_levels':scene_levels,
        'stems':stems,'motion_sync':motion,'clipped_samples':0,'limits':LIMITS}
    atomic_json(EP/'controle/audit_son.json',audit)
    atomic_json(EP/'controle/audit_audio_v27.json',audit)
    print(json.dumps({'mix':str(OUT/'mix.wav'),'seconds':duration,'events':len(events),
        'retained_v26':len(equivalence),'vocal_events':len(voices),'supplemental_events':len(extra),
        'mix_metrics':metric(mix),'loudness':audit['input_loudness'],
        'exact_zero_interval_seconds':[32.,32.5],'final_hold_silence_seconds':[37.25,38.]},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
