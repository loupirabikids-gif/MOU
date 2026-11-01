"""V25 intentions: attention, fussiness, relief, discovery and caught reaction.

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
    phase='cuisine';gaze_phase='cible_action';blink=1.;face_overrides={}
    values,first,last,weight=_select('joie_leger')
    intention='Le plaisir de cuisiner accompagne le regard vers les objets réellement manipulés.'

    if t<7.:
        relish=(.42*_smooth(_u(t,1.85,2.35))*(1.-_smooth(_u(t,3.8,4.55))))
        values,first,last,weight=_select('joie_leger','joie_franc',relish)
        if state.get('spoon') and state.get('spoon_held'):
            target=tuple(state['spoon']['bowl'])
        phase='cuisine_absorbee';roll=0.
        intention='Se pencher une fois vers le plat avec plaisir, puis revenir au travail, sans balancement mécanique.'
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
            intensity=_smooth(_u(f,4.,8.))
            face_overrides={'eye_open_l':.94+.04*intensity,'eye_open_r':.96+.04*intensity,
                            'brow_raise':.35+.42*intensity,'brow_l':.05+.55*intensity,
                            'brow_r':.05-.25*intensity,'mouth_open':.08*intensity}
        if f>=15.:
            target=_point(hand,(102.,1130.),_smooth(_u(f,15.,17.)));gaze_phase='vers_lavabo'
        phase='premiere_inspection';roll=0.
        intention='Le regard rejoint la moufle avant le doute, puis gagne le lavabo avant la coupe.'
    elif t<35.35:
        cycle=state.get('production_cycle')
        if state['shot']=='sink':
            # This face is outside the insert; the approved sink SVG ignores it.
            values,first,last,weight=_select('doute_leger');phase='lavabo_hors_visage'
        elif cycle and cycle['inspect'][0]<=t<cycle['inspect'][1]:
            level='doute_franc' if cycle['id']>=3 else 'doute_leger'
            values,first,last,weight=_select(level);phase='inspection_repetee'
            face_overrides={'eye_open_l':.94,'eye_open_r':1.,'brow_raise':.55,
                            'brow_l':.40,'brow_r':-.15,'mouth_open':.035}
        elif state['phase']=='decouper_carotte':
            values,first,last,weight=_select('curiosite_leger');phase='precision_carotte'
            intention='L’attention suit la lame et la carotte, sans ponctuer chaque coupe d’une grimace.'
        elif state['phase']=='ajouter_sel':
            values,first,last,weight=_select('joie_leger');phase='assaisonner'
        elif cycle and cycle['paper'][0]<=t<cycle['throw'][1]:
            ordinal=cycle['id'];phase='rituel_papier'
            if ordinal==1:
                values,first,last,weight=_select('doute_leger','soulagement_leger',
                                               _smooth(_u(t,12.25,12.40)))
                if t>=12.40:
                    face_overrides={'eye_open_l':.72,'eye_open_r':.76,'smile':.45,
                                    'mouth_shape':'smile','mouth_open':0.,'mouth_width':24.}
                phase='premier_soulagement'
                intention='La fin du premier essuyage apporte un bref apaisement avant le retour à la cuisine.'
            elif ordinal==2:
                values,first,last,weight=_select('curiosite_leger')
                face_overrides={'mouth_shape':'flat','mouth_width':19.,'mouth_open':0.,
                                'brow_l':-.20,'brow_r':-.15,'eye_open_l':.88,'eye_open_r':.94}
            elif ordinal==3:
                values,first,last,weight=_select('contrariete_leger');phase='contretemps_recurrent'
                face_overrides={'mouth_shape':'flat','mouth_width':24.,'mouth_open':0.,
                                'brow_l':-.28,'brow_r':.08,'eye_open_l':.82,'eye_open_r':.98}
            else:
                values,first,last,weight=_select('contrariete_franc');phase='contretemps_pese'
                face_overrides={'mouth_shape':'flat','mouth_width':27.,'mouth_open':0.,
                                'brow_l':-.42,'brow_r':-.20,'eye_open_l':.79,'eye_open_r':.96}
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
            if f>=7.:face_overrides={'mouth_open':.38,'pupil_scale':.90}
            intention='La petite feuille est montrée et regardée avant que la surprise apparaisse.'
        elif t<38.1:
            values,first,last,weight=_select('surprise_franc','curiosite_leger',_smooth(_u(t,36.8,37.13)))
            if t>=37.13:
                face_overrides={'mouth_shape':'flat','mouth_width':19.,'mouth_open':0.,
                                'brow_l':-.28,'brow_r':-.22,'eye_open_l':.84,'eye_open_r':.92}
            intention='S’appliquer au petit morceau : regard aux moufles et bouche serrée, pas une longue mine triste.'
        else:
            values,first,last,weight=_select('soulagement_leger')
            face_overrides={'eye_open_l':.67,'eye_open_r':.72,'smile':.48,
                            'mouth_shape':'smile','mouth_width':25.,'mouth_open':0.}
            target=tuple(state['hands']['left']);gaze_phase='main_enfin_seche'
            intention='Après l’essuyage achevé, croire le problème résolu ; le spectateur voit la boulette avant lui.'
    else:
        f=float(state['pro_test_frame']);phase='cloture_gaspillage_courte'
        roll=0.;hand=tuple(state['hands']['left']);waste=(165.,1475.)
        if f<8.:
            values,first,last,weight=_select('soulagement_leger')
            face_overrides={'eye_open_l':.67,'eye_open_r':.72,'smile':.48,
                            'mouth_shape':'smile','mouth_width':25.,'mouth_open':0.}
            target=_point(hand,waste,_smooth(_u(f,3.,7.)))
        elif f<14.:
            values,first,last,weight=_select('soulagement_leger','surprise_franc',
                                           _smooth(_u(f,8.,14.)))
            face_overrides={'mouth_open':.4*_smooth(_u(f,8.,14.))}
            target=waste
        elif f<36.:
            values,first,last,weight=_select('surprise_franc')
            face_overrides={'mouth_open':.40,'pupil_scale':.86}
        elif f<49.:
            values,first,last,weight=_select('surprise_franc','gene_franc',
                                           _smooth(_u(f,36.,49.)))
        else:
            values,first,last,weight=_select('gene_franc')
        if f>=49.:
            face_overrides={'mouth_open':.025,'smile':-.30,'mouth_shape':'wince',
                            'mouth_width':24.,'mouth_skew':.42,'eye_open_l':.77,
                            'eye_open_r':.92,'brow_l':.85,'brow_r':.55}
        if f<3.:gaze_phase='main_enfin_seche'
        elif f<8.:gaze_phase='vers_dechets'
        elif f<26.:gaze_phase='dechets_decouverts'
        elif f<35.:gaze_phase='vers_public'
        else:gaze_phase='public'
        intention='Se croire quitte, voir enfin les déchets, se figer avec un recul, puis rejoindre le public avant de refermer sa réaction.'

    if 31.1<=t<32.25:
        phase='impatience_retour_cuisine'
        paper_target=tuple((state['hands']['left'][axis]+state['hands']['right'][axis])/2.
                           for axis in (0,1))
        glance=_smooth(_u(t,31.18,31.30))*(1.-_smooth(_u(t,31.50,31.65)))
        target=_point(paper_target,(293.,1305.),glance)
        gaze_phase='poele_puis_papier'
        before={**values,**face_overrides}
        tension={**before,'eye_open_l':.66,'eye_open_r':.92,'brow_raise':.04,
                 'brow_l':-.72,'brow_r':-.40,'mouth_shape':'grit',
                 'mouth_open':.025,'mouth_width':23.,'mouth_skew':-.22,'smile':-.45}
        strain=_smooth(_u(t,31.10,31.32))*(1.-_smooth(_u(t,32.,32.25)))
        face_overrides=visage.blend_face_params(before,tension,strain)
        intention='Vouloir retourner à la poêle : buste incliné vers elle, coup d’œil cuisine, puis finir le papier avec la bouche serrée.'

    values.update(face_overrides)
    params=dict(state['pose'])
    params.update({key:value for key,value in values.items()
                   if key not in ('arm_hips','arm_clasp','lift_l','lift_r')})
    unposed_target=animation._performance.inverse_world(target,state)
    compensated=_target_for_face(unposed_target,roll,state['actor_transform'])
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
                         'target_before_body_rotation_world':unposed_target,
                         'target_compensated_world':compensated,'face_roll_deg':roll,
                         'performance_face_overrides':face_overrides,
                         'blink_factor':blink,'source_sha256':SOURCE_SHA,
                         'library_pose_count':36}
    return state
