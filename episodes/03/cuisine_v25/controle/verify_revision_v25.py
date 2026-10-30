"""Independent V25 checks of grounded rigid acting, contacts and soft-bed recipe.

The user authorizes new poses and motion. Historical state identity is therefore
not required. This audit verifies physical constraints, not comic or auditory
quality; the independent critic examines the actual montage separately.
"""
from __future__ import annotations

import argparse
import ast
from collections import deque
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS=EP.parent/'cuisine_v24'
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
COSTUME_SHA='39bd95eb065c632c16d345f244ba21d66a08e0395cbbbf4bc0cd8e4f952938bb'
ARM_FUNCTIONS=('controls','native_grip','world_grip','solve_arm','arm_linear_transform',
               '_connect_left_root','soften_left_root','draw_arm')
NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
PIVOT=(205.,420.)
FPS=24;DURATION=43.;FRAMES=1032;SR=48000


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),
                                    ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def ast_functions(path):
    return {node.name:ast.dump(node,include_attributes=False)
            for node in ast.parse(path.read_text()).body if isinstance(node,ast.FunctionDef)}


def close(actual,expected,tolerance=3.e-5,path=''):
    if isinstance(expected,(int,float)) and not isinstance(expected,bool):
        assert isinstance(actual,(int,float)) and abs(float(actual)-float(expected))<=tolerance,(path,actual,expected)
    elif isinstance(expected,dict):
        assert isinstance(actual,dict) and actual.keys()==expected.keys(),(path,'keys')
        for key,value in expected.items():close(actual[key],value,tolerance,path+'.'+key)
    elif isinstance(expected,(list,tuple)):
        assert isinstance(actual,(list,tuple)) and len(actual)==len(expected),(path,'length')
        for i,(a,b) in enumerate(zip(actual,expected)):close(a,b,tolerance,path+f'[{i}]')
    else:assert actual==expected,(path,actual,expected)


def rotate(point,degrees,pivot):
    angle=math.radians(degrees);ca,sa=math.cos(angle),math.sin(angle)
    x,y=point[0]-pivot[0],point[1]-pivot[1]
    return pivot[0]+ca*x-sa*y,pivot[1]+sa*x+ca*y


def world_rotation(point,transform,degrees):
    ax,ay,scale=transform
    local=((point[0]-ax)/scale,(point[1]-ay)/scale)
    x,y=rotate(local,degrees,PIVOT)
    return ax+scale*x,ay+scale*y


def native_hand(animation,state,side):
    """Recover the actual native endpoint; do not trust meta.hand as geometry."""
    meta=state['arm_meta'][side]
    native=animation.native_grip(side,meta['hips'],meta['clasp'],meta.get('grip_depth',animation.GRIP_DEPTH))
    sx,sy=animation.SHOULDERS[side]
    angle=math.radians(meta['rotation']);ca,sa=math.cos(angle),math.sin(angle)
    x=sx+ca*(native[0]-sx)-sa*(native[1]-sy)
    y=sy+sa*(native[0]-sx)+ca*(native[1]-sy)
    if meta.get('reflect_axis') is not None:
        # Existing reflection is confined to untouched sink inserts.
        phi=math.radians(2.*meta['reflect_axis']);a,b=math.cos(phi),math.sin(phi)
        dx,dy=x-sx,y-sy;x,y=sx+a*dx+b*dy,sy+b*dx-a*dy
    ax,ay,scale=state['actor_transform'];raw=(ax+scale*x,ay+scale*y)
    angle=state.get('performance',{}).get('angle_deg',0.)
    return world_rotation(raw,state['actor_transform'],angle)


