"""Reproduce PATCH's complete animated shots and encode silent or sound MP4s."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import cairosvg
from PIL import Image,ImageDraw,ImageFont
from scene import FPS,DURATION,svg_at

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
POSES=[(2.8,'Déposer dans le coffre'),(3.5,'Fermer par le côté'),(3.75,'Passer à gauche'),(3.92,'Presser le bouton'),(4.875,'Deux petits mm'),(13.25,'Soupir descendant'),(18.0,'Bâillement aigu'),(25.125,'Petits rires')]


def source_hash():
    h=hashlib.sha256()
    for p in sorted((EP/'sources').glob('*')):
        if p.suffix in ('.py','.json') and p.name!='controle.py':h.update(p.name.encode());h.update(p.read_bytes())
    h.update((EP/'chronologie.json').read_bytes())
    return h.hexdigest()


def frame_job(args):
    frame,width,folder=args
    p=Path(folder)/f'{frame:04d}.png';temp=p.with_suffix('.tmp')
    temp.write_bytes(cairosvg.svg2png(bytestring=svg_at((frame-1)/FPS).encode(),output_width=width,output_height=width*16//9))
    os.replace(temp,p)
    return frame


def stills():
    (EP/'poses').mkdir(exist_ok=True)
    f=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),22)
    out=Image.new('RGB',(1440,1420),'#FFF8EE');d=ImageDraw.Draw(out)
    for j,(t,label) in enumerate(POSES):
        p=EP/f'poses/{j+1:02d}.png';svg=svg_at(t);p.with_suffix('.svg').write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(p),output_width=1080,output_height=1920)
        out.paste(Image.open(p).convert('RGB').resize((360,640),Image.Resampling.LANCZOS),((j%4)*360,(j//4)*710))
        d.text(((j%4)*360+12,(j//4)*710+662),label,font=f,fill='#302D35')
    out.save(EP/'PATCH_Le_coffre_V7_storyboard.png')


def encode(folder,target,mix=None):
    temp=target.with_name('.'+target.name)
    if mix:
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(folder),'-i',str(mix),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(DURATION),'-movflags','+faststart',str(temp)]
    else:
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-start_number','1','-i',str(folder/'%04d.png'),
             '-frames:v',str(round(DURATION*FPS)),'-c:v','libx264','-crf','18','-preset','medium','-threads','4',
             '-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temp)]
    subprocess.run(cmd,check=True);os.replace(temp,target)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stills',action='store_true');p.add_argument('--preview',action='store_true')
    p.add_argument('--mux',action='store_true');p.add_argument('--workers',type=int,default=4)
    args=p.parse_args()
    if args.stills:stills();print('PATCH_STILLS_READY');return
    mode='preview' if args.preview else 'hd'
    video=EP/('PATCH_Le_coffre_V7_animatique_muette.mp4' if args.preview else 'PATCH_Le_coffre_V7_muet.mp4')
    if args.mux:
        target=EP/('PATCH_Le_coffre_V7_animatique.mp4' if args.preview else 'PATCH_Le_coffre_V7.mp4')
        encode(video,target,EP/'audio/mix.wav');print('PATCH_MUX_READY='+str(target));return
    width=540 if args.preview else 1080
    folder=EP/'work'/mode;folder.mkdir(parents=True,exist_ok=True)
    started=time.time();digest=source_hash()
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers)as pool:
        list(pool.map(frame_job,[(f,width,str(folder))for f in range(1,round(DURATION*FPS)+1)]))
    assert source_hash()==digest,'Producer changed during rendering'
    encode(folder,video)
    report={'file':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'source_sha256':digest,
            'frames':round(DURATION*FPS),'fps':FPS,'duration':DURATION,'width':width,'height':width*16//9,
            'audio':False,'elapsed_seconds':round(time.time()-started,2)}
    (EP/f'controle/rendu_{mode}.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)


if __name__=='__main__':main()
