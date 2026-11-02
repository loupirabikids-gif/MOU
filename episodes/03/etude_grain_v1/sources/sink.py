"""Five sink inserts with the rounded, articulated thumb approved by the user.

The native forearm, sink and timing remain unchanged. Only its distal hand
uses the approved isolated-study contour, fitted to each existing wash.
"""
from __future__ import annotations

from functools import lru_cache
import math
import re
import xml.etree.ElementTree as ET

import mitten

INK = '#382035'
HAND_SCALE = 2.3*.70
VIEWBOX = (0., 925., 270., 480.)
RINSE_TIP = (98., 1119.)
TIP_ANGLE = math.radians(168.)


def _n(v):
    return f'{float(v):.6f}'


def _smooth(v):
    v=max(0., min(1., float(v)))
    return v*v*(3.-2.*v)


def _u(t, interval):
    return _smooth((t-interval[0])/max(.000001, interval[1]-interval[0]))


def _mix(a, b, u):
    return a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u


def _path(d, fill='none', stroke=INK, width=3., **attrs):
    extra=' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{_n(width)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _ellipse(cx, cy, rx, ry, fill, stroke='none', width=0., **attrs):
    extra=' '.join(f'{k.replace("_", "-")}="{v}"' for k,v in attrs.items())
    return (f'<ellipse cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{_n(width)}" {extra}/>')


def _apply(matrix, point):
    a,b,c,d,e,f=matrix; x,y=point
    return a*x+c*y+e, b*x+d*y+f


def _cycle_at(t, state, animation):
    cycle=state.get('production_cycle')
    if isinstance(cycle, dict):
        return cycle
    return next(c for c in animation.PRODUCTION_TIMELINE['cycles']
                if c['sink'][0]<=t<c['sink'][1])


def _native_geometry_at(playback_time, state, animation):
    """Raw emitted geometry, suitable for independent intersection/raster QA.

    Coordinates are the SVG world coordinates before VIEWBOX projection.
    The native controls, raw hand polygon and matrix make the contact claim
    independently testable; no boolean 'fingertips correct' is substituted.
    """
    t=float(playback_time); c=_cycle_at(t,state,animation)
    opening,closing=c['open'],c['close']
    wash=c['wash']; water=c['water']
    contact=opening[0]+.58*(opening[1]-opening[0])
    reach_end=water[1]-.12
    start_tip=(420., 1119.)
    control_off=(221., 1095.)
    def lever_point(v):
        a=math.radians(-63.*v)
        return 202.+19.*math.cos(a)+11.*math.sin(a),1106.+19.*math.sin(a)-11.*math.cos(a)
    if t<contact:
        lever=0.; tip=_mix(start_tip,control_off,_u(t,(opening[0],contact)))
        phase='reach_tap'
    elif t<opening[1]:
        lever=_u(t,(contact,opening[1]));tip=lever_point(lever);phase='open_tap'
    elif t<wash[0]:
        lever=1.;tip=_mix(lever_point(1.),RINSE_TIP,_u(t,(opening[1],wash[0])))
        phase='approach_tip'
    elif t<wash[1]:
        lever=1.;v=(t-wash[0])/max(.000001,wash[1]-wash[0])
        # A two-millimetre rub at the tip, not a sweep of the forearm into water.
        tip=(RINSE_TIP[0]+1.1*math.sin(4.*math.pi*v),
             RINSE_TIP[1]+1.3*math.sin(6.*math.pi*v))
        phase='rinse_tip'
    elif t<reach_end:
        lever=1.;tip=_mix(RINSE_TIP,lever_point(1.),_u(t,(closing[0],reach_end)))
        phase='return_tap'
    elif t<water[1]:
        lever=1.-_u(t,(reach_end,water[1]));tip=lever_point(lever);phase='close_tap'
    else:
        lever=0.;tip=_mix(control_off,start_tip,_u(t,(water[1],c['sink'][1])))
        phase='withdraw'
    controls=tuple(tuple(p) for p in animation.controls('left',0.,1.))
    end=controls[-1]; tx,ty=animation._tangent(controls,1.)
    angle=TIP_ANGLE-math.atan2(ty,tx)
    ca,sa=math.cos(angle),math.sin(angle)
    a,b,cx,d=HAND_SCALE*ca,HAND_SCALE*sa,-HAND_SCALE*sa,HAND_SCALE*ca
    native_tip=(end[0]+19.*tx,end[1]+19.*ty)
    e=tip[0]-a*native_tip[0]-cx*native_tip[1]
    f=tip[1]-b*native_tip[0]-d*native_tip[1]
    matrix=(a,b,cx,d,e,f)
    native=animation._arm('left',0.,1.)
    outline=re.search(r'<path d="([^"]+)"[^>]*data-part="hand"',native)
    assert outline is not None
    points=tuple(tuple(map(float,p)) for p in re.findall(r'(-?[\d.]+) (-?[\d.]+)',outline[1]))
    centre=_apply(matrix,end)
    wrist=_apply(matrix,animation._cubic(controls,.75))
    # Full cap coordinates, independently separable from the wrist/body path.
    cap=tuple(_apply(matrix,(end[0]+(-ty*math.cos(q)+tx*math.sin(q))*19.,
                            end[1]+(tx*math.cos(q)+ty*math.sin(q))*19.))
              for q in (math.pi*j/96. for j in range(97)))
    return {'time_seconds':t,'cycle':int(c['id']),'phase':phase,'lever':lever,
            'water_on':water[0]<=t<water[1],'native_scale':HAND_SCALE,
            'native_hips':0.,'native_clasp':1.,'native_controls':controls,
            'native_outline_d':outline[1],'native_arm_svg':native,
            'matrix':matrix,'native_polygon':points,
            'hand_polygon':tuple(_apply(matrix,p) for p in points),
            'distal_cap_polygon':cap,'tip':tip,'end_centre':centre,'wrist':wrist,
            'jet_polygon':((94.,1069.),(110.,1069.),(114.,1167.),(90.,1167.)),
            'jet_bounds':(90.,1069.,114.,1167.),'basin_bounds':(55.,1115.,257.,1181.),
            'tap_target':lever_point(lever),'viewbox':VIEWBOX}


