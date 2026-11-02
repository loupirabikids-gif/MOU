"""Thirty story minutes, shown through explicit ellipses and minute checks.

The validated phone/box contacts are retained from V1. The revision changes
the stakes, passage of time and visibility of the work left undone.
"""
from __future__ import annotations
import base64
from functools import lru_cache
import html
import io
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import reference_scene as ref
from personnage import character_svg

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
TIMELINE=ref.TIMELINE
FPS=TIMELINE['fps'];DURATION=TIMELINE['duration']
LOCK=4.;UNLOCK=23.;PICKUP=1.70;DEPOSIT=2.80;RETRIEVE=24.05
CHECKS=TIMELINE['time_representation']['minute_checks']


@lru_cache(maxsize=160)
def text_image(text,size,color='#3C3441'):
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),size)
    bounds=font.getbbox(text);w=bounds[2]-bounds[0]+8;h=bounds[3]-bounds[1]+8
    image=Image.new('RGBA',(w,h),(0,0,0,0))
    ImageDraw.Draw(image).text((4-bounds[0],4-bounds[1]),text,font=font,fill=color)
    buffer=io.BytesIO();image.save(buffer,format='PNG')
    return w,h,base64.b64encode(buffer.getvalue()).decode()


def text_svg(text,x,y,size,uid,color='#3C3441'):
    w,h,b64=text_image(text,size,color)
    return (f'<image id="{uid}" data-text="{html.escape(text,quote=True)}" x="{x}" y="{y}" '
            f'width="{w}" height="{h}" href="data:image/png;base64,{b64}"/>')


def minute_segment(t):
    frame=round(t*FPS)
    candidates=[m for m in CHECKS if frame>=m['frame_start']-1]
    if not candidates:return None
    m=candidates[-1];start=(m['frame_start']-1)/FPS
    end=CHECKS[m['elapsed_minute']]['frame_start']/FPS-1/FPS if m['elapsed_minute']<29 else 22.
    return m,start,end,ref.unit(t,start,end)


def legacy_time(t):
    if t<4.4:return t
    if t<6.:return ref.lerp(4.4,5.45,ref.unit(t,4.4,6.))
    if t<10.:
        start=6. if t<8. else 8.
        return ref.lerp(5.45,6.15,ref.unit(t,start,start+2.))
    if t<12.25:return ref.lerp(6.15,8.55,ref.unit(t,10.,12.25))
    if t<22.:
        m,_,_,p=minute_segment(t)
        return ref.key(m['elapsed_minute']+.3*p,[(4.,8.55),(8.,9.2),(14.,10.4),(20.,11.8),(29.5,12.75)])
    if t<23.:return ref.lerp(12.75,14.,ref.unit(t,22.,23.))
    return 14.+t-23.


def story_seconds(t):
    if t<LOCK:return 0.
    if t<6.:return t-LOCK
    if t<22.:
        m,start,_,_=minute_segment(t)
        return 60.*m['elapsed_minute']+t-start
    if t<UNLOCK:return 1799.+t-22.
    return 1800.+t-UNLOCK