def baseline():
    path=PREVIOUS/'sources/render.py'
    if not path.is_file():return None
    dependencies=list((PREVIOUS/'sources').glob('*.py'))+[PREVIOUS/'chronologie.json']
    snapshot={str(p):sha(p) for p in dependencies}
    out=ROOT/'work/qa_v25';out.mkdir(parents=True,exist_ok=True)
    target=out/('baseline_'+stable(snapshot)+'.json')
    if target.is_file():return json.loads(target.read_text())
    worker=r'''
import hashlib,importlib.util,json,pathlib,sys
path=pathlib.Path(sys.argv[1]);spec=importlib.util.spec_from_file_location('v24_baseline',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
fields=('actor_transform','hands','arm_meta','spoon','spoon_held','paper','water','lever',
        'bin_count','flying_ball','floor_ball','roll','carrot','salt','tomato','tomato_added',
        'shot','whistle','rhythm','phase','look_target','t')
rows=[]
for i in range(1032):
 s=r.animation.scene_state(i/24.);row={k:s.get(k) for k in fields}
 if s['shot']=='sink':row['sink_svg_sha256']=hashlib.sha256(r.svg_at(i/24.).encode()).hexdigest()
 rows.append(row)
print(json.dumps({'frames':rows},separators=(',',':')))
'''
    env=os.environ.copy();env.pop('PYTHONPATH',None);env['PYTHONDONTWRITEBYTECODE']='1'
    result=subprocess.run([sys.executable,'-I','-B','-c',worker,str(path)],cwd=ROOT,
                          env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    data=json.loads(result.stdout);data['source_snapshot']=snapshot
    assert snapshot=={str(p):sha(p) for p in dependencies},'V24 changed during baseline extraction'
    temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(data,separators=(',',':')))
    os.replace(temporary,target);return data


def gaze(state,t):
    meta=state['expression'];target=tuple(meta['target_world'])
    close(state['look_target'],target,path=f'{t} actual gaze target')
    transform=state['actor_transform'];ax,ay,scale=transform
    angle=state.get('performance',{}).get('angle_deg',0.)
    body_inverse=world_rotation(target,transform,-angle)
    expected=rotate(body_inverse,-state['face_roll_deg'],(ax+205.*scale,ay+250.*scale))
    close(meta['target_compensated_world'],expected,tolerance=1.e-6,path=f'{t} combined inverse gaze')
    px=max(-.92,min(.92,(expected[0]-(ax+202.*scale))/310.))
    py=max(-.88,min(.88,(expected[1]-(ay+234.*scale))/340.))
    for axis,value in (('x',px),('y',py)):
        assert abs(state['pose']['pupil_'+axis]-value)<1.e-7,(t,axis,'actual pupils miss compensated target')
        for side in ('l','r'):
            key='pupil_'+axis+'_'+side
            if key in state['pose']:assert abs(state['pose'][key]-value)<1.e-7,(t,key)
    return meta


def alpha(svg):
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=800,output_height=1000)
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[:,:,3]


def wrap(content,transforms):
    for transform in reversed(transforms):content=f'<g transform="{transform}">{content}</g>'
    return content


def masks(renderer):
    records=[]
    for t in (.5,2.5,3.5,7.125,7.375,11.9,12.5,22.875,28.9,35.7,36.3,37.3,38.2,40.5,40.875,41.4,41.8,42.5):
        state=renderer.animation.scene_state(t)
        root=ET.fromstring('<svg xmlns="'+NS+'">'+state['torso']+'</svg>')
        parents={c:n for n in root.iter() for c in n}
        clips={n.attrib['id']:n for n in root.iter() if n.tag.endswith('clipPath')}
        pupils=[]
        for node in root.iter():
            if not node.tag.endswith('ellipse'):continue
            ancestor=parents[node];transforms=[];identifier=None
            while ancestor is not root:
                if identifier is None and 'clip-path' in ancestor.attrib:
                    identifier=re.fullmatch(r'url\(#([^)]*)\)',ancestor.attrib['clip-path'])[1]
                if 'transform' in ancestor.attrib:transforms.append(ancestor.attrib['transform'])
                ancestor=parents[ancestor]
            if not identifier or not re.search(r'-eye-[lr]$',identifier):continue
            transforms=list(reversed(transforms))
            if state.get('performance_affine_svg'):transforms.insert(0,state['performance_affine_svg'])
            clip=clips[identifier];header='<svg xmlns="'+NS+'" width="400" height="500" viewBox="0 0 400 500">'
            definition='<defs>'+ET.tostring(copy.deepcopy(clip),encoding='unicode')+'</defs>'
            painted=alpha(header+definition+wrap('<g clip-path="url(#'+identifier+')">'+ET.tostring(node,encoding='unicode')+'</g>',transforms)+'</svg>')
            aperture=''.join(ET.tostring(n,encoding='unicode') for n in clip)
            mask=alpha(header+wrap(aperture,transforms)+'</svg>')
            outside=int(np.count_nonzero((mask==0)&(painted>0)))
            assert outside==0,(t,identifier,'Pupil outside actual transformed aperture')
            pupils.append(identifier);records.append({'time_seconds':t,'eye':identifier,'outside_pixels':outside})
        assert len(pupils)==2,(t,'Pupil count')
    return {'transformed_actual_pupil_rasters':records,'zero_outside_pixels':True}


