"""V25 recorded-paper adaptations, exact visual intervals and documented sources.

No new noise synthesis. All cuts are local original sample excerpts. The
palette is a proposal; no previous sound trial is treated as user approval.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
SR=48000
ASSETS=Path(__file__).resolve().parents[1]/'assets/paper_recordings'
MOTION_SYNC={1:[11.74576,12.05567],2:[19.87547,20.17028],
             3:[25.56459,25.80354],4:[31.44576,31.75567],
             5:[37.377,37.820]}


def run(arguments):return subprocess.check_output(arguments,stderr=subprocess.PIPE)

def edge_fade(n,attack=.008,release=.035):
    envelope=np.ones(n);a=min(n,round(attack*SR));b=min(n,round(release*SR))
    envelope[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    envelope[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return envelope

def recording_excerpt(item,offset,duration,attack,release,old_metrics):
    # Resample/channel conversion, DC removal and short fades preserve the
    # recording's broad spectrum. A gentle2:1 compressor above4x source RMS
    # handles isolated high-crest transients. One fixed RMS-match gain is
    # bounded by the previous cue peak+3dB. No synthesis, loop, time stretch,
    # low-pass or denoiser is applied.
    decoded=np.frombuffer(run(['ffmpeg','-v','error','-i',str(item['resolved']),
        '-ar',str(SR),'-ac','2','-c:a','pcm_f32le','-f','f32le','-']),'<f4').reshape(-1,2).astype(float)
    start=round(offset*SR);n=round(duration*SR)
    assert start>=0 and start<len(decoded),('Recording offset outside file',item['id'])
    used=min(n,len(decoded)-start)
    excerpt=decoded[start:start+used].copy()
    assert np.isfinite(excerpt).all()
    raw_peak=float(np.abs(excerpt).max())
    raw_activity=np.flatnonzero(np.max(np.abs(excerpt),axis=1)>raw_peak*.02)
    assert len(raw_activity)>0
    dc=excerpt.mean(axis=0);excerpt-=dc[None,:]
    excerpt*=edge_fade(used,attack,release)[:,None]
    source_rms=float(np.sqrt(np.mean(excerpt**2)))
    threshold=max(4.*source_rms,1e-7)
    detector=np.max(np.abs(excerpt),axis=1)
    attack_coefficient=np.exp(-1./(.002*SR));release_coefficient=np.exp(-1./(.040*SR))
    envelope=0.;gain_reductions=np.ones(used)
    for index,value in enumerate(detector):
        coefficient=attack_coefficient if value>envelope else release_coefficient
        envelope=coefficient*envelope+(1.-coefficient)*value
        gain_reductions[index]=max(envelope/threshold,1.)**(-.5)
    excerpt*=gain_reductions[:,None]
    if used<n:excerpt=np.pad(excerpt,((0,n-used),(0,0)))
    peak=float(np.abs(excerpt).max());assert peak>1e-7,('Empty recording excerpt',item['id'])
    old_peak=10.**(float(old_metrics['peak_dbfs'])/20.)
    old_rms=10.**(float(old_metrics['rms_dbfs'])/20.)
    new_rms=float(np.sqrt(np.mean(excerpt**2)))
    rms_gain=old_rms/max(new_rms,1e-12)
    peak_gain=old_peak*10.**(3./20.)/peak
    gain=min(rms_gain,peak_gain)
    result=np.rint(excerpt*gain*32768.).astype(np.int32)
    assert np.abs(result).max()<32767
    result_activity=np.flatnonzero(np.max(np.abs(result),axis=1)>np.abs(result).max()*.02)
    processing={'recording_offset_seconds':offset,'output_duration_seconds':duration,
                'recording_duration_used_seconds':used/SR,'silence_tail_padding_seconds':(n-used)/SR,
                'raw_first_activity_above_2pct_peak_seconds':float(raw_activity[0]/SR),
                'processed_first_activity_above_2pct_peak_seconds':float(result_activity[0]/SR),
                'activity_measure_is_not_listening':True,
                'dc_removed_per_channel':dc.tolist(),'edge_fade_seconds':[attack,release],
                'resample_hz':SR,'channels':2,'lowpass_hz':None,
                'synthesis_or_looping_or_time_stretch':False,
                'compression':{'ratio':2.,'threshold_dbfs':float(20*np.log10(threshold)),
                               'threshold_relative_to_source_rms_db':float(20*np.log10(4.)),
                               'attack_ms':2.,'release_ms':40.,
                               'maximum_gain_reduction_db':float(-20*np.log10(gain_reductions.min()))},
                'fixed_gain_db':float(20*np.log10(gain)),
                'gain_policy':'Match old cue RMS, bounded by old peak+3dB',
                'rms_db_change_from_old_cue':float(20*np.log10((new_rms*gain)/old_rms)),
                'peak_db_change_from_old_cue':float(20*np.log10(peak*gain/old_peak)),
                'result_peak_dbfs':float(20*np.log10(np.abs(result).max()/32768.))}
    return result,processing

def sources():
    manifest=ASSETS/'provenance.json';data=json.loads(manifest.read_text());result={}
    for item in data['sources']:
        local=dict(item)
        for key,digest_key in [('path','sha256'),('licence_file','licence_sha256'),('evidence_file','evidence_sha256')]:
            p=(ASSETS/item[key]).resolve();assert p.is_relative_to(ASSETS.resolve()) and p.is_file()
            assert hashlib.sha256(p.read_bytes()).hexdigest()==item[digest_key]
            if key=='path':local['resolved']=p
        assert item['licence'] in ('MIT','CC0-1.0')
        result[item['id']]=local
    return result,data


def cues(timeline,reference_events):
    library,source_provenance=sources();old={e['name']:e for e in reference_events};result=[]
    def cue(previous,source_id,offset,start,duration,interval,sync):
        prior=old[previous];item=library[source_id]
        assert interval[0]-1e-7<=start and start+duration<=interval[1]+1e-7,(previous,start,duration,interval)
        attack=.008 if 'wipe' in prior['kind'] else .002 if 'tear' in prior['kind'] or 'land' in prior['kind'] or 'floor' in prior['kind'] else .005
        release=.015 if 'land' not in prior['kind'] else .020
        signal,processing=recording_excerpt(item,offset,duration,attack,release,prior['actual_metrics'])
        name=previous.replace('_v24','')+'_v25'
        meta={'name':name,'kind':prior['kind'],'cycle':prior.get('cycle'),
              'start':start,'duration':len(signal)/SR,'replaces_event':previous,
              'original_event_sha256':prior['sha256'],'source_id':source_id,
              'source_recording_file':'assets/paper_recordings/'+item['path'],
              'source_recording_sha256':item['sha256'],'source_url':item['source_url'],
              'source_licence':item['licence'],'source_description':item['description'],
              'recording_method_verified':item['recording_method_verified'],
              'recording_method_note':item['recording_method_note'],
              'processing':processing,'sync':{'action_interval':interval,**sync}}
        result.append((meta,signal))
    for c in timeline['cycles']:
        number=int(c['id']);tiny=bool(c.get('tiny'));a,b=c['pull']
        if tiny:
            duration=.14;start=a+.42*(b-a);offset=.22
        else:
            duration=min(.34,.98*(b-a)*.58);start=a+.42*(b-a)
            offset=(.04,.06,.05,.08)[number-1]
        cue(f'c{number}_papier_deroule','flatten01',offset,start,duration,c['pull'],
            {'target':'actual paper drag inside pull phase','starts_at_pull_fraction':.42})
        tear_duration=(.20,.18,.14,.20,.12)[number-1]
        cue(f'c{number}_papier_dechire','cardboardtear',(.0,.005,.02,.0,.03)[number-1],c['tear'],tear_duration,
            (c['tear'],c['wipe'][1]),{'target':'visible tear contact','contact_seconds':c['tear']})
        for j,centre in enumerate(MOTION_SYNC[number],1):
            duration=.24 if number==3 else .26
            source_id='flatten01' if (number+j)%2==0 else 'flatten02'
            offset=(.12+.01*(number%3)) if source_id=='flatten01' else (.04+.01*(number%3))
            cue(f'c{number}_essuyage_{j}_v24',source_id,offset,centre-duration/2.,duration,c['wipe'],
                {'target':'actual relative mitten speed peak','centre_seconds':centre,
                 'trajectory_preserved_from_v24':True,'method':'Fixed world grips retained; main speed peaks sampled from V24. Last pair uses earlier main peaks to fit longer recorded strokes.'})
        a,b=c['crumple']
        cue(f'c{number}_froissage_v24','paperscraps',.65+.05*number,a,b-a,c['crumple'],
            {'target':'visible paper compression','material_adaptation':'Paper Scraps library texture; exact recorded gesture and recording method unknown'})
        previous=f'c{number}_poubelle_impact'+('_v24' if number in (2,3,4) else '')
        offset=(.0,.18,.30,.005,.20)[number-1];duration=.12 if tiny else .16
        cue(previous,'flatten02',offset,c['land'],duration,(c['land'],c['throw'][1]),
            {'target':'paper reaches bin','contact_seconds':c['land'],
             'material_adaptation':'recorded palm/paper contact adapted as soft paper landing'})
    when=float(timeline['overflow']['floor_land'])
    cue('c5_papier_sol','flatten02',.31,when,.12,(when,40.25),
        {'target':'last paper reaches floor','contact_seconds':when,
         'material_adaptation':'recorded paper/palm contact adapted as floor contact'})
    assert len(result)==31 and len({x[0]['replaces_event'] for x in result})==31
    return result,source_provenance

