"""Individually drawn room and desk views for PATCH's V4 staging.

Coordinates are final 1080 x 1920 output coordinates. The views have distinct
perspective surfaces and occlusion boundaries; they are not crops of one
frontal picture. Character, props, clock and their contacts belong to scene.py.
"""
from __future__ import annotations

from functools import lru_cache
import math

INK = '#493C42'
WALL = '#DCC2B6'
TOP = '#DBBE9A'
FRONT = '#BE9876'
SIDE = '#AD8269'


def _path(d, fill='none', stroke=INK, width=5., extra=''):
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _rect(x, y, w, h, fill, rx=0, stroke=INK, width=5., extra=''):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>')


def clock_placement(view):
    """Clock centre and radius, with room left around the head silhouette."""
    return {
        'wide_high': (924., 350., 106.),
        'medium': (936., 350., 112.),
        'work_close': (1120., 270., 125.),
        'low': (929., 354., 128.),
        'joy': (928., 320., 112.),
        'phone_final': (1050., 184., 138.),
        'lock_insert': (1030., 320., 125.),
        'box_insert': (1080., 250., 125.),
        'face_box': (1080., 225., 130.),
        'clock': (540., 750., 345.),
        'paper': (1040., 120., 120.),
    }[view]


def _defs(view):
    return (f'<defs><linearGradient id="{view}-wall" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#EAD8C7"/><stop offset="1" stop-color="#C9A79D"/>'
            '</linearGradient>'
            f'<linearGradient id="{view}-desk" x1="0" y1="0" x2=".8" y2="1">'
            '<stop offset="0" stop-color="#E4CCA9"/><stop offset="1" stop-color="#CFA883"/>'
            '</linearGradient>'
            f'<linearGradient id="{view}-chair" x1="0" y1="0" x2="1" y2="0">'
            '<stop offset="0" stop-color="#718691"/><stop offset="1" stop-color="#9DAFB1"/>'
            '</linearGradient>'
            f'<linearGradient id="{view}-beam" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#FFF4D9" stop-opacity=".55"/>'
            '<stop offset="1" stop-color="#FFF4D9" stop-opacity="0"/>'
            '</linearGradient></defs>')


def _window(view):
    # Window casing, glass and rays share the perspective of each room drawing.
    if view == 'wide_high':
        outer='M-70 120 L269 206 V1010 L-70 934 Z'
        inner='M-44 167 L231 236 V952 L-44 889 Z'
        cross='M93 206 V922 M-44 535 L231 603'
        sill='M-77 937 L252 1015 L294 999 L288 1040 L-77 958 Z'
    elif view == 'low':
        outer='M-75 352 L253 225 V1039 L-75 1110 Z'
        inner='M-39 391 L216 292 V1000 L-39 1064 Z'
        cross='M91 342 V1030 M-39 743 L216 668'
        sill='M-77 1080 L233 1009 L273 1020 L273 1061 L-77 1148 Z'
    elif view in ('lock_insert', 'box_insert', 'face_box', 'clock'):
        return ''
    else:
        x=-74 if view != 'phone_final' else -118
        outer=f'M{x} -45 L250 -45 V1108 H{x} Z'
        inner=f'M{x+31} 2 H212 V1066 H{x+31} Z'
        cross=f'M72 2 V1066 M{x+31} 474 H212'
        sill=f'M{x-5} 1085 H238 L279 1112 V1144 H{x-5} Z'
    glass=(f'<g id="{view}-window">'+_path(outer,'#C2B5AA',width=7.)
           +_path(inner,'#E0E8E0',stroke='#F6EAD9',width=15.)
           +_path(cross,stroke='#FFF5E1',width=14.)
           +_path(sill,'#E8D7C0',width=5.)+'</g>')
    return glass