def connected(mask):
    """A visible gap between a leg and body creates a detached component."""
    remaining=mask.copy();components=[]
    while remaining.any():
        y,x=np.argwhere(remaining)[0];remaining[y,x]=False
        queue=deque([(int(y),int(x))]);size=0
        while queue:
            y,x=queue.popleft();size+=1
            for ny,nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
                if 0<=ny<remaining.shape[0] and 0<=nx<remaining.shape[1] and remaining[ny,nx]:
                    remaining[ny,nx]=False;queue.append((ny,nx))
        components.append(size)
    return sorted(components,reverse=True)


def leg_rasters(renderer,samples):
    records=[]
    for t in samples:
        state=renderer.animation.scene_state(t)
        body=re.search(r'<g id="body">.*?</g>',state['torso'])[0]
        feet=state.get('grounded_feet','')
        if not feet:feet=''.join(re.findall(r'<g id="foot-[lr]">.*?</g>',state['torso']))
        transform=state.get('performance_affine_svg','')
        upper=wrap(body,[transform]) if transform else body
        svg=f'<svg xmlns="{NS}" width="400" height="500" viewBox="0 0 400 500">'+feet+upper+'</svg>'
        rgba=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(),output_width=400,output_height=500))).convert('RGBA'))
        components=connected(rgba[:,:,3]>64)
        assert len([n for n in components if n>8])==1,(t,'Detached body or leg',components)
        records.append({'time_seconds':t,'angle_degrees':state.get('performance',{}).get('angle_deg',0.),
                        'nontrivial_connected_components':1,'painted_pixels':int(np.count_nonzero(rgba[:,:,3]>64))})
    return records


