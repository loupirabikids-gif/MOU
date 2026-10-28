"""Rendered studies of the requested apron and stronger water, using the native rig."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import sys
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image,ImageDraw,ImageFont

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'mou_rig.py').is_file())
OUT=Path(__file__).resolve().parent


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m)
    return m


def render(svg,width,height):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),
        output_width=width,output_height=height))).convert('RGB')


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r=module('v5_apron_study_renderer',ROOT/'episodes/03/carotte_v5/sources/render.py')
    old=r.art
    new=module('v6_apron_water_art',ROOT/'episodes/03/cuisine_v6/sources/art.py')
    source_before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [ROOT/'mou_rig.py',ROOT/'episodes/03/carotte_v5/sources/render.py',
                             ROOT/'episodes/03/carotte_v5/sources/animation.py']}
    font=lambda size:ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),size)

    def scene(t,apron=False):
        r.art=new
        svg=r.svg_at(t)
        if apron:
            root=ET.fromstring(svg);state=r.animation.scene_state(t)
            actor=root.find("{http://www.w3.org/2000/svg}g[@id='mou-corps']")
            if actor is not None:
                x,y,scale=state['actor_transform']
                garment=ET.fromstring('<g xmlns="http://www.w3.org/2000/svg" '
                    f'transform="translate({x} {y}) scale({scale})">'+new.apron_svg(state)+'</g>')
                root.insert(list(root).index(actor)+1,garment)
            svg=ET.tostring(root,encoding='unicode')
        return svg

    samples=[('Cuisine',.5),('Tomate',8.9),('Carotte',16.083333),
             ('Petit essuyage',26.5),('Main propre',29.6)]
    width,height=360,664
    board=Image.new('RGB',(width*3,height*2+60),'#FFF4E5');draw=ImageDraw.Draw(board)
    draw.text((16,14),'V6 — étude du tablier sur MOU',font=font(25),fill='#382035')
    for i,(name,t) in enumerate(samples):
        svg=scene(t,True);dest=OUT/f'tablier_{t:.3f}.svg';dest.write_text(svg)
        im=render(svg,360,640)
        x,y=(i%3)*width,60+(i//3)*height
        board.paste(im,(x,y));draw.text((x+10,y+642),f'{name} · {t:.2f}s',font=font(15),fill='#382035')
        if i==0:im.resize((540,960),Image.Resampling.LANCZOS).save(OUT/'MOU_tablier_cuisine.png')
    draw.text((2*width+20,height+100),'Bavette corail, poche crème.',font=font(16),fill='#382035')
    draw.text((2*width+20,height+132),'Sous les deux bras natifs.',font=font(16),fill='#382035')
    draw.text((2*width+20,height+164),'Yeux et bouche dégagés.',font=font(16),fill='#382035')
    board.save(OUT/'planche_tablier_v6.png')

    waterboard=Image.new('RGB',(800,752),'#FFF4E5');draw=ImageDraw.Draw(waterboard)
    for i,(name,art) in enumerate([('V5 — petit filet',old),('V6 — débit exagéré',new)]):
        r.art=art;svg=r.svg_at(4.)
        (OUT/f'eau_{i}.svg').write_text(svg)
        im=render(svg,400,711);waterboard.paste(im,(i*400,41))
        draw.text((i*400+12,11),name,font=font(20),fill='#382035')
        if i==1:render(svg,540,960).save(OUT/'MOU_eau_exageree.png')
    waterboard.save(OUT/'comparaison_eau_v5_v6.png')
    assert source_before=={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in source_before}
    (OUT/'audit_etudes.json').write_text(json.dumps({'production_sources_unchanged':source_before,
        'art_sha256':hashlib.sha256((ROOT/'episodes/03/cuisine_v6/sources/art.py').read_bytes()).hexdigest(),
        'apron_times':[t for _,t in samples],'water_time':4.,
        'limits':'Rendered stills with V5 poses. Costume and water appearance only; V6 rhythmic movement and audio require the new full animatic.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'apron':str(OUT/'planche_tablier_v6.png'),
                      'water':str(OUT/'comparaison_eau_v5_v6.png'),'sources_unchanged':True}))


if __name__=='__main__':main()
