"""V26: re-stage canonical cooking gestures on the 38-second dramatic clock.

Reference gestures are retimed by action phase. MOU's four decisions, true
elastic acting and false victory are newly directed, not a shortened V25 film.
"""
from __future__ import annotations
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;EP=HERE.parent
sys.path.insert(0,str(HERE))
_spec=importlib.util.spec_from_file_location('mou_v26_reference_animation',HERE/'reference_animation.py')
_reference=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=_reference;_spec.loader.exec_module(_reference)
PRODUCTION_TIMELINE=json.loads((EP/'chronologie.json').read_text())
DURATION=38.;FPS=24;CYCLES=PRODUCTION_TIMELINE['cycles'];TIMELINE=PRODUCTION_TIMELINE
OLD_CYCLES=_reference.PRODUCTION_TIMELINE['cycles']
import performance as _performance
import jeu_visage as _jeu_visage

# Present the native rounded ends below the mouth. These modest targets come
# from the original hips/clasp controls, with small shoulder rotations, rather
# than turning whole arms sideways above the shoulders.
FINAL_HAND_TARGETS={
    side:_reference.world_grip(side,.7,.25,-8. if side=='left' else 8.,(80.,380.,2.3))
    for side in ('left','right')
}


def __getattr__(name):return getattr(_reference,name)


def _u(t,a,b):return max(0.,min(1.,(float(t)-a)/max(1e-9,b-a)))


def _smooth(x):return x*x*(3.-2.*x)


def _point(a,b,u):return tuple(x+(y-x)*u for x,y in zip(a,b))


