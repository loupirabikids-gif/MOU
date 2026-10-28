"""Le torchon : jeu paramétrique, tissu et contacts du modèle MOU original.

Les chemins des bras sont exactement ceux de mou_rig._arm. Seules des
rotations autour de leurs racines les articulent ; aucune racine n'est masquée.
Le tissu est une nappe souple à deux prises et un coin bloqué sous le pied.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mou_rig import DEFAULT_POSE, PALETTE, character_fragment, _arm, _pt, _tangent

INK = PALETTE['outline']
CLOTH = '#E98178'
RELEASE = 7.25
HIT = 7.5
GRIP = 1.5
FINAL = 11.5


def smooth(x):
    x = min(1., max(0., float(x)))
    return x*x*(3.-2.*x)


def lerp(a,b,u):
    return a+(b-a)*u


def xy(a,b,u):
    return [lerp(a[0],b[0],u),lerp(a[1],b[1],u)]


def state(**changes):
    return {**DEFAULT_POSE, 'arm_rot_l':0., 'arm_rot_r':0.,
            'body_sx':1., 'body_sy':1., 'body_skew':0., 'body_dx':0., 'body_dy':0.,
            **changes}


READY = state(pupil_x=.30,pupil_y=1.,smile=.12,eye_open_l=.92,eye_open_r=.92)
REACH = state(arm_clasp=.90,arm_rot_l=16.,arm_rot_r=-16.,
              body_sx=1.04,body_sy=.73,pupil_y=1.,smile=.08,brow_raise=.1)
HOLD = state(arm_clasp=.55,arm_rot_l=-13.,arm_rot_r=13.,
             body_sy=.98,pupil_y=.7,smile=.05)
PULL1 = state(arm_clasp=.45,arm_rot_l=-28.,arm_rot_r=28.,
              body_sx=1.015,body_sy=1.04,body_skew=-.04,
              pupil_y=.55,eye_open_l=.73,eye_open_r=.73,
              brow_l=-.65,brow_r=-.65,mouth_open=.08,smile=-.25)
RESET = state(arm_clasp=.50,arm_rot_l=-15.,arm_rot_r=15.,
              pupil_y=.65,brow_l=.2,brow_r=.2,smile=-.08)
PULL2 = state(arm_clasp=.42,arm_rot_l=-31.,arm_rot_r=31.,
              body_sx=.99,body_sy=1.10,body_skew=-.06,
              pupil_y=.35,eye_open_l=.58,eye_open_r=.58,
              brow_l=-.90,brow_r=-.90,mouth_open=.18,smile=-.65)
SEE_FOOT = dict(PULL2,pupil_x=-.8,pupil_y=1.,eye_open_l=1.,eye_open_r=1.,
                brow_l=.25,brow_r=.25,brow_raise=.45,mouth_open=.03,smile=0.)
RELEASE_POSE = dict(SEE_FOOT,lift_l=20.)
SNAP = state(arm_clasp=.25,arm_rot_l=-48.,arm_rot_r=48.,
             body_sy=1.12,body_skew=-.01,body_dy=-12.,lift_l=20.,
             eye_open_l=1.,eye_open_r=1.,pupil_y=.2,brow_raise=.8,mouth_open=.12)
COVERED = dict(SNAP)
LOWER = state(arm_clasp=.55,arm_rot_l=-12.,arm_rot_r=12.,
              eye_open_l=.84,eye_open_r=.84,pupil_y=.2,smile=-.20)
BLAME = dict(LOWER,pupil_x=-.88,pupil_y=1.,brow_l=-.78,brow_r=-.78,
             brow_raise=.03,eye_open_l=.74,eye_open_r=.80)

KEYS = [(0.,READY),(.35,READY),(1.5,REACH),(2.,HOLD),(2.25,HOLD),
        (2.5,PULL1),(3.,RESET),(4.25,RESET),(5.,PULL2),(6.,PULL2),
        (7.,SEE_FOOT),(7.208333333333333,SEE_FOOT),(RELEASE,RELEASE_POSE),
        (HIT,SNAP),(8.5,COVERED),(9.,dict(COVERED,lift_l=0.)),
        (10.5,LOWER),(FINAL,BLAME),(12.,BLAME)]


def pose_at(t):
    t = max(0.,min(FINAL,float(t)))
    for (ta,a),(tb,b) in zip(KEYS,KEYS[1:]):
        if ta <= t <= tb:
            u = smooth((t-ta)/(tb-ta))
            p = dict(b) if u >= 1. else {k:lerp(a[k],b[k],u) for k in a}
            break
    else:
        p = dict(KEYS[-1][1])
    p['_t'] = t
    return p


def motion_at(t):
    return {'dx':0.,'dy':0.,'sx':1.,'sy':1.}


def deformation_at(p):
    return {'sx':p['body_sx'],'sy':p['body_sy'],'skew':p['body_skew'],
            'dx':p['body_dx'],'dy':p['body_dy'],'anchor_x':200.,'anchor_y':437.}


def body_point(point,p):
    x,y=point
    return [200.+p['body_sx']*(x-200.)+p['body_skew']*(y-437.)+p['body_dx'],
            437.+p['body_sy']*(y-437.)+p['body_dy']]


def rotate_point(point,pivot,degrees):
    a=math.radians(degrees);c,s=math.cos(a),math.sin(a)
    x,y=point[0]-pivot[0],point[1]-pivot[1]
    return [pivot[0]+c*x-s*y,pivot[1]+s*x+c*y]


def arm_controls(side,p):
    if side=='left':
        down=[(105,291),(80,311),(70,341),(76,367)]
        hip=[(105,291),(24,307),(40,344),(118,356)]
        folded=[(105,291),(91,344),(119,386),(178,389)]
    else:
        down=[(297,291),(321,310),(332,340),(325,367)]
        hip=[(297,291),(377,307),(361,344),(283,356)]
        folded=[(297,291),(311,344),(281,386),(225,389)]
    return [_pt(_pt(a,b,p['arm_hips']),c,p['arm_clasp']) for a,b,c in zip(down,hip,folded)]


def hand_grip(side,p):
    """Contact à l'intérieur de la moufle native, sur son extrémité arrondie."""
    controls=arm_controls(side,p);ex,ey=controls[-1];tx,ty=_tangent(controls,1.)
    point=(ex+12*tx,ey+12*ty)
    pivot=(105,291) if side=='left' else (297,291)
    angle=p['arm_rot_l' if side=='left' else 'arm_rot_r']
    return body_point(rotate_point(point,pivot,angle),p)


