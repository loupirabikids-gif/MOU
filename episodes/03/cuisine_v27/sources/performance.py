"""Grounded area-preserving elastic acting on the canonical MOU drawing.

One affine transforms torso, face, costume and native arm roots together.
Only scene-anchored grips are inverse solved; free held paper follows the hands.
"""
from __future__ import annotations
import math
import re
import reference_performance as native

PIVOT=(205.,420.)


def smooth(x):
    x=max(0.,min(1.,float(x)));return x*x*(3.-2.*x)


def curve(t,keys):
    if t<=keys[0][0]:return float(keys[0][1])
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*smooth((t-a)/(b-a))
    return float(keys[-1][1])


def matrix(sx,sy,angle):
    theta=math.radians(angle);c,s=math.cos(theta),math.sin(theta)
    a,b,c_,d=c*sx,s*sx,-s*sy,c*sy
    x,y=PIVOT
    return (a,b,c_,d,x-a*x-c_*y,y-b*x-d*y)


def transform_point(point,m):
    a,b,c,d,e,f=m;x,y=point
    return a*x+c*y+e,b*x+d*y+f


def forward_world(point,state):
    x,y,z=state['actor_transform'];local=((point[0]-x)/z,(point[1]-y)/z)
    out=transform_point(local,state.get('performance',{}).get('matrix_native',(1,0,0,1,0,0)))
    return x+z*out[0],y+z*out[1]


def inverse_world(point,state):
    x,y,z=state['actor_transform'];px,py=(point[0]-x)/z,(point[1]-y)/z
    a,b,c,d,e,f=state.get('performance',{}).get('matrix_native',(1,0,0,1,0,0))
    determinant=a*d-b*c
    return x+z*(d*(px-e)-c*(py-f))/determinant,y+z*(-b*(px-e)+a*(py-f))/determinant


def _direction(t):
    sy=1.;angle=0.;phase='geste'
    keys=[(0.,1.),(.35,1.),(.65,.94),(1.05,1.025),(1.4,1.),(2.70,1.),(2.9,.94),(3.15,1.02),(3.5,1.),
          (5.75,1.),(5.95,1.03),(6.18,.94),(6.5,1.025),(6.8,1.),(7.58,.95),(7.8,1.04),(8.,1.),
          (12.75,1.),(12.9,1.05),(13.1,.90),(13.3,1.04),(13.55,1.),(13.95,.90),(14.13,1.08),(14.35,1.),
          (17.75,1.),(17.87,1.07),(18.04,.87),(18.18,1.05),(18.4,1.),(18.69,.90),(18.85,1.10),(19.,1.),
          (24.5,1.),(25.2,1.035),(25.38,.94),(25.55,1.),(26.4,1.),(26.52,.80),(26.65,.80),(26.9,1.10),(27.15,1.),
          (28.,1.),(28.15,1.08),(28.25,.80),(28.375,.80),(28.54,1.12),(28.75,1.),
          (31.5,1.),(31.667,1.04),(31.833,.80),(31.958,.80),(32.15,1.10),(32.4,.98),(32.65,1.),
          (34.7,1.),(35.25,1.025),(35.65,1.)]
    sy=curve(t,keys)
    if t<2.35:angle=curve(t,[(0.,0.),(.6,-2.5),(1.7,-2.5),(2.35,0.)]);phase='chef_heureux'
    elif t<3.5:angle=curve(t,[(2.35,0.),(2.75,0.),(3.02,3.2),(3.5,3.2)]);phase='inspection'
    elif 7.05<=t<7.58:angle=-1.5;phase='satisfaction'
    elif 12.75<=t<14.25:angle=curve(t,[(12.75,0.),(13.1,-3.),(13.7,-3.),(14.25,0.)]);phase='impatience'
    elif 17.75<=t<19.:angle=curve(t,[(17.75,0.),(18.05,-4.2),(18.65,-4.2),(19.,0.)]);phase='automatisme'
    elif 21.<=t<23.:angle=curve(t,[(21.,0.),(21.65,-3.),(21.95,-4.),(22.45,-4.),(22.7,2.5),(23.,2.5)]);phase='resister_puis_ceder'
    elif 25.55<=t<28.:angle=curve(t,[(25.55,0.),(25.9,-4.),(26.15,-4.),(26.4,-4.),(27.35,-3.),(28.,0.)]);phase='finir_malgre_fumee'
    elif 28.<=t<28.75:angle=curve(t,[(28.,0.),(28.25,4.),(28.375,4.),(28.54,-5.),(28.75,0.)]);phase='jet_excessif'
    elif 31.5<=t<33.25:angle=curve(t,[(31.5,0.),(31.667,0.),(31.833,8.),(31.958,8.),(32.15,5.),(32.5,3.),(33.25,3.)]);phase='repas_perdu'
    elif t>=33.25:angle=curve(t,[(33.25,3.),(34.7,3.),(35.25,-2.),(35.75,-2.),(37.25,-2.)]);phase='fausse_victoire'
    return sy,angle,phase