def _room(view):
    defs=_defs(view)
    if view=='paper':
        return defs+_rect(-300,-300,1700,2600,f'url(#{view}-desk)',stroke='none')
    room=defs+_rect(-350,-350,1800,2700,f'url(#{view}-wall)',stroke='none')
    if view=='wide_high':
        room+=_path('M-100 -100 L345 -100 L345 1280 L-100 1500 Z','#D2B3A6',width=0)
        room+=_path('M345 -100 V1280',stroke='#BA998F',width=4.)
        room+=_path('M-100 1470 L345 1270 L1250 1430 V2150 H-100 Z','#BEA390',width=0.)
        for x in (-500,-200,100,400,700,1000,1300,1600):
            room+=_path(f'M{480+(x-480)*.16} 1290 L{x} 2120',stroke='#A88D7B',width=3.,extra='opacity=".55"')
        for y in (1500,1690,1960):
            room+=_path(f'M-150 {y+70} L1250 {y-100}',stroke='#A88D7B',width=3.,extra='opacity=".5"')
        room+=_path('M129 600 L300 675 L1240 1890 L490 1760 Z',f'url(#{view}-beam)',width=0.)
        room+='<ellipse cx="628" cy="1825" rx="575" ry="170" fill="#715B59" opacity=".18"/>'
    else:
        room+=_path('M-200 0 L278 0 L278 1440 L-200 1440 Z','#D8BBAE',width=0.)
        room+=_path('M278 -100 V1560',stroke='#BE9F95',width=3.,extra='opacity=".65"')
        if view not in ('lock_insert','box_insert','face_box','clock'):
            room+=_path('M35 490 L231 415 L1060 1750 L550 1930 Z',f'url(#{view}-beam)',width=0.)
        if view=='low':
            room+=_path('M-50 64 L1080 -64',stroke='#B5958C',width=6.)
        elif view in ('lock_insert','box_insert','face_box'):
            room+=_path('M-100 40 L335 -100 L1260 1080 L1060 1510 Z',f'url(#{view}-beam)',width=0.)
    room+=_window(view)
    return room


def _chair(view):
    if view in ('clock','paper','box_insert','lock_insert','face_box'):return ''
    grad=f'url(#{view}-chair)'
    if view=='wide_high':
        return ('<g id="chair-wide-high">'
                +_path('M292 876 C311 838 368 837 402 845 L663 897 Q707 907 698 957 L681 1304 Q675 1345 630 1337 L332 1292 Q288 1285 281 1245 Z',grad,width=7.)
                +_path('M315 891 Q323 867 349 873 L670 930',stroke='#B6C6C4',width=10.)
                +_path('M315 1268 L647 1318 L653 1405 Q524 1488 340 1406 Z','#748891',width=7.)
                +_path('M314 1230 C267 1206 243 1244 258 1270 L316 1304 Z','#60767F',width=6.)
                +_path('M450 1402 L463 1612 L516 1617 L505 1412 Z','#4E626B',width=6.)
                +_path('M488 1606 L326 1704 M488 1606 L655 1674',stroke='#4E626B',width=20.)+'</g>')
    if view=='low':
        return ('<g id="chair-low">'+_path('M227 1080 Q241 1021 298 1020 H729 Q780 1028 783 1084 V1450 H228 Z',grad,width=7.)
                +_path('M245 1082 Q258 1047 291 1048 H743',stroke='#B5C5C4',width=9.)+'</g>')
    if view=='joy':
        x,y,w,h=265,1080,508,620
    elif view=='phone_final':
        x,y,w,h=205,1100,652,740
    elif view=='work_close':
        x,y,w,h=120,1135,760,720
    else:x,y,w,h=245,1085,540,675
    return ('<g id="chair-'+view+'">'
            +_rect(x,y,w,h,grad,rx=112,width=7.)
            +_path(f'M{x+25} {y+104} Q{x+27} {y+27} {x+100} {y+25} H{x+w-93}',stroke='#B9C8C6',width=9.)
            +_path(f'M{x+38} {y+h-83} Q{x+w/2} {y+h-18} {x+w-34} {y+h-83} L{x+w-16} {y+h+28} Q{x+w/2} {y+h+83} {x+20} {y+h+28} Z','#7D939A',width=7.)
            +_path(f'M{x+w/2} {y+h+40} V{y+h+212}',stroke='#4F636B',width=35.)
            +_path(f'M{x+w/2-175} {y+h+240} L{x+w/2} {y+h+190} L{x+w/2+185} {y+h+240}',stroke='#4F636B',width=20.)+'</g>')


