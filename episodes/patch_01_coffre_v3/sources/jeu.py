"""Purposeful acting for PATCH, reconstructed from the supplied reference.

All gestures are analytic poses with continuous transitions. Validated prop
contacts stay untouched through locking, pencil release and phone recovery.
The scene must attach the recovered phone to the resulting right palm.
"""
from __future__ import annotations
from copy import deepcopy
import math
from personnage import BASE, SHOULDERS, face_parameters, to_local, to_world


def clamp(x):return max(0.,min(1.,x))
def ease(t,a,b):
    p=clamp((t-a)/(b-a));return p*p*(3.-2.*p)
def lerp(a,b,p):return a+(b-a)*p
def point(a,b,p):return tuple(lerp(x,y,p)for x,y in zip(a,b))


def _elbow(a,side):
    if side in a.get('elbows',{}):return tuple(a['elbows'][side])
    h=a['hands'][side];hx,hy=to_local((h['x'],h['y']),a);sx,sy=SHOULDERS[side]
    dx,dy=hx-sx,hy-sy;length=max(1.,math.hypot(dx,dy))
    wx,wy=hx-dx/length*26.,hy-dy/length*26.
    return to_world(((sx+wx)/2.+(-20. if side=='left' else 20.),(sy+wy)/2.+12.),a)


def _blend(a,b,p):
    if p<=0.:return deepcopy(a)
    if p>=1.:return deepcopy(b)
    out=deepcopy(a)
    for key,default in [('cx',540.),('floor_y',1570.),('scale',1.),('body_tilt',0.),
                        ('head_tilt',0.),('head_scale',1.),('tail_angle',0.),('blink',1.)]:
        out[key]=lerp(a.get(key,default),b.get(key,default),p)
    for key,default in [('lean',(0.,0.)),('head_shift',(0.,0.)),('gaze',(.4,-.35))]:
        out[key]=point(a.get(key,default),b.get(key,default),p)
    out['hands']={side:{key:lerp(a['hands'][side].get(key,0.),b['hands'][side].get(key,0.),p)
                        for key in ('x','y','rotation','grip')}for side in ('left','right')}
    out['elbows']={side:point(_elbow(a,side),_elbow(b,side),p)for side in ('left','right')}
    af,bf=face_parameters(a),face_parameters(b)
    out.pop('pose_weights',None);out['pose']='curieux'
    out['face']={key:lerp(af[key],bf[key],p)for key in BASE}
    return out


def _target(a,pose,lean,head_shift=(0.,0.),head_tilt=0.,hands=None,elbows=None):
    out=deepcopy(a);out.pop('pose_weights',None);out.pop('face',None)
    out['pose']=pose;out['lean']=tuple(lean);out['body_tilt']=0.
    out['head_shift']=head_shift;out['head_tilt']=head_tilt;out['head_scale']=1.
    if hands:out['hands']={s:dict(out['hands'][s],**h)for s,h in hands.items()}
    if elbows:out['elbows']=elbows
    return out


def performance(t,actor):
    """Return an independent actor state; the input and its props are untouched."""
    a=deepcopy(actor)
    a['performance_state']='base'
    if 6.<=t<10.:
        start=6. if t<8. else 8.;p=(t-start)/2.
        # The torso straightens and the pencil settles for a real new attempt.
        reset=ease(p,.68,.84)*(1.-ease(p,.94,1.))
        a['lean']=(a['lean'][0],a['lean'][1]-15.*reset)
        a['head_tilt']-=3.8*reset
        a['hands']['left']['y']-=10.*reset
        a['performance_state']='attempt_again'
        return a
    if 12.3<=t<23.:
        # The normal-size paw carries the left cheek. Elbow control bends the
        # sleeve down toward the desktop instead of stretching a straight arm.
        breath=1.1*math.sin((t-12.3)*2.6)
        cheek=_target(a,'ennui',(-20.,30.),head_shift=(0.,12.+breath),head_tilt=-8.,
            hands={'left':{'x':350.,'y':1166.,'rotation':12.,'grip':.12},
                   'right':{'x':656.,'y':1313.,'rotation':-10.,'grip':.1}},
            elbows={'left':(275.,1345.),'right':(644.,1280.)})
        crossed=_target(a,'impatient',(0.,7.),head_shift=(0.,0.),head_tilt=1.,
            hands={'left':{'x':600.,'y':1233.,'rotation':-62.,'grip':.2},
                   'right':{'x':449.,'y':1260.,'rotation':63.,'grip':.2}},
            elbows={'left':(451.,1365.),'right':(611.,1350.)})
        low=_target(a,'suppliant',(90.,105.),head_shift=(0.,28.),head_tilt=3.,
            hands={'left':{'x':485.,'y':1304.,'rotation':-6.,'grip':.08},
                   'right':{'x':670.,'y':1307.,'rotation':5.,'grip':.08}},
            elbows={'left':(472.,1320.),'right':(706.,1335.)})
        out=_blend(a,cheek,ease(t,12.3,12.86))
        out=_blend(out,crossed,ease(t,15.2,15.78))
        out=_blend(out,low,ease(t,18.15,18.82))
        # Keep each minute's directed gaze, with a small accompanying head move.
        out['gaze']=a['gaze'];out['head_tilt']+=.9*clamp((a['gaze'][0]+.1)/1.1)
        out['performance_state']='cheek' if t<15.2 else 'crossed' if t<18.15 else 'low'
        # Release the waiting pose into the already validated lid/phone action.
        out=_blend(out,a,ease(t,22.42,23.))
        return out
    if 24.7<=t<26.65:
        # Crouch, quick buoyant rise, brief apex, soft overshoot and recovery.
        keys=[(24.7,0.),(24.9,23.),(25.12,-94.),(25.3,-102.),(25.57,12.),(25.79,-8.),(26.1,0.),(26.65,0.)]
        dy=0.
        for (ta,va),(tb,vb) in zip(keys,keys[1:]):
            if ta<=t<=tb:dy=lerp(va,vb,ease(t,ta,tb));break
        delight=ease(t,24.7,24.98)*(1.-ease(t,26.02,26.65))
        happy=_target(a,'joie',(0.,dy),head_shift=(0.,0.),head_tilt=-5.*delight,
            hands={'left':{'x':lerp(390.,590.,delight),'y':lerp(1310.,1160.,delight)+dy,
                            'rotation':lerp(-12.,-45.,delight),'grip':.25},
                   'right':{'x':lerp(750.,722.,delight),'y':lerp(1190.,1120.,delight)+dy,
                             'rotation':lerp(-10.,-4.,delight),'grip':1.}})
        happy['tail_angle']=12.*math.sin(math.pi*delight)
        if 24.92<t<25.08:
            happy['blink']=1.-.92*math.sin(math.pi*ease(t,24.92,25.08))
        happy['performance_state']='joy_bounce'
        return _blend(a,happy,ease(t,24.7,24.88))
    if t>=27.9:
        content=_target(a,'idee',(0.,0.),head_tilt=-3.,
            hands={'left':{'x':610.,'y':1217.,'rotation':-62.,'grip':.65},
                   'right':{'x':724.,'y':1190.,'rotation':-8.,'grip':1.}})
        content['face']={'mouth_width':70.,'mouth_open':0.,'mouth_smile':1.,'sparkle':.3}
        content['gaze']=(.95,.85);content['performance_state']='absorbed'
        return _blend(a,content,ease(t,27.9,28.25))
    return a
