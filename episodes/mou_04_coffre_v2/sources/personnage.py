"""The canonical lime MOU, adapted to the lockbox's world-space contacts.

Body, two oval eyes, brows, mouth and dark feet come from mou_rig_original.
Only articulated arm control points and expression parameters are adapted.
The legacy acting parameters are retained as a data vocabulary, never drawn.
"""
from __future__ import annotations
from copy import deepcopy
import html
import math
import re
import xml.etree.ElementTree as ET

import mou_rig_original as rig
from jeu_support import BASE, POSES, face_parameters, default_state

INK=rig.PALETTE['outline'];FUR=rig.PALETTE['skin'];WHITE=rig.PALETTE['eye_white']
BASE_SCALE=2.
SHOULDERS={'left':(105.,291.),'right':(297.,291.)}
REST_HANDS={'left':(178.,389.),'right':(225.,389.)}


def clamp(v,a=0.,b=1.):return max(a,min(b,float(v)))
def n(v):return f'{float(v):.5f}'
def _pt(a,b,u):return tuple(x+(y-x)*u for x,y in zip(a,b))


def matrix(state):
    unit=float(state.get('scale',1.));scale=BASE_SCALE*unit
    angle=math.radians(float(state.get('body_tilt',0.)));c,s=math.cos(angle),math.sin(angle)
    lx,ly=state.get('lean',(0.,0.))
    cx=float(state.get('cx',540.))-35.*unit+lx
    floor=float(state.get('floor_y',1570.))-150.*unit+ly
    return c*scale,s*scale,-s*scale,c*scale,cx-scale*(205.*c-449.*s),floor-scale*(205.*s+449.*c)


def to_world(point,state):
    a,b,c,d,tx,ty=matrix(state);x,y=point
    return a*x+c*y+tx,b*x+d*y+ty


def to_local(point,state):
    a,b,c,d,tx,ty=matrix(state);x,y=point[0]-tx,point[1]-ty;det=a*d-b*c
    return (d*x-c*y)/det,(-b*x+a*y)/det


def _hand(side,state):
    h=state.get('hands',{}).get(side,{})
    if isinstance(h,(list,tuple)):h=dict(x=h[0],y=h[1])
    default=to_world(REST_HANDS[side],state)
    return dict(x=float(h.get('x',default[0])),y=float(h.get('y',default[1])),rotation=float(h.get('rotation',0.)),grip=clamp(h.get('grip',0.)))


def feet_local(state):
    spread=clamp(state.get('jump_spread',0.))
    return {'left':(151.-14.*spread,437.-8.*spread),'right':(252.+14.*spread,437.-8.*spread)}


def _arm_controls(side,state):
    hand=_hand(side,state);h=to_local((hand['x'],hand['y']),state);s=SHOULDERS[side]
    explicit=state.get('elbows',{}).get(side)
    e=to_local(explicit,state) if explicit is not None else ((s[0]+h[0])*.5+(-15. if side=='left' else 15.),(s[1]+h[1])*.5+17.)
    supplied=state.get('wrists',{}).get(side)
    if supplied is not None:
        w=to_local(tuple(supplied),state)
        dx,dy=h[0]-w[0],h[1]-w[1]
        length=max(1.e-7,math.hypot(dx,dy));tx,ty=dx/length,dy/length
        # Native mitten grip is16 local units in front of its last cubic point.
        # Keep the hand target exact; the external wrist controls its direction.
        w=(h[0]-16.*tx,h[1]-16.*ty)
    else:
        dx,dy=h[0]-e[0],h[1]-e[1]
        length=max(1.e-7,math.hypot(dx,dy));tx,ty=dx/length,dy/length
        radial=(h[0]-s[0],h[1]-s[1]);distance=max(1.e-7,math.hypot(*radial))
        amount=clamp((distance-60.)/50.)
        tx=(1.-amount)*radial[0]/distance+amount*tx
        ty=(1.-amount)*radial[1]/distance+amount*ty
        length=max(1.e-7,math.hypot(tx,ty));tx,ty=tx/length,ty/length
        if side=='left' and state.get('performance_state')=='whole_body_joy':
            # The free palm comes back across the belly before the second
            # phone grip. Its inherited elbow can point the terminal tangent
            # backward through the widening mitten and create a tiny hook.
            # Keep that tangent in the forward reach cone; targets stay exact.
            rx,ry=radial[0]/distance,radial[1]/distance
            dot=tx*rx+ty*ry
            if dot<.65:
                u=clamp((.65-dot)/max(1.e-7,1.-dot))
                tx,ty=(1.-u)*tx+u*rx,(1.-u)*ty+u*ry
                length=max(1.e-7,math.hypot(tx,ty));tx,ty=tx/length,ty/length
        w=(h[0]-16.*tx,h[1]-16.*ty)
    reach=math.hypot(w[0]-s[0],w[1]-s[1])
    # Keep the elbow control away from the distal cap. A cubic handle next
    # to the hand makes its offset contour reverse into a hook/double outline.
    ex,ey=e[0]-s[0],e[1]-s[1];elbow_length=max(1.e-7,math.hypot(ex,ey))
    limit=reach*.62
    if elbow_length>limit:e=(s[0]+ex*limit/elbow_length,s[1]+ey*limit/elbow_length)
    tangent=min(38.,max(12.,reach*.30))
    c2=(w[0]-tx*tangent,w[1]-ty*tangent)
    # Existing elbow controls give a curve; arm and rounded end share topology.
    return (s,e,c2,w),h


