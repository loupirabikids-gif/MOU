"""Independent V26 export, geometric continuity and fresh-raster checks.

Run after the final renderer and audio authors have frozen their sources.
This checker does not manufacture frames or reuse the PNG raster cache.
It makes no claim of hearing, emotional recognition or audience success.
"""
from __future__ import annotations
import argparse
import ast
from fractions import Fraction
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
import tempfile
import wave
import xml.etree.ElementTree as ET
import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
TIMELINE=json.loads((EP/'chronologie.json').read_text())
W,H=TIMELINE['dimensions']
FPS,DURATION=int(TIMELINE['fps']),float(TIMELINE['duration'])
NFRAMES=round(FPS*DURATION)
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
MEAN_ERROR_LIMIT=3.0
SAMPLE_TIMES=(.5,1.8,2.75,3.25,3.85,4.5,5.4,6.15,6.75,7.45,8.4,
 9.4,9.98,10.75,11.35,11.9,13.,13.4,14.65,15.65,16.5,16.9,18.,18.3,
 19.2,20.25,21.4,22.15,22.75,23.3,23.7,24.3,24.95,25.4,25.8,26.2,
 26.8,27.75,28.25,28.5,29.05,29.5,29.9,30.8,31.8,32.5,33.7,34.7,35.5,37.5)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            output.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def command(args):
    try:
        return subprocess.check_output(args, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f'{args[0]} exited {error.returncode}: '
                           f'{error.stderr.decode(errors="replace")[-3000:]}') from error


def probe(path):
    return json.loads(command(['ffprobe', '-v', 'error', '-count_frames',
        '-show_streams', '-show_format', '-of', 'json', str(path)]))


def check_video(path, sound):
    data = probe(path)
    videos = [s for s in data['streams'] if s['codec_type'] == 'video']
    audios = [s for s in data['streams'] if s['codec_type'] == 'audio']
    assert len(videos) == 1 and len(audios) == int(sound), (str(path), 'stream count')
    assert len(data['streams']) == 1+int(sound), (str(path), 'unexpected stream')
    video = videos[0]
    assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p', video
    assert (video['width'], video['height']) == (W, H), video
    assert Fraction(video['r_frame_rate']) == FPS, video['r_frame_rate']
    assert Fraction(video['avg_frame_rate']) == FPS, video['avg_frame_rate']
    assert int(video['nb_read_frames']) == NFRAMES, video['nb_read_frames']
    assert int(video['nb_frames']) == NFRAMES, video['nb_frames']
    assert abs(float(video['duration'])-DURATION) < .001, video['duration']
    assert abs(float(data['format']['duration'])-DURATION) < .05, data['format']['duration']
    if sound:
        audio = audios[0]
        assert audio['codec_name'] == 'aac', audio
        assert (int(audio['sample_rate']), int(audio['channels'])) == (48000, 2), audio
        assert abs(float(audio['duration'])-DURATION) < .025, audio['duration']
    subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2',
        '-i', str(path), '-map', '0', '-f', 'null', '-'], check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return {'path': str(path.relative_to(ROOT)), 'file_sha256': digest(path),
            'size_bytes': path.stat().st_size, 'full_decode_without_errors': True,
            'streams': [{k: s[k] for k in ('codec_type', 'codec_name', 'width', 'height',
                'pix_fmt', 'r_frame_rate', 'avg_frame_rate', 'nb_frames', 'nb_read_frames',
                'duration', 'sample_rate', 'channels') if k in s} for s in data['streams']]}


def bitstream_digest(path):
    # Strip the MP4 container. The compressed H264 stream must be identical
    # after the AAC mux, not merely similar after decompression.
    raw = command(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
        '-c:v', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'h264', '-'])
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}


def load_renderer():
    path = EP/'sources/render.py'
    spec = importlib.util.spec_from_file_location('papier_verified_renderer', path)
    renderer = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = renderer
    spec.loader.exec_module(renderer)
    return renderer