@lru_cache(maxsize=2)
def _study_reference(animation):
    cycle=animation.PRODUCTION_TIMELINE['cycles'][0]
    # Preserve the approved rinse pose's phase, rather than its old film time.
    start,end=cycle['wash']
    reference_time=start+(end-start)*(.35/1.3)
    return _native_geometry_at(reference_time,{'production_cycle':cycle},animation)


def geometry_at(playback_time, state, animation):
    """Expose the actual replacement cubics, forearm matrix and contacts.

The study's hand and the preserved forearm receive the same translation.
During tap manipulation the true rounded-fingertip boundary follows the
moving lever. That tiny local correction fades out before rinsing.
"""
    t=float(playback_time)
    c=_cycle_at(t,state,animation)
    g=_native_geometry_at(t,state,animation)
    reference=_study_reference(animation)
    a,b=c['wash']; duration=b-a
    progress=(t-a)/duration if a<=t<=b else None
    pose=mitten.pose_at(progress,3 if duration>=.8 else 2)
    open_tip=mitten.fingertip(mitten.OPEN)
    # The old native tip and the study contour's real distal edge differ by
    # a few units. Only the tap manipulation needs that registration change.
    if g['phase'] in ('reach_tap','open_tap','close_tap','withdraw'):
        tap_weight=1.
    elif g['phase']=='approach_tip':
        tap_weight=1.-_u(t,(c['open'][1],a))
    elif g['phase']=='return_tap':
        tap_weight=_u(t,(b,c['water'][1]-.12))
    else:
        tap_weight=0.
    correction=((reference['tip'][0]-open_tip[0])*tap_weight,
                (reference['tip'][1]-open_tip[1])*tap_weight)
    dx=g['matrix'][4]-reference['matrix'][4]+correction[0]
    dy=g['matrix'][5]-reference['matrix'][5]+correction[1]
    world=tuple((x+dx,y+dy) for x,y in pose['points'])
    matrix=list(g['matrix']);matrix[4]+=correction[0];matrix[5]+=correction[1]
    polygon=mitten.sample_outline(world)
    thumb=mitten.sample_outline(world[:13])
    margin=mitten.STROKE/2.
    bounds=(min(p[0] for p in thumb)-margin,min(p[1] for p in thumb)-margin,
            max(p[0] for p in thumb)+margin,max(p[1] for p in thumb)+margin)
    g.update({'native_reference_tip':reference['tip'],
              'native_tip_before_replacement':g['tip'],
              'reference_native_distal_cap_polygon':g['distal_cap_polygon'],
              'distal_cap_polygon':mitten.sample_outline(world[15:19]),
              'tip':mitten.fingertip(world),
              'wrist':(g['wrist'][0]+correction[0],g['wrist'][1]+correction[1]),
              'matrix':tuple(matrix),'hand_polygon':polygon,
              'mitten_local_points':tuple(tuple(p) for p in pose['points']),
              'mitten_world_points':world,'mitten_outline_d':mitten.outline(world),
              'mitten_translation':(dx,dy),'mitten_phase':pose['phase'],
              'mitten_progress':progress,'mitten_amount':pose['amount'],
              'rub_cycles':pose['rub_cycles'],'study_clock':pose['study_clock'],
              'thumb_bounds':bounds,'forearm_clip_x':170.+dx,
              'forearm_join_points':(world[0],world[-1]),
              'tap_registration_weight':tap_weight,
              'tap_registration_correction':correction})
    return g


