"""Render the selected pebble cooking, using the approved vector kitchen."""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import wave
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent;EP=HERE.parent
ROOT=next(p for p in EP.parents if (p/'fonts/DejaVuSans-Bold.ttf').is_file())
sys.path.insert(0,str(HERE))
import animation
import art
import character
import cooking_fx
import sink_galet

W,H=1080,1920;FPS=24;DURATION=38.
DECOR=EP.parent/'decor'
ET.register_namespace('','http://www.w3.org/2000/svg')
serial=lambda e:ET.tostring(e,encoding='unicode')
approved=ET.fromstring((DECOR/'MOU_cuisine_decor.svg').read_text())
DEFS=serial(next(e for e in approved if e.tag.endswith('defs')))+character.defs_svg()
GROUPS={e.attrib['id']:serial(e)for e in approved if'id'in e.attrib}
background=ET.fromstring(GROUPS['fond-cuisine'])
for parent in background.iter():
    for child in list(parent):
        if child.attrib.get('d')=='M202 1124 V1106 L221 1095':parent.remove(child)
BACKGROUND=serial(background)
props=ET.fromstring(GROUPS['accessoires-cuisine'])
for parent in props.iter():
    for child in list(parent):
        if child.attrib.get('id')=='essuie-tout':parent.remove(child)
PROPS=serial(props)
FLOOR=('<g id="sol-prolonge-camera"><rect x="0" y="1919" width="1080" height="481" fill="#E4D6DD"/>'
       '<path d="M0 2013 H1080 M0 2124 H1080 M0 2235 H1080 M0 2346 H1080 '
       'M72 1920 L-104.44 2400 M453 1920 L409.36 2400 M850 1920 L965.73 2400" '
       'fill="none" stroke="#D6C2CB" stroke-width="3"/></g>')


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb')as f:f.write(data)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def write_json(path,data):atomic_write(path,(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode())


def _caption():
    layer=Image.new('RGBA',(W,650),(0,0,0,0));draw=ImageDraw.Draw(layer)
    draw.rounded_rectangle((60,128,480,274),radius=27,fill='#FFF8ED',outline='#382035',width=3)
    draw.rounded_rectangle((70,151,76,179),radius=3,fill='#D8F449')
    font=ImageFont.truetype(str(EP/'assets/Nunito-wght.ttf'),48);font.set_variation_by_name('ExtraBold')
    for text,y in (('Just cooking.',148),('Mostly washing.',206)):draw.text((84,y),text,font=font,anchor='lt',fill='#382035')
    b=io.BytesIO();layer.save(b,format='PNG');return base64.b64encode(b.getvalue()).decode()


CAPTION=_caption()


def camera_at(t,s):
    if s['shot']=='sink':return sink_galet.VIEWBOX
    if s['shot']=='bin':return (0.,1220.,500.,888.8888888889)
    if 8.75<=t<10.5:return (430.,1100.,440.,782.2222222222)
    if 30.25<=t<31.5:return (170.,1180.,280.,497.7777777778)
    if 2.75<=t<3.5:return (180.,620.,850.,1511.1111111111)
    if 21.<=t<23.:
        v=animation.u(t,21.,21.95);return tuple(animation.mix(x,y,v)for x,y in zip((80.,400.,1000.,1777.7777777778),(120.,550.,900.,1600.)))
    if 31.5<=t<35.75:return (70.,520.,960.,1706.6666666667)
    if t>=35.75:
        v=animation.u(min(t,37.25),35.75,37.25)
        return tuple(animation.mix(x,y,v)for x,y in zip((70.,520.,960.,1706.6666666667),(0.,0.,1080.,1920.)))
    if any(a<=t<b for a,b in ((5.75,8.),(10.5,11.),(12.75,14.25),(17.75,19.),(24.5,28.))):
        return (180.,650.,840.,1493.3333333333)
    return (0.,0.,1080.,1920.)


