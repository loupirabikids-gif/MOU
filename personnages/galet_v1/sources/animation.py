"""One five-second silent acting test on the original floating-mitten rig."""
from __future__ import annotations

import math
import rig

DURATION=5.;FPS=24;TRANSFER=1.6;FINAL_HOLD=4.5
LEFT_LOCAL=rig.GLOVE_OPEN[15]


def smooth(v):
    v=max(0.,min(1.,v));return v*v*(3.-2.*v)


def u(t,a,b):return smooth((t-a)/max(1e-9,b-a))


def mix(a,b,v):return a+(b-a)*v


def point(a,b,v):return tuple(mix(x,y,v)for x,y in zip(a,b))


def curve(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return mix(x,y,u(t,a,b))
    return keys[-1][1]


def pulse(t,a,b,c,d):return u(t,a,b)*(1.-u(t,c,d))


def right_anchor_local(pinch):return rig.cubic(rig.glove_points(pinch)[9:13],.5)


def _hand(x,y,rotation,mirror,pinch=0.):
    return {'x':x,'y':y,'rotation':rotation,'mirror':mirror,'scale':1.2,'pinch':pinch}


def _at_anchor(hand,local,world):
    old=rig.hand_local_to_world(local,hand)
    return {**hand,'x':hand['x']+world[0]-old[0],'y':hand['y']+world[1]-old[1]}


def scene_state(time):
    real=max(0.,min(DURATION,float(time)));t=min(real,FINAL_HOLD)
    # A held ground anchor gives the pebble weight; no decorative idle sway.
    sy=curve(t,[(0.,1.),(.35,1.),(.58,.97),(.75,1.),(2.55,1.),(2.75,.94),
                (2.90,1.025),(3.10,1.),(3.8,1.),(4.08,1.025),(4.35,1.)])
    rotation=curve(t,[(0.,-2.),(.35,-2.),(.70,3.),(1.2,3.),(2.25,3.),
                       (2.7,-3.5),(3.45,-3.5),(3.85,0.),(4.35,-1.)])
    body={'sx':1./sy,'sy':sy,'rotation':rotation,'dx':0.,'dy':0.}
    left=_hand(225.,1154.,14.,True)
    # Raise the dirty hand for inspection before the other moves toward it.
    lift=u(t,.18,.65)
    left['y']-=24.*lift;left['rotation']+=2.*lift
    left_crumb=rig.hand_local_to_world(LEFT_LOCAL,left)
    pinch=u(t,1.20,1.45)
    right=_hand(890.,1143.,-16.,False,pinch)
    if .55<=t<.70:
        right['y']+=10.*u(t,.55,.70)
    if .70<=t<1.20:
        v=u(t,.70,1.20);right['rotation']=mix(-16.,-74.,v)
        contact=_at_anchor({**right,'rotation':-74.,'pinch':0.},right_anchor_local(0.),left_crumb)
        right['x'],right['y']=rig.cubic(((890.,1153.),(800.,1410.),
                                        (260.,1280.),(contact['x'],contact['y'])),v)
    elif 1.20<=t<TRANSFER:
        right['rotation']=-74.
        right=_at_anchor(right,right_anchor_local(pinch),left_crumb)
    elif t>=TRANSFER:
        # At the transfer both real surface anchors are coincident. The crumb
        # changes parent, then leaves with the right hand; it never teleports.
        contact=_at_anchor({**right,'rotation':-74.,'pinch':1.},right_anchor_local(1.),left_crumb)
        v=u(t,TRANSFER,2.18)
        right['x'],right['y']=rig.cubic(((contact['x'],contact['y']),(300.,1300.),
                                        (805.,1420.),(892.,1121.)),v)
        right['rotation']=mix(-74.,-12.,v)
    # The empty hand stays exposed; a tiny lower at the final reaction creates
    # an asymmetry, without replacing the manipulation by a symmetrical shrug.
    left['y']+=22.*u(t,3.55,4.15)
    right['y']-=10.*u(t,3.55,4.15)
    owner='left'if t<TRANSFER else'right'
    anchor=rig.hand_local_to_world(LEFT_LOCAL,left)if owner=='left'else rig.hand_local_to_world(right_anchor_local(right['pinch']),right)
    crumb={'x':anchor[0],'y':anchor[1],'rotation':-9. if owner=='left'else right['rotation']+65.,'owner':owner}
    target=(540.,1060.);audience=True
    if t>=.12:
        audience=False;target=point((540.,1060.),left_crumb,u(t,.12,.35))
    if 1.2<=t<1.7:target=left_crumb
    if 1.7<=t<2.25:target=rig.hand_local_to_world(LEFT_LOCAL,left)
    if 2.25<=t<2.60:target=point(rig.hand_local_to_world(LEFT_LOCAL,left),(crumb['x'],crumb['y']),u(t,2.25,2.60))
    if 2.60<=t<3.72:target=(crumb['x'],crumb['y'])
    if 3.72<=t<4.05:target=point((crumb['x'],crumb['y']),(540.,1060.),u(t,3.72,4.05))
    if t>=4.05:audience=True
    notice=u(t,.35,.60);shock=pulse(t,2.60,2.77,3.05,3.30);save=u(t,3.85,4.30)
    forward_weight=0.
    if t<.35:
        target=left_crumb;forward_weight=1.-u(t,.12,.35)
    elif t>=3.72:
        target=(crumb['x'],crumb['y']);forward_weight=u(t,3.72,4.05)
    face={'target':target,'audience':audience,'forward_weight':forward_weight,
          'open_l':mix(.75,.98,notice)-save*.04,'open_r':mix(.92,1.,notice)-save*.16,
          'brow_l':mix(-.25,.05,notice)+shock*.8+save*.38,
          'brow_r':mix(-.2,-.05,notice)-shock*.45-save*.10,
          'brow_raise':.10+shock*.7+save*.25,
          'pupil':1.-shock*.24,'smile':curve(t,[(0.,.65),(.65,.25),(2.25,.27),(2.70,-.12),(3.60,-.12),(4.30,.15)]),
          'skew':mix(.15,1.5,save),'mouth_width':curve(t,[(0.,66.),(.65,42.),(2.60,42.),(2.82,28.),(3.30,37.),(4.30,65.)]),
          'mouth_open':shock*.56,'blink':1.}
    if 3.875<=t<4.0416666667:
        face['blink']=(.45,.08,.08,.50)[min(3,int((t-3.875)*FPS))]
    phase=('assurance_et_trace'if t<.7 else'approche'if t<1.2 else'prise'if t<1.8 else
           'gauche_propre_droite_collante'if t<2.7 else'constat'if t<3.8 else'dignite_de_facade')
    return {'time':real,'acting_time':t,'body':body,'hands':{'left':left,'right':right},
            'crumb':crumb,'face':face,'phase':phase,'transfer_s':TRANSFER,'hold_s':FINAL_HOLD}


def svg_at(t):return rig.svg(scene_state(t))