def scene(renderer):
    old=baseline();a=renderer.animation
    assert renderer.DURATION==43. and renderer.FPS==24
    assert sha(ROOT/'mou_rig.py')==RIG_SHA
    if old:
        before,after=ast_functions(PREVIOUS/'sources/animation.py'),ast_functions(EP/'sources/animation.py')
        for name in ARM_FUNCTIONS:assert before[name]==after[name],(name,'Native arm function changed')
    canonical=a.character_fragment({},uid='qa-canonical')
    canonical_body=re.search(r'<g id="body">.*?</g>',canonical)[0]
    canonical_feet=''.join(re.findall(r'<g id="foot-[lr]">.*?</g>',canonical))
    counters={'sink_frames_identical':0,'constrained_hand_targets_checked':0,'actual_endpoint_frames':0,
              'common_body_arm_transforms':0,'grounded_foot_groups':0,'gaze_frames':0}
    angles=[];free_displacements=[];contact_errors=[];last=[];bin_counts=[];expressions={};angle_times=[]
    invariant_props=('paper','carrot','roll','water','lever','bin_count','flying_ball','floor_ball','tomato','tomato_added','whistle')
    for index in range(FRAMES):
        t=index/FPS;state=a.scene_state(t);svg=renderer.svg_at(t);doc=ET.fromstring(svg)
        ids=[n.attrib['id'] for n in doc.iter() if 'id' in n.attrib]
        assert len(ids)==len(set(ids)),(t,'Duplicate SVG ID')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',svg)),(t,'Broken SVG clip reference')
        visible=state['shot']!='sink'
        assert sum(n.attrib.get('id')=='face' for n in doc.iter())==int(visible)
        assert sum(n.attrib.get('id')=='mouth' for n in doc.iter())==int(visible)
        assert sum(n.attrib.get('data-part')=='hand' for n in doc.iter())==(2 if visible else 1)
        for costume in ('apron','chef-hat'):
            assert sum(n.attrib.get('data-costume')==costume for n in doc.iter())==int(visible),(t,costume)
        bin_counts.append(state['bin_count'])
        if state['shot']=='sink':
            if old:assert sha_text(svg)==old['frames'][index]['sink_svg_sha256'];counters['sink_frames_identical']+=1
            continue
        expression=gaze(state,t);counters['gaze_frames']+=1
        expressions[expression['phase']]=expressions.get(expression['phase'],0)+1
        p=state.get('performance');assert p,(t,'Missing performance metadata')
        assert re.search(r'<g id="body">.*?</g>',state['torso'])[0]==canonical_body,(t,'Canonical body outline changed')
        assert sha_text(renderer.costume.costume_svg(state))==COSTUME_SHA,(t,'Approved costume shape changed')
        angle=float(p['angle_deg']);angles.append(angle);angle_times.append((abs(angle),t))
        assert abs(angle)<=4.+1.e-7 and list(p['pivot_native'])==list(PIVOT),(t,'Unexpected upper-body transform')
        values=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',state['performance_affine_svg'])))
        close(values,[angle,*PIVOT],tolerance=1.e-8,path=f'{t} SVG performance')
        groups=[n for n in doc.iter() if n.attrib.get('data-performance') in ('upper-body','native-arms')]
        assert len(groups)==2 and {g.attrib['transform'] for g in groups}=={state['performance_affine_svg']},(t,'Body and arms do not share rigid performance')
        counters['common_body_arm_transforms']+=1
        feet=ET.fromstring('<g>'+state['grounded_feet']+'</g>')
        assert {n.attrib.get('id') for n in feet if 'id'in n.attrib}=={'foot-l','foot-r'}
        assert not any(n.attrib.get('id','').startswith('foot-') for n in ET.fromstring('<g>'+state['torso']+'</g>').iter())
        parent={c:n for n in doc.iter() for c in n}
        for n in doc.iter():
            if n.attrib.get('id') not in ('foot-l','foot-r'):continue
            ancestor=parent[n]
            while ancestor is not doc:
                assert 'data-performance' not in ancestor.attrib,(t,'Foot rotated with upper body')
                ancestor=parent[ancestor]
            counters['grounded_foot_groups']+=1
        assert state['grounded_feet']==canonical_feet,(t,'Foot shape or floor level changed')
        if old:
            baseline_state=old['frames'][index]
            expected_transform=list(baseline_state['actor_transform'])
            removed=(0.,0.)
            if t<6.6:
                removed=(expected_transform[0]-80.,expected_transform[1]-380.)
                expected_transform[:2]=[80.,380.]
            close(state['actor_transform'],expected_transform,path=f'{t} actor staging')
            close(p['removed_rhythm_offset'],removed,path=f'{t} old periodic offset')
            for field in invariant_props:close(state.get(field),baseline_state.get(field),path=f'{t} prop {field}')
            spoon=copy.deepcopy(baseline_state.get('spoon'))
            if spoon and t<6.6:
                for key in ('grip','bowl'):spoon[key]=[spoon[key][0]-removed[0],spoon[key][1]-removed[1]]
            close(state.get('spoon'),spoon,path=f'{t} spoon')
        for side in ('left','right'):
            actual=native_hand(a,state,side)
            close(actual,state['hands'][side],tolerance=1.e-6,path=f'{t} actual {side} endpoint')
            meta=state['arm_meta'][side]
            close(actual,meta['hand'],tolerance=1.e-6,path=f'{t} declared {side} hand')
            assert 0.<=meta['clasp']<=1. and 0.<=meta['hips']<=1.
            counters['actual_endpoint_frames']+=1
            if side in p['constrained_hands']:
                target=p['world_targets_before'][side]
                if old:
                    original=old['frames'][index]['hands'][side]
                    expected=(original[0]-removed[0],original[1]-removed[1])
                    close(target,expected,path=f'{t} preserved {side} world target')
                error=math.dist(actual,target);contact_errors.append(error)
                allowance=old['frames'][index]['arm_meta'][side].get('contact_error',0.)+.031 if old else .05
                assert error<=allowance,(t,side,'Held contact exceeds native baseline',error,allowance)
                close(meta['solver_target'],world_rotation(target,state['actor_transform'],-angle),tolerance=1.e-6,path=f'{t} inverse grip')
                counters['constrained_hand_targets_checked']+=1
            elif old:
                original=old['frames'][index]['hands'][side]
                free_displacements.append(math.dist(actual,original))
        if state.get('spoon_held'):close(state['spoon']['grip'],state['hands']['left'],tolerance=.05,path=f'{t} spoon stays gripped')
        if state['carrot']['knife_held']:close(state['carrot']['knife_grip'],state['hands']['left'],tolerance=.05,path=f'{t} knife stays gripped')
        if index>=FRAMES-15:last.append(sha_text(svg))
    assert len(last)==15 and len(set(last))==1,'Last15 frames are not an exact exposure'
    assert bin_counts==sorted(bin_counts) and bin_counts[-1]==4
    if old:assert counters['sink_frames_identical']==215
    extreme_times=[]
    for _,t in sorted(angle_times,reverse=True):
        if all(abs(t-u)>.4 for u in extreme_times):extreme_times.append(t)
        if len(extreme_times)==6:break
    extreme_times=sorted(set(extreme_times+[2.5,7.375,40.875,41.4,42.5]))
    return {**counters,'full_frames':FRAMES,'external_v24_contact_comparison':'passed' if old else 'unavailable',
            'native_arm_functions_unchanged':list(ARM_FUNCTIONS) if old else 'external V24 unavailable',
            'canonical_rig_unchanged':True,'new_poses_allowed':True,
            'actual_performance_angle_min_max_degrees':[min(angles),max(angles)],
            'maximum_free_hand_displacement_from_v24_pixels':max(free_displacements,default=0.),
            'maximum_native_contact_error_pixels':max(contact_errors,default=0.),
            'final_hold_exact_frames':15,'body_leg_connected_rasters':leg_rasters(renderer,extreme_times),
            'expression_phase_frames':expressions}


