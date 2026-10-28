"""Decode actual V12 edits for independent chronological visual review."""
from pathlib import Path
from fractions import Fraction
import hashlib
import io
import json
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'mou_rig.py').is_file())
TIMES=(13.458333,13.5,14.25,14.541667,15.25,15.958333,16.458333,16.5,
       18.625,21.458333,21.5,21.75,22.125,22.291667,22.5,22.958333,
       23.,26.791667,29.666667,31.5,34.958333)


def main():
    video=Path(sys.argv[1]);tag=sys.argv[2]
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
        '-show_format','-of','json',str(video)]))
    stream=next(s for s in probe['streams'] if s['codec_type']=='video')
    fps=float(Fraction(stream['avg_frame_rate']));w,h=stream['width'],stream['height']
    indices=sorted({min(int(stream['nb_frames'])-1,round(t*fps)) for t in TIMES})
    selector='select='+'+'.join(f'eq(n\\,{n})' for n in indices)
    raw=subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(video),
        '-vf',selector,'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    assert len(raw)==len(indices)*w*h*3
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),12)
    tw,th=216,408;sheet=Image.new('RGB',(tw*3,th*((len(indices)+2)//3)),'#FFF4E5')
    draw=ImageDraw.Draw(sheet)
    native_indices={round(t*fps) for t in (15.25,21.75,22.5)}
    for j,n in enumerate(indices):
        data=raw[j*w*h*3:(j+1)*w*h*3];im=Image.frombytes('RGB',(w,h),data)
        im.save(OUT/f'{tag}_{n:04d}.jpg',quality=92,subsampling=0)
        if n in native_indices: im.save(OUT/f'{tag}_{n:04d}.png')
        small=im.resize((216,384),Image.Resampling.LANCZOS);x=j%3*tw;y=j//3*th
        sheet.paste(small,(x,y));draw.text((x+7,y+387),f'{n/fps:.3f}s · {n}',font=font,fill='#382035')
    sheet.save(OUT/f'{tag}_planche.png')
    result={'video':str(video),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'width':w,'height':h,'fps':fps,'duration':probe['format']['duration'],
        'decoded_indices':indices,'decoded_times':[n/fps for n in indices],
        'selected_native_indices':sorted(native_indices)}
    (OUT/f'{tag}_captures.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