def trace_svg(s):
    trace=s.get('trace')
    if not trace:return''
    x,y=trace['anchor'];color=trace['color']
    return (f'<g id="trace-sur-moufle" data-trigger="tiny-cooking-trace">'
            f'<ellipse cx="{x:.5f}" cy="{y:.5f}" rx="8" ry="4.5" fill="{color}" stroke="#AE805C" stroke-width="1.5"/></g>')


def svg_at(time):
    t=float(time);s=animation.scene_state(t)
    if s['shot']=='sink':return sink_galet.svg_at(t,s['production_cycle'],DEFS,BACKGROUND,art)
    parts=[DEFS,FLOOR,BACKGROUND,art.lever_svg(0.),character.actor_svg(s)]
    # After discovering the meal, the lowered mittens stay behind the worktop.
    # They emerge above it during the deliberate presentation, without laying
    # a supposedly spotless glove over the black food in the foreground.
    if t>=30.25:parts.append(character.hands_svg(s))
    parts.extend([GROUPS['ilot-cuisine'],PROPS,art.roll_svg(s['roll']),
                  cooking_fx.food_svg(t,s,art),cooking_fx.steam_svg(t,s),art.tomato_dish_svg(False)])
    tomato=s.get('tomato')
    if tomato is not None and not s.get('tomato_held',False):parts.append(art.tomato_svg(*tomato))
    spoon=s.get('spoon')
    parts.append(art.spoon_svg(spoon['grip'],spoon['bowl'])if spoon else art.parked_spoon_svg())
    parts.append(art.carrot_svg(s.get('carrot')))
    parts.append(art.salt_svg(s.get('salt'),t,layer='bowl'))
    paper=s.get('paper')
    if paper and not paper.get('in_front'):parts.append(art.paper_svg(paper,t))
    if t<30.25:parts.append(character.hands_svg(s))
    parts.append(trace_svg(s))
    for side,a,b in (('left',35.05,35.25),('right',35.25,35.45)):
        if a<=t<b:
            amount=math.sin(math.pi*(t-a)/(b-a))
            x,y=character.point(s['hands'][side],'grip');y-=18.
            radius=10.*amount
            parts.append(f'<g id="eclat-proprete-{side}" data-effect="clean-mitten-glint">'
                         f'<path d="M{x:.5f} {y-radius:.5f} Q{x+2:.5f} {y-2:.5f} {x+radius:.5f} {y:.5f} '
                         f'Q{x+2:.5f} {y+2:.5f} {x:.5f} {y+radius:.5f} Q{x-2:.5f} {y+2:.5f} {x-radius:.5f} {y:.5f} '
                         f'Q{x-2:.5f} {y-2:.5f} {x:.5f} {y-radius:.5f} Z" fill="#FFFDF7"/></g>')
    parts.append(art.salt_svg(s.get('salt'),t,layer='grains'))
    if paper and paper.get('in_front'):parts.append(art.paper_svg(paper,t))
    if tomato is not None and s.get('tomato_held',False):parts.append(art.tomato_svg(*tomato))
    if s['wet_hand']:
        x,y=character.point(s['hands']['left'],'tip')
        parts.append(f'<g id="gouttes-bouts"><path d="M{x-4:.5f} {y+5:.5f} q-7 12 0 16 q7 -4 0 -16 M{x+10:.5f} {y+10:.5f} q-5 10 0 13 q5 -3 0 -13" fill="#B8E2E4" stroke="#668D9A" stroke-width="2.2"/></g>')
    parts.append(art.bin_svg(s['bin_count'],s['flying_ball'],s['floor_ball']))
    if 0.<=t<3.:
        opacity=1.-animation.u(t,2.85,3.)
        parts.append(f'<g id="caption-ouverture" opacity="{opacity:.8f}"><image x="0" y="0" width="1080" height="650" href="data:image/png;base64,{CAPTION}"/></g>')
    box=camera_at(t,s)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="{box[0]:.6f} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f}">'+''.join(parts)+'</svg>')


