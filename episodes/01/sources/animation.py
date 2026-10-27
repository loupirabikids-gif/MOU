"""La dernière retouche : le même MOU embellit sa pose jusqu'à l'excès.

Les contacts, les rubans des bras et la peau des joues partagent les mêmes
repères locaux. Aucun étirement de peau avant le contact des deux mitaines.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mou_rig import (DEFAULT_POSE, PALETTE, character_fragment, _mouth, _arm,
                     _cubic, _tangent, _clamp, _pt, _n, _path)

FPS = 24
FLASH = 154/24
CONTACT_TIME = 3.55


def smooth(x):
    x = max(0., min(1., float(x)))
    return x*x*(3-2*x)


def state(**changes):
    return {**DEFAULT_POSE, 'vanity': 0., 'pout': 0., 'shame': 0.,
            'arm_raise': 0., 'cheek_contact': 0., 'cheek_lift': 0.,
            'cheek_stretch': 0., 'cheek_asym': 0., 'chin_up': 0.,
            'chin_tuck': 0., 'shutter_press': 0., **changes}


READY = state(arm_hips=.7, eye_open_l=.65, eye_open_r=.72,
              pupil_x=0., pupil_y=.1, brow_l=.12, brow_r=-.75,
              brow_raise=.45, smile=.75, vanity=.6, chin_up=.55)
PRESS = dict(READY, shutter_press=1.)
ADMIRE = state(arm_hips=1., eye_open_l=.53, eye_open_r=.64,
               pupil_x=0., pupil_y=0., brow_l=.15, brow_r=-1.,
               brow_raise=.65, smile=.35, pout=1., chin_up=1.)
PROUD = state(arm_hips=1., eye_open_l=.55, eye_open_r=.68,
              pupil_x=0., pupil_y=0., brow_l=.12, brow_r=-1.,
              brow_raise=.7, smile=1., vanity=1., chin_up=1.)
TOUCH = dict(PROUD, arm_hips=.35, arm_raise=1., cheek_contact=1.)
LIFT = dict(TOUCH, cheek_lift=1.)
APPROVE = dict(LIFT, eye_open_l=.51, eye_open_r=.64, brow_raise=.82)
PULL = dict(APPROVE, cheek_stretch=.38, cheek_asym=.08)
MORE = dict(APPROVE, cheek_stretch=.68, cheek_asym=.35,
            eye_open_l=.53, eye_open_r=.62)
CAPTURE = dict(APPROVE, cheek_stretch=1., cheek_asym=1.,
               eye_open_l=.53, eye_open_r=.40)
READ = dict(CAPTURE, pupil_y=.95, eye_open_l=.95, eye_open_r=.95,
            brow_l=.56, brow_r=.56, brow_raise=.45, chin_up=.75)
SEEN = dict(READ, pupil_y=1., brow_l=.78, brow_r=.78,
            brow_raise=.2, smile=.02, vanity=.25, chin_up=.5)
RELEASE = state(arm_hips=0., arm_clasp=.12, arm_raise=.52,
                cheek_contact=.25, cheek_lift=.4, cheek_stretch=.35,
                cheek_asym=.35, pupil_y=1., eye_open_l=.80, eye_open_r=.84,
                brow_l=.75, brow_r=.75, brow_raise=.18,
                smile=0., shame=.75, chin_tuck=.4)
LOWER = state(arm_clasp=.55, eye_open_l=.72, eye_open_r=.76,
              pupil_x=-.1, pupil_y=.9, brow_l=.78, brow_r=.78,
              brow_raise=.10, smile=0., shame=1., chin_tuck=.85)
ASHAMED = dict(LOWER, arm_clasp=1., pupil_x=-.12, pupil_y=.72,
                chin_tuck=1.)

KEYS = [
    (0., READY), (.18, READY), (.46, PRESS), (.62, PRESS), (.90, READY),
    (34/24, ADMIRE), (1.78, ADMIRE), (2.20, PROUD), (82/24, PROUD),
    (CONTACT_TIME, TOUCH), (3.5833333333333335, TOUCH), (4.15, LIFT),
    (4.42, APPROVE), (4.8, APPROVE), (5.6, PULL), (6.15, MORE),
    (FLASH, CAPTURE), (8.8, CAPTURE), (9.25, READ), (9.7, SEEN),
    (10.2, RELEASE), (10.7, LOWER), (11.1, ASHAMED), (13., ASHAMED),
]


def pose_at(t):
    for (ta,a),(tb,b) in zip(KEYS,KEYS[1:]):
        if ta <= t <= tb:
            raw = max(0., min(1., (t-ta)/(tb-ta)))
            # La dernière traction est encore en mouvement au clic.
            u = raw if ta == 6.15 and tb == FLASH else smooth(raw)
            p = dict(b) if raw >= 1 else {k:a[k]+(b[k]-a[k])*u for k in a}
            break
    else:
        p = dict(KEYS[0 if t<0 else -1][1])
    for side in ('l','r'):
        if p['eye_open_'+side] < .30:
            p['eye_open_'+side] = 0.
    return p


def motion_at(t):
    return {'sx':1., 'sy':1., 'dx':0., 'dy':0.}


def deformation_at(p):
    """Aucune affine globale : la retouche est une déformation locale de peau."""
    return {'sx':1., 'sy':1., 'skew':0., 'anchor_x':200., 'anchor_y':437.}


def _skin_displacements(p):
    contact = _clamp(p.get('cheek_contact',0.))
    lift = _clamp(p.get('cheek_lift',0.))
    stretch = _clamp(p.get('cheek_stretch',0.))
    asym = _clamp(p.get('cheek_asym',0.))
    # Tirer la droite plus haut amplifie le sourire déjà sûr de lui.
    return {'left':(-45*stretch*contact, (-8*lift+34*asym)*contact),
            'right':(45*stretch*contact, (-8*lift-32*asym)*contact)}


def _base_controls(side,p):
    if side=='left':
        down=[(105,291),(80,311),(70,341),(76,367)]
        hip=[(105,291),(24,307),(40,344),(118,356)]
        # Avant-bras courts devant le ventre ; racines sur les flancs.
        folded=[(92,302),(73,333),(125,356),(174,366)]
    else:
        down=[(297,291),(321,310),(332,340),(325,367)]
        hip=[(297,291),(377,307),(361,344),(283,356)]
        folded=[(316,301),(335,336),(285,360),(230,366)]
    return [_pt(_pt(a,b,_clamp(p.get('arm_hips',0))),c,
                _clamp(p.get('arm_clasp',0))) for a,b,c in zip(down,hip,folded)]


def contact_geometry(p):
    """Repères locaux400×500, les mêmes qui construisent bras et peau.

    in_contact signifie que la main a atteint la joue ; pendant la descente
    la peau revient avec le relâchement, sans prétendre garder le contact.
    """
    displacements = _skin_displacements(p)
    raise_ = _clamp(p.get('arm_raise',0.))
    out={'skin_displacement':{k:list(v) for k,v in displacements.items()}}
    for side,base in [('left',(134.,315.)),('right',(272.,315.))]:
        dx,dy=displacements[side]
        target=(base[0]+dx,base[1]+dy)
        if side=='left':
            shoulder=(105+dx*.45,291+dy*.45)
            raised=[shoulder,(33+dx*.35,350+dy*.35),
                    (70+dx*.65,315+dy),target]
        else:
            asym=_clamp(p.get('cheek_asym',0.))*_clamp(p.get('cheek_contact',0.))
            # Le bras droit se replie depuis une attache plus basse ;
            # la mitaine haute ne se superpose pas à sa propre épaule.
            shoulder=(297+dx*.45,291+dy*.45+62*math.sqrt(asym))
            raised=[shoulder,(369+dx*.35,350+dy*.35),
                    (332+dx*.65,315+dy),target]
        controls=[_pt(a,b,raise_) for a,b in zip(_base_controls(side,p),raised)]
        center=controls[-1];tx,ty=_tangent(controls,1.)
        out[side]={
            'shoulder':list(controls[0]), 'controls':[list(q) for q in controls],
            'hand_center':list(center), 'hand_tip':[center[0]+19*tx,center[1]+19*ty],
            'cheek_target':list(target), 'contact_gap':math.dist(center,target),
            'in_contact':raise_>=1-1e-10 and p.get('cheek_contact',0.)>=1-1e-10,
            'mitten_radius':19.,
        }
    return out


def _raised_arm(side,p,uid):
    """Union visuelle de capsules SVG : contour rond, aucun trait de poignet.

    L'arc reste celui du rig, avec largeur croissante et une seule moufle.
    Toutes les encres sont dessinées avant toutes les peaux : les recouvrements
    ne produisent donc plus les triangles des anciens offsets auto-croisés.
    """
    controls=contact_geometry(p)[side]['controls']
    samples=[]
    for i in range(65):
        t=i/64;x,y=_cubic(controls,t)
        hand=_clamp((t-.75)/.25);hand=hand*hand*(3-2*hand)
        samples.append((x,y,10.5+8.5*hand))
    ink=[];skin=[]
    for color,extra,dest in [(PALETTE['outline'],2.6,ink),(PALETTE['skin'],0.,skin)]:
        for (x1,y1,r1),(x2,y2,r2) in zip(samples,samples[1:]):
            r=(r1+r2)/2+extra
            dest.append(f'<path d="M{x1:.3f} {y1:.3f} L{x2:.3f} {y2:.3f}" '
                        f'fill="none" stroke="{color}" stroke-width="{2*r:.3f}" '
                        'stroke-linecap="round"/>')
        ex,ey,r=samples[-1]
        dest.append(f'<circle cx="{ex:.3f}" cy="{ey:.3f}" r="{r+extra:.3f}" fill="{color}"/>')
    # La racine est noyée dans le torse, comme l'épaule ouverte du rig.
    sx,sy,_=samples[0]
    clip=f'{uid}-arm-root-{side}'
    root=(f'<defs><clipPath id="{clip}"><path d="{_body_path(p)}"/></clipPath></defs>'
          f'<circle cx="{sx:.3f}" cy="{sy:.3f}" r="20" '
          f'fill="{PALETTE["skin"]}" clip-path="url(#{clip})"/>')
    return (f'<g id="arm-{side}">'+''.join(ink)
            +f'<g data-part="hand" data-side="{side}">'+''.join(skin)+'</g>'+root+'</g>')


def _body_path(p):
    ds=_skin_displacements(p);lx,ly=ds['left'];rx,ry=ds['right']
    d=(f'M{90+lx:.3f} {310+ly:.3f} '
       f'C{100+lx*.55:.3f} {284+ly*.55:.3f} 111 241 124 200 '
       'C141 148 175 123 208 125 '
       'C224 124 234 128 246 132 '
       'C265 119 290 121 300 137 '
       'C310 152 304 171 301 188 '
       f'C305 225 {313+rx*.6:.3f} {267+ry*.5:.3f} {319+rx:.3f} {305+ry:.3f} '
       f'C{331+rx:.3f} {350+ry*.6:.3f} 321 388 297 403 '
       'C265 424 147 426 112 405 '
       f'C82 390 {74+lx:.3f} {350+ly*.6:.3f} {90+lx:.3f} {310+ly:.3f} Z')
    return d


def _retouched_body(p):
    return '<g id="body">'+_path(_body_path(p),PALETTE['skin'],sw=6)+'</g>'


def _retouched_mouth(p,uid):
    smile=max(-1.,min(1.,p.get('smile',0.)));op=_clamp(p.get('mouth_open',0.))
    mix=lambda a,b,t:a+(b-a)*t
    width=mix(12+12*abs(smile),52,op)
    yl=mix(-5*smile,-25,op);yr=mix(-9*smile-8*max(0.,smile),-31,op)
    upper=mix(20*smile,-12,op);lower=mix(20*smile,52,op)
    points=[(-width,yl),(-width*.4,upper),(width*.4,upper),
            (width,yr),(width*.9,lower),(-width*.75,lower)]
    grin=[(-37,2),(-17,27),(20,27),(39,-20),(30,21),(-24,28)]
    lips=[(-11,-2),(-3,-10),(9,-6),(14,-2),(7,6),(-5,5)]
    shy=[(-12,0),(-3,3),(7,1),(13,-1.5),(7,1),(-3,3)]
    for shape,weight in [(grin,p.get('vanity',0.)),(lips,p.get('pout',0.)),(shy,p.get('shame',0.))]:
        points=[_pt(a,b,_clamp(weight)) for a,b in zip(points,shape)]
    ds=_skin_displacements(p);ldx,ldy=ds['left'];rdx,rdy=ds['right']
    # Les lèvres suivent les joues réellement saisies. Les yeux restent libres.
    moved=[]
    for x,y in points:
        side='left' if x<0 else 'right'
        dx,dy=ds[side]
        influence=min(1.,abs(x)/34.)
        moved.append((x+dx*.9*influence,y+dy*influence))
    xy=[f'{x:.3f} {y:.3f}' for x,y in moved]
    d=f'M{xy[0]} C{xy[1]} {xy[2]} {xy[3]} C{xy[4]} {xy[5]} {xy[0]} Z'
    ink=PALETTE['outline'];clip=f'{uid}-mouth'
    return (f'<g id="mouth" transform="translate(205 321)">'
            +_path(d,ink,ink,4.6)
            +f'<defs><clipPath id="{clip}"><path d="{d}"/></clipPath></defs>'
            +f'<g clip-path="url(#{clip})" opacity="{op:.3f}">'
            +f'<ellipse cx="8" cy="25" rx="33" ry="15" fill="{PALETTE["tongue"]}"/>'
            +'</g></g>')


def character_at(p,uid='mou'):
    fragment=character_fragment(p,uid=uid)
    fragment=fragment.replace(_mouth(p,uid),_retouched_mouth(p,uid),1)
    # Garder le même contour pendant la descente et la pose finale,
    # sans retour soudain aux longs rubans du clasp historique.
    if p.get('arm_raise',0.)>1e-8 or p.get('arm_clasp',0.)>1e-8:
        for side in ('left','right'):
            original=_arm(side,_clamp(p.get('arm_hips',0.)),_clamp(p.get('arm_clasp',0.)))
            assert original in fragment
            fragment=fragment.replace(original,_raised_arm(side,p,uid),1)
    ds=_skin_displacements(p)
    if any(abs(v)>1e-8 for d in ds.values() for v in d):
        start=fragment.index('<g id="body">');end=fragment.index('</g>',start)+4
        fragment=fragment[:start]+_retouched_body(p)+fragment[end:]
    shift=-3*p.get('chin_up',0.)+4*p.get('chin_tuck',0.)
    if abs(shift)>1e-8:
        fragment=fragment.replace('<g id="face">',f'<g id="face" transform="translate(0 {shift:.4f})">',1)
    return fragment


def intention_at(t):
    if t<34/24:return 'active le retardateur'
    if t<82/24:return 'certain d’être magnifique'
    if t<CONTACT_TIME:return 'deux mitaines vers les joues'
    if t<4.15:return 'petit lift des joues'
    if t<4.8:return 'approuve sa retouche'
    if t<FLASH:return 'encore une dernière traction'
    if t<8.8:return 'satisfait de son embellissement'
    if t<9.7:return 'découvre le résultat sous l’objectif'
    if t<11.1:return 'mains descendent, prétention défaite'
    return 'gêne, bouche minuscule'
