"""Render the original pebble design, its six acting poses and silent test."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent;EP=HERE.parent
ROOT=next(p for p in EP.parents if (p/'fonts/DejaVuSans-Bold.ttf').is_file())
sys.path.insert(0,str(HERE))
import animation
from PIL import Image,ImageDraw,ImageFont
import cairosvg

KEY_TIMES=(.05,.70,1.43,2.12,2.90,4.60)
LABELS=('Il est sûr de lui','Une petite trace','Il la retire','Propre… de ce côté','Elle colle à l’autre','Sauver les apparences')


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def job(args):
    i,scale=args;p=EP/'frames'/('preview'if scale<1. else'final')/f'{i:05d}.png';p.parent.mkdir(parents=True,exist_ok=True)
    svg=animation.svg_at(i/animation.FPS)
    p.write_bytes(cairosvg.svg2png(bytestring=svg.encode(),output_width=round(1080*scale),output_height=round(1920*scale)))
    return str(p)


def stills():
    (EP/'controle').mkdir(exist_ok=True);(EP/'poses').mkdir(exist_ok=True)
    fnt=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),19)
    board=Image.new('RGB',(1440,1830),'#FFF5E9');draw=ImageDraw.Draw(board)
    for j,(t,label)in enumerate(zip(KEY_TIMES,LABELS)):
        svg=animation.svg_at(t);(EP/'poses'/f'pose_{j+1:02d}.svg').write_text(svg)
        data=cairosvg.svg2png(bytestring=svg.encode(),output_width=1080,output_height=1920)
        image=Image.open(io.BytesIO(data)).convert('RGB')
        # A scene crop keeps the acting legible in the six-pose study.
        tile=image.crop((80,680,1000,1450)).resize((480,402),Image.Resampling.LANCZOS)
        x=j%3*480;y=j//3*900
        draw.text((x+18,y+22),f'{j+1:02d} / {t:.2f}s',font=fnt,fill='#342238')
        board.paste(tile,(x,y+85))
        draw.text((x+18,y+520),label,font=fnt,fill='#342238')
        if j==0:image.save(EP/'Galet_reference.png')
        if j==5:image.save(EP/'Galet_pose_finale.png')
    # Compact portrait sheet with two rows and no empty display cards.
    compact=Image.new('RGB',(1440,1220),'#FFF5E9')
    compact.paste(board.crop((0,0,1440,610)),(0,0));compact.paste(board.crop((0,900,1440,1510)),(0,610))
    compact.save(EP/'Galet_poses.png')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--preview',action='store_true');args=ap.parse_args()
    files=sorted(HERE.glob('*.py'))+list(HERE.glob('*.json'));frozen={str(p.relative_to(EP)):digest(p)for p in files}
    stills()
    if args.stills:return
    scale=.5 if args.preview else 1.;count=round(animation.DURATION*animation.FPS)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3)as pool:
        for i,_ in enumerate(pool.map(job,[(i,scale)for i in range(count)]),1):
            if i%24==0:print(f'galet {i}/{count}',flush=True)
    frames=EP/'frames'/('preview'if args.preview else'final')
    output=EP/('Galet_miette_animatique_muette.mp4'if args.preview else'Galet_miette_muette.mp4')
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(animation.FPS),'-i',str(frames/'%05d.png'),
                    '-frames:v',str(count),'-c:v','libx264','-threads','3','-preset','medium','-crf','10',
                    '-pix_fmt','yuv420p','-an','-movflags','+faststart',str(output)],check=True)
    assert frozen=={str(p.relative_to(EP)):digest(p)for p in files},'Sources changed during rendering'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]))
    result={'sources_sha256':frozen,'output_sha256':digest(output),'probe':probe,'silent':True}
    (EP/'controle'/('rendu_animatique.json'if args.preview else'rendu_final.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(output,flush=True)


if __name__=='__main__':main()
