"""Direct the selected floating-mitten pebble through the cooking episode."""
from __future__ import annotations

import json
import math
from pathlib import Path

import character
import cooking_actions
import sink_galet

EP=Path(__file__).resolve().parents[1]
TIMELINE=json.loads((EP/'chronologie.json').read_text())
DURATION=38.;FPS=24;CYCLES=TIMELINE['cycles']


def clamp(v):return max(0.,min(1.,float(v)))


def smooth(v):v=clamp(v);return v*v*(3.-2.*v)


def u(t,a,b):return smooth((t-a)/max(1e-9,b-a))


def mix(a,b,v):return a+(b-a)*v


def point(a,b,v):return tuple(mix(x,y,v)for x,y in zip(a,b))


def curve(t,keys):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y)in zip(keys,keys[1:]):
        if t<=b:return mix(x,y,u(t,a,b))
    return keys[-1][1]


def rest_hands():
    return {'left':character.hand('left',(270.,1170.),12.),
            'right':character.hand('right',(925.,1040.),-12.)}


def roll_at(t):
    levels=(1.,.82,.58,.006,0.);remaining=1.;pulling=False
    for j,c in enumerate(CYCLES):
        if t<c['pull'][0]:break
        if t<c['pull'][1]:
            remaining=mix(levels[j],levels[j+1],u(t,*c['pull']));pulling=True;break
        remaining=levels[j+1]
    radius=math.sqrt(16.**2+(67.**2-16.**2)*remaining)
    return {'remaining':remaining,'empty':remaining<1e-9,'pulling':pulling,
            'edge':(876.-radius,1175.),'radius':radius,'tab_length':40. if remaining<=.006001 else 133.}


def _paper_actions(t,c,roll):
    """Every material edge is attached to an emitted fingertip, not a proxy."""
    index=c['id'];reach,pull,wipe,crumple=c['reach'],c['pull'],c['wipe'],c['crumple']
    roll_edge=roll['edge'];start=(roll_edge[0]-19.,1268.)
    left_target=(430.-20.*(index-1),1280.)
    right_target=roll_edge
    phase='prendre_papier';paper=None;wet=t<wipe[0]+.20
    left_angle,right_angle=90.,-90.
    if t<reach[1]:
        v=u(t,*reach)
        # The insert cuts to the wet hand already touching the hanging tab.
        # Avoid forcing a wide traverse into the inherited 2–4-frame reach.
        left_target=start
        right_target=point((810.,1190.),roll_edge,v)
    elif t<pull[1]:
        v=u(t,*pull);left_target=point(start,left_target,v)
        paper={'mode':'pull','progress':v,'amount':c['amount']}
        phase='tirer_trop_de_papier'
    elif t<wipe[1]:
        p=clamp((t-wipe[0])/(wipe[1]-wipe[0]));settle=u(p,0.,.28)
        left_target=point(left_target,(480.,1230.),settle)
        right_target=point(roll_edge,(606.,1240.),settle)
        wave=math.sin(4.*math.pi*p)*math.sin(math.pi*p)
        right_target=(right_target[0]+(12.+index*3.)*wave,right_target[1]-8.*wave)
        paper={'mode':'wipe','progress':p,'amount':c['amount']}
        phase='essuyer_applique'if index==1 else'essuyer_presse'
    elif t<crumple[0]:
        left_target,right_target=(480.,1230.),(606.,1240.)
        paper={'mode':'wipe','progress':1.,'amount':c['amount']};phase='verifier_main_propre'
    else:
        v=u(t,*crumple)
        left_target=point((480.,1230.),(500.,1230.),v)
        right_target=point((606.,1240.),(555.,1230.),v)
        paper={'mode':'crumple','progress':v,'amount':c['amount'],
               'center':point((538.,1235.),left_target,v)};phase='froisser'
    if index==4:
        # The last sheet is visibly smaller, but its contour is still readable.
        left_target=(470.,1230.)
        if t<reach[1]:
            right_target=point((810.,1190.),(roll_edge[0],1217.),u(t,*reach));paper=None
        elif t<pull[1]:
            right_target=point((roll_edge[0],1217.),(690.,1235.),u(t,*pull))
            paper={'mode':'tiny_pull','progress':u(t,*pull),'amount':c['amount']}
        elif t<c['reveal'][1]:
            right_target=(690.,1235.)
            paper={'mode':'tiny','progress':1.,'amount':c['amount']};phase='decouvrir_dernier_bout'
        elif t<wipe[1]:
            p=clamp((t-wipe[0])/(wipe[1]-wipe[0]));v=u(p,0.,.30)
            wave=math.sin(4.*math.pi*p)*math.sin(math.pi*p)
            left_target=point((470.,1230.),(505.,1235.),v)
            right_target=point((690.,1235.),(540.,1235.),v)
            right_target=(right_target[0]+9.*wave,right_target[1]+5.*wave)
            paper={'mode':'tiny_wipe','progress':p,'amount':c['amount']};phase='finir_malgre_la_fumee'
        else:
            v=u(t,*crumple);left_target=point((505.,1235.),(500.,1230.),v)
            right_target=point((540.,1235.),(520.,1230.),v)
            paper={'mode':'crumple','progress':v,'amount':c['amount'],
                   'center':point((530.,1200.),left_target,v),'tiny':True};phase='froisser_dernier_bout'
        wet=t<wipe[0]+.25
    hands={'left':character.hand('left',left_target,left_angle,pinch=.25,anchor='tip'),
           'right':character.hand('right',right_target,right_angle,pinch=.55,anchor='tip')}
    if paper:
        left=character.point(hands['left'],'tip');right=character.point(hands['right'],'tip')
        paper.update(start=roll_edge if paper['mode']=='pull'else left,end=left if paper['mode']=='pull'else right,
                     cycle=index,visual_seed=index,r=TIMELINE['bin_layout']['radii'][index-1]if index<4 else 22.,tiny=index==4)
        if paper['mode'].startswith('tiny'):
            paper.update(center=(right[0]-8.,right[1]-35.),in_front=True)
    return hands,paper,wet,phase


