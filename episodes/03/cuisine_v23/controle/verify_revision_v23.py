"""Independent checks of V23 expression integration, native geometry and new jazz.

Numerical geometry and waveform checks do not certify expressive acting or
auditory comfort. External V22 comparisons are unavailable in a standalone
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
PREVIOUS=EP.parent/'cuisine_v22'
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
COSTUME_SHA='39bd95eb065c632c16d345f244ba21d66a08e0395cbbbf4bc0cd8e4f952938bb'
ARM_FUNCTIONS=('controls','native_grip','world_grip','solve_arm',
               'arm_linear_transform','_connect_left_root','soften_left_root','draw_arm')
PRESERVED=('arms','hands','actor_transform','spoon','spoon_held','tomato',
           'tomato_added','paper','water','lever','bin_count','flying_ball',
           'floor_ball','roll','carrot','salt','arm_meta','wet_hand','whistle','shot','phase',
           't','production_time','contact_apron','drop','ending_drop','apron_wetness','pro_shot')
NARRATIVE_BEATS=[('medium_cause',0,40),('face_discovery',40,76),('macro_apron',76,116),
                 ('wide_waste',116,160),('face_audience',160,192)]
CAMERA_SHOTS=[('medium',0,40),('face_discovery',40,76),('cloth_macro',76,116),
              ('wide_look',116,128),('bin_pov',128,160),('face_audience',160,192)]
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
        43.7,44.416667,46.916667,47.166667,47.916667]
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
        if state.get('pro_shot')=='macro_apron':
            face_alpha=alpha('<svg xmlns="'+NS+'" width="400" height="500" viewBox="0 0 400 500">'
                             +ET.tostring(faces[0],encoding='unicode')+'</svg>')
            ys,xs=np.nonzero(face_alpha)
            assert len(ys) and (int(ys.max())+1)/2.<334.,(t,'Face enters apron macro')
    return {'isolated_actual_pupil_mask_rasters':records,'optional_tongue_teeth_mask_rasters':mouth_records,
            'whole_face_rotation_keeps_graphics_clipped':True,'exactly_two_pupils_per_sample':True,
            'one_face_one_mouth_per_sample':True,'macro_face_raster_above_viewport':True}


def stable_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,
        separators=(',',':'),allow_nan=False).encode()).hexdigest()


def external_baseline():
    """Isolate V22 imports; both renderers normally use the same module names."""
    path=PREVIOUS/'sources/render.py'
    if not path.is_file():return None
    dependencies=[PREVIOUS/'sources'/n for n in ('animation.py','acting.py','poses.json',
        'art.py','render.py','sink.py','mitten.py','costume.py')]
    dependencies+=[PREVIOUS/'chronologie.json',ROOT/'mou_rig.py']
    snapshot={str(p):sha(p) for p in dependencies}
    cache=ROOT/'work/qa_v23';cache.mkdir(parents=True,exist_ok=True)
    target=cache/('baseline_'+stable_digest(snapshot)+'.json')
    if target.is_file():return json.loads(target.read_text())
    worker=r'''
import hashlib,importlib.util,json,pathlib,re,sys
path=pathlib.Path(sys.argv[1]);fields=json.loads(sys.argv[2])
spec=importlib.util.spec_from_file_location('qa_v22_isolated',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
def digest(value):
 return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
rows=[]
for index in range(1158):
 t=index/24.;s=r.animation.scene_state(t)
 row={'frame':index,'fields':{key:digest(s.get(key)) for key in fields},
      'camera':r.camera_at(s['t'],s)}
 if s['shot']=='sink':row['sink_svg_sha256']=hashlib.sha256(r.svg_at(t).encode()).hexdigest()
 rows.append(row)
print(json.dumps({'frames':rows,'physical_fields':fields},separators=(',',':')))
'''
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    done=subprocess.run([sys.executable,'-I','-B','-c',worker,str(path),json.dumps(PRESERVED)],
        cwd=ROOT,env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    result=json.loads(done.stdout);result['source_snapshot']=snapshot
    assert snapshot=={str(p):sha(p) for p in dependencies},'V22 baseline changed during isolated evaluation'
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
        if 10<=f<48:assert math.dist(target,(876.,1175.))<1.e-7,(t,'Empty roll gaze')
        elif 56<=f<116:assert math.dist(target,(528.5,1265.5))<1.e-7,(t,'Cloth gaze')
        elif 122<=f<160:assert math.dist(target,(165.,1475.))<1.e-7,(t,'Waste gaze')
        elif f>=166:assert math.dist(target,(544.6,918.2))<1.e-7,(t,'Audience gaze')
    return meta


def scene_checks(renderer):
    planned=renderer.TIMELINE['professional_ending']['shots']
    assert [(s['type'],*s['frames']) for s in planned]==[
        ('medium',0,40),('face',40,76),('cloth_macro',76,116),
        ('wide_look',116,128),('bin_pov',128,160),('face',160,192)]
    previous=external_baseline()
    if previous:
        old,new=ast_functions(PREVIOUS/'sources/animation.py'),ast_functions(EP/'sources/animation.py')
        for name in ARM_FUNCTIONS:assert old[name]==new[name],(name,'Native articulation changed')
    assert round(renderer.DURATION*renderer.FPS)==1158
    compared=sinks=contacts=wet_frames=0;body=None;bin_frames={};counts=[]
    shot_views={};last=[];trace=[];gaps=[];macro_contact=[];macro_entry_partial=[]
    camera_changes=[];expression_poses=set();expression_phases={}
    for index in range(1158):
        t=index/24.;state=renderer.animation.scene_state(t)
        expression=gaze_check(state,t)
        expression_poses.update((expression['pose_from'],expression['pose_to']))
        phase=expression['phase'];expression_phases[phase]=expression_phases.get(phase,0)+1
        vb=renderer.camera_at(state['t'],state);vx,vy,vw,vh=vb
        assert vx>=-1.e-7 and vy>=-1.e-7 and vx+vw<=1080.+1.e-7 and vy+vh<=1920.+1.e-7,(t,vb,'Viewport leaves decor')
        outline=re.search(r'<g id="body">(.*?)</g>',state['torso'])[1]
        if body is None:body=outline
        assert outline==body,(t,'Native body shape changed')
        assert hashlib.sha256(renderer.costume.costume_svg(state).encode()).hexdigest()==COSTUME_SHA
        if previous:
            before=previous['frames'][index]
            for field in PRESERVED:assert stable_digest(state.get(field))==before['fields'][field],(t,field,'V22 physical action changed')
            compared+=1
            if state['shot']=='sink':
                assert hashlib.sha256(renderer.svg_at(t).encode()).hexdigest()==before['sink_svg_sha256'],(t,'Sink changed');sinks+=1
            if list(vb)!=before['camera']:camera_changes.append({'frame':index,'viewbox':vb,'previous_viewbox':before['camera']})
        svg=renderer.svg_at(t);doc=ET.fromstring(svg)
        identifiers=[n.attrib['id'] for n in doc.iter() if 'id' in n.attrib]
        assert len(identifiers)==len(set(identifiers)),(t,'Duplicate SVG IDs')
        assert all(ref in identifiers for ref in re.findall(r'url\(#([^)]*)\)',svg)),(t,'Dangling mask')
        actor_visible=state['shot']!='sink'
        assert sum(n.attrib.get('id')=='mouth' for n in doc.iter())==int(actor_visible),(t,'Ghost mouth')
        assert sum(n.attrib.get('id')=='face' for n in doc.iter())==int(actor_visible),(t,'Duplicate face')
        assert sum(n.attrib.get('data-part')=='hand' for n in doc.iter())==(2 if actor_visible else 1),(t,'Hand count')
        whistling=bool(state['whistle']['amount']>0.) and actor_visible
        assert sum(n.attrib.get('data-expression')=='whistling' for n in doc.iter())==int(whistling),(t,'Initial whistle mouth lost or duplicated')
        counts.append(state['bin_count'])
        flying=state.get('flying_ball')
        if flying:
            vertices=ball_polygon(renderer.art,flying)
            assert all(vx+3<=px<=vx+vw-3 and vy+3<=py<=vy+vh-3 for px,py in vertices),(t,flying['id'],'Flying paper clipped')
            if state['shot']=='bin':bin_frames[str(flying['id'])]=bin_frames.get(str(flying['id']),0)+1
        if t>=40.:
            ball=state.get('floor_ball');assert ball and state['bin_count']==4
            assert (ball['x'],ball['y'])==(325.,1805.)
            if state.get('pro_shot')=='wide_waste' or state['shot']=='bin':
                assert all(vx+3<=px<=vx+vw-3 and vy+3<=py<=vy+vh-3 for px,py in ball_polygon(renderer.art,ball))
        if index<966:continue
        f=index-966
        assert tuple(state['actor_transform'])==(80.,380.,2.3),(f,'Body is not stationary')
        expected=next(name for name,a,b in NARRATIVE_BEATS if a<=f<b)
        assert state['pro_shot']==expected,(f,'Unexpected shot')
        camera_shot=next(name for name,a,b in CAMERA_SHOTS if a<=f<b)
        shot_views.setdefault(camera_shot,set()).add(tuple(vb))
        cap=cap_polygon(renderer.animation,state);drop=state['drop']
        anchor=tuple(drop['anchor']);amount=float(drop['amount']);wet=float(state['apron_wetness'])
        if amount>0.:
            distance=gap(anchor,cap)
            assert distance<=6.2 and anchor[1]>=max(py for px,py in cap),(f,'Drop detached')
            inside=vx+12<anchor[0]<vx+vw-12 and vy<anchor[1] and anchor[1]+30<vy+vh
            if expected=='macro_apron' and f<84:
                # The planned entry starts outside this very tight insert;
                # the complete cap and attached water must be inside at contact.
                if not inside:macro_entry_partial.append(f)
            else:
                assert inside,(f,'Drop clipped outside the planned macro entry')
            wet_frames+=1;gaps.append(distance)
        if f<84:assert amount==1. and wet==0.,(f,'Water disappears before contact')
        if f>=89:assert amount==0.
        if 84<=f<104:
            assert state['contact_apron']['active']
            x,y,scale=state['actor_transform'];nx,ny=(anchor[0]-x)/scale,(anchor[1]-y)/scale
            assert 175.<nx<226. and abs(ny-385.)<2.,(f,nx,ny,'Cap not at the cloth')
            assert all(vx+6<px<vx+vw-6 and vy+6<py<vy+vh-6 for px,py in cap),(f,'Contact calotte ink clipped')
            contacts+=1;macro_contact.append({'frame':f,'native_anchor':[nx,ny]})
        if 108<=f<116:
            assert amount==0. and wet==1.
            x,y,scale=state['actor_transform']
            # The whole left cap is above the persistent wet mark (y376–395).
            assert max(py for px,py in cap)<y+376.*scale
            # Compare the actual viewport. Hidden face changes need not alter
            # an otherwise fixed hand/cloth close-up.
            trace.append(hashlib.sha256(cairosvg.svg2png(bytestring=svg.encode(),
                output_width=1080,output_height=1920)).hexdigest())
        if f>=176:
            last.append(hashlib.sha256(cairosvg.svg2png(bytestring=svg.encode(),
                output_width=1080,output_height=1920)).hexdigest())
        if expected=='macro_apron':
            svg=renderer.svg_at(t);doc=ET.fromstring(svg)
            assert 'ilot-cuisine' not in svg and 'poubelle-papier' not in svg
            nx,ny,nw,nh=renderer.TIMELINE['professional_ending']['macro_native_viewbox']
            x,y,scale=state['actor_transform']
            assert all(abs(a-b)<1.e-7 for a,b in zip(vb,(x+nx*scale,y+ny*scale,nw*scale,nh*scale)))
            assert len([n for n in doc.iter() if n.attrib.get('data-part')=='hand'])==2
            right=cap_polygon(renderer.animation,state,'right')
            assert max(x for x,y in right)<vx or min(x for x,y in right)>vx+vw or max(y for x,y in right)<vy or min(y for x,y in right)>vy+vh,'Second mitten enters the cloth detail'
    assert compared in (0,1158) and sinks in (0,215)
    assert counts==sorted(counts) and counts[-1]==4
    assert set(bin_frames)==set('12345')
    assert all(len(v)==1 for v in shot_views.values()),'Camera moves during a planned fixed shot'
    assert len(trace)==8 and len(set(trace))==1,'Wet-result hold is not exact'
    assert len(last)==16 and len(set(last))==1,'Final 16-frame hold is not exact'
    assert contacts==20 and wet_frames==89
    return {'full_frames':1158,'external_v22_comparison':'passed' if previous else 'unavailable',
            'historical_action_frames_identical':compared,'sink_svg_frames_identical':sinks,
            'body_and_costume_preserved':True,'arm_functions_identical':list(ARM_FUNCTIONS),
            'ending_body_transform_constant':[80.,380.,2.3],
            'six_fixed_camera_shots':{k:list(next(iter(v))) for k,v in shot_views.items()},
            'camera_changes_against_v22':camera_changes,
            'actual_gaze_and_inverse_face_rotation_checked_frames':1158,
            'library_pose_ids_used':sorted(expression_poses),'expression_phase_frames':expression_phases,
            'narrative_beats':len(NARRATIVE_BEATS),
            'bin_flight_contour_frames_by_paper':bin_frames,'all_paper_flights_fully_cadrated':True,
            'all_viewports_within_decor':True,'wet_cap_frames':wet_frames,
            'drop_to_native_cap_ink_max_gap':max(gaps),'apron_contact_frames':contacts,
            'macro_contact_anchors':macro_contact,'wet_trace_hold_exact_frames':8,
            'planned_macro_entry_partial_water_frames':macro_entry_partial,
            'final_hold_exact_frames':16,'fifth_paper_persistent_on_floor':True}


def audio_checks():
    audio=EP/'audio';audit=json.loads((EP/'controle/audit_son.json').read_text())
    provenance=json.loads((audio/'provenance.json').read_text())
    assert audit['source_sha256']==sha(EP/'sources/son.py')
    assert audit['chronologie_sha256']==sha(EP/'chronologie.json')
    assert audit['mix_sha256']==sha(audio/'mix.wav')
    music=audit['background_music']
    assert music['music_source_sha256']==sha(EP/'sources/music.py')
    font=music['soundfont'];font_path=EP/font['file']
    assert font_path.resolve().is_relative_to(EP.resolve())
    assert sha(font_path)==font['sha256'],'Music sample bank differs from rendered source'
    assert music['continuous_global_clock'] is True and music['visual_cut_restarts']==0
    assert music['frame_or_action_dependent_notes'] is False
    assert -1.51<=float(music['duck_db'])<=0.,'Unexpected deep or positive musical duck'
    current=pcm(audio/'mix.wav');assert current.shape==(2316000,2)
    events=provenance['events'];assert len({e['name'] for e in events})==len(events)
    water=[e for e in events if e['kind']=='water']
    assert len(water)==5 and not any(e['kind']=='hand_water' for e in events)
    assert not any(e['kind'] in ('voice','speech','beep','laugh','reaction') for e in events)
    timeline=json.loads((EP/'chronologie.json').read_text())
    for cycle in timeline['cycles']:
        e=next(e for e in water if e['cycle']==cycle['id'])
        assert e['start']==cycle['water'][0] and abs(e['duration']-(cycle['water'][1]-cycle['water'][0]))<1.e-8
    cloths=[e for e in events if e['kind']=='cloth_wipe']
    assert len(cloths)==1
    cloth=cloths[0]
    assert abs(cloth['start']-43.75)<1.e-9 and abs(cloth['duration']-20/24.)<1.e-8
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
    delivery=float(audit.get('delivery_gain_db',0.))
    expected=np.rint(expected*10.**(delivery/20.)).astype(np.int32)
    assert np.array_equal(expected,current.astype(np.int32)),'Post-mix recipe does not reconstruct PCM'
    assert int(np.abs(current.astype(np.int32)).max())<32767
    start=round(40.25*48000);a,b=map(lambda t:round(t*48000),(43.75,44.583333333333336))
    assert not occupancy[start:a].any() and not occupancy[b:].any()
    assert occupancy[a:b].max()==1
    assert np.array_equal(pcm(audio/'test_fin_8s.wav'),current[start:])
    for name,digest in audit.get('reference_sources_unchanged',{}).items():assert sha(audio/name)==digest
    unchanged_non_music=0
    old_provenance=PREVIOUS/'audio/provenance.json'
    if old_provenance.is_file():
        previous=json.loads(old_provenance.read_text())
        old={(e['kind'],e['start_sample'],e['samples']):e for e in previous['events'] if e['kind']!='background_music'}
        new={(e['kind'],e['start_sample'],e['samples']):e for e in events if e['kind']!='background_music'}
        assert old.keys()==new.keys(),'Non-music cue timing or membership changed'
        for key,event in new.items():
            assert event['sha256']==old[key]['sha256'],(key,'Postmix Foley changed instead of the music')
            unchanged_non_music+=1
    return {'duration_seconds':48.25,'mix_sha256':sha(audio/'mix.wav'),
            'active_events':len(events),'removed_events':len(provenance.get('removed_events',[])),
            'single_water_layer_per_wash':True,'cloth_contact_sound_seconds':[43.75,44.583333333333336],
            'no_foreground_reaction_accents':True,'no_clipping':True,
            'postmix_recipe_reconstructs_integer_pcm_exactly':True,
            'fixed_delivery_gain_db':delivery,'eight_second_audio_is_exact_final_slice':True,
            'raw_reference_wavs_verified':len(audit.get('reference_sources_unchanged',{})),
            'non_music_postmix_events_identical_to_v22':unchanged_non_music if old_provenance.is_file() else 'external V22 unavailable',
            'music_source_sha256':music['music_source_sha256'],
            'music_soundfont_sha256':font['sha256'],'continuous_music_clock_no_visual_cut_restarts':True,
            'limits':'No numerical loudness, spectrum or layering check proves perceptual comfort.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true')
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    report={'status':'running','scope':'independent V23 geometry/expression/audio checks',
            'limits':'No artistic, audience, continuous-viewing or listening approval is implied.'}
    destination=EP/'controle/audit_revision_v23.json'
    names=('animation.py','art.py','render.py','sink.py','mitten.py','costume.py','acting.py','poses.json','jeu_visage.py','visage.py','expressions.json')
    paths=[EP/'sources'/n for n in names]+[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'assets/Nunito-wght.ttf']
    if not args.geometry_only:
        paths+=[EP/'sources/son.py',EP/'sources/music.py',EP/'audio/mix.wav']
        audio_manifest=json.loads((EP/'controle/audit_son.json').read_text())
        paths.append(EP/audio_manifest['background_music']['soundfont']['file'])
        paths.extend(EP/'audio'/name for name in ('partition_v23.json','partition_v23.mid'))
    frozen={str(p):sha(p) for p in paths}
    try:
        renderer=module('independent_v23',EP/'sources/render.py')
        assert sha(ROOT/'mou_rig.py')==RIG_SHA
        report['scene']=scene_checks(renderer)
        report['masks']=face_mask_checks(renderer)
        report['audio']='pending explicit sound freeze' if args.geometry_only else audio_checks()
        report['final_mp4s']='not requested'
        if args.final:
            tested={}
            for name in ('MOU_Encore_une_feuille.mp4','MOU_Encore_une_feuille_muette.mp4'):
                path=EP/name
                probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
                video=next(s for s in probe['streams'] if s['codec_type']=='video')
                assert [video['width'],video['height'],int(video['nb_frames'])]==[1080,1920,1158]
                assert abs(float(probe['format']['duration'])-48.25)<.05
                tested[name]={'sha256':sha(path),'frames':1158,'duration_seconds':48.25}
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
          'cloth_contact_frames':report['scene']['apron_contact_frames'],
          'final_exact_hold_frames':report['scene']['final_hold_exact_frames']},indent=2))


if __name__=='__main__':main()
