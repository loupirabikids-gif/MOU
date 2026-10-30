"""Contextual library expressions for the unchanged V22 physical actions.

The controller only replaces MOU's face, its gaze and acting annotations.
It does not draw a second character or change any hand, contact or prop.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
_spec=importlib.util.spec_from_file_location('mou_visage_library_v23',HERE/'visage.py')
visage=importlib.util.module_from_spec(_spec)
sys.modules[_spec.name]=visage
_spec.loader.exec_module(visage)
CATALOGUE=json.loads((HERE/'expressions.json').read_text())
POSES={p['id']:p['params'] for p in CATALOGUE['poses']}
POSES['neutre']=CATALOGUE['neutral']['params']
SOURCE_SHA={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
            for name in ('visage.py','expressions.json')}


def _u(t,start,end):return max(0.,min(1.,(t-start)/max(1.e-9,end-start)))


def _smooth(v):return v*v*(3.-2.*v)


def _frame(t,start,fps):
    value=(float(t)-start)*fps;nearest=round(value)
    return float(nearest) if abs(value-nearest)<1.e-8 else value


def _point(a,b,u):return tuple(x+(y-x)*u for x,y in zip(a,b))


def _select(first,second=None,weight=0.):
    if not second or weight<=0.:return dict(POSES[first]),first,first,0.
    if weight>=1.:return dict(POSES[second]),second,second,1.
    return visage.blend_face_params(POSES[first],POSES[second],weight),first,second,float(weight)


def _target_for_face(target,degrees,transform):
    x,y,scale=transform;cx=x+205.*scale;cy=y+250.*scale
    dx,dy=target[0]-cx,target[1]-cy;angle=math.radians(-degrees)
    ca,sa=math.cos(angle),math.sin(angle)
    return cx+ca*dx-sa*dy,cy+sa*dx+ca*dy


def _paper_target(state):
    paper=state.get('paper')
    if paper:
        for key in ('center','end','start'):
            if key in paper:return tuple(paper[key])
    return tuple(state.get('look_target',state['hands']['right']))


def apply(clock,state,animation):
    """Apply one directed face while keeping all physical state fields intact."""
    t=float(clock);fps=float(animation.FPS);target=tuple(state['look_target'])
    roll=float(state.get('face_roll_deg',-2. if 7.<=t<7.75 else 0.))
    phase='cuisine';gaze_phase='cible_action';blink=1.
    values,first,last,weight=_select('joie_leger')
    intention='Le plaisir de cuisiner accompagne le regard vers les objets réellement manipulés.'

    if t<7.:
        if 1.85<=t<6.45:
            values,first,last,weight=_select('joie_leger','joie_franc',_smooth(_u(t,1.85,2.25)))
        elif 6.45<=t<7.:
            values,first,last,weight=_select('joie_franc','joie_leger',_smooth(_u(t,6.45,6.85)))
        phase='plaisir_cuisine'
        # A single blink away from the original whistled notes and the cut.
        f=_frame(t,4.40,fps)
        if 0.<=f<4.:
            blink=(.45,.035,.035,.45)[int(math.floor(f))]
    elif t<7.75:
        f=_frame(t,7.,fps);hand=tuple(state['hands']['left'])
        target=_point((293.,1305.),hand,_smooth(_u(f,0.,3.)))
        if f<4.:
            values,first,last,weight=_select('joie_leger');gaze_phase='vers_main'
        else:
            values,first,last,weight=_select('joie_leger','doute_franc',_smooth(_u(f,4.,7.)))
            gaze_phase='main_observee'
        if f>=15.:
            target=_point(hand,(102.,1130.),_smooth(_u(f,15.,17.)));gaze_phase='vers_lavabo'
        phase='premiere_inspection'
        intention='Le regard rejoint la moufle avant le doute, puis gagne le lavabo avant la coupe.'
    elif t<35.35:
        cycle=state.get('production_cycle')
        if state['shot']=='sink':
            # This face is outside the insert; the approved sink SVG ignores it.
            values,first,last,weight=_select('doute_leger');phase='lavabo_hors_visage'
        elif state['phase']=='decouper_carotte':
            values,first,last,weight=_select('curiosite_leger');phase='precision_carotte'
            intention='L’attention suit la lame et la carotte, sans ponctuer chaque coupe d’une grimace.'
        elif state['phase']=='ajouter_sel':
            values,first,last,weight=_select('joie_leger');phase='assaisonner'
        elif cycle and cycle['inspect'][0]<=t<cycle['inspect'][1]:
            level='doute_franc' if cycle['id']>=3 else 'doute_leger'
            values,first,last,weight=_select(level);phase='inspection_repetee'
        elif cycle and cycle['paper'][0]<=t<cycle['throw'][1]:
            ordinal=cycle['id'];phase='rituel_papier'
            if ordinal==1:
                values,first,last,weight=_select('doute_leger','soulagement_leger',
                                               _smooth(_u(t,11.94,12.25)))
                phase='premier_soulagement'
                intention='La fin du premier essuyage apporte un bref apaisement avant le retour à la cuisine.'
            elif ordinal==2:
                values,first,last,weight=_select('doute_leger')
            elif ordinal==3:
                values,first,last,weight=_select('contrariete_leger');phase='contretemps_recurrent'
            else:
                values,first,last,weight=_select('contrariete_franc');phase='contretemps_pese'
        elif 33.<=t<34.:
            values,first,last,weight=_select('joie_leger','doute_franc',_smooth(_u(t,33.60,33.85)))
            phase='manche_propre'
    elif t<40.25:
        phase='dernier_papier';target=_paper_target(state)
        if t<36.05:
            values,first,last,weight=_select('contrariete_leger','fierte_leger',_smooth(_u(t,35.35,35.55)))
            intention='Le tirage prépare encore l’attente du grand morceau habituel.'
        elif t<36.8:
            f=_frame(t,36.05,fps)
            values,first,last,weight=_select('fierte_leger','surprise_franc',_smooth(_u(f,4.,7.)))
            gaze_phase='petite_feuille_visible_avant_surprise'
            intention='La petite feuille est montrée et regardée avant que la surprise apparaisse.'
        elif t<38.4:
            values,first,last,weight=_select('surprise_franc','contrariete_franc',_smooth(_u(t,36.8,37.13)))
            intention='La surprise cède à un seul constat contrarié, conservé pendant l’essuyage et le froissage.'
        else:
            values,first,last,weight=_select('contrariete_franc')
            target=tuple(state['look_target']);gaze_phase='suite_action_physique'
            intention='La dernière boulette suit son trajet ; aucun sourire ne vient annuler le constat.'
    else:
        f=float(state['pro_test_frame']);phase='cloture_tablier'
        # The established sequence determines every physical action and gaze.
        # We reuse its actual targets rather than the catalogue's generic gaze.
        if f<12.:
            values,first,last,weight=_select('doute_franc')
        elif f<20.:
            values,first,last,weight=_select('doute_franc','contrariete_franc',_smooth(_u(f,12.,20.)))
        elif f<64.:
            values,first,last,weight=_select('contrariete_franc')
        elif f<68.:
            values,first,last,weight=_select('contrariete_franc','curiosite_franc',_smooth(_u(f,64.,68.)))
        elif f<122.:
            values,first,last,weight=_select('curiosite_franc')
        elif f<128.:
            values,first,last,weight=_select('curiosite_franc','tristesse_leger',_smooth(_u(f,122.,128.)))
        elif f<172.:
            values,first,last,weight=_select('tristesse_leger')
        elif f<176.:
            values,first,last,weight=_select('tristesse_leger','gene_franc',_smooth(_u(f,172.,176.)))
        else:
            values,first,last,weight=_select('gene_franc')
        if 48.<=f<52.:
            blink=(.38,.035,.035,.42)[int(math.floor(f-48.))]
        if f<48.:gaze_phase='tube_vide'
        elif f<56.:gaze_phase='vers_tissu'
        elif f<116.:gaze_phase='tissu'
        elif f<160.:gaze_phase='vers_dechets'
        elif f<166.:gaze_phase='vers_public'
        else:gaze_phase='public'
        intention='Tube vide, idée du tablier, geste visible puis constat des déchets et gêne devant le public.'

    params=dict(state['pose'])
    params.update({key:value for key,value in values.items()
                   if key not in ('arm_hips','arm_clasp','lift_l','lift_r')})
    compensated=_target_for_face(target,roll,state['actor_transform'])
    animation.look_at(params,compensated,state['actor_transform'])
    # Explicit gaze wins over generic catalogue directions, including future
    # poses that expose separate eye-direction controls.
    for side in ('l','r'):
        for axis in ('x','y'):
            if 'pupil_'+axis+'_'+side in params:
                params['pupil_'+axis+'_'+side]=params['pupil_'+axis]
        params['eye_open_'+side]*=blink

    fragment=visage.face_fragment(params,'mou-visage-v23')
    if state['whistle']['amount']>0.:
        mouth=visage._mouth({**visage.rig.DEFAULT_POSE,**params},'mou-visage-v23')
        assert fragment.count(mouth)==1
        fragment=fragment.replace(mouth,animation.whistling_mouth_svg(params,state['whistle']['amount']),1)
    marker='<g id="face">';assert fragment.count(marker)==1
    fragment=fragment.replace(marker,f'<g id="face" transform="rotate({roll:.6f} 205 250)">',1)
    position=state['torso'].index('<g id="face"')
    state['torso']=state['torso'][:position]+fragment
    state['pose']=params;state['look_target']=target;state['face_roll_deg']=roll
    state['intention']=intention
    state['expression']={'phase':phase,'pose_from':first,'pose_to':last,'weight':weight,
                         'gaze_phase':gaze_phase,'target_world':target,
                         'target_compensated_world':compensated,'face_roll_deg':roll,
                         'blink_factor':blink,'source_sha256':SOURCE_SHA,
                         'library_pose_count':36}
    return state
