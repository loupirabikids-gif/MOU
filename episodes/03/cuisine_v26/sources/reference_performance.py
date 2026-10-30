"""Purposeful upper-body acting on the unchanged MOU rig.

The native body, costume and two native arms share one rigid rotation. Feet
stay on the ground. World grips are inverse-solved so the stage objects do
not follow a cosmetic body tilt. No limb is stretched or redrawn.
"""
from __future__ import annotations

import copy
import math
import re

PIVOT=(205.,420.)


def smooth(value):
    value=max(0.,min(1.,float(value)))
    return value*value*(3.-2.*value)


def curve(t,keys):
    if t<=keys[0][0]:return float(keys[0][1])
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*smooth((t-a)/(b-a))
    return float(keys[-1][1])


def rotate_native(point,degrees):
    dx,dy=point[0]-PIVOT[0],point[1]-PIVOT[1]
    theta=math.radians(degrees);c,s=math.cos(theta),math.sin(theta)
    return PIVOT[0]+c*dx-s*dy,PIVOT[1]+s*dx+c*dy


def map_world(point,transform,degrees):
    x,y,scale=transform
    local=((point[0]-x)/scale,(point[1]-y)/scale)
    px,py=rotate_native(local,degrees)
    return x+scale*px,y+scale*py


def inverse_world(point,state):
    return map_world(point,state['actor_transform'],-state.get('performance',{}).get('angle_deg',0.))


def _solve(animation,side,target,transform,meta):
    """Use native controls, including the original spoon grip's12px depth."""
    depth=meta.get('grip_depth',animation.GRIP_DEPTH)
    hips=float(meta['hips']);x,y,scale=transform;sx,sy=animation.SHOULDERS[side]
    dx,dy=(target[0]-x)/scale-sx,(target[1]-y)/scale-sy
    existing=animation.world_grip(side,hips,meta['clasp'],meta['rotation'],transform,depth)
    if math.dist(existing,target)<1.e-7:
        return {**meta,'hand':existing,'target':target,'contact_error':math.dist(existing,target)}
    radius=math.hypot(dx,dy)
    def r(h,c):
        px,py=animation.native_grip(side,h,c,depth)
        return math.hypot(px-sx,py-sy)
    def roots(h):
        # The near-straight stirring pose has a shallow minimum before
        # extending. Bracket each branch, then retain the closest pose.
        samples=[(j/32.,r(h,j/32.)-radius) for j in range(33)]
        candidates=[c for c,error in samples if abs(error)<1.e-8]
        for (lo,fl),(hi,fh) in zip(samples,samples[1:]):
            if fl*fh>=0.:continue
            for _ in range(30):
                mid=(lo+hi)/2.;fm=r(h,mid)-radius
                if fl*fm<=0.:hi=mid
                else:lo,fl=mid,fm
            candidates.append((lo+hi)/2.)
        return candidates
    candidates=roots(hips)
    if not candidates:
        for h in sorted((j/100. for j in range(101)),key=lambda h:abs(h-hips)):
            candidates=roots(h)
            if candidates:hips=h;break
    if candidates:clasp=min(candidates,key=lambda c:abs(c-float(meta['clasp'])))
    else:clasp=min((j/64. for j in range(65)),key=lambda c:abs(r(hips,c)-radius))
    px,py=animation.native_grip(side,hips,clasp,depth)
    angle=math.degrees(math.atan2(dy,dx)-math.atan2(py-sy,px-sx))
    hand=animation.world_grip(side,hips,clasp,angle,transform,depth)
    return {'hips':hips,'clasp':clasp,'rotation':angle,'hand':hand,
            'target':target,'contact_error':math.dist(target,hand),'grip_depth':depth}


def _direction(t):
    if t<6.6:
        return curve(t,[(0.,0.),(1.85,0.),(2.35,-1.7),(3.8,-1.7),(4.55,0.),(6.6,0.)]),'plaisir_absorbe'
    if 7.<=t<7.75:
        return curve(t,[(7.,0.),(7.1666667,0.),(7.375,2.8),(7.75,2.8)]),'recul_inspection'
    if 12.25<=t<12.8:
        return curve(t,[(12.25,0.),(12.4,-1.25),(12.6,-1.25),(12.8,0.)]),'premier_apaisement'
    if 22.75<=t<23.:
        return curve(t,[(22.75,0.),(22.875,1.5),(23.,1.5)]),'inspection_impatiente'
    if 28.8<=t<29.:
        return curve(t,[(28.8,0.),(28.925,1.8),(29.,1.8)]),'inspection_contrariete'
    if 31.1<=t<32.25:
        return curve(t,[(31.1,0.),(31.35,-3.3),(32.,-3.3),(32.25,0.)]),'retour_cuisine_impatient'
    if 38.1<=t<38.7:
        return curve(t,[(38.1,0.),(38.3,-1.3),(38.55,-1.3),(38.7,0.)]),'enfin_sec'
    if t>=40.25:
        f=(t-40.25)*24.
        return curve(f,[(0.,-1.3),(7.,-1.3),(14.,3.7),(26.,3.7),
                        (35.,3.7),(49.,.8),(51.,.8),(66.,.8)]),'decouverte_puis_retenue'
    return 0.,'geste_objet'


