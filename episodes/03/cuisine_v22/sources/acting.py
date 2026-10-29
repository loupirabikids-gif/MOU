"""Five-shot acting test using only the existing MOU rig and arm solvers.

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
    """Return one state for frames0–191, with exact holds between actions.

    Metadata keys ``pro_shot`` and ``pro_test_frame`` select the camera.
    ``face_roll_deg`` must rotate the *whole* native face group, including its
    masks, around native(205,250). ``drop`` and ``ending_drop`` are aliases.
    The caller may map ``pro_test_time`` to a later full-episode time.
    """
    f=max(0.,min(float(NFRAMES-1),float(frame)))
    a=animation_module
    state=copy.deepcopy(base_state)
    left_rest=a.rest_hand('left',TRANSFORM)
    right_rest=a.rest_hand('right',TRANSFORM)
    wet_hold=(475.,1165.)
    tube=(876.,1175.)
    right_paper=(810.,1217.)
    right_clear=(700.,1240.)
    cloth=(TRANSFORM[0]+195.*TRANSFORM[2],TRANSFORM[1]+385.*TRANSFORM[2])
    bin_target=(165.,1475.)
    audience=(TRANSFORM[0]+202.*TRANSFORM[2],TRANSFORM[1]+234.*TRANSFORM[2])

    # The right arm starts after the eyes and pauses before an empty tube.
    left=wet_hold
    if f<10.:
        right=right_rest
    elif f<24.:
        right=a.arc_point(right_rest,right_paper,_smooth(_u(f,10.,24.)),
                          'right',TRANSFORM)
    elif f<40.:
        right=right_paper
    elif f<56.:
        right=a.arc_point(right_paper,right_clear,_smooth(_u(f,40.,56.)),
                          'right',TRANSFORM)
    else:
        right=right_clear

    # Enter, make ONE lateral pass, then lift clear of the mark for8 frames.
    if 76.<=f<84.:
        left=_move(f,(76.,84.),wet_hold,(535.,1208.))
    elif 84.<=f<104.:
        left=_move(f,(84.,104.),(535.,1208.),(575.,1208.))
    elif 104.<=f<108.:
        left=_move(f,(104.,108.),(575.,1208.),wet_hold)
    elif 108.<=f<116.:
        left=wet_hold
    elif f>=116.:
        # Start the wide shot on the same hand positions as the macro exit;
        # withdraw them together and then hold the native folded pose.
        left=_move(f,(116.,124.),wet_hold,left_rest)
        right=a.arc_point(right_clear,right_rest,_smooth(_u(f,116.,124.)),
                          'right',TRANSFORM)

    lm=a.solve_arm('left',left,TRANSFORM)
    rm=a.solve_arm('right',right,TRANSFORM)
    anchor=_lower_cap_anchor(a,'left',lm)

    if f<4.:
        look=anchor
    elif f<10.:
        look=_move(f,(4.,10.),anchor,tube)
    elif f<48.:
        look=tube
    elif f<56.:
        look=_move(f,(48.,56.),tube,cloth)
    elif f<116.:
        look=cloth
    elif f<122.:
        look=_move(f,(116.,122.),cloth,bin_target)
    elif f<160.:
        look=bin_target
    elif f<166.:
        look=_move(f,(160.,166.),bin_target,audience)
    else:
        look=audience

    pose=copy.deepcopy(state['pose'])
    pose.update(arm_hips=0.,arm_clasp=1.,laugh=0.,lift_l=0.,lift_r=0.)
    if f<12.:
        values=_pose('notice_drop')
    elif f<20.:
        values=_pose('notice_drop','contrariete',_smooth(_u(f,12.,20.)))
    elif f<64.:
        values=_pose('contrariete')
    elif f<68.:
        values=_pose('contrariete','solution',_smooth(_u(f,64.,68.)))
    elif f<116.:
        values=_pose('solution')
    elif f<172.:
        values=_pose('waste_realisation')
    elif f<176.:
        values=_pose('waste_realisation','caught',_smooth(_u(f,172.,176.)))
    else:
        values=_pose('caught')
    pose.update(values)

    # A single short blink accompanies the change of attention, rather than
    # a loop. The target moves while the lids close; the thought then holds.
    if 48.<=f<52.:
        blink={48.:.38,49.:.035,50.:.035,51.:.42}
        factor=blink[float(math.floor(f))]
        pose['eye_open_l']*=factor
        pose['eye_open_r']*=factor

    if f<40.:
        roll=0.
    elif f<48.:
        roll=2.5
    elif f<56.:
        roll=2.5-4.5*_smooth(_u(f,48.,56.))
    elif f<64.:
        roll=-2.
    elif f<68.:
        roll=-2.+2.*_smooth(_u(f,64.,68.))
    elif f<116.:
        roll=0.
    elif f<122.:
        roll=-2.*_smooth(_u(f,116.,122.))
    elif f<160.:
        roll=-2.
    elif f<166.:
        roll=-2.+2.*_smooth(_u(f,160.,166.))
    else:
        roll=0.
    a.look_at(pose,_inverse_face_target(look,roll),TRANSFORM)

    shot=next(s['id'] for s in SPEC['shots'] if s['start']<=f<s['stop'])
    drop_amount=1.-_smooth(_u(f,84.,89.))
    wetness=_smooth(_u(f,84.,94.))
    drop={'anchor':anchor,'amount':drop_amount,'hand_side':'left'}
    contact={'active':84.<=f<104.,'point':cloth,'native_point':(195.,385.),
             'point_world':anchor,
             'point_local':((anchor[0]-TRANSFORM[0])/TRANSFORM[2],
                            (anchor[1]-TRANSFORM[1])/TRANSFORM[2]),
             'hand_side':'left','contact_start_frame':84,'contact_stop_frame':104}
    state.update(actor_transform=TRANSFORM,pose=pose,
                 arm_meta={'left':lm,'right':rm},
                 hands={'left':lm['hand'],'right':rm['hand']},
                 arms=a.draw_arm('left',lm)+a.draw_arm('right',rm),
                 torso=a._torso_for_pose(pose,state['whistle']),
                 shot='wide',phase='pro_apron_test',paper=None,water=False,
                 wet_hand=False,lever=0.,spoon=None,spoon_held=False,tomato=None,
                 proud_nod_offset=0.,acting_body_offset=(0.,0.),
                 pro_test_frame=f,pro_test_time=f/FPS,pro_shot=shot,
                 face_roll_deg=roll,look_target=look,drop=drop,ending_drop=drop,
                 apron_wetness=wetness,contact_apron=contact,
                 bin_count=4,paper_disposed_count=5,flying_ball=None,
                 floor_ball={'x':325.,'y':1805.,'r':22.,'rotation':12.,
                             'id':5,'visual_seed':4})
    state['whistle']={**state['whistle'],'active':False,'amount':0.}
    return state