def apply(t,state,animation):
    if state['shot']=='sink':return state
    t=min(float(t),37.25)
    requested_sy,requested_angle,phase=_direction(t)
    initial_meta=state['arm_meta'];original_hands=dict(state['hands']);transform=state['actor_transform']
    constrained=set(state.get('lock_world_hands',()))
    if state.get('spoon_held'):constrained.add('left')
    if state.get('carrot',{}).get('knife_held'):constrained.update(('left','right'))
    if state.get('salt',{}).get('active') and t<20.6:constrained.update(('left','right'))
    if state.get('paper',{}):
        if state['paper']['mode'] in ('pull','tiny_pull'):constrained.update(('left','right'))
    def build(alpha):
        sy=1.+(requested_sy-1.)*alpha;sx=1./sy;angle=requested_angle*alpha
        coeffs=matrix(sx,sy,angle)
        state['performance']={'matrix_native':list(coeffs),'scale_x':sx,'scale_y':sy,'angle_deg':angle}
        result={}
        for side in ('left','right'):
            old=initial_meta[side]
            if side in constrained:
                solver_target=inverse_world(original_hands[side],state)
                meta=native._solve(animation,side,solver_target,transform,old)
                raw=meta['hand'];actual=forward_world(raw,state)
                meta.update(unposed_hand=raw,hand=actual,target=original_hands[side],target_world=original_hands[side],
                            solver_target=solver_target,contact_error=math.dist(actual,original_hands[side]))
            else:
                meta=dict(old);raw=animation.world_grip(side,meta['hips'],meta['clasp'],meta['rotation'],transform,meta.get('grip_depth',16.))
                actual=forward_world(raw,state)
                meta.update(unposed_hand=raw,hand=actual,target=actual,target_world=actual,contact_error=0.)
            result[side]=meta
        return result,sx,sy,angle,coeffs
    alpha=1.;metas,sx,sy,angle,coeffs=build(alpha)
    for _ in range(14):
        if all(metas[side]['contact_error']<.03+float(initial_meta[side].get('contact_error',0.)) for side in constrained):break
        alpha*=.5;metas,sx,sy,angle,coeffs=build(alpha)
    state['hands']={side:meta['hand'] for side,meta in metas.items()};state['arm_meta']=metas
    state['arms']=''.join(animation.draw_arm(side,metas[side]) for side in ('left','right'))
    torso=animation._torso_for_pose(state['pose'],state['whistle']);feet=[]
    for side in ('l','r'):
        found=re.search(f'<g id="foot-{side}">.*?</g>',torso)
        assert found,(t,side)
        feet.append(found.group());torso=torso.replace(found.group(),'',1)
    state['torso']=torso
    ax,ay,az=state['actor_transform']
    state['grounded_feet']=(f'<g data-grounded-feet="world-anchor" transform="translate({(80.-ax)/az:.10f} {(380.-ay)/az:.10f})">'+''.join(feet)+'</g>')
    state['performance_affine_svg']='matrix('+ ' '.join(f'{v:.10f}' for v in coeffs)+')'
    state['performance'].update(requested_scale_y=requested_sy,requested_angle_deg=requested_angle,
        constrained_hands=sorted(constrained),free_hands=[s for s in ('left','right') if s not in constrained],
        feet_grounded=True,feet_world_actor_transform=[80.,380.,state['actor_transform'][2]],pivot_native=list(PIVOT),phase=phase,attenuation=alpha,area_scale=sx*sy,source_version='V26')
    paper=state.get('paper')
    if paper and paper['mode'] not in ('pull','tiny_pull'):
        left,right=state['hands']['left'],state['hands']['right']
        paper['start']=left;paper['end']=left if paper['mode']=='ball' else right
        if 'center' in paper:paper['center']=(right[0]-10.,right[1]-35.) if paper['mode'] in ('tiny','tiny_wipe') else ((left[0]+right[0])/2.,(left[1]+right[1])/2.-12.)
    return state