@lru_cache(maxsize=2)
def _background_without_sink(background):
    root=ET.fromstring(background)
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get('id')=='arriere-cuisine':
                parent.remove(child)
    return ET.tostring(root,encoding='unicode')


def _sink_decor():
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


def _water(t):
    ripple=1.1*math.sin(t*31.)
    out=['<g id="lavabo-jet">',
         _path(f'M94 1069 Q{92+ripple:.5f} 1112 90 1167 Q102 1174 114 1167 '
               f'Q{112+ripple:.5f} 1111 110 1069 Z','#A8DCE5','#679DAE',1.5,opacity='.96',id='lavabo-jet-primary'),
         _path(f'M99 1072 Q{97+ripple*.3:.5f} 1115 96 1166',stroke='#F1FDFF',width=3.6),
         _path('M106 1073 Q109 1120 108 1166',stroke='#D5F3F7',width=2.5)]
    for j in range(4):
        y=1078.+((t*6.+j/4.)%1.)*78.
        out.append(_path(f'M{98.+j%2*7.} {y:.5f} l.4 5',stroke='#FFFFFF',width=1.5,opacity='.8'))
    out.append('</g>')
    return ''.join(out)


def svg_at(playback_time,state,animation,art,defs,background,width=1080,height=1920):
    g=geometry_at(playback_time,state,animation)
    t=float(playback_time);matrix=' '.join(_n(v) for v in g['matrix'])
    outline=g['mitten_outline_d']
    parts=[defs,_background_without_sink(background),_sink_decor(),
           art.lever_svg(g['lever'])]
    if g['water_on']:
        parts.append(_water(t))
        parts.append('<g id="lavabo-rides-bassin">'
                     +_ellipse(104,1168,18.+2.*math.sin(t*15.),4.2,'none','#83AFBB',1.4)
                     +_ellipse(108,1169,26.+3.*math.cos(t*12.),6.,'none','#CDE6E8',1.2)+'</g>')
    parts.append('<defs>'
                 f'<clipPath id="lavabo-avant-bras-conserve"><rect x="{_n(g["forearm_clip_x"])}" y="0" width="3000" height="3000"/></clipPath>'
                 f'<clipPath id="lavabo-main-contour"><path d="{outline} Z"/></clipPath>'
                 '</defs>')
    # The clipped native SVG now contains only the forearm. The real, sole
    # visible hand has its own truthful data-part marker below.
    forearm=g['native_arm_svg'].replace('data-part="hand"','data-part="forearm"')
    parts.append('<g id="lavabo-avant-bras" clip-path="url(#lavabo-avant-bras-conserve)">'
                 f'<g transform="matrix({matrix})">{forearm}</g></g>')
    parts.append(f'<path id="lavabo-main-pouce-arrondi" data-part="hand" '
                 f'data-hand-region="approved-rounded-thumb" d="{outline} Z" '
                 f'fill="{mitten.SKIN}" stroke="none"/>')
    parts.append(_path(outline,stroke=mitten.INK,width=mitten.STROKE))
    if g['water_on']:
        parts.append('<g id="lavabo-wet-tip" clip-path="url(#lavabo-main-contour)">'
                     +_path('M94 1069 H110 L114 1167 H90 Z','#B8E2E4','none',0.,opacity='.32')
                     +'</g>')
        if g['phase']=='rinse_tip':
            tipx,tipy=g['tip']
            spray=[]
            for j in range(5):
                u=(t*6.2+j*.2)%1.
                x=tipx-2.+(10.+j*1.8)*u
                y=tipy+3.+24.*u-9.*math.sin(math.pi*u)
                spray.append(_ellipse(x,y,1.2,2.,'#D9F7F8','#86B3BE',.5))
            parts.append('<g id="lavabo-splash-tip">'+''.join(spray)+'</g>')
    vx,vy,vw,vh=VIEWBOX
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="{vx} {vy} {vw} {vh}">'+''.join(parts)+'</svg>')