def _wide_desk():
    # Back edge is lowered enough to leave the hoodie above the work surface.
    top=(_path('M60 1260 L845 1160 L1050 1370 L300 1600 Z','url(#wide_high-desk)',width=8.)
         +_path('M73 1274 L845 1179 M315 1577 L1030 1367',stroke='#F4DDC0',width=5.))
    for d in ('M153 1301 L890 1214','M192 1358 L928 1272','M232 1413 L971 1325','M269 1472 L1009 1370','M303 1524 L812 1454'):
        top+=_path(d,stroke='#B28E70',width=2.5,extra='opacity=".47"')
    top+=_path('M340 1356 Q382 1340 428 1349 Q445 1357 411 1362 M639 1290 Q663 1275 688 1282',stroke='#A98367',width=2.3,extra='opacity=".52"')
    front=(_path('M60 1260 L300 1600 V1980 L64 1662 Z','#C4A17D',width=8.)
           +_path('M300 1600 L1050 1370 V1748 L301 1980 Z','#AF866B',width=8.)
           +_path('M60 1260 L300 1600 L1050 1370 V1416 L300 1649 L60 1302 Z','#BB9172',width=7.))
    for x,y0,y1 in ((94,1339,1672),(152,1432,1770),(216,1520,1871)):
        front+=_path(f'M{x} {y0} Q{x-7} {(y0+y1)/2} {x+3} {y1}',stroke='#A58064',width=2.5,extra='opacity=".65"')
    for d in ('M350 1670 L1005 1471','M351 1788 L1005 1589','M351 1901 L1005 1703','M463 1642 L464 1907','M721 1561 L722 1830'):
        front+=_path(d,stroke='#916C58',width=3.,extra='opacity=".5"')
    return top,front


def _front_desk(view,back,front):
    depth=front-back
    top=(_path(f'M-150 {back} H1200 L1280 {front} H-230 Z',f'url(#{view}-desk)',width=8.)
         +_path(f'M-120 {back+13} H1175',stroke='#F2DBBC',width=4.5))
    for p in (.25,.57,.82):
        yy=back+depth*p
        top+=_path(f'M-200 {yy:.2f} H1250',stroke='#B58D6D',width=2.5,extra='opacity=".42"')
    for x in (180,670,1000):
        yy=back+depth*.48
        top+=_path(f'M{x-32} {yy:.2f} q29 -10 57 0 q15 8 -16 10',stroke='#B18A6B',width=2.,extra='opacity=".45"')
    apron=(_path(f'M-230 {front} H1280 V2025 H-230 Z','#BE9878',width=8.)
           +_path(f'M-230 {front} H1280 V{front+45} H-230 Z','#B48C6D',width=7.)
           +_path(f'M-210 {front+19} H1260',stroke='#E5C4A0',width=4.))
    for x in (84,430,790,1060):
        apron+=_path(f'M{x} {front+53} Q{x-9} {(front+2025)/2} {x+3} 2040',stroke='#A47D61',width=2.5,extra='opacity=".6"')
    apron+=_path(f'M-170 {front+155} H1200',stroke='#AB8164',width=3.,extra='opacity=".5"')
    return top,apron


@lru_cache(maxsize=16)
def _fixed_layers(view):
    background=_room(view);chair=_chair(view)
    if view=='wide_high':top,front=_wide_desk()
    elif view=='medium':top,front=_front_desk(view,1384.,1570.)
    elif view=='work_close':top,front=_front_desk(view,1538.,1768.)
    elif view=='low':top,front=_front_desk(view,1426.,1486.)
    elif view=='joy':top,front=_front_desk(view,1504.,1643.)
    elif view=='phone_final':top,front=_front_desk(view,1480.,1695.)
    elif view=='lock_insert':top,front=_front_desk(view,1025.,1755.)
    elif view=='box_insert':top,front=_front_desk(view,1420.,2130.)
    elif view=='face_box':top,front=_front_desk(view,1658.,1918.)
    elif view in ('clock','paper'):top,front='',''
    else:raise ValueError('Unknown scene view: '+str(view))
    return {'background':background,'chair':chair,'tabletop':top,'front':front}


def scene_layers(view, elapsed=0., t=0.):
    """Return separate drawing layers; time values are reserved for direction.

    No clock is drawn here, so the coordinator can keep exact story time.
    This returns a new dictionary to prevent callers modifying the cache.
    """
    return dict(_fixed_layers(view))