def _map(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*_u(t,a,b)
    return keys[-1][1]


def _source_at(t):
    if t<3.5:return _map(t,[(0.,0.),(2.35,6.6),(2.75,7.),(3.5,7.75)])
    if 8.75<=t<11.:
        return _map(t,[(8.75,13.5),(9.4,14.55),(9.98,15.25),(10.4,15.95),(10.5,16.3),(11.,16.5)])
    if 15.<=t<16.25:return _map(t,[(15.,21.5),(15.58,22.3),(16.,22.75),(16.25,23.)])
    if 19.5<=t<21.:
        return _map(t,[(19.5,27.),(19.75,27.35),(20.,27.65),(20.1,28.05),(20.6,28.55),(21.,28.8)])
    if 21.<=t<23.:return 28.85
    for c,index in zip(CYCLES,(0,1,2,4)):
        old=OLD_CYCLES[index]
        if c['sink'][0]<=t<c['sink'][1]:
            return _map(t,[(c['sink'][0],old['sink'][0]),(c['open'][1],old['open'][1]),
                (c['close'][0],old['close'][0]),(c['sink'][1],old['sink'][1])])
        if c['reach'][0]<=t<c['throw'][1]:
            if t<c['pull'][0]:return _map(t,list(zip(c['reach'],old['reach'])))
            if t<c['tear']:return _map(t,list(zip(c['pull'],old['pull'])))
            if c['id']==4 and t<c['wipe'][0]:return _map(t,list(zip(c['reveal'],old['reveal'])))
            if t<c['wipe'][1]:return _map(t,list(zip(c['wipe'],old['wipe'])))
            if t<c['crumple'][0]:return old['wipe'][1]-.00001
            if t<c['crumple'][1]:return _map(t,list(zip(c['crumple'],old['crumple'])))
            return _map(t,[(c['throw'][0],old['throw'][0]),(c['release'],old['release']),
                           (c['land'],old['land']),(c['throw'][1],old['throw'][1])])
    return 40.10


def _solve_targets(state,targets):
    transform=state['actor_transform']
    metas={}
    for side,target in targets.items():
        old=state['arm_meta'][side]
        metas[side]=_performance.native._solve(sys.modules[__name__],side,target,transform,old)
    state['arm_meta']=metas;state['hands']={side:m['hand'] for side,m in metas.items()}
    state['arms']=''.join(_reference.draw_arm(side,metas[side]) for side in ('left','right'))


def _stock_at(t):
    levels=(1.,.82,.58,.006,0.);remaining=1.;pulling=False
    for j,c in enumerate(CYCLES):
        if t<c['pull'][0]:break
        if t<c['pull'][1]:
            remaining=levels[j]+(levels[j+1]-levels[j])*_smooth(_u(t,*c['pull']));pulling=True;break
        remaining=levels[j+1]
    radius=math.sqrt(16.**2+(67.**2-16.**2)*remaining)
    return {'remaining':remaining,'empty':remaining<=1e-8,'pulling':pulling,
            'edge':(876.-radius,1175.),'hand':(874.-radius,1217.),
            'tab_length':40. if remaining<=.006001 else 133.}


def _ball_at(t,state):
    layout=PRODUCTION_TIMELINE['bin_layout'];state['bin_count']=sum(t>=c['land']+.14 for c in CYCLES[:3])
    state['flying_ball']=None;state['floor_ball']=None;state['overflow_phase']=None
    for c in CYCLES:
        if c['release']<=t<c['land']:
            u=_u(t,c['release'],c['land'])
            sy,angle,_=_performance._direction(c['release'])
            temporary={'actor_transform':state['actor_transform'],'performance':{'matrix_native':_performance.matrix(1./sy,sy,angle)}}
            origin=_performance.forward_world((430.,1215.),temporary)
            destination=tuple(layout['centres'][c['id']-1]) if c['id']<4 else (128.,1357.)
            control=((origin[0]+destination[0])*.5,1080.)
            xy=tuple((1.-u)**2*origin[k]+2*(1.-u)*u*control[k]+u*u*destination[k] for k in (0,1))
            state['flying_ball']={'x':xy[0],'y':xy[1],'r':layout['radii'][c['id']-1] if c['id']<4 else 22.,
                'rotation':(360.+(layout['rotations'][c['id']-1] if c['id']<4 else 0.))*u,'visual_seed':c['id'],'id':c['id']}
        if c['id']<4 and c['land']<=t<c['land']+.14:
            u=_u(t,c['land'],c['land']+.14);x,y=layout['centres'][c['id']-1]
            state['flying_ball']={'x':x,'y':y-10.*math.sin(math.pi*u),'r':layout['radii'][c['id']-1],
                'rotation':layout['rotations'][c['id']-1]+5.*math.sin(math.pi*u),'visual_seed':c['id'],'id':c['id']}
    if t>=29.:
        ball={'r':22.,'visual_seed':4,'id':4}
        if t<29.85:
            u=_u(t,29.,29.85);state['flying_ball']={**ball,'x':128.+197.*u,'y':1357.+448.*u-100.*math.sin(math.pi*u),'rotation':360.+360.*u};state['overflow_phase']='rebound_and_fall'
        else:
            u=_u(t,29.85,29.95);y=1805.-10.*math.sin(math.pi*u) if t<29.95 else 1805.
            state['floor_ball']={**ball,'x':325.,'y':y,'rotation':12.};state['overflow_phase']='settled' if t>=29.95 else 'floor_bounce'
    state['paper_disposed_count']=sum(t>=c['land'] for c in CYCLES)


def _camera(t):
    if 8.<=t<8.75 or 14.25<=t<15. or 19.<=t<19.5 or 28.75<=t<30.25:return (0.,1020.,500.,888.8888888889)
    if 8.75<=t<10.5:return (430.,1120.,420.,746.6666666667)
    if 30.25<=t<31.5:return (130.,1020.,520.,924.4444444444)
    if 21.<=t<23.:
        u=_smooth(_u(t,21.,21.95));return tuple(x+(y-x)*u for x,y in zip((70.,150.,1000.,1777.7777777778),(160.,430.,860.,1528.8888888889)))
    if 31.5<=t<35.75:return (70.,400.,960.,1706.6666666667)
    if t>=35.75:
        u=_smooth(_u(t,35.75,36.75));return tuple(x+(y-x)*u for x,y in zip((70.,400.,960.,1706.6666666667),(0.,0.,1080.,1920.)))
    if 5.75<=t<8. or 12.75<=t<14.25 or 17.75<=t<19. or 24.5<=t<28.75:return (120.,400.,920.,1635.5555555556)
    return (0.,0.,1080.,1920.)


def scene_state(playback_time):
    real_t=max(0.,min(DURATION,float(playback_time)));t=min(real_t,37.25);source=_source_at(t)
    state=copy.deepcopy(_reference._base_scene_state(source))
    c=next((c for c in CYCLES if c['trigger_start']<=t<c['throw'][1]),None)
    state.update(production_time=real_t,source_time=source,t=state['t'],production_cycle=c,cycle=c['id'] if c else 0,
                 pro_shot=None,pro_test_frame=0.,whistle=_reference.whistle_at(t),face_roll_deg=0.)
    state['shot']='sink' if c and c['sink'][0]<=t<c['sink'][1] else 'wide'
    if t<2.35:
        # Rebase the approved stir gesture as a single assembly. There is no
        # inherited periodic torso/foot translation beneath the elastic pose.
        x,y,z=state['actor_transform'];dx,dy=x-80.,y-380.
        state['actor_transform']=(80.,380.,z)
        state['hands']={side:(point[0]-dx,point[1]-dy) for side,point in state['hands'].items()}
        for side,meta in state['arm_meta'].items():
            for key in ('hand','target'):
                if key in meta:meta[key]=(meta[key][0]-dx,meta[key][1]-dy)
        if state.get('spoon'):
            for key in ('grip','bowl'):
                point=state['spoon'][key];state['spoon'][key]=(point[0]-dx,point[1]-dy)
        state['rhythm']={**state.get('rhythm',{}),'offset':[0.,0.],'body_envelope':0.}
    state['camera_viewbox']=_camera(t)
    state['tomato_added']=t>=15.58
    if t<15.:state['tomato']=_reference.TOMATO_START
    elif t>=15.58:state['tomato']=None
    state['roll']=_stock_at(t)
    state['salt']={**state.get('salt',{}),'active':19.5<=t<21.,'pinch':[19.75,20.],
                   'sprinkle':[20.1,20.6],'progress':_u(t,20.1,20.6),'bowl':(590.,1284.),'target':(301.,1300.),
                   'grains_on_hand':19.75<=t<20.6,'emission_origins':getattr(_reference,'SALT_EMISSIONS',())}
    if not state['salt']['active']:state['salt']['phase']='idle'
    if t>=10.5:state['carrot'].update(cuts=2)
    paper=state.get('paper')
    if paper:
        paper.update(cycle=c['id'],amount=c['amount'],r=PRODUCTION_TIMELINE['bin_layout']['radii'][c['id']-1] if c['id']<4 else 22.,visual_seed=c['id'],tiny=c['id']==4)
        if paper['mode'] in ('pull','tiny_pull'):paper['start']=state['roll']['edge']
    # The whole roll can shrink farther in cycle3 than in the original movie.
    # Align a hand still holding its near edge before solving the native arm.
    if c and c['pull'][0]<=t<c['wipe'][0]+.28*(c['wipe'][1]-c['wipe'][0]) and c['id']==3:
        previous=state['hands']['right'];oldroll=_reference.roll_state_at(source,_reference.PRODUCTION_TIMELINE['cycles'])
        delta=state['roll']['hand'][0]-oldroll['hand'][0]
        if t>=c['wipe'][0]:delta*=1.-_smooth(_u(t,c['wipe'][0],c['wipe'][0]+.28*(c['wipe'][1]-c['wipe'][0])))
        targets=dict(state['hands']);targets['right']=(previous[0]+delta,previous[1]);_solve_targets(state,targets)
        if paper and (_u(t,*c['pull'])<.42 or t>=c['wipe'][0]):paper['end']=state['hands']['right']
    if 21.<=t<23.:
        state.update(spoon=None,spoon_held=False,paper=None,phase='hesiter_avant_lavage',wet_hand=False,water=False,lever=0.)
        start=(475.,1165.);approach=(495.,1210.)
        if t<21.65:left=start
        elif t<21.95:left=_point(start,approach,_smooth(_u(t,21.65,21.95)))
        elif t<22.45:left=approach
        else:left=_point(approach,start,_smooth(_u(t,22.45,22.75)))
        _solve_targets(state,{'left':left,'right':_reference.rest_hand('right',state['actor_transform'])})
        state['lock_world_hands']=['left','right']
    if t>=30.25:
        state.update(actor_transform=(80.,380.,2.3),spoon=None,spoon_held=False,paper=None,phase='decouverte_et_fausse_victoire',
                     wet_hand=False,water=False,lever=0.,apron_wetness=0.,ending_drop=None,contact_apron={'active':False})
        rest={side:_reference.rest_hand(side,state['actor_transform']) for side in ('left','right')}
        # Examine one hand and then the other; the presentation grows from that
        # inspection instead of appearing as a held-pose jump at the cut.
        left=_reference.arc_move(t,(33.50,34.0),rest['left'],FINAL_HAND_TARGETS['left'],'left',state['actor_transform'])
        right=_reference.arc_move(t,(34.25,34.7),rest['right'],FINAL_HAND_TARGETS['right'],'right',state['actor_transform'])
        _solve_targets(state,{'left':left,'right':right})
    _ball_at(t,state)
    if c and c['zoom'][0]<=t<c['zoom'][1]:state['shot']='bin'
    state=_performance.apply(t,state,sys.modules[__name__])
    state=_jeu_visage.apply(t,state,sys.modules[__name__])
    state['production_time']=real_t;state['body_time']=t
    return state


def pose_at(t):return scene_state(t)['pose']

def intention_at(t):return scene_state(t)['intention']
