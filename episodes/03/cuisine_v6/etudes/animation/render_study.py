"""Render the proposed rhythmic cooking and whistling from the V6 scene."""
from pathlib import Path
import ast,hashlib,importlib.util,io,json,math,subprocess,tempfile,xml.etree.ElementTree as ET

import cairosvg
from PIL import Image,ImageDraw,ImageFont

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').exists())
OUT=Path(__file__).resolve().parent
EP=OUT.parents[1]
spec=importlib.util.spec_from_file_location('v6_acting_study',EP/'sources/render.py')
render=importlib.util.module_from_spec(spec);spec.loader.exec_module(render)
font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),17)
sources=[EP/'sources'/n for n in ['animation.py','art.py','render.py']]+[EP/'chronologie.json']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):digest(p) for p in sources}
times=[.15,.40,.75,1.05,1.32,1.58,8.72,15.23,22.16]
crop=(160,620,970,1400)
tilew,tileh=486,497
board=Image.new('RGB',(tilew*3,tileh*3),'#FFF8ED');draw=ImageDraw.Draw(board)
samples=[]
for j,t in enumerate(times):
    svg=render.svg_at(t);state=render.animation.scene_state(t)
    root=ET.fromstring(svg)
    assert sum(e.get('id')=='mouth' for e in root.iter())==1
    assert sum(e.get('data-part')=='hand' for e in root.iter())==2
    (OUT/f'jeu_{t:05.2f}.svg').write_text(svg)
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=1080,output_height=1920)
    image=Image.open(io.BytesIO(png)).convert('RGB').crop(crop)
    image=image.resize((486,468),Image.Resampling.LANCZOS)
    x,y=(j%3)*tilew,(j//3)*tileh
    board.paste(image,(x,y))
    active=state['whistle']['active']
    draw.text((x+8,y+473),f'{t:.2f}s  '+('sifflement' if active else 'sourire / respiration'),font=font,fill='#382035')
    samples.append({'time':t,'actor_transform':state['actor_transform'],
                    'whistle':state['whistle'],'rhythm':state['rhythm']})
board.save(OUT/'etude_jeu_sifflement.png')

mouth_times=[.24,.40,.75,1.05,1.32,1.58]
mouth_board=Image.new('RGB',(310*3,260*2),'#FFF8ED');draw=ImageDraw.Draw(mouth_board)
for j,t in enumerate(mouth_times):
    state=render.animation.scene_state(t)
    x,y,scale=state['actor_transform']
    cx,cy=x+205*scale,y+321*scale
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=render.svg_at(t).encode()))).convert('RGB')
    image=image.crop((round(cx-72),round(cy-48),round(cx+73),round(cy+57))).resize((290,210),Image.Resampling.LANCZOS)
    xx,yy=(j%3)*310,(j//3)*260
    mouth_board.paste(image,(xx+10,yy+5))
    draw.text((xx+10,yy+224),f'{t:.2f}s  '+('note' if state['whistle']['active'] else 'silence'),font=font,fill='#382035')
mouth_board.save(OUT/'etude_bouche_unique.png')

maximum,pan_max,whistling=0.,0.,0
for index in range(720):
    t=index/24;state=render.animation.scene_state(t)
    maximum=max(maximum,max(meta['contact_error'] for meta in state['arm_meta'].values()))
    fragment=ET.fromstring('<svg>'+state['torso']+state['arms']+'</svg>')
    assert sum(e.get('id')=='mouth' for e in fragment.iter())==1
    assert sum(e.get('data-part')=='hand' for e in fragment.iter())==2
    whistling+=int(state['whistle']['active'])
    if state['phase']=='remuer':
        bx,by=state['spoon']['bowl']
        pan_max=max(pan_max,((bx-293.)/114.)**2+((by-1304.)/34.)**2)
        meta=state['arm_meta']['left']
        grip=render.animation.world_grip('left',meta['hips'],meta['clasp'],meta['rotation'],state['actor_transform'],meta['grip_depth'])
        assert math.dist(grip,state['spoon']['grip'])<.001
assert maximum<.01 and pan_max<1.
names=['controls','native_grip','world_grip','solve_arm','arm_linear_transform','_connect_left_root','soften_left_root','draw_arm']
defs=lambda p:{n.name:ast.dump(n,include_attributes=False) for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)}
old,new=defs(ROOT/'episodes/03/carotte_v5/sources/animation.py'),defs(EP/'sources/animation.py')
assert all(old[n]==new[n] for n in names)
assert before=={str(p):digest(p) for p in sources},'Source changed during acting study'
report={'samples':samples,'duration':30.,'fps':24,'states_checked':720,
        'max_programmed_grip_error':maximum,'spoon_bowl_max_pan_normalized_radius_squared':pan_max,
        'native_arm_functions_preserved':names,'one_mouth_and_two_hands_all_states':True,
        'whistling_frame_count':whistling,'sources_sha256':before,
        'limits':'Rendered acting study and numeric geometry checks; rhythm and soundtrack still need review on the actual complete encoded movie.'}
(OUT/'audit_jeu.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'study':str(OUT/'etude_jeu_sifflement.png'),'max_grip_error':maximum,'pan_max':pan_max,'whistling_frames':whistling}))
