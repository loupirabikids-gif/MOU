"""Reproduce a controlled7s A/B sound-isolation diagnostic from frozen V24.

A is the exact V24 mix excerpt before AAC encoding. B omits only the music
event; every other event and the whole-film mixing contract stay unchanged.
Both outputs reuse one encoded video stream. This is not a proposed final mix.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP=ROOT/'episodes/03/cuisine_v24'
OUT=Path(__file__).resolve().parent
WORK=ROOT/'work/diagnostic_son_v24'
START=10.25;END=17.25;DURATION=END-START;FPS=24;SR=48000


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(arguments):return subprocess.check_output(arguments,stderr=subprocess.PIPE)


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert(source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def write_pcm(path,values):
    assert values.ndim==2 and values.shape[1]==2 and np.abs(values.astype(np.int32)).max()<32767
    with wave.open(str(path),'wb') as target:
        target.setnchannels(2);target.setsampwidth(2);target.setframerate(SR)
        target.writeframes(values.astype('<i2').tobytes())


def edge_fade(n):
    envelope=np.ones(n);a=round(.008*SR);b=round(.035*SR)
    envelope[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    envelope[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return envelope


def pcm_digest(values):return hashlib.sha256(values.astype('<i2').tobytes()).hexdigest()


def video_digest(path):
    data=run(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy',
              '-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}


def inspect(path,expected_pcm):
    probe=json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams',
                          '-show_format','-of','json',str(path)]))
    assert len(probe['streams'])==2
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert(video['width'],video['height'],video['r_frame_rate'],int(video['nb_read_frames']))==(1080,1920,'24/1',168)
    assert abs(float(video['duration'])-DURATION)<.001
    assert(audio['codec_name'],int(audio['sample_rate']),int(audio['channels']))==('aac',SR,2)
    assert abs(float(audio['duration'])-DURATION)<.001
    run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(path),'-f','null','-'])
    decoded=np.frombuffer(run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
        '-t',str(DURATION),'-c:a','pcm_f32le','-f','f32le','-']),'<f4').astype(float)
    reference=expected_pcm.astype(float).ravel()/32768.
    assert decoded.shape==reference.shape and np.isfinite(decoded).all()
    peak=float(np.abs(decoded).max());assert peak<.999
    correlation=float(np.dot(decoded,reference)/np.sqrt(np.dot(decoded,decoded)*np.dot(reference,reference)))
    assert correlation>.9
    return {'file':path.name,'sha256':sha(path),'bytes':path.stat().st_size,
            'dimensions':[1080,1920],'fps':24,'frames':168,'duration_seconds':DURATION,
            'video_bitstream':video_digest(path),'full_decode_without_errors':True,
            'audio':{'codec':'AAC','sample_rate':SR,'channels':2,
                     'decoded_aac_peak_dbfs':float(20*np.log10(peak)),
                     'decoded_aac_matches_own_pcm_correlation':correlation}}


def main():
    OUT.mkdir(parents=True,exist_ok=True);WORK.mkdir(parents=True,exist_ok=True)
    source_video=EP/'MOU_Encore_une_feuille_muette.mp4'
    source_mix=EP/'audio/mix.wav';source_provenance=EP/'audio/provenance.json'
    protected=[source_video,source_mix,source_provenance]
    before={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
    provenance=json.loads(source_provenance.read_text());assert provenance['duration_seconds']==43.
    assert provenance['delivery_gain_db']==3.5
    full=pcm(source_mix);n=round(43*SR);assert full.shape==(n,2)
    start,end=round(START*SR),round(END*SR)
    a=full[start:end].astype(np.int32);assert len(a)==336000
    summed=np.zeros((n,2),dtype=np.int32);retained=[];omitted=[]
    for event in provenance['events']:
        if event['kind']=='background_music':
            omitted.append(event['name']);continue
        path=EP/'audio'/event['file'];assert sha(path)==event['sha256']
        data=pcm(path).astype(np.int32);offset=event['start_sample']
        assert offset+len(data)<=n and len(data)==event['samples']
        summed[offset:offset+len(data)]+=data;retained.append(event['name'])
    assert len(retained)==57 and omitted==['musique_v24']
    before_gain=np.rint(summed*edge_fade(n)[:,None]).astype(np.int32)
    reconstructed=np.rint(before_gain*provenance['delivery_gain_linear']).astype(np.int32)
    assert np.abs(reconstructed).max()<32767
    b=reconstructed[start:end];assert b.shape==a.shape
    for name,values in [('A',a),('B',b)]:write_pcm(WORK/f'{name}.wav',values)
    silent=WORK/'segment_muette.mp4'
    run(['ffmpeg','-y','-v','error','-threads','2','-i',str(source_video),'-map','0:v:0',
         '-vf','trim=start_frame=246:end_frame=414,setpts=PTS-STARTPTS','-an',
         '-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p',
         '-r','24','-threads','2','-movflags','+faststart',str(silent)])
    reports={}
    for name,filename,values in [('A','A_mix_actuel.mp4',a),('B','B_effets_seuls.mp4',b)]:
        destination=OUT/filename;temporary=WORK/filename
        run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(WORK/f'{name}.wav'),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
             '-t',str(DURATION),'-movflags','+faststart',str(temporary)])
        os.replace(temporary,destination)
        reports[name]=inspect(destination,values)
    assert reports['A']['video_bitstream']==reports['B']['video_bitstream']==video_digest(silent)
    assert before=={p.relative_to(ROOT).as_posix():sha(p) for p in protected}
    audit={'status':'passed','purpose':'Sound-isolation diagnostic; B is not a proposed music-free final',
           'sources_sha256':before,'sources_unchanged':True,
           'range_seconds':[START,END],'source_video_frame_range_half_open':[246,414],
           'source_pcm_frame_range_half_open':[start,end],'frames':168,'duration_seconds':DURATION,
           'same_compressed_video_bitstreams':True,'outputs':reports,
           'A':{'method':'Exact V24 mix PCM slice before lossy AAC encode',
                'exact_source_pcm_segment':True,'pcm_sha256':pcm_digest(a),
                'clipped_samples':int(np.count_nonzero(np.abs(a)>=32767))},
           'B':{'method':'All V24 nonmusic events summed at original start_sample; global8/35ms edge fade then round; original fixed+3.50dB gain then round; exact slice',
                'retained_event_count':len(retained),'omitted_event_names':omitted,
                'existing_frying_and_other_ambience_retained':True,
                'extra_gain_or_normalization':False,'delivery_gain_db':3.5,
                'pcm_sha256':pcm_digest(b),'clipped_samples':int(np.count_nonzero(np.abs(b)>=32767))},
           'intermediates':'Ignored work/diagnostic_son_v24; no WAV copies in this delivery folder',
           'reproduce_script_sha256':sha(__file__),
           'limits':'Technical checks only; no model listening or subjective sound-quality judgement.'}
    fd,temp=tempfile.mkstemp(prefix='.audit_',dir=OUT)
    with os.fdopen(fd,'w') as target:target.write(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    os.replace(temp,OUT/'audit.json')
    print(json.dumps({'status':audit['status'],'clips':reports,'same_video':True},indent=2))


if __name__=='__main__':main()
