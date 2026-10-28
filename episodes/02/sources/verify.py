"""Contrôles des deux MP4 réellement encodés, des silences et des gestes."""
from pathlib import Path
import hashlib, io, json, math, subprocess
import numpy as np
import cairosvg
from PIL import Image
from render import EP, TIMELINE, FPS, DURATION, NFRAMES, W, H, audit, svg_at
from animation import pose_at, contact_at

def probe(path):
    return json.loads(subprocess.check_output(
        ['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))

def decoded_frame(path,t):
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),
                                 '-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)

def video_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v',
        '-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def main():
    audit()
    stem=TIMELINE['file_stem']
    full,mute=[EP/(stem+suffix+'.mp4')for suffix in ('','_muet')]
    for path in (full,mute):
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(path),'-f','null','-'],check=True)
    p,q=probe(full),probe(mute)
    v=next(s for s in p['streams']if s['codec_type']=='video')
    a=next(s for s in p['streams']if s['codec_type']=='audio')
    assert(v['width'],v['height'])==(W,H)==(1080,1920)
    assert v['r_frame_rate']=='24/1'and int(v['nb_read_frames'])==NFRAMES
    assert abs(float(p['format']['duration'])-DURATION)<.001
    assert a['sample_rate']=='48000'and a['channels']==2
    assert len(q['streams'])==1 and q['streams'][0]['codec_type']=='video'
    assert video_hash(full)==video_hash(mute)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(full),'-map','0:a',
                                 '-f','f32le','-acodec','pcm_f32le','-'])
    samples=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    peak=float(np.abs(samples).max());assert 0<peak<.99
    silences=[]
    for event in TIMELINE['silences']:
        window=samples[round(event['start']*48000):round(event['end']*48000)]
        value=float(np.abs(window).max());assert value<.0001
        silences.append({**event,'decoded_peak':value})
    flap=float(TIMELINE['flap_time'])
    # The cloth swish is intentional immediately before contact. Measure
    # the main contact attack from its boundary, not the preceding swish.
    j=round(flap*48000)
    window=np.abs(samples[j:round((flap+.04)*48000)]).max(axis=1)
    onset=(j+int(np.argmax(window>.003)))/48000
    assert abs(onset-flap)<.01
    hold=TIMELINE['final_hold']['start']
    assert svg_at(hold)==svg_at((NFRAMES-1)/FPS), 'final pose moved'
    final_delta=float(np.abs(decoded_frame(full,hold).astype(float)-
                             decoded_frame(full,(NFRAMES-1)/FPS).astype(float)).mean())
    assert final_delta<.5
    matches={}
    points=[0.,1.5,2.5,5.,6.5,7.25,7.5,7.75,8.25,9.25,9.75,10.5,11.25,11.75]
    for t in points:
        t=round(t*FPS)/FPS
        source=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_at(t).encode()))).convert('RGB'))
        actual=decoded_frame(full,t)
        # Full character, tissue and feet; typography is outside this ROI.
        err=float(np.abs(source[390:1740,30:1050].astype(float)-
                         actual[390:1740,30:1050].astype(float)).mean())
        assert err<3.,(t,err,'encoded pose differs from fresh SVG')
        matches[str(round(t,6))]=round(err,6)
    report={'episode':'02','revision':TIMELINE['revision'],'duration_seconds':DURATION,
        'dimensions':[W,H],'fps':FPS,'decoded_frames':NFRAMES,
        'format':'H264/yuv420p + AAC stereo48kHz','complete_decode_without_errors':True,
        'mute_contains_no_audio':True,'video_bitstream_identical':True,
        'fresh_svg_matches_encoded_gestures':True,'gesture_roi_mean_errors_0_255':matches,
        'decoded_flap_onset_seconds':round(onset,6),'audio_peak_dbfs':round(20*math.log10(peak),3),
        'silences':silences,'final_hold_seconds':DURATION-hold,
        'final_frame_mean_delta':round(final_delta,6),
        'contacts':{str(t):contact_at(t)for t in (1.5,2.5,5.,7.25,7.5,10.5,11.75)},
        'files':{p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in(full,mute)},
        'limits':'Source fraîche et décodage numérique ; critique visuelle distincte. Aucune écoute humaine, test mobile ou public revendiqué.'}
    (EP/'controle/audit_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
