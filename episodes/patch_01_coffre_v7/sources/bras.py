"""V7: retreat around the closed box and press its button from the left.

The earlier hand went through the flank and sat over the first LCD digit.
This corrects only the end of closing and the button reach, not phone handling.
Explicit world-space wrist controls give the bent forearm a lateral approach.
"""
from copy import deepcopy
import math
from personnage import SHOULDERS, to_local, to_world


def ease(t,a,b):
    x=max(0.,min(1.,(t-a)/(b-a)))
    return x*x*(3.-2.*x)


def lerp(a,b,p):return a+(b-a)*p


def point(a,b,p):return tuple(lerp(x,y,p) for x,y in zip(a,b))


def key_point(t,keys):
    for (at,a),(bt,b) in zip(keys,keys[1:]):
        if t<=bt:return point(a,b,ease(t,at,bt))
    return keys[-1][1]


def default_wrist_elbow(actor):
    h=actor['hands']['right'];hx,hy=to_local((h['x'],h['y']),actor)
    sx,sy=SHOULDERS['right'];dx,dy=hx-sx,hy-sy
    length=max(1.,math.hypot(dx,dy))
    wx,wy=hx-dx/length*26.,hy-dy/length*26.
    wrist=to_world((wx,wy),actor)
    elbow=actor.get('elbows',{}).get('right',to_world(((sx+wx)/2.+20.,(sy+wy)/2.+12.),actor))
    return wrist,elbow


def apply_arms(t,actor):
    a=deepcopy(actor)
    if not 3.20<=t<4.65:return a
    h=a['hands']['right']
    if t<3.55:
        # Stay on the top of the panel rather than sagging over its front edge.
        p=ease(t,3.20,3.55)
        h['x']-=200.*p
        h['y']-=21.*p
        a['box_contact']='closing_lid'
        return a

    source=(h['x'],h['y'])
    x,y=key_point(t,[
        (3.55,(665.,1259.)),
        (3.67,(608.,1270.)),
        (3.80,(612.,1417.)),
        (3.88,(690.,1417.)),
        (4.02,(690.,1417.)),
        (4.16,(612.,1417.)),
        (4.65,(608.,1351.837158203125)),
    ])
    restore=ease(t,4.48,4.65)
    h['x'],h['y']=point((x,y),source,restore)
    wrist,elbow=default_wrist_elbow(a)
    lateral=ease(t,3.66,3.84)*(1.-ease(t,4.10,4.60))
    a.setdefault('wrists',{})['right']=point(wrist,(h['x']-45.,h['y']),lateral)
    a.setdefault('elbows',{})['right']=point(elbow,(590.,1332.),lateral)
    a['box_contact']=('button' if 3.84<=t<=4.06 else 'outside_return')
    return a
