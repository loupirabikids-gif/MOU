"""Still proposals for MOU's recurring editorial title; production unchanged."""
from pathlib import Path
import hashlib
import importlib.util
import io
import json
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT=Path(__file__).resolve().parent
FONT=OUT/'assets/Nunito-wght.ttf'
INK='#382035';CREAM='#FFF8ED';LIME='#D8F449'
SOURCE=ROOT/'episodes/03/cuisine_v18/sources/render.py'
spec=importlib.util.spec_from_file_location('signature_native_reference',SOURCE)
ref=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ref;spec.loader.exec_module(ref)
original_svg=ref.svg_at(1.)
ref.caption_svg_at=lambda t:''
clean_svg=ref.svg_at(1.)

def font(size,weight='ExtraBold'):
    f=ImageFont.truetype(str(FONT),size)
    f.set_variation_by_name(weight)
    return f

def source_image(svg):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGBA')

def proposal(base,language='fr',card=True):
    overlay=Image.new('RGBA',base.size,(0,0,0,0));d=ImageDraw.Draw(overlay)
    if card:
        # The label belongs in the blank ceiling, above the window and left
        # of the actual hanging lamp. Nothing is painted on those objects.
        d.rounded_rectangle((80,128,468,274),radius=27,fill=CREAM,outline=INK,width=3)
    title,body,ts,bs=('LA MÉTHODE MOU','Faire simple.',31,54) if language=='fr' else ('THE MOU METHOD','Keep it simple.',29,50)
    x=104 if card else 90
    # One restrained lime accent, echoing MOU without competing with its body.
    d.rounded_rectangle((x-1,145,x+7,174),radius=4,fill=LIME)
    d.text((x+17,145),title,font=font(ts),fill=INK,anchor='lt')
    d.text((x,196),body,font=font(bs),fill=INK,anchor='lt')
    result=Image.alpha_composite(base,overlay)
    box=overlay.getbbox()
    return result,box

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    clean=source_image(clean_svg);current=source_image(original_svg)
    current.save(OUT/'MOU_titre_actuel.png')
    report={'scope':'Still proposals only; episode MP4, production sources and audio unchanged.',
            'frame_time_seconds':1.,'dimensions':[1080,1920],
            'font':'Nunito ExtraBold, SIL OFL 1.1',
            'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),
            'font_source':'https://github.com/google/fonts/tree/main/ofl/nunito',
            'versions':[]}
    images=[]
    for language,card,name in [('fr',True,'MOU_signature_proposee'),('fr',False,'MOU_signature_texte_seul'),('en',True,'MOU_signature_english')]:
        im,bbox=proposal(clean,language,card)
        im.save(OUT/f'{name}.png');im.resize((360,640),Image.Resampling.LANCZOS).save(OUT/f'{name}_mobile.png')
        # Only the proposed text panel may change the native clean frame.
        a=clean.convert('RGB');b=im.convert('RGB')
        from PIL import ImageChops
        changed=ImageChops.difference(a,b).getbbox()
        assert changed[1]>=120 and changed[3]<=278,changed
        assert changed[2]<480,changed
        report['versions'].append({'name':name,'language':language,'card':card,'overlay_bbox':bbox,'changed_pixel_bbox':changed})
        images.append(im)
    columns=[current,images[0],images[1]]
    sheet=Image.new('RGB',(1080,704),'#FAF1E5');draw=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip(columns,['Actuel','Proposition : cartouche','Alternative : texte seul'])):
        sheet.paste(im.convert('RGB').resize((360,640),Image.Resampling.LANCZOS),(i*360,64))
        draw.text((i*360+18,21),label,font=font(20),fill=INK)
    sheet.save(OUT/'MOU_comparaison_titres.png')
    (OUT/'controle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
