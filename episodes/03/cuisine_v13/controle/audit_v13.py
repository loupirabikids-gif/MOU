"""Independent production-state, native-shape and contact audit for MOU V13.

Run from a checkout containing the delivered V12 baseline. This reads emitted
SVG and the canonical rig, not PNG caches. Decoded-film checks and visual
critique are separate; no claim of audio listening or audience comprehension.
"""
from __future__ import annotations
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
import tempfile
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP=Path(__file__).resolve().parents[1]
BASE='bad439dafb1d2bd7fccb2683efc4d7c2258be8c7'
NS='{http://www.w3.org/2000/svg}'
IDENTITY=(1.,0.,0.,1.,0.,0.)
FPS=24


def sha(data):
    return hashlib.sha256(data).hexdigest()


def historical(name):
    return subprocess.check_output(['git','show',f'{BASE}:{name}'],cwd=ROOT)


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def definitions(source):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}


def near(a,b):
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isclose(a,b,rel_tol=1.e-10,abs_tol=1.e-7)
    if isinstance(a,dict) and isinstance(b,dict):
        return a.keys()==b.keys() and all(near(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        return len(a)==len(b) and all(near(x,y) for x,y in zip(a,b))
    return a==b

def compose(a, b):
    aa, ab, ac, ad, ae, af = a
    ba, bb, bc, bd, be, bf = b
    return (aa*ba+ac*bb, ab*ba+ad*bb, aa*bc+ac*bd, ab*bc+ad*bd,
            aa*be+ac*bf+ae, ab*be+ad*bf+af)

def transform(text):
    result = IDENTITY
    for name, raw in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)', text):
        v = [float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?', raw)]
        if name == 'translate':
            matrix = (1., 0., 0., 1., v[0], v[1] if len(v)>1 else 0.)
        elif name == 'scale':
            matrix = (v[0], 0., 0., v[1] if len(v)>1 else v[0], 0., 0.)
        elif name == 'rotate':
            angle = math.radians(v[0]); c, s = math.cos(angle), math.sin(angle)
            matrix = (c, s, -s, c, 0., 0.)
            if len(v) == 3:
                matrix = compose((1.,0.,0.,1.,v[1],v[2]),
                                 compose(matrix,(1.,0.,0.,1.,-v[1],-v[2])))
        elif name == 'matrix':
            matrix = tuple(v)
        else:
            raise AssertionError(('unsupported transform', name))
        result = compose(result, matrix)
    return result

def apply(matrix, p):
    a,b,c,d,e,f = matrix
    return a*p[0]+c*p[1]+e, b*p[0]+d*p[1]+f

def flatten_path(data):
    """Flatten the actual emitted M/L/H/V/Q/C/Z outline independently."""
    tokens = re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?', data)
    points = []; current = (0.,0.); start = None; i = 0; command = None
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]; i += 1
        assert command is not None
        kind = command.upper(); relative = command.islower()
        if kind == 'Z':
            current = start
            command = None
            continue
        n = {'M':2,'L':2,'H':1,'V':1,'Q':4,'C':6}.get(kind)
        assert n is not None, ('unsupported outline command', command)
        values = tuple(float(v) for v in tokens[i:i+n]); i += n
        def point(x, y):
            return (x+current[0],y+current[1]) if relative else (x,y)
        if kind in ('M','L'):
            current = point(*values); points.append(current)
            if kind == 'M':
                start = current; command = 'l' if relative else 'L'
        elif kind == 'H':
            current = ((current[0]+values[0]) if relative else values[0],current[1]); points.append(current)
        elif kind == 'V':
            current = (current[0],(current[1]+values[0]) if relative else values[0]); points.append(current)
        elif kind in ('Q','C'):
            p0 = current
            control = [point(*values[j:j+2]) for j in range(0,n,2)]
            for j in range(1,13):
                t=j/12.; u=1.-t
                if kind == 'Q':
                    p1,p2=control
                    p=(u*u*p0[0]+2*u*t*p1[0]+t*t*p2[0],u*u*p0[1]+2*u*t*p1[1]+t*t*p2[1])
                else:
                    p1,p2,p3=control
                    p=(u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                       u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1])
                points.append(p)
            current=control[-1]
    if len(points)>1 and math.dist(points[0],points[-1]) < 1.e-8:
        points.pop()
    return points