def audio_check(video):
    path = EP/'audio/mix.wav'
    with wave.open(str(path), 'rb') as source:
        n = source.getnframes()
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (48000, 2, 2)
        assert n == round(48000*DURATION), (n, 'WAV duration')
        pcm = np.frombuffer(source.readframes(n), '<i2').reshape(-1, 2)
    clipped = int(np.count_nonzero(np.abs(pcm.astype(np.int32)) >= 32767))
    assert clipped == 0, 'clipped PCM samples'
    reference = pcm.astype(np.float64)/32768.
    raw = command(['ffmpeg', '-v', 'error', '-xerror', '-i', str(video),
        '-map', '0:a:0', '-t', str(DURATION), '-ar', '48000', '-ac', '2',
        '-c:a', 'pcm_f32le', '-f', 'f32le', '-'])
    decoded = np.frombuffer(raw, '<f4').reshape(-1, 2)
    assert decoded.shape == reference.shape, (decoded.shape, reference.shape, 'AAC coverage')
    assert np.isfinite(decoded).all() and float(np.abs(decoded).max()) < .999, 'clipped or invalid decoded AAC'
    # Detect attaching an old or offset sound mix. Lossy AAC is not expected
    # to reproduce each PCM sample; correspondence is assessed over the signal.
    a, b = reference.ravel(), decoded.astype(np.float64).ravel()
    correlation = float(np.dot(a, b)/math.sqrt(float(np.dot(a, a))*float(np.dot(b, b))))
    relative_rmse = float(np.sqrt(np.mean((a-b)**2))/np.sqrt(np.mean(a*a)))
    assert correlation > .90, ('AAC does not match current WAV', correlation)
    def db(v):
        return round(20.*math.log10(v), 6) if v else None
    return {'wav_sha256': digest(path), 'duration_seconds': n/48000.,
            'sample_rate': 48000, 'channels': 2, 'bits': 16,
            'wav_clipped_samples': clipped,
            'wav_peak_dbfs': db(float(np.abs(reference).max())),
            'decoded_aac_peak_dbfs': db(float(np.abs(decoded).max())),
            'wav_vs_decoded_aac_correlation_without_offset': correlation,
            'wav_vs_decoded_aac_relative_rmse': relative_rmse,
            'first_and_last_wav_frame_silent': bool(not pcm[0].any() and not pcm[-1].any())}