def _throw(t,c):
    start,release,land=c['throw'][0],c['release'],c['land']
    left=point((500.,1230.),(430.,1215.),u(t,start,release))
    if t>=release:left=point((430.,1215.),(270.,1170.),u(t,release,release+.28))
    right=character.rig.cubic(((555. if c['id']<4 else 520.,1230.),(800.,1370.),
                                (970.,1190.),(925.,1040.)),u(t,start,release+.25))
    hands={'left':character.hand('left',left,90.-30.*u(t,start,release+.28),.35,anchor='tip'),
           'right':character.hand('right',right,-75.,.25,anchor='tip')}
    paper=None
    if t<release:
        paper={'mode':'ball','start':left,'end':left,'center':left,'r':TIMELINE['bin_layout']['radii'][c['id']-1]if c['id']<4 else 22.,
               'cycle':c['id'],'visual_seed':c['id'],'progress':u(t,start,release),'amount':c['amount']}
    return hands,paper


def _balls(t):
    layout=TIMELINE['bin_layout'];count=sum(t>=c['land']+.14 for c in CYCLES[:3]);flying=None;floor=None
    for c in CYCLES:
        if c['release']<=t<c['land']:
            v=clamp((t-c['release'])/(c['land']-c['release']));origin=(430.,1215.)
            dest=tuple(layout['centres'][c['id']-1])if c['id']<4 else(128.,1357.)
            control=((origin[0]+dest[0])*.5,1080.)
            xy=tuple((1.-v)**2*origin[k]+2.*(1.-v)*v*control[k]+v*v*dest[k]for k in (0,1))
            flying={'x':xy[0],'y':xy[1],'r':layout['radii'][c['id']-1]if c['id']<4 else 22.,
                    'rotation':360.*v,'visual_seed':c['id'],'id':c['id']}
        if c['id']<4 and c['land']<=t<c['land']+.14:
            v=(t-c['land'])/.14;x,y=layout['centres'][c['id']-1]
            flying={'x':x,'y':y-10.*math.sin(math.pi*v),'r':layout['radii'][c['id']-1],
                    'rotation':layout['rotations'][c['id']-1],'visual_seed':c['id'],'id':c['id']}
    if 29.<=t<29.85:
        v=(t-29.)/.85
        flying={'x':128.+197.*v,'y':1357.+448.*v-100.*math.sin(math.pi*v),'r':22.,'rotation':360.+360.*v,'visual_seed':4,'id':4}
    if t>=29.85:
        v=clamp((t-29.85)/.10)
        floor={'x':325.,'y':1805.-10.*math.sin(math.pi*v)if t<29.95 else 1805.,'r':22.,'rotation':12.,'visual_seed':4,'id':4}
    return count,flying,floor


