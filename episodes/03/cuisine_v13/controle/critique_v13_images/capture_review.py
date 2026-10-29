"""Decode the actual V13 film for the independent visual critique."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT = Path(__file__).resolve().parent
TIMES = (7.25,8.75,9.75,15.25,22.5,27.,27.45,27.8,28.125,28.4,28.85,
         29.15,29.8,30.2,31.3,32.8,33.5,34.8,36.1,36.55,37.3,39.2,40.4,40.95)
NATIVE_TIMES = (8.75,28.125,40.4)


def main():
    film = Path(sys.argv[1]).resolve()
    stage = sys.argv[2]
    assert stage in ('animatique','final')
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_entries','stream=width,height,r_frame_rate,nb_frames','-of','json',str(film)]))['streams'][0]
    fps = float(Fraction(probe['r_frame_rate']))
    width,height = int(probe['width']),int(probe['height'])
    count = int(probe['nb_frames'])
    indices = sorted({min(count-1,round(t*fps)) for t in TIMES+NATIVE_TIMES})
    selected = {min(count-1,round(t*fps)) for t in NATIVE_TIMES}
    select = 'select='+ '+'.join(f'eq(n\\,{i})' for i in indices)
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(film),'-vf',select,
        '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    frames = np.frombuffer(raw,np.uint8).reshape(len(indices),height,width,3)
    cols,tilew,tileh = 4,216,408
    sheet = Image.new('RGB',(cols*tilew,((len(indices)+cols-1)//cols)*tileh),'#FFF4E5')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),14)
    for j,(index,frame) in enumerate(zip(indices,frames)):
        image = Image.fromarray(frame)
        image.save(OUT/f'{stage}_{index:04d}.jpg',quality=91)
        if index in selected:
            image.save(OUT/f'{stage}_{index:04d}.png')
        image.thumbnail((216,384),Image.Resampling.LANCZOS)
        x,y = (j%cols)*tilew,(j//cols)*tileh
        sheet.paste(image,(x,y))
        draw.text((x+5,y+387),f'{index/fps:.3f}s · {index}',font=font,fill='#382035')
    sheet.save(OUT/f'{stage}_planche.png')
    (OUT/f'{stage}_captures.json').write_text(json.dumps({
        'film':str(film.relative_to(ROOT)),
        'sha256':hashlib.sha256(film.read_bytes()).hexdigest(),
        'fps':fps,'dimensions':[width,height],'frames':indices,
        'selected_native_png_frames':sorted(selected)},indent=2)+'\n')
    print(json.dumps({'film':str(film),'sha256':hashlib.sha256(film.read_bytes()).hexdigest(),
                      'frames':len(indices),'native_frames':sorted(selected)}))


if __name__=='__main__':
    main()
