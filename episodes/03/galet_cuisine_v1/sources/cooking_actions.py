"""Kitchen actions made for the selected pebble's independent floating mittens.

Only the cooking actions are directed here. The episode director overrides the
hands for sink, paper and ending shots. All exposed object anchors are computed
from the same poses and artwork that are emitted, without the former MOU rig.
"""
from __future__ import annotations

import math

import art
import character

PAN=(301.,1300.)
LEFT_REST=(270.,1170.)
RIGHT_REST=(925.,1040.)
SPOON_PARK={'grip':(468.,1275.),'bowl':(337.,1308.)}
CARROT_BODY=(635.,1360.)
CARROT_STABILIZER=(747.,1340.)
KNIFE_PARK_GRIP=(548.,1300.)
KNIFE_PARK_TIP=(698.,1300.)
CUT_TIMES=(9.4,9.98)
TOMATO_START=(530.,1268.)
TOMATO_RELEASE=15.38
TOMATO_CONTACT=15.58
SALT_BOWL=(590.,1284.)
SALT_PICK=(590.,1277.)
SALT_ABOVE=(365.,1190.)
SALT_EMISSIONS=tuple(20.1+j*.05 for j in range(11))


def smooth(value):
    value=max(0.,min(1.,float(value)))
    return value*value*(3.-2.*value)


def progress(t,a,b):return smooth((float(t)-a)/max(1.e-9,b-a))


def mix(a,b,v):return a+(b-a)*v


def point(a,b,v):return tuple(mix(x,y,v)for x,y in zip(a,b))


def move(t,a,b,start,end):return point(start,end,progress(t,a,b))


def low_arc(t,a,b,start,end,drop=30.):
    """Purposeful worktop route; its highest point is never above its endpoints."""
    v=progress(t,a,b)
    x,y=point(start,end,v)
    return x,y+drop*math.sin(math.pi*v)


def rest_hands():
    return {'left':character.hand('left',LEFT_REST,rotation=14.),
            'right':character.hand('right',RIGHT_REST,rotation=-14.)}


def _stir_spoon(t):
    if t<2.35:
        # A closed orbit changes the bowl and the holding palm together.
        angle=2.*math.pi*t/1.20
        bowl=(301.+27.*math.cos(angle),1300.+8.*math.sin(angle))
        length=math.dist(SPOON_PARK['grip'],SPOON_PARK['bowl'])
        theta=math.radians(-18.+6.*math.sin(angle))
        grip=(bowl[0]+length*math.cos(theta),bowl[1]+length*math.sin(theta))
        return {'grip':grip,'bowl':bowl}
    if t<2.70:
        source=_stir_spoon(2.35-1.e-8)
        v=progress(t,2.35,2.70)
        return {key:point(source[key],SPOON_PARK[key],v)for key in ('grip','bowl')}
    return dict(SPOON_PARK)


def _knife_from_edge(edge,angle):
    """Place the artwork's actual belly (94,33), preserving its rigid150px blade."""
    theta=math.radians(angle);dx,dy=math.cos(theta),math.sin(theta)
    offset=(94.*dx-33.*dy,94.*dy+33.*dx)
    grip=(edge[0]-offset[0],edge[1]-offset[1])
    return grip,(grip[0]+150.*dx,grip[1]+150.*dy)


def _knife_pose(t):
    park_edge=art.knife_edge_point(KNIFE_PARK_GRIP,KNIFE_PARK_TIP)
    raised1=(655.,1278.);cut1=(655.,1360.)
    raised2=(675.,1278.);cut2=(675.,1360.)
    if t<8.95 or t>=10.4:return KNIFE_PARK_GRIP,KNIFE_PARK_TIP
    if t<9.15:
        v=progress(t,8.95,9.15)
        return _knife_from_edge(point(park_edge,raised1,v),mix(0.,-8.,v))
    if t<9.4:return _knife_from_edge(move(t,9.15,9.4,raised1,cut1),-8.)
    if t<9.46:return _knife_from_edge(cut1,-8.)
    if t<9.66:return _knife_from_edge(move(t,9.46,9.66,cut1,raised1),-8.)
    if t<9.75:return _knife_from_edge(move(t,9.66,9.75,raised1,raised2),-8.)
    if t<9.98:return _knife_from_edge(move(t,9.75,9.98,raised2,cut2),-8.)
    if t<10.035:return _knife_from_edge(cut2,-8.)
    if t<10.14:return _knife_from_edge(move(t,10.035,10.14,cut2,raised2),-8.)
    v=progress(t,10.14,10.4)
    return _knife_from_edge(point(raised2,park_edge,v),mix(-8.,0.,v))


