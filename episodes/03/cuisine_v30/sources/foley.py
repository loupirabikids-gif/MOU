"""V26 recorded-paper adaptations, exact visual intervals and documented sources.

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
# Fallback centres follow the same native relative-moufle motion fractions.
# A later motion_sync_v26.json generated from the final rig states supersedes them.
MOTION_FRACTIONS={1:[.40678,.77138],2:[.41,.79],3:[.32,.77],4:[.44385,.78462]}
TARGETS={
 'paper_pull':(-41.,-29.),'paper_tear':(-41.,-28.5),
 'paper_wipe':(-42.5,-29.5),'paper_crumple':(-45.,-31.),'paper_land':(-44.,-30.5),
 'tiny_paper_pull':(-43.,-31.),'tiny_paper_tear':(-43.,-31.5),
 'tiny_paper_wipe':(-44.,-31.),'tiny_paper_crumple':(-46.,-32.),
 'tiny_paper_land':(-46.,-33.),'tiny_paper_floor':(-48.,-34.)}



def run(arguments):return subprocess.check_output(arguments,stderr=subprocess.PIPE)

def edge_fade(n,attack=.008,release=.035):
    envelope=np.ones(n);a=min(n,round(attack*SR));b=min(n,round(release*SR))
    envelope[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    envelope[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return envelope

def recording_excerpt(item,offset,duration,attack,release,target_metrics):
    # Resample/channel conversion, DC removal and short fades preserve the
    # recording's broad spectrum. A gentle2:1 compressor above4x source RMS
    # handles isolated high-crest transients. One fixed per-type RMS gain is
    # bounded by the per-type peak reference+3dB. No synthesis, loop, time stretch,
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
    target_peak=10.**(float(target_metrics['peak_dbfs'])/20.)
    target_rms=10.**(float(target_metrics['rms_dbfs'])/20.)
    new_rms=float(np.sqrt(np.mean(excerpt**2)))
    rms_gain=target_rms/max(new_rms,1e-12)
    peak_gain=target_peak*10.**(3./20.)/peak
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
                'gain_policy':'One fixed target per action type, bounded by target peak+3dB; no live mix normalization',
                'rms_db_change_from_type_target':float(20*np.log10((new_rms*gain)/target_rms)),
                'peak_db_change_from_type_reference':float(20*np.log10(peak*gain/target_peak)),
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
    library,source_provenance=sources()
    old={e['name']:e for e in reference_events};result=[]
    sync_path=Path(__file__).resolve().parents[1]/'audio/motion_sync_v26.json'
    measured=json.loads(sync_path.read_text()) if sync_path.exists() else {}
    def cue(previous,cycle,source_id,offset,start,duration,interval,sync,kind=None):
        prior=old[previous];item=library[source_id];kind=kind or prior['kind']
        assert interval[0]-1e-7<=start and start+duration<=interval[1]+1e-7,(previous,start,duration,interval)
        attack=.008 if 'wipe' in kind else .002 if 'tear' in kind or 'land' in kind or 'floor' in kind else .005
        release=.015 if 'land' not in kind else .020
        target_rms,target_peak=TARGETS[kind]
        signal,processing=recording_excerpt(item,offset,duration,attack,release,{'rms_dbfs':target_rms,'peak_dbfs':target_peak})
        name=f"c{cycle}_{kind}_v26_{len(result):02d}"
        meta={'name':name,'kind':kind,'cycle':cycle,'start':start,'duration':len(signal)/SR,
              'reference_event':previous,'original_event_sha256':prior['sha256'],
              'source_id':source_id,'source_recording_file':'assets/paper_recordings/'+item['path'],
              'source_recording_sha256':item['sha256'],'source_url':item['source_url'],
              'source_licence':item['licence'],'source_description':item['description'],
              'recording_method_verified':item['recording_method_verified'],
              'recording_method_note':item['recording_method_note'],
              'fixed_type_target_rms_dbfs':target_rms,'fixed_type_reference_peak_dbfs':target_peak,
              'processing':processing,'sync':{'action_interval':interval,**sync}}
        result.append((meta,signal))
    for c in timeline['cycles']:
        number=int(c['id']);previous_number=5 if number==4 else number;tiny=number==4
        a,b=c['pull'];span=b-a;duration=min(.28,span*.66)
        start=a+min(span-duration,span*.20)
        cue(f'c{previous_number}_papier_deroule',number,'flatten01',(.04,.06,.05,.22)[number-1],start,duration,c['pull'],{'target':'paper drag visible inside pull phase'})
        tear_duration=min((.16,.14,.12,.12)[number-1],(c['wipe'][1]-c['tear'])*.7)
        cue(f'c{previous_number}_papier_dechire',number,'cardboardtear',(.0,.005,.02,.03)[number-1],c['tear'],tear_duration,(c['tear'],c['wipe'][1]),{'target':'visible tear contact','contact_seconds':c['tear']})
        a,b=c['wipe'];span=b-a
        measured_cycle=measured.get('cycles',{}).get(str(number),{})
        centres=measured_cycle.get('centres_seconds',[a+f*span for f in MOTION_FRACTIONS[number]])
        for j,centre in enumerate(centres,1):
            duration=min(.20,span*.28,2.*(centre-a),2.*(b-centre))
            source_id='flatten01' if (number+j)%2==0 else 'flatten02'
            offset=(.12+.01*(number%3)) if source_id=='flatten01' else (.04+.01*(number%3))
            cue(f'c{previous_number}_essuyage_{j}_v24',number,source_id,offset,centre-duration/2.,duration,c['wipe'],
                {'target':'relative mitten motion peak','centre_seconds':centre,
                 'method':measured_cycle.get('method','Mapped native-motion fraction; to verify against final V26 states'),
                 'trajectory_measurement':bool(measured_cycle)})
        a,b=c['crumple']
        cue(f'c{previous_number}_froissage_v24',number,'paperscraps',.65+.05*number,a,b-a,c['crumple'],{'target':'visible paper compression','material_adaptation':'Paper Scraps library texture; exact recorded gesture and method unknown'})
        previous=f'c{previous_number}_poubelle_impact'+('_v24' if previous_number in (2,3,4) else '')
        duration=.12 if tiny else .16
        cue(previous,number,'flatten02',(.0,.18,.30,.20)[number-1],c['land'],duration,(c['land'],c['throw'][1]),{'target':'paper reaches heap','contact_seconds':c['land'],'material_adaptation':'recorded palm/paper contact adapted as paper landing'})
    when=float(timeline['paper_overflow']['floor_land'])
    cue('c5_papier_sol',4,'flatten02',.31,when,.12,(when,30.25),{'target':'last paper reaches floor','contact_seconds':when,'material_adaptation':'recorded palm/paper contact adapted as floor landing'})
    assert len(result)==25
    return result,source_provenance