def decoded_samples(video, indices):
    # A long left-associated sum exceeds libavutil's expression recursion
    # limit. A balanced tree selects the same indices at logarithmic depth.
    def expression(values):
        if len(values) == 1:
            return f'eq(n\\,{values[0]})'
        middle = len(values)//2
        return '('+expression(values[:middle])+'+'+expression(values[middle:])+')'
    select = 'select='+expression(indices)
    raw = command(['ffmpeg', '-v', 'error', '-xerror', '-threads', '2',
        '-filter_threads', '2', '-i', str(video),
        '-map', '0:v:0', '-vf', select, '-fps_mode', 'passthrough',
        '-threads', '2', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
    expected = len(indices)*W*H*3
    assert len(raw) == expected, ('unexpected decoded sample count', len(raw), expected)
    return np.frombuffer(raw, np.uint8).reshape(len(indices), H, W, 3)


def bbox_screen(rectangle, viewbox):
    x0, y0, x1, y1 = rectangle
    vx, vy, vw, vh = viewbox
    left, right = math.floor((x0-vx)*W/vw), math.ceil((x1-vx)*W/vw)
    top, bottom = math.floor((y0-vy)*H/vh), math.ceil((y1-vy)*H/vh)
    return [max(0, left), max(0, top), min(W, right), min(H, bottom)]



def source_checks():
    manifest=json.loads((EP/'controle/sources_final.json').read_text())
    frozen=manifest['sha256']
    assert frozen,'empty render freeze'
    for name,expected in frozen.items():
        assert digest(Path(name))==expected,(name,'source changed since final rendering')
    required=[EP/'sources'/n for n in ('animation.py','render.py','art.py','cooking_fx.py',
        'sink.py','mitten.py','costume.py','performance.py','jeu_visage.py','visage.py',
        'expressions.json','reference_animation.py','reference_performance.py',
        'reference_jeu_visage.py','reference_acting.py')]
    required += [EP/'chronologie.json',EP/'chronologie_reference_v25.json',EP/'assets/Nunito-wght.ttf']
    assert {str(p) for p in required}.issubset(frozen),'incomplete visual-source freeze'
    assert digest(ROOT/'mou_rig.py')==RIG_SHA,'canonical rig changed'
    protected=json.loads((EP/'controle/baseline_protegee.json').read_text())
    protection={}
    for name,expected in protected.items():
        path=ROOT/name
        if path.is_file():
            actual=digest(path);assert actual==expected,(name,'protected baseline changed')
            protection[name]={'sha256':actual,'present_and_unchanged':True}
        else:
            protection[name]={'expected_sha256':expected,'present_and_unchanged':None,
                'note':'Historical media may be excluded from a portable source archive.'}
    reference=json.loads((EP.parent/'test_remuer/controle/audit_structure.json').read_text())
    decor=reference['decor_files_unchanged']
    for name,expected in decor.items():assert digest(EP.parent/'decor'/name)==expected,(name,'approved decor changed')
    sound=json.loads((EP/'controle/audit_son.json').read_text())
    provenance=json.loads((EP/'audio/provenance.json').read_text())
    source_hashes=sound['source_hashes']
    assert set(source_hashes)=={'son.py','music.py','foley.py'},'incomplete audio source freeze'
    for name,expected in source_hashes.items():
        assert digest(EP/'sources'/name)==expected,(name,'audio source changed')
    assert source_hashes['son.py']==provenance['source_sha256'],'audio provenance source mismatch'
    assert source_hashes['music.py']==provenance['music_source_sha256'],'music provenance source mismatch'
    assert source_hashes['foley.py']==provenance['foley_source_sha256'],'foley provenance source mismatch'
    assert digest(EP/'audio/mix.wav')==sound['mix_sha256'],'sound audit mix mismatch'
    assert digest(EP/'chronologie.json')==sound['chronologie_sha256'],'sound timeline mismatch'
    return {'rig_sha256':RIG_SHA,'render_frozen_sources':frozen,'approved_decor_unchanged':decor,
        'protected_baseline':protection,'sound_source_sha256':source_hashes['son.py'],
        'all_sound_source_hashes':source_hashes,
        'sound_audit_mix_sha256':sound['mix_sha256']}


def affine_matrix(text):
    """SVG transform list, composed in SVG local-to-parent order."""
    result=np.eye(3)
    residue=re.sub(r'([A-Za-z]+)\s*\(([^)]*)\)','',text).strip(' ,\t\n')
    assert not residue,('unparsed SVG transform',text)
    for name,raw in re.findall(r'([A-Za-z]+)\s*\(([^)]*)\)',text):
        values=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?',raw)]
        m=np.eye(3)
        if name=='matrix':
            assert len(values)==6
            a,b,c,d,e,f=values;m=np.array([[a,c,e],[b,d,f],[0.,0.,1.]])
        elif name=='translate':
            assert len(values) in (1,2);m[0,2]=values[0];m[1,2]=values[-1] if len(values)==2 else 0.
        elif name=='scale':
            assert len(values) in (1,2);m[0,0]=values[0];m[1,1]=values[-1]
        elif name=='rotate':
            assert len(values) in (1,3)
            theta=math.radians(values[0]);c,s=math.cos(theta),math.sin(theta)
            m=np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
            if len(values)==3:
                x,y=values[1:];m[0,2]=x-c*x+s*y;m[1,2]=y-s*x-c*y
        else:raise AssertionError(('unsupported SVG transform',name))
        result=result@m
    assert np.isfinite(result).all()
    return result


def native_matrix(state):
    return affine_matrix(state.get('performance_affine_svg',''))


def world_from_native(point,state,matrix=None):
    matrix=native_matrix(state) if matrix is None else matrix
    ax,ay,scale=map(float,state['actor_transform'])
    native=np.array([(point[0]-ax)/scale,(point[1]-ay)/scale,1.])
    x,y,_=matrix@native
    return ax+scale*x,ay+scale*y


def performance_rectangle(rectangle,state):
    x0,y0,x1,y1=rectangle
    points=[world_from_native(p,state) for p in ((x0,y0),(x1,y0),(x0,y1),(x1,y1))]
    return min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)


def actor_signature(state):
    fields={name:state.get(name) for name in ('actor_transform','torso','arms',
        'grounded_feet','performance_affine_svg','hands')}
    return hashlib.sha256(json.dumps(fields,sort_keys=True,allow_nan=False).encode()).hexdigest()


def structure_checks(renderer):
    counts=[];stock=[];max_contact=0.;max_metadata_difference=0.;max_recomputed=0.
    min_area,max_area=math.inf,-math.inf
    stage_max={'opening':0.,'middle':0.,'last_third':0.}
    stage_at={};grounded=set();foot_reference={};foot_max_error=0.
    held=[];steam=set();sink_observations=[];nonsink=0
    actual_scales=[];constraints=0;native_contours=0
    for index in range(NFRAMES):
        t=index/FPS;s=renderer.animation.scene_state(t)
        svg=renderer.svg_at(t);root=ET.fromstring(svg)
        ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids)==len(set(ids)),(t,'duplicate SVG ids')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',svg)),(t,'missing SVG mask/clip reference')
        sink=s['shot']=='sink'
        expected_hands=1 if sink else 2
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter())==expected_hands,(t,'hand markers')
        for key in ('apron','chef-hat'):
            assert sum(e.attrib.get('data-costume')==key for e in root.iter())==int(not sink),(t,key)
        assert sum(e.attrib.get('id')=='mouth' for e in root.iter())==int(not sink),(t,'mouth markers')
        assert math.isclose(float(s.get('production_time',t)),t,abs_tol=1e-8),(t,'production clock')
        counts.append(int(s['bin_count']));stock.append(float(s['roll']['remaining']))
        for side,p in s['hands'].items():assert len(p)==2 and all(math.isfinite(v) for v in p),(t,side,'invalid hand')
        if sink:
            g=renderer.sink.geometry_at(t,s,renderer.animation)
            assert g['water_on']==(s['production_cycle']['water'][0]<=t<s['production_cycle']['water'][1]),(t,'water state')
            if g['phase']=='rinse_tip':
                hx,hy=g['tip'];wx,wy=g['wrist'];l,top,r,b=g['jet_bounds']
                assert l-5.<hx<r+5. and top<hy<b,(t,'fingertips miss jet',g['tip'])
                assert not(l<=wx<=r and top<=wy<=b),(t,'wrist in water',g['wrist'])
                if not any(o['cycle']==g['cycle'] for o in sink_observations):
                    sink_observations.append({'cycle':g['cycle'],'time':t,'tip':g['tip'],'wrist':g['wrist'],
                        'jet_bounds':g['jet_bounds'],'thumb_bounds':g['thumb_bounds'],'native_hand_scale':g['native_scale']})
            continue
        nonsink+=1
        foot=s.get('grounded_feet','')
        assert 'id="foot-l"' in foot and 'id="foot-r"' in foot,(t,'missing grounded native feet')
        parents={child:parent for parent in root.iter() for child in parent}
        for foot_id,cx in (('foot-l',151.),('foot-r',252.)):
            node=next(e for e in root.iter() if e.attrib.get('id')==foot_id)
            grounded.add((foot_id,hashlib.sha256(ET.tostring(node)).hexdigest()))
            ancestors=[];ancestor=node
            while ancestor is not None:
                ancestors.append(ancestor);ancestor=parents.get(ancestor)
            assert not any(e.attrib.get('data-performance')=='upper-body' for e in ancestors),(t,foot_id,'foot follows body squash')
            world=np.eye(3)
            for ancestor in reversed(ancestors):
                if ancestor.attrib.get('transform'):world=world@affine_matrix(ancestor.attrib['transform'])
            anchor=world@np.array([cx,437.,1.])
            if foot_id not in foot_reference:foot_reference[foot_id]=anchor[:2].tolist()
            error=math.dist(anchor[:2],foot_reference[foot_id]);foot_max_error=max(foot_max_error,error)
            assert error<.003,(t,foot_id,'world foot anchor drifts',error)
        matrix=native_matrix(s)
        determinant=float(np.linalg.det(matrix[:2,:2]));min_area=min(min_area,determinant);max_area=max(max_area,determinant)
        assert determinant>0.,(t,'reflected/degenerate body')
        assert .85<determinant<1.15,(t,'body area drift',determinant)
        singular=np.linalg.svd(matrix[:2,:2],compute_uv=False)
        compression=1.-float(min(singular))
        stage='opening' if t<8.75 else 'middle' if t<38.*2./3. else 'last_third'
        if compression>stage_max[stage]:stage_max[stage]=compression;stage_at[stage]=t
        actual_scales.append({'frame':index,'time':t,'singular_scales':singular.tolist(),'area':determinant})
        for side,meta in s.get('arm_meta',{}).items():
            if all(key in meta for key in ('hips','clasp')):
                # Compare the actual emitted mitten/arm contour with the
                # canonical rig, outside the approved local shoulder join.
                canonical=ET.fromstring(renderer.animation._arm(side,meta['hips'],meta['clasp']))
                expected=next(e for e in canonical.iter() if e.attrib.get('data-part')=='hand')
                actual=next(e for e in root.iter() if e.attrib.get('data-part')=='hand'
                    and e.attrib.get('data-side')==side)
                shoulder=renderer.animation.SHOULDERS[side]
                def distal_points(element):
                    points=[tuple(map(float,p)) for p in re.findall(r'(-?[\d.]+) (-?[\d.]+)',element.attrib['d'])]
                    return [p for p in points if math.dist(p,shoulder)>24.]
                expected_points,actual_points=distal_points(expected),distal_points(actual)
                assert len(expected_points)==len(actual_points),(t,side,'native contour size')
                assert all(math.dist(a,b)<.003 for a,b in zip(expected_points,actual_points)),(t,side,'native mitten/arm contour changed')
                native_contours+=1
            error=float(meta.get('contact_error',0.));max_contact=max(max_contact,error)
            assert math.isfinite(error) and error<.15,(t,side,'grip solve miss',error)
            stored=meta.get('hand',s['hands'][side]);delta=math.dist(stored,s['hands'][side])
            max_metadata_difference=max(max_metadata_difference,delta)
            assert delta<1e-5,(t,side,'hand state disagreement',delta)
            if all(key in meta for key in ('hips','clasp','rotation')) and meta.get('reflect_axis') is None:
                raw=renderer.animation.world_grip(side,meta['hips'],meta['clasp'],meta['rotation'],
                    s['actor_transform'],meta.get('grip_depth',16.))
                actual=world_from_native(raw,s,matrix)
                delta=math.dist(actual,s['hands'][side]);max_recomputed=max(max_recomputed,delta);constraints+=1
                assert delta<.15,(t,side,'emitted native controls do not reach hand',delta)
        if t>=TIMELINE['final_hold'][0]:
            held.append(actor_signature(s))
            steam.add(renderer.cooking_fx.steam_svg(t,s))
    assert counts==sorted(counts) and counts[-1]==3,(counts[-1],'bin persistence')
    assert stock==sorted(stock,reverse=True),'roll stock regrows'
    assert stock[0]==1. and stock[-1]==0.,(stock[0],stock[-1],'roll incomplete')
    assert len(sink_observations)==4,'not all four fingertip washes observed'
    assert len(grounded)==2,('native foot geometry changes',len(grounded))
    assert len(held)==18 and len(set(held))==1,('final body hold',len(held),len(set(held)))
    assert len(steam)>1,'final smoke unexpectedly frozen'
    assert stage_max['opening']>=.03,'opening elasticity absent'
    assert stage_max['middle']>=.06,'middle elasticity absent'
    assert stage_max['last_third']>=.18,'late cartoon deformation absent'
    assert stage_max['last_third']>stage_max['opening']+.07,'elasticity does not escalate'
    return {'frames_examined':NFRAMES,'nonsink_actor_frames':nonsink,
        'unique_ids_and_clip_references':True,'wide_hand_markers':2,'sink_hand_markers':1,
        'final_bin_count':3,'final_discarded_paper_count':4,'roll_stock_first_last':[stock[0],stock[-1]],
        'max_reported_contact_error_px':max_contact,'max_hand_metadata_disagreement_px':max_metadata_difference,
        'native_world_grips_recomputed':constraints,'max_recomputed_world_hand_error_px':max_recomputed,
        'native_arm_and_mitten_contours_compared_outside_24px_root':native_contours,
        'body_affine_area_min_max':[min_area,max_area],'stage_max_compression':stage_max,'stage_peak_times':stage_at,
        'native_foot_geometry_signatures':len(grounded),'world_foot_reference_anchors':foot_reference,
        'max_world_foot_anchor_drift_px':foot_max_error,'feet_excluded_from_upper_body_affine':True,
        'final_actor_hold_frames':len(held),
        'distinct_steam_fragments_during_hold':len(steam),'fingertip_washes':sink_observations,
        'actual_affine_samples':actual_scales,
        'limits':'Structural/numeric checks do not prove facial-emotion recognition, artistic success or natural sound.'}


