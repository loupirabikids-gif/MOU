"""Render complete silent SVG acting studies and their actual pose images."""
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
from PIL import Image, ImageDraw, ImageFont
from scene import FPS,DURATION,svg_at,state_at

EP=Path(__file__).resolve().parents[1]
POSES=[(2.95,'Assurance'),(4.45,'Surprise'),(9.6,'Garder sa dignité')]


def source_hash():
    h=hashlib.sha256()
    for p in sorted((EP/'sources').glob('*')):
        if p.suffix in ('.py','.json'):
            h.update(p.name.encode());h.update(p.read_bytes())
    return h.hexdigest()


def frame_job(args):
    frame,width,directory=args
    path=Path(directory)/f'{frame:04d}.png'; temp=path.with_suffix('.tmp')
    data=cairosvg.svg2png(bytestring=svg_at((frame-1)/FPS).encode(),output_width=width,output_height=width*16//9)
    temp.write_bytes(data);os.replace(temp,path)
    return frame


def stills():
    font=ImageFont.truetype(str(EP.parents[1]/'fonts/DejaVuSans-Bold.ttf'),25)
    sheet=Image.new('RGB',(1620,1032),'#F1ECF8');draw=ImageDraw.Draw(sheet)
    for j,(t,label) in enumerate(POSES):
        path=EP/f'poses/{j+1:02d}.png'
        svg=svg_at(t);(path.with_suffix('.svg')).write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(path),output_width=1080,output_height=1920)
        sheet.paste(Image.open(path).convert('RGB').resize((540,960),Image.Resampling.LANCZOS),(j*540,0))
        draw.text((j*540+18,978),label,font=font,fill='#342238')
    sheet.save(EP/'MOU_Poids_plume_trois_poses.png')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.stills:
        stills();print('POSES_READY');return
    width=540 if args.preview else 1080
    mode='preview' if args.preview else 'hd';folder=EP/'work'/mode;folder.mkdir(parents=True,exist_ok=True)
    digest=source_hash();started=time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(frame_job,[(f,width,str(folder)) for f in range(1,int(DURATION*FPS)+1)]))
    assert source_hash()==digest,'Producer changed during render'
    target=EP/('MOU_Poids_plume_animatique_muette.mp4' if args.preview else 'MOU_Poids_plume_10s_muet.mp4')
    temporary=target.with_name('.'+target.name)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-start_number','1',
                    '-i',str(folder/'%04d.png'),'-frames:v',str(int(DURATION*FPS)),
                    '-c:v','libx264','-crf','18','-preset','medium','-threads',str(args.workers),
                    '-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temporary)],check=True)
    os.replace(temporary,target)
    report={'source_sha256':digest,'file':target.name,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'frames':int(DURATION*FPS),'fps':FPS,'duration':DURATION,'width':width,'height':width*16//9,
            'audio':False,'elapsed_seconds':round(time.time()-started,2)}
    (EP/f'controle/rendu_{mode}.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