def render_job(args):
    index,scale,tag=args;svg=svg_at(index/FPS).encode()
    key=hashlib.sha256(str(scale).encode()+svg).hexdigest();cache=EP/'cache'/f'{key}.png'
    if not cache.exists():atomic_write(cache,cairosvg.svg2png(bytestring=svg,output_width=round(W*scale),output_height=round(H*scale)))
    out=EP/'frames'/tag/f'{index:05d}.png';data=cache.read_bytes()
    if not out.exists()or out.read_bytes()!=data:atomic_write(out,data)
    return str(out)


SAMPLES=(0.,1.4,2.9,3.8,4.5,5.3,6.2,6.75,7.4,7.9,8.4,9.4,9.98,10.6,11.7,13.3,14.65,
         15.3,15.9,16.9,18.3,19.2,20.3,21.8,23.6,24.8,25.45,26.05,26.8,28.3,29.4,30.8,31.85,32.7,33.8,34.5,35.4,36.3,37.5)


def sheet(frames,scale):
    tiles=(270,480);rows=math.ceil(len(SAMPLES)/4)
    out=Image.new('RGB',(1080,rows*510),'#FFF5E9');d=ImageDraw.Draw(out)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),16)
    for j,t in enumerate(SAMPLES):
        index=min(round(t*FPS),round(DURATION*FPS)-1)
        im=Image.open(frames/f'{index:05d}.png').convert('RGB');im.thumbnail(tiles,Image.Resampling.LANCZOS)
        x,y=j%4*270,j//4*510;out.paste(im,(x,y));d.text((x+6,y+484),f'{index/FPS:.2f}s',font=font,fill='#382035')
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');p.add_argument('--stills',action='store_true');p.add_argument('--silent-only',action='store_true');p.add_argument('--mux-only',action='store_true');args=p.parse_args()
    tag='animatique'if args.preview else'final';scale=.5 if args.preview else 1.
    muted=EP/('Galet_Cuisine_animatique_muette.mp4'if args.preview else'Galet_Cuisine_muette.mp4')
    final=EP/('Galet_Cuisine_animatique.mp4'if args.preview else'Galet_Cuisine.mp4')
    visual_names=('animation.py','art.py','character.py','cooking_actions.py','cooking_fx.py',
                  'costume.py','reference_character.py','render.py','sink_galet.py','palette.json')
    sources=[HERE/name for name in visual_names]+[EP/'chronologie.json',EP/'assets/Nunito-wght.ttf']
    frozen={str(p.relative_to(EP)):digest(p)for p in sources}
    if not args.mux_only:
        indices=sorted({min(round(t*FPS),911)for t in SAMPLES})if args.stills else list(range(912))
        with concurrent.futures.ProcessPoolExecutor(max_workers=3)as pool:
            for n,_ in enumerate(pool.map(render_job,[(i,scale,tag)for i in indices]),1):
                if n%48==0:print(f'{tag} {n}/{len(indices)}',flush=True)
        frames=EP/'frames'/tag;board=sheet(frames,scale);(EP/'controle').mkdir(exist_ok=True)
        board.save(EP/'controle'/f'planche_{tag}.png')
        if args.stills:return
        temporary=muted.with_name('.'+muted.name)
        subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%05d.png'),'-frames:v','912',
                        '-c:v','libx264','-threads','3','-preset','medium','-crf','10','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temporary)],check=True)
        os.replace(temporary,muted)
    audio=EP/'audio/mix.wav'
    if not args.silent_only and audio.exists():
        with wave.open(str(audio),'rb')as f:assert f.getnframes()==round(DURATION*f.getframerate())
        temporary=final.with_name('.'+final.name)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(muted),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
                        '-c:v','copy','-c:a','aac','-b:a','160k','-t','38','-movflags','+faststart',str(temporary)],check=True)
        os.replace(temporary,final)
    assert frozen=={str(p.relative_to(EP)):digest(p)for p in sources},'Sources changed during render'
    output=final if final.exists()and not args.silent_only else muted
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]))
    write_json(EP/'controle'/f'rendu_{tag}.json',{'sources_sha256':frozen,'output_sha256':digest(output),'probe':probe})
    print(output,flush=True)


if __name__=='__main__':main()