def outline(fragment):
    root=ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{fragment}</svg>')
    def visit(element, parent=IDENTITY):
        matrix=compose(parent,transform(element.attrib.get('transform','')))
        if element.tag == NS+'path' and element.attrib.get('fill','none') not in ('none','transparent'):
            return [apply(matrix,p) for p in flatten_path(element.attrib['d'])]
        for child in element:
            found=visit(child,matrix)
            if found is not None:
                return found
        return None
    result=visit(root)
    assert result is not None
    return result

def area(points):
    return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))

def crossings(points):
    def cross(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    edges=list(zip(points,points[1:]+points[:1])); found=[]
    for i,(a,b) in enumerate(edges):
        for j in range(i+2,len(edges)):
            if i == 0 and j == len(edges)-1:
                continue
            c,d=edges[j]
            # Strict crossings exclude shared vertices and collinear edges.
            if cross(a,b,c)*cross(a,b,d)<-1.e-8 and cross(c,d,a)*cross(c,d,b)<-1.e-8:
                found.append([i,j])
    return found

def mask(points):
    data='M'+' L'.join(f'{x:.8f} {y:.8f}' for x,y in points)+' Z'
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" width="800" height="800"><path d="{data}" fill="white"/></svg>'
    return np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).getchannel('A'))

def alpha(fragment, without_texture=False):
    root=ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" width="400" height="400">{fragment}</svg>')
    if without_texture:
        for parent in root.iter():
            for child in list(parent):
                if child.tag==NS+'path' and child.attrib.get('fill','none')=='none':
                    parent.remove(child)
    raw=cairosvg.svg2png(bytestring=ET.tostring(root,encoding='utf-8'))
    return np.asarray(Image.open(io.BytesIO(raw)).getchannel('A'))


def records(tree):
    """Return actual element/ancestor transforms from the emitted SVG."""
    out=[]
    def walk(node,parent=IDENTITY):
        matrix=compose(parent,transform(node.attrib.get('transform','')))
        out.append((node,matrix))
        for child in node:
            walk(child,matrix)
    walk(tree)
    return out


def hand_tip(animation,state,side='left'):
    """Derive the canonical cap extreme independently of the salt helper."""
    meta=state['arm_meta'][side]
    points=animation.controls(side,meta['hips'],meta['clasp'])
    end=points[-1]; tangent=animation._tangent(points,1.)
    local=(end[0]+19.*tangent[0],end[1]+19.*tangent[1])
    sx,sy=animation.SHOULDERS[side]
    theta=math.radians(meta['rotation']);c,s=math.cos(theta),math.sin(theta)
    dx,dy=local[0]-sx,local[1]-sy
    x,y,scale=state['actor_transform']
    return x+scale*(sx+c*dx-s*dy),y+scale*(sy+s*dx+c*dy)


def raster_path(element,matrix,viewbox,size=(540,960)):
    node=copy.deepcopy(element)
    node.attrib.pop('transform',None)
    node.attrib.update(fill='white',stroke='none',opacity='1')
    # Only the chosen actual filled path; decorative highlights are excluded.
    root=ET.Element(NS+'svg',{'viewBox':' '.join(map(str,viewbox)),
                            'width':str(size[0]),'height':str(size[1])})
    group=ET.SubElement(root,NS+'g',{'transform':'matrix('+ ' '.join(map(str,matrix))+')'})
    group.append(node)
    return np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=ET.tostring(root)))).getchannel('A'))


def inverse(matrix,points):
    a,b,c,d,e,f=matrix;den=a*d-b*c
    assert abs(den)>1.e-9
    x,y=points[:,0]-e,points[:,1]-f
    return np.stack(((d*x-c*y)/den,(-b*x+a*y)/den),axis=1)