def fresh_image_checks(renderer,video):
    indices=sorted({min(NFRAMES-1,round(t*FPS)) for t in SAMPLE_TIMES})
    actual_frames=decoded_samples(video,indices)
    results=[];failures=[]
    for index,actual in zip(indices,actual_frames):
        t=index/FPS;svg=renderer.svg_at(t).encode()
        png=cairosvg.svg2png(bytestring=svg,output_width=W,output_height=H)
        fresh=np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))
        difference=np.abs(fresh.astype(np.int16)-actual.astype(np.int16))
        full_error=float(difference.mean())
        if full_error>=MEAN_ERROR_LIMIT:failures.append({'frame':index,'roi':'full_frame','mean_error':full_error})
        s=renderer.animation.scene_state(t)
        vb=tuple(map(float,ET.fromstring(svg).attrib['viewBox'].split()))
        regions={'food':(190.,1240.,405.,1350.),'bin_and_floor':(40.,1360.,370.,1845.),
            'carrot_knife':(450.,1160.,820.,1415.),'paper_roll':(780.,1060.,965.,1368.)}
        if s['shot']=='sink':
            g=renderer.sink.geometry_at(t,s,renderer.animation);hx,hy=g['tip'];wx,wy=g['wrist']
            regions={'basin':g['basin_bounds'],'fingertips':(hx-25.,hy-25.,hx+35.,hy+35.),
                'dry_wrist':(wx-25.,wy-25.,wx+25.,wy+25.),'rounded_thumb':g['thumb_bounds']}
        else:
            ax,ay,scale=s['actor_transform']
            for name,(x0,y0,x1,y1) in {'face':(115.,145.,292.,343.),'hat':(170.,45.,310.,145.),
                'left_root':(75.,265.,130.,325.),'right_root':(270.,265.,325.,325.)}.items():
                regions[name]=performance_rectangle((ax+x0*scale,ay+y0*scale,ax+x1*scale,ay+y1*scale),s)
            for side,(hx,hy) in s['hands'].items():regions['hand_'+side]=(hx-75.,hy-75.,hx+75.,hy+75.)
        if t<renderer.CAPTION_END:regions['caption']=(52.,120.,488.,282.)
        measured={}
        for name,rectangle in regions.items():
            box=bbox_screen(rectangle,vb);left,top,right,bottom=box
            if right-left<12 or bottom-top<12:measured[name]={'visible':False};continue
            error=float(difference[top:bottom,left:right].mean())
            measured[name]={'visible':True,'pixel_bbox':box,'mean_abs_rgb_error_0_255':error}
            if error>=MEAN_ERROR_LIMIT:failures.append({'frame':index,'roi':name,'mean_error':error})
        results.append({'frame':index,'time_seconds':t,'shot':s['shot'],'phase':s.get('phase'),
            'fresh_svg_sha256':hashlib.sha256(svg).hexdigest(),'fresh_png_sha256':hashlib.sha256(png).hexdigest(),
            'full_frame_mean_abs_rgb_error_0_255':full_error,'regions':measured})
    return {'samples':results,'failures':failures,'threshold_mean_abs_rgb_error_0_255':MEAN_ERROR_LIMIT,
        'method':'Actual decoded final MP4 vs fresh direct CairoSVG; no PNG/cache lookup.'}


