"""Vérifie le MP4 réel de quatre secondes et ses gestes hors cache."""
from pathlib import Path
import hashlib,io,json,subprocess
import cairosvg
import numpy as np
from PIL import Image
from render import EP,W,H,FPS,DURATION,NFRAMES,svg_at,audit,animation

def decode_frame(path,t):
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(path),
        '-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-'])
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)

def main():
    audit(EP/'controle/audit_structure.json')
    video=EP/'MOU_test_remuer.mp4'
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames',
        '-show_streams','-show_format','-of','json',str(video)]))
    assert len(probe['streams'])==1
    stream=probe['streams'][0]
    assert stream['codec_type']=='video'and stream['codec_name']=='h264'
    assert stream['pix_fmt']=='yuv420p'
    assert(stream['width'],stream['height'])==(W,H)==(1080,1920)
    assert stream['r_frame_rate']=='24/1'and int(stream['nb_read_frames'])==96
    assert abs(float(probe['format']['duration'])-DURATION)<.001
    samples=(0,8,17,26,35,44,52,61,63,70,79,88,95)
    errors={};face_errors={}
    for i in samples:
        t=i/FPS
        fresh=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg_at(t).encode()))).convert('RGB'))
        actual=decode_frame(video,t)
        # Active hand, spoon and pan; exclude unrelated static scenery.
        roi=(slice(1050,1415),slice(155,555))
        error=float(np.abs(fresh[roi].astype(float)-actual[roi].astype(float)).mean())
        assert error<3.,(i,error)
        errors[str(i)]=round(error,6)
        if i in(0,63,95):
            face=(slice(800,1165),slice(285,805))
            value=float(np.abs(fresh[face].astype(float)-actual[face].astype(float)).mean())
            assert value<3.,(i,value,'face differs from fresh source')
            face_errors[str(i)]=round(value,6)
    # Fixed non-actor scene regions should stay fixed in the encoded stream.
    first,last=decode_frame(video,0),decode_frame(video,95/FPS)
    fixed=np.zeros((H,W),bool);fixed[:600,:]=True;fixed[1510:,:]=True;fixed[800:1460,875:]=True
    scenery_delta=float(np.abs(first.astype(float)-last.astype(float))[fixed].mean())
    assert scenery_delta<.2
    start=animation.contact_at(animation.STIR_START);end=animation.contact_at(animation.STIR_END)
    assert abs((end['phase']-start['phase'])/(2*np.pi)-2)<1e-10
    right_native=True
    from mou_rig import _arm
    for i in range(NFRAMES):
        layer=animation.actor_layers_at(i/FPS)
        assert _arm('right',0.,1.) in layer['arms_front']
    report={'stage':'microtest_remuer_uniquement','duration_seconds':DURATION,
        'dimensions':[W,H],'fps':FPS,'decoded_frames':NFRAMES,
        'format':'H264/yuv420p','audio_streams':0,'full_decode_without_errors':True,
        'fresh_svg_vs_encoded_contact_roi_mean_errors_0_255':errors,
        'fresh_svg_vs_encoded_face_roi_mean_errors_0_255':face_errors,
        'fixed_scenery_mean_delta_first_last_0_255':round(scenery_delta,6),
        'right_arm_exact_original_fixed':right_native,'net_stirring_turns':2,
        'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'tested_animation_sha256':hashlib.sha256((EP/'sources/animation.py').read_bytes()).hexdigest(),
        'tested_renderer_sha256':hashlib.sha256((EP/'sources/render.py').read_bytes()).hexdigest(),
        'scope':'Vérification technique du geste ; naturel et profondeur examinés dans la critique du MP4. Aucun essuyage, son ou épisode complet.'}
    (EP/'controle/audit_final.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='fresh_svg_vs_encoded_contact_roi_mean_errors_0_255'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