def sink_contact(renderer,t,state,svg):
    """Measure emitted native-fill/primary-jet overlap in canonical coordinates."""
    root=ET.fromstring(svg); rec=records(root)
    hand,matrix=next((e,m)for e,m in rec if e.attrib.get('data-part')=='hand')
    native_group=next(e for e,_ in rec if e.attrib.get('id')=='lavabo-main-native')
    hips,clasp=float(native_group.attrib['data-hips']),float(native_group.attrib['data-clasp'])
    native=ET.fromstring('<svg>'+renderer.animation._arm('left',hips,clasp)+'</svg>')
    original=next(e for e in native.iter() if e.attrib.get('data-part')=='hand')
    assert hand.attrib['d']==original.attrib['d'], ('sink replaced native mitten',t)
    values=np.array(((matrix[0],matrix[2]),(matrix[1],matrix[3])))
    singular=np.linalg.svd(values,compute_uv=False)
    assert np.allclose(singular,[1.61,1.61],atol=1.e-6),('sink deforms native hand',t,singular.tolist())
    g=renderer.sink.geometry_at(t,state,renderer.animation)
    # A moving lever's endpoint must be touched by the true native cap extreme.
    controls=renderer.animation.controls('left',hips,clasp)
    end=np.array(controls[-1]); tangent=np.array(renderer.animation._tangent(controls,1.))
    distal=apply(matrix,tuple(end+19.*tangent))
    tap_error=None
    if g['phase'] in ('open_tap','close_tap'):
        tap_error=math.dist(distal,g['tap_target'])
        assert tap_error<.001,('hand misses moving tap',t,tap_error)
    jet_record=next(((e,m) for e,m in rec if e.attrib.get('id')=='lavabo-jet-primary'),None)
    result={'time':t,'phase':g['phase'],'tap_error':tap_error,'uniform_native_scale':float(singular[0]),
            'wet_pixels':0,'minimum_local_cap_projection':None,'wet_fraction_of_distal_cap':0.}
    if jet_record is None:
        assert not state['water'],('source water flag and actual jet differ',t)
        return result
    viewbox=tuple(map(float,root.attrib['viewBox'].split()))
    hand_mask=raster_path(hand,matrix,viewbox)>127
    jet_mask=raster_path(*jet_record,viewbox)>127
    ys,xs=np.nonzero(hand_mask & jet_mask)
    if not len(xs):
        assert g['phase']!='rinse_tip',('tip fails to contact actual water',t)
        return result
    height,width=hand_mask.shape;vx,vy,vw,vh=viewbox
    world=np.stack((vx+(xs+.5)*vw/width,vy+(ys+.5)*vh/height),axis=1)
    local=inverse(matrix,world)
    axial=(local-end)@tangent
    # The fingertip is the distal semicircle beyond the end of the native
    # centerline. Negative projection would wet the palm/wrist/forearm.
    minimum=float(axial.min())
    assert minimum>=-.75,('water overlaps palm/wrist beyond distal cap',t,minimum)
    all_y,all_x=np.nonzero(hand_mask)
    all_world=np.stack((vx+(all_x+.5)*vw/width,vy+(all_y+.5)*vh/height),axis=1)
    all_local=inverse(matrix,all_world)
    cap_count=int(np.count_nonzero((all_local-end)@tangent>=0.))
    fraction=len(xs)/max(1,cap_count)
    assert fraction<.60,('more than fingertip portion of cap washed',t,fraction)
    result.update(wet_pixels=len(xs),minimum_local_cap_projection=minimum,
                  wet_fraction_of_distal_cap=fraction)
    wet_group=next((e for e,_ in rec if e.attrib.get('id')=='lavabo-wet-tip'),None)
    if wet_group is not None:
        clip=next(e for e,_ in rec if e.attrib.get('id')=='lavabo-main-contour')
        clip_path=next(iter(clip))
        assert clip_path.attrib['d']==hand.attrib['d'],('wet tint clip changes native outline',t)
        assert near(transform(clip_path.attrib.get('transform','')),matrix),('wet tint clip transform differs',t)
        tint_record=next((e,m)for e,m in rec if e in list(wet_group))
        tint=raster_path(*tint_record,viewbox)>127
        tint_y,tint_x=np.nonzero(hand_mask&tint)
        tint_world=np.stack((vx+(tint_x+.5)*vw/width,vy+(tint_y+.5)*vh/height),axis=1)
        tint_local=inverse(matrix,tint_world)
        tint_axial=(tint_local-end)@tangent
        assert len(tint_axial)>0 and float(tint_axial.min())>=-.75,('wet tint paints palm/wrist',t)
        tint_fraction=len(tint_x)/max(1,cap_count)
        assert tint_fraction<.60,('wet tint covers too much cap',t,tint_fraction)
        result.update(wet_tint_pixels=len(tint_x),wet_tint_fraction_of_distal_cap=tint_fraction,
                      wet_tint_minimum_local_projection=float(tint_axial.min()),
                      wet_tint_clip_exact_native_outline=True)
    return result


