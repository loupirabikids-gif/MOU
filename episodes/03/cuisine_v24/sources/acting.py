"""Short V24 ending using the existing MOU rig and native arm geometry.

The caller supplies a V20 animation module and a deep copy of scene_state(40.5).
Nothing in the production episodes is imported or modified here. The body
transform is constant. Camera composition and face-group rotation belong to
the renderer; this module supplies the timed poses and physical contacts.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

SPEC = json.loads(Path(__file__).with_name('poses.json').read_text())
FPS = int(SPEC['fps'])
NFRAMES = int(SPEC['frames'])
TRANSFORM = tuple(map(float, SPEC['actor_transform']))
POSES = SPEC['face_poses']


def _u(frame, start, stop):
    return max(0., min(1., (frame-start)/max(1.e-9, stop-start)))


def _smooth(value):
    return value*value*(3.-2.*value)


def _point(a, b, amount):
    return tuple(x+(y-x)*amount for x,y in zip(a,b))


def _move(frame, interval, a, b):
    return _point(a,b,_smooth(_u(frame,*interval)))


def _pose(a, b=None, amount=0.):
    first=POSES[a]
    second=POSES[b] if b else first
    return {key:float(value)+(float(second[key])-float(value))*amount
            for key,value in first.items()}


def _lower_cap_anchor(animation, side, meta):
    """Read the native cap vertices after its rigid shoulder rotation.

    The returned point is on the lower ink boundary, not a guessed palm
    centre. No cap, wrist, forearm or root geometry is redrawn.
    """
    cs=animation.controls(side,meta['hips'],meta['clasp'])
    ex,ey=cs[-1]
    tx,ty=animation._tangent(cs,1.)
    sx,sy=animation.SHOULDERS[side]
    angle=math.radians(meta['rotation'])
    ca,sa=math.cos(angle),math.sin(angle)
    x,y,scale=TRANSFORM
    vertices=[]
    for index in range(25):
        q=math.pi*index/24.
        px=ex+(-ty*math.cos(q)+tx*math.sin(q))*19.
        py=ey+(tx*math.cos(q)+ty*math.sin(q))*19.
        dx,dy=px-sx,py-sy
        vertices.append((x+scale*(sx+ca*dx-sa*dy),
                         y+scale*(sy+sa*dx+ca*dy)))
    px,py=max(vertices,key=lambda p:p[1])
    return px,py+2.6*scale


def _inverse_face_target(target, degrees):
    """Match the caller's rotation of the full face group around(205,250)."""
    ax,ay,scale=TRANSFORM
    pivot=(ax+205.*scale,ay+250.*scale)
    dx,dy=target[0]-pivot[0],target[1]-pivot[1]
    angle=math.radians(-degrees)
    ca,sa=math.cos(angle),math.sin(angle)
    return pivot[0]+ca*dx-sa*dy,pivot[1]+sa*dx+ca*dy


def state_at(frame, animation_module, base_state):
    """Short waste/audience closure, frames 0–65, with a fixed native body.

    The paper has already fallen. There is no new wet hand, apron contact or
    reach toward the empty roll. Eyes move from the waste to the audience,
    then the facial controller completes the caught reaction and holds it.
    """
    f=max(0.,min(float(NFRAMES-1),float(frame)))
    a=animation_module
    state=copy.deepcopy(base_state)
    bin_target=(165.,1475.)
    audience=(TRANSFORM[0]+202.*TRANSFORM[2],
              TRANSFORM[1]+234.*TRANSFORM[2])
    if f<26.:
        look=bin_target
        roll=-2.
    elif f<35.:
        amount=_smooth(_u(f,26.,34.))
        look=_point(bin_target,audience,amount)
        roll=-2.+2.*amount
    else:
        look=audience
        roll=0.
    pose=copy.deepcopy(state['pose'])
    pose.update(arm_hips=0.,arm_clasp=1.,laugh=0.,lift_l=0.,lift_r=0.)
    pose.update(_pose('waste_realisation' if f<36. else 'caught'))
    a.look_at(pose,_inverse_face_target(look,roll),TRANSFORM)
    shot=next(s['id'] for s in SPEC['shots'] if s['start']<=f<s['stop'])
    state.update(actor_transform=TRANSFORM,pose=pose,
                 torso=a._torso_for_pose(pose,state['whistle']),
                 shot='wide',phase='short_waste_ending',paper=None,water=False,
                 wet_hand=False,lever=0.,spoon=None,spoon_held=False,tomato=None,
                 proud_nod_offset=0.,acting_body_offset=(0.,0.),
                 pro_test_frame=f,pro_test_time=f/FPS,pro_shot=shot,
                 face_roll_deg=roll,look_target=look,drop=None,ending_drop=None,
                 apron_wetness=0.,contact_apron={'active':False},
                 bin_count=4,paper_disposed_count=5,flying_ball=None,
                 floor_ball={'x':325.,'y':1805.,'r':22.,'rotation':12.,
                             'id':5,'visual_seed':4})
    state['whistle']={**state['whistle'],'active':False,'amount':0.}
    return state
