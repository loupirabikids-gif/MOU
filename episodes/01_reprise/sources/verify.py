"""Contrôles du fichier réellement encodé et du jeu frais indépendant du cache."""
from pathlib import Path
import hashlib, io, json, math, subprocess
import cairosvg
from PIL import Image
import numpy as np
from render import EP, FPS, DURATION, NFRAMES, FLASH, TIMELINE, PHOTO_START, PHOTO_END, audit, prepare_photo, svg_at, puppet, photo_svg
from animation import pose_at, character_at
REVISION=int(TIMELINE["revision"])

def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))

def decoded_frame(p,t):
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
    return np.frombuffer(data,np.uint8).reshape(1920,1080,3)

def video_hash(p):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def main():
    prepare_photo(); audit()
    stem=TIMELINE['file_stem']
    full=EP/f'{stem}.mp4';mute=EP/f'{stem}_muet.mp4'
    for p in [full,mute]:
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
    a,b=probe(full),probe(mute)
    vs=next(s for s in a['streams'] if s['codec_type']=='video')
    sound=next(s for s in a['streams'] if s['codec_type']=='audio')
    assert (vs['width'],vs['height'])==(1080,1920)
    assert vs['r_frame_rate']=='24/1' and int(vs['nb_read_frames'])==NFRAMES
    assert abs(float(a['format']['duration'])-DURATION)<.001
    assert sound['sample_rate']=='48000' and sound['channels']==2
    assert len(b['streams'])==1 and b['streams'][0]['codec_type']=='video'
    assert video_hash(full)==video_hash(mute)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(full),'-map','0:a','-f','f32le','-acodec','pcm_f32le','-'])
    samples=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    peak=float(np.abs(samples).max()); assert peak<.99
    silence=TIMELINE['audio_silence_before_flash']
    pre=samples[round(silence['decoded_check_start']*48000):round(silence['decoded_check_end']*48000)]
    photo_audio=samples[round(TIMELINE['photo_hold']['start']*48000):round(TIMELINE['photo_hold']['end']*48000)]
    assert float(np.abs(pre).max())<.0001 and float(np.abs(photo_audio).max())<.0001
    final_start=TIMELINE['reaction']['final_hold_start']
    final_audio=samples[round(final_start*48000):round(DURATION*48000)]
    assert float(np.abs(final_audio).max())<.0001
    j=round((FLASH-.02)*48000)
    win=np.abs(samples[j:round((FLASH+.05)*48000)]).max(axis=1)
    onset=(j+int(np.argmax(win>.005)))/48000
    assert abs(onset-FLASH)<.01
    assert pose_at(FLASH-1/FPS)!=pose_at(FLASH)
    # Frozen result appears only after the click; it is the same vector model.
    assert all('data:image/png' not in svg_at(i/FPS) for i in range(TIMELINE['flash_frame']))
    f1,f2=decoded_frame(full,7.0),decoded_frame(full,7.75)
    delta=np.abs(f1[395:1280,255:825].astype(float)-f2[395:1280,255:825].astype(float))
    assert float(delta.mean())<1.0
    assert PHOTO_END-PHOTO_START==1.25
    assert puppet(FLASH,'photo') in photo_svg(), 'photograph differs from captured avatar'
    captured=pose_at(FLASH)
    assert all(pose_at(i/FPS)==captured for i in range(round(FLASH*FPS),round(TIMELINE['capture_hold']['end']*FPS)))
    last=pose_at(final_start)
    assert all(pose_at(i/FPS)==last for i in range(round(final_start*FPS),NFRAMES))
    assert svg_at(final_start)==svg_at((NFRAMES-1)/FPS)
    last1,last2=decoded_frame(full,final_start),decoded_frame(full,(NFRAMES-1)/FPS)
    last_delta=float(np.abs(last1.astype(float)-last2.astype(float)).mean())
    assert last_delta<.5
    laughs=[]
    for event in TIMELINE['reaction']['laughs']:
        start,duration=event['start'],event['duration']
        audio=samples[round(start*48000):round((start+duration)*48000)]
        assert float(np.abs(audio).max())>.025, 'missing nervous laugh'
        breath_onset=start+int(np.argmax(np.abs(audio).max(axis=1)>.0003))/48000
        assert breath_onset-start<.04
        assert abs(pose_at(start+2/FPS)['warp_sy']-pose_at(start)['warp_sy'])>.001, 'missing micro-shake'
        laughs.append({'start_seconds':start,'decoded_onset_seconds':round(breath_onset,6),
                       'peak_dbfs':round(20*math.log10(float(np.abs(audio).max())),3)})
    flash=decoded_frame(full,FLASH);before=decoded_frame(full,FLASH-1/FPS)
    assert float(flash.mean())>float(before.mean())+25
    source_match={}
    for t,roi in [(22/FPS,(350,1250,1080,1920)),(54/FPS,(100,500,1000,1600)),
                  (132/FPS,(100,500,1000,1600)),(143/FPS,(100,500,1000,1600)),
                  (FLASH,(100,500,1000,1600)),(147/FPS,(100,500,1000,1600)),
                  (174/FPS,(135,165,945,1420)),(210/FPS,(100,500,1000,1600)),
                  (240/FPS,(100,500,1000,1600)),(279/FPS,(100,500,1000,1600)),
                  (289/FPS,(100,500,1000,1600)),(306/FPS,(100,500,1000,1600))]:
        expected=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_at(t).encode()))).convert('RGB'))
        actual=decoded_frame(full,t);x0,y0,x1,y1=roi
        err=float(np.abs(actual[y0:y1,x0:x1].astype(float)-expected[y0:y1,x0:x1].astype(float)).mean())
        assert err<3.,(t,'encoded gesture differs from source',err)
        source_match[str(round(t,6))]=round(err,6)
    result={'revision':REVISION,'encoded_gestures_match_fresh_svg':True,'gesture_roi_mean_errors_0_255':source_match,
            'format':'H264/yuv420p + AAC stereo48kHz','dimensions':[1080,1920],
            'duration_seconds':DURATION,'fps':FPS,'decoded_frames':NFRAMES,'complete_decode_without_errors':True,
            'mute_contains_no_audio':True,'video_bitstream_identical_between_versions':True,
            'flash_frame':TIMELINE['flash_frame'],'capture_uses_same_character_at_exact_click':True,
            'collapse_still_in_motion_before_click':True,'no_photo_before_click':True,
            'decoded_click_onset_seconds':round(onset,6),'audio_peak_dbfs':round(20*math.log10(peak),3),
            'decoded_preflash_peak':float(np.abs(pre).max()),'decoded_photo_hold_audio_peak':float(np.abs(photo_audio).max()),
            'photo_screen_mean_delta_7_to_7_75':round(float(delta.mean()),6),
            'photo_hold_seconds':PHOTO_END-PHOTO_START,'capture_hold_frames':TIMELINE['capture_hold']['frames'],
            'laughs':laughs,'final_pose_hold_seconds':DURATION-final_start,
            'decoded_final_silence_peak':float(np.abs(final_audio).max()),
            'final_frame_mean_delta':round(last_delta,6),
            'limits':'Inspection par extractions denses et planches ; contrôle audio numérique, sans écoute sur téléphone ni test public.'}
    (EP/'controle/audit_final.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