def paper_geometry(art,old_art):
    radii=(47.,53.,59.,61.,22.);seeds=(1,2,3,3,4)
    results=[]
    for ordinal,(radius,seed) in enumerate(zip(radii,seeds),1):
        tiny=ordinal==5;areas=[]
        for step in range(101):
            u=step/100.
            fragment=art.paper_svg({'mode':'crumple','cycle':ordinal,'visual_seed':seed,'tiny':tiny,
                                    'center':(0.,0.),'r':radius,'progress':u})
            polygon=outline(fragment);a=area(polygon)
            assert not crossings(polygon),('paper crosses while crumpling',ordinal,u)
            assert a>0.,('paper collapse/winding',ordinal,u,a)
            areas.append(a)
            if step==0:start=polygon
            if step==100:finish=polygon
        ball=outline(art.paper_svg({'mode':'ball','cycle':ordinal,'visual_seed':seed,'tiny':tiny,
                                   'center':(0.,0.),'r':radius,'rotation':0.}))
        error=int(np.count_nonzero(mask(finish)!=mask(ball)))
        assert error<50,('crumple/ball endpoint jump',ordinal,error)
        if tiny:
            held=art.paper_svg({'mode':'tiny','cycle':ordinal,'visual_seed':seed,'tiny':True,'center':(0.,0.)})
            previous=old_art.paper_svg({'mode':'tiny','cycle':4,'center':(0.,0.)})
            assert held==previous,'last held material changed beyond approved acting'
            assert np.array_equal(mask(outline(held)),mask(start)), 'last held/crumple jump'
            old_ball=old_art.paper_svg({'mode':'ball','cycle':4,'center':(0.,0.),'r':22.,'rotation':0.})
            new_ball=art.paper_svg({'mode':'ball','cycle':5,'visual_seed':4,'tiny':True,'center':(0.,0.),'r':22.,'rotation':0.})
            assert new_ball==old_ball,'last tiny ball identity changed'
        results.append({'cycle':ordinal,'radius':radius,'visual_seed':seed,'samples':101,
                        'min_area':min(areas),'max_area':max(areas),'strict_crossings':0,
                        'endpoint_alpha_different_pixels':error})
    return results


