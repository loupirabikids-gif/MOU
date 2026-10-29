"""Independent audit of the approved rounded mitten in V14 sink inserts.

Run from the repository root after the V14 sources are frozen. The emitted
SVG supplies the actual outlines and transforms; PNG caches are never read.
This does not establish comic success, perceptive listening or user approval.
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
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
PREVIOUS = EP.parent/'cuisine_v13'
STUDY = EP.parent/'etudes_geste/moufle_pouce/render.py'
NS = '{http://www.w3.org/2000/svg}'
IDENTITY = (1.,0.,0.,1.,0.,0.)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def compose(a,b):
    aa,ab,ac,ad,ae,af=a;ba,bb,bc,bd,be,bf=b
    return (aa*ba+ac*bb,ab*ba+ad*bb,aa*bc+ac*bd,ab*bc+ad*bd,
            aa*be+ac*bf+ae,ab*be+ad*bf+af)


def apply(matrix,p):
    a,b,c,d,e,f=matrix
    return a*p[0]+c*p[1]+e,b*p[0]+d*p[1]+f


def matrix_of(text):
    result=IDENTITY
    for name,raw in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)',text):
        v=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?',raw)]
        if name=='translate':matrix=(1.,0.,0.,1.,v[0],v[1]if len(v)>1 else 0.)
        elif name=='scale':matrix=(v[0],0.,0.,v[1]if len(v)>1 else v[0],0.,0.)
        elif name=='matrix':matrix=tuple(v)
        elif name=='rotate':
            angle=math.radians(v[0]);c,s=math.cos(angle),math.sin(angle)
            matrix=(c,s,-s,c,0.,0.)
            if len(v)==3:
                matrix=compose((1.,0.,0.,1.,v[1],v[2]),compose(matrix,(1.,0.,0.,1.,-v[1],-v[2])))
        else:raise AssertionError(('unsupported transform',name))
        result=compose(result,matrix)
    return result


def records(root):
    output=[]
    def walk(node,parent=IDENTITY):
        matrix=compose(parent,matrix_of(node.attrib.get('transform','')))
        output.append((node,matrix))
        for child in node:walk(child,matrix)
    walk(root)
    return output


def flatten(data):
    """Flatten the emitted path, independently of the production helper."""
    tokens=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?',data)
    current=(0.,0.);start=None;index=0;command=None;points=[]
    while index<len(tokens):
        if tokens[index].isalpha():command=tokens[index];index+=1
        assert command is not None
        kind=command.upper();relative=command.islower()
        if kind=='Z':current=start;command=None;continue
        count={'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6}.get(kind)
        assert count is not None,command
        values=list(map(float,tokens[index:index+count]));index+=count
        def p(x,y):return (x+current[0],y+current[1])if relative else(x,y)
        if kind in('M','L'):
            current=p(*values);points.append(current)
            if kind=='M':start=current;command='l'if relative else'L'
        elif kind=='H':current=((current[0]+values[0])if relative else values[0],current[1]);points.append(current)
        elif kind=='V':current=(current[0],(current[1]+values[0])if relative else values[0]);points.append(current)
        else:
            origin=current;control=[p(*values[j:j+2])for j in range(0,count,2)]
            for j in range(1,25):
                t=j/24.;u=1.-t
                if kind=='Q':
                    a,b=control
                    point=(u*u*origin[0]+2*u*t*a[0]+t*t*b[0],u*u*origin[1]+2*u*t*a[1]+t*t*b[1])
                else:
                    a,b,c=control
                    point=tuple(u**3*origin[k]+3*u*u*t*a[k]+3*u*t*t*b[k]+t**3*c[k]for k in(0,1))
                points.append(point)
            current=control[-1]
    return points


def distance_segment(point,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    u=0. if not den else max(0.,min(1.,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/den))
    return math.dist(point,(a[0]+u*dx,a[1]+u*dy))


def inside(point,polygon):
    x,y=point;result=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result


def shape_mask(element,matrix,viewbox):
    clone=copy.deepcopy(element)
    clone.attrib.pop('transform',None)
    clone.attrib.update(fill='white',stroke='none',opacity='1')
    root=ET.Element(NS+'svg',{'viewBox':' '.join(map(str,viewbox)),'width':'540','height':'960'})
    group=ET.SubElement(root,NS+'g',{'transform':'matrix('+' '.join(map(str,matrix))+')'})
    group.append(clone)
    raw=cairosvg.svg2png(bytestring=ET.tostring(root))
    return np.asarray(Image.open(io.BytesIO(raw)).getchannel('A'))>127


def constants(path):
    wanted={}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name)and target.id in('OPEN','CONTACT'):
                    wanted[target.id]=ast.literal_eval(node.value)
    return wanted


def thumb_tangents(hand,matrix):
    """Measure the two actual upper cubic joins, not pose metadata."""
    data=hand.attrib['d']
    assert set(re.findall(r'[A-Za-z]',data)).issubset({'M','C','Z'}),('unexpected mitten topology',data[:80])
    numbers=list(map(float,re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?',data)))
    assert len(numbers)==44,('mitten cubic count',len(numbers))
    points=[apply(matrix,p)for p in zip(numbers[::2],numbers[1::2])]
    angles=[]
    for j in(3,6):
        a=(points[j][0]-points[j-1][0],points[j][1]-points[j-1][1])
        b=(points[j+1][0]-points[j][0],points[j+1][1]-points[j][1])
        angle=abs(math.degrees(math.atan2(a[0]*b[1]-a[1]*b[0],a[0]*b[0]+a[1]*b[1])))
        assert angle<.01,('upper thumb tangent kink',j,angle)
        angles.append(angle)
    return max(angles)


def native_preserved():
    names=['chronologie.json','sources/animation.py','sources/art.py','sources/son.py']
    same={}
    for name in names:
        assert (EP/name).read_bytes()==(PREVIOUS/name).read_bytes(),('unchanged dependency',name)
        same[name]=digest(EP/name)
    previous_audio={p.relative_to(PREVIOUS/'audio'):digest(p)for p in(PREVIOUS/'audio').rglob('*')if p.is_file()}
    current_audio={p.relative_to(EP/'audio'):digest(p)for p in(EP/'audio').rglob('*')if p.is_file()}
    assert previous_audio==current_audio,'audio changed beyond approved hand integration'
    return {'identical_sources':same,'audio_files_byte_identical':len(current_audio),
            'mix_sha256':current_audio[Path('mix.wav')]}


def inspect_sink(renderer,t):
    state=renderer.animation.scene_state(t);svg=renderer.svg_at(t);tree=ET.fromstring(svg)
    rec=records(tree);hands=[(e,m)for e,m in rec if e.attrib.get('data-part')=='hand']
    assert len(hands)==1,('visible sink hand count',t,len(hands))
    hand,matrix=hands[0]
    assert 'd'in hand.attrib,('hand must expose the actual drawn contour',t)
    polygon=[apply(matrix,p)for p in flatten(hand.attrib['d'])]
    geometry=renderer.sink.geometry_at(t,state,renderer.animation)
    result={'time':t,'phase':geometry['phase'],'cycle':geometry['cycle']}
    if geometry['phase']in('open_tap','close_tap'):
        group=next(e for e,m in rec if e.attrib.get('id')=='commande-robinet')
        lever=next(e for e in reversed(list(group))if e.tag==NS+'path'and'L'in e.attrib['d'])
        lever_matrix=next(m for e,m in rec if e is lever)
        tip=apply(lever_matrix,flatten(lever.attrib['d'])[-1])
        boundary_distance=min(distance_segment(tip,a,b)for a,b in zip(polygon,polygon[1:]+polygon[:1]))
        overlap=inside(tip,polygon)
        stroke=float(hand.attrib.get('stroke-width','0'))
        lever_stroke=float(lever.attrib.get('stroke-width','0'))
        assert overlap or boundary_distance<=(stroke+lever_stroke)/2.+.5,('drawn hand misses lever',t,boundary_distance)
        result.update(actual_lever_endpoint=list(tip),lever_inside_hand_fill=overlap,
                      lever_to_hand_boundary_distance=boundary_distance)
    if geometry['phase']=='rinse_tip':
        jet,m=next((e,m)for e,m in rec if e.attrib.get('id')=='lavabo-jet-primary')
        viewbox=tuple(map(float,tree.attrib['viewBox'].split()))
        wet=shape_mask(hand,matrix,viewbox)&shape_mask(jet,m,viewbox)
        ys,xs=np.nonzero(wet)
        assert len(xs)>0,('no actual water/hand contact',t)
        vx,vy,vw,vh=viewbox
        x=vx+(xs+.5)*vw/540.;y=vy+(ys+.5)*vh/960.
        minimum=min(p[0]for p in polygon);maximum=max(p[0]for p in polygon)
        fraction=float((x.max()-minimum)/(maximum-minimum))
        assert fraction<.40,('water overlaps beyond distal portion',t,fraction)
        wx,wy=geometry['wrist']
        wrist_distance=float(np.sqrt((x-wx)**2+(y-wy)**2).min())
        assert wrist_distance>12.,('water reaches wrist',t,wrist_distance)
        clip=next(e for e,m in rec if e.attrib.get('id')=='lavabo-main-contour')
        assert next(iter(clip)).attrib['d']==hand.attrib['d'],('wet tint clip differs from actual mitten',t)
        forearm_clip=next(e for e,m in rec if e.attrib.get('id')=='lavabo-avant-bras-conserve')
        clip_x=float(next(iter(forearm_clip)).attrib['x'])
        assert clip_x>float(x.max())+30.,('forearm enters wet distal area',t,clip_x,float(x.max()))
        result.update(wet_pixels=int(len(xs)),wet_bounds=[float(x.min()),float(y.min()),float(x.max()),float(y.max())],
                      wet_distal_extent_fraction=fraction,dry_wrist_min_distance=wrist_distance,
                      wet_tint_clip_is_drawn_mitten=True,dry_forearm_clip_x=clip_x,
                      actual_rub_cycles=geometry['rub_cycles'])
    return result


def decoded_proofs(renderer,video):
    indices=[]
    for cycle in renderer.TIMELINE['cycles']:
        a,b=cycle['wash'];indices.extend(round((a+(b-a)*q)*24)for q in(.20,.50,.80))
    indices=sorted(set(indices));destination=EP/'controle/preuves_audit_v14';destination.mkdir(exist_ok=True)
    select='select='+'+'.join(f'eq(n\\,{i})'for i in indices)
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vf',select,
        '-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    frames=np.frombuffer(raw,np.uint8).reshape(len(indices),1920,1080,3)
    output=[]
    for index,actual in zip(indices,frames):
        svg=renderer.svg_at(index/24)
        fresh=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('RGB'))
        error=float(np.abs(actual.astype(np.int16)-fresh.astype(np.int16)).mean())
        assert error<3.,('actual film differs from fresh SVG',index,error)
        target=destination/f'final_{index:04d}.png';Image.fromarray(actual).save(target)
        output.append({'frame':index,'time':index/24,'mean_rgb_error':error,'proof':str(target.relative_to(EP))})
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true',help='also decode the delivered full MP4')
    args=parser.parse_args()
    path=EP/'controle/audit_pouce_v14.json'
    report={'status':'in_progress','scope':'V14 integration of approved rounded mitten in sink shots only',
        'limits':'Emitted geometry, preservation and actual-film samples; separate visual critique, no listening or audience validation.'}
    try:
        tracked=[EP/'chronologie.json']+list((EP/'sources').glob('*.py'))
        frozen={str(p.relative_to(ROOT)):digest(p)for p in tracked}
        report['preservation']=native_preserved()
        baseline=load(PREVIOUS/'sources/render.py','audit_pouce_v13_renderer')
        renderer=load(EP/'sources/render.py','audit_pouce_v14_renderer')
        assert constants(EP/'sources/mitten.py')==constants(STUDY),'rounded poses differ from the validated study'
        report['approved_pose_constants_exact']=True
        wide=sink=0;thumb_angles=[]
        for index in range(984):
            t=index/24.;state=renderer.animation.scene_state(t);svg=renderer.svg_at(t)
            tree=ET.fromstring(svg);ids=[e.attrib['id']for e in tree.iter()if'id'in e.attrib]
            assert len(ids)==len(set(ids)),('duplicate SVG IDs',t)
            assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',svg)),('missing SVG reference',t)
            hands=sum(e.attrib.get('data-part')=='hand'for e in tree.iter())
            if state['shot']=='sink':
                sink+=1;assert hands==1,('sink hand count',t)
                assert 'mouth'not in ids and'mou-corps'not in ids,('body in sink shot',t)
                hand,matrix=next((e,m)for e,m in records(tree)if e.attrib.get('data-part')=='hand')
                thumb_angles.append(thumb_tangents(hand,matrix))
            else:
                wide+=1;assert hands==2,('wide hand count',t)
                assert svg==baseline.svg_at(t),('wide image changed',t)
        report['all_frames']={'total':984,'wide_svg_byte_identical':wide,'sink_single_hand':sink,
                              'unique_svg_ids_and_refs':True,
                              'max_actual_upper_thumb_tangent_angle_degrees':max(thumb_angles)}
        checks=[]
        for cycle in renderer.TIMELINE['cycles']:
            a,b=cycle['wash']
            checks.extend(inspect_sink(renderer,a+(b-a)*q)for q in(.20,.50,.80))
            # Tap phases are measured on real emitted outlines; phase starts
            # are located by sampling the bounded existing open/close windows.
            for name,phase in(('open','open_tap'),('close','close_tap')):
                a,b=cycle[name]
                found=[a+(b-a)*q/20 for q in range(1,20)
                       if renderer.sink.geometry_at(a+(b-a)*q/20,renderer.animation.scene_state(a+(b-a)*q/20),renderer.animation)['phase']==phase]
                assert found,('missing tap phase',cycle['id'],phase)
                checks.append(inspect_sink(renderer,found[len(found)//2]))
        report['sink_contact_checks']=checks
        if args.final:
            report['final_video_sha256']=digest(EP/'MOU_Encore_une_feuille.mp4')
            report['actual_final_samples']=decoded_proofs(renderer,EP/'MOU_Encore_une_feuille.mp4')
        assert frozen=={str(p.relative_to(ROOT)):digest(p)for p in tracked},'source changed during audit'
        report['frozen_sources_sha256']=frozen
        report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        raise
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(path),'scope':report['scope']},ensure_ascii=False))


if __name__=='__main__':main()
