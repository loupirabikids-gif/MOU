"""Render Encore une feuille from the approved kitchen and native MOU rig.

The lightweight animatic is 540x960 at12fps. The corrected full export is
1080x1920 at24fps. All SVG scene inputs form the content-addressed cache key.
"""
from __future__ import annotations
import argparse
import base64
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
import wave

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
DECOR = EP.parent/'decor'
TIMELINE = json.loads((EP/'chronologie.json').read_text())
DURATION, FPS = float(TIMELINE['duration']), int(TIMELINE['fps'])
W, H = TIMELINE['dimensions']
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
CACHE_VERSION = 'papier-sel-pouce-arrondi-v14'
CAPTION_TEXT = 'Just cooking. Mostly washing.'
CAPTION_END = 3.
CAPTION_FONT = EP/'assets/Nunito-wght.ttf'
CAPTION_BOUNDS = (60.,128.,480.,274.)


def caption_image():
    """Render the approved text with the bundled font, independent of fontconfig."""
    layer=Image.new('RGBA',(W,650),(0,0,0,0))
    draw=ImageDraw.Draw(layer)
    draw.rounded_rectangle(CAPTION_BOUNDS,radius=27,fill='#FFF8ED',outline='#382035',width=3)
    draw.rounded_rectangle((70,151,76,179),radius=3,fill='#D8F449')
    for text,y in [('Just cooking.',148),('Mostly washing.',206)]:
        font=ImageFont.truetype(str(CAPTION_FONT),48)
        font.set_variation_by_name('ExtraBold')
        draw.text((84,y),text,font=font,anchor='lt',fill='#382035')
    data=io.BytesIO();layer.save(data,format='PNG')
    return base64.b64encode(data.getvalue()).decode('ascii')


CAPTION_IMAGE = caption_image()

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
sink=module('mou_lavabo_v14',EP/'sources/sink.py')
costume=module('mou_costume_chef_v20',EP/'sources/costume.py')
cooking_fx=module('mou_cooking_fx_v26',EP/'sources/cooking_fx.py')

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
# Close camera frames expose more floor than the original 1920px artboard.
# Continue its original fill and tile lines in SVG, retaining the approved art.
FLOOR_EXTENSION=('<g id="sol-prolonge-camera">'
    '<rect x="0" y="1919" width="1080" height="481" fill="#E4D6DD"/>'
    '<path d="M0 2013 H1080 M0 2124 H1080 M0 2235 H1080 M0 2346 H1080 '
    'M72 1920 L-104.44 2400 M453 1920 L409.36 2400 '
    'M850 1920 L965.73 2400" fill="none" stroke="#D6C2CB" stroke-width="3"/>'
    '</g>')
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


def caption_svg_at(playback_time):
    if not 0.<=playback_time<CAPTION_END:
        return ''
    opacity=1.-smooth((playback_time-(CAPTION_END-.15))/.15)
    return (f'<g id="caption-ouverture" data-caption="{CAPTION_TEXT}" opacity="{opacity:.8f}">'
            f'<image x="0" y="0" width="{W}" height="650" '
            f'href="data:image/png;base64,{CAPTION_IMAGE}"/></g>')

def camera_at(t,state):
    clock=float(state.get('production_time',t))
    if state['shot']=='sink':return sink.VIEWBOX
    if 2.75<=clock<3.50:return (260.,480.,620.,1102.2222222222)
    if 30.25<=clock<31.50:return (170.,1180.,280.,497.7777777778)
    if state.get('camera_viewbox') is not None:return tuple(state['camera_viewbox'])
    if state['shot']=='bin':return (0.,1020.,500.,888.8888888889)
    if 8.75<=clock<10.50:return (430.,1100.,440.,782.2222222222)
    if 21.<=clock<23.:
        u=smooth((clock-21.)/1.7)
        return (100.+80.*u,250.+170.*u,900.-140.*u,(900.-140.*u)*16./9.)
    if 31.5<=clock<35.75:return (30.,160.,1020.,1813.3333333333)
    if clock>=35.75:
        u=smooth((min(clock,37.25)-35.75)/1.5)
        return (30.*(1.-u),160.*(1.-u),1020.+60.*u,(1020.+60.*u)*16./9.)
    if any(a<=clock<b for a,b in ((5.75,8.),(10.5,11.),(12.75,14.25),(17.75,19.),(24.5,28.))):
        return (100.,250.,900.,1600.)
    return (0.,0.,1080.,1920.)