def phase_at(t):
    if t<GRIP:return 'approche'
    if t<2.25:return 'prise'
    if t<3.:return 'premiere_traction'
    if t<4.25:return 'reajuste'
    if t<6.:return 'seconde_traction'
    if t<RELEASE:return 'decouvre_pied'
    if t<HIT:return 'liberation'
    if t<9.:return 'visage_couvert'
    if t<10.5:return 'revelation'
    if t<FINAL:return 'accuse_pied'
    return 'tenue_finale'


def _cloth_data(p):
    t=p['_t']
    grips=[hand_grip(s,p) for s in ('left','right')]
    cloth_grips=grips if t>=GRIP else [hand_grip(s,REACH) for s in ('left','right')]
    centre=xy(cloth_grips[0],cloth_grips[1],.5)
    vx,vy=cloth_grips[1][0]-cloth_grips[0][0],cloth_grips[1][1]-cloth_grips[0][1]
    length=max(1e-9,math.hypot(vx,vy));ux,uy=vx/length,vy/length
    unfold=smooth((t-GRIP)/.5)
    half_width=56.+45.*unfold
    a=[centre[0]-half_width*ux,centre[1]-half_width*uy]
    b=[centre[0]+half_width*ux,centre[1]+half_width*uy]
    # The opposite end is folded into a narrow fan under the LEFT foot.
    # The right sole stays outside the cloth; one lifted foot really frees it.
    initial_d,initial_c=[80.,450.],[110.,478.]
    reveal=smooth((t-9.)/1.5)
    if t<=RELEASE:
        d,c=initial_d,initial_c
    elif t<HIT:
        u=smooth((t-RELEASE)/(HIT-RELEASE))
        d,c=xy(initial_d,[100.,140.],u),xy(initial_c,[302.,140.],u)
    else:
        d,c=xy([100.,140.],[100.,289.],reveal),xy([302.,140.],[302.,289.],reveal)
    # Four material edges; hands clasp two positions along the same hem.
    polygon=[a,b,c,d]
    return {'time':t,'phase':phase_at(t),'grips':grips,'cloth_grips':cloth_grips,
            'hem':[a,b],'free_edge':[d,c],'polygon':polygon,
            'foot_anchor':[151.,443.],'pinned':t<RELEASE,'released':t>=RELEASE,
            'face_covered':HIT<=t<9.6,'reveal_fraction':reveal,
            'cloth_width_units':202.,'projected_hem_width':2*half_width,
            'unfold_fraction':unfold,'material':'torchon_plisse_non_elastique'}


def cloth_geometry_at(t):
    return _cloth_data(pose_at(t))


def inside_polygon(point,polygon):
    x,y=point;result=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y):
            crossing=a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
            if x<crossing:result=not result
    return result