def anchors(state):
    hsx,hsy=state.get('head_shift',(0.,0.))
    hands={};wrists={}
    for side in SHOULDERS:
        controls,h=_arm_controls(side,state)
        hands[side]=to_world(h,state);wrists[side]=to_world(controls[-1],state)
    return {'head':to_world((205.+hsx*.5,235.+hsy*.5),state),
            'shoulders':{side:to_world(p,state) for side,p in SHOULDERS.items()},
            'hands':hands,'wrists':wrists,
            'feet':{side:to_world(p,state) for side,p in feet_local(state).items()}}


def _arm_art(side,state,uid,hands_only=False):
    controls,hand=_arm_controls(side,state);left=[];right=[];count=64
    for j in range(count+1):
        t=j/count;x,y=rig._cubic(controls,t);tx,ty=rig._tangent(controls,t)
        amount=clamp((t-.75)/.25);amount=amount*amount*(3.-2.*amount)
        radius=10.5+8.5*amount
        left.append((x-ty*radius,y+tx*radius));right.append((x+ty*radius,y-tx*radius))
    ex,ey=controls[-1];tx,ty=rig._tangent(controls,1.)
    tip=[]
    for j in range(1,25):
        a=math.pi*j/24.
        tip.append((ex+(-ty*math.cos(a)+tx*math.sin(a))*19.,ey+(tx*math.cos(a)+ty*math.sin(a))*19.))
    boundary=left+tip+list(reversed(right[:-1]))
    coord=lambda p:f'{p[0]:.5f} {p[1]:.5f}'
    contour='M'+' L'.join(coord(p) for p in boundary)
    art=rig._path(contour+' Z',FUR,'none',0)+rig._path(contour,sw=5.2)
    if hands_only:
        start=int(count*.73)
        distal=left[start:]+tip+list(reversed(right[start:-1]))
        clip_id=f'{uid}-mitten-region-{side}'
        clip='M'+' L'.join(coord(p) for p in distal)+' Z'
        return (f'<defs><clipPath id="{clip_id}"><path d="{clip}"/></clipPath></defs>'
                f'<g id="{uid}-hand-{side}" data-part="mitten-paw" data-native-rig="continuous-rounded-end" '
                f'clip-path="url(#{clip_id})">'+art+'</g>')
    return f'<g id="{uid}-arm-{side}" data-part="continuous-mou-arm">'+art+'</g>'


def _native_pose(state):
    f=face_parameters(state);blink=clamp(state.get('blink',1.));gx,gy=state.get('gaze',(.4,-.35))
    p=dict(rig.DEFAULT_POSE,
        eye_open_l=clamp(f['open_l'])*blink,eye_open_r=clamp(f['open_r'])*blink,
        pupil_x=clamp(gx,-1.,1.),pupil_y=clamp(gy,-1.,1.),
        brow_l=clamp((f['brow_l0']-f['brow_l1'])/30.,-1.,1.),
        brow_r=clamp((f['brow_r1']-f['brow_r0'])/30.,-1.,1.),
        brow_raise=clamp((f['brow_raise_l']+f['brow_raise_r'])/28.,-1.,1.),
        smile=clamp(f['mouth_smile'],-1.,1.),mouth_open=clamp(f['mouth_open']))
    # Finish a blink on the native closed arc instead of leaving an empty
    # green lens when the shrinking aperture overtakes the eyelid/pupil.
    for side in ('l','r'):
        if p['eye_open_'+side]<.30:p['eye_open_'+side]=0.
    return p,f


