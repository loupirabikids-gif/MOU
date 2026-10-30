"""Controlled first-paper-cycle material trial from V24, no production edits.

Requires a coordinator-approved assets/selection.json manifest with verified
recording provenance and licence evidence. It does not fetch or invent assets.
A preserves the V24 mix; B replaces only six first-cycle paper cues. Shared
video, music, ambience, other events and global delivery gain stay identical.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT=Path(__file__).resolve().parent
EP=ROOT/'episodes/03/cuisine_v24'
WORK=ROOT/'work/papier_foley_v1'
SR=48000;FPS=24;START=10.25;END=13.5;DURATION=END-START
EXPECTED={
    'c1_papier_deroule':(10.99,.34,.005,.020),
    'c1_papier_dechire':(11.4,.22,.002,.015),
    'c1_essuyage_1_v24':(11.74576-.13,.26,.008,.015),
    'c1_essuyage_2_v24':(12.05567-.13,.26,.008,.015),
    'c1_froissage_v24':(12.25,.35,.005,.015),
    'c1_poubelle_impact':(13.22,.20,.002,.020),
}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(arguments):return subprocess.check_output(arguments,stderr=subprocess.PIPE)


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert(source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,signal):
    data=np.asarray(signal,dtype=np.int32)
    assert data.ndim==2 and data.shape[1]==2 and np.abs(data).max()<32767
    with wave.open(str(path),'wb') as target:
        target.setnchannels(2);target.setsampwidth(2);target.setframerate(SR)
        target.writeframes(data.astype('<i2').tobytes())


def atomic_json(path,data):
    fd,temp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    with os.fdopen(fd,'w') as target:target.write(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    os.replace(temp,path)


def edge_fade(n,attack=.008,release=.035):
    envelope=np.ones(n);a=min(n,round(attack*SR));b=min(n,round(release*SR))
    envelope[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    envelope[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return envelope


def local_file(name):
    path=(OUT/name).resolve()
    assert path.is_relative_to(OUT) and path.is_file(),('Trial asset must be included locally',name)
    return path


def approved_sources(selection):
    approval=selection.get('approval',{})
    assert approval.get('approved_by')=='/root' and approval.get('use_verified_sources') is True, 'Await coordinator source approval'
    sources={}
    for item in selection['sources']:
        assert item['id'] not in sources
        source=local_file(item['path']);assert sha(source)==item['sha256']
        assert item['licence'] in ('MIT','CC0-1.0','CC0','Public Domain'),item['licence']
        for kind in ('licence','evidence'):
            path=local_file(item[kind+'_file']);assert sha(path)==item[kind+'_sha256']
        assert item['source_url'] and item['description']
        assert isinstance(item['recording_method_verified'],bool)
        assert item['recording_method_note']
        sources[item['id']]={**item,'resolved':source}
    return sources


def recording_excerpt(item,offset,duration,attack,release,old_pcm):
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
    old_peak=float(np.abs(old_pcm.astype(np.int32)).max())/32768.
    old_rms=float(np.sqrt(np.mean((old_pcm.astype(float)/32768.)**2)))
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


def video_digest(path):
    data=run(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy',
              '-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def inspect(path,expected_pcm):
    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(path)]))
    assert len(probe['streams'])==2
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    a=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1080,1920,'24/1',78)
    assert abs(float(v['duration'])-DURATION)<.001
    assert(a['codec_name'],int(a['sample_rate']),int(a['channels']))==('aac',SR,2)
    assert abs(float(a['duration'])-DURATION)<.001
    run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(path),'-f','null','-'])
    decoded=np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
        '-t',str(DURATION),'-c:a','pcm_f32le','-f','f32le','-']),'<f4').astype(float)
    reference=expected_pcm.astype(float).ravel()/32768.
    assert decoded.shape==reference.shape and np.isfinite(decoded).all() and np.abs(decoded).max()<.999
    correlation=float(np.dot(decoded,reference)/np.sqrt(np.dot(decoded,decoded)*np.dot(reference,reference)))
    assert correlation>.9
    return {'file':path.name,'sha256':sha(path),'bytes':path.stat().st_size,
            'dimensions':[1080,1920],'fps':24,'frames':78,'duration_seconds':DURATION,
            'video_bitstream':video_digest(path),'full_decode_without_errors':True,
            'audio_aac_correlation_to_own_pcm':correlation,'pcm_clipped_samples':0,
            'decoded_aac_peak_dbfs':float(20*np.log10(np.abs(decoded).max()))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection',type=Path,default=OUT/'assets/selection.json')
    args=parser.parse_args()
    selection_path=args.selection.resolve();selection=json.loads(selection_path.read_text())
    sources=approved_sources(selection)
    cues={c['replace_name']:c for c in selection['cues']};assert set(cues)==set(EXPECTED)
    WORK.mkdir(parents=True,exist_ok=True)
    video=EP/'MOU_Encore_une_feuille_muette.mp4';mix_path=EP/'audio/mix.wav';prov_path=EP/'audio/provenance.json'
    protected=[video,mix_path,prov_path]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
    provenance=json.loads(prov_path.read_text());assert provenance['duration_seconds']==43.
    assert provenance['delivery_gain_db']==3.5
    n=round(43*SR);start,end=round(START*SR),round(END*SR)
    original_full=pcm(mix_path);assert original_full.shape==(n,2)
    a=original_full[start:end].astype(np.int32);assert a.shape==(156000,2)
    unchanged_sum=np.zeros((n,2),dtype=np.int32);b_sum=np.zeros_like(unchanged_sum)
    replacements=[];unchanged=[];music=None
    for event in provenance['events']:
        path=EP/'audio'/event['file'];assert sha(path)==event['sha256']
        data=pcm(path).astype(np.int32);offset=event['start_sample'];assert offset+len(data)<=n
        if event['name'] not in EXPECTED:
            unchanged_sum[offset:offset+len(data)]+=data
            b_sum[offset:offset+len(data)]+=data
            unchanged.append({'name':event['name'],'file':event['file'],'sha256':event['sha256'],
                              'start_sample':offset,'samples':len(data),'extra_gain_db':0.})
            if event['kind']=='background_music':music=unchanged[-1]
            continue
        cue=cues[event['name']];item=sources[cue['source_id']]
        time,duration,attack,release=EXPECTED[event['name']]
        new,processing=recording_excerpt(item,float(cue['offset_seconds']),duration,attack,release,data)
        offset=round(time*SR);b_sum[offset:offset+len(new)]+=new
        write_pcm(WORK/f"{event['name']}_recorded.wav",new)
        replacements.append({'replaced_event':event['name'],'original_file':event['file'],
                             'original_sha256':event['sha256'],'source_id':item['id'],
                             'source_recording_sha256':item['sha256'],'start_seconds':time,
                             'duration_seconds':duration,'start_sample':offset,'samples':len(new),
                             'processing':processing,'pcm_sha256':hashlib.sha256(new.astype('<i2').tobytes()).hexdigest()})
    assert len(replacements)==6 and len(unchanged)==52 and music is not None
    # One unaltered bed consists of the same music and all unreplaced V24
    # events. Changes are restricted to the six explicitly listed paper cues.
    gain=provenance['delivery_gain_linear'];envelope=edge_fade(n)[:,None]
    b_full=np.rint(np.rint(b_sum*envelope)*gain).astype(np.int32)
    assert np.abs(b_full).max()<32767
    b=b_full[start:end]
    for label,data in [('A',a),('B',b)]:write_pcm(WORK/f'{label}.wav',data)
    silent=WORK/'segment_muette.mp4'
    run(['ffmpeg','-y','-v','error','-threads','2','-i',str(video),'-map','0:v:0',
         '-vf','trim=start_frame=246:end_frame=324,setpts=PTS-STARTPTS','-an',
         '-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-r','24',
         '-threads','2','-movflags','+faststart',str(silent)])
    outputs={}
    for label,filename,data in [('A','A_papier_actuel.mp4',a),('B','B_nouvelle_matiere.mp4',b)]:
        temp=WORK/filename;destination=OUT/filename
        run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(WORK/f'{label}.wav'),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
             '-t',str(DURATION),'-movflags','+faststart',str(temp)])
        os.replace(temp,destination);outputs[label]=inspect(destination,data)
    assert outputs['A']['video_bitstream']==outputs['B']['video_bitstream']==video_digest(silent)
    assert frozen=={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
    # Explicitly verify that all samples outside replacement windows are
    # unchanged by the altered event set, including the same musical bed.
    changed=np.zeros(n,dtype=bool)
    for event in provenance['events']:
        if event['name'] in EXPECTED:changed[event['start_sample']:event['start_sample']+event['samples']]=True
    for replacement in replacements:changed[replacement['start_sample']:replacement['start_sample']+replacement['samples']]=True
    assert np.array_equal(b_full[~changed],original_full[~changed])
    source_records=[{k:v for k,v in item.items() if k!='resolved'} for item in sources.values()]
    audit={'status':'passed','purpose':'Short paper-material listening trial; no final-episode revision',
           'range_seconds':[START,END],'duration_seconds':DURATION,'frames':78,
           'source_video_frames_half_open':[246,324],'source_pcm_frames_half_open':[start,end],
           'sources_sha256':frozen,'production_sources_unchanged':True,
           'selection_sha256':sha(selection_path),'recording_sources':source_records,
           'outputs':outputs,'same_video_bitstreams':True,
           'A_exact_source_pcm_segment':True,
           'A_pcm_sha256':hashlib.sha256(a.astype('<i2').tobytes()).hexdigest(),
           'B_pcm_sha256':hashlib.sha256(b.astype('<i2').tobytes()).hexdigest(),
           'replaced_events':replacements,'unchanged_events':unchanged,
           'music_event_unchanged':music,'music_gain_change_db':0.,
           'ambience_and_other_event_gain_change_db':0.,'samples_outside_changed_windows_identical':True,
           'delivery_gain_db':3.5,'extra_mix_gain_or_normalization':False,
           'B_mix_recipe':'sum unchanged events and6 replacement PCM at start_sample; global8/35ms envelope; round; original fixed+3.50dB; round; slice',
           'new_noise_synthesis':False,'new_lowpass_processing':False,
           'intermediates':'Ignored work/papier_foley_v1',
           'reproduce_script_sha256':sha(__file__),
           'limits':'Technical provenance/source/timing checks only. No model listening, recognised-material or naturalness success claimed.'}
    atomic_json(OUT/'audit.json',audit)
    print(json.dumps({'status':'passed','outputs':outputs,'replaced_event_count':6,'music_gain_change_db':0.},indent=2))


if __name__=='__main__':main()