def _point_line_distance(point,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    return abs(dx*(a[1]-point[1])-(a[0]-point[0])*dy)/max(1e-9,math.hypot(dx,dy))


def contact_at(t):
    p=pose_at(t);g=_cloth_data(p)
    errors=[_point_line_distance(q,*g['hem']) for q in g['cloth_grips']]
    anchor=g['foot_anchor'];lift=p['lift_l']
    ellipse=((anchor[0]-151.)/27.)**2+((anchor[1]-(437.-lift))/12.)**2
    return {**g,'geometric_grip_errors':errors,
            'grip_separation':math.dist(*g['grips']),
            'blocking_foot_lift':lift,
            'blocking_anchor_inside_panel':inside_polygon(anchor,g['polygon']) if g['pinned'] else None,
            'blocking_foot_covers_anchor':ellipse<=1. if g['pinned'] else None,
            'source_arm_paths_exact':True,'two_hands':2}


def _body_transform(p):
    return (f'translate({200.+p["body_dx"]:.6f} {437.+p["body_dy"]:.6f}) '
            f'matrix({p["body_sx"]:.6f} 0 {p["body_skew"]:.6f} {p["body_sy"]:.6f} 0 0) '
            'translate(-200 -437)')


def _cloth_svg(p,uid):
    g=_cloth_data(p);a,b,c,d=g['polygon']
    n=lambda q:f'{q[0]:.4f} {q[1]:.4f}'
    # Flattened folds initially, unfolded panel as the hands rise.
    path=f'M{n(a)} L{n(b)} Q{n(xy(b,c,.52))} {n(c)} Q{n(xy(c,d,.50))} {n(d)} Q{n(xy(d,a,.50))} {n(a)} Z'
    clip=f'{uid}-cloth-outline';occlusion=f'{uid}-foot-occlusion'
    holes='M-100 -100 H600 V600 H-100 Z '
    # Correct scene occlusion: the existing soles remain in front of the cloth.
    # This masks only the PROP, never the original arms or their roots.
    for cx,side in [(151,'l'),(252,'r')]:
        lift=min(20.,max(0.,p['lift_'+side]))
        cy=437-lift
        # Opposite winding makes real holes with Cairo's nonzero clip rule.
        # CairoSVG does not implement the SVG luminance-mask alternative.
        holes+=(f'M{cx+27:.4f} {cy:.4f} A27 12 0 1 0 {cx-27:.4f} {cy:.4f} '
                f'A27 12 0 1 0 {cx+27:.4f} {cy:.4f} Z ')
    content=[f'<defs><clipPath id="{clip}"><path d="{path}"/></clipPath>',
             f'<clipPath id="{occlusion}"><path d="{holes}"/></clipPath></defs>',
              f'<g id="cloth" clip-path="url(#{occlusion})"><path data-part="cloth" d="{path}" '
              f'fill="{CLOTH}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>',
              f'<g clip-path="url(#{clip})">']
    for v in (.87,.92):
        left,right=xy(a,d,v),xy(b,c,v)
        content.append(f'<path d="M{n(left)} L{n(right)}" fill="none" stroke="#FFE9D6" stroke-width="2.2"/>')
    for fraction in (.24,.50,.76):
        top,bottom=xy(a,b,fraction),xy(d,c,fraction)
        mid=xy(top,bottom,.5);mid[0]+=7*math.sin(fraction*math.pi*2)
        content.append(f'<path d="M{n(top)} Q{n(mid)} {n(bottom)}" fill="none" '
                       'stroke="#B94B56" stroke-width="1.7" opacity=".65"/>')
    content+=['</g></g>']
    return ''.join(content)


def character_at(p,uid='mou'):
    fragment=character_fragment(p,uid=uid)
    feet,rest=fragment.split('<g id="body">',1)
    bodyface='<g id="body">'+rest
    arm_parts=[]
    for side,root,angle in [('left',(105,291),p['arm_rot_l']),('right',(297,291),p['arm_rot_r'])]:
        canonical=_arm(side,p['arm_hips'],p['arm_clasp'])
        assert canonical in bodyface
        bodyface=bodyface.replace(canonical,'',1)
        arm_parts.append(f'<g id="articulation-{side}" transform="rotate({angle:.6f} {root[0]} {root[1]})">'
                         +canonical+'</g>')
    transform=_body_transform(p)
    return (feet+f'<g id="body-warp" transform="{transform}">'+bodyface+'</g>'
            +_cloth_svg(p,uid)
            +f'<g id="arms-warp" transform="{transform}">'+''.join(arm_parts)+'</g>')


def intention_at(t):
    return {'approche':'veut ramasser le torchon','prise':'saisit la lisière à deux mains',
            'premiere_traction':'ça résiste','reajuste':'accuse déjà le tissu',
            'seconde_traction':'tire de toutes ses forces','decouvre_pied':'comprend enfin son propre appui',
            'liberation':'lève le pied sans cesser de tirer','visage_couvert':'FLAP, tissu sur le visage',
            'revelation':'ses deux yeux émergent','accuse_pied':'rejette la faute sur son pied',
            'tenue_finale':'regard accusateur tenu en silence'}[phase_at(min(FINAL,max(0.,float(t))))]