def apron_water_svg(state):
    amount=float(state.get('apron_wetness',0.))
    if amount<=0.:
        return ''
    cx,cy=state.get('contact_apron',{}).get('native_point',(195.,370.))
    return (f'<g id="tablier-humide" data-effect="wet-cloth" opacity="{amount:.6f}" '
            f'transform="translate({cx-195.:.6f} {cy-370.:.6f})">'
            '<path d="M185 370 C186 364 194 362 201 363 '
            'C209 363 217 365 219 370 C221 376 213 379 204 379 '
            'C196 381 186 377 185 370 Z" '
            'fill="#8EBAC6" opacity=".60"/></g>')

def ending_drop_svg(state):
    drop=state.get('ending_drop')
    if not drop or float(drop.get('amount',0.))<=0.:
        return ''
    x,y=drop['anchor'];amount=float(drop['amount'])
    return (f'<g id="derniere-goutte" data-effect="attached-water-drop" opacity="{amount:.6f}">'
            f'<path d="M{x:.5f} {y:.5f} '
            f'C{x-2:.5f} {y+7:.5f} {x-9:.5f} {y+13:.5f} {x-7:.5f} {y+19:.5f} '
            f'C{x-5:.5f} {y+28:.5f} {x+8:.5f} {y+28:.5f} {x+8:.5f} {y+19:.5f} '
            f'C{x+8:.5f} {y+12:.5f} {x+2:.5f} {y+6:.5f} {x:.5f} {y:.5f} Z" '
            'fill="#B8E2E4" stroke="#668D9A" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M{x-3:.5f} {y+17:.5f} q-2 5 1 7" fill="none" '
            'stroke="#FFFDF7" stroke-width="2.5" stroke-linecap="round"/></g>')

def hand_trace_svg(t,state):
    """Expose the tiny trigger before each wash; no mark survives the rinse."""
    intervals=((2.75,3.5,'#D99455'),(10.5,11.,'#D99455'),
               (16.,16.25,'#CC6959'),(21.,23.,'#FFF8E8'))
    active=next((color for a,b,color in intervals if a<=t<b),None)
    if active is None:return ''
    x,y=state['hands']['left']
    return (f'<g id="trace-sur-moufle" data-trigger="tiny-cooking-trace">'
            f'<ellipse cx="{x+4:.5f}" cy="{y-8:.5f}" rx="6" ry="3.5" '
            f'fill="{active}" stroke="#AE805C" stroke-width="1.2"/>'
            f'<circle cx="{x-5:.5f}" cy="{y-13:.5f}" r="2.5" fill="{active}"/></g>')


