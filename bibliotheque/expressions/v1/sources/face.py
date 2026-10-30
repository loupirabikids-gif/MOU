"""Expressive face adapter for MOU's unchanged canonical character.

Only the face is drawn here. Eyes keep the canonical two large oval apertures;
arms, hands, body and feet belong to the parent renderer. All mouth drawings
share two cubic contours so transitions need one outline, never two ghost mouths.
The native pose without extended controls reproduces mou_rig's face exactly.

mouth_width is a HALF width in native 400x500 character units, normally 8..48.
mouth_skew is -1..1, giving up to seven pixels of opposite corner displacement.
"""
from __future__ import annotations

import math
from pathlib import Path
import re
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import mou_rig as rig

MOUTH_SHAPES = ('native', 'smile', 'frown', 'flat', 'o', 'grit', 'wince', 'pout', 'revulsion')
_EXTENDED_DEFAULTS = {
    'mouth_width': 24., 'mouth_skew': 0., 'pupil_scale': 1.,
    'pupil_scale_l': 1., 'pupil_scale_r': 1.,
    'brow_raise_l': 0., 'brow_raise_r': 0., 'brow_curve': 0.,
}


def _clamp(value, lo=0., hi=1.):
    return max(lo, min(hi, float(value)))


def _mix(a, b, amount):
    return float(a)+(float(b)-float(a))*amount


def _uid(value):
    value=re.sub(r'[^A-Za-z0-9_.-]', '-', str(value))
    return 'mou-'+value if not value or not re.match(r'[A-Za-z_]', value) else value


def _eye(side, params, uid):
    local=dict(params)
    local['pupil_x']=params.get('pupil_x_'+side, params.get('pupil_x', 0.))
    local['pupil_y']=params.get('pupil_y_'+side, params.get('pupil_y', 0.))
    # The final few percent of the canonical closing morph can leave a tiny
    # outlined lens. For explicitly adapted expressions, finish that drawing
    # on the canonical closed arc rather than a green leaf-shaped sliver.
    effective_open=_clamp(params.get('eye_open_'+side,1.))*(1.-_clamp(params.get('laugh',0.)))
    if params.get('mouth_shape','native')!='native' and effective_open<=.045:
        local['eye_open_'+side]=0.
    cx,cy,rx=(164,235,34) if side=='l' else (242,232,33)
    fragment=rig._eye(cx,cy,rx,side,local,uid)
    scale=_clamp(params.get('pupil_scale_'+side,params.get('pupil_scale',1.)),.7,1.2)
    if scale!=1.:
        # The pupil alone changes; canonical eye aperture and its mask do not.
        fragment=fragment.replace('rx="9.300" ry="15.000"',
                                  f'rx="{9.3*scale:.3f}" ry="{15.*scale:.3f}"',1)
    return fragment


def _brows(params):
    if not any(key in params for key in ('brow_raise_l','brow_raise_r','brow_curve')):
        return rig._brows(params)
    out=[]
    for side,cx in (('l',164),('r',242)):
        base=177.-_clamp(params.get('brow_raise',0.),-1.,1.)*14.
        base-=_clamp(params.get('brow_raise_'+side,0.),-1.,1.)*8.
        amount=_clamp(params.get('brow_'+side,0.),-1.,1.)
        outer,inner=base+amount*15.,base-amount*15.
        ya,yb=(outer,inner) if side=='l' else (inner,outer)
        control=base-16.+abs(amount)*8.-_clamp(params.get('brow_curve',0.),-1.,1.)*8.
        out.append(rig._path(f'M{cx-22} {ya:.3f} Q{cx} {control:.3f} {cx+22} {yb:.3f}',sw=7))
    return '<g id="brows">'+''.join(out)+'</g>'


