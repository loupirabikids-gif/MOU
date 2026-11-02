"""A ten-second silent acting study: a feather is too much for proud MOU."""
from __future__ import annotations
import math
from personnage import default_state, character_svg, body_to_world

FPS, DURATION = 24, 10.
CONTACT, RELEASE = 3.5, 5.55


def u(t, a, b):
    return max(0., min(1., (t-a)/(b-a)))


def ease(t, a, b):
    x=u(t,a,b)
    return x*x*(3.-2.*x)


def lerp(a,b,x):
    return a+(b-a)*x


def keys(t, points):
    if t <= points[0][0]: return points[0][1]
    for (a,va),(b,vb) in zip(points,points[1:]):
        if t <= b: return lerp(va,vb,ease(t,a,b))
    return points[-1][1]


def pose_mix(a,b,amount):
    return {a:1.-amount,b:amount}


def head_anchor(actor):
    x,y=body_to_world((10.5,-202.),actor)
    return x,y-4.25*actor['scale']*actor['sy']


def state_at(t):
    t=max(0.,min(DURATION-1/FPS,float(t)))
    actor=default_state()
    actor.update(cx=480.,floor_y=1500.,scale=1.35,pose_posture=False)
    actor['cx']=lerp(480.,540.,ease(t,1.96,2.38))
    actor['hop']=48.*math.sin(math.pi*u(t,1.96,2.38)) if 1.96<t<2.38 else 0.
    actor['sx']=keys(t,[(0,1.),(1.55,.975),(1.88,1.045),(1.96,1.06),(2.12,.96),
                         (2.38,1.04),(2.58,1.),(3.5,1.),(3.625,1.42),(3.83,1.34),
                         (5.9,1.34),(6.55,1.18),(6.92,1.16),(7.13,1.41),(7.35,1.34)])
    actor['sy']=keys(t,[(0,1.),(1.55,1.05),(1.88,.95),(1.96,.93),(2.12,1.04),
                         (2.38,.96),(2.58,1.03),(3.5,1.03),(3.625,.43),(3.83,.55),
                         (5.9,.55),(6.55,.72),(6.92,.75),(7.13,.48),(7.35,.55)])
    actor['tilt']=keys(t,[(0,0),(1.1,-3),(1.8,-5),(2.38,-2),(3.15,0),
                           (3.5,0),(4.1,0),(6.55,-2),(7.35,0),(8.5,1.)])
    if t<.35:
        actor['pose']='neutre'; actor['gaze']=(.75,-.65)
    elif t<1.05:
        actor['pose_weights']=pose_mix('neutre','attention',ease(t,.35,.65))
        actor['gaze']=(.65,-1.)
    elif t<3.5:
        actor['pose_weights']=pose_mix('attention','assurance',ease(t,1.05,1.5))
        to_camera=ease(t,1.5,1.72)*(1.-ease(t,2.48,2.85))
        actor['gaze']=(.4*(1.-to_camera),-1.*(1.-to_camera))
        actor['face']={'open_l':lerp(.58,.9,ease(t,2.85,3.2)),
                       'open_r':lerp(.69,.9,ease(t,2.85,3.2))}
    elif t<5.75:
        actor['pose']='panique'; actor['gaze']=(0.,-1.)
        actor['face']={'sweat':ease(t,3.9,4.3)}
    elif t<7.55:
        actor['pose']='panique'
        actor['gaze']=(lerp(.85,0.,ease(t,5.9,6.2)),lerp(-.7,1.,ease(t,5.85,6.2)))
        effort=ease(t,6.15,6.45)*(1.-ease(t,6.92,7.2))
        actor['face']={'open_l':1.,'open_r':1.,
                       'mouth_open':lerp(.5,0.,effort),'mouth_width':46.,
                       'mouth_smile':lerp(.1,-.45,effort),'mouth_skew':0.,
                       'brow_l0':lerp(12.,-7.,effort),'brow_l1':lerp(-18.,9.,effort),
                       'brow_r0':lerp(-18.,9.,effort),'brow_r1':lerp(12.,-7.,effort),
                       'sweat':1.}
    else:
        actor['pose_weights']=pose_mix('panique','gene',ease(t,8.25,9.2))
        actor['gaze']=(0.,lerp(1.,0.,ease(t,7.55,8.05)))
        actor['face']={'mouth_open':lerp(.3,0.,ease(t,8.05,8.7))}
    # One purposeful blink before the offer, none during the final held pose.
    actor['blink']=1.-math.sin(math.pi*u(t,1.28,1.43)) if 1.28<t<1.43 else 1.
    if 6.15<t<7.2:
        strain=ease(t,6.15,6.45)*(1.-ease(t,6.92,7.2))
        actor['blink']=1.-.98*strain
    head=head_anchor(actor)
    if t<CONTACT:
        end_actor=dict(actor,cx=540.,sx=1.,sy=1.03,tilt=0.,hop=0.)
        target=head_anchor(end_actor)
        p=u(t,0.,CONTACT)
        feather={'x':lerp(710.,target[0],p)+35.*math.sin(p*math.pi*3.)*(1.-p),
                 'y':lerp(510.,target[1],p),
                 'angle':18.*math.sin(p*math.pi*3.)*(1.-p),'visible':True}
    elif t<RELEASE:
        feather={'x':head[0],'y':head[1],'angle':8.*math.sin((t-CONTACT)*3.),'visible':True}
    else:
        rest_actor=dict(actor,cx=540.,sx=1.34,sy=.55,tilt=0.,hop=0.)
        start=head_anchor(rest_actor); p=u(t,RELEASE,7.5)
        feather={'x':lerp(start[0],1330.,p),'y':lerp(start[1],380.,p),
                 'angle':lerp(2.,75.,p)+12.*math.sin(p*math.pi*3.),'visible':t<7.5}
    camera=(0.,170.,1080.,1920.) if t<7.75 else (160.,650.,760.,760.*16./9.)
    phase=('decouvrir' if t<1.05 else 'offrir_sa_tete' if t<CONTACT else
           'recevoir_le_poids' if t<4.2 else 'constater' if t<RELEASE else
           'essayer_de_se_redresser' if t<7.55 else 'sauver_les_apparences')
    return {'t':t,'actor':actor,'head':head,'feather':feather,'camera':camera,'phase':phase}


