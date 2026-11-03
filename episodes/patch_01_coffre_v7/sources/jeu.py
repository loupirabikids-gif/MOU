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
                        ('head_tilt',0.),('head_scale',1.),('tail_angle',0.),('blink',1.),
                        ('screen_glow',0.),('jump_spread',0.),('_phone_progress',0.)]:
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


def _rotate(point,angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    return (point[0]*c-point[1]*s,point[0]*s+point[1]*c)


def _key(t,points):
    if t<=points[0][0]:return points[0][1]
    for (ta,va),(tb,vb) in zip(points,points[1:]):
        if t<=tb:return lerp(va,vb,ease(t,ta,tb))
    return points[-1][1]


def _blink(t,start,end):
    return 1.-.99*math.sin(math.pi*clamp((t-start)/(end-start))) if start<t<end else 1.


def phone_binding(t,actor):
    """Bind the same physical phone to the right palm and its second grip.

    Before 24.7 s the established pickup offset is exact. During the visible
    regrouping the offset changes continuously, then the two palms grip
    opposite edges with a 15 px vertical offset from the phone centre.
    """
    b=actor.get('_phone_progress',0.)
    h=actor['hands']['right'];angle=float(h['rotation'])
    offset=point((25.,-30.),(-42.,-15.),b)
    dx,dy=_rotate(offset,angle);center=(h['x']+dx,h['y']+dy)
    grips={side:(actor['hands'][side]['x'],actor['hands'][side]['y'])for side in ('left','right')}
    return {'center':center,'angle':angle,'face':'back' if t>=24.7 else 'screen',
            'bilateral':b>=1.-1e-9,'offset_from_right':offset,'grip_points':grips}


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
        out=_blend(out,crossed,ease(t,15.2,15.43))
        out=_blend(out,low,ease(t,18.15,18.82))
        # Keep each minute's directed gaze, with a small accompanying head move.
        out['gaze']=a['gaze'];out['head_tilt']+=.9*clamp((a['gaze'][0]+.1)/1.1)
        if 15.16<t<15.47:
            out['blink']=min(out.get('blink',1.),_blink(t,15.16,15.47))
        if 15.43<=t<18.15:
            out['tail_angle']=8.*math.sin((t-15.43)*5.6)
        if 18.15<=t<22.42:
            # The eye change is an event, after the head has approached.
            widen=ease(t,18.94,19.10)
            sleepy=face_parameters(dict(out,pose='ennui',pose_weights=None,face={}))
            eager=face_parameters(dict(out,pose='suppliant',pose_weights=None,face={}))
            out['face']={k:lerp(sleepy[k],eager[k],widen)for k in BASE}
            out['blink']=min(out.get('blink',1.),_blink(t,18.84,19.10))
            out['gaze']=(.70+.25*clamp((a['gaze'][0]+.1)/1.1),-.10)
        out['performance_state']='cheek' if t<15.2 else 'crossed' if t<18.15 else 'low'
        # Release the waiting pose into the already validated lid/phone action.
        out=_blend(out,a,ease(t,22.42,23.))
        return out
    if 24.7<=t<26.65:
        # One fast release into a held airborne pose, with both feet visible.
        dy=_key(t,[(24.7,0.),(24.90,12.),(25.04,18.),(25.10,-355.),
                   (25.24,-370.),(25.98,-345.),(26.65,-315.)])
        grip=ease(t,24.84,25.04)
        right={'x':lerp(750.,742.,grip),'y':lerp(1190.,1155.,grip)+dy,
               'rotation':lerp(-10.,0.,grip),'grip':1.}
        offset=point((25.,-30.),(-42.,-15.),grip)
        ox,oy=_rotate(offset,right['rotation']);cx,cy=right['x']+ox,right['y']+oy
        lx,ly=_rotate((-42.,15.),right['rotation'])
        # The left palm approaches, then really shares the phone's opposite edge.
        lifted=(lerp(390.,454.,ease(t,24.7,24.84)),lerp(1310.,1190.,ease(t,24.7,24.84))+dy)
        left_xy=point(lifted,(cx+lx,cy+ly),grip)
        happy=_target(a,'joie',(0.,dy),head_tilt=-3.,
            hands={'left':{'x':left_xy[0],'y':left_xy[1],
                           'rotation':lerp(-12.,-28.,grip),'grip':.85*grip},
                   'right':right},
            elbows={'left':(478.,1270.+dy),'right':(718.,1250.+dy)})
        # Before the release: small closed pleasure, then open joy in the air.
        erupt=ease(t,25.04,25.12)
        happy['face']={'mouth_open':lerp(.02,.64,erupt),'mouth_width':lerp(63.,82.,erupt),
                       'mouth_smile':1.,'sparkle':lerp(.25,1.,erupt)}
        happy['blink']=_blink(t,24.88,25.08)
        happy['gaze']=(.86,.56)
        happy['tail_angle']=10.*math.sin((t-24.7)*4.0)
        happy['_phone_progress']=grip
        happy['seated']=t<25.04
        happy['jump_spread']=ease(t,25.04,25.12)
        happy['airborne']=t>=25.08
        happy['screen_glow']=.18*grip
        happy['performance_state']='whole_body_joy'
        return happy
    if t>=26.65:
        content=_target(a,'idee',(0.,0.),head_tilt=-3.,
            hands={'left':{'x':498.,'y':1255.,'rotation':-28.,'grip':.85},
                   'right':{'x':582.,'y':1255.,'rotation':0.,'grip':.85}},
            elbows={'left':(434.,1295.),'right':(630.,1295.)})
        content['face']={'mouth_width':70.,'mouth_open':0.,'mouth_smile':1.,'sparkle':.3}
        content['gaze']=(.04,1.);content['performance_state']='absorbed_two_hands'
        content['_phone_progress']=1.;content['screen_glow']=.62
        content['seated']=True;content['airborne']=False
        return content
    return a