def _mouth_geometry(params):
    shape=params.get('mouth_shape','native')
    if shape not in MOUTH_SHAPES:
        raise ValueError(f'Unknown MOU mouth shape: {shape}')
    op=_clamp(params.get('mouth_open',0.))
    smile=_clamp(params.get('smile',0.),-1.,1.)
    if shape=='native':
        width=_mix(12.+12.*abs(smile),52.,op)
        if 'mouth_width' in params:
            width=_clamp(params['mouth_width'],8.,48.)
        yl,yr=_mix(-5.*smile,-25.,op),_mix(-9.*smile-8.*max(0.,smile),-31.,op)
        upper,lower=_mix(20.*smile,-12.,op),_mix(20.*smile,52.,op)
        points=[(-width,yl),(-width*.4,upper),(width*.4,upper),(width,yr),
                (width*.9,lower),(-width*.75,lower)]
    else:
        width=_clamp(params.get('mouth_width',24.),8.,48.)
        if shape=='smile':
            strength=max(.25,abs(smile))
            yl,yr=-3.*strength,-7.*strength
            upper,lower=15.*strength-15.*op,15.*strength+35.*op
            points=[(-width,yl),(-width*.45,upper),(width*.45,upper),(width,yr),
                    (width*.8,lower),(-width*.8,lower)]
        elif shape=='frown':
            strength=max(.3,abs(smile))
            yl,yr=3.*strength,4.*strength
            upper,lower=-18.*strength-5.*op,-18.*strength+36.*op
            points=[(-width,yl),(-width*.5,upper),(width*.5,upper),(width,yr),
                    (width*.5,lower),(-width*.5,lower)]
        elif shape=='flat':
            points=[(-width,0.),(-width*.4,-3.*op),(width*.4,-3.*op),(width,0.),
                    (width*.65,29.*op),(-width*.65,29.*op)]
        elif shape=='o':
            height=5.+27.*op
            points=[(-width,0.),(-width,-height*4./3.),(width,-height*4./3.),(width,0.),
                    (width,height*4./3.),(-width,height*4./3.)]
        elif shape=='grit':
            height=8.+5.*op
            points=[(-width,0.),(-width*.8,-height),(width*.8,-height),(width,0.),
                    (width*.8,height),(-width*.8,height)]
        elif shape=='wince':
            # A compressed, uneasy inverted curve. Upturned corners read as
            # smugness even with worried brows; keep both corners low.
            points=[(-width,4.),(-width*.45,-9.-5.*op),(width*.3,-3.-5.*op),(width,4.),
                    (width*.3,-3.+14.*op),(-width*.45,-9.+14.*op)]
        elif shape=='revulsion':
            # One side of the upper lip contracts while the lower contour
            # sags away. Both corners stay low enough to avoid a smug smile.
            # The catalogue pairs the raised right lip with the right squint.
            points=[(-width,5.),(-width*.4,6.-3.*op),(width*.35,-20.-4.*op),(width,4.),
                    (width*.65,-2.+28.*op),(-width*.55,14.+22.*op)]
        else:  # pursed, small dark mouth; no lip colour or new anatomy.
            height=2.+12.*op
            points=[(-width,0.),(-width*.45,-height),(width*.45,-height),(width,0.),
                    (width*.45,height*.65),(-width*.45,height*.65)]
    skew=_clamp(params.get('mouth_skew',0.),-1.,1.)*(3. if shape in ('wince','revulsion') else 7.)
    # A continuous tilt of the same contour, rather than an added mouth corner.
    points=[(x,y-skew*x/max(width,1.)) for x,y in points]
    teeth=1. if shape=='grit' else 0.
    tongue=_clamp((op-.18)/.5) if shape in ('native','smile','frown','flat') else 0.
    return {'points':points,'width':width,'teeth':teeth,'tongue':tongue}