def _face(state,uid):
    p,f=_native_pose(state);eyes=[]
    for side,cx,cy,rx in [('l',164.,235.,34.),('r',242.,232.,33.)]:
        eye=rig._eye(cx,cy,rx*clamp(f['eye_scale'],.9,1.12),side,p,uid)
        pupil=clamp(f['pupil']/14.,.75,1.22)
        eye=eye.replace('rx="9.300" ry="15.000"',f'rx="{9.3*pupil:.3f}" ry="{15.*pupil:.3f}"',1)
        if f['sparkle']>.1:
            op=p['eye_open_'+side]
            x=cx+p['pupil_x']*15.-3.;y=cy+2.+p['pupil_y']*13.+17.*(1.-op)-5.
            spot=rig._ellipse(x,y,2.8,3.8,WHITE,opacity=n(clamp(f['sparkle'])))
            eye=re.sub(r'(<ellipse[^>]+fill="#2B0A24"[^>]*/>)',lambda m:m.group(1)+spot,eye,count=1)
        eyes.append(f'<g id="{uid}-eye-display-{side}">'+eye+'</g>')
    brows=rig._brows(p)
    shape=state.get('mouth_shape')
    if shape in ('o','breath'):
        op=(.72*float(state.get('mouth_o_scale',1.))) if shape=='o' else p['mouth_open']
        rx=10.5 if shape=='o' else max(7.,f['mouth_width']*.25)
        mouth=f'<g id="mouth" data-mouth-shape="round">'+rig._ellipse(205.,321.,rx,max(1.,op*25.),INK,INK,3.4)+'</g>'
    else:mouth=rig._mouth(p,uid)
    hsx,hsy=state.get('head_shift',(0.,0.));angle=float(state.get('head_tilt',0.))
    transform=f'translate({hsx*.5:.5f} {hsy*.5:.5f}) rotate({angle:.5f} 205 235)'
    return f'<g id="{uid}-face" transform="{transform}">'+''.join(eyes)+brows+mouth+'</g>'


def _body_and_feet(state,uid):
    # Extract the unchanged native body and two feet, not a recoloured old body.
    source=ET.fromstring('<svg>'+rig.character_fragment(rig.DEFAULT_POSE,uid+'-native')+'</svg>')
    nodes={child.get('id'):child for child in source}
    feet=feet_local(state);parts=[]
    for side,short,native_x in [('left','l',151.),('right','r',252.)]:
        x,y=feet[side];art=ET.tostring(nodes['foot-'+short],encoding='unicode')
        art=art.replace('id="foot-'+short+'"',f'id="{uid}-foot-{side}"')
        parts.append(f'<g transform="translate({x-native_x:.5f} {y-437.:.5f})">'+art+'</g>')
    body=ET.tostring(nodes['body'],encoding='unicode').replace('id="body"',f'id="{uid}-body"')
    return ''.join(parts)+body+_face(state,uid)


def character_svg(state,uid='mou',layer='all'):
    if layer not in ('all','body','torso','arms','hands'):raise ValueError('Unknown character layer '+layer)
    uid=html.escape(str(uid),quote=True);transform=' '.join(n(v) for v in matrix(state))
    parts=[]
    if layer in ('all','body','torso'):parts.append(_body_and_feet(state,uid))
    if layer in ('all','body','arms'):parts.extend(_arm_art(side,state,uid) for side in SHOULDERS)
    if layer in ('all','hands'):parts.extend(_arm_art(side,state,uid,True) for side in SHOULDERS)
    return (f'<g id="{uid}-character-{layer}" data-character="mou" data-rig="mou_rig_original" '
            f'transform="matrix({transform})">'+''.join(parts)+'</g>')
