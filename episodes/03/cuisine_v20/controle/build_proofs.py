"""Extract visual proof frames from the actual episode MP4, never from PNG cache."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()
    tag = 'animatique' if args.preview else 'final'
    video = EP/('MOU_Encore_une_feuille_animatique.mp4' if args.preview
                else 'MOU_Encore_une_feuille.mp4')
    fps, width, height = (12,540,960) if args.preview else (24,1080,1920)
    times = [38.75,38.916667,39.083333,39.125,39.166667,39.25,39.416667,
             39.583333,39.75,39.916667,40.083333,40.25,40.75]
    ending = sorted({round(t*fps) for t in times})
    named = {round(4.*fps):'chef', round(18.*fps):'lavabo', round(40.75*fps):'final'}
    indices = sorted(set(ending)|set(named))
    select = 'select='+'+'.join(f'eq(n\\,{n})' for n in indices)
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',select,
          '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    frames = np.frombuffer(raw,np.uint8).reshape(len(indices),height,width,3)
    frame_map = {n:Image.fromarray(frame) for n,frame in zip(indices,frames)}
    board = Image.new('RGB',(1080,505*((len(ending)+3)//4)),'#FFF8ED')
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),17)
    for j,n in enumerate(ending):
        im = frame_map[n]
        im.save(EP/'controle'/f'{tag}_contact_{n:04d}.png')
        tile = im.resize((270,480),Image.Resampling.LANCZOS)
        x,y=(j%4)*270,(j//4)*505
        board.paste(tile,(x,y))
        draw.text((x+8,y+483),f'{n/fps:.3f} s',font=font,fill='#382035')
    board.save(EP/'controle'/f'{tag}_chute_planche.png')
    for n,name in named.items():
        frame_map[n].save(EP/'controle'/f'{tag}_{name}.png')
    report = {'video':video.name,'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
              'method':'Frames decoded directly from MP4, including AAC muxed version.',
              'fps':fps,'ending_frames':ending,'named_frames':named}
    (EP/'controle'/f'{tag}_proofs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'tag':tag,'ending_frames':len(ending),'actual_decoded_frames':len(indices)}))


if __name__=='__main__':
    main()
