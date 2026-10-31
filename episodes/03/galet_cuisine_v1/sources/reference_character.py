"""Original compact pebble and independent floating mittens, drawn in SVG.

The thumb is one rounded lobe. The other fingers remain one simple mass.
This module does not import or change the previous MOU production rig.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

PALETTE=json.loads(Path(__file__).with_name('palette.json').read_text())
W,H=1080,1920
BODY_ORIGIN=(540.,1100.)
BODY_PIVOT=(0.,185.)
BODY_PATH=('M-235 25 C-245 -80 -195 -175 -78 -194 '
           'C40 -215 166 -196 220 -120 C280 -34 246 88 190 146 '
           'C130 206 -34 210 -140 168 C-208 139 -235 84 -235 25 Z')
GLOVE_OPEN=((0.,42.),(-20.,44.),(-36.,35.),(-39.,18.),
            (-40.,13.),(-40.,9.),(-40.,5.),
            (-49.,12.),(-64.,5.),(-62.,-7.),
            (-60.,-20.),(-44.,-20.),(-34.,-9.),
            (-37.,-31.),(-27.,-49.),(-8.,-53.),
            (16.,-59.),(34.,-40.),(36.,-16.),
            (41.,16.),(30.,41.),(10.,42.),
            (7.,43.),(3.,43.),(0.,42.))
GLOVE_PINCH=((0.,42.),(-20.,44.),(-36.,35.),(-39.,18.),
             (-40.,13.),(-40.,9.),(-40.,5.),
             (-42.,-13.),(-56.,-16.),(-49.,-29.),
             (-43.,-42.),(-26.,-47.),(-19.,-36.),
             (-22.,-44.),(-12.,-53.),(-4.,-53.),
             (16.,-59.),(34.,-40.),(36.,-16.),
             (41.,16.),(30.,41.),(10.,42.),
             (7.,43.),(3.,43.),(0.,42.))


def n(v):return f'{float(v):.5f}'


def cubic(points,u):
    a,b,c,d=points;v=1.-u
    return tuple(v*v*v*a[k]+3*v*v*u*b[k]+3*v*u*u*c[k]+u*u*u*d[k]for k in (0,1))


def glove_points(amount=0.):
    return tuple(tuple(a[k]+(b[k]-a[k])*amount for k in (0,1))
                 for a,b in zip(GLOVE_OPEN,GLOVE_PINCH))


def glove_path(amount=0.):
    p=glove_points(amount)
    return 'M'+n(p[0][0])+' '+n(p[0][1])+' '+ ' '.join(
        'C'+' '.join(n(v)for pt in p[j:j+3]for v in pt)
        for j in range(1,len(p),3))+' Z'


def hand_local_to_world(point,hand):
    mirror=-1. if hand.get('mirror') else 1.
    theta=math.radians(hand['rotation']);c,s=math.cos(theta),math.sin(theta)
    px,py=point[0]*mirror*hand['scale'],point[1]*hand['scale']
    return hand['x']+c*px-s*py,hand['y']+s*px+c*py


def body_local_to_world(point,body):
    px=(point[0]-BODY_PIVOT[0])*body['sx']
    py=(point[1]-BODY_PIVOT[1])*body['sy']
    angle=math.radians(body['rotation']);c,s=math.cos(angle),math.sin(angle)
    return (BODY_ORIGIN[0]+body['dx']+BODY_PIVOT[0]+c*px-s*py,
            BODY_ORIGIN[1]+body['dy']+BODY_PIVOT[1]+s*px+c*py)


def body_matrix(body):
    angle=math.radians(body['rotation']);c,s=math.cos(angle),math.sin(angle)
    a,b,cc,d=c*body['sx'],s*body['sx'],-s*body['sy'],c*body['sy']
    px,py=BODY_PIVOT;ox,oy=BODY_ORIGIN
    return (a,b,cc,d,ox+body['dx']+px-a*px-cc*py,oy+body['dy']+py-b*px-d*py)


def _path(d,fill='none',width=6.,stroke=None,extra=''):
    ink=PALETTE['ink']if stroke is None else stroke
    return f'<path d="{d}" fill="{fill}" stroke="{ink}" stroke-width="{n(width)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def _ellipse(x,y,rx,ry,fill,extra=''):
    return f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(ry)}" fill="{fill}" {extra}/>'


def face_svg(face,body):
    ink=PALETTE['ink'];parts=[]
    target=face['target']
    for side,cx,cy in (('l',-82.,-42.),('r',88.,-48.)):
        opening=face['open_'+side]*face.get('blink',1.)
        rx,ry=58.,78.
        top=cy-ry+2.*ry*(1.-opening)
        clip=f'eye-clip-{side}'
        closing=max(0.,min(1.,1.-opening/.28))
        closing=closing*closing*(3.-2.*closing)
        open_points=((cx-rx,cy),(cx-rx,cy-ry*4./3.),
                     (cx+rx,cy-ry*4./3.),(cx+rx,cy),
                     (cx+rx,cy+ry*4./3.),(cx-rx,cy+ry*4./3.))
        closed_points=((cx-rx*.85,cy+6.),(cx-rx*.85/3.,cy+10.),
                       (cx+rx*.85/3.,cy+10.),(cx+rx*.85,cy+6.),
                       (cx+rx*.85/3.,cy+10.),(cx-rx*.85/3.,cy+10.))
        pts=[tuple(a[k]+(b[k]-a[k])*closing for k in (0,1))
             for a,b in zip(open_points,closed_points)]
        pair=lambda p:n(p[0])+' '+n(p[1])
        shape=f'M{pair(pts[0])} C{pair(pts[1])} {pair(pts[2])} {pair(pts[3])} C{pair(pts[4])} {pair(pts[5])} {pair(pts[0])} Z'
        aperture=f'<path d="{shape}"/>'
        parts.append(f'<defs><clipPath id="{clip}">{aperture}</clipPath></defs>')
        parts.append(_path(shape,'#FFFEF9',0.,'none',extra=f'id="eye-white-{side}"'))
        eye_world=body_local_to_world((cx,cy),body)
        dx,dy=target[0]-eye_world[0],target[1]-eye_world[1]
        px=max(-19.,min(19.,dx*.061))
        py=max(-19.,min(20.,dy*.071))
        forward=face.get('forward_weight',1. if face.get('audience')else 0.)
        px*=1.-forward;py=py*(1.-forward)+2.*forward
        pr=face['pupil']
        parts.append(f'<g clip-path="url(#{clip})">')
        parts.append(_ellipse(cx+px,cy+py,14.5*pr,22.*pr,ink,f'id="pupil-{side}"'))
        parts.append(_ellipse(cx+px-3.,cy+py-6.,3.0,4.2,'#FFFEF9'))
        if opening<.999 and closing<.001:
            parts.append(_path(f'M{cx-rx-10} {cy-ry-10} H{cx+rx+10} V{top+3} Q{cx} {top-5} {cx-rx-10} {top-3} Z',
                               PALETTE['body'],0.,'none'))
            parts.append(_path(f'M{cx-rx-8} {top-3} Q{cx} {top-7} {cx+rx+8} {top+3}',width=5.))
        parts.append('</g>')
        parts.append(_path(shape,width=6.,extra=f'id="eye-outline-{side}"'))
        brow=face['brow_'+side];by=cy-ry-24.-face['brow_raise']*16.
        parts.append(_path(f'M{cx-42} {by+brow*17} Q{cx} {by-19} {cx+42} {by-brow*17}',width=9.,extra=f'id="brow-{side}"'))
    smile=face['smile'];skew=face['skew'];width=face['mouth_width'];op=face['mouth_open']
    if op>.02:
        parts.append(_ellipse(4.,91.,width*.5,max(3.,op*37.),ink,'id="mouth"'))
    else:
        parts.append(_path(f'M{4-width*.5} {89.-skew*5} Q{4+skew*10} {89.+smile*37} {4+width*.5} {89.+skew*5}',
                           width=6.,extra='id="mouth"'))
    return '<g id="face">'+''.join(parts)+'</g>'


def hand_svg(side,hand):
    flip=-1. if hand['mirror']else 1.
    tr=f'translate({n(hand["x"])} {n(hand["y"])}) rotate({n(hand["rotation"])}) scale({n(flip*hand["scale"])} {n(hand["scale"])})'
    return (f'<g id="hand-{side}" data-part="floating-mitten" transform="{tr}">'
            +_path(glove_path(hand['pinch']),'url(#skin)',5.7,extra=f'id="hand-outline-{side}"')+'</g>')


def crumb_svg(crumb):
    return (f'<g id="crumb" data-owner="{crumb["owner"]}" transform="translate({n(crumb["x"])} {n(crumb["y"])}) rotate({n(crumb["rotation"])})">'
            +_path('M-12 -6 Q-12 -12 -5 -11 L1 -13 Q6 -12 7 -8 Q14 -8 13 -1 L11 7 Q5 13 -2 10 Q-11 12 -13 4 Z',
                    PALETTE['crumb'],3.4,PALETTE['crumb_ink'],extra='id="crumb-outline"')
            +_path('M-5 -6 Q-1 -9 2 -6',width=2.,stroke='#FFE0A0')+'</g>')


def svg(state):
    p=PALETTE;body=state['body']
    defs=(f'<defs><linearGradient id="skin" x1="0" y1="0" x2=".45" y2="1" gradientUnits="objectBoundingBox">'
          f'<stop offset="0" stop-color="{p["light"]}"/><stop offset=".48" stop-color="{p["body"]}"/>'
          f'<stop offset="1" stop-color="{p["shade"]}"/></linearGradient>'
          '<radialGradient id="ground-shadow"><stop stop-color="#3D2540" stop-opacity=".19"/>'
          '<stop offset="1" stop-color="#3D2540" stop-opacity="0"/></radialGradient>'
          f'<clipPath id="body-clip"><path d="{BODY_PATH}"/></clipPath></defs>')
    parts=[defs,f'<rect width="1080" height="1920" fill="{p["background"]}"/>',
           '<ellipse cx="552" cy="1030" rx="448" ry="523" fill="#F6EADD"/>',
           f'<path d="M0 1370 Q540 1340 1080 1370 V1920 H0 Z" fill="{p["floor"]}"/>',
           _ellipse(548.,1347.,345.,51.,'url(#ground-shadow)')]
    for side,x,y,angle in (('l',433.,1324.,-7.),('r',650.,1324.,6.)):
        parts.append(f'<g id="foot-{side}" data-part="foot" transform="rotate({angle} {x} {y})">'+
                     _ellipse(x,y,43.,20.,p['ink'])+'</g>')
    matrix=' '.join(n(v)for v in body_matrix(body))
    parts.append(f'<g id="pebble-body" transform="matrix({matrix})">')
    parts.append(_path(BODY_PATH,'url(#skin)',7.5,extra='id="body-outline"'))
    parts.append('<g clip-path="url(#body-clip)">'+_ellipse(-105.,-125.,135.,78.,'#FFFFFF','opacity=".12"')+'</g>')
    parts.append(face_svg(state['face'],body));parts.append('</g>')
    # Both mittens remain separate world objects; there is no hidden arm.
    parts.append(hand_svg('left',state['hands']['left']))
    parts.append(hand_svg('right',state['hands']['right']))
    parts.append(crumb_svg(state['crumb']))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">'
            +''.join(parts)+'</svg>')
