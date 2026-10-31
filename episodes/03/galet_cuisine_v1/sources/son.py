"""Rebuild Galet's soft kitchen mix from local, credited source cues.

The input bank comes from the existing project sound work. No new filtered-noise
Foley or unapproved character voice is generated. A constant music trim and a
constant delivery gain are applied; there is no scene normalization or AGC.
"""
from __future__ import annotations

import argparse
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
SR=48000
MUSIC_GAIN_DB=-1.5
DELIVERY_GAIN_DB=3.5
LIMITS=('No model listening is available. Waveform timing, reproducibility and '
        'levels do not establish perceived naturalness, comfort or comic success.')


def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()


def write_json(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def pcm(path):
    with wave.open(str(path),'rb')as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2),path
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    arr=np.asarray(data,dtype=np.int64)
    assert arr.ndim==2 and arr.shape[1]==2 and np.abs(arr).max()<32767,path
    fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent);os.close(fd)
    try:
        with wave.open(temp,'wb')as f:
            f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
            f.writeframes(arr.astype('<i2').tobytes())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def db(x):return float(20.*np.log10(max(float(x),1e-15)))


def metrics(data):
    x=np.asarray(data,dtype=np.float64)/32768.
    return {'peak_dbfs':db(np.abs(x).max()),'rms_dbfs':db(np.sqrt(np.mean(x*x))),
            'clipped_samples':int(np.count_nonzero(np.abs(np.asarray(data,dtype=np.int64))>=32767))}


def energy_anchor(data):
    """Reproducible 8 ms RMS peak; an energy marker, not an audibility claim."""
    x=np.asarray(data,dtype=np.float64)/32768.
    power=np.mean(x*x,axis=1);window=min(len(x),round(.008*SR))
    integral=np.r_[0.,np.cumsum(power)]
    averaged=(integral[window:]-integral[:-window])/window
    return int(np.argmax(averaged)+window//2)


def envelope(start,n):
    time=start+np.arange(n,dtype=np.float64)/SR;gain=np.ones(n)
    edge=(time>=31.994)&(time<32.)
    gain[edge]*=np.cos((time[edge]-31.994)/.006*np.pi/2.)**2
    gain[(time>=32.)&(time<32.5)]=0.
    edge=(time>=32.5)&(time<32.508)
    gain[edge]*=np.sin((time[edge]-32.5)/.008*np.pi/2.)**2
    edge=(time>=37.218)&(time<37.25)
    gain[edge]*=np.cos((time[edge]-37.218)/.032*np.pi/2.)**2
    gain[time>=37.25]=0.
    gain*=np.sin(np.minimum(1.,np.maximum(0.,time/.008))*np.pi/2.)**2
    return gain


def measure_motion(timeline):
    """Measure the new rendered hand trajectories, only when explicitly asked."""
    source=EP/'sources';paths=[source/n for n in ('animation.py','character.py','reference_character.py')]
    assert all(p.is_file()for p in paths),'New character animation is not ready for sound synchronization'
    frozen={p.name:sha(p)for p in paths};sys.path.insert(0,str(source))
    spec=importlib.util.spec_from_file_location('galet_sound_actual_motion',source/'animation.py')
    animation=importlib.util.module_from_spec(spec);sys.modules[spec.name]=animation;spec.loader.exec_module(animation)
    import character
    result={'method':'240 fresh scene states per wipe, true world fingertip coordinates; two relative-velocity maxima after the approach, numerical only',
            'source_hashes':frozen,'cycles':{}}
    for cycle in timeline['cycles']:
        a,b=cycle['wipe'];times=np.linspace(a,b,240,endpoint=False);relative=[]
        for t in times:
            state=animation.scene_state(float(t));points={}
            for side in ('left','right'):
                hand=state['hands'][side]
                points[side]=np.array(character.point(hand,'tip')if isinstance(hand,dict)else hand)
            relative.append(points['right']-points['left'])
        speed=np.linalg.norm(np.gradient(np.array(relative),times,axis=0),axis=1)
        candidates=[i for i in range(1,len(times)-1)
                    if speed[i]>=speed[i-1] and speed[i]>speed[i+1]
                    and a+.26*(b-a)<=times[i]<=b-.04*(b-a)]
        chosen=[]
        for i in sorted(candidates,key=lambda j:speed[j],reverse=True):
            if all(abs(times[i]-times[j])>=.20*(b-a)for j in chosen):chosen.append(i)
            if len(chosen)==2:break
        assert len(chosen)==2,(cycle['id'],'Two actual wipe accents were not identifiable')
        chosen.sort()
        result['cycles'][str(cycle['id'])]={'action_interval':[a,b],
            'centres_seconds':[float(times[i])for i in chosen],
            'speed_pixels_per_second':[float(speed[i])for i in chosen]}
    assert frozen=={p.name:sha(p)for p in paths},'Animation changed during sound synchronization'
    return result


def placement(item,timeline,motion,anchor):
    name,kind=item['source_name'],item['kind'];start=float(item['source_start'])
    cycle_match=re.match(r'c([1-4])_',name)
    c=timeline['cycles'][int(cycle_match[1])-1]if cycle_match else None
    target=None;method='Existing source cue mapped to the shared scene clock'
    if kind=='carrot_chop':target=timeline['carrot']['cut_times'][int(re.search(r'coupe_([12])',name)[1])-1]
    elif kind=='knife_setdown':target=timeline['carrot']['knife_park']
    elif kind=='tomato_contact':target=timeline['cooking_events']['tomato_contact']
    elif kind=='tap' and c:target=c['water'][0 if'ouvre'in name else 1]
    elif kind in ('paper_tear','tiny_paper_tear')and c:target=c['tear']
    elif kind in ('paper_land','tiny_paper_land')and c:target=c['land']
    elif kind=='tiny_paper_floor':target=timeline['paper_overflow']['floor_land']
    elif kind in ('paper_wipe','tiny_paper_wipe')and c:
        peers=[i for i in BANK['inputs']if i['kind']in('paper_wipe','tiny_paper_wipe')
               and i['source_name'].startswith(f'c{c["id"]}_')]
        peers.sort(key=lambda i:i['source_start']);j=next(j for j,p in enumerate(peers)if p['source_name']==name)
        measured=motion.get('cycles',{}).get(str(c['id']),{})
        if measured:
            target=measured['centres_seconds'][j]
            method='New galet world relative-fingertip speed maximum matched to this cue 8 ms RMS energy peak'
        else:
            target=(item.get('source_sync')or{}).get('centre_seconds',start+item['source_duration']/2.)
            method='Provisional inherited timing marker; not measured on the new character yet'
    if target is not None:
        start=float(target)-anchor/SR
        if kind in ('paper_wipe','tiny_paper_wipe')and c:
            start=max(c['wipe'][0],start)
        return max(0.,start),{'target_seconds':float(target),'marker':'8 ms RMS energy peak',
                              'method':method,'audio_marker_is_not_listening':True}
    return start,{'method':method,'audio_marker_is_not_listening':True}


def loudness(path):
    p=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af',
                      'loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return {k:v for k,v in json.loads(re.findall(r'\{[\s\S]*?\}',p.stderr.decode())[-1]).items()
            if k.startswith('input_')}