def _knife_hands(t):
    hands=rest_hands();grip,tip=_knife_pose(t)
    if t<8.95:
        target=low_arc(t,8.75,8.95,LEFT_REST,KNIFE_PARK_GRIP,20.)
        hands['left']=character.hand('left',target,rotation=mix(14.,-65.,progress(t,8.75,8.95)),pinch=.75*progress(t,8.75,8.95))
    elif t<10.4:
        hands['left']=character.hand('left',grip,rotation=-65.,pinch=.75)
    else:
        hands['left']=character.hand('left',low_arc(t,10.4,10.68,KNIFE_PARK_GRIP,LEFT_REST,20.),
                                      rotation=mix(-65.,14.,progress(t,10.4,10.68)),
                                      pinch=.75*(1.-progress(t,10.4,10.68)))
    # A true fingertip presses the leafy half, well to the right of both cuts.
    if t<9.12:
        initial=character.point(rest_hands()['right'],'tip')
        target=low_arc(t,8.75,9.12,initial,CARROT_STABILIZER,15.)
        angle=mix(-14.,175.,progress(t,8.75,9.12))
        hands['right']=character.hand('right',target,rotation=angle,pinch=.18,anchor='tip')
    elif t<10.4:
        hands['right']=character.hand('right',CARROT_STABILIZER,rotation=175.,pinch=.18,anchor='tip')
    else:
        final=character.point(rest_hands()['right'],'tip')
        target=low_arc(t,10.4,10.78,CARROT_STABILIZER,final,25.)
        hands['right']=character.hand('right',target,rotation=mix(175.,-14.,progress(t,10.4,10.78)),
                                      pinch=.18*(1.-progress(t,10.4,10.78)),anchor='tip')
    return hands,grip,tip


def _tomato_at(t):
    if t<15.12:return (*TOMATO_START,1.)
    if t<TOMATO_RELEASE:
        v=progress(t,15.12,TOMATO_RELEASE)
        target=point(TOMATO_START,(420.,1165.),v)
        return (*target,1.)
    if t<TOMATO_CONTACT:
        v=(t-TOMATO_RELEASE)/(TOMATO_CONTACT-TOMATO_RELEASE)
        origin=(420.,1165.);control=(320.,1090.)
        xy=tuple((1.-v)**2*origin[k]+2.*(1.-v)*v*control[k]+v*v*PAN[k]for k in (0,1))
        return (*xy,mix(1.,.66,v))
    return None


def _tomato_hand(t):
    if t<15.12:
        start=character.point(rest_hands()['left'],'thumb')
        target=low_arc(t,15.,15.12,start,TOMATO_START,10.)
        return character.hand('left',target,rotation=mix(14.,-35.,progress(t,15.,15.12)),
                              pinch=.85*progress(t,15.,15.12),anchor='thumb')
    if t<TOMATO_RELEASE:
        target=_tomato_at(t)[:2]
        return character.hand('left',target,rotation=-35.,pinch=.85,anchor='thumb')
    if t<16.0:
        final=character.point(rest_hands()['left'],'thumb')
        target=low_arc(t,TOMATO_RELEASE,16.0,(420.,1165.),final,28.)
        return character.hand('left',target,rotation=mix(-35.,14.,progress(t,TOMATO_RELEASE,16.0)),
                              pinch=.85*(1.-progress(t,TOMATO_RELEASE,15.70)),anchor='thumb')
    return rest_hands()['left']


def _salt_hand(t):
    rest=rest_hands()['left']
    if t<19.75:
        start=character.point(rest,'thumb')
        target=low_arc(t,19.5,19.75,start,SALT_PICK,18.)
        return character.hand('left',target,rotation=mix(14.,-40.,progress(t,19.5,19.75)),anchor='thumb')
    if t<19.90:
        return character.hand('left',SALT_PICK,rotation=-40.,pinch=progress(t,19.75,19.90),anchor='thumb')
    if t<20.10:
        v=progress(t,19.90,20.10)
        return character.hand('left',point(SALT_PICK,SALT_ABOVE,v),rotation=mix(-40.,-68.,v),pinch=1.,anchor='thumb')
    if t<20.60:
        v=(t-20.10)/.50
        target=(SALT_ABOVE[0]+4.*math.sin(4.*math.pi*v),SALT_ABOVE[1]-2.*math.sin(2.*math.pi*v))
        amount=1.-.50*math.sin(2.*math.pi*v)**2
        return character.hand('left',target,rotation=-68.,pinch=amount,anchor='thumb')
    if t<21.0:
        finish=character.point(rest,'thumb')
        target=low_arc(t,20.60,21.0,SALT_ABOVE,finish,14.)
        return character.hand('left',target,rotation=mix(-68.,14.,progress(t,20.60,21.0)),
                              pinch=1.-progress(t,20.60,21.0),anchor='thumb')
    if t<21.65:return rest
    approach=(442.,1208.)
    if t<21.95:
        v=progress(t,21.65,21.95)
        return character.hand('left',point(LEFT_REST,approach,v),rotation=mix(14.,-65.,v),pinch=.25*v)
    if t<22.45:return character.hand('left',approach,rotation=-65.,pinch=.25)
    if t<22.85:
        v=progress(t,22.45,22.85)
        return character.hand('left',point(approach,LEFT_REST,v),rotation=mix(-65.,14.,v),pinch=.25*(1.-v))
    return rest


