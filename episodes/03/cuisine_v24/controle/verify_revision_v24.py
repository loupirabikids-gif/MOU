"""Independent V24 preservation, short-ending and audio-contract checks.

Numerical geometry and waveform checks do not certify expressive acting or
auditory comfort. External V23 comparisons are unavailable in a standalone
source archive and are reported explicitly.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS=EP.parent/'cuisine_v23'
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
COSTUME_SHA='39bd95eb065c632c16d345f244ba21d66a08e0395cbbbf4bc0cd8e4f952938bb'
ARM_FUNCTIONS=('controls','native_grip','world_grip','solve_arm',
               'arm_linear_transform','_connect_left_root','soften_left_root','draw_arm')
PRESERVED=('arms','hands','actor_transform','spoon','spoon_held','tomato',
           'tomato_added','paper','water','lever','bin_count','flying_ball',
           'floor_ball','roll','carrot','salt','arm_meta','wet_hand','whistle','shot','phase',
           't','production_time','contact_apron','drop','ending_drop','apron_wetness','pro_shot')
NARRATIVE_BEATS=[('medium_cause',0,26),('face_audience',26,66)]
CAMERA_SHOTS=list(NARRATIVE_BEATS)
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(48000,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2)


def numbers(path):
    values=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',path)))
    return list(zip(values[::2],values[1::2]))


def cap_polygon(animation,state,side='left'):
    """Read the cap from the real native hand path, not from state metadata."""
    meta=state['arm_meta'][side]
    native=ET.fromstring(animation._arm(side,meta['hips'],meta['clasp']))
    points=numbers(native[0].attrib['d'])[64:89]
    assert len(points)==25
    sx,sy=animation.SHOULDERS[side]
    aa,ab,ba,bb=animation.arm_linear_transform(meta['rotation'],meta.get('reflect_axis'))
    x,y,scale=state['actor_transform']
    return [(x+scale*(sx+aa*(px-sx)+ab*(py-sy)),
             y+scale*(sy+ba*(px-sx)+bb*(py-sy))) for px,py in points]


def point_edge(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    u=max(0.,min(1.,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)))
    return math.hypot(p[0]-a[0]-u*vx,p[1]-a[1]-u*vy)


def gap(point,polygon):
    return min(point_edge(point,a,polygon[(j+1)%len(polygon)]) for j,a in enumerate(polygon))


def ball_polygon(art,ball):
    group=ET.fromstring(art._ball(ball['x'],ball['y'],ball['r'],ball['rotation'],ball['visual_seed']))
    tx,ty,angle,sx,sy=map(float,re.findall(r'-?\d+(?:\.\d+)?',group.attrib['transform']))
    ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    return [(tx+ca*sx*x-sa*sy*y,ty+sa*sx*x+ca*sy*y) for x,y in numbers(group[0].attrib['d'])]


def ast_functions(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body
            if isinstance(n,ast.FunctionDef)}


def alpha(svg):
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=800,output_height=1000)
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[:,:,3]


def wrap(content,transforms):
    for transform in reversed(transforms):content=f'<g transform="{transform}">{content}</g>'
    return content


def face_mask_checks(renderer):
    """Rasterize actual pupils, optional tongue/teeth at full face transforms."""
    records=[];mouth_records=[];sample_times=[.5,1.2,2.5,6.9,7.125,7.458333,11.7,18.95,
        22.5,27.7,31.4,35.7,36.3,36.75,37.3,40.5,41.916667,42.25,42.916667,
        41.333333,41.708333,42.125,42.375,42.958333]
    for t in sample_times:
        state=renderer.animation.scene_state(t)
        doc=ET.fromstring('<svg xmlns="'+NS+'">'+state['torso']+'</svg>')
        parent={child:node for node in doc.iter() for child in node}
        clips={n.attrib['id']:n for n in doc.iter() if n.tag.endswith('clipPath')}
        faces=[n for n in doc.iter() if n.attrib.get('id')=='face']
        mouths=[n for n in doc.iter() if n.attrib.get('id')=='mouth']
        assert len(faces)==len(mouths)==1,(t,'Duplicated face or mouth')
        pupils=[];optional=[]
        for graphic in faces[0].iter():
            if not graphic.tag.endswith(('ellipse','rect')):continue
            node=parent[graphic];ancestors=[];clip_group=None
            while node is not doc:
                if clip_group is None and 'clip-path' in node.attrib:clip_group=node
                if 'transform' in node.attrib:ancestors.append(node.attrib['transform'])
                node=parent[node]
            if clip_group is None:continue
            identifier=re.fullmatch(r'url\(#([^)]*)\)',clip_group.attrib['clip-path'])[1]
            is_pupil=graphic.tag.endswith('ellipse') and re.search(r'-eye-[lr]$',identifier)
            is_mouth=identifier.endswith('-mouth')
            if not is_pupil and not is_mouth:continue
            clip=clips[identifier];transforms=list(reversed(ancestors))
            definition='<defs>'+ET.tostring(copy.deepcopy(clip),encoding='unicode')+'</defs>'
            content='<g clip-path="url(#'+identifier+')">'+ET.tostring(copy.deepcopy(graphic),encoding='unicode')+'</g>'
            aperture=''.join(ET.tostring(copy.deepcopy(child),encoding='unicode') for child in clip)
            header='<svg xmlns="'+NS+'" width="400" height="500" viewBox="0 0 400 500">'
            painted=alpha(header+definition+wrap(content,transforms)+'</svg>')
            mask=alpha(header+wrap(aperture,transforms)+'</svg>')
            outside=int(np.count_nonzero((mask==0)&(painted>0)))
            assert outside==0,(t,identifier,'Paint outside actual mask')
            row={'time_seconds':t,'mask':identifier,'outside_mask_pixels':outside}
            (pupils if is_pupil else optional).append(row)
        assert len(pupils)==2,(t,'Expected exactly two native clipped pupils')
        records.extend(pupils);mouth_records.extend(optional)
    return {'isolated_actual_pupil_mask_rasters':records,'optional_tongue_teeth_mask_rasters':mouth_records,
            'whole_face_rotation_keeps_graphics_clipped':True,'exactly_two_pupils_per_sample':True,
            'one_face_one_mouth_per_sample':True}


def stable_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        separators=(',',':'),allow_nan=False).encode()).hexdigest()


def external_baseline():
    """Isolate V23 imports and hash every complete state and SVG before40.25s."""
    path=PREVIOUS/'sources/render.py'
    if not path.is_file():return None
    dependencies=[PREVIOUS/'sources'/n for n in ('animation.py','acting.py','poses.json',
        'art.py','render.py','sink.py','mitten.py','costume.py','jeu_visage.py','visage.py','expressions.json')]
    dependencies+=[PREVIOUS/'chronologie.json',ROOT/'mou_rig.py',PREVIOUS/'assets/Nunito-wght.ttf',
                   EP.parent/'decor/MOU_cuisine_decor.svg']
    snapshot={str(p):sha(p) for p in dependencies}
    cache=ROOT/'work/qa_v24';cache.mkdir(parents=True,exist_ok=True)
    target=cache/('baseline_'+stable_digest(snapshot)+'.json')
    if target.is_file():return json.loads(target.read_text())
    worker=r'''
import hashlib,importlib.util,json,pathlib,re,sys
path=pathlib.Path(sys.argv[1]);fields=json.loads(sys.argv[2])
spec=importlib.util.spec_from_file_location('qa_v23_isolated',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
rows=[]
for index in range(966):
 t=index/24.;s=r.animation.scene_state(t);svg=r.svg_at(t)
 row={'frame':index,'state_sha256':digest(s),'svg_sha256':hashlib.sha256(svg.encode()).hexdigest(),
      'fields':{key:digest(s.get(key)) for key in fields},'camera':r.camera_at(s['t'],s),'shot':s['shot']}
 rows.append(row)
print(json.dumps({'frames':rows,'physical_fields':fields},separators=(',',':')))
'''
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    done=subprocess.run([sys.executable,'-I','-B','-c',worker,str(path),json.dumps(PRESERVED)],
        cwd=ROOT,env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    result=json.loads(done.stdout);result['source_snapshot']=snapshot
    assert snapshot=={str(p):sha(p) for p in dependencies},'V23 baseline changed during isolated evaluation'
    temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(result,separators=(',',':')))
    os.replace(temporary,target)
    return result


def gaze_check(state,t):
    """Recompute compensation and pupil direction without calling the controller."""
    meta=state.get('expression');assert isinstance(meta,dict),(t,'Missing expression direction metadata')
    target=tuple(meta['target_world']);assert tuple(state['look_target'])==target
    roll=float(meta['face_roll_deg']);assert float(state['face_roll_deg'])==roll
    x,y,scale=state['actor_transform'];cx,cy=x+205.*scale,y+250.*scale
    dx,dy=target[0]-cx,target[1]-cy;angle=math.radians(-roll)
    ca,sa=math.cos(angle),math.sin(angle)
    expected=(cx+ca*dx-sa*dy,cy+sa*dx+ca*dy)
    assert math.dist(expected,meta['target_compensated_world'])<1.e-7,(t,'Incorrect inverse face rotation')
    px=max(-.92,min(.92,(expected[0]-(x+202.*scale))/310.))
    py=max(-.88,min(.88,(expected[1]-(y+234.*scale))/340.))
    pose=state['pose']
    for axis,value in (('x',px),('y',py)):
        assert abs(pose['pupil_'+axis]-value)<1.e-8,(t,axis,'Pupil not directed at effective target')
        for side in ('l','r'):
            key='pupil_'+axis+'_'+side
            if key in pose:assert abs(pose[key]-value)<1.e-8,(t,key,'Generic eye override defeats actual gaze')
    if 7.<=t<7.75:
        f=round((t-7.)*24.)
        if 3<=f<15:assert math.dist(target,state['hands']['left'])<1.e-7,(t,'Inspection misses actual mitten')
    if 36.05<=t<36.8:
        paper=state.get('paper');assert paper
        actual=next((tuple(paper[k]) for k in ('center','end','start') if k in paper),None)
        assert actual is not None and math.dist(target,actual)<1.e-7,(t,'Reveal gaze misses actual paper')
    if t>=40.25:
        f=round((t-40.25)*24.)
        if f<26:assert math.dist(target,(165.,1475.))<1.e-7,(t,'Waste gaze')
        elif f>=35:assert math.dist(target,(544.6,918.2))<1.e-7,(t,'Audience gaze')
    return meta


def scene_checks(renderer):
    planned=renderer.TIMELINE['professional_ending']['shots']
    assert [(s['type'],*s['frames']) for s in planned]==[
        ('medium_waste',0,26),('face_audience',26,66)]
    assert renderer.TIMELINE['professional_ending']['final_hold_frames']==[51,66]
    previous=external_baseline()
    if previous:
        old,new=ast_functions(PREVIOUS/'sources/animation.py'),ast_functions(EP/'sources/animation.py')
        for name in ARM_FUNCTIONS:assert old[name]==new[name],(name,'Native articulation changed')
    assert renderer.FPS==24 and renderer.DURATION==43. and round(renderer.DURATION*renderer.FPS)==1032
    compared=sinks=0;body=None;bin_frames={};counts=[];shot_views={};last=[]
    tail_unchanged=None;expression_poses=set();expression_phases={}
    tail_physical=('arms','hands','arm_meta','actor_transform','roll','carrot','salt','floor_ball','bin_count')
    for index in range(1032):
        t=index/24.;state=renderer.animation.scene_state(t);svg=renderer.svg_at(t)
        expression=gaze_check(state,t)
        expression_poses.update((expression['pose_from'],expression['pose_to']))
        phase=expression['phase'];expression_phases[phase]=expression_phases.get(phase,0)+1
        vb=renderer.camera_at(state['t'],state);vx,vy,vw,vh=vb
        assert vx>=-1.e-7 and vy>=-1.e-7 and vx+vw<=1080.+1.e-7 and vy+vh<=1920.+1.e-7,(t,vb,'Viewport leaves decor')
        outline=re.search(r'<g id="body">(.*?)</g>',state['torso'])[1]
        if body is None:body=outline
        assert outline==body,(t,'Native body shape changed')
        assert hashlib.sha256(renderer.costume.costume_svg(state).encode()).hexdigest()==COSTUME_SHA
        if previous and index<966:
            before=previous['frames'][index]
            for field in PRESERVED:assert stable_digest(state.get(field))==before['fields'][field],(t,field,'V23 physical action changed')
            assert stable_digest(state)==before['state_sha256'],(t,'Complete V23 state changed before40.25')
            assert sha_svg(svg)==before['svg_sha256'],(t,'V23 SVG changed before40.25')
            assert list(vb)==before['camera'],(t,'V23 camera changed before40.25')
            compared+=1
            if state['shot']=='sink':sinks+=1
        doc=ET.fromstring(svg)
        identifiers=[n.attrib['id'] for n in doc.iter() if 'id' in n.attrib]
        assert len(identifiers)==len(set(identifiers)),(t,'Duplicate SVG IDs')
        assert all(ref in identifiers for ref in re.findall(r'url\(#([^)]*)\)',svg)),(t,'Dangling mask')
        actor_visible=state['shot']!='sink'
        assert sum(n.attrib.get('id')=='mouth' for n in doc.iter())==int(actor_visible),(t,'Ghost mouth')
        assert sum(n.attrib.get('id')=='face' for n in doc.iter())==int(actor_visible),(t,'Duplicate face')
        assert sum(n.attrib.get('data-part')=='hand' for n in doc.iter())==(2 if actor_visible else 1),(t,'Hand count')
        whistling=bool(state['whistle']['amount']>0.) and actor_visible
        assert sum(n.attrib.get('data-expression')=='whistling' for n in doc.iter())==int(whistling),(t,'Initial whistle mouth lost or duplicated')
        counts.append(state['bin_count']);flying=state.get('flying_ball')
        if flying:
            vertices=ball_polygon(renderer.art,flying)
            assert all(vx+3<=px<=vx+vw-3 and vy+3<=py<=vy+vh-3 for px,py in vertices),(t,flying['id'],'Flying paper clipped')
            if state['shot']=='bin':bin_frames[str(flying['id'])]=bin_frames.get(str(flying['id']),0)+1
        if t>=40.:
            ball=state.get('floor_ball');assert ball and state['bin_count']==4
            assert (ball['x'],ball['y'])==(325.,1805.)
            if state.get('pro_shot')=='medium_cause' or state['shot']=='bin':
                assert all(vx+3<=px<=vx+vw-3 and vy+3<=py<=vy+vh-3 for px,py in ball_polygon(renderer.art,ball)),(t,'Waste outside readable shot')
        if index<966:continue
        f=index-966
        assert tuple(state['actor_transform'])==(80.,380.,2.3),(f,'Body is not stationary')
        physical={key:stable_digest(state.get(key)) for key in tail_physical}
        if tail_unchanged is None:tail_unchanged=physical
        assert physical==tail_unchanged,(f,'Tail native arms or props moved')
        expected=next(name for name,a,b in NARRATIVE_BEATS if a<=f<b)
        assert state['pro_shot']==expected,(f,'Unexpected shot')
        shot_views.setdefault(expected,set()).add(tuple(vb))
        assert state.get('paper') is None and state.get('spoon') is None
        assert not state.get('water') and not state.get('wet_hand')
        assert not state.get('contact_apron',{}).get('active') and state.get('apron_wetness',0.)==0.
        assert state.get('drop') is None and state.get('ending_drop') is None
        assert 'tablier-humide' not in svg and 'derniere-goutte' not in svg
        if f>=51:
            last.append(hashlib.sha256(cairosvg.svg2png(bytestring=svg.encode(),
                output_width=1080,output_height=1920)).hexdigest())
    assert compared in (0,966) and sinks in (0,215)
    assert counts==sorted(counts) and counts[-1]==4
    assert set(bin_frames)==set('12345')
    assert all(len(v)==1 for v in shot_views.values()),'Camera moves during a planned fixed shot'
    assert len(last)==15 and len(set(last))==1,'Final 15-frame hold is not exact'
    return {'full_frames':1032,'external_v23_comparison':'passed' if previous else 'unavailable',
            'complete_states_and_svgs_identical_before40_25':compared,'historical_action_frames_identical':compared,
            'sink_svg_frames_identical':sinks,'body_and_costume_preserved':True,
            'arm_functions_identical':list(ARM_FUNCTIONS) if previous else 'external V23 unavailable',
            'ending_body_transform_constant':[80.,380.,2.3],
            'two_fixed_ending_camera_shots':{k:list(next(iter(v))) for k,v in shot_views.items()},
            'tail_arms_hands_and_props_constant':True,'apron_wipe_and_water_removed_from_tail':True,
            'actual_gaze_and_inverse_face_rotation_checked_frames':1032,
            'library_pose_ids_used':sorted(expression_poses),'expression_phase_frames':expression_phases,
            'narrative_beats':len(NARRATIVE_BEATS),'bin_flight_contour_frames_by_paper':bin_frames,
            'all_paper_flights_fully_cadrated':True,'all_viewports_within_decor':True,
            'final_hold_exact_frames':15,'fifth_paper_persistent_on_floor':True}


def sha_svg(svg):return hashlib.sha256(svg.encode()).hexdigest()


def audio_checks(renderer):
    audio=EP/'audio';audit=json.loads((EP/'controle/audit_son.json').read_text())
    provenance=json.loads((audio/'provenance.json').read_text())
    assert audit['source_sha256']==sha(EP/'sources/son.py')
    assert audit['chronologie_sha256']==sha(EP/'chronologie.json')
    assert audit['mix_sha256']==sha(audio/'mix.wav')
    music=audit['background_music']
    assert music['music_source_sha256']==sha(EP/'sources/music.py')
    partition=json.loads((audio/music['partition_json']).read_text())
    font=partition['soundfont'];font_path=EP/font['file']
    assert font_path.resolve().is_relative_to(EP.resolve())
    assert sha(font_path)==font['sha256'],'Music sample bank differs from rendered source'
    assert partition['continuous_global_clock'] is True and partition['visual_cut_restarts']==0
    assert partition['frame_or_action_dependent_notes'] is False
    assert float(partition['bpm'])==108.
    assert music['new_composition'] is False and music['scene_restarts'] is False
    assert music['reduction_db']==-4.
    assert -1.51<=float(partition['duck_db'])<=0.,'Unexpected deep or positive musical duck'
    assert audit['foley_source_sha256']==sha(EP/'sources/foley.py')
    current=pcm(audio/'mix.wav');assert current.shape==(2064000,2)
    events=provenance['events'];assert len(events)==58 and len({e['name'] for e in events})==58
    water=[e for e in events if e['kind']=='water']
    assert len(water)==5 and not any(e['kind']=='hand_water' for e in events)
    assert not any(e['kind'] in ('voice','speech','beep','laugh','reaction','cloth_wipe') for e in events)
    timeline=json.loads((EP/'chronologie.json').read_text())
    for cycle in timeline['cycles']:
        e=next(e for e in water if e['cycle']==cycle['id'])
        assert e['start']==cycle['water'][0] and abs(e['duration']-(cycle['water'][1]-cycle['water'][0]))<1.e-8
    assert not provenance.get('new_voice_or_jingles',False)
    n=len(current);summed=np.zeros(current.shape,dtype=np.int32);occupancy=np.zeros(n,dtype=np.uint8)
    for e in events:
        data=pcm(audio/e['file']);assert sha(audio/e['file'])==e['sha256']
        assert e.get('mix_gain_db',0.)==0.,'Post-mix bank has an extra gain'
        start=int(e['start_sample']);stop=start+len(data)
        assert len(data)==e['samples'] and 0<=start<stop<=n
        assert start==round(e['start']*48000)
        summed[start:stop]+=data.astype(np.int32)
        if e['kind'] not in ('background_music','frying'):occupancy[start:stop]+=1
    env=np.ones(n);attack=round(.008*48000);release=round(.035*48000)
    env[:attack]=np.sin(np.linspace(0.,np.pi/2.,attack))**2
    env[-release:]=np.cos(np.linspace(0.,np.pi/2.,release))**2
    expected=np.rint(summed*env[:,None]).astype(np.int32)
    delivery=float(audit['delivery_gain_db']);assert delivery==3.5,'V24 delivery gain changed'
    expected=np.rint(expected*10.**(delivery/20.)).astype(np.int32)
    assert np.array_equal(expected,current.astype(np.int32)),'Post-mix recipe does not reconstruct PCM'
    assert int(np.abs(current.astype(np.int32)).max())<32767
    assert not occupancy[round(40.25*48000):].any(),'New foreground accents in the closing reaction'
    for name,digest in audit.get('reference_sources_unchanged',{}).items():assert sha(audio/name)==digest
    old_provenance=audio/'reference_v23/provenance.json';assert old_provenance.is_file()
    external_provenance=PREVIOUS/'audio/provenance.json'
    if external_provenance.is_file():assert sha(old_provenance)==sha(external_provenance),'Archived V23 provenance differs'
    previous=json.loads(old_provenance.read_text())
    old={e['name']:e for e in previous['events'] if e['kind']!='background_music' and e['start']<43.}
    assert len(old)==39
    existing={e['name']:e for e in events if e['name'] in old}
    assert existing.keys()==old.keys(),'V23 Foley cue omitted or renamed'
    for name,event in existing.items():
        for key in ('kind','start_sample','samples','sha256'):
            assert event[key]==old[name][key],(name,key,'Existing V23 Foley changed')
    added=[e for e in events if e['name'] not in old and e['kind']!='background_music']
    wipes=[e for e in added if e['kind'] in ('paper_wipe','tiny_paper_wipe')]
    crumples=[e for e in added if e['kind'] in ('paper_crumple','tiny_paper_crumple')]
    lands=[e for e in added if e['kind']=='paper_land']
    assert len(added)==18 and len(wipes)==10 and len(crumples)==5 and len(lands)==3
    contact_records=[]
    for cycle in timeline['cycles']:
        ordinal=cycle['id'];a,b=cycle['wipe']
        pair=[e for e in wipes if e['name'].startswith('c'+str(ordinal)+'_')]
        assert len(pair)==2
        for e in pair:
            assert a<=e['start'] and e['end_seconds']<=b+1/48000.,(e['name'],'Wipe sound outside visible wipe')
            sync=e['sync'];centre=float(sync['centre_seconds'])
            assert sync['target']=='relative_mitten_motion_speed_peak' and sync['action_interval']==cycle['wipe']
            assert abs(centre-(e['start']+.5*e['duration']))<=1/48000.
            # Re-measure the real hand trajectories locally at much finer
            # sampling than the sound author's240-point original study.
            times=np.linspace(centre-1/24.,centre+1/24.,81)
            relative=[]
            for time in times:
                hands=renderer.animation.scene_state(float(time))['hands']
                relative.append(np.asarray(hands['right'])-np.asarray(hands['left']))
            speeds=np.linalg.norm(np.gradient(np.asarray(relative),times,axis=0),axis=1)
            peak=int(np.argmax(speeds));assert 0<peak<len(times)-1
            assert abs(float(times[peak])-centre)<.015,(e['name'],'Sound centre misses relative hand-speed peak')
            assert abs(float(speeds[peak])-float(sync['relative_speed_pixels_per_second']))/float(speeds[peak])<.02,(e['name'],'Declared speed not supported by real hands')

        crush=[e for e in crumples if e['name'].startswith('c'+str(ordinal)+'_')]
        assert len(crush)==1
        c=crush[0];a,b=cycle['crumple']
        assert abs(c['start']-a)<=1/48000. and c['end_seconds']<=b+1/48000.,(c['name'],'Crumple does not match action')
        for e in pair+crush:
            middle=e['start']+.5*e['duration']
            physical=renderer.animation.scene_state(middle)
            assert physical['paper'] is not None and physical['shot']!='sink',(e['name'],'No visible paper contact')
            contact_records.append({'name':e['name'],'start':e['start'],'end':e['end_seconds'],
                                    'visible_paper_mode_at_middle':physical['paper']['mode']})
    for ordinal,when in ((2,21.27),(3,26.77),(4,32.77)):
        cue=next(e for e in lands if e['name'].startswith('c'+str(ordinal)+'_'))
        assert abs(cue['start']-when)<1/48000.
        cycle=next(c for c in timeline['cycles'] if c['id']==ordinal)
        assert when==cycle['land']
        physical=renderer.animation.scene_state(when)
        assert physical['shot']=='bin' and physical['bin_count']>=ordinal,(cue['name'],'No visible bin landing')
        contact_records.append({'name':cue['name'],'start':cue['start'],'visible_cycle_land':cycle['land']})
    tracks=[e for e in events if e['kind']=='background_music'];assert len(tracks)==1
    track=tracks[0];assert track['start_sample']==0 and track['samples']==n
    ref=audio/'reference_v23/musique_v23.wav';assert ref.is_file()
    old_music=next(e for e in previous['events'] if e['kind']=='background_music')
    assert sha(ref)==old_music['sha256'],'V24 music reference differs from V23'
    raw=pcm(ref)[:n].astype(np.float64);fade=np.ones(n);fade_samples=28800
    fade[-fade_samples:]=np.cos(np.linspace(0.,np.pi/2.,fade_samples))**2
    expected_music=np.rint(raw*10.**(-4./20.)*fade[:,None]).astype(np.int32)
    assert np.array_equal(expected_music,pcm(audio/track['file']).astype(np.int32)),'Music is not exactly V23 minus4dB with the planned final fade'
    excerpts={}
    for name,a,b in [('test_fin_8s.wav',35.,43.),('test_fin_v24.wav',40.25,43.)]:
        path=audio/name
        if path.is_file():
            assert np.array_equal(pcm(path),current[round(a*48000):round(b*48000)]),(name,'Excerpt is not the exact claimed final interval')
            excerpts[name]=[a,b]
    assert 'test_fin_v24.wav' in excerpts
    return {'duration_seconds':43.,'mix_sha256':sha(audio/'mix.wav'),
            'active_events':len(events),'single_water_layer_per_wash':True,
            'no_foreground_reaction_accents':True,'no_clipping':True,
            'postmix_recipe_reconstructs_integer_pcm_exactly':True,'fixed_delivery_gain_db':delivery,
            'raw_reference_wavs_verified':len(audit.get('reference_sources_unchanged',{})),
            'non_music_postmix_events_identical_to_v23':len(existing),
            'added_wipe_events':len(wipes),'added_crumple_events':len(crumples),'added_bin_impacts':len(lands),
            'foley_action_intervals_checked':contact_records,'actual_wipe_speed_peaks_independently_checked':10,'exact_final_excerpts':excerpts,
            'music_minus4dB_exact_integer_pcm':True,'music_end_fade_seconds':[42.4,43.],
            'music_source_sha256':music['music_source_sha256'],'music_soundfont_sha256':font['sha256'],
            'continuous_music_clock_no_visual_cut_restarts':True,
            'limits':'No numerical loudness, spectrum or layering check proves perceptual comfort.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true')
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    report={'status':'running','scope':'independent V24 preservation/ending/audio checks',
            'limits':'No artistic, audience, continuous-viewing or listening approval is implied.'}
    destination=EP/'controle/audit_revision_v24.json'
    names=('animation.py','art.py','render.py','sink.py','mitten.py','costume.py','acting.py','poses.json','jeu_visage.py','visage.py','expressions.json')
    paths=[EP/'sources'/n for n in names]+[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'assets/Nunito-wght.ttf']
    if not args.geometry_only:
        paths+=[EP/'sources/son.py',EP/'sources/music.py',EP/'sources/foley.py',EP/'audio/mix.wav']
        audio_manifest=json.loads((EP/'controle/audit_son.json').read_text())
        partition=json.loads((EP/'audio'/audio_manifest['background_music']['partition_json']).read_text())
        paths.append(EP/partition['soundfont']['file'])
        paths.extend(EP/'audio'/name for name in ('partition_v23.json','partition_v23.mid','provenance.json','reference_v23/musique_v23.wav','reference_v23/provenance.json','test_fin_v24.wav'))
        paths.append(EP/'controle/audit_son.json')
        paths.extend(EP/'audio'/e['file'] for e in json.loads((EP/'audio/provenance.json').read_text())['events'])
    frozen={str(p):sha(p) for p in paths}
    try:
        renderer=module('independent_v24',EP/'sources/render.py')
        assert sha(ROOT/'mou_rig.py')==RIG_SHA
        report['scene']=scene_checks(renderer)
        report['masks']=face_mask_checks(renderer)
        report['audio']='pending explicit sound freeze' if args.geometry_only else audio_checks(renderer)
        report['final_mp4s']='not requested'
        if args.final:
            tested={}
            for name in ('MOU_Encore_une_feuille.mp4','MOU_Encore_une_feuille_muette.mp4'):
                path=EP/name
                probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
                video=next(s for s in probe['streams'] if s['codec_type']=='video')
                assert [video['width'],video['height'],int(video['nb_frames'])]==[1080,1920,1032]
                assert abs(float(probe['format']['duration'])-43.)<.05
                assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p' and video['avg_frame_rate']=='24/1'
                sounds=[stream for stream in probe['streams'] if stream['codec_type']=='audio']
                assert len(sounds)==int('_muette' not in name)
                if sounds:assert sounds[0]['codec_name']=='aac' and sounds[0]['sample_rate']=='48000' and sounds[0]['channels']==2
                tested[name]={'sha256':sha(path),'frames':1032,'duration_seconds':43.}
            report['final_mp4s']=tested
        assert frozen=={str(p):sha(p) for p in paths},'Verified production dependencies changed during QA'
        report['source_snapshot']=frozen
        report['status']='geometry_passed_audio_pending' if args.geometry_only else 'passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(destination),
          'historical_frames':report['scene']['historical_action_frames_identical'],
          'bin_flight_frames':report['scene']['bin_flight_contour_frames_by_paper'],
          'final_exact_hold_frames':report['scene']['final_hold_exact_frames']},indent=2))


if __name__=='__main__':main()
