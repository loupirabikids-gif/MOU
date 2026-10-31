"""The selected pebble, staged in the kitchen with independent floating hands."""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
import reference_character as rig
import costume

rig.BODY_ORIGIN=(580.,1050.)
PALETTE=rig.PALETTE
GRIP=(0.,-8.)


def local_anchor(hand,anchor='grip'):
    if anchor=='tip':return rig.glove_points(hand['pinch'])[15]
    if anchor=='thumb':return rig.cubic(rig.glove_points(hand['pinch'])[9:13],.5)
    if isinstance(anchor,(tuple,list)):return tuple(anchor)
    return GRIP


def point(hand,anchor='grip'):
    return rig.hand_local_to_world(local_anchor(hand,anchor),hand)


def hand(side,target,rotation=0.,pinch=0.,scale=1.2,anchor='grip'):
    h={'x':0.,'y':0.,'rotation':float(rotation),'pinch':float(pinch),
       'scale':float(scale),'mirror':side=='left','anchor':anchor}
    p=point(h,anchor);h['x']=target[0]-p[0];h['y']=target[1]-p[1]
    h['target']=tuple(target)
    return h


def hand_svg(side,h):return rig.hand_svg(side,h)


def hands_svg(state):
    return ''.join(hand_svg(side,state['hands'][side])for side in ('left','right'))


def face(name='happy',target=(301.,1300.),forward=0.):
    values={'target':tuple(target),'audience':forward>=1.,'forward_weight':forward,
            'open_l':.88,'open_r':.96,'brow_l':-.18,'brow_r':-.12,'brow_raise':.10,
            'pupil':1.,'smile':.65,'skew':.12,'mouth_width':62.,'mouth_open':0.,'blink':1.}
    presets={
        'inspect':dict(open_l=1.,open_r=1.,brow_l=.18,brow_r=-.12,smile=.05,mouth_width=39.),
        'focus':dict(open_l=.88,open_r=.90,brow_l=-.30,brow_r=-.28,smile=.12,mouth_width=40.),
        'relief':dict(open_l=.77,open_r=.89,smile=.48,mouth_width=56.),
        'impatient':dict(open_l=.82,open_r=.91,brow_l=.35,brow_r=-.20,smile=-.18,mouth_width=42.),
        'resist':dict(open_l=.94,open_r=.98,brow_l=.40,brow_r=-.22,smile=-.27,mouth_width=44.),
        'dread':dict(open_l=1.,open_r=1.,brow_raise=.75,brow_l=.50,brow_r=-.25,pupil=.88,mouth_open=.32,mouth_width=26.),
        'shock':dict(open_l=1.,open_r=1.,brow_raise=1.,brow_l=.8,brow_r=-.5,pupil=.70,mouth_open=.80,mouth_width=40.),
        'lost':dict(open_l=.90,open_r=.94,brow_raise=.52,brow_l=.48,brow_r=-.28,smile=-.50,mouth_width=49.),
        'notice':dict(open_l=.97,open_r=.98,brow_raise=.20,brow_l=.20,brow_r=-.15,smile=.05,mouth_width=39.),
        'proud':dict(open_l=.73,open_r=.89,brow_l=-.26,brow_r=-.18,smile=.63,mouth_width=63.,skew=.45),
    }
    values.update(presets.get(name,{}));return values


def blend_face(a,b,u):
    result={}
    for k,v in a.items():
        other=b.get(k,v)
        if k=='target':result[k]=tuple(x+(y-x)*u for x,y in zip(v,other))
        elif isinstance(v,(int,float))and not isinstance(v,bool):result[k]=v+(other-v)*u
        else:result[k]=other if u>=.5 else v
    return result


def costume_svg():
    root=ET.fromstring(costume.costume_svg())
    hat=next(e for e in root if e.attrib.get('id')=='toque-chef')
    apron=next(e for e in root if e.attrib.get('id')=='tablier-taille')
    hat_svg=ET.tostring(hat,encoding='unicode');apron_svg=ET.tostring(apron,encoding='unicode')
    return ('<g transform="translate(-396 -415) scale(1.65)">'+hat_svg+'</g>'
            '<g transform="translate(-307.5 -383) scale(1.5)">'+apron_svg+'</g>')


def defs_svg():
    p=PALETTE
    return (f'<defs><linearGradient id="skin" x1="0" y1="0" x2=".45" y2="1">'
            f'<stop offset="0" stop-color="{p["light"]}"/><stop offset=".48" stop-color="{p["body"]}"/>'
            f'<stop offset="1" stop-color="{p["shade"]}"/></linearGradient>'
            f'<clipPath id="body-clip"><path d="{rig.BODY_PATH}"/></clipPath></defs>')


def actor_svg(state):
    p=PALETTE;body=state['body'];m=' '.join(rig.n(v)for v in rig.body_matrix(body))
    parts=['<g id="galet-personnage">']
    for side,x in (('l',473.),('r',690.)):
        parts.append(f'<g id="foot-{side}" data-part="foot">'+rig._ellipse(x,1324.,43.,20.,p['ink'])+'</g>')
    parts.append(f'<g id="pebble-body" transform="matrix({m})">')
    parts.append(rig._path(rig.BODY_PATH,'url(#skin)',7.5,extra='id="body-outline"'))
    parts.append('<g clip-path="url(#body-clip)">'+rig._ellipse(-105.,-125.,135.,78.,'#FFFFFF','opacity=".12"')+'</g>')
    parts.append(rig.face_svg(state['face'],body));parts.append(costume_svg());parts.append('</g></g>')
    return ''.join(parts)