def sha_text(text):return hashlib.sha256(text.encode()).hexdigest()


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert(source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2)


def rms(data):return float(np.sqrt(np.mean(np.asarray(data,dtype=np.float64)**2)))


def midi_check(path,expected_notes):
    data=Path(path).read_bytes();assert data[:4]==b'MThd'
    size=struct.unpack('>I',data[4:8])[0]
    kind,tracks,division=struct.unpack('>HHH',data[8:14]);assert kind==1 and division==480
    offset=8+size;tempos=[];notes=[];programs={}
    for track in range(tracks):
        assert data[offset:offset+4]==b'MTrk'
        length=struct.unpack('>I',data[offset+4:offset+8])[0]
        content=data[offset+8:offset+8+length];offset+=8+length
        cursor=0;tick=0;running=None
        def vlq():
            nonlocal cursor
            value=0
            while True:
                byte=content[cursor];cursor+=1;value=(value<<7)|(byte&127)
                if not byte&128:return value
        while cursor<len(content):
            tick+=vlq();status=content[cursor]
            if status&128:cursor+=1
            else:assert running is not None;status=running
            if status==255:
                meta=content[cursor];cursor+=1;n=vlq();payload=content[cursor:cursor+n];cursor+=n
                if meta==81:tempos.append((tick,int.from_bytes(payload,'big')))
            elif status in (240,247):
                n=vlq();cursor+=n
            else:
                running=status;family=status>>4;channel=status&15
                n=1 if family in (12,13) else 2;payload=content[cursor:cursor+n];cursor+=n
                if family==12:programs[channel]=payload[0]
                if family==9 and payload[1]>0:notes.append((track,tick,channel,payload[0],payload[1]))
    assert offset==len(data) and tempos==[(0,555556)],'Unexpected MIDI timing or tempo restart'
    assert len(notes)==expected_notes and {n[2] for n in notes}=={0,1}
    assert programs[0]==32 and programs[1]==0,'Unexpected MIDI program'
    assert all(28<=n[4]<=36 for n in notes)
    return {'format':kind,'tracks':tracks,'ticks_per_quarter':division,
            'tempo_microseconds_per_quarter':555556,'note_on_count':len(notes),
            'active_channels':[0,1],'programs':programs,'percussion_note_events':0}


