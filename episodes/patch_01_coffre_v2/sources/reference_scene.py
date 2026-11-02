"""PATCH's phone is locked away; the countdown becomes his new distraction."""
from __future__ import annotations
import json
import math
from pathlib import Path
from personnage import default_state,character_svg,anchors

EP=Path(__file__).resolve().parents[1]
TIMELINE=json.loads((EP/'chronologie.json').read_text())
FPS=TIMELINE['fps'];DURATION=TIMELINE['duration']
LOCK=4.;UNLOCK=14.;PICKUP=1.70;DEPOSIT=2.80;RETRIEVE=15.05
PHONE_OFFSET=(25.,-30.)


def unit(t,a,b):return max(0.,min(1.,(t-a)/(b-a)))
def ease(t,a,b):
    x=unit(t,a,b);return x*x*(3.-2.*x)
def lerp(a,b,p):return a+(b-a)*p
def point(a,b,p):return tuple(lerp(x,y,p)for x,y in zip(a,b))
def key(t,points):
    if t<=points[0][0]:return points[0][1]
    for (a,va),(b,vb) in zip(points,points[1:]):
        if t<=b:return lerp(va,vb,ease(t,a,b))
    return points[-1][1]
def path_point(t,points):return tuple(key(t,[(a,p[k])for a,p in points])for k in (0,1))
def rotate(v,angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    return (c*v[0]-s*v[1],s*v[0]+c*v[1])


def state_at(t):
    t=max(0.,min(DURATION-1/FPS,float(t)))
    a=default_state();a['cx']=510.;a['seated']=True
    lx=key(t,[(0,0),(1.4,0),(2.5,35),(3.7,35),(4.6,0),(8.2,0),(10.4,90),
              (12.75,105),(13.6,90),(14.2,55),(15.7,0),(20,0)])
    ly=key(t,[(0,0),(2.5,22),(4.6,0),(8.2,0),(10.4,95),(12.75,110),
              (14.,95),(15.7,0),(20,0)])
    a['lean']=(lx,ly)
    a['head_tilt']=key(t,[(0,0),(.65,0),(1.15,4),(1.6,-3),(2.8,3),(4.5,0),
                         (6.15,0),(7.4,3),(10.4,11),(12.75,8),(14.2,-3),(15.7,-2)])
    a['tail_angle']=7.*math.sin(2.*math.pi*unit(t,10.6,11.5)) if 10.6<t<11.5 else 0.
    angle=key(t,[(0,0),(2.1,0),(DEPOSIT,-90),(RETRIEVE,-90),(15.7,-10.)])
    rp=path_point(t,[(0,(752,1278)),(1.40,(752,1278)),(PICKUP,(614,1390)),
        (2.1,(740,1175)),(DEPOSIT,(857,1300)),(3.05,(865,1095)),
        (3.55,(865,1280)),(3.68,(755,1378)),(3.90,(755,1397)),
        (4.10,(755,1378)),(4.65,(655,1350)),(8.2,(655,1350)),
        (10.4,(655,1350)),(12.75,(655,1350)),(13.7,(862,1275)),
        (14.2,(865,1280)),(14.75,(865,1095)),(RETRIEVE,(857,1300)),
        (15.7,(750,1190)),(20,(750,1190))])
    lp=path_point(t,[(0,(510,1316)),(.65,(510,1330)),(1.7,(510,1327)),
        (4.4,(510,1327)),(5.2,(510,1330)),(7.4,(510,1330)),
        (8.05,(505,1375)),(8.55,(390,1310)),(10.4,(390,1310)),
        (14.2,(390,1310)),(15.7,(390,1310)),(20,(390,1310))])
    grip=1. if PICKUP<=t<DEPOSIT or t>=RETRIEVE else .15
    a['hands']={'left':{'x':lp[0],'y':lp[1],'rotation':-12.,'grip':.7 if t<8.05 else .1},
                'right':{'x':rp[0],'y':rp[1],'rotation':angle if grip>.5 else -5.,'grip':grip}}
    if t<.65:
        a['pose']='concentre';a['gaze']=(-.1,1.)
    elif t<1.05:
        a['pose']='curieux';a['gaze']=(1.,.85)
    elif t<4.4:
        a['pose_weights']={'curieux':1.-ease(t,1.05,1.35),'idee':ease(t,1.05,1.35)}
        a['gaze']=(1.,.85)
    elif t<5.45:
        a['pose_weights']={'idee':1.-ease(t,4.4,4.7),'satisfait':ease(t,4.4,4.7)}
        a['gaze']=(-.1,1.)
    elif t<6.15:
        peek=ease(t,5.45,5.62)*(1.-ease(t,5.85,6.15))
        a['pose']='satisfait';a['gaze']=(lerp(-.1,1.,peek),1.)
    elif t<7.4:
        a['pose_weights']={'satisfait':1.-ease(t,6.15,6.45),'impatient':ease(t,6.15,6.45)}
        a['gaze']=(1.,1.)
    elif t<12.75:
        a['pose']='impatient';a['gaze']=(1.,1.)
    elif t<14.:
        a['pose_weights']={'impatient':1.-ease(t,12.75,13.4),'curieux':ease(t,12.75,13.4)}
        a['gaze']=(1.,1.)
    elif t<15.7:
        a['pose']='surprise';a['gaze']=(1.,.8)
    else:
        a['pose_weights']={'surprise':1.-ease(t,15.7,16.4),'idee':ease(t,15.7,16.4)}
        a['gaze']=(.9,.72)
        a['face']={'mouth_width':82.,'mouth_open':.58,'mouth_smile':1.}
    blink=1.
    for start in (1.18,4.75,6.85,9.75,11.8,16.7,19.0):
        if start<t<start+.14:blink=min(blink,1.-math.sin(math.pi*unit(t,start,start+.14)))
    a['blink']=blink
    if t<PICKUP:
        jitter=2.8*math.sin(58.*t)*math.sin(math.pi*unit(t,.65,.95)) if .65<t<.95 else 0.
        phone={'center':(639.+jitter,1360.),'angle':0.,'owner':'desk','visible':True}
    elif t<DEPOSIT or t>=RETRIEVE:
        v=rotate(PHONE_OFFSET,angle)
        phone={'center':(rp[0]+v[0],rp[1]+v[1]),'angle':angle,'owner':'right','visible':True}
    else:
        phone={'center':(827.,1275.),'angle':-90.,'owner':'box','visible':True}
    # Phone centre is exactly continuous at deposit and pickup.
    if DEPOSIT<=t<RETRIEVE:phone['visible']=t<3.55 or t>=14.2
    lid=1.-ease(t,3.0,3.55) if t<14.2 else ease(t,14.2,14.75)
    remaining=10 if t<LOCK else max(0,math.ceil(UNLOCK-t-1e-8))
    if t<2.1:camera=(20.,430.,1040.,1040.*16/9);shot='S01'
    elif t<4.4:camera=(590.,1000.,450.,800.);shot='S02'
    elif t<14.:
        p=ease(t,8.2,12.75);w=lerp(1040.,980.,p)
        camera=(lerp(20.,65.,p),lerp(430.,480.,p),w,w*16/9);shot='S03'
    else:
        p=ease(t,17.25,18.5);w=lerp(800.,1080.,p)
        camera=(lerp(220.,0.,p),lerp(660.,430.,p),w,w*16/9);shot='S04'
    return {'t':t,'actor':a,'phone':phone,'lid':lid,'remaining':remaining,
            'locked':LOCK<=t<UNLOCK,'camera':camera,'shot':shot,
            'pencil_held':t<8.05,'pencil_angle':key(t,[(0,35.),(7.4,35.),(8.05,78.)]),
            'paper_has_marks':False,'phone_deep':2.20<=t<15.30}


def path(d,fill,stroke='#3C3441',width=5.,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def phone_svg(s):
    p=s['phone']
    if not p['visible']:return ''
    x,y=p['center'];notif=s['t']>=.65
    content=(f'<rect x="-31" y="-58" width="62" height="114" rx="7" fill="{("#F7BA9B" if notif else "#ADB9CA")}"/>'
             '<path d="M-20 -29 H20 M-20 -7 H12 M-20 15 H19" stroke="#FFF5EA" stroke-width="9" stroke-linecap="round"/>')
    if notif:content+='<circle cx="23" cy="-47" r="10" fill="#E85F61" stroke="#FFF4E3" stroke-width="2"/>'
    return (f'<g id="phone" data-owner="{p["owner"]}" transform="translate({x:.5f} {y:.5f}) rotate({p["angle"]:.5f})">'
            '<rect x="-39" y="-70" width="78" height="140" rx="12" fill="#3B3947" stroke="#302D35" stroke-width="5"/>'
            +content+'<path d="M-9 -63 H9" stroke="#302D35" stroke-width="4" stroke-linecap="round"/></g>')


def pencil_svg(s):
    if s['pencil_held']:
        h=s['actor']['hands']['left'];x,y=h['x'],h['y'];angle=s['pencil_angle']
    else:
        h=state_at(8.05)['actor']['hands']['left'];x,y=h['x'],h['y'];angle=78.
    return (f'<g id="pencil" data-held="{int(s["pencil_held"])}" transform="translate({x:.5f} {y:.5f}) rotate({angle:.5f})">'
            '<path d="M-5 -53 H5 V76 L0 91 L-5 76 Z" fill="#D7AD55" stroke="#4C3A38" stroke-width="2.6"/>'
            '<path d="M-5 76 H5 L0 91 Z" fill="#F5D8AE" stroke="#4C3A38" stroke-width="1.4"/>'
            '<path d="M-2 85 H2 L0 91 Z" fill="#302D35"/>'
            '<path d="M-5 -53 H5 V-39 H-5 Z" fill="#E28B85"/></g>')


SEGMENTS={'0':'abcedf','1':'bc','2':'abged','3':'abgcd','4':'fgbc','5':'afgcd','6':'afgecd','7':'abc','8':'abcdefg','9':'abfgcd'}
def digit_svg(value,x,y):
    lines={'a':(4,0,22,0),'b':(26,4,26,22),'c':(26,30,26,48),'d':(4,52,22,52),
           'e':(0,30,0,48),'f':(0,4,0,22),'g':(4,26,22,26)}
    return ''.join(f'<path d="M{x+a} {y+b} L{x+c} {y+d}" stroke="#F9F2DF" stroke-width="5" stroke-linecap="square"/>'
                   for k in SEGMENTS[value] for a,b,c,d in [lines[k]])


def box_back(s):
    return ('<g id="box-interior">'+path('M700 1228 H990 V1458 H700 Z','#8DA6A2')
            +path('M713 1240 H975 V1312 H713 Z','#394B51',width=3.)+'</g>')


def box_front(s):
    v=f'00:{s["remaining"]:02d}';locked=s['locked'];parts=[]
    parts.append(path('M700 1295 H990 V1465 H700 Z','#B0C5BD',extra='id="box-front"'))
    parts.append(path('M990 1228 L1022 1267 V1436 L990 1465 Z','#819E99'))
    parts.append('<rect x="754" y="1335" width="200" height="86" rx="12" fill="#344149" stroke="#3C3441" stroke-width="4"/>')
    parts.append(f'<g id="timer" data-display="{v}" data-remaining="{s["remaining"]}">')
    for ch,x in zip(v.replace(':',''),(770,805,867,902)):parts.append(digit_svg(ch,x,1352))
    parts.append('<circle cx="851" cy="1368" r="3.2" fill="#F9F2DF"/><circle cx="851" cy="1389" r="3.2" fill="#F9F2DF"/></g>')
    color='#D5A656' if locked else '#D9EEE1'
    parts.append(f'<g id="lock" data-locked="{int(locked)}" transform="translate(720 1332)">')
    parts.append(path('M0 10 V1 Q12 -17 24 1 V10' if locked else 'M0 10 V1 Q12 -17 24 1', 'none',width=4.))
    parts.append('<rect x="-4" y="8" width="32" height="27" rx="4" fill="'+color+'" stroke="#3C3441" stroke-width="3"/></g>')
    pressed=3.84<=s['t']<4.02
    parts.append(f'<ellipse id="start-button" cx="731" cy="1417" rx="16" ry="{9 if pressed else 12}" fill="{("#ED7563" if pressed else "#FFF0D6")}" stroke="#3C3441" stroke-width="3"/>')
    return ''.join(parts)


def lid_svg(s):
    front_y=1295.-195.*s['lid']
    return (f'<g id="lid" data-open="{s["lid"]:.6f}">'
            +path(f'M700 1228 H990 L990 {front_y:.5f} H700 Z','#78948F',width=5.)
            +f'<path d="M714 {front_y:.5f} H978" stroke="#DBE5D8" stroke-width="5"/>'
            +f'<path d="M827 {front_y+3:.5f} H858" stroke="#344149" stroke-width="7" stroke-linecap="round"/></g>')


def background_svg():
    return ('<rect x="-600" y="-600" width="2600" height="3400" fill="#FAF1E5"/>'
            '<path d="M0 490 H1080 V1635 H0 Z" fill="#F1E6DA"/>'
            '<rect x="76" y="596" width="260" height="389" rx="126" fill="#D2DFDC" stroke="#B8C9C4" stroke-width="8"/>'
            '<path d="M205 602 V980 M80 790 H332" stroke="#F9F2E5" stroke-width="12"/>'
            '<circle cx="253" cy="688" r="38" fill="#F9E6AF"/>'
            '<path d="M798 758 H1053" stroke="#BBA9A2" stroke-width="18" stroke-linecap="round"/>'
            '<rect x="826" y="656" width="37" height="92" rx="4" fill="#D1AAA0"/>'
            '<rect x="869" y="634" width="43" height="114" rx="4" fill="#ADC3B8"/>'
            '<rect x="919" y="668" width="33" height="80" rx="4" fill="#D6BC8C"/>'
            '<rect x="-600" y="1635" width="2600" height="1400" fill="#DBD2D2"/>'
            '<path d="M-600 1635 H2000" stroke="#C9BBBE" stroke-width="4"/>')


def desk_svg():
    return (path('M140 1514 H205 V2070 H140 Z','#967F79',width=5.)
            +path('M895 1514 H958 V2070 H895 Z','#967F79',width=5.)
            +path('M65 1320 H1010 L1058 1482 H24 Z','#D7B99D',width=6.)
            +path('M24 1482 H1058 V1540 H24 Z','#B58F7E',width=6.)
            +'<path d="M44 1500 H1038" stroke="#E8CAB1" stroke-width="5"/>')


def paper_svg():
    return ('<g id="paper" data-has-marks="0">'+path('M215 1363 L567 1366 L602 1454 L178 1454 Z','#FFFEF9',stroke='#AFA4A4',width=3.)
            +'<path d="M218 1455 H595" stroke="#AA8F82" stroke-width="3" opacity=".4"/></g>')


def svg_at(t):
    s=state_at(t);a=s['actor'];c=s['camera']
    parts=[background_svg(),'<rect x="300" y="1120" width="430" height="430" rx="90" fill="#827F91"/>',
           '<defs><clipPath id="desk-body-clip"><rect x="-500" y="-600" width="2200" height="1920"/></clipPath></defs>',
           '<g clip-path="url(#desk-body-clip)">'+character_svg(a,'patch',layer='torso')+'</g>',
           desk_svg(),paper_svg(),box_back(s)]
    # The upright open lid is behind the opening; the horizontal closed lid
    # covers its contents. Switch ordering only at the edge-on position.
    lid_is_behind=s['lid']>(1295.-1228.)/195.
    if lid_is_behind:parts.append(lid_svg(s))
    if s['phone_deep']:parts.append(phone_svg(s))
    arms_behind_box=4.4<=t<13.0
    if arms_behind_box:parts.append(character_svg(a,'patch',layer='arms'))
    parts.append(box_front(s))
    if not lid_is_behind:parts.append(lid_svg(s))
    if not arms_behind_box:parts.append(character_svg(a,'patch',layer='arms'))
    if not s['phone_deep']:parts.append(phone_svg(s))
    parts.extend([pencil_svg(s),character_svg(a,'patch',layer='hands')])
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" '
            f'viewBox="{c[0]} {c[1]} {c[2]} {c[3]}" data-shot="{s["shot"]}">'+''.join(parts)+'</svg>')
