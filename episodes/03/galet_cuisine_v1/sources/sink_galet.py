"""Four close-ups of the selected floating mitten washing only its tips.

The basin and tap reuse the approved kitchen drawing. The hand is exactly the
new pebble's contour, at close-up scale, with no forearm or old MOU rig import.
All geometry exposed below comes from the actual emitted cubic control points.
"""
from __future__ import annotations

from functools import lru_cache
import math
import xml.etree.ElementTree as ET

import character

INK='#382035'
VIEWBOX=(0.,925.,270.,480.)
HAND_SCALE=.70
RINSE_TIP=(102.,1125.)
JET_POLYGON=((94.,1069.),(110.,1069.),(116.,1167.),(88.,1167.))
BASIN_BOUNDS=(55.,1115.,257.,1182.)


def _n(value):return f'{float(value):.6f}'


def _smooth(value):
    value=max(0.,min(1.,float(value)))
    return value*value*(3.-2.*value)


def _u(time,interval):return _smooth((time-interval[0])/max(1e-9,interval[1]-interval[0]))


def _mix(a,b,amount):return tuple(x+(y-x)*amount for x,y in zip(a,b))


def _path(d,fill='none',stroke=INK,width=3.,**attrs):
    extra=' '.join(f'{key.replace("_","-")}="{value}"'for key,value in attrs.items())
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{_n(width)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _ellipse(cx,cy,rx,ry,fill,stroke='none',width=0.,**attrs):
    extra=' '.join(f'{key.replace("_","-")}="{value}"'for key,value in attrs.items())
    return (f'<ellipse cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{_n(width)}" {extra}/>')


def _lever_tip(amount):
    angle=math.radians(-63.*amount)
    return (202.+19.*math.cos(angle)+11.*math.sin(angle),
            1106.+19.*math.sin(angle)-11.*math.cos(angle))


def _sample_cubics(points,samples=40):
    result=[]
    for index in range(0,len(points)-1,3):
        result.extend(character.rig.cubic(points[index:index+4],step/samples)
                      for step in range(samples+1))
    return tuple(result)


def _outline(points):
    return ('M'+_n(points[0][0])+' '+_n(points[0][1])+' '
            +' '.join('C'+' '.join(_n(value)for point in points[index:index+3]for value in point)
                       for index in range(1,len(points),3))+' Z')


def geometry_at(playback_time,cycle):
    """Return the sole mitten, its real contours, tap contact and wash state.

    `tip` is control knot 15 of the actually deformed finger-block contour,
    transformed by the hand's real scale/reflection/rotation/translation.
    The hand is re-anchored there while the thumb closes: no metadata-only
    correction or hidden forearm is used to suggest contact.
    """
    time=float(playback_time)
    opening,closing=cycle['open'],cycle['close']
    wash,water=cycle['wash'],cycle['water']
    contact=opening[0]+.58*(opening[1]-opening[0])
    close_contact=water[1]-.12
    start_tip=(420.,1119.)
    lever=0.;pinch=0.;rotation=-90.
    rub_cycles=3 if wash[1]-wash[0]>=.8 else 2
    if time<contact:
        tip=_mix(start_tip,_lever_tip(0.),_u(time,(opening[0],contact)))
        phase='reach_tap'
    elif time<opening[1]:
        lever=_u(time,(contact,opening[1]))
        tip=_lever_tip(lever);phase='open_tap'
    elif time<wash[0]:
        lever=1.
        tip=_mix(_lever_tip(1.),RINSE_TIP,_u(time,(opening[1],wash[0])))
        phase='approach_tip'
    elif time<wash[1]:
        lever=1.;progress=(time-wash[0])/(wash[1]-wash[0])
        envelope=_smooth(progress/.18)*(1.-_smooth((progress-.82)/.18))
        wave=math.sin(2.*math.pi*rub_cycles*progress)
        pinch=envelope*(.48+.16*wave)
        rotation+=2.*math.sin(4.*math.pi*progress)*envelope
        tip=(RINSE_TIP[0]+1.1*math.sin(4.*math.pi*progress),
             RINSE_TIP[1]+1.3*math.sin(6.*math.pi*progress))
        phase='rinse_tip'
    elif time<close_contact:
        lever=1.
        tip=_mix(RINSE_TIP,_lever_tip(1.),_u(time,(closing[0],close_contact)))
        phase='return_tap'
    elif time<water[1]:
        lever=1.-_u(time,(close_contact,water[1]))
        tip=_lever_tip(lever);phase='close_tap'
    else:
        tip=_mix(_lever_tip(0.),start_tip,_u(time,(water[1],cycle['sink'][1])))
        phase='withdraw'
    hand=character.hand('left',tip,rotation=rotation,pinch=pinch,
                        scale=HAND_SCALE,anchor='tip')
    local=character.rig.glove_points(pinch)
    world=tuple(character.rig.hand_local_to_world(point,hand)for point in local)
    polygon=_sample_cubics(world)
    thumb=_sample_cubics(world[6:13])
    distal=_sample_cubics(world[12:19])
    actual_tip=character.point(hand,'tip')
    half_stroke=5.7*HAND_SCALE/2.
    bounds=(min(p[0]for p in polygon)-half_stroke,min(p[1]for p in polygon)-half_stroke,
            max(p[0]for p in polygon)+half_stroke,max(p[1]for p in polygon)+half_stroke)
    water_on=water[0]<=time<water[1]
    return {'time_seconds':time,'cycle':int(cycle['id']),'phase':phase,
            'hand':hand,'side':'left','tip':actual_tip,'target_tip':tip,
            'tip_error':math.dist(actual_tip,tip),'lever':lever,
            'tap_target':_lever_tip(lever),'water':water_on,'water_on':water_on,
            'pinch':pinch,'rotation':rotation,'scale':HAND_SCALE,'rub_cycles':rub_cycles,
            'local_control_points':local,'world_control_points':world,
            'hand_polygon':polygon,'thumb_polygon':thumb,'distal_polygon':distal,
            'hand_outline_world_d':_outline(world),'hand_bounds':bounds,
            'palm_reference':character.point(hand,'grip'),
            'jet_polygon':JET_POLYGON,'jet_bounds':(88.,1069.,116.,1175.),
            'basin_bounds':BASIN_BOUNDS,'viewbox':VIEWBOX}


@lru_cache(maxsize=2)
def _background_without_sink(background):
    root=ET.fromstring(background)
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get('id')=='arriere-cuisine':parent.remove(child)
            elif child.attrib.get('d')=='M202 1124 V1106 L221 1095':parent.remove(child)
    return ET.tostring(root,encoding='unicode')


def _sink_decor():
    """Approved deep-basin drawing copied without the earlier hand layers."""
    return ('<g id="lavabo-profond">'
            +_path('M-30 1172 L18 1115 H304 V1195 H-30 Z','#DABDA8',width=7.)
            +_path('M0 1190 H303 V1490 H0 Z','#C4ADCA',width=7.)
            +_path('M170 1205 V1450',stroke='#A68AAF',width=4.)
            +_path('M45 1249 H105 M215 1249 H264',stroke='#65495F',width=7.)
            +_ellipse(157,1168,101,27,'#AE909E',opacity='.20')
            +_ellipse(156,1147,101,32,'#FFF3E4',INK,5.5)
            +_ellipse(156,1148,82,23,'#9DADB2','#75838C',3.)
            +_path('M74 1147 C87 1161 222 1161 238 1147 L230 1167 '
                   'C211 1182 101 1182 82 1167 Z','#BCCDD0','#75838C',2.7)
            +_ellipse(156,1168,13,5.3,'#8D9BA4','#65747D',1.6)
            +_ellipse(156,1168,7.5,2.6,'#5F6D79')
            +_path('M147 1167 H165 M153 1165 V1171 M159 1165 V1171',stroke='#BACACE',width=.8)
            +_path('M63 1146 C65 1188 246 1190 249 1146',stroke='#FFF8ED',width=4.)
            +_path('M159 1121 V1054 Q159 1017 128 1017 Q102 1017 102 1045 V1069',
                   stroke='#5E5267',width=15.)
            +_path('M159 1121 V1054 Q159 1027 139 1025',stroke='#C1B9C9',width=5.)
            +'</g>')


def _water(time):
    ripple=1.2*math.sin(time*31.)
    out=['<g id="lavabo-jet" data-water-flow="exaggerated">',
         _path(f'M94 1069 Q{94+ripple:.6f} 1109 88 1167 Q102 1175 116 1167 '
               f'Q{110+ripple:.6f} 1109 110 1069 Z',
               '#A8DCE5','#679DAE',1.5,opacity='.96',id='lavabo-jet-primary'),
         _path(f'M99 1072 Q{97+ripple*.3:.6f} 1115 96 1166',stroke='#F1FDFF',width=3.6),
         _path('M106 1073 Q109 1120 108 1166',stroke='#D5F3F7',width=2.5)]
    for index in range(6):
        y=1077.+((time*7.+index/6.)%1.)*83.
        out.append(_path(f'M{98.+index%2*7.} {y:.6f} l.4 5',
                         stroke='#FFFFFF',width=1.5,opacity='.8'))
    out.append('</g>')
    return ''.join(out)


def svg_at(playback_time,cycle,defs,background,art,width=1080,height=1920):
    """Full-frame insert: one floating mitten, tap action and fingertip rinse."""
    geometry=geometry_at(playback_time,cycle);time=float(playback_time)
    skin_defs=''if 'id="skin"'in defs or "id='skin'"in defs else character.defs_svg()
    parts=[defs,skin_defs,_background_without_sink(background),_sink_decor(),
           art.lever_svg(geometry['lever'])]
    if geometry['water_on']:
        parts.append(_water(time))
        parts.append('<g id="lavabo-rides-bassin">'
                     +_ellipse(104,1168,18.+2.*math.sin(time*15.),4.2,'none','#83AFBB',1.4)
                     +_ellipse(108,1169,26.+3.*math.cos(time*12.),6.,'none','#CDE6E8',1.2)+'</g>')
    parts.append(character.hand_svg('left',geometry['hand']))
    if geometry['water_on']:
        parts.append('<defs><clipPath id="lavabo-moufle-contour">'
                     f'<path d="{geometry["hand_outline_world_d"]}"/></clipPath></defs>')
        parts.append('<g id="lavabo-wet-tip" clip-path="url(#lavabo-moufle-contour)">'
                     +_path('M94 1069 H110 L116 1167 H88 Z','#B8E2E4','none',0.,opacity='.30')
                     +'</g>')
        if geometry['phase']=='rinse_tip':
            tx,ty=geometry['tip'];spray=[]
            for index in range(5):
                u=(time*6.2+index*.2)%1.
                x=tx-2.+(10.+index*1.8)*u
                y=ty+3.+24.*u-9.*math.sin(math.pi*u)
                spray.append(_ellipse(x,y,1.2,2.,'#D9F7F8','#86B3BE',.5))
            parts.append('<g id="lavabo-splash-tip">'+''.join(spray)+'</g>')
    vx,vy,vw,vh=VIEWBOX
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="{vx} {vy} {vw} {vh}">'+''.join(parts)+'</svg>')