def svg_at(t):
    playback_time=float(t)
    s=animation.scene_state(playback_time)
    t=float(s['t'])
    x,y,scale=s['actor_transform']
    tr=f'translate({x:.6f} {y:.6f}) scale({scale:.6f})'
    hand=s['hands']['left']
    upper=s['torso']+costume.costume_svg(s)+apron_water_svg(s)
    arms_native=s['arms']
    performance=s.get('performance_affine_svg')
    if performance:
        upper=(s.get('grounded_feet','')
               +f'<g data-performance="upper-body" transform="{performance}">'+upper+'</g>')
        arms_native=f'<g data-performance="native-arms" transform="{performance}">'+arms_native+'</g>'
    body=f'<g id="mou-corps" transform="{tr}">'+upper+'</g>'
    arms=f'<g id="mou-bras" transform="{tr}">'+arms_native+'</g>'
    if s['shot']=='sink':
        return sink.svg_at(playback_time,s,animation,art,DEFS,BACKGROUND,width=W,height=H)
    if s.get('pro_shot')=='macro_apron':
        vb=camera_at(t,s)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                f'viewBox="{vb[0]:.8f} {vb[1]:.8f} {vb[2]:.8f} {vb[3]:.8f}">'
                +DEFS+f'<rect x="{vb[0]-10}" y="{vb[1]-10}" width="{vb[2]+20}" height="{vb[3]+20}" fill="#FFF8ED"/>'
                +body+arms+ending_drop_svg(s)+'</svg>')
    paper=s.get('paper')
    parts=[DEFS,FLOOR_EXTENSION,BACKGROUND,art.lever_svg(float(s.get('lever',0))),body,
           GROUPS['ilot-cuisine'],PROPS_WITHOUT_ROLL,art.roll_svg(s['roll']),
           cooking_fx.food_svg(playback_time,s,art),
           cooking_fx.steam_svg(playback_time,s)]
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
    if hasattr(art,'salt_svg'):
        parts.append(art.salt_svg(s.get('salt'),playback_time,layer='bowl'))
    if paper and not paper.get('in_front',False):
        parts.append(art.paper_svg(paper,t))
    if s.get('water'):
        parts.append(art.water_svg(t,True,hand))
    parts.append(arms)
    parts.append(hand_trace_svg(playback_time,s))
    parts.append(ending_drop_svg(s))
    if hasattr(art,'salt_svg'):
        parts.append(art.salt_svg(s.get('salt'),playback_time,layer='grains'))
    if paper and paper.get('in_front',False):
        parts.append(art.paper_svg(paper,t))
    if tomato_in_front:
        parts.append(art.tomato_svg(*tomato))
    # Remaining droplets keep a wet hand legible until the towel reaches it.
    if s.get('wet_hand') and not s.get('water') and (not paper or paper['mode'] in ('pull','tiny','tiny_pull','tiny_wipe')):
        hx,hy=hand
        parts.append(f'<path d="M{hx-8:.3f} {hy+31:.3f} q-7 12 0 16 q7 -4 0 -16 M{hx+15:.3f} {hy+43:.3f} q-5 10 0 13 q5 -3 0 -13" fill="#B8E2E4" stroke="#668D9A" stroke-width="2.5"/>')
    parts.append(art.bin_svg(s['bin_count'],s.get('flying_ball'),s.get('floor_ball')))
    parts.append(caption_svg_at(playback_time))
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
        # Same complete SVG/scale/version key: unchanged frames can reuse
        # the previously verified raster cache. New title frames miss it.
        candidates=[EP.parent/name/'cache'/f'{key}.png' for name in ('cuisine_v24','cuisine_v23','cuisine_v22','cuisine_v20','cuisine_v14')]
        previous=next((p for p in candidates if p.is_file()),None)
        raw=previous.read_bytes() if previous is not None else cairosvg.svg2png(bytestring=data,output_width=round(W*scale),output_height=round(H*scale))
        atomic_write(cached,raw)
    destination=Path(frames)/f'{index:05d}.png'
    raw=cached.read_bytes()
    if not destination.exists() or destination.read_bytes()!=raw:
        atomic_write(destination,raw)
    assert destination.stat().st_nlink==1
    return index

SAMPLE_TIMES=[0.,1.5,2.9,4.2,6.6,7.3,8.4,9.4,10.75,11.7,13.3,14.6,
 15.6,16.85,18.3,19.2,20.3,21.4,22.15,23.65,24.9,25.65,26.1,26.6,
 27.2,28.25,29.04,29.4,29.9,30.8,31.8,32.5,33.8,34.7,35.5,36.5,37.5]

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
        expected_hands=1 if s['shot']=='sink' and sink is not None else 2
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter())==expected_hands,(t,'hand count')
        visible_actor=s['shot']!='sink'
        assert sum(e.attrib.get('id')=='mouth' for e in root.iter())==int(visible_actor),(t,'mouth count')
        assert sum(e.attrib.get('data-costume')=='apron' for e in root.iter())==int(visible_actor),(t,'apron count')
        assert sum(e.attrib.get('data-costume')=='chef-hat' for e in root.iter())==int(visible_actor),(t,'chef hat count')
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
    assert counts[-1]==3
    assert stock==sorted(stock,reverse=True),'paper roll regrows'
    assert stock[0]==1. and stock[-1]==0.,'roll consumption incomplete'
    return {'duration':DURATION,'fps':FPS,'frames':round(DURATION*FPS),
            'rig_sha256':RIG_SHA,'approved_decor_unchanged':expected,
            'two_native_hands_wide_one_approved_mitten_sink_unique_ids_valid':True,
            'bin_count_monotonic':True,'final_bin_count':3,'final_discarded_paper_count':4,'contacts':contacts,
            'roll_stock_monotonic_decreasing':True,'roll_stock_first_last':[stock[0],stock[-1]],
            'single_mouth_apron_and_chef_hat_when_actor_rendered':True,'whistling_frames':whistle_frames,
            'limits':'Vector structure and numeric checks; rendered gestures require independent visual review.'}

