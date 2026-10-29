"""Build review clips and unnamed acting images from the real MP4 exports."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    tag='animatique' if args.preview else 'final'
    video=EP/('MOU_Encore_une_feuille_animatique.mp4' if args.preview else 'MOU_Encore_une_feuille.mp4')
    silent=video.with_name(video.stem+'_muette.mp4')
    fps,w,h=(12,540,960) if args.preview else (24,1080,1920)
    # These review images have timestamps, without intended-emotion captions.
    times=[40.5,41.15,41.7,42.25,42.95,43.6,44.15]
    ending=sorted({round(t*fps) for t in times})
    other=[round(t*fps) for t in (7.3,16.4,22.875,28.9,33.916667,36.4,36.7,39.083333,39.125)]
    indices=sorted(set(ending+other))
    select='select='+'+'.join(f'eq(n\\,{n})' for n in indices)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',select,
        '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    frames=np.frombuffer(raw,np.uint8).reshape(len(indices),h,w,3)
    mapping={n:Image.fromarray(a) for n,a in zip(indices,frames)}
    spec=importlib.util.spec_from_file_location('proof_reference',EP/'sources/render.py')
    renderer=importlib.util.module_from_spec(spec);sys.modules[spec.name]=renderer;spec.loader.exec_module(renderer)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),18)
    board=Image.new('RGB',(1080,505*((len(ending)+3)//4)),'#FFF8ED')
    faces=Image.new('RGB',(1080,385*((len(ending)+3)//4)),'#FFF8ED')
    draw,fd=ImageDraw.Draw(board),ImageDraw.Draw(faces)
    for j,n in enumerate(ending):
        frame=mapping[n];frame.save(EP/'controle'/f'{tag}_jeu_{j+1:02d}.png')
        x,y=j%4*270,j//4*505
        board.paste(frame.resize((270,480),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+8,y+483),f'{n/fps:.3f}s',font=font,fill='#382035')
        state=renderer.animation.scene_state(n/fps);ax,ay,scale=state['actor_transform']
        vx,vy,vw,vh=renderer.camera_at(state['t'],state)
        box=[(ax+118*scale-vx)*w/vw,(ay+150*scale-vy)*h/vh,
             (ax+288*scale-vx)*w/vw,(ay+350*scale-vy)*h/vh]
        face=frame.crop(tuple(round(v) for v in box)).resize((270,350),Image.Resampling.LANCZOS)
        fx,fy=j%4*270,j//4*385;faces.paste(face,(fx,fy))
        fd.text((fx+8,fy+358),f'{n/fps:.3f}s',font=font,fill='#382035')
    board.save(EP/'controle'/f'{tag}_jeu_planche.png')
    faces.save(EP/'controle'/f'{tag}_visages_planche.png')
    for n in other:mapping[n].save(EP/'controle'/f'{tag}_contact_{n:04d}.png')
    # Accurate cuts are reencoded; seek happens after opening the source.
    for mute,source in ((False,video),(True,silent)):
        name='MOU_fin_tablier'+('_animatique' if args.preview else '')+('_muette' if mute else '')+'.mp4'
        command=['ffmpeg','-y','-v','error','-i',str(source),'-ss','37','-t','7.5',
                 '-c:v','libx264','-threads','2','-preset','medium','-crf','12','-pix_fmt','yuv420p']
        command+=['-an'] if mute else ['-c:a','aac','-b:a','160k']
        subprocess.run(command+['-movflags','+faststart',str(EP/name)],check=True)
    (EP/'controle'/f'{tag}_proofs.json').write_text(json.dumps({
        'source_video':video.name,'source_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'method':'Actual MP4 frames; face crops provide no intended-emotion captions.',
        'ending_frames':ending,'other_frames':other,'clip_start_seconds':37.,'clip_duration_seconds':7.5,
    },indent=2)+'\n')
    print(json.dumps({'tag':tag,'review_frames':len(indices),'clip_duration_seconds':7.5}))


if __name__=='__main__':main()
