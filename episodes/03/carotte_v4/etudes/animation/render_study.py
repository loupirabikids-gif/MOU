from pathlib import Path
import importlib.util,io
from PIL import Image,ImageDraw,ImageFont
import cairosvg
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').exists())
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v4_render_study',ROOT/'episodes/03/carotte_v4/sources/render.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),20)
for label,times,box in [('carotte',[15.27,15.7,16.05,16.45,16.75,17.45],(330,950,900,1450)),('retenue',[26.6,27.,27.3,27.55,28.,28.6],(350,800,1000,1350))]:
    w,h=box[2]-box[0],box[3]-box[1]
    board=Image.new('RGB',(w*3,(h+35)*2),'#FFF8ED');draw=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        svg=m.svg_at(t)
        (OUT/f'{label}_{t:.2f}.svg').write_text(svg)
        png=cairosvg.svg2png(bytestring=svg.encode())
        im=Image.open(io.BytesIO(png)).convert('RGB').crop(box)
        board.paste(im,((i%3)*w,(i//3)*(h+35)))
        draw.text(((i%3)*w+10,(i//3)*(h+35)+h+3),f'{t:.2f}s',font=font,fill='#382035')
    board.save(OUT/f'etude_{label}.png')
    print(OUT/f'etude_{label}.png')
