"""Independent V27 sound-only checks against the exact V26 picture master.

Run after sources, PCM mix and muxed MP4 have been frozen. This checker does
not render or alter images, synthesize sound, or claim hearing or audience tests.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import wave
import numpy as np

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
SR=48000
DURATION=38.
FPS=24
NFRAMES=912
NSAMPLES=1824000
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
V26_SILENT_SHA='8190747fb4931221ba7f1e1968c1d795f813179f822eb8f33f81c1d3db9d4eeb'
VOICE_TIMES={
    'mou_hesitation':(21.98,.18),
    'mou_inspiration':(25.68,.16),
    'mou_choc':(31.76,.20),
    'mou_expiration':(32.78,.28),
    'mou_satisfaction':(35.15,.16),
}
LIMITS='Numerical sound/mux/source checks only. No listening, perceptual wordlessness, emotion recognition, comfort or audience success is certified.'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name,dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f:f.write(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def command(args):
    try:return subprocess.check_output(args,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'{args[0]} exited {e.returncode}: {e.stderr.decode(errors="replace")[-2500:]}') from e


def read_pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2),(str(path),'PCM format')
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def metric(data,integer=True):
    values=np.asarray(data,dtype=np.float64)/(32768. if integer else 1.)
    rms=float(np.sqrt(np.mean(values*values)))
    peak=float(np.abs(values).max())
    return {'rms_dbfs':20.*math.log10(max(rms,1.e-15)),
            'peak_dbfs':20.*math.log10(max(peak,1.e-15)),
            'nonzero_samples':int(np.count_nonzero(data))}


def probe_video(path,sound):
    info=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
    video=[v for v in info['streams'] if v['codec_type']=='video']
    audio=[v for v in info['streams'] if v['codec_type']=='audio']
    assert len(video)==1 and len(audio)==int(sound) and len(info['streams'])==1+int(sound),'Stream counts differ'
    v=video[0]
    assert (v['codec_name'],v['pix_fmt'],v['width'],v['height'])==('h264','yuv420p',1080,1920)
    assert Fraction(v['r_frame_rate'])==Fraction(v['avg_frame_rate'])==FPS
    assert int(v['nb_frames'])==int(v['nb_read_frames'])==NFRAMES
    assert abs(float(v['duration'])-DURATION)<.001
    assert abs(float(v.get('start_time',0)))<.001
    assert abs(float(info['format']['duration'])-DURATION)<.025
    if sound:
        a=audio[0]
        assert (a['codec_name'],int(a['sample_rate']),int(a['channels']))==('aac',SR,2)
        assert abs(float(a['duration'])-DURATION)<.025
    command(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(path),'-map','0','-f','null','-'])
    return {'file_sha256':digest(path),'bytes':path.stat().st_size,'full_decode_without_errors':True,
            'streams':[{k:s[k] for k in ('codec_type','codec_name','width','height','pix_fmt','r_frame_rate','avg_frame_rate',
               'nb_frames','nb_read_frames','duration','start_time','sample_rate','channels') if k in s} for s in info['streams']]}


def video_stream(path):
    raw=command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy',
                 '-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def video_timestamps(path):
    info=json.loads(command(['ffprobe','-v','error','-select_streams','v:0','-show_packets',
        '-show_entries','packet=pts_time,dts_time,duration_time','-of','json',str(path)]))
    packets=[(p['pts_time'],p['dts_time'],p['duration_time']) for p in info['packets']]
    assert len(packets)==NFRAMES
    encoded=json.dumps(packets,separators=(',',':')).encode()
    return packets,{'packets':len(packets),'timestamp_sha256':hashlib.sha256(encoded).hexdigest()}


def source_checks():
    assert digest(ROOT/'mou_rig.py')==RIG_SHA,'MOU rig changed'
    originals=json.loads((EP/'controle/baseline_protegee.json').read_text())
    verified={};unavailable=[]
    for name,expected in originals.items():
        path=ROOT/name
        if path.is_file():
            assert digest(path)==expected,('Protected original changed',name)
            verified[name]=expected
        else:unavailable.append(name)
    baseline=json.loads((EP/'controle/visual_sources_v26.json').read_text())
    assert len(baseline)>=15
    for name,expected in baseline.items():assert digest(EP/'sources'/name)==expected,('Visual source changed',name)
    old_timeline=ROOT/'episodes/03/cuisine_v26/chronologie.json'
    if old_timeline.is_file():assert digest(EP/'chronologie.json')==digest(old_timeline),'Visual timeline changed'
    audit=json.loads((EP/'controle/audit_son.json').read_text())
    hashes=audit.get('source_hashes')
    assert isinstance(hashes,dict),'Sound audit source_hashes missing'
    for required in ('son.py','music.py','foley_supplement.py','vocal.py'):
        assert required in hashes,('Sound audit omits producer',required)
    for name,expected in hashes.items():assert digest(EP/'sources'/name)==expected,('Sound source changed',name)
    assert audit['mix_sha256']==digest(EP/'audio/mix.wav'),'Mix differs from synthesis audit'
    if 'chronologie_sha256' in audit:assert audit['chronologie_sha256']==digest(EP/'chronologie.json')
    return {'rig_sha256':RIG_SHA,'visual_sources_unchanged':baseline,'protected_originals_verified':verified,
            'protected_originals_unavailable_in_this_checkout':unavailable,'sound_producer_hashes':hashes,
            'sound_audit_mix_sha256':audit['mix_sha256']}


def audio_checks(movie):
    mix=read_pcm(EP/'audio/mix.wav')
    assert mix.shape==(NSAMPLES,2),'WAV duration differs'
    assert np.abs(mix.astype(np.int32)).max()<32767,'Clipped PCM'
    assert not mix[0].any() and not mix[-1].any()
    silence=mix[32*SR:int(32.5*SR)]
    assert silence.shape==(24000,2) and not silence.any(),'32–32.5s is not exactly silent in PCM'
    ending=mix[int(37.25*SR):]
    assert not ending.any(),'Sound continues during final 0.75s pose hold'
    raw=command(['ffmpeg','-v','error','-xerror','-i',str(movie),'-map','0:a:0','-t','38',
                 '-ar',str(SR),'-ac','2','-c:a','pcm_f32le','-f','f32le','-'])
    decoded=np.frombuffer(raw,'<f4').reshape(-1,2)
    assert decoded.shape==mix.shape and np.isfinite(decoded).all()
    assert float(np.abs(decoded).max())<.999
    ref=mix.astype(np.float64)/32768.;a=ref.ravel();b=decoded.astype(np.float64).ravel()
    corr=float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)))
    assert corr>.95,('AAC/current WAV mismatch or offset',corr)
    gap=decoded[round(32.06*SR):round(32.44*SR)]
    gap_metrics=metric(gap,False)
    assert gap_metrics['rms_dbfs'] < -80. and gap_metrics['peak_dbfs'] < -65.,('AAC core silence contains material',gap_metrics)
    excerpt=read_pcm(EP/'audio/test_fin_v27.wav')
    assert np.array_equal(excerpt,mix[30*SR:]),'30–38s excerpt differs from actual final mix'
    return {'mix_sha256':digest(EP/'audio/mix.wav'),'samples_per_channel':NSAMPLES,
        'sample_rate':SR,'channels':2,'bit_depth':16,'pcm_metrics':metric(mix),
        'wav_clipped_samples':0,'decoded_aac_metrics':metric(decoded,False),
        'wav_vs_decoded_aac_correlation_without_offset':corr,
        'silence_pcm':{'interval_s':[32.,32.5],'frames':24000,'nonzero_samples':0},
        'silence_decoded_aac_core':{'interval_s':[32.06,32.44],**gap_metrics},
        'final_pose_pcm':{'interval_s':[37.25,38.],'nonzero_samples':0},
        'test_final_excerpt_sha256':digest(EP/'audio/test_fin_v27.wav'),'excerpt_interval_s':[30.,38.]}


def cue_checks():
    provenance=json.loads((EP/'audio/provenance.json').read_text())
    assert abs(float(provenance['delivery_gain_db'])-3.5)<1e-9,'Delivery gain differs from fixed contract'
    assert provenance['mix_sha256']==digest(EP/'audio/mix.wav')
    events=provenance['events'];voices=[];stats=[]
    for event in events:
        path=EP/'audio'/event['file']
        assert path.is_file() and digest(path)==event['sha256'],('Cue PCM differs',event['name'])
        data=read_pcm(path);start=int(event['start_sample']);end=start+len(data)
        assert len(data)==int(event['samples']) and 0<=start<end<=NSAMPLES
        assert abs(float(event['duration'])-len(data)/SR)<1/SR
        a=max(start,32*SR);b=min(end,int(32.5*SR))
        if b>a:assert not data[a-start:b-start].any(),('Cue overlaps silence',event['name'])
        a=max(start,int(37.25*SR));b=min(end,NSAMPLES)
        if b>a:assert not data[a-start:b-start].any(),('Cue overlaps final pose silence',event['name'])
        assert event['kind'] not in ('smoke_alarm','alarm','detector','beep'),'Unrequested alarm changes sound hierarchy'
        if event['kind']=='mou_nonverbal':
            assert event['name'] in VOICE_TIMES,('Unexpected vocal event',event['name'])
            t,d=VOICE_TIMES[event['name']]
            assert abs(start/SR-t)<=1/SR and abs(len(data)/SR-d)<=1/SR
            assert len(data)<=round(.3*SR)
            voices.append({'name':event['name'],'start':start/SR,'duration':len(data)/SR,'metrics':metric(data)})
        stats.append({'name':event['name'],'kind':event['kind'],'start_s':start/SR,'end_s':end/SR,
                      'pcm_sha256':event['sha256'],'metrics':metric(data)})
    assert len(voices)==5 and {e['name'] for e in voices}==set(VOICE_TIMES),'Five intended accents not all present'
    # Recheck retained PCM against the frozen V26 event metadata, rather than
    # accepting an author's boolean claim that the baseline cues were kept.
    reference_path=EP/'audio'/provenance['reference_events_file']
    assert digest(reference_path)==provenance['reference_events_sha256']
    reference_data=json.loads(reference_path.read_text())
    reference={e['name']:{**e,'start_sample':round(float(e['start'])*SR)}
               for e in reference_data['events']}
    original_provenance=ROOT/'episodes/03/cuisine_v26/audio/provenance.json'
    if original_provenance.is_file():
        original={e['name']:e for e in json.loads(original_provenance.read_text())['events']}
        for name,event in reference.items():
            for key in ('sha256','start_sample','samples','kind'):
                assert event[key]==original[name][key],('Frozen V26 reference differs',name,key)
    current={e['name']:e for e in events}
    retained=provenance['retained_v26_cues']
    assert len(retained)==46 and len({e['current'] for e in retained})==46
    for entry in retained:
        now,old=current[entry['current']],reference[entry['reference']]
        assert old['kind'] not in ('background_music','frying')
        for key in ('sha256','start_sample','samples','kind'):
            assert now[key]==old[key],('Retained cue changed',entry['current'],key)
    stem_metrics=[]
    for stem in provenance['stems']:
        path=EP/'audio'/stem['file'];assert digest(path)==stem['sha256']
        data=read_pcm(path);assert data.shape==(NSAMPLES,2)
        assert not data[32*SR:round(32.5*SR)].any(),('Stem overlaps silence',stem['track'])
        assert not data[round(37.25*SR):].any(),('Stem overlaps final pose',stem['track'])
        if stem['track'] in ('guitare','basse'):
            outside=np.ones(NSAMPLES,dtype=bool)
            outside[:32*SR]=False;outside[round(36.25*SR):round(36.75*SR)]=False
            assert not data[outside].any(),('Musical stem outside allowed note window',stem['track'])
        stem_metrics.append({'track':stem['track'],'file_sha256':stem['sha256'],'metrics':metric(data)})
    assert {s['track'] for s in stem_metrics}=={'guitare','basse','effets','voix','ambiance'}
    music=read_pcm(EP/'audio/musique_v27.wav');assert music.shape==(NSAMPLES,2)
    allowed=np.arange(NSAMPLES)<32*SR
    allowed[round(36.25*SR):round(36.75*SR)]=True
    assert not music[~allowed].any(),'Music outside 0–32s and the single final-note window'
    assert music[:32*SR].any() and music[round(36.25*SR):round(36.75*SR)].any()
    voice_manifest=json.loads((EP/'assets/vocal_sources/provenance.json').read_text())
    assert digest(EP/'assets/vocal_sources/CC0_LICENSE.txt')==voice_manifest['licence_sha256']
    for entry in voice_manifest['sources']:
        assert digest(EP/'assets/vocal_sources'/entry['local_wav'])==entry['wav_sha256']
        assert digest(EP/'assets/vocal_sources'/entry['local_original'])==entry['source_sha256']
    return {'event_count':len(events),'all_event_pcm_and_intervals_verified':True,'events':stats,
        'retained_v26_pcm_and_timing_directly_verified':len(retained),'stems':stem_metrics,
        'vocal_count':len(voices),'vocal_total_seconds':sum(v['duration'] for v in voices),'vocals':voices,
        'music_pcm_sha256':digest(EP/'audio/musique_v27.wav'),'music_zero_outside_intervals':[[0.,32.],[36.25,36.75]],
        'vocal_sources_licence_verified':'CC0 1.0 notice and all original/decoded SHA verified',
        'vocal_source_limits':voice_manifest.get('limits',LIMITS),
        'wordlessness_note':'Intended nonverbal cue timings verified; no listening/transcription claim.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,default=EP/'MOU_Encore_une_feuille.mp4')
    parser.add_argument('--silent',type=Path,default=EP/'MOU_Encore_une_feuille_muette.mp4')
    parser.add_argument('--report',type=Path,default=EP/'controle/audit_final.json')
    args=parser.parse_args()
    report={'status':'in_progress','scope':'V27 sound-only: exact V26 picture identity, new PCM and mux',
        'dimensions':[1080,1920],'fps':FPS,'duration_seconds':DURATION,'expected_frames':NFRAMES,'limits':LIMITS}
    atomic_json(args.report,report)
    try:
        tracked=[p for p in (EP/'sources').glob('*') if p.is_file() and p.suffix in ('.py','.json')]
        tracked += list(EP.glob('chronologie*.json'))
        tracked += [p for p in (EP/'assets').rglob('*') if p.is_file()]
        before={str(p):digest(p) for p in tracked}
        report['source_integrity']=source_checks()
        assert digest(args.silent)==V26_SILENT_SHA,'Silent MP4 differs from the exact V26 master'
        report['sound_video']=probe_video(args.video,True)
        report['silent_video']=probe_video(args.silent,False)
        sound_stream,silent_stream=video_stream(args.video),video_stream(args.silent)
        assert sound_stream==silent_stream,'Mux changed compressed picture data'
        report['identical_compressed_video_bitstreams']=sound_stream
        sound_pts,sound_pts_meta=video_timestamps(args.video)
        silent_pts,silent_pts_meta=video_timestamps(args.silent)
        assert sound_pts==silent_pts,'Mux changed video timing'
        report['identical_video_timestamps']=sound_pts_meta
        old=ROOT/'episodes/03/cuisine_v26/MOU_Encore_une_feuille_muette.mp4'
        if old.is_file():
            assert video_stream(old)==silent_stream
            old_pts,_=video_timestamps(old);assert old_pts==sound_pts
            report['v26_original_picture_rechecked']=True
        else:report['v26_original_picture_rechecked']=False
        report['audio']=audio_checks(args.video)
        report['cue_provenance']=cue_checks()
        assert before=={str(p):digest(p) for p in tracked},'Producer changed during final QA'
        report['tested_sources_sha256']=before
        report['status']='passed'
    except Exception as e:
        report['status']='failed';report['error']=f'{type(e).__name__}: {e}'
        atomic_json(args.report,report)
        raise
    atomic_json(args.report,report)
    print(json.dumps({'status':report['status'],'report':str(args.report),'v26_picture_identical':True,
        'audio_correlation':report['audio']['wav_vs_decoded_aac_correlation_without_offset'],
        'vocal_count':report['cue_provenance']['vocal_count'],'silence_pcm_interval':[32.,32.5],
        'final_hold_silence':[37.25,38.]},ensure_ascii=False))


if __name__=='__main__':main()