def sound(renderer):
    directory=EP/'audio';provenance=json.loads((directory/'provenance.json').read_text())
    audit=json.loads((EP/'controle/audit_son.json').read_text())
    assert audit['source_sha256']==sha(EP/'sources/son.py')
    assert audit['chronologie_sha256']==sha(EP/'chronologie.json')
    assert audit['mix_sha256']==sha(directory/'mix.wav')
    partition=json.loads((directory/'partition_v25.json').read_text())
    assert float(partition['bpm'])==108.
    assert set(partition['instruments'])=={'accords','basse'},'Unexpected active music instruments'
    assert partition['melody_line'] is False and partition['drums_or_brushes'] is False
    notes=partition['notes'];assert notes
    assert {note['track'] for note in notes}=={'accords','basse'}
    for note in notes:
        assert 28<=int(note['velocity'])<=36,(note,'Unexpected note velocity')
        attack=.045 if note['track']=='accords' else .035
        assert abs(float(note['additional_attack_seconds'])-attack)<1.e-9
        assert 0.<=float(note['start'])<43. and float(note['duration'])>0.
    font=partition['soundfont'];font_file=EP/font['file']
    assert font_file.resolve().is_relative_to(EP.resolve()) and sha(font_file)==font['sha256']
    midi=midi_check(directory/'partition_v25.mid',len(notes))
    current=pcm(directory/'mix.wav');assert current.shape==(2064000,2)
    events=provenance['events'];assert len({e['name'] for e in events})==len(events)
    reference_path=directory/provenance['raw_source_provenance']
    reference=json.loads(reference_path.read_text())
    if (PREVIOUS/'audio/provenance.json').is_file():
        assert sha(reference_path)==sha(PREVIOUS/'audio/provenance.json'),'Embedded V24 reference differs'
    old_events={e['name']:e for e in reference['events']}
    old_paper={name for name,e in old_events.items()
               if e['kind'].startswith(('paper_','tiny_paper_'))}
    replacements=[e for e in events if e.get('replaces_event')]
    assert len(old_paper)==len(replacements)==31
    assert {e['replaces_event'] for e in replacements}==old_paper,'Paper replacement set incomplete'
    recording_files={};adaptations={}
    for e in replacements:
        old=old_events[e['replaces_event']]
        assert e['original_event_sha256']==old['sha256'] and e['sha256']!=old['sha256']
        path=EP/e['source_recording_file']
        assert path.resolve().is_relative_to(EP.resolve()) and sha(path)==e['source_recording_sha256']
        recording_files[e['source_recording_file']]=e['source_recording_sha256']
        assert not e['processing']['synthesis_or_looping_or_time_stretch']
        assert e['processing']['lowpass_hz'] is None
        adaptations[e['source_id']]={'description':e['source_description'],
                                     'recording_method_verified':e['recording_method_verified'],
                                     'licence':e['source_licence']}
    retained=[e for e in events if not e.get('replaces_event') and e['kind']!='background_music']
    assert len(retained)==26
    for e in retained:
        old=old_events[e['name']]
        for key in ('kind','sha256','start_sample','samples'):assert e[key]==old[key],(e['name'],key,'Retained cue changed')
    rights=EP/'assets/paper_recordings/rights'
    assert 'MIT License' in (rights/'atom_MIT_LICENSE.txt').read_text()
    assert 'Creative Commons 0' in (rights/'Ben_Burnes_Paper_Cutter_CC0.txt').read_text()
    total=np.zeros(current.shape,dtype=np.int32);music=[];water=[];foreground=[]
    for e in events:
        path=directory/e['file'];assert sha(path)==e['sha256'],e['name']
        data=pcm(path).astype(np.int32);start=int(e['start_sample']);stop=start+len(data)
        assert start==round(e['start']*SR) and len(data)==e['samples'] and 0<=start<stop<=len(current)
        assert e.get('mix_gain_db',0.)==0.,(e['name'],'Unexpected second event gain')
        total[start:stop]+=data
        if e['kind']=='background_music':music.append(e)
        elif e['kind']=='water':water.append(e)
        elif e['kind']!='frying':foreground.append(e)
    env=np.ones(len(current));attack=round(.008*SR);release=round(.035*SR)
    env[:attack]=np.sin(np.linspace(0,np.pi/2,attack))**2
    env[-release:]=np.cos(np.linspace(0,np.pi/2,release))**2
    expected=np.rint(total*env[:,None]).astype(np.int32)
    delivery=float(provenance['delivery_gain_db']);assert delivery==3.5
    expected=np.rint(expected*10.**(delivery/20.)).astype(np.int32)
    assert np.array_equal(current.astype(np.int32),expected),'Independent event sum does not reconstruct current PCM'
    assert np.abs(expected).max()<32767
    assert len(music)==1 and len(water)==5
    assert not any(e['kind'] in ('voice','speech','beep','laugh','reaction') for e in events)
    assert all(e['start']+e['duration']<=40.25+1/SR for e in foreground),'New closing reaction punctuation'
    for cycle in renderer.TIMELINE['cycles']:
        matches=[e for e in water if e.get('cycle')==cycle['id'] or e['name'].startswith(f"c{cycle['id']}_")]
        assert len(matches)==1
        close([matches[0]['start'],matches[0]['duration']],[cycle['water'][0],cycle['water'][1]-cycle['water'][0]],tolerance=1/SR)
    track=music[0];assert track['start_sample']==0 and track['samples']==len(current)
    signal=pcm(directory/track['file']);old_path=PREVIOUS/'audio/musique_v24.wav';music_delta=None
    if old_path.is_file():
        old=pcm(old_path)
        body=slice(round(2.*SR),round(40.*SR));music_delta=20.*math.log10(rms(signal[body])/rms(old[body]))
        assert music_delta<=-4.0,('Quiet bed not meaningfully lower than V24',music_delta)
    wipes=[e for e in events if e['kind'] in ('paper_wipe','tiny_paper_wipe')]
    crumples=[e for e in events if e['kind'] in ('paper_crumple','tiny_paper_crumple')]
    lands=[e for e in events if e['kind'] in ('paper_land','tiny_paper_land')]
    assert len(wipes)==10 and len(crumples)==5
    rub_sync=[]
    for cycle in renderer.TIMELINE['cycles']:
        matches=[e for e in wipes if e.get('cycle')==cycle['id'] or e['name'].startswith(f"c{cycle['id']}_")]
        assert len(matches)==2
        for event in matches:
            start=event['start'];stop=start+event['duration'];a,b=cycle['wipe']
            assert a-1/SR<=start<stop<=b+1/SR,(event['name'],'Rub outside visible wipe')
            centre=start+.5*event['duration']
            times=np.linspace(centre-1/24.,centre+1/24.,81)
            points=[]
            for time in times:
                hands=renderer.animation.scene_state(float(time))['hands']
                points.append(np.asarray(hands['right'])-np.asarray(hands['left']))
            speed=np.linalg.norm(np.gradient(points,times,axis=0),axis=1)
            peak=int(np.argmax(speed));assert 0<peak<len(speed)-1,(event['name'],'No local motion-speed peak')
            assert abs(float(times[peak])-centre)<.016,(event['name'],'Rub centre misses actual motion')
            rub_sync.append({'name':event['name'],'centre_seconds':centre,
                             'independent_motion_peak_seconds':float(times[peak]),
                             'independent_peak_speed_pixels_per_second':float(speed[peak])})
        crush=[e for e in crumples if e.get('cycle')==cycle['id'] or e['name'].startswith(f"c{cycle['id']}_")]
        assert len(crush)==1
        assert abs(crush[0]['start']-cycle['crumple'][0])<=1/SR
        assert crush[0]['start']+crush[0]['duration']<=cycle['crumple'][1]+1/SR
    excerpts={}
    for filename,start in (('test_fin_v25.wav',35.),('test_fin_8s.wav',35.)):
        path=directory/filename
        if path.is_file():
            assert np.array_equal(pcm(path),current[round(start*SR):]),(filename,'Excerpt samples differ')
            excerpts[filename]=[start,43.]
    assert excerpts,'Exact eight-second ending WAV missing'
    return {'duration_seconds':43.,'mix_sha256':sha(directory/'mix.wav'),'events':len(events),
            'integer_pcm_reconstruction_exact':True,'fixed_delivery_gain_db':delivery,
            'clipped_samples':0,'single_music_bed':True,'single_water_event_per_wash':True,
            'music_rms_change_db_against_v24_seconds2_to40':music_delta,
            'music_active_tracks':['accords','basse'],'melody_and_brushes_absent_from_score':True,
            'music_note_count':len(notes),'music_note_velocity_min_max':[min(n['velocity'] for n in notes),max(n['velocity'] for n in notes)],
            'per_note_additional_attack_seconds':{'accords':.045,'basse':.035},
            'soundfont_sha256':font['sha256'],'actual_rub_motion_checks':rub_sync,
            'midi_independent_parse':midi,
            'recorded_or_library_paper_replacements':len(replacements),'retained_v24_nonpaper_events_exact':len(retained),
            'source_recording_files_verified':recording_files,'source_material_method_distinctions':adaptations,
            'paper_source_licence_notices_included':True,
            'no_foreground_reaction_accents_after40_25':True,'exact_final_excerpts':excerpts,
            'limits':'An exact mix recipe and lower background RMS do not certify auditory softness or comfort.'}