def _mouth(params, uid):
    if (params.get('mouth_shape','native')=='native'
            and not any(key in params for key in ('mouth_width','mouth_skew','_mouth_geometry'))):
        return rig._mouth(params,uid)
    geometry=params.get('_mouth_geometry') or _mouth_geometry(params)
    p=geometry['points']
    coord=lambda point:f'{float(point[0]):.3f} {float(point[1]):.3f}'
    d=f'M{coord(p[0])} C{coord(p[1])} {coord(p[2])} {coord(p[3])} C{coord(p[4])} {coord(p[5])} {coord(p[0])} Z'
    ink=rig.PALETTE['outline'];clip=f'{uid}-mouth'
    width=float(geometry['width'])
    out=[f'<g id="mouth" transform="translate(205 321)">',rig._path(d,ink,ink,4.6),
         f'<defs><clipPath id="{clip}">{rig._path(d,"white","none",0)}</clipPath></defs>',
         f'<g clip-path="url(#{clip})">']
    tongue=float(geometry['tongue']);teeth=float(geometry['teeth'])
    if tongue>0.:
        out.append(f'<g opacity="{tongue:.5f}">'+rig._ellipse(4.,22.,width*.9,10.,rig.PALETTE['tongue'])+'</g>')
    if teeth>0.:
        # One unified tooth plate and a restrained jaw seam, not extra anatomy.
        out.append(f'<g opacity="{teeth:.5f}">'
                   +f'<rect x="{-width-2.:.3f}" y="-18" width="{2.*width+4.:.3f}" height="36" fill="{rig.PALETTE["eye_white"]}"/>'
                   +rig._path(f'M{-width:.3f} 0 H{width:.3f}',sw=1.6)+'</g>')
    out.extend(['</g>',rig._path(d,'none',ink,4.6),'</g>'])
    return ''.join(out)


def face_fragment(p:dict, uid:str='mou-expression')->str:
    """Return one native-coordinate face with exactly two clipped eye pupils.

    Extended mouth controls are optional. With only native rig parameters,
    this is byte-for-byte the canonical face fragment. No body/limb is drawn.
    """
    uid=_uid(uid)
    params={**rig.DEFAULT_POSE,**p}
    return ('<g id="face">'+_eye('l',params,uid)+_eye('r',params,uid)
            +_brows(params)+_mouth(params,uid)+'</g>')


def _value(params,key):
    if key in params:
        return params[key]
    for axis in ('x','y'):
        if key in ('pupil_'+axis+'_l','pupil_'+axis+'_r'):
            return params.get('pupil_'+axis,0.)
    if key in ('pupil_scale_l','pupil_scale_r'):
        return params.get('pupil_scale',1.)
    return rig.DEFAULT_POSE.get(key,_EXTENDED_DEFAULTS.get(key,0.))


def blend_face_params(a:dict,b:dict,amount:float)->dict:
    """Interpolate one mouth contour plus native controls, without crossfade.

    This helper does not decide acting timing: callers expose poses and choose
    gaze/anticipation/holds. Endpoints return their original parameters exactly.
    At intermediate values the mouth has a single interpolated outline and a
    single mask; teeth/tongue remain clipped to that outline.
    """
    u=_clamp(amount)
    if u<=0.:return dict(a)
    if u>=1.:return dict(b)
    result={}
    for key in set(rig.DEFAULT_POSE)|set(a)|set(b):
        if key.startswith('_'):continue
        x,y=_value(a,key),_value(b,key)
        if isinstance(x,(int,float)) and isinstance(y,(int,float)):
            result[key]=_mix(x,y,u)
        else:
            result[key]=y if u>=.5 else x
    ga=a.get('_mouth_geometry') or _mouth_geometry(a)
    gb=b.get('_mouth_geometry') or _mouth_geometry(b)
    result['_mouth_geometry']={
        'points':[(_mix(p[0],q[0],u),_mix(p[1],q[1],u)) for p,q in zip(ga['points'],gb['points'])],
        'width':_mix(ga['width'],gb['width'],u),
        'teeth':_mix(ga['teeth'],gb['teeth'],u),
        'tongue':_mix(ga['tongue'],gb['tongue'],u),
    }
    return result