def main(default_report=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,default=EP/'MOU_Encore_une_feuille.mp4')
    parser.add_argument('--silent',type=Path,default=EP/'MOU_Encore_une_feuille_muette.mp4')
    parser.add_argument('--report',type=Path,default=default_report or EP/'controle/audit_final.json')
    args=parser.parse_args()
    args.video,args.silent,args.report=(p.resolve() for p in (args.video,args.silent,args.report))
    report={'status':'in_progress','scope':'V26 final outputs and all912 scene states',
        'dimensions':[W,H],'fps':FPS,'duration_seconds':DURATION,'expected_frames':NFRAMES,
        'limits':'No claim of hearing, continuous viewing, public recognition of emotions, comic success or user approval.'}
    atomic_json(args.report,report)
    try:
        assert args.video.is_file() and args.silent.is_file(),'render both final videos before QA'
        tracked=list((EP/'sources').glob('*.py'))+list((EP/'sources').glob('*.json'))
        tracked += [EP/'chronologie.json',EP/'chronologie_reference_v25.json',ROOT/'mou_rig.py']
        tracked += [p for p in (EP/'assets').rglob('*') if p.is_file()]
        before={str(path):digest(path) for path in tracked}
        report['source_integrity']=source_checks()
        report['sound_video']=check_video(args.video,True)
        report['silent_video']=check_video(args.silent,False)
        sound_bits,silent_bits=bitstream_digest(args.video),bitstream_digest(args.silent)
        assert sound_bits==silent_bits,'sound/mute compressed video differs'
        report['identical_compressed_video_bitstreams']=sound_bits
        report['audio']=audio_check(args.video)
        renderer=load_renderer()
        report['structure']=structure_checks(renderer)
        report['uncached_frame_checks']=fresh_image_checks(renderer,args.video)
        assert not report['uncached_frame_checks']['failures'],report['uncached_frame_checks']['failures']
        assert before=={str(path):digest(path) for path in tracked},'source changed during QA'
        report['tested_sources_sha256']=before;report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        atomic_json(args.report,report)
        raise
    atomic_json(args.report,report)
    revision=EP/'controle/audit_revision_v26.json'
    if revision.resolve()!=args.report:atomic_json(revision,report)
    print(json.dumps({'status':report['status'],'report':str(args.report),'frames':NFRAMES,
        'duration_seconds':DURATION,'uncached_samples':len(report['uncached_frame_checks']['samples']),
        'audio_correlation':report['audio']['wav_vs_decoded_aac_correlation_without_offset'],
        'elasticity_actual_stage_peaks':report['structure']['stage_max_compression'],
        'final_actor_hold_frames':report['structure']['final_actor_hold_frames']},ensure_ascii=False))


if __name__=='__main__':main()