BANK={}


def main():
    global BANK
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sync-motion',action='store_true',help='Measure the frozen new animation before rebuilding the mix')
    args=ap.parse_args();timeline_path=EP/'chronologie.json';timeline=json.loads(timeline_path.read_text())
    assert timeline['duration']==38. and timeline['fps']==24
    BANK=json.loads((OUT/'input_bank.json').read_text());n=round(SR*timeline['duration'])
    assert len(BANK['inputs'])==58 and all(i['kind']!='mou_nonverbal'for i in BANK['inputs'])
    if args.sync_motion:
        motion=measure_motion(timeline);write_json(OUT/'motion_sync.json',motion)
    else:
        motion=json.loads((OUT/'motion_sync.json').read_text())if(OUT/'motion_sync.json').exists()else{}
    frozen={'son.py':sha(Path(__file__)),'input_bank.json':sha(OUT/'input_bank.json'),'chronologie.json':sha(timeline_path)}
    stems={key:np.zeros((n,2),dtype=np.int64)for key in ('music','foley','ambience')};events=[]
    for item in BANK['inputs']:
        path=OUT/item['file'];assert sha(path)==item['sha256'],path
        data=pcm(path);assert len(data)==item['source_samples']
        anchor=energy_anchor(data);start,sync=placement(item,timeline,motion,anchor)
        edit={'source_offset_samples':0,'source_samples':len(data),'tail_trimmed_samples':0}
        if item['kind']in('paper_wipe','tiny_paper_wipe'):
            number=int(re.match(r'c([1-4])_',item['source_name'])[1]);end=timeline['cycles'][number-1]['wipe'][1]
            available=min(len(data),round((end-start)*SR))
            if available<len(data):
                edit['tail_trimmed_samples']=len(data)-available;data=data[:available].copy()
                tail=min(round(.008*SR),max(2,available-anchor-2))
                data[-tail:]=np.rint(data[-tail:]*np.cos(np.linspace(0.,np.pi/2.,tail))[:,None]**2).astype(np.int16)
        category='music'if item['kind']=='background_music'else'ambience'if item['kind']=='room_ambience'else'foley'
        gain_db=DELIVERY_GAIN_DB+(MUSIC_GAIN_DB if category=='music'else 0.)
        rendered=np.rint(data.astype(np.float64)*10.**(gain_db/20.)*envelope(start,len(data))[:,None]).astype(np.int64)
        begin=round(start*SR);assert begin>=0 and begin+len(rendered)<=n,(item['source_name'],start,len(rendered)/SR)
        name=item['source_name'];out=OUT/'cues'/f'{name}.wav';write_pcm(out,rendered)
        stems[category][begin:begin+len(rendered)]+=rendered
        final_anchor=energy_anchor(rendered)
        event={'name':name,'kind':item['kind'],'file':out.relative_to(OUT).as_posix(),
               'source_file':item['file'],'source_sha256':item['sha256'],
               'sha256':sha(out),'start':begin/SR,'start_sample':begin,'samples':len(rendered),
               'duration':len(rendered)/SR,'stem':category,'fixed_gain_db':gain_db,
               'energy_peak_sample':final_anchor,'energy_peak_seconds':(begin+final_anchor)/SR,
               'sync':sync,'source_edit':edit,'metrics':metrics(rendered),'voice':False}
        if 'target_seconds'in sync:event['energy_sync_error_ms']=1000.*((begin+final_anchor)/SR-sync['target_seconds'])
        events.append(event)
    mix=sum(stems.values());assert np.abs(mix).max()<32767
    assert not mix[32*SR:round(32.5*SR)].any()and not mix[round(37.25*SR):].any()
    for key,data in stems.items():write_pcm(OUT/'stems'/f'{key}.wav',data)
    write_pcm(OUT/'mix.wav',mix);write_pcm(OUT/'test_fin.wav',mix[30*SR:])
    events.sort(key=lambda e:(e['start_sample'],e['name']))
    bank_summary={k:BANK[k]for k in ('source_original_commit','source_provenance_sha256','source_mix_sha256')}
    result={'title':'Just cooking. Mostly washing. — Galet cuisine','duration_seconds':38.,'sample_rate':SR,
            'channels':2,'samples_per_channel':n,'events':events,'event_count':len(events),
            'vocal_event_count':0,'source_bank':bank_summary,'source_hashes':frozen,
            'mix_sha256':sha(OUT/'mix.wav'),'test_final_sha256':sha(OUT/'test_fin.wav'),
            'delivery_gain_db':DELIVERY_GAIN_DB,'music_relative_gain_db':MUSIC_GAIN_DB,
            'gain_policy':'One fixed per-category trim plus one constant delivery gain; no scene normalization, no AGC and no whole-track time shift.',
            'silences':[[32.,32.5],[37.25,38.]],'music_cut_seconds':32.,'final_note_window':[36.25,36.75],
            'motion_sync_status':'measured_new_character'if motion else'pending_new_character_motion',
            'metrics':metrics(mix),'input_loudness':loudness(OUT/'mix.wav'),'limits':LIMITS,
            'stems':[{ 'stem':key,'file':f'stems/{key}.wav','sha256':sha(OUT/'stems'/f'{key}.wav'),
                      'metrics':metrics(data)}for key,data in stems.items()],
            'reproduction':'python sources/son.py; add --sync-motion only after the final animation is frozen',
            'source_provenance_scope':'source_provenance_v27.json is historical evidence, not an active list of required file paths; input_bank.json is the complete active source bank.'}
    write_json(OUT/'events.json',result);write_json(OUT/'provenance.json',result)
    levels=[]
    for label,a,b in [('cook',0.2,2.6),('wash1',3.9,5.35),('wash2',11.3,12.4),('wash3',16.5,17.45),
                      ('wash4',23.25,24.2),('shock',31.5,32.),('silence',32.,32.5),
                      ('lost',32.5,33.25),('proud',35.,35.75),('hold',37.25,38.)]:
        sample=slice(round(a*SR),round(b*SR));levels.append({'scene':label,'interval':[a,b],
                  'mix':metrics(mix[sample]),'music':metrics(stems['music'][sample]),'foley':metrics(stems['foley'][sample])})
    audit={'status':'passed','sample_rate':SR,'channels':2,'duration_seconds':38.,'samples_per_channel':n,
           'event_count':len(events),'voice_count':0,'mix_sha256':sha(OUT/'mix.wav'),'metrics':metrics(mix),
           'constant_delivery_gain_db':DELIVERY_GAIN_DB,'music_relative_gain_db':MUSIC_GAIN_DB,
           'exact_silence_intervals':[[32.,32.5],[37.25,38.]],'stem_sum_equals_mix_pcm':True,
           'opening_whistle_events':[{k:e[k]for k in ('name','start','duration')}for e in events if e['kind']=='whistle'],
           'scene_levels':levels,'input_loudness':result['input_loudness'],'motion_sync_status':result['motion_sync_status'],
           'limits':LIMITS}
    assert frozen=={'son.py':sha(Path(__file__)),'input_bank.json':sha(OUT/'input_bank.json'),'chronologie.json':sha(timeline_path)}
    assert np.array_equal(sum(pcm(OUT/'stems'/f'{k}.wav').astype(np.int64)for k in stems),pcm(OUT/'mix.wav'))
    write_json(EP/'controle/audit_son.json',audit)
    print(json.dumps({'mix':str(OUT/'mix.wav'),'events':len(events),'duration':38.,'voice_count':0,
                      'metrics':result['metrics'],'motion_sync_status':result['motion_sync_status'],
                      'loudness':result['input_loudness']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
