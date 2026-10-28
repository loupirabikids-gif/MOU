from pathlib import Path
import importlib.util,io,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
import cairosvg
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').exists())
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v5_render_study',ROOT/'episodes/03/carotte_v5/sources/render.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),20)
ns={'s':'http://www.w3.org/2000/svg'}
for label,times,box in [('carotte',[15.55,15.72,16.05,16.45,16.75,17.45],(410,1000,1010,1460)),('dernier_bout',[24.65,25.05,25.45,26.15,26.6,27.2,27.55,28.2,29.5],(350,850,1000,1410))]:
    w,h=box[2]-box[0],box[3]-box[1]
    rows=(len(times)+2)//3
    board=Image.new('RGB',(w*3,(h+35)*rows),'#FFF8ED');draw=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        svg=m.svg_at(t)
        root=ET.fromstring(svg)
        root.set('viewBox','0 0 1080 1920')
        svg=ET.tostring(root,encoding='unicode')
        (OUT/f'{label}_{t:.2f}.svg').write_text(svg)
        png=cairosvg.svg2png(bytestring=svg.encode())
        im=Image.open(io.BytesIO(png)).convert('RGB').crop(box)
        board.paste(im,((i%3)*w,(i//3)*(h+35)))
        draw.text(((i%3)*w+10,(i//3)*(h+35)+h+3),f'{t:.2f}s',font=font,fill='#382035')
    board.save(OUT/f'etude_{label}.png')
    print(OUT/f'etude_{label}.png')