def _free_gestures(t):
    if 1.85<=t<4.55:
        amount=curve(t,[(1.85,0.),(2.45,1.),(3.8,1.),(4.55,0.)])
        return {'right':(-.10*amount,-4.*amount)}
    if 7.<=t<7.75:
        amount=curve(t,[(7.,0.),(7.1666667,0.),(7.375,1.),(7.75,1.)])
        return {'left':(0.,-6.*amount),'right':(0.,0.)}
    if 22.75<=t<23. or 28.8<=t<29.:
        return {'left':(0.,0.),'right':(0.,0.)}
    if t>=40.25:
        f=(t-40.25)*24.
        amount=curve(f,[(0.,0.),(7.,0.),(14.,1.),(35.,1.),(49.,.35),(66.,.35)])
        return {'left':(-.08*amount,4.5*amount),'right':(-.10*amount,-5.*amount)}
    return {}


def apply(t,state,animation):
    """Set the grounded acting interface consumed by the V25 renderer."""
    if state['shot']=='sink':
        return state
    baseline_transform=tuple(state['actor_transform'])
    transform=baseline_transform
    hands={side:tuple(point) for side,point in state['hands'].items()}
    removed=(0.,0.)
    # Replace the old periodic whole-character sway with one motivated lean.
    # The original approved stir path is restored relative to the fixed pan.
    if 0.<=t<6.6:
        x,y,scale=transform;removed=(x-80.,y-380.)
        transform=(80.,380.,scale)
        hands={side:(p[0]-removed[0],p[1]-removed[1]) for side,p in hands.items()}
        if state.get('spoon'):
            state['spoon']=copy.deepcopy(state['spoon'])
            for key in ('grip','bowl'):
                p=state['spoon'][key];state['spoon'][key]=(p[0]-removed[0],p[1]-removed[1])
        state['rhythm']={**state['rhythm'],'offset':[0.,0.],'body_envelope':0.}
    state['actor_transform']=transform
    proposed,phase=_direction(t);free=_free_gestures(t)
    if state.get('paper') is not None:free={}
    targets=copy.deepcopy(hands)
    baseline_meta=state['arm_meta']
    def build(angle):
        result={}
        for side in ('left','right'):
            old=baseline_meta[side]
            if side in free:
                dc,da=free[side]
                meta={**old,'clasp':max(0.,min(1.,old['clasp']+dc)),
                      'rotation':old['rotation']+da}
                raw=animation.world_grip(side,meta['hips'],meta['clasp'],meta['rotation'],
                                         transform,meta.get('grip_depth',16.))
                target=map_world(raw,transform,angle)
                meta['hand']=target;meta['target']=target;meta['contact_error']=0.
            else:
                target=targets[side]
                solver_target=map_world(target,transform,-angle)
                meta=_solve(animation,side,solver_target,transform,old)
                raw=meta['hand'];actual=map_world(raw,transform,angle)
                meta.update(hand=actual,target=target,contact_error=math.dist(target,actual),
                            solver_target=solver_target)
            meta['unposed_hand']=raw
            meta['performance_angle_deg']=angle
            result[side]=meta
        return result
    angle=proposed;metas=build(angle)
    # A shoulder gesture is never allowed to stretch a native arm or pull a
    # utensil off its previous world grip. Fade the requested lean if needed.
    for _ in range(12):
        if all(meta['contact_error']<=baseline_meta[side].get('contact_error',0.)+.03
               for side,meta in metas.items() if side not in free):break
        angle*=.5;metas=build(angle)
    state['arm_meta']=metas;state['hands']={side:m['hand'] for side,m in metas.items()}
    if 31.1<=t<32.25:
        # Keep the held paper's canonical stage points exactly. The inverse
        # native solve differs only by floating-point roundoff (<3e-9px).
        for side in ('left','right'):
            metas[side]['computed_world_hand']=metas[side]['hand']
            metas[side]['hand']=targets[side]
        state['hands']=dict(targets)
    state['arms']=''.join(animation.draw_arm(side,metas[side]) for side in ('left','right'))
    torso=animation._torso_for_pose(state['pose'],state['whistle'])
    feet=[]
    for side in ('l','r'):
        match=re.search(f'<g id="foot-{side}">.*?</g>',torso)
        assert match,(t,side,'native foot missing')
        feet.append(match.group());torso=torso.replace(match.group(),'',1)
    state['torso']=torso;state['grounded_feet']=''.join(feet)
    state['performance_affine_svg']=f'rotate({angle:.9f} {PIVOT[0]:.1f} {PIVOT[1]:.1f})'
    state['performance']={'angle_deg':angle,'requested_angle_deg':proposed,
                          'pivot_native':list(PIVOT),'phase':phase,
                          'free_hands':list(free),'constrained_hands':[s for s in ('left','right') if s not in free],
                          'feet_grounded':True,'world_targets_before':targets,
                          'baseline_actor_transform':baseline_transform,'removed_rhythm_offset':removed,
                          'source_version':'V25'}
    return state
