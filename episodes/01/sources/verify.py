"""Audits du MP4 livré, du silence, de la capture et de la chaîne de rendu."""
from pathlib import Path
import hashlib, json, math, subprocess, sys
import numpy as np
from render import EP, ROOT, FPS, FLASH, audit, prepare_photo
from animation import pose_at

def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))

def decoded_frame(p,t):
    data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
    return np.frombuffer(data,np.uint8).reshape(1920,1080,3)

def video_hash(p):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def main():
    prepare_photo(); structure=audit()
    full=EP/'MOU_01_le_retardateur.mp4';mute=EP/'MOU_01_le_retardateur_muet.mp4'
    for p in [full,mute]:
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
    a,b=probe(full),probe(mute)
    vs=next(s for s in a['streams'] if s['codec_type']=='video')
    sound=next(s for s in a['streams'] if s['codec_type']=='audio')
    assert (vs['width'],vs['height'])==(1080,1920)
    assert vs['r_frame_rate']=='24/1' and int(vs['nb_read_frames'])==336
    assert abs(float(a['format']['duration'])-14)<.001
    assert sound['sample_rate']=='48000' and sound['channels']==2
    assert len(b['streams'])==1 and b['streams'][0]['codec_type']=='video'
    assert video_hash(full)==video_hash(mute)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(full),'-map','0:a','-f','f32le','-acodec','pcm_f32le','-'])
    samples=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    peak=float(np.abs(samples).max());assert peak<.99
    # AAC has small tails; measure real decoded audio, not only the source WAV.
    pre=samples[round(6.05*48000):round(6.45*48000)]
    assert float(np.abs(pre).max())<.0001
    win=np.abs(samples[round(6.48*48000):round(6.55*48000)]).max(axis=1)
    onset=(round(6.48*48000)+int(np.argmax(win>.005)))/48000
    assert abs(onset-FLASH)<.01
    assert pose_at(155/FPS)==pose_at(FLASH)
    # Camera is held here: compare the decoded screen, tolerance for H264.
    # At zoom3.6, screen occupies x180..900, y366..1482.
    f1,f2=decoded_frame(full,7.5),decoded_frame(full,8.5)
    delta=np.abs(f1[380:1460,195:885].astype(float)-f2[380:1460,195:885].astype(float))
    assert float(delta.mean())<1.0
    flash=decoded_frame(full,6.5);before=decoded_frame(full,155/FPS)
    assert float(flash.mean())>float(before.mean())+25
    result={'format':'H264/yuv420p + AAC stereo48kHz','dimensions':[1080,1920],
            'duration_seconds':14,'fps':24,'decoded_frames':336,'complete_decode_without_errors':True,
            'mute_contains_no_audio':True,'video_bitstream_identical_between_versions':True,
            'flash_frame':156,'capture_matches_pose_immediately_before_flash':True,
            'decoded_click_onset_seconds':round(onset,6),'audio_peak_dbfs':round(20*math.log10(peak),3),
            'decoded_preflash_peak':float(np.abs(pre).max()),'photo_screen_mean_delta_7_5_to_8_5':round(float(delta.mean()),6),
            'limits':'Inspection visuelle par échantillons denses et planches ; contrôles audio numériques, sans écoute sur téléphone réel ni test de public.'}
    (EP/'controle/audit_final.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
