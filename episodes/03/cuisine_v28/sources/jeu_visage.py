"""V26 facial acting: a resisted ritual and the false victory of clean hands.

Only the face and gaze are replaced. Body deformation and contacts are supplied
by performance.py; the gaze is inverse-mapped through that same affine.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('mou_face_library_v26', HERE/'visage.py')
visage = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = visage
_spec.loader.exec_module(visage)
CATALOGUE = json.loads((HERE/'expressions.json').read_text())
POSES = {p['id']:p['params'] for p in CATALOGUE['poses']}
POSES['neutre'] = CATALOGUE['neutral']['params']
SOURCE_SHA = {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
              for name in ('visage.py','expressions.json')}


def _adapt(pose_id, **values):
    return {**POSES[pose_id], **values}


FACES = {
    'cook': _adapt('joie_leger', eye_open_l=.91, eye_open_r=.94, smile=.61, mouth_width=25.),
    'precision': _adapt('curiosite_leger', mouth_shape='flat', mouth_width=17., mouth_open=0.,
                        brow_l=-.16, brow_r=-.14, eye_open_l=.90, eye_open_r=.94),
    'inspect': _adapt('doute_franc', eye_open_l=.96, eye_open_r=1., mouth_open=.055,
                     brow_raise=.50, brow_l=.50, brow_r=-.20, mouth_width=21.),
    'dry_focus': _adapt('curiosite_leger', mouth_shape='flat', mouth_width=19., mouth_open=0.,
                       brow_l=-.18, brow_r=-.12, eye_open_l=.87, eye_open_r=.92),
    'relief': _adapt('soulagement_leger', eye_open_l=.71, eye_open_r=.76,
                    smile=.48, mouth_width=25., brow_l=.12, brow_r=.12),
    'impatient': _adapt('contrariete_leger', eye_open_l=.74, eye_open_r=.94,
                       brow_l=-.30, brow_r=.16, mouth_shape='flat', mouth_width=23., mouth_open=0.),
    'more_impatient': _adapt('contrariete_franc', eye_open_l=.63, eye_open_r=.90,
                            brow_raise=.04, brow_l=-.63, brow_r=-.27, mouth_shape='grit',
                            mouth_width=22., mouth_open=.015, mouth_skew=-.14),
    'hesitate': _adapt('doute_franc', eye_open_l=.72, eye_open_r=.97, brow_l=.48,
                      brow_r=-.40, mouth_shape='flat', mouth_width=20., mouth_open=.02),
    'resist': _adapt('contrariete_franc', eye_open_l=.72, eye_open_r=.93,
                    brow_raise=.05, brow_l=-.62, brow_r=-.40, mouth_shape='grit',
                    mouth_width=22., mouth_open=.015, mouth_skew=-.15),
    'cede': _adapt('contrariete_leger', eye_open_l=.78, eye_open_r=.88,
                  brow_l=.36, brow_r=.08, mouth_shape='frown', smile=-.34,
                  mouth_width=20., mouth_open=0.),
    'expect_big': _adapt('fierte_leger', smile=.24, mouth_width=20.),
    'small_sheet': _adapt('surprise_franc', mouth_open=.38, mouth_width=18., pupil_scale=.88),
    'dread': _adapt('doute_franc', eye_open_l=.98, eye_open_r=1., brow_raise=.75,
                   mouth_shape='o', mouth_open=.20, mouth_width=15., pupil_scale=.90),
    'shock': _adapt('surprise_exagere', mouth_open=.86, mouth_width=25., pupil_scale=.74),
    'lost': _adapt('tristesse_leger', eye_open_l=.79, eye_open_r=.87,
                  brow_l=.76, brow_r=.64, mouth_width=24., smile=-.56),
    'hands_notice': _adapt('curiosite_leger', eye_open_l=.92, eye_open_r=.95,
                          brow_l=.18, brow_r=-.10, mouth_shape='flat', mouth_width=18., mouth_open=.015),
    'proud': _adapt('fierte_franc', eye_open_l=.72, eye_open_r=.89, mouth_open=.015,
                   smile=.57, mouth_width=26., mouth_skew=.32, brow_l=-.08, brow_r=-.39),
}


def _u(t, start, end):
    return max(0., min(1., (float(t)-start)/max(1.e-9, end-start)))


def _smooth(value):
    return value*value*(3.-2.*value)


def _mix_point(a, b, amount):
    return tuple(x+(y-x)*amount for x,y in zip(a,b))


def _move_target(t, start, end, a, b):
    return _mix_point(a, b, _smooth(_u(t,start,end)))


def _select(first, last=None, amount=0.):
    if last is None or amount<=0.:
        return dict(FACES[first]), first, first, 0.
    if amount>=1.:
        return dict(FACES[last]), last, last, 1.
    return visage.blend_face_params(FACES[first], FACES[last], amount), first, last, float(amount)


def _paper_target(state):
    paper=state.get('paper')
    if paper:
        if paper.get('center') is not None:
            return tuple(paper['center'])
        if paper.get('start') is not None and paper.get('end') is not None:
            return _mix_point(paper['start'],paper['end'],.5)
    return _mix_point(state['hands']['left'],state['hands']['right'],.5)


def _audience(state, animation):
    x,y,scale=state['actor_transform']
    centre=(x+202.*scale,y+234.*scale)
    return animation._performance.forward_world(centre,state)


def apply(clock, state, animation):
    # Hold the face on the same frame as the final body; only scene smoke moves.
    t=min(float(clock),37.25)
    hand=tuple(state['hands']['left']); right=tuple(state['hands']['right'])
    pan=(293.,1305.); sink=(102.,1130.); spoon=(468.,1275.); smoke=(280.,1190.)
    paper=_paper_target(state)
    target=pan; phase='cuisine'; gaze_phase='poele'; blink=1.
    values,first,last,weight=_select('cook')
    intention='Prendre plaisir à réussir le repas.'

    if t<2.75:
        if state.get('spoon') and state.get('spoon_held'):
            target=tuple(state['spoon']['bowl'])
        phase='cuisine_heureuse'
        if 1.75<=t<1.75+4./24.:
            blink=(.45,.035,.035,.45)[min(3,int((t-1.75)*24.))]
    elif t<3.5:
        target=_move_target(t,2.75,2.875,pan,hand)
        values,first,last,weight=_select('cook','inspect',_smooth(_u(t,2.9166667,3.0833333)))
        if t>=3.3333333:
            target=_move_target(t,3.3333333,3.5,hand,sink)
            gaze_phase='vers_lavabo'
        else:
            gaze_phase='trace_sur_moufle'
        phase='premiere_inspection'
        intention='La trace attire les yeux avant la crispation ; puis le lavabo attire le geste.'
    elif state['shot']=='sink':
        values,first,last,weight=_select('dry_focus')
        target=hand; phase='lavabo_hors_visage'; gaze_phase='main_lavee'
        intention='Les bouts de la moufle sont rincés dans l’insert sans visage.'
    elif t<8.75:
        target=paper if t<7.05 else hand
        values,first,last,weight=_select('dry_focus','relief',_smooth(_u(t,7.05,7.175)))
        phase='premier_rituel_applique' if t<7.05 else 'premiere_petite_victoire'
        gaze_phase='papier_puis_main_propre'
        intention='Le papier est démesuré ; après séchage seulement, croire le problème réglé.'
    elif t<10.5:
        values,first,last,weight=_select('precision')
        target=(635.,1360.); phase='carotte'; gaze_phase='coupe_carotte'
        intention='Deux coupes appliquées ; pas de grimace au moment du contact de la lame.'
    elif t<11.:
        values,first,last,weight=_select('precision','impatient',_smooth(_u(t,10.5,10.70)))
        target=_move_target(t,10.8333333,11.,hand,sink)
        phase='inspection_carotte'; gaze_phase='moufle_puis_lavabo'
        intention='Reconnaître encore le même détour avant de le refaire.'
    elif t<15.:
        values,first,last,weight=_select('impatient')
        glance=_smooth(_u(t,13.20,13.33))*(1.-_smooth(_u(t,13.50,13.67)))
        target=_mix_point(paper,pan,glance)
        phase='deuxieme_rituel_impatient'; gaze_phase='papier_poele_papier'
        intention='Vouloir retourner à la poêle pendant que les mains finissent leur corvée.'
    elif t<16.25:
        values,first,last,weight=_select('precision','impatient',_smooth(_u(t,15.80,16.08)))
        tomato=state.get('tomato')
        target=tuple(tomato) if tomato is not None and t<15.58 else _move_target(t,15.75,16.05,pan,hand)
        if t>=16.0833333:
            target=_move_target(t,16.0833333,16.25,hand,sink)
        phase='tomate_et_inspection'; gaze_phase='tomate_main_lavabo'
        intention='La recette avance à peine ; l’attention est reprise par la moufle.'
    elif t<19.5:
        values,first,last,weight=_select('more_impatient')
        glance=_smooth(_u(t,18.13,18.25))*(1.-_smooth(_u(t,18.38,18.50)))
        target=_mix_point(paper,pan,glance)
        phase='troisieme_rituel_presse'; gaze_phase='papier_retour_poele'
        intention='Sécher presque machinalement, le désir de cuisiner toujours ailleurs.'
    elif t<21.:
        values,first,last,weight=_select('precision')
        target=(365.,1230.) if t<20.60 else hand
        phase='sel'; gaze_phase='sel_puis_grain'
        intention='Assaisonner, puis repérer un grain sans comprendre encore l’état du plat.'
    elif t<23.:
        phase='tentative_de_resister'; gaze_phase='main_poele_cuillere_main_lavabo'
        values,first,last,weight=_select('hesitate','resist',_smooth(_u(t,21.65,21.95)))
        if t<21.25:target=hand
        elif t<21.65:target=_move_target(t,21.25,21.45,hand,pan)
        elif t<22.45:target=_move_target(t,21.65,21.85,pan,spoon)
        elif t<22.65:target=_move_target(t,22.45,22.60,spoon,hand)
        else:target=_move_target(t,22.65,22.90,hand,sink)
        if t>=22.45:
            values,first,last,weight=_select('resist','cede',_smooth(_u(t,22.45,22.75)))
        intention='Essayer de reprendre la cuillère, suspendre le geste, puis céder au détour.'
    elif t<25.2:
        values,first,last,weight=_select('impatient','expect_big',_smooth(_u(t,24.5,24.75)))
        target=right; phase='attendre_encore_une_grande_bande'; gaze_phase='tirer_papier'
        intention='Anticiper la bande habituelle alors que le rouleau est presque vide.'
    elif t<25.55:
        target=paper if t<25.40 else (876.,1175.)
        values,first,last,weight=_select('expect_big','small_sheet',_smooth(_u(t,25.3666667,25.50)))
        phase='dernier_morceau'; gaze_phase='feuille_puis_tube'
        intention='La feuille est visible avant la surprise ; vérifier le tube vide.'
    elif t<26.4:
        if t<25.90:
            target=_move_target(t,25.55,25.70,(876.,1175.),smoke)
            values,first,last,weight=_select('small_sheet','dread',_smooth(_u(t,25.60,25.80)))
            gaze_phase='fumee_vue'
        else:
            target=_move_target(t,25.90,26.10,smoke,hand)
            values,first,last,weight=_select('dread','resist',_smooth(_u(t,25.95,26.15)))
            gaze_phase='choisir_la_main_humide'
        phase='choix_essuyage_avant_repas'
        intention='Voir la première alerte de fumée, puis décider de finir quand même le séchage.'
    elif t<27.35:
        values,first,last,weight=_select('resist')
        target=paper; phase='essuyage_final_nerveux'; gaze_phase='finir_sechage'
        intention='Deux frottements appliqués gagnent encore du temps sur le repas.'
    elif t<31.5:
        values,first,last,weight=_select('resist','relief',_smooth(_u(t,27.35,27.55)))
        target=hand; phase='enfin_sec'; gaze_phase='main_propre'
        intention='Croire avoir terminé ; le spectateur voit le papier et le repas avant lui.'
    elif t<33.25:
        target=_move_target(t,31.5,31.6666667,hand,pan)
        phase='decouverte_repas_rate'; gaze_phase='poele_avant_reaction'
        if t<32.:
            values,first,last,weight=_select('relief','shock',_smooth(_u(t,31.6666667,31.8333333)))
        else:
            values,first,last,weight=_select('shock','lost',_smooth(_u(t,32.,32.5)))
        intention='Le regard constate le repas noir avant la surprise ; la déception a un arrêt de lecture.'
    elif t<35.75:
        phase='fausse_victoire'; gaze_phase='examiner_gauche_puis_droite'
        if t<34.:
            target=_move_target(t,33.25,33.50,pan,hand)
        else:
            target=_move_target(t,34.,34.25,hand,right)
        if t<34.70:
            values,first,last,weight=_select('lost','hands_notice',_smooth(_u(t,33.50,34.15)))
        else:
            values,first,last,weight=_select('hands_notice','proud',_smooth(_u(t,34.70,35.25)))
        intention='Après le repas perdu, examiner les deux moufles ; se découvrir enfin un succès dérisoire.'
    else:
        values,first,last,weight=_select('proud')
        target=_move_target(t,35.75,36.15,right,_audience(state,animation))
        phase='presenter_son_faux_succes'; gaze_phase='public' if t>=36.15 else 'vers_public'
        intention='Présenter les mains impeccables au public en conservant le sourire déjà né, malgré le repas noir.'

    vocal_sync=None
    # Align visible breathing with the measured energy of the existing cues.
    # These are local mouth actions; the soundtrack and surrounding gestures stay fixed.
    if 25.625<=t<25.9166667:
        amount=_smooth(_u(t,25.625,25.6666667))*(1.-_smooth(_u(t,25.875,25.9166667)))
        target_mouth={key:value for key,value in values.items() if not key.startswith('_mouth_')}
        target_mouth.update(mouth_shape='o',mouth_open=.38,mouth_width=18.)
        values=visage.blend_face_params(values,target_mouth,amount)
        vocal_sync={'kind':'inspiration','amount':amount,'audio_rms_peak_s':25.766771,
                    'visual_open_hold_s':[25.6666667,25.875]}
    elif 32.75<=t<33.0833334:
        amount=_smooth(_u(t,32.75,32.8333333))*(1.-_smooth(_u(t,32.8333333,33.0833333)))
        target_mouth={key:value for key,value in values.items() if not key.startswith('_mouth_')}
        target_mouth.update(mouth_shape='o',mouth_open=.10,mouth_width=11.,mouth_skew=0.)
        values=visage.blend_face_params(values,target_mouth,amount)
        vocal_sync={'kind':'expiration','amount':amount,'audio_rms_peak_s':32.809271,
                    'visual_max_s':32.8333333}

    params={key:value for key,value in state['pose'].items() if not key.startswith('_mouth_')}
    params.update({key:value for key,value in values.items()
                   if key not in ('arm_hips','arm_clasp','lift_l','lift_r')})
    # The complete actor affine is inverted before native pupil direction.
    unposed_target=animation._performance.inverse_world(target,state)
    animation.look_at(params,unposed_target,state['actor_transform'])
    for side in ('l','r'):
        for axis in ('x','y'):
            key='pupil_'+axis+'_'+side
            if key in params:params[key]=params['pupil_'+axis]
        params['eye_open_'+side]*=blink

    fragment=visage.face_fragment(params,'mou-visage-v26')
    if state.get('whistle',{}).get('amount',0.)>0.:
        mouth=visage._mouth({**visage.rig.DEFAULT_POSE,**params},'mou-visage-v26')
        assert fragment.count(mouth)==1
        fragment=fragment.replace(mouth,animation.whistling_mouth_svg(params,state['whistle']['amount']),1)
    position=state['torso'].index('<g id="face"')
    state['torso']=state['torso'][:position]+fragment
    state['pose']=params; state['look_target']=target; state['face_roll_deg']=0.
    state['intention']=intention
    state['expression']={
        'phase':phase,'pose_from':first,'pose_to':last,'weight':weight,
        'gaze_phase':gaze_phase,'target_world':target,
        'target_before_body_rotation_world':unposed_target,
        'target_compensated_world':unposed_target,'face_roll_deg':0.,
        'performance_face_overrides':values,'blink_factor':blink,
        'source_sha256':SOURCE_SHA,'library_pose_count':36,
        'final_face_hold':float(clock)>=37.25,
        'vocal_sync':vocal_sync,
    }
    return state