def final_videos():
    results={};streams=[]
    for filename in ('MOU_Encore_une_feuille.mp4','MOU_Encore_une_feuille_muette.mp4'):
        path=EP/filename
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))
        video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=[s for s in probe['streams'] if s['codec_type']=='audio']
        assert(video['width'],video['height'],video['avg_frame_rate'],int(video['nb_read_frames']))==(1080,1920,'24/1',FRAMES)
        assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p' and abs(float(video['duration'])-43.)<.001
        assert len(audio)==int('_muette' not in filename)
        if audio:assert(audio[0]['codec_name'],audio[0]['sample_rate'],audio[0]['channels'])==('aac','48000',2)
        subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(path),'-f','null','-'],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])
        streams.append(hashlib.sha256(raw).hexdigest())
        results[filename]={'sha256':sha(path),'frames':FRAMES,'duration_seconds':43.,'full_decode_without_errors':True}
    assert streams[0]==streams[1],'Silent and sound video bitstreams differ'
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(EP/'MOU_Encore_une_feuille.mp4'),'-map','0:a:0','-t','43','-c:a','pcm_f32le','-f','f32le','-'])
    decoded=np.frombuffer(raw,'<f4').astype(float);reference=pcm(EP/'audio/mix.wav').astype(float).ravel()/32768.
    assert decoded.shape==reference.shape and np.isfinite(decoded).all() and np.abs(decoded).max()<.999
    correlation=float(np.dot(decoded,reference)/np.sqrt(np.dot(decoded,decoded)*np.dot(reference,reference)))
    assert correlation>.90,'AAC does not correspond to current WAV'
    return {'files':results,'same_compressed_video_bitstream':streams[0],'aac_current_wav_correlation':correlation}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry-only',action='store_true');parser.add_argument('--final',action='store_true')
    args=parser.parse_args();destination=EP/'controle/audit_revision_v25.json'
    report={'status':'running','scope':'independent V25 transformations, contacts and PCM checks',
            'limits':'No artistic, audience, continuous-viewing or listening approval is implied.'}
    names=('animation.py','art.py','render.py','sink.py','mitten.py','costume.py','acting.py','poses.json',
           'jeu_visage.py','visage.py','expressions.json','performance.py')
    paths=[EP/'sources'/n for n in names]+[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'assets/Nunito-wght.ttf']
    if not args.geometry_only:
        paths.extend(EP/'sources'/n for n in ('son.py','music.py','foley.py'))
        paths.extend((EP/'audio/mix.wav',EP/'audio/provenance.json',EP/'controle/audit_son.json'))
        paths.extend(EP/'audio'/n for n in ('partition_v25.json','partition_v25.mid'))
        paths.extend(sorted((EP/'assets').rglob('*.sf2')))
        paths.extend(p for p in (EP/'assets/paper_recordings').rglob('*') if p.is_file())
        paths.extend(EP/'audio'/n for n in ('provenance_reference_v24.json','reference_levels_v23_v24.json','test_fin_v25.wav'))
        provenance=json.loads((EP/'audio/provenance.json').read_text())
        paths.extend(EP/'audio'/e['file'] for e in provenance['events'])
    frozen={str(p):sha(p) for p in paths}
    try:
        renderer=module('independent_v25_renderer',EP/'sources/render.py')
        report['scene']=scene(renderer);report['masks']=masks(renderer)
        report['audio']='pending sound freeze' if args.geometry_only else sound(renderer)
        report['final_mp4s']=final_videos() if args.final else 'not requested'
        assert frozen=={str(p):sha(p) for p in paths},'Production source changed during QA'
        report['source_snapshot']=frozen
        report['status']='geometry_passed_audio_pending' if args.geometry_only else 'passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(destination)},indent=2))


if __name__=='__main__':main()