def feather_svg(feather):
    if not feather['visible']:return ''
    # Original white feather, asymmetric barbs and a visible slender quill.
    barbs=''.join(f'<path d="M{side*2} {-j*23} Q{side*25} {-j*23-9} {side*(39-j*3)} {-j*23-25}"/>'
                  for side in (-1,1) for j in range(1,6))
    return (f'<g id="plume" transform="translate({feather["x"]:.5f} {feather["y"]:.5f}) '
            f'rotate({feather["angle"]:.5f}) scale(.78)">'
            '<path d="M0 -15 C-34 -28 -55 -84 -39 -140 C-31 -171 -6 -198 4 -208 '
            'C31 -179 56 -130 44 -79 C37 -49 17 -27 0 -15 Z" fill="#FFFEF9" '
            'stroke="#61516D" stroke-width="4.5" stroke-linejoin="round"/>'
            '<g fill="none" stroke="#C8C1D4" stroke-width="2.1" stroke-linecap="round">'+barbs+'</g>'
            '<path d="M0 0 Q-10 -74 4 -192" fill="none" stroke="#61516D" '
            'stroke-width="3.6" stroke-linecap="round"/></g>')


def svg_at(t):
    state=state_at(t);a=state['actor'];c=state['camera']
    shadow_rx=240.*a['sx']*(1.-.15*a['hop']/48.)
    body=(f'<rect x="-600" y="-700" width="2400" height="3100" fill="#F1ECF8"/>'
          '<path d="M15 1500 V1020 C15 420 1065 420 1065 1020 V1500 Z" fill="#E8E0F2"/>'
          '<rect x="-600" y="1500" width="2400" height="1000" fill="#DED5E8"/>'
          '<path d="M-600 1500 H1800" stroke="#C8BDD4" stroke-width="3"/>'
          f'<ellipse cx="{a["cx"]:.5f}" cy="1506" rx="{shadow_rx:.5f}" ry="24" fill="#7D688D" opacity=".16"/>'
          +character_svg(a,'mou')+feather_svg(state['feather']))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" '
            f'viewBox="{c[0]} {c[1]} {c[2]} {c[3]}">'+body+'</svg>')