def state_at(time):
    t=max(0.,min(38.,float(time)))
    hands=rest_hands();spoon=_stir_spoon(t)
    grip,tip=_knife_pose(t)
    knife_held=8.95<=t<10.4
    carrot={'body':CARROT_BODY,'cuts':sum(t>=v for v in CUT_TIMES),'visible':True,
            't':t,'cut_times':CUT_TIMES,'knife_grip':grip,'knife_tip':tip,
            'knife_held':knife_held,'knife_hidden':False,
            'knife_edge':art.knife_edge_point(grip,tip),
            'stabilizer_tip':CARROT_STABILIZER if 9.12<=t<10.4 else None}
    gaze=PAN;emotion='happy';phase='repos_cuisine'
    spoon_held=t<2.70
    if t<2.70:
        hands['left']=character.hand('left',spoon['grip'],rotation=-65.,pinch=.70)
        gaze=spoon['bowl'];phase='remuer'if t<2.35 else'poser_cuillere'
    elif t<3.5:
        v=progress(t,2.70,3.05)
        target=low_arc(t,2.70,3.05,SPOON_PARK['grip'],LEFT_REST,15.)
        hands['left']=character.hand('left',target,rotation=mix(-65.,14.,v),pinch=.70*(1.-v))
        gaze=character.point(hands['left'],'tip');emotion='inspect';phase='inspecter_trace_cuillere'
    elif 8.75<=t<11.:
        hands,grip,tip=_knife_hands(t)
        carrot.update(knife_grip=grip,knife_tip=tip,knife_edge=art.knife_edge_point(grip,tip))
        phase='couper_carotte'if t<10.40 else'poser_couteau_et_inspecter'
        gaze=carrot['knife_edge']if t<10.40 else character.point(hands['left'],'tip')
        emotion='focus'if t<10.5 else'impatient'
    elif 15.<=t<16.25:
        hands['left']=_tomato_hand(t);phase='ajouter_tomate'if t<TOMATO_CONTACT else'inspecter_trace_tomate'
        tomato=_tomato_at(t)
        gaze=tomato[:2]if tomato is not None else PAN if t<15.90 else character.point(hands['left'],'thumb')
        emotion='focus'if t<15.90 else'impatient'
    elif 19.5<=t<23.:
        hands['left']=_salt_hand(t)
        phase='pincer_sel'if t<20.10 else'saupoudrer'if t<20.60 else'inspecter_grain'if t<21.65 else'resister_au_lavage'
        gaze=SALT_BOWL if t<19.9 else character.point(hands['left'],'thumb')
        if 21.15<=t<21.65:gaze=PAN
        if 21.65<=t<22.45:gaze=SPOON_PARK['grip']
        emotion='focus'if t<20.6 else'resist'
    tip_salt=character.point(hands['left'],'thumb')
    emissions=[{'time':born,'origin':character.point(_salt_hand(born),'thumb')}
               for born in SALT_EMISSIONS]
    salt={'visible':True,'active':19.5<=t<23.,'bowl':SALT_BOWL,
          'pinch':(19.75,20.),'sprinkle':(20.1,20.6),'target':PAN,
          'fall_duration':.24,'pinch_tip':tip_salt,'hand':tip_salt,
          'grains_on_hand':19.75<=t<23.,'emission_origins':emissions,
          'phase':phase if 19.5<=t<23. else'idle'}
    return {'hands':hands,'spoon':spoon,'spoon_held':spoon_held,
            'carrot':carrot,'tomato':_tomato_at(t),'tomato_added':t>=TOMATO_CONTACT,
            'tomato_held':15.12<=t<TOMATO_RELEASE,'tomato_in_front':15.12<=t<TOMATO_RELEASE,
            'tomato_release':TOMATO_RELEASE,'tomato_contact':TOMATO_CONTACT,
            'salt':salt,'gaze_target':gaze,'emotion_hint':emotion,'cooking_phase':phase,
            'cooking_contacts':{'spoon_grip':spoon['grip']if spoon_held else None,
                                'knife_grip':grip if knife_held else None,
                                'knife_edge':carrot['knife_edge'],
                                'carrot_support':carrot['stabilizer_tip'],
                                'tomato_anchor':_tomato_at(t)[:2]if 15.12<=t<TOMATO_RELEASE else None}}
