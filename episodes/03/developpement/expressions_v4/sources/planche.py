"""Acting study using the existing MOU rig and its corrected native arms.

This renders six proposed facial intentions. It does not alter the episode,
character model, kitchen, timeline, audio or production animation sources.
"""
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
OUT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from mou_rig import DEFAULT_POSE,character_fragment,_arm

source=ROOT/'episodes/03/film/sources/animation.py'
spec=importlib.util.spec_from_file_location('mou_corrected_acting',source)
animation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(animation)

STATES=[
 {'id':'envie','title':'1. Envie de cuisiner','target':'Regard vers la poêle',
  'note':'Le plaisir précède le premier geste.',
  'pose':{'eye_open_l':1.,'eye_open_r':1.,'brow_raise':.30,
          'smile':.68,'mouth_open':.10,'pupil_x':-.72,'pupil_y':.83}},
 {'id':'doute','title':'2. Petit doute','target':'Regard vers sa main',
  'note':'Un arrêt bref après le contact.',
  'pose':{'eye_open_l':.96,'eye_open_r':1.,'brow_raise':.10,
          'brow_l':.22,'brow_r':.04,'smile':-.13,'pupil_x':0.,'pupil_y':.88}},
 {'id':'soulagement','title':'3. Soulagement éclair','target':'Regard sur la main séchée',
  'note':'Un sourire bref, puis retour à la cuisine.',
  'pose':{'eye_open_l':.81,'eye_open_r':.84,'brow_raise':.18,
          'smile':.58,'pupil_x':.03,'pupil_y':.80}},
 {'id':'concentration','title':'4. Concentration','target':'Regard vers la carotte',
  'note':'La précision prépare les deux coupes.',
  'pose':{'eye_open_l':.90,'eye_open_r':.94,'brow_raise':.02,
          'brow_l':-.23,'brow_r':-.18,'smile':.04,
          'pupil_x':-.65,'pupil_y':.87}},
 {'id':'reflexe','title':'5. Pris par son réflexe','target':'Le regard rejoint la main',
  'note':'À jouer surtout par le départ du geste.',
  'pose':{'eye_open_l':1.,'eye_open_r':1.,'brow_raise':.42,
          'brow_l':.06,'brow_r':.15,'smile':-.10,'mouth_open':.05,
          'pupil_x':.02,'pupil_y':.86}},
 {'id':'resistance','title':'6. Résistance finale','target':'Regard gourmand vers la poêle',
  'note':'Une main retient l’autre avant le papier.',
  'pose':{'eye_open_l':.90,'eye_open_r':.94,'brow_raise':.05,
          'brow_l':.22,'brow_r':.18,'smile':-.22,
          'pupil_x':-.72,'pupil_y':.85}},
]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def actor(p,uid):
    p={**DEFAULT_POSE,'arm_clasp':1.,**p}
    torso=character_fragment(p,uid=uid)
    for side in ('left','right'):
        arm=_arm(side,p['arm_hips'],p['arm_clasp'])
        assert torso.count(arm)==1
        torso=torso.replace(arm,'',1)
    arms=''.join(animation.draw_arm(side,{'hips':0.,'clasp':1.,'rotation':0.})
                 for side in ('left','right'))
    return torso+arms,p

def main():
    (OUT/'poses').mkdir(parents=True,exist_ok=True)
    w,h=1440,1250
    board=Image.new('RGB',(w,h),'#EEE6FA');draw=ImageDraw.Draw(board)
    font=lambda size:ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),size)
    draw.text((28,20),'MOU — intentions de jeu proposées',font=font(29),fill='#2B0A24')
    draw.text((28,62),'Étude du visage ; le récit se construit avec les objets, les gestes et les regards.',font=font(16),fill='#67506A')
    sources_before={str(p):digest(p) for p in [ROOT/'mou_rig.py',source]}
    manifest=[]
    for j,state in enumerate(STATES):
        x,y=(j%3)*480,105+(j//3)*550
        draw.rounded_rectangle((x+12,y,x+468,y+532),radius=20,fill='#FFF8ED')
        draw.text((x+28,y+18),state['title'],font=font(23),fill='#2B0A24')
        fragment,pose=actor(state['pose'],f'jeu-v4-{j}')
        svg=('<svg xmlns="http://www.w3.org/2000/svg" width="420" height="400" '
             'viewBox="55 105 290 355">'+fragment+'</svg>')
        root=ET.fromstring(svg)
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter())==2
        (OUT/'poses'/f'{state["id"]}.svg').write_text(svg)
        png=cairosvg.svg2png(bytestring=svg.encode())
        image=Image.open(io.BytesIO(png)).convert('RGBA')
        board.paste(image,(x+30,y+62),image)
        draw.text((x+26,y+468),state['target'],font=font(17),fill='#2B0A24')
        draw.text((x+26,y+499),state['note'],font=font(13),fill='#67506A')
        manifest.append({**state,'full_pose':pose,'svg_sha256':hashlib.sha256(svg.encode()).hexdigest()})
    draw.text((28,1211),'Les deux moufles et le modèle restent conservés. Les bras sont au repos sur cette étude.',font=font(16),fill='#67506A')
    board.save(OUT/'MOU_jeu_sans_dialogue.png')
    assert sources_before=={p:digest(Path(p)) for p in sources_before}
    (OUT/'intentions.json').write_text(json.dumps({'status':'proposed_acting_study_not_film',
        'sources_unchanged':sources_before,'states':manifest,
        'limits':'Faces and gaze suggestions only. Resting arms are shared across panels; intercepting, chopping and emotional timing require animation. Labels describe the study and are not episode dialogue.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(OUT/'MOU_jeu_sans_dialogue.png'),'dimensions':[w,h],'intentions':len(STATES),'production_sources_unchanged':True}))

if __name__=='__main__':main()