def encode(frames,fps,scale,tag,include_audio=True):
    silent=EP/('MOU_Encore_une_feuille_muette.mp4' if tag=='final' else 'MOU_Encore_une_feuille_animatique_muette.mp4')
    final=EP/('MOU_Encore_une_feuille.mp4' if tag=='final' else 'MOU_Encore_une_feuille_animatique.mp4')
    temp=silent.with_name('.'+silent.name)
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(fps),'-i',str(Path(frames)/'%05d.png'),
        '-frames:v',str(round(DURATION*fps)),'-c:v','libx264','-threads','3','-preset','medium',
        '-crf',str(8 if tag=='final' else 12),'-pix_fmt','yuv420p','-an','-movflags','+faststart',str(temp)],check=True)
    os.replace(temp,silent)
    audio=EP/'audio/mix.wav'
    if include_audio and audio.exists():
        with wave.open(str(audio),'rb') as src:
            assert src.getnframes()==round(DURATION*src.getframerate()), 'audio duration is not V26'
        temp=final.with_name('.'+final.name)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(audio),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
            '-t',str(DURATION),'-movflags','+faststart',str(temp)],check=True)
        os.replace(temp,final)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final if include_audio and audio.exists() else silent)]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert [v['width'],v['height']]==[round(W*scale),round(H*scale)]
    assert int(v['nb_frames'])==round(DURATION*fps)
    assert abs(float(probe['format']['duration'])-DURATION)<.05
    write_json(EP/'controle'/f'probe_{tag}.json',probe)
    return final if include_audio and audio.exists() else silent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preview',action='store_true')
    parser.add_argument('--stills',action='store_true')
    parser.add_argument('--silent-only',action='store_true',help='Encode the visual animatic while audio is being prepared independently')
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    fps,scale,tag=(FPS,.5,'animatique') if args.preview else (FPS,1.,'final')
    assert sink is not None,'the approved rounded-thumb sink module is required for V14'
    sources=[EP/'sources'/n for n in ('animation.py','art.py','render.py','sink.py','mitten.py','costume.py','acting.py','poses.json','jeu_visage.py','visage.py','expressions.json','performance.py','cooking_fx.py','reference_animation.py','reference_performance.py','reference_jeu_visage.py','reference_acting.py')]+[EP/'chronologie.json',EP/'chronologie_reference_v25.json']
    sources.extend([p for p in (EP/'sources').glob('motion*.py')])
    sources.append(CAPTION_FONT)
    sources.append(ROOT/'fonts/DejaVuSans-Bold.ttf')
    frozen={str(p):digest(p) for p in sources}
    write_json(EP/'controle/audit_structure.json',structure_audit())
    indices=sorted({round(t*fps) for t in SAMPLE_TIMES}) if args.stills else list(range(round(DURATION*fps)))
    frames=EP/'frames'/tag;frames.mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        for count,_ in enumerate(pool.map(render_job,[(i,fps,scale,str(frames)) for i in indices]),1):
            if count%48==0:print(f'{tag}: {count}/{len(indices)} frames',flush=True)
    assert frozen=={str(p):digest(p) for p in sources},'source modified during render'
    contact_sheet(frames,fps,EP/'controle'/f'planche_{tag}.png')
    output=encode(frames,fps,scale,tag,include_audio=not args.silent_only) if not args.stills else None
    write_json(EP/'controle'/f'sources_{tag}.json',{'sha256':frozen,'output':str(output) if output else None})
    print(json.dumps({'output':str(output),'frames':len(indices),'fps':fps,'scale':scale}),flush=True)

if __name__=='__main__':main()
