"""Independently check the scoped paper correction against the delivered V10.

Run from the repository root with the project Python. The historical comparison
uses Git; geometry and raster checks read the emitted SVG, not the artist's
interpolation helpers. This is a material/preservation audit, not audience QA.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import types
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
BASE = 'b7328c6c628fa16dc5b5e1d6b1633280d32e49b6'
NS = '{http://www.w3.org/2000/svg}'
IDENTITY = (1., 0., 0., 1., 0., 0.)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


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


def stripped(svg):
    root=ET.fromstring(svg)
    removed=0
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get('id')=='papier-en-main':
                parent.remove(child);removed+=1
    assert removed<=1
    return ET.tostring(root,encoding='utf-8')


def alpha(fragment, without_texture=False):
    root=ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" width="400" height="400">{fragment}</svg>')
    if without_texture:
        for parent in root.iter():
            for child in list(parent):
                if child.tag==NS+'path' and child.attrib.get('fill','none')=='none':
                    parent.remove(child)
    raw=cairosvg.svg2png(bytestring=ET.tostring(root,encoding='utf-8'))
    return np.asarray(Image.open(io.BytesIO(raw)).getchannel('A'))


def main():
    # These bytes must remain unchanged for this narrowly scoped correction.
    paths=['mou_rig.py','episodes/03/cuisine_v6/chronologie.json',
           'fonts/DejaVuSans-Bold.ttf','episodes/03/cuisine_v6/audio/mix.wav']
    paths += [f'episodes/03/cuisine_v6/sources/{name}.py' for name in ('animation','son')]
    preserved={}
    for path in paths:
        old,new=historical(path),(ROOT/path).read_bytes()
        assert old == new, ('unauthorized source/audio change',path)
        preserved[path]=sha(new)
    # The strict actual-export check found two hand ROI errors just above
    # 3/255 at CRF14. Raise encode quality only, preserving every SVG byte.
    render_path='episodes/03/cuisine_v6/sources/render.py'
    old_render,new_render=historical(render_path),(ROOT/render_path).read_bytes()
    old_literal,new_literal=b"'-crf','14'",b"'-crf','12'"
    assert old_render.count(old_literal)==1
    assert new_render==old_render.replace(old_literal,new_literal), 'renderer changed beyond encoding quality'
    encoding_exception={'path':render_path,'baseline_sha256':sha(old_render),
        'current_sha256':sha(new_render),'only_byte_change':"'-crf','14' -> '-crf','12'",
        'reason':'Two decoded hand ROI errors exceeded the unchanged 3/255 threshold at CRF14; use CRF12.',
        'svg_rendering_code_otherwise_byte_identical':True}
    art_path=EP/'sources/art.py'; before=sha(art_path.read_bytes())
    old_source=historical('episodes/03/cuisine_v6/sources/art.py').decode()
    old_art=types.ModuleType('audit_baseline_art')
    exec(compile(old_source,'<historical art.py>','exec'),old_art.__dict__)
    def definitions(source):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
    olddefs,newdefs=definitions(old_source),definitions(art_path.read_text())
    unchanged=[]
    for name,definition in olddefs.items():
        if name != 'paper_svg':
            assert newdefs.get(name) == definition, ('unrelated art function changed',name)
            unchanged.append(name)
    spec=importlib.util.spec_from_file_location('audit_material_renderer',EP/'sources/render.py')
    renderer=importlib.util.module_from_spec(spec);sys.modules[spec.name]=renderer;spec.loader.exec_module(renderer)
    new_art=renderer.art
    assert (new_art.LAST_PAPER_WIDTH,new_art.LAST_PAPER_HEIGHT)==(64.,88.)
    assert new_art.BIN_RADII == old_art.BIN_RADII
    changed=[];identical=0
    for index in range(840):
        t=index/24.
        renderer.art=old_art; old=renderer.svg_at(t)
        renderer.art=new_art; new=renderer.svg_at(t)
        assert stripped(old) == stripped(new), ('non-paper scene changed',index)
        if old == new:
            identical+=1
        else:
            state=renderer.animation.scene_state(t);paper=state.get('paper')
            assert 29.65<=t<=32.65 and state['cycle']==4 and paper and paper['mode'] in ('tiny','tiny_pull','tiny_wipe','crumple'), ('change outside last material scene',index,t)
            changed.append(index)
    assert changed
    pieces={mode:outline(new_art.paper_svg({'mode':mode,'center':(0.,0.)},0.)) for mode in ('tiny','tiny_pull','tiny_wipe')}
    assert pieces['tiny']==pieces['tiny_pull']==pieces['tiny_wipe']
    areas=[];worst_intersections=0;texture_samples=0;texture_spill_pixels=0
    for step in range(1001):
        p=step/1000.
        fragment=new_art.paper_svg({'mode':'crumple','cycle':4,'center':(0.,0.),'r':22.,'progress':p})
        points=outline(fragment)
        intersections=crossings(points); a=area(points)
        assert not intersections, ('self-crossing crumple silhouette',p,intersections)
        assert a>0., ('winding/collapse',p,a)
        areas.append(a);worst_intersections=max(worst_intersections,len(intersections))
        material=ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{fragment}</svg>')
        paths=list(material.iter(NS+'path'))
        filled=next(e for e in paths if e.attrib.get('fill','none')!='none')
        clip=next(e for e in material.iter(NS+'clipPath') if e.attrib.get('id')=='papier-dernier-plis-clip')
        assert next(iter(clip)).attrib['d']==filled.attrib['d'], ('texture clip differs from silhouette',p)
        if step%20==0:
            full=alpha(fragment);base=alpha(fragment,True)
            spill=int(np.count_nonzero((full.astype(np.int16)-base.astype(np.int16))>1))
            assert spill==0, ('texture spills outside paper alpha',p,spill)
            texture_samples+=1;texture_spill_pixels=max(texture_spill_pixels,spill)
        if step==0:
            start_points=points
        if step==1000:
            end_points=points
    held_mask,start_mask=mask(pieces['tiny']),mask(start_points)
    assert np.array_equal(held_mask,start_mask), 'held-to-crumple silhouette jump'
    target=outline(new_art.paper_svg({'mode':'ball','cycle':4,'center':(0.,0.),'r':22.,'rotation':0.}))
    final_mask,target_mask=mask(end_points),mask(target)
    end_error=int(np.count_nonzero(final_mask!=target_mask))
    assert end_error<50, ('crumple-to-ball silhouette mismatch',end_error)
    assert sha(art_path.read_bytes())==before, 'artist changed art during audit'
    report={'status':'passed','baseline_commit':BASE,'scope':'Only the final sheet material and its continuous crumple; no audio listening or audience validation.',
            'preserved_files_sha256':preserved,'encoding_quality_exception':encoding_exception,
            'art_sha256':before,'unchanged_art_functions':unchanged,
            'scene_comparison':{'frames':840,'identical_full_svg_frames':identical,
                'changed_paper_only_frames':len(changed),'first_changed_frame':min(changed),'last_changed_frame':max(changed),
                'first_changed_seconds':min(changed)/24.,'last_changed_seconds':max(changed)/24.,
                'all_non_paper_svg_subtrees_identical':True},
            'geometry':{'method':'Flatten actual emitted SVG M/L/H/V/Q/C/Z outlines, applying SVG transforms; test strict nonadjacent segment crossings and signed areas. Endpoints compared by independent CairoSVG alpha raster.',
                'progress_samples':1001,'curve_subdivisions_per_segment':12,'strict_crossings':worst_intersections,
                'min_signed_area':min(areas),'max_signed_area':max(areas),'start_signed_area':areas[0],'end_signed_area':areas[-1],
                'same_outline_for_pull_reveal_wipe':True,'held_vs_crumple_zero_alpha_exact':True,
                'all_progress_texture_clip_matches_current_outline':True,
                'texture_alpha_raster_samples':texture_samples,'texture_spill_pixels':texture_spill_pixels,
                'crumple_one_vs_ball_alpha_different_pixels':end_error,'endpoint_raster_dimensions':[800,800],
                'sheet_dimensions':[64.,88.],'last_ball_radius':22.}}
    destination=EP/'controle/audit_papier_v11.json'
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
