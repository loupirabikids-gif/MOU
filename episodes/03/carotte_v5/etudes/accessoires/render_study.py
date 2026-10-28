"""Render the revised props in the approved kitchen; no character study here."""
from pathlib import Path
import importlib.util
import io
import math
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image,ImageDraw,ImageFont

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'mou_rig.py').is_file())
EP=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('props_v5',EP/'sources/art.py')
art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
ET.register_namespace('','http://www.w3.org/2000/svg')
decor=ET.parse(ROOT/'episodes/03/decor/MOU_cuisine_decor.svg').getroot()
for parent in decor.iter():
    for child in list(parent):
        if child.get('id')=='essuie-tout':parent.remove(child)
native=''.join(ET.tostring(c,encoding='unicode')for c in decor)


def svg(fragment,box,width,height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="{box}">'+native+fragment+'</svg>')


def main():
    board=Image.new('RGB',(1200,1160),'#FFF4E5');draw=ImageDraw.Draw(board)
    font=lambda n:ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),n)
    draw.text((20,12),'V5 — accessoires proposés, sans MOU',font=font(27),fill=art.INK)
    draw.text((20,49),'Le couteau coupe par son tranchant ; le rouleau perd du rayon, à hauteur fixe.',font=font(16),fill='#785F73')
    theta=math.radians(20.)
    for j in range(3):
        contact=(655.+20.*min(j,1),1380.)
        grip=(contact[0]-94*math.cos(theta)+33*math.sin(theta),contact[1]-94*math.sin(theta)-33*math.cos(theta))
        if j==0:grip=(grip[0],grip[1]-60.)
        tip=(grip[0]+150*math.cos(theta),grip[1]+150*math.sin(theta))
        c={'body':(635,1360),'cuts':j,'knife_grip':grip,'knife_tip':tip,'knife_hidden':j==2}
        data=svg(art.carrot_svg(c),'475 1238 360 205',400,245)
        (OUT/f'carotte_{j}.svg').write_text(data)
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode()))).convert('RGB')
        board.paste(im,(j*400,100))
        draw.text((j*400+16,78),f'{j} coupe(s)',font=font(19),fill=art.INK)
    stocks=[1.,.76,.42,.006,0.]
    for j,remaining in enumerate(stocks):
        data=svg(art.roll_svg({'remaining':remaining}),'754 1045 246 340',240,340)
        (OUT/f'rouleau_{j}.svg').write_text(data)
        im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode()))).convert('RGB')
        board.paste(im,(j*240,410))
        label='Départ' if j==0 else ('Carton nu' if j==4 else f'Après {j} tirage(s)')
        draw.text((j*240+10,382),label,font=font(17),fill=art.INK)
        radius=art.roll_geometry({'remaining':remaining})['radius']
        draw.text((j*240+12,756),f'r = {radius:.1f} px',font=font(16),fill='#785F73')
    draw.text((20,810),'Dernier bout : 26 × 40 px dans la scène ; dernière boulette : rayon 11 px.',font=font(18),fill=art.INK)
    fragment=(art.paper_svg({'mode':'tiny_wipe','center':(55,60)})
              +art.paper_svg({'mode':'crumple','start':(140,60),'end':(140,60),'r':11,'progress':.5,'cycle':4})
              +art._ball(230,60,11,12,4))
    data='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="270" viewBox="0 10 300 90">'+fragment+'</svg>'
    (OUT/'dernier_bout.svg').write_text(data)
    im=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode()))).convert('RGBA')
    board.paste(im,(140,835),im)
    draw.text((20,1130),'Étude des objets seuls : prises, coupe et séchage doivent encore être examinés avec MOU.',font=font(15),fill='#785F73')
    board.save(OUT/'accessoires_carotte_rouleau_v5.png')
    print(OUT/'accessoires_carotte_rouleau_v5.png')


if __name__=='__main__':main()
