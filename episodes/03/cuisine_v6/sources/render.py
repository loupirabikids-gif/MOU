"""Render Encore une feuille from the approved kitchen and native MOU rig.

The lightweight animatic is 540x960 at12fps. The corrected full export is
1080x1920 at24fps. All SVG scene inputs form the content-addressed cache key.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
DECOR = EP.parent/'decor'
TIMELINE = json.loads((EP/'chronologie.json').read_text())
DURATION, FPS = float(TIMELINE['duration']), int(TIMELINE['fps'])
W, H = TIMELINE['dimensions']
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
CACHE_VERSION = 'papier-cuisine-v6'

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(EP/'sources'))
animation=module('papier_animation',EP/'sources/animation.py')
art=module('papier_art',EP/'sources/art.py')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic_write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as out:out.write(data)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def write_json(path,value):
    atomic_write(path,(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())

ET.register_namespace('','http://www.w3.org/2000/svg')
approved=ET.fromstring((DECOR/'MOU_cuisine_decor.svg').read_text())
serial=lambda e:ET.tostring(e,encoding='unicode')
DEFS=serial(next(e for e in approved if e.tag.endswith('defs')))
GROUPS={e.attrib['id']:serial(e) for e in approved if 'id'in e.attrib}
background=ET.fromstring(GROUPS['fond-cuisine'])
for parent in background.iter():
    for child in list(parent):
        if child.attrib.get('d')=='M202 1124 V1106 L221 1095':
            parent.remove(child)
BACKGROUND=serial(background)
props=ET.fromstring(GROUPS['accessoires-cuisine'])
for parent in props.iter():
    for child in list(parent):
        if child.attrib.get('id')=='essuie-tout':
            parent.remove(child)
PROPS_WITHOUT_ROLL=serial(props)
for parent in props.iter():
    for child in list(parent):
        if child.attrib.get('d','').startswith(('M810 1140','M783 1230')):
            parent.remove(child)
PROPS_PULL=serial(props)

def smooth(u):
    u=max(0.,min(1.,u));return u*u*(3.-2.*u)

def camera_at(t,state):
    # Hands-only insert on the existing sink, without the foreground island.
    if state['shot']=='sink':
        return (0.,900.,270.,270.*H/W)
    elif state['shot']=='bin':
        c=next(c for c in TIMELINE['cycles'] if c['id']==state['cycle'])
        u=smooth((t-c['zoom'][0])/.22)
        zoom=1.+1.8*u;cx=540.+(200.-540.)*u;cy=960.+(1575.-960.)*u
    elif state['phase']=='decouper_carotte':
        # Bring the two small rounds closer while retaining the eyes and hands.
        u=smooth((t-15.)/.35)*(1.-smooth((t-17.45)/.35))
        zoom=1.+.24*u;cx=540.+20.*u;cy=960.+140.*u
    elif state['cycle']==4 and 24.35<=t<27.4:
        # See the tiny scrap, wet mitten and empty tube together with the face.
        u=smooth((t-24.35)/.4)*(1.-smooth((t-27.)/.4))
        zoom=1.+.36*u;cx=540.+70.*u;cy=960.+140.*u
    else:
        zoom,cx,cy=1.,540.,960.
    width,height=W/zoom,H/zoom
    return (cx-width/2.,cy-height/2.,width,height)

def svg_at(t):
    s=animation.scene_state(float(t))
    x,y,scale=s['actor_transform']
    tr=f'translate({x:.6f} {y:.6f}) scale({scale:.6f})'
    hand=s['hands']['left']
    body=f'<g id="mou-corps" transform="{tr}">'+s['torso']+art.apron_svg(s)+'</g>'
    arms=f'<g id="mou-bras" transform="{tr}">'+s['arms']+'</g>'
    if s['shot']=='sink':
        # The character stays off screen; its original hand/forearm enters
        # naturally from the right. Cooking props belong to the wider shot.
        parts=[DEFS,BACKGROUND,art.lever_svg(float(s.get('lever',0)))]
        extension=smooth((hand[1]-1120.)/46.)*smooth((165.-hand[0])/50.)
        if s.get('water'):
            # The smaller mitten meets the jet a little lower. Keep the
            # outlet fixed and let the stream reach its visible surface.
            water_scale=1.+15./72.*extension
            parts.append(f'<g transform="translate(0 1069) scale(1 {water_scale:.8f}) translate(0 -1069)">'+art.water_svg(t,True,hand)+'</g>')
        hx,hy=hand
        hand_parts=[arms]
        if s.get('wet_hand') and not s.get('water'):
            hand_parts.append(f'<path d="M{hx-8:.3f} {hy+31:.3f} q-7 12 0 16 q7 -4 0 -16 M{hx+15:.3f} {hy+43:.3f} q-5 10 0 13 q5 -3 0 -13" fill="#B8E2E4" stroke="#668D9A" stroke-width="2.5"/>')
        parts.append(f'<g id="proportion-main-lavabo" transform="translate({hx:.6f} {hy-8.*extension:.6f}) scale(.70) translate({-hx:.6f} {-hy:.6f})">'+''.join(hand_parts)+'</g>')
        vb=camera_at(t,s)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                f'viewBox="{vb[0]:.6f} {vb[1]:.6f} {vb[2]:.6f} {vb[3]:.6f}">'
                +''.join(parts)+'</svg>')
    paper=s.get('paper')
    parts=[DEFS,BACKGROUND,art.lever_svg(float(s.get('lever',0))),body,
           GROUPS['ilot-cuisine'],PROPS_WITHOUT_ROLL,art.roll_svg(s['roll']),
           art.food_svg(t,bool(s.get('tomato_added',t>=10.85)))]
    # Cooking props stay on the worktop; tomato is removed from its dish at pick-up.
    if hasattr(art,'tomato_dish_svg'):
        parts.append(art.tomato_dish_svg(occupied=False))
    else:
        parts.append('<ellipse cx="530" cy="1281" rx="31" ry="10" fill="#FFF3E4" stroke="#382035" stroke-width="4"/>')
    tomato=s.get('tomato')
    tomato_in_front=tomato is not None and s['phase']=='ajouter_tomate'
    if tomato is not None and not tomato_in_front:
        parts.append(art.tomato_svg(*tomato))
    spoon=s.get('spoon')
    if spoon:
        parts.append(art.spoon_svg(spoon['grip'],spoon['bowl']))
    else:
        parts.append(art.parked_spoon_svg())
    parts.append(art.carrot_svg(s.get('carrot')))
    if paper and not paper.get('in_front',False):
        parts.append(art.paper_svg(paper,t))
    if s.get('water'):
        parts.append(art.water_svg(t,True,hand))
    parts.append(arms)
    if paper and paper.get('in_front',False):
        parts.append(art.paper_svg(paper,t))
    if tomato_in_front:
        parts.append(art.tomato_svg(*tomato))
    # Remaining droplets keep a wet hand legible until the towel reaches it.
    if s.get('wet_hand') and not s.get('water') and (not paper or paper['mode'] in ('pull','tiny','tiny_pull','tiny_wipe')):
        hx,hy=hand
        parts.append(f'<path d="M{hx-8:.3f} {hy+31:.3f} q-7 12 0 16 q7 -4 0 -16 M{hx+15:.3f} {hy+43:.3f} q-5 10 0 13 q5 -3 0 -13" fill="#B8E2E4" stroke="#668D9A" stroke-width="2.5"/>')
    parts.append(art.bin_svg(s['bin_count'],s.get('flying_ball')))
    vb=camera_at(t,s)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="{vb[0]:.6f} {vb[1]:.6f} {vb[2]:.6f} {vb[3]:.6f}">'
            +''.join(parts)+'</svg>')

def render_job(args):
    index,fps,scale,frames=args
    data=svg_at(index/fps).encode()
    key=hashlib.sha256(CACHE_VERSION.encode()+str(scale).encode()+data).hexdigest()
    cached=EP/'cache'/f'{key}.png'
    if not cached.exists():
        atomic_write(cached,cairosvg.svg2png(bytestring=data,output_width=round(W*scale),output_height=round(H*scale)))
    destination=Path(frames)/f'{index:05d}.png'
    raw=cached.read_bytes()
    if not destination.exists() or destination.read_bytes()!=raw:
        atomic_write(destination,raw)
    assert destination.stat().st_nlink==1
    return index

SAMPLE_TIMES=[0.5,2.58,3.23,4.0,5.9,6.8,7.8,8.3,9.2,
              10.2,10.9,12.7,13.5,14.85,15.4,16.05,16.4,16.75,
              17.45,18.6,20.0,20.6,21.85,22.5,23.6,24.8,
              25.1,25.4,26.3,27.2,28.25,29.6]

def contact_sheet(frames,fps,destination,times=SAMPLE_TIMES):
    columns,tilew,tileh=4,270,505
    sheet=Image.new('RGB',(columns*tilew,math.ceil(len(times)/columns)*tileh),'#FFF4E5')
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),14)
    for j,t in enumerate(times):
        index=min(round(DURATION*fps)-1,round(t*fps))
        im=Image.open(Path(frames)/f'{index:05d}.png').convert('RGB')
        im.thumbnail((270,480),Image.Resampling.LANCZOS)
        x,y=(j%columns)*tilew,(j//columns)*tileh
        sheet.paste(im,(x,y));draw.text((x+8,y+483),f'{index/fps:.2f}s',font=font,fill='#382035')
    b=io.BytesIO();sheet.save(b,format='PNG');atomic_write(destination,b.getvalue())

def structure_audit():
    assert digest(ROOT/'mou_rig.py')==RIG_SHA,'native rig changed'
    expected=json.loads((EP.parent/'test_remuer/controle/audit_structure.json').read_text())['decor_files_unchanged']
    assert all(digest(DECOR/name)==sha for name,sha in expected.items()),'approved decor changed'
    counts=[];contacts=[];stock=[];whistle_frames=0
    for i in range(round(DURATION*FPS)):
        t=i/FPS;s=animation.scene_state(t)
        root=ET.fromstring(svg_at(t))
        ids=[e.attrib['id'] for e in root.iter() if 'id'in e.attrib]
        assert len(ids)==len(set(ids)),(t,'duplicate SVG IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',svg_at(t))),t
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter())==2,(t,'hand count')
        visible_actor=s['shot']!='sink'
        assert sum(e.attrib.get('id')=='mouth' for e in root.iter())==int(visible_actor),(t,'mouth count')
        assert sum(e.attrib.get('data-costume')=='apron' for e in root.iter())==int(visible_actor),(t,'apron count')
        whistling=s['whistle']['amount']>0.
        assert sum(e.attrib.get('data-expression')=='whistling' for e in root.iter())==int(whistling and visible_actor),(t,'whistle mouth')
        whistle_frames+=int(whistling and visible_actor)
        counts.append(s['bin_count'])
        stock.append(s['roll']['remaining'])
        for side,point in s['hands'].items():
            assert all(math.isfinite(v) for v in point),(t,side)
        if 'arm_meta'in s:
            contacts.append({'t':t,'arms':s['arm_meta']})
    assert counts==sorted(counts),'paper disappears from bin'
    assert counts[-1]==4
    assert stock==sorted(stock,reverse=True),'paper roll regrows'
    assert stock[0]==1. and stock[-1]==0.,'roll consumption incomplete'
    return {'duration':DURATION,'fps':FPS,'frames':round(DURATION*FPS),
            'rig_sha256':RIG_SHA,'approved_decor_unchanged':expected,
            'two_hands_unique_ids_valid_references_all_frames':True,
            'bin_count_monotonic':True,'final_bin_count':4,'contacts':contacts,
            'roll_stock_monotonic_decreasing':True,'roll_stock_first_last':[stock[0],stock[-1]],
            'single_mouth_and_apron_when_actor_rendered':True,'whistling_frames':whistle_frames,
            'limits':'Vector structure and numeric checks; rendered gestures require independent visual review.'}

def encode(frames,fps,scale,tag):
    silent=EP/('MOU_Encore_une_feuille_muette.mp4' if tag=='final' else 'MOU_Encore_une_feuille_animatique_muette.mp4')
    final=EP/('MOU_Encore_une_feuille.mp4' if tag=='final' else 'MOU_Encore_une_feuille_animatique.mp4')
    temp=silent.with_name('.'+silent.name)
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(fps),'-i',str(Path(frames)/'%05d.png'),
        '-frames:v',str(round(DURATION*fps)),'-c:v','libx264','-threads','3','-preset','medium',
        '-crf','14','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temp)],check=True)
    os.replace(temp,silent)
    audio=EP/'audio/mix.wav'
    if audio.exists():
        temp=final.with_name('.'+final.name)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(audio),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
            '-t',str(DURATION),'-movflags','+faststart',str(temp)],check=True)
        os.replace(temp,final)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final if audio.exists() else silent)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert [v['width'],v['height']]==[round(W*scale),round(H*scale)]
    assert int(v['nb_frames'])==round(DURATION*fps)
    assert abs(float(probe['format']['duration'])-DURATION)<.05
    write_json(EP/'controle'/f'probe_{tag}.json',probe)
    return final if audio.exists() else silent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    fps,scale,tag=(12,.5,'animatique') if args.preview else (FPS,1.,'final')
    sources=[EP/'sources'/n for n in ('animation.py','art.py','render.py')]+[EP/'chronologie.json']
    frozen={str(p):digest(p) for p in sources}
    write_json(EP/'controle/audit_structure.json',structure_audit())
    indices=sorted({round(t*fps) for t in SAMPLE_TIMES}) if args.stills else list(range(round(DURATION*fps)))
    frames=EP/'frames'/tag;frames.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for count,_ in enumerate(pool.map(render_job,[(i,fps,scale,str(frames)) for i in indices]),1):
            if count%48==0:print(f'{tag}: {count}/{len(indices)} frames',flush=True)
    assert frozen=={str(p):digest(p) for p in sources},'source modified during render'
    contact_sheet(frames,fps,EP/'controle'/f'planche_{tag}.png')
    output=encode(frames,fps,scale,tag) if not args.stills else None
    write_json(EP/'controle'/f'sources_{tag}.json',{'sha256':frozen,'output':str(output) if output else None})
    print(json.dumps({'output':str(output),'frames':len(indices),'fps':fps,'scale':scale}),flush=True)

if __name__=='__main__':main()
