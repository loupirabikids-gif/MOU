"""Local continuity corrections: wrist, release, pickup and a readable turn."""
from __future__ import annotations
import math


def ease(t,a,b):
    x=max(0.,min(1.,(t-a)/(b-a)));return x*x*(3.-2.*x)


def lerp(a,b,p):return a+(b-a)*p


def correct_phone_state(s):
    t=s['t'];h=s['actor']['hands']['right'];p=s['phone']
    if 1.4<=t<1.76:
        if t<1.7:h['rotation']=lerp(-5.,0.,ease(t,1.52,1.7))
        h['grip']=lerp(.15,1.,ease(t,1.60,1.76))
    if 2.8<=t<3.55:
        h['grip']=lerp(1.,.15,ease(t,2.82,3.06))
        h['rotation']=lerp(-90.,-5.,ease(t,2.88,3.20))
        if t<2.92:h['x'],h['y']=857.,1300.
        elif t<3.20:
            u=ease(t,2.92,3.20)
            h['x']=lerp(857.,865.,u);h['y']=lerp(1300.,1095.,u)
        else:
            u=ease(t,3.20,3.55)
            h['x']=865.;h['y']=lerp(1095.,1280.,u)
        # The hand clears the opening before pushing the lid down. Its final
        # closure and the existing contact sound remain at exactly3.55s.
        s['lid']=1.-ease(t,3.20,3.55)
    if 23.76<=t<24.05:
        h['rotation']=lerp(-5.,-90.,ease(t,23.76,24.05))
    if 23.90<=t<24.12:
        h['grip']=lerp(.15,1.,ease(t,23.90,24.12))
    # The stored phone, its trajectory, and its release/pickup times remain
    # unchanged. Wrist alignment is ready before the ownership changes.
    if 24.35<=t<24.7:
        turn=ease(t,24.35,24.65)
        p['plane_scale_x']=max(.055,abs(math.cos(math.pi*turn)))
        p['face']='screen'if turn<.5 else'back'
        p['turn_progress']=turn
    return s