def main():
    report_path=EP/'controle/audit_v13.json'
    report={'status':'in_progress','baseline_commit':BASE,
            'scope':'Independent native model, emitted SVG/state, salt/contact and material continuity checks. Separate actual-film decode/visual critique required; no listening or audience validation.'}
    try:
        paths=[ROOT/'mou_rig.py',ROOT/'fonts/DejaVuSans-Bold.ttf',EP/'chronologie.json']
        paths += [EP/'sources'/name for name in ('animation.py','art.py','render.py','sink.py')]
        frozen={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}
        for name in ('mou_rig.py','fonts/DejaVuSans-Bold.ttf','episodes/03/decor/MOU_cuisine_decor.svg'):
            assert (ROOT/name).read_bytes()==historical(name),('canonical model/decor altered',name)
        for name in ('chronologie.json','sources/animation.py','sources/art.py','sources/render.py','sources/son.py'):
            path='episodes/03/cuisine_v6/'+name
            assert (ROOT/path).read_bytes()==historical(path),('previous delivered production altered',path)
        olddefs=definitions(historical('episodes/03/cuisine_v6/sources/animation.py').decode())
        newdefs=definitions((EP/'sources/animation.py').read_text())
        arm_functions=('controls','native_grip','world_grip','solve_arm','arm_linear_transform',
                       '_connect_left_root','soften_left_root','draw_arm')
        for name in arm_functions:
            assert olddefs[name]==newdefs[name],('native arm drawing/solver changed',name)
        oldart=load(ROOT/'episodes/03/cuisine_v6/sources/art.py','qa_v12_art')
        renderer=load(EP/'sources/render.py','qa_v13_renderer')
        timeline=renderer.animation.PRODUCTION_TIMELINE
        assert (timeline['duration'],timeline['fps'],timeline['dimensions'])==(41.,24,[1080,1920])
        cycles=timeline['cycles'];assert [c['id'] for c in cycles]==[1,2,3,4,5]
        assert [c['tiny'] if 'tiny'in c else False for c in cycles]==[False,False,False,False,True]
        assert timeline['paper_stock']==[1.,.82,.58,.32,.006,0.]
        assert tuple(renderer.animation.BIN_LANDS)==tuple(renderer.art.BIN_CENTRES)
        assert tuple(renderer.animation.BIN_RADII)==tuple(renderer.art.BIN_RADII)==(47.,53.,59.,61.,22.)
        states=[];counts=[];stocks=[];carrot_cuts=[];paper_samples=flight_samples=caption_frames=0
        wide_frames=sink_frames=grain_samples=0;max_origin_error=max_native_tip_error=0.
        sink_checks=[];wash_cycle_sampled=set();tap_cycle_sampled=set()
        preserved_cooking=0
        oldanim=load(ROOT/'episodes/03/cuisine_v6/sources/animation.py','qa_v12_animation')
        # Load each actual emitted scene, independently from cached PNGs.
        for index in range(round(timeline['duration']*FPS)):
            t=index/FPS;state=renderer.animation.scene_state(t);states.append(state)
            assert set(state['hands'])=={'left','right'},('physical hand count',index)
            assert state['actor_transform'][2]==2.3,('wide actor scale changed',index)
            tree=ET.fromstring(renderer.svg_at(t));ids=[e.attrib['id']for e in tree.iter()if 'id'in e.attrib]
            assert len(ids)==len(set(ids)),('duplicate SVG IDs',index)
            assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',ET.tostring(tree,encoding='unicode'))),('unresolved clip',index)
            emitted_view=tuple(map(float,tree.attrib['viewBox'].split()))
            assert np.allclose(emitted_view,renderer.camera_at(t,state),rtol=0.,atol=1.e-6),('camera metadata differs from emitted framing',index,emitted_view,renderer.camera_at(t,state))
            hands=[e for e in tree.iter()if e.attrib.get('data-part')=='hand']
            if state['shot']=='sink':
                sink_frames+=1;assert len(hands)==1,('sink must show one native hand only',index)
                assert 'mou-corps'not in ids and 'mouth'not in ids,('body/face in sink insert',index)
                g=renderer.sink.geometry_at(t,state,renderer.animation);cid=state['cycle']
                # One measurement per moving-tap direction and three real
                # water-contact phases per cycle; paths come from final SVG.
                c=state['production_cycle'];wash=c['wash'];u=(t-wash[0])/max(1.e-9,wash[1]-wash[0])
                key=(cid,min(2,max(0,int(u*3))))
                tapkey=(cid,g['phase'])
                if (g['phase']=='rinse_tip' and key not in wash_cycle_sampled) or (g['phase']in('open_tap','close_tap')and tapkey not in tap_cycle_sampled):
                    sink_checks.append(sink_contact(renderer,t,state,ET.tostring(tree,encoding='unicode')))
                    if g['phase']=='rinse_tip':wash_cycle_sampled.add(key)
                    else:tap_cycle_sampled.add(tapkey)
            else:
                wide_frames+=1;assert len(hands)==2,('wide must show two native hands',index)
            caption_frames+=int('caption-ouverture'in ids)
            counts.append(state['bin_count']);stocks.append(float(state['roll']['remaining']));carrot_cuts.append(state['carrot']['cuts'])
            assert state['bin_count']==sum(t>=c['land']for c in cycles),('bin chronology',index)
            assert state['carrot']['cuts']==sum(t>=q for q in timeline['carrot']['cut_times']),('carrot persistence',index)
            assert bool(state['tomato_added'])==(t>=timeline['cooking_events']['tomato_contact']),('tomato chronology',index)
            if t<21.72:assert state['tomato']==renderer.animation.TOMATO_START,('tomato dish continuity',index)
            if t>=15.95:assert not state['carrot']['knife_held'],('knife not parked',index)
            paper=state.get('paper')
            if paper:
                cid=state['cycle'];assert paper['cycle']==cid
                assert paper['r']==renderer.art.BIN_RADII[cid-1]
                assert bool(paper.get('tiny',False))==(cid==5)
                assert paper['visual_seed']==renderer.art.BIN_VISUAL_SEEDS[cid-1]
                if paper['mode']=='pull':
                    assert math.dist(paper['start'],state['roll']['edge'])<.001,('paper is detached from shrinking roll',index)
                    assert min(math.dist(paper['end'],p)for p in state['hands'].values())<.001,('paper misses native grip',index)
                paper_samples+=1
            flying=state.get('flying_ball')
            if flying:
                cid=state['cycle'];assert flying['r']==renderer.art.BIN_RADII[cid-1]
                assert flying['visual_seed']==renderer.art.BIN_VISUAL_SEEDS[cid-1]
                flight_samples+=1
            salt=state.get('salt')
            if salt and salt.get('active'):
                actual=hand_tip(renderer.animation,state,salt['hand_side'])
                tip_error=math.dist(actual,salt['pinch_tip']);max_native_tip_error=max(max_native_tip_error,tip_error)
                assert tip_error<.001,('salt pinch not on original distal tip',index,tip_error)
            for grain in tree.iter():
                if grain.attrib.get('data-grain')!='fall':continue
                attr=grain.attrib;born=float(attr['data-emission-time'])
                emission=renderer.animation.scene_state(born)
                origin=hand_tip(renderer.animation,emission,emission['salt']['hand_side'])
                declared=(float(attr['data-origin-x']),float(attr['data-origin-y']))
                error=math.dist(origin,declared);max_origin_error=max(max_origin_error,error)
                assert error<.002,('salt grain release leaves original tip',index,born,error)
                target=(float(attr['data-target-x']),float(attr['data-target-y']))
                assert ((target[0]-293.)/135.)**2+((target[1]-1305.)/42.)**2<1.,('salt misses pan',index,target)
                u=float(attr['data-progress']);x,y=float(attr['cx']),float(attr['cy'])
                assert -.001<=u<=1.001 and min(origin[0],target[0])-.1<=x<=max(origin[0],target[0])+.1
                assert min(origin[1],target[1])-.1<=y<=max(origin[1],target[1])+.1
                grain_samples+=1
            # Existing cooking/utensil motions keep their original native grip.
            ref=t-6. if 33.<=t<34. else t
            if 0.<=t<6.6 or 13.5<=t<16.3 or 21.5<=t<23. or 33.<=t<34.:
                old=oldanim.scene_state(ref)
                for key in ('hands','arm_meta','actor_transform','spoon','spoon_held'):
                    assert near(state[key],old[key]),('unrequested cooking movement changed',index,key)
                preserved_cooking+=1
        assert counts==sorted(counts) and counts[0]==0 and counts[-1]==5
        assert stocks==sorted(stocks,reverse=True) and stocks[0]==1. and stocks[-1]==0.
        assert carrot_cuts==sorted(carrot_cuts)and carrot_cuts[-1]==2
        assert caption_frames==72
        first_inspection=[s for s in states if 7.<=s['production_time']<7.75]
        reveal=cycles[-1]['reveal']
        last_reveal=[s for s in states if reveal[0]<=s['production_time']<reveal[1]]
        final=[s for s in states if timeline['final'][0]<=s['production_time']]
        hold=[s for s in final if s['production_time']>=timeline['final_hold'][0]]
        assert all(abs(s.get('proud_nod_offset',0.))<1.e-9 for s in hold),'final nod did not settle before hold'
        acting_metrics={'first_inspection_smile_min':min(s['pose']['smile']for s in first_inspection),
                        'first_inspection_brow_peak':max(s['pose']['brow_raise']for s in first_inspection),
                        'last_reveal_left_eye_min':min(s['pose']['eye_open_l']for s in last_reveal),
                        'last_reveal_tube_glance_frames':sum(math.dist(s['look_target'],(876.,1175.))<.01 for s in last_reveal),
                        'final_smile_min':min(s['pose']['smile']for s in final),
                        'final_nod_offset_peak':max(s.get('proud_nod_offset',0.)for s in final),
                        'final_hold_nod_settled':True}
        assert len(wash_cycle_sampled)==15 and len(tap_cycle_sampled)==10
        assert grain_samples>0 and all(c['wash'][0]>=timeline['salt']['end'] for c in cycles if c['id']==4)
        # Attached tube/grip and each flight endpoint are checked at exact
        # event times as well as sampled film frames.
        exact_roll_contacts=[]
        for cycle in cycles:
            t=cycle['pull'][0]
            state=renderer.animation.scene_state(t)
            error=math.dist(state['hands']['right'],state['roll']['hand'])
            assert error<.02,('native hand misses actual shrinking roll at pull',cycle['id'],error)
            flight=renderer.animation.scene_state(cycle['land']-1.e-6)['flying_ball']
            centre=renderer.art.BIN_CENTRES[cycle['id']-1]
            flight_error=math.dist((flight['x'],flight['y']),centre)
            assert flight_error<.02,('ball flight ends away from landed ball',cycle['id'],flight_error)
            exact_roll_contacts.append({'cycle':cycle['id'],'right_grip_to_roll_error':error,
                                        'flight_to_landed_centre_error':flight_error})
        geometry=paper_geometry(renderer.art,oldart)
        assert frozen=={str(p.relative_to(ROOT)):sha(p.read_bytes())for p in paths},'production changed during QA'
        report.update(status='passed',tested_sources_sha256=frozen,preserved_native_arm_functions=list(arm_functions),
          scenes={'frames':len(states),'wide_frames':wide_frames,'sink_frames':sink_frames,'physical_hands_each_state':2,
                  'rendered_hands_wide':2,'rendered_hands_sink':1,'caption_frames':caption_frames,
                  'preserved_native_cooking_performance_frames':preserved_cooking,
                  'all_emitted_viewboxes_match_camera_metadata':True},
          continuity={'bin_count_first_last':[counts[0],counts[-1]],'bin_count_monotonic':True,
                      'roll_stock_first_last':[stocks[0],stocks[-1]],'roll_stock_monotonic_decreasing':True,
                      'carrot_cuts_persist':True,'paper_samples':paper_samples,'flying_samples':flight_samples,
                      'bin_centres':renderer.art.BIN_CENTRES,'radii':renderer.art.BIN_RADII,
                      'exact_roll_and_flight_contacts':exact_roll_contacts},
          salt={'falling_grain_samples':grain_samples,'maximum_native_tip_error':max_native_tip_error,
                'maximum_emission_origin_error':max_origin_error,'all_targets_in_pan':True},
          sink={'method':'Independently extract actual native fill and primary jet from emitted SVG; rasterize540x960, inverse-transform their overlap into canonical native cap coordinates. Negative axial projection would wet palm/wrist. Native shape and uniform scale checked directly.',
                'checks':sink_checks,'rinse_samples':len(wash_cycle_sampled),'moving_tap_samples':len(tap_cycle_sampled)},
          paper_geometry=geometry,acting_parameter_observations=acting_metrics,
          limits='SVG/state/contact checks and finite geometry samples, not continuous audience viewing or sound audition. Actual encoded MP4s are audited and visually reviewed separately.')
    except Exception as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
        report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
        raise
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