def state_at(t):
    t=max(0.,min(DURATION-1/FPS,float(t)))
    old_t=legacy_time(t);s=ref.state_at(old_t);a=s['actor']
    s['legacy_t']=old_t;s['t']=t
    elapsed=story_seconds(t)
    s['story_elapsed_seconds']=elapsed
    s['remaining_seconds']=1800 if t<LOCK else max(0,math.ceil(1800.-elapsed-1e-8))
    s['remaining']=s['remaining_seconds']
    s['display']=f'{s["remaining"]//60:02d}:{s["remaining"]%60:02d}'
    s['locked']=LOCK<=t<UNLOCK
    # Fractional frame times can evaluate just below an exact minute.
    s['elapsed_minute']=min(30,int((elapsed+1e-7)//60))
    s['paper_has_marks']=False;s['completed_tasks']=0
    s['paper_insert']=26.65<=t<27.9
    s['caption']=''
    if 4.<=t<5.2:s['caption']='30 MINUTES'
    if 6.<=t<7.25:s['caption']='1 MIN LATER'
    elif 8.<=t<22.:s['caption']=f'{s["elapsed_minute"]} MIN ELAPSED'
    elif 22.<=t<23.:s['caption']='LAST SECOND'
    elif 23.<=t<25.4 or t>=27.9:s['caption']='30 MIN LATER'
    if 6.<=t<10.:
        start=6. if t<8. else 8.;p=ref.unit(t,start,start+2.)
        end_peek=.50 if start==6. else .68
        look=ref.ease(p,.05,.20)*(1.-ref.ease(p,end_peek,end_peek+.22))
        a.pop('pose',None)
        a['pose_weights']={'concentre':1.-look,'curieux' if start==6. else 'impatient':look}
        a['gaze']=(ref.lerp(-.15,1.,look),1.)
        a['head_tilt']=look*(2. if start==6. else 5.)
        # A visible return of the nib, not just an eye flick back to the page.
        a['hands']['left']['x']=510.
        a['hands']['left']['y']=ref.lerp(1312.,1332.,ref.ease(p,end_peek+.20,.98))
    elif 12.25<=t<22.:
        m,_,_,p=minute_segment(t);number=m['elapsed_minute']
        look=ref.ease(p,.04,.36)
        a['gaze']=(ref.lerp(-.10 if number<21 else .45,1.,look),1.)
        a.pop('pose_weights',None)
        a['pose']='satisfait' if number<=8 else 'impatient' if number<=14 else 'concentre' if number<=20 else 'curieux'
        a['head_tilt']+=1.7*look
        a['blink']=1.
        if number in (7,13,19,25):a['blink']=1.-.88*math.sin(math.pi*p)
    if t<2.1:s['camera']=(20.,430.,1040.,1040.*16/9);s['shot']='S01'
    elif t<4.6:s['camera']=(590.,1000.,450.,800.);s['shot']='S02'
    elif t<23.:
        p=ref.ease(t,10.,21.3);w=ref.lerp(1040.,980.,p)
        s['camera']=(ref.lerp(20.,65.,p),ref.lerp(430.,480.,p),w,w*16/9)
        s['shot']='S03' if t<12.25 else 'S04' if t<22. else 'S05'
    elif t<26.65:
        p=ref.ease(t,25.8,26.65);w=ref.lerp(800.,1080.,p)
        s['camera']=(ref.lerp(220.,0.,p),ref.lerp(660.,430.,p),w,w*16/9);s['shot']='S05'
    elif s['paper_insert']:
        s['camera']=(0.,0.,1080.,1920.);s['shot']='S06_paper'
    else:s['camera']=(0.,430.,1080.,1920.);s['shot']='S06'
    return s


def box_front(s):
    # Keep the same box geometry and controls, replacing only its display.
    tmp=dict(s,remaining=0)
    out=ref.box_front(tmp)
    import re
    parts=[f'<g id="timer" data-display="{s["display"]}" data-remaining="{s["remaining"]}">']
    for ch,x in zip(s['display'].replace(':',''),(770,805,867,902)):
        parts.append(ref.digit_svg(ch,x,1352))
    parts.append('<circle cx="851" cy="1368" r="3.2" fill="#F9F2DF"/><circle cx="851" cy="1389" r="3.2" fill="#F9F2DF"/></g>')
    out=re.sub(r'<g id="timer"[^>]*>.*?</g>',''.join(parts),out,flags=re.S)
    return out+text_svg('30 MIN',818,1303,18,'box-duration')+text_svg('MIN:SEC',817,1432,14,'box-units')


def wall_clock(s):
    minutes=s['story_elapsed_seconds']/60.
    hour=math.radians(180.+minutes*.5)
    minute=math.radians(-90.+minutes*6.)
    x,y,r=935.,965.,77.
    parts=[f'<g id="wall-clock" data-elapsed-seconds="{s["story_elapsed_seconds"]:.6f}">',
           f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFF9ED" stroke="#8C878A" stroke-width="6"/>']
    for k in range(12):
        theta=math.radians(k*30.-90.);a=(x+math.cos(theta)*62,y+math.sin(theta)*62);b=(x+math.cos(theta)*69,y+math.sin(theta)*69)
        parts.append(f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" stroke="#8C878A" stroke-width="3"/>')
    parts.extend([f'<path d="M{x} {y} L{x+40*math.cos(hour)} {y+40*math.sin(hour)}" stroke="#4E4854" stroke-width="7" stroke-linecap="round"/>',
                  f'<path d="M{x} {y} L{x+59*math.cos(minute)} {y+59*math.sin(minute)}" stroke="#D96959" stroke-width="5" stroke-linecap="round"/>',
                  f'<circle cx="{x}" cy="{y}" r="6" fill="#4E4854"/></g>'])
    return ''.join(parts)


def paper_svg(overhead=False):
    if overhead:
        parts=['<g id="paper" data-design="todo-v2" data-completed="0" data-has-marks="0">',
               ref.path('M190 440 H865 L887 1435 H175 Z','#FFFEF9',stroke='#B6A9A0',width=5.),
               text_svg('TO DO',270,520,76,'todo-header')]
        for i in range(3):
            y=760+i*200
            parts.append(f'<rect id="todo-box-{i}" data-checked="0" x="260" y="{y}" width="69" height="69" rx="4" fill="none" stroke="#9D9AA1" stroke-width="6"/>')
            parts.append(f'<path d="M385 {y+45} H783" stroke="#D7D4D5" stroke-width="7"/>')
        parts.append('</g>');return ''.join(parts)
    parts=['<g id="paper" data-design="todo-v2" data-completed="0" data-has-marks="0">',
           ref.path('M215 1363 L567 1366 L602 1454 L178 1454 Z','#FFFEF9',stroke='#AFA4A4',width=3.),
           text_svg('TO DO',235,1369,19,'todo-header')]
    for i in range(3):
        y=1394+i*18
        parts.append(f'<rect id="todo-box-{i}" data-checked="0" x="{225-i*3}" y="{y}" width="12" height="12" rx="1" fill="none" stroke="#A5A0A4" stroke-width="1.8"/>')
        parts.append(f'<path d="M255 {y+8} H{525+i*14}" stroke="#DEDBDC" stroke-width="2"/>')
    parts.append('</g>');return ''.join(parts)


def caption_svg(s):
    if not s['caption']:return ''
    text=s['caption'];w,h,_=text_image(text,43)
    return ('<g id="time-caption" data-caption="'+html.escape(text,quote=True)+'">'
            f'<rect x="70" y="155" width="{w+42}" height="{h+28}" rx="16" fill="#FFF9EE" stroke="#CFC4C4" stroke-width="2"/>'
            +text_svg(text,91,169,43,'caption-image')+'</g>')


def svg_at(t):
    s=state_at(t);a=s['actor'];c=s['camera'];old=s['legacy_t']
    if s['paper_insert']:
        body='<rect width="1080" height="1920" fill="#D7B99D"/>'+paper_svg(True)
        body+='<path d="M915 660 L933 659 L961 1320 L951 1360 L939 1320 Z" fill="#D7AD55" stroke="#4C3A38" stroke-width="4"/>'
    else:
        parts=[ref.background_svg(),wall_clock(s),'<rect x="300" y="1120" width="430" height="430" rx="90" fill="#827F91"/>',
               '<defs><clipPath id="desk-body-clip"><rect x="-500" y="-600" width="2200" height="1920"/></clipPath></defs>',
               '<g clip-path="url(#desk-body-clip)">'+character_svg(a,'patch',layer='torso')+'</g>',
               ref.desk_svg(),paper_svg(),ref.box_back(s)]
        lid_behind=s['lid']>(1295.-1228.)/195.
        if lid_behind:parts.append(ref.lid_svg(s))
        if s['phone_deep']:parts.append(ref.phone_svg(s))
        arms_behind=4.4<=old<13.
        if arms_behind:parts.append(character_svg(a,'patch',layer='arms'))
        parts.append(box_front(s))
        if not lid_behind:parts.append(ref.lid_svg(s))
        if not arms_behind:parts.append(character_svg(a,'patch',layer='arms'))
        if not s['phone_deep']:parts.append(ref.phone_svg(s))
        parts.extend([ref.pencil_svg(s),character_svg(a,'patch',layer='hands')])
        body=''.join(parts)
    # Time captions are in output coordinates, independent of camera cuts.
    overlay=(f'<svg x="{c[0]}" y="{c[1]}" width="{c[2]}" height="{c[3]}" viewBox="0 0 1080 1920">'+caption_svg(s)+'</svg>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" '
            f'viewBox="{c[0]} {c[1]} {c[2]} {c[3]}" data-shot="{s["shot"]}" data-story-seconds="{s["story_elapsed_seconds"]:.6f}">'+body+overlay+'</svg>')