def _body(t):
    sy=curve(t,[(0.,1.),(.35,1.),(.75,.96),(1.05,1.025),(1.4,1.),(2.75,1.),(3.02,.97),(3.3,1.),
                (5.75,1.),(5.93,.97),(6.2,1.03),(6.6,1.),(7.58,.96),(7.82,1.04),(8.05,1.),
                (12.75,1.),(12.9,.95),(13.13,1.04),(13.5,1.),(13.9,.94),(14.12,1.06),(14.4,1.),
                (17.75,1.),(17.86,.93),(18.08,1.05),(18.4,1.),(18.69,.92),(18.86,1.08),(19.2,1.),
                (24.5,1.),(25.2,.92),(25.45,1.06),(25.7,1.),(26.4,.98),(26.65,.91),(27.0,1.04),(27.35,1.),
                (28.,1.),(28.25,.86),(28.45,1.10),(28.7,1.),(31.5,1.),(31.75,1.04),
                (31.833,.84),(31.958,.84),(32.15,1.09),(32.4,.97),(32.75,1.),(35.0,1.),(35.25,1.025),(35.65,1.)])
    angle=0.
    if t<2.35:angle=1.8*math.sin(t*3.8)*math.sin(math.pi*t/2.35)
    elif t<3.5:angle=curve(t,[(2.35,0.),(2.9,3.),(3.5,3.)])
    elif 12.75<=t<14.25:angle=curve(t,[(12.75,0.),(13.1,-3.),(13.7,-3.),(14.25,0.)])
    elif 17.75<=t<19.:angle=-3.5*math.sin(math.pi*u(t,17.75,19.))
    elif 21.<=t<23.:angle=curve(t,[(21.,0.),(21.65,-3.),(21.95,-4.),(22.45,-4.),(22.75,2.5),(23.,2.5)])
    elif 25.55<=t<28.:angle=curve(t,[(25.55,0.),(25.9,-4.),(26.4,-4.),(27.35,-3.),(28.,0.)])
    elif 31.5<=t<33.25:angle=curve(t,[(31.5,0.),(31.833,6.),(32.4,3.),(33.25,3.)])
    elif t>=33.25:angle=curve(t,[(33.25,3.),(34.7,3.),(35.25,-2.),(37.25,-2.)])
    return {'sx':1./sy,'sy':sy,'rotation':angle,'dx':0.,'dy':0.}


def _face(t,s):
    left=character.point(s['hands']['left'],'tip');right=character.point(s['hands']['right'],'tip')
    pan=(301.,1300.);sink=(102.,1125.);paper=s.get('paper');target=pan;name='happy';forward=0.
    if t<2.35:target=tuple(s.get('gaze_target',pan))
    elif t<3.5:
        target=point(pan,left,u(t,2.7,2.9));name='inspect'
        if t>=3.3:target=point(left,sink,u(t,3.3,3.5))
    elif s['shot']=='sink':name='focus';target=left
    elif t<8.75:
        target=left if t>=7.05 else right;name='relief'if t>=7.05 else'focus'
    elif t<10.5:name='focus';target=(635.,1360.)
    elif t<11.:name='impatient';target=point(left,sink,u(t,10.8,11.))
    elif t<15.:
        name='impatient';target=right
        glance=u(t,13.2,13.33)*(1.-u(t,13.5,13.67));target=point(right,pan,glance)
    elif t<16.25:
        name='focus'if t<15.85 else'inspect';target=(530.,1268.)if t<15.58 else left
        if t>=16.05:target=point(left,sink,u(t,16.05,16.25))
    elif t<19.5:
        name='impatient';glance=u(t,18.13,18.25)*(1.-u(t,18.38,18.50));target=point(right,pan,glance)
    elif t<21.:name='focus';target=tuple(s.get('gaze_target',pan))
    elif t<23.:
        name='resist';target=left
        if 21.25<=t<21.65:target=point(left,pan,u(t,21.25,21.45))
        elif 21.65<=t<22.45:target=point(pan,(468.,1275.),u(t,21.65,21.85))
        elif 22.65<=t:target=point(left,sink,u(t,22.65,22.9))
    elif t<25.2:name='focus';target=right
    elif t<25.55:name='dread';target=right if t<25.40 else(876.,1175.)
    elif t<26.4:
        name='dread'if t<25.95 else'resist';target=point((876.,1175.),(280.,1190.),u(t,25.55,25.7))if t<25.9 else point((280.,1190.),left,u(t,25.9,26.1))
    elif t<27.35:name='resist';target=right
    elif t<31.5:name='relief';target=left
    elif t<33.25:
        target=point(left,pan,u(t,31.5,31.667))
        a=character.face('relief',target);b=character.face('shock',target)
        if t<32.:return character.blend_face(a,b,u(t,31.667,31.833))
        return character.blend_face(b,character.face('lost',target),u(t,32.,32.5))
    elif t<35.75:
        target=point(pan,left,u(t,33.25,33.5))if t<34. else point(left,right,u(t,34.,34.25))
        if t<34.7:return character.blend_face(character.face('lost',target),character.face('notice',target),u(t,33.5,34.15))
        return character.blend_face(character.face('notice',target),character.face('proud',target),u(t,34.7,35.25))
    else:name='proud';target=right;forward=u(t,35.75,36.15)
    f=character.face(name,target,forward)
    if t<2.:
        whistle=0.
        for a,b in ((.300,.700),(.85556,1.25556),(1.41110,1.73110)):
            whistle=max(whistle,u(t,a,a+.06)*(1.-u(t,b-.06,b)))
        f['mouth_open']=mix(f['mouth_open'],.12,whistle)
        f['mouth_width']=mix(f['mouth_width'],14.,whistle)
        f['whistle_amount']=whistle
    if t<2.2 and 1.65<=t<1.65+4./FPS:
        f['blink']=(.45,.08,.08,.50)[min(3,int((t-1.65)*FPS))]
    return f


