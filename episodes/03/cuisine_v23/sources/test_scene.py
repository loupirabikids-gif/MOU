"""Render the eight-second directing test before the complete episode."""
from pathlib import Path
import argparse
import concurrent.futures
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
spec=importlib.util.spec_from_file_location('pro_test_renderer',EP/'sources/render.py')
render=importlib.util.module_from_spec(spec);sys.modules[spec.name]=render;spec.loader.exec_module(render)
FPS=24;START=966;COUNT=192


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--silent-only',action='store_true')
    args=parser.parse_args()
    sources=[EP/'sources'/n for n in ('animation.py','acting.py','poses.json','art.py','render.py','costume.py','test_scene.py','jeu_visage.py','visage.py','expressions.json')]
    sources+=[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'assets/Nunito-wght.ttf']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    frozen={str(p):digest(p) for p in sources}
    frames=EP/'frames/test';frames.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        for n,_ in enumerate(pool.map(render.render_job,[(i,FPS,1.,str(frames)) for i in range(START,START+COUNT)]),1):
            if n%48==0:print(f'test: {n}/{COUNT}',flush=True)
    assert frozen=={str(p):digest(p) for p in sources},'Source changed during test rendering'
    silent=EP/'MOU_test_mise_en_scene_muette.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-start_number',str(START),
        '-i',str(frames/'%05d.png'),'-frames:v',str(COUNT),'-c:v','libx264','-threads','3',
        '-preset','medium','-crf','8','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(silent)],check=True)
    if not args.silent_only:
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(EP/'audio/test_fin_8s.wav'),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-t','8',
            '-movflags','+faststart',str(EP/'MOU_test_mise_en_scene.mp4')],check=True)
    indices=[16,32,48,64,82,88,100,110,128,150,166,184]
    selection='select='+'+'.join(f'eq(n\\,{n})' for n in indices)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(silent),'-vf',selection,
          '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    decoded=np.frombuffer(raw,np.uint8).reshape(len(indices),1920,1080,3)
    board=Image.new('RGB',(1080,1515),'#FFF8ED');draw=ImageDraw.Draw(board)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),17)
    for j,(n,pixels) in enumerate(zip(indices,decoded)):
        im=Image.fromarray(pixels);im.save(EP/'controle'/f'test_image_{n:03d}.png')
        x,y=j%4*270,j//4*505;board.paste(im.resize((270,480),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+8,y+483),f'{n/FPS:.3f}s',font=font,fill='#382035')
    board.save(EP/'controle/test_plans_planche.png')
    render.write_json(EP/'controle/sources_test.json',{'sources_sha256':frozen,'start_episode_seconds':40.25,
        'duration_seconds':8.,'fps':FPS,'frames':COUNT,'silent_video_sha256':digest(silent)})
    print(json.dumps({'output':str(silent),'frames':COUNT,'duration':8.,'sound':not args.silent_only}),flush=True)


if __name__=='__main__':main()