def scene_state(time):
    real=max(0.,min(DURATION,float(time)));t=min(real,37.25)
    action=cooking_actions.state_at(t)
    s={**action,'production_time':real,'body_time':t,'hands':dict(action.get('hands',rest_hands())),
       'body':_body(t),'shot':'wide','paper':None,'wet_hand':False,'phase':action.get('cooking_phase','cuisiner'),
       'roll':roll_at(t),'production_cycle':None,'water':False,'lever':0.}
    c=next((c for c in CYCLES if c['trigger_start']<=t<c['throw'][1]),None)
    s['production_cycle']=c;s['cycle']=c['id']if c else 0
    if c and c['sink'][0]<=t<c['sink'][1]:
        g=sink_galet.geometry_at(t,c)
        s.update(shot='sink',phase='rincer_bouts_moufle',wet_hand=True,
                 hands={**s['hands'],'left':g['hand']},lever=g['lever'],
                 water=g['water_on'],sink_geometry=g)
    elif c and c['reach'][0]<=t<c['throw'][0]:
        hands,paper,wet,phase=_paper_actions(t,c,s['roll'])
        s.update(hands=hands,paper=paper,wet_hand=wet,phase=phase)
    elif c and c['throw'][0]<=t<c['throw'][1]:
        hands,paper=_throw(t,c);s.update(hands=hands,paper=paper,phase='jeter_papier')
    if c and c['zoom'][0]<=t<c['zoom'][1]:s['shot']='bin'
    if t>=30.25:
        left_amount=u(t,33.5,34.);right_amount=u(t,34.25,34.7)
        left=point((355.,1280.),(430.,1170.),left_amount)
        right=point((810.,1280.),(740.,1165.),right_amount)
        s.update(hands={'left':character.hand('left',left,mix(22.,0.,left_amount),anchor='grip'),
                        'right':character.hand('right',right,mix(-22.,0.,right_amount),anchor='grip')},
                 spoon=None,spoon_held=False,paper=None,wet_hand=False,phase='repas_perdu_mains_impeccables')
    count,flying,floor=_balls(real)
    s.update(bin_count=count,flying_ball=flying,floor_ball=floor,disposed_count=sum(real>=c['land']for c in CYCLES))
    s['face']=_face(t,s)
    s['trace']=None
    for a,b,col in ((2.75,3.5,'#DC9553'),(10.5,11.,'#E6A14C'),(15.85,16.25,'#DA6F59'),(21.,23.,'#FFF8EB')):
        if a<=t<b:s['trace']={'side':'left','color':col,'anchor':character.point(s['hands']['left'],'tip')}
    return s
