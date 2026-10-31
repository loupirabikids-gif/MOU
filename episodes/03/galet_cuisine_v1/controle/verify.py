"""Independent emitted-geometry, encoded-picture and audio checks.

Run only after the coordinator announces the producer freeze and final exports.
Contact checks isolate the shapes actually emitted, not a producer success flag.
No listening, continuous viewing or artistic approval is implied by a pass.
"""
from __future__ import annotations

import argparse
import concurrent.futures
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
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
SOURCE=EP/'sources'
TIMELINE=json.loads((EP/'chronologie.json').read_text())
FPS=int(TIMELINE['fps']);DURATION=float(TIMELINE['duration'])
DIMENSIONS=tuple(TIMELINE['dimensions'])
COUNT=round(FPS*DURATION)
IMAGE_TIMES=(0.,1.5,2.9,3.85,4.3,5.3,6.1,6.7,7.8,8.4,9.25,9.4,9.98,
             10.6,11.7,12.9,13.4,14.62,15.3,15.58,16.1,16.9,18.2,19.18,
             19.85,20.35,21.4,22.15,23.7,24.9,25.45,26.2,26.7,28.25,
             28.5,29.04,29.4,29.9,30.8,31.83,32.8,33.7,34.5,35.5,37.5)


def digest(path):
    with Path(path).open('rb')as src:return hashlib.file_digest(src,'sha256').hexdigest()


def atomic_json(path,value):
    path=Path(path);temporary=path.with_name('.'+path.name)
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def command(args):return subprocess.check_output(args)


def module(path,name):
    sys.path.insert(0,str(Path(path).resolve().parent))
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def isolate(svg,ids,dimensions=None,world=False):
    selected=set(ids);root=ET.fromstring(svg)
    present={n.get('id')for n in root.iter()}
    missing=selected-present
    assert not missing,('Missing SVG parts',sorted(missing))
    def prune(node):
        tag=node.tag.rsplit('}',1)[-1]
        if tag in ('defs','style')or node.get('id')in selected:return copy.deepcopy(node)
        result=ET.Element(node.tag,node.attrib)
        for child in node:
            kept=prune(child)
            if kept is not None:result.append(kept)
        return result if len(result)or node is root else None
    result=prune(root)
    if world:result.set('viewBox','0 0 1080 1920')
    if dimensions:
        result.set('width',str(dimensions[0]));result.set('height',str(dimensions[1]))
    return ET.tostring(result,encoding='unicode')


def rgba(svg,dimensions=DIMENSIONS):
    png=cairosvg.svg2png(bytestring=svg.encode(),output_width=dimensions[0],output_height=dimensions[1])
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))


def mask(svg,ids,dimensions=DIMENSIONS,world=False):
    return rgba(isolate(svg,ids,dimensions,world),dimensions)[:,:,3]>=64


def bounds(binary):
    yy,xx=np.nonzero(binary)
    return None if not len(xx)else[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]


def boundary(binary):
    inner=binary.copy()
    for axis in (0,1):inner&=np.roll(binary,1,axis)&np.roll(binary,-1,axis)
    inner[0]=inner[-1]=False;inner[:,0]=inner[:,-1]=False
    return np.argwhere(binary&~inner).astype(float)


def gap(a,b):
    if np.any(a&b):return 0.
    aa,bb=boundary(a),boundary(b)
    assert len(aa)and len(bb),'An intended contact component is outside its view'
    result=float('inf')
    for start in range(0,len(aa),256):
        delta=aa[start:start+256,None,:]-bb[None,:,:]
        result=min(result,float(np.sum(delta*delta,axis=2).min()))
    return result**.5


def canonical(node):
    return {'tag':node.tag.rsplit('}',1)[-1],
            'attributes':dict(sorted(node.attrib.items())),
            'children':[canonical(child)for child in node]}


def signature(node):
    return hashlib.sha256(json.dumps(canonical(node),sort_keys=True).encode()).hexdigest()


def element_signature(svg,ids):
    root=ET.fromstring(svg);lookup={n.get('id'):n for n in root.iter()if n.get('id')}
    return {key:signature(lookup[key])for key in ids}


def svg_transform(text):
    output=np.eye(3)
    for name,raw in re.findall(r'([a-zA-Z]+)\(([^)]*)\)',text or''):
        values=[float(v)for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',raw)]
        m=np.eye(3)
        if name=='translate':m[:2,2]=(values[0],values[1]if len(values)>1 else 0.)
        elif name=='scale':m[0,0]=values[0];m[1,1]=values[1]if len(values)>1 else values[0]
        elif name=='rotate':
            angle=math.radians(values[0]);c,s=math.cos(angle),math.sin(angle)
            m[:2,:2]=((c,-s),(s,c))
            if len(values)==3:
                pivot=np.array(values[1:3]);m[:2,2]=pivot-m[:2,:2]@pivot
        elif name=='matrix':
            a,b,c,d,e,f=values;m=np.array(((a,c,e),(b,d,f),(0.,0.,1.)))
        else:raise AssertionError(('Unsupported emitted transform',name))
        output=output@m
    return output


def video_probe(path,audio_expected):
    probe=json.loads(command(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    video=[s for s in probe['streams']if s['codec_type']=='video']
    assert len(video)==1,(path,'Expected a single video stream')
    v=video[0]
    assert v['codec_name']=='h264'
    assert[v['width'],v['height']]==list(DIMENSIONS),(path,'Wrong image dimensions')
    assert v['r_frame_rate']==f'{FPS}/1'and int(v['nb_frames'])==COUNT
    assert abs(float(probe['format']['duration'])-DURATION)<.05
    sound=[s for s in probe['streams']if s['codec_type']=='audio']
    assert bool(sound)==audio_expected
    if sound:
        assert len(sound)==1 and int(sound[0]['sample_rate'])==48000 and sound[0]['channels']==2
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(path),'-f','null','-'],check=True)
    return probe


def h264_sha(path):
    return hashlib.sha256(command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0',
                                  '-c:v','copy','-f','h264','-'])).hexdigest()


def decoded_frames(video,indices):
    selected='select='+'+'.join(f'eq(n\\,{i})'for i in indices)
    raw=command(['ffmpeg','-v','error','-threads','2','-filter_threads','2','-i',str(video),
                 '-vf',selected,'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'])
    w,h=DIMENSIONS;array=np.frombuffer(raw,np.uint8).reshape(len(indices),h,w,3)
    return dict(zip(indices,array))


def component_contact(svg,a,b,maximum=3.,world=False):
    ma,mb=mask(svg,a,world=world),mask(svg,b,world=world)
    measured=gap(ma,mb)
    assert measured<=maximum,('Rendered contact gap',a,b,measured)
    return {'first':a,'second':b,'gap_pixels':measured,
            'first_bounds':bounds(ma),'second_bounds':bounds(mb)}


def identify_emitted_fragment(svg,fragment,label):
    """Label an anonymous emitted prop for mask isolation without redrawing it."""
    root=ET.fromstring(svg);expected=signature(ET.fromstring(fragment))
    matches=[n for n in root.iter()if signature(n)==expected]
    assert len(matches)==1,('Anonymous prop not uniquely found in actual SVG',label,len(matches))
    matches[0].set('id',label)
    return ET.tostring(root,encoding='unicode')


def gross_face_worker(item):
    index,svg=item;tree=ET.fromstring(svg)
    ids={n.get('id')for n in tree.iter()}
    if 'eye-white-l'not in ids:return {'frame':index,'actor_visible':False}
    dimensions=(270,480)
    hands=mask(svg,['hand-left','hand-right'],dimensions)
    eyes=mask(svg,['eye-white-l','eye-white-r'],dimensions)
    mouth=mask(svg,['mouth'],dimensions)
    overlap_eyes=int(np.count_nonzero(hands&eyes))
    overlap_mouth=int(np.count_nonzero(hands&mouth))
    assert overlap_eyes<=1,(index,'Mittens cross the eyes at phone scale',overlap_eyes)
    assert overlap_mouth<=1,(index,'Mittens cross the mouth at phone scale',overlap_mouth)
    return {'frame':index,'actor_visible':True,'eye_overlap_pixels_270':overlap_eyes,
            'mouth_overlap_pixels_270':overlap_mouth}


def check_audio(video,wav_path):
    with wave.open(str(wav_path),'rb')as src:
        sr=src.getframerate();channels=src.getnchannels();width=src.getsampwidth();count=src.getnframes()
        assert(sr,channels,width)==(48000,2,2)
        assert count==round(sr*DURATION)
        pcm=np.frombuffer(src.readframes(count),'<i2').reshape(-1,2)
    clipping=int(np.count_nonzero(np.abs(pcm.astype(np.int32))>=32767));assert clipping==0
    silence=[]
    for a,b in ((32.,32.5),(37.25,38.)):
        section=pcm[round(a*sr):round(b*sr)];nonzero=int(np.count_nonzero(section))
        assert nonzero==0,('Required PCM silence contains samples',a,b,nonzero)
        silence.append({'start':a,'end':b,'nonzero_samples':nonzero})
    raw=command(['ffmpeg','-v','error','-i',str(video),'-map','0:a:0','-ar','48000',
                 '-ac','2','-f','f32le','-'])
    decoded=np.frombuffer(raw,'<f4').reshape(-1,2)
    assert len(decoded)>=len(pcm)-1024
    length=min(len(decoded),len(pcm));reference=pcm[:length].astype(float)/32768.;decoded=decoded[:length].astype(float)
    correlation=float(np.corrcoef(reference.ravel(),decoded.ravel())[0,1])
    assert correlation>.95,('AAC does not correspond closely to source WAV',correlation)
    windows=[]
    for a,b in ((.4,1.),(4.05,4.8),(6.35,6.9),(9.3,10.1),(23.4,24.),(28.4,29.1)):
        start,end=round(a*sr),round(b*sr)
        x=reference[start:end].mean(axis=1);ener=float(np.dot(x,x))
        if ener<1e-9:continue
        scores=[]
        for lag in range(-48,49):
            y=decoded[start+lag:end+lag].mean(axis=1)
            denom=float(np.dot(y,y)*ener)**.5
            scores.append(float(np.dot(x,y)/denom)if denom else 0.)
        best=int(np.argmax(scores))-48
        assert abs(best)<=2,(a,b,'Global audio timing shift',best,max(scores))
        windows.append({'start':a,'end':b,'best_lag_samples':best,'correlation':max(scores)})
    bank=check_audio_cues(pcm,sr)
    return {'wav_sha256':digest(wav_path),'sample_rate':sr,'channels':channels,'frames':len(pcm),
            'clipped_samples':clipping,'peak_dbfs':20.*math.log10(max(1.,float(np.abs(pcm.astype(np.int32)).max()))/32768.),
            'aac_wav_correlation':correlation,'zero_lag_windows':windows,'exact_pcm_silences':silence,
            'independent_cue_reconstruction':bank,
            'limits':'Signal identity and timing only; no listening or perceived-balance validation.'}


def read_pcm(path):
    with wave.open(str(path),'rb')as src:
        assert(src.getframerate(),src.getnchannels(),src.getsampwidth())==(48000,2,2)
        return np.frombuffer(src.readframes(src.getnframes()),'<i2').reshape(-1,2).copy()


def written_energy_peak(data,sr):
    # Fixed definition in the published sound contract: maximum centred8ms RMS.
    energy=np.mean((data.astype(np.float64)/32768.)**2,axis=1)
    width=min(len(data),round(.008*sr));integral=np.r_[0.,np.cumsum(energy)]
    windows=(integral[width:]-integral[:-width])/width
    return int(np.argmax(windows)+width//2)


def check_audio_cues(pcm,sr):
    metadata=json.loads((EP/'audio/events.json').read_text())
    assert metadata['motion_sync_status']=='measured_new_character','Paper effects still use provisional timing'
    assert metadata['mix_sha256']==digest(EP/'audio/mix.wav')
    assert metadata['vocal_event_count']==0
    audio_sources={'son.py':digest(SOURCE/'son.py'),
                   'input_bank.json':digest(EP/'audio/input_bank.json'),
                   'chronologie.json':digest(EP/'chronologie.json')}
    assert metadata['source_hashes']==audio_sources,'Sound metadata refers to older source code or timeline'
    events=metadata['events'];assert len(events)==metadata['event_count']
    reconstructed=np.zeros_like(pcm,dtype=np.int64);timed=[];whistles=[]
    for event in events:
        path=EP/'audio'/event['file'];assert digest(path)==event['sha256']
        source_path=EP/'audio'/event['source_file']
        assert digest(source_path)==event['source_sha256'],(event['name'],'Active source cue changed')
        data=read_pcm(path);start=int(event['start_sample'])
        assert start==round(float(event['start'])*sr)
        assert len(data)==int(event['samples'])and not event['voice']
        n=min(len(data),len(pcm)-start);assert n>0
        reconstructed[start:start+n]+=data[:n].astype(np.int64)
        measured=written_energy_peak(data,sr)
        absolute=(start+measured)/sr
        assert abs(absolute-event['energy_peak_seconds'])<=1./sr,(event['name'],'Cue energy metadata does not match actual written PCM')
        target=event.get('sync',{}).get('target_seconds')
        if target is not None:
            error=absolute-float(target)
            assert abs(error)<.002,(event['name'],'Cue RMS maximum misses its stated action target',error)
            timed.append({'name':event['name'],'kind':event['kind'],'target_seconds':target,
                          'written_energy_peak_seconds':absolute,'error_seconds':error})
        if event['kind']=='whistle':
            assert float(event['start'])+float(event['duration'])<TIMELINE['cycles'][0]['sink'][0]
            whistles.append({'name':event['name'],'start':event['start'],'duration':event['duration']})
    assert np.array_equal(reconstructed,pcm.astype(np.int64)),'Delivered cues do not reconstruct the actual mix'
    stem_sum=np.zeros_like(pcm,dtype=np.int64)
    for item in metadata['stems']:
        path=EP/'audio'/item['file'];assert digest(path)==item['sha256']
        data=read_pcm(path);assert data.shape==pcm.shape
        stem_sum+=data.astype(np.int64)
    assert np.array_equal(stem_sum,pcm.astype(np.int64)),'Delivered stems do not reconstruct the actual mix'
    motion=json.loads((EP/'audio/motion_sync.json').read_text())
    expected_hashes={name:digest(SOURCE/name)for name in('animation.py','character.py','reference_character.py')}
    assert motion['source_hashes']==expected_hashes,'Paper sound timings were measured on older trajectories'
    return {'events_verified':len(events),'voice_events':0,'opening_whistle_events':whistles,
            'cue_sum_equals_mix_pcm':True,'stem_sum_equals_mix_pcm':True,
            'energy_targets_verified':timed,'paper_motion_source_sha256':expected_hashes,
            'audio_source_sha256':audio_sources,
            'limits':'RMS anchors are numerical timing markers, not audibility or perceived-synchronization tests.'}


def check_sink(renderer,character,svg_at):
    sink=getattr(renderer,'sink',None)or sys.modules.get('sink_galet')
    assert sink is not None,'Sink module is not exposed by the local renderer'
    rows=[]
    for cycle in TIMELINE['cycles']:
        all_states=[]
        start,end=cycle['sink']
        for i in range(math.ceil(start*FPS),math.ceil(end*FPS)):
            t=i/FPS;g=sink.geometry_at(t,cycle);h=g['hand']
            actual=character.point(h,'tip')
            assert math.dist(actual,g['tip'])<1e-5
            assert math.dist(actual,g['target_tip'])<1e-5
            assert abs(h['scale']-.70)<1e-9
            if g['phase']in('open_tap','close_tap'):
                assert math.dist(actual,g['tap_target'])<1e-5,(t,'No fingertip/lever contact')
            if g['phase']=='rinse_tip':
                assert g['water_on']
                px,py=character.point(h,'grip')
                assert px>116.+8.,(t,'Palm enters the main water stream',px,py)
                assert 88.<actual[0]<116. and 1115.<actual[1]<1167.
            all_states.append({'frame':i,'phase':g['phase'],'tip':actual,'lever':g['lever'],'water':g['water_on']})
        wash_mid=sum(cycle['wash'])/2.
        raster_t=round(wash_mid*FPS)/FPS;svg=svg_at(raster_t)
        jet=mask(svg,['lavabo-jet-primary']);hand=mask(svg,['hand-left'])
        intersection=int(np.count_nonzero(jet&hand));hand_area=int(hand.sum())
        assert intersection>0,(raster_t,'No visible tip rinse contact')
        assert intersection/hand_area<.30,(raster_t,'Too much of the mitten is immersed',intersection,hand_area)
        # Read an actual open/close state and measure emitted shapes, not just anchors.
        taps=[]
        for phase in('open_tap','close_tap'):
            samples=[x for x in all_states if x['phase']==phase];assert samples,(cycle['id'],phase)
            selected=samples[len(samples)//2];t=selected['frame']/FPS
            taps.append({'phase':phase,'time':t,**component_contact(svg_at(t),['hand-left'],['commande-robinet'])})
        rows.append({'cycle':cycle['id'],'frames':len(all_states),'tap_contacts':taps,
                     'rinse_time':raster_t,'wet_intersection_pixels':intersection,
                     'wet_fraction_of_mitten':intersection/hand_area,
                     'hand_bounds':bounds(hand),'jet_bounds':bounds(jet)})
    return rows


def check_tools(animation,character,art,svg_at):
    rows=[]
    for t in(.75,1.5):
        s=animation.scene_state(t);assert s['spoon_held']
        actual=character.point(s['hands']['left'],'grip')
        assert math.dist(actual,s['spoon']['grip'])<1e-4
        rows.append({'time':t,'action':'stir',**component_contact(svg_at(t),['hand-left'],['cuillere-cuisine'])})
    for index,t in enumerate(TIMELINE['carrot']['cut_times']):
        s=animation.scene_state(t);carrot=s['carrot'];assert carrot['knife_held']
        actual=character.point(s['hands']['left'],'grip')
        assert math.dist(actual,carrot['knife_grip'])<1e-4
        blade=art.knife_edge_point(carrot['knife_grip'],carrot['knife_tip'])
        expected_cut=(carrot['body'][0]+20.*(index+1),carrot['body'][1])
        blade_error=math.dist(blade,expected_cut)
        assert blade_error<.03,(t,'Actual cutting belly misses the carrot cut line',blade,expected_cut)
        contact=component_contact(svg_at(t),['couteau-carotte'],['carotte-planche'])
        rows.append({'time':t,'action':'carrot_cut','actual_blade_belly':blade,
                     'expected_cut_line':expected_cut,'blade_error_world_pixels':blade_error,
                     'hand_grip':actual,**contact})
        rows.append({'time':t,'action':'knife_hold',
                     **component_contact(svg_at(t),['hand-left'],['couteau-carotte'])})
        rows.append({'time':t,'action':'carrot_stabilizer',
                     **component_contact(svg_at(t),['hand-right'],['carotte-planche'])})
    for t in(15.22,15.34):
        s=animation.scene_state(t);assert s['tomato_held']and s['tomato']is not None
        actual=character.point(s['hands']['left'],'thumb');tomato=s['tomato']
        assert math.dist(actual,tomato[:2])<1e-4,(t,'Tomato slips from the emitted thumb')
        svg=identify_emitted_fragment(svg_at(t),art.tomato_svg(*tomato),'qa-held-tomato')
        rows.append({'time':t,'action':'tomato_hold','actual_thumb':actual,
                     **component_contact(svg,['hand-left'],['qa-held-tomato'])})
    t=19.82;s=animation.scene_state(t);thumb=character.point(s['hands']['left'],'thumb')
    assert math.dist(thumb,(s['salt']['bowl'][0],s['salt']['bowl'][1]-7.))<.001
    rows.append({'time':t,'action':'salt_pick','actual_thumb':thumb,
                 **component_contact(svg_at(t),['hand-left'],['coupelle-sel'])})
    t=20.30;s=animation.scene_state(t);thumb=character.point(s['hands']['left'],'thumb')
    assert math.dist(thumb,s['salt']['pinch_tip'])<1e-4
    root=ET.fromstring(svg_at(t));emitted=[]
    for node in root.iter():
        if node.get('data-grain')!='fall':continue
        born=float(node.get('data-emission-time'))
        hand=animation.scene_state(born)['hands']['left']
        actual=character.point(hand,'thumb')
        origin=(float(node.get('data-origin-x')),float(node.get('data-origin-y')))
        assert math.dist(origin,actual)<.001,(t,born,'Rendered salt grain was not emitted from its actual thumb')
        emitted.append({'emission_time':born,'rendered_origin':origin,'actual_thumb':actual})
    assert emitted,'No salt grains are actually emitted during the sprinkle'
    rows.append({'time':t,'action':'salt_sprinkle','origins':emitted,
                 **component_contact(svg_at(t),['hand-left'],['grains-sel'])})
    return rows


def check_material_persistence(animation,art,svg_at):
    result=[]
    for t in(8.6,14.9,19.4,29.2,37.5):
        state=animation.scene_state(t);root=ET.fromstring(svg_at(t))
        bin_group=next(n for n in root.iter()if n.get('id')=='poubelle-papier')
        emitted={signature(n)for n in bin_group.iter()if n.tag.rsplit('}',1)[-1]=='g'}
        count=int(state['bin_count']);items=[]
        for j in range(count):
            expected=ET.fromstring(art._ball(*TIMELINE['bin_layout']['centres'][j],
                                            TIMELINE['bin_layout']['radii'][j],
                                            TIMELINE['bin_layout']['rotations'][j],
                                            TIMELINE['bin_layout']['visual_seeds'][j]))
            sha=signature(expected)
            assert sha in emitted,(t,j+1,'Previously landed paper geometry is absent from the emitted bin')
            items.append({'ordinal':j+1,'emitted_geometry_sha256':sha})
        result.append({'time':t,'landed_papers':items})
    contacts=[]
    for c in TIMELINE['cycles']:
        for stage,t in(('pull',sum(c['pull'])/2.),('wipe',c['wipe'][0]+.65*(c['wipe'][1]-c['wipe'][0]))):
            svg=svg_at(t)
            for side in('left','right'):
                # The last small sheet is held solely by the right mitten
                # before the two tips are brought together for drying.
                if c['id']==4 and stage=='pull'and side=='left':continue
                contacts.append({'cycle':c['id'],'stage':stage,'time':t,
                                 **component_contact(svg,['hand-'+side],['papier-en-main'])})
    return {'persistent_landed_geometry':result,'paper_hand_contacts':contacts}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',type=Path,required=True)
    parser.add_argument('--silent',type=Path,required=True)
    parser.add_argument('--audio',type=Path,default=EP/'audio/mix.wav')
    parser.add_argument('--report',type=Path,default=EP/'controle/QA.json')
    parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    # Parent owns the producer freeze; this independent snapshot also detects
    # any mutation during the checks, including resources and the timeline.
    files=sorted(p for p in SOURCE.rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc')
    files+=[EP/'chronologie.json']
    files+=[EP/'audio/events.json',EP/'audio/input_bank.json',EP/'audio/motion_sync.json']
    files+=sorted(p for p in(EP/'assets').rglob('*')if p.is_file())
    frozen={str(p.relative_to(ROOT)):digest(p)for p in files}
    announced_freeze=json.loads((EP/'controle/gel_sources.json').read_text())
    visual_freeze=announced_freeze['visual_sources_sha256']
    assert all(digest(ROOT/p)==sha for p,sha in visual_freeze.items()),'Visual producer differs from the announced render freeze'
    protected=json.loads((EP/'controle/baseline_protegee.json').read_text())
    assert all(digest(ROOT/p)==sha for p,sha in protected.items()),'Historical reference changed before QA'
    selected_rig=ROOT/'personnages/galet_v1/sources/rig.py'
    selected_palette=ROOT/'personnages/galet_v1/sources/palette.json'
    assert digest(SOURCE/'reference_character.py')==digest(selected_rig),'The episode changed the selected pebble drawing'
    assert digest(SOURCE/'palette.json')==digest(selected_palette),'The episode changed the selected pebble palette'
    renderer=module(SOURCE/'render.py','galet_episode_qa_fresh_renderer')
    animation=getattr(renderer,'animation',None)or module(SOURCE/'animation.py','galet_episode_qa_fresh_animation')
    character=getattr(renderer,'character',None)or sys.modules.get('character')
    art=getattr(renderer,'art',None)or sys.modules.get('art')
    assert character is not None and art is not None
    svg_at=renderer.svg_at
    probe=video_probe(args.video,True);silent_probe=video_probe(args.silent,False)
    video_sha,silent_sha=h264_sha(args.video),h264_sha(args.silent)
    assert video_sha==silent_sha,'The sound and silent exports have different pictures'
    states=[];svgs=[];counts=[];stocks=[];hold=[];steam=[];scales=[];drawn_roll=[]
    feet_signatures={'foot-l':set(),'foot-r':set()}
    for i in range(COUNT):
        t=i/FPS;s=animation.scene_state(t);svg=svg_at(t);tree=ET.fromstring(svg)
        ids=[n.get('id')for n in tree.iter()if n.get('id')];lookup={n.get('id'):n for n in tree.iter()if n.get('id')}
        assert len(ids)==len(set(ids)),(i,'Duplicate SVG IDs')
        assert all(ref in lookup for ref in re.findall(r'url\(#([^)]*)\)',svg)),(i,'Invalid SVG mask reference')
        sink_shot=s['shot']=='sink'
        mitten_nodes=[n for n in tree.iter()if n.get('data-part')=='floating-mitten']
        assert len(mitten_nodes)==(1 if sink_shot else 2),(i,'Wrong mitten count')
        assert not any(n.get('data-part')=='arm'or(n.get('id')or'').startswith('arm-')for n in tree.iter()),(i,'Unexpected arm')
        if not sink_shot:
            for part in('pebble-body','foot-l','foot-r','eye-white-l','eye-white-r','pupil-l','pupil-r','mouth','toque-chef','tablier-taille'):
                assert part in lookup,(i,'Missing character/costume',part)
            parents={child:parent for parent in tree.iter()for child in parent}
            for foot_id in feet_signatures:
                inherited=[];parent=parents.get(lookup[foot_id])
                while parent is not None:
                    inherited.append(parent.get('transform',''))
                    parent=parents.get(parent)
                pose=signature(lookup[foot_id])+json.dumps(inherited)
                feet_signatures[foot_id].add(hashlib.sha256(pose.encode()).hexdigest())
            for side,h in s['hands'].items():
                path=lookup['hand-outline-'+side]
                assert path.get('d')==character.rig.glove_path(h['pinch']),(i,side,'Mitten outline differs from selected rig')
                determinant=abs(float(np.linalg.det(svg_transform(lookup['hand-'+side].get('transform'))[:2,:2])))
                assert abs(determinant-1.44)<1e-8,(i,side,'Wide mitten changes scale',determinant)
                scales.append(determinant)
        else:
            assert 'pebble-body'not in lookup and'mouth'not in lookup,(i,'Face enters sink insert')
        counts.append(int(s['bin_count']));stocks.append(float(s['roll']['remaining']))
        assert 0.<=stocks[-1]<=1.
        if not sink_shot:
            roll_node=lookup['essuie-tout-variable']
            roll_body=next(n for n in roll_node if n.tag.rsplit('}',1)[-1]=='path')
            coordinates=[float(v)for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+)',roll_body.get('d'))]
            width=coordinates[-2]-coordinates[0]
            radius=math.sqrt(16.**2+(67.**2-16.**2)*stocks[-1])
            assert abs(width-2.*radius)<.001,(i,'Drawn roll width does not match remaining paper',width,radius)
            if stocks[-1]<1.e-9:assert roll_body.get('fill')=='#BD9977',(i,'Empty roll still looks like white paper')
            drawn_roll.append({'frame':i,'width_world_pixels':width})
        if t>=TIMELINE['paper_overflow']['settle']:
            assert 'dernier-papier-au-sol'in lookup,(i,'Last paper disappeared from floor')
        if t>=TIMELINE['final_hold'][0]:
            hold.append(element_signature(svg,['pebble-body','hand-left','hand-right','foot-l','foot-r']))
            steam.append(signature(lookup['vapeur-cuisson']))
        states.append(s);svgs.append(svg)
    assert counts==sorted(counts)and counts[-1]==3,'Basket state resets or lacks its persistent three papers'
    assert stocks==sorted(stocks,reverse=True)and stocks[0]==1. and stocks[-1]==0.,'Roll stock does not decrease to zero'
    assert all(len(values)==1 for values in feet_signatures.values()),'The emitted feet drift in world coordinates'
    assert all(row==hold[0]for row in hold),'The final actor pose is not held'
    assert len(set(steam))>1,'Steam no longer animates in the held ending'
    print(f'QA: {COUNT} emitted SVG states, stocks and final hold checked',flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers)as pool:
        face_checks=list(pool.map(gross_face_worker,enumerate(svgs)))
    print('QA: phone-scale mitten/face intersections checked',flush=True)
    sink_checks=check_sink(renderer,character,svg_at)
    tools=check_tools(animation,character,art,svg_at)
    materials=check_material_persistence(animation,art,svg_at)
    print('QA: sink, tool and paper contacts checked on emitted silhouettes',flush=True)
    indices=sorted({min(COUNT-1,round(t*FPS))for t in IMAGE_TIMES}|{COUNT-1})
    decoded=decoded_frames(args.video,indices);images=[]
    for i in indices:
        reference=rgba(svgs[i]);assert np.all(reference[:,:,3]==255),(i,'Transparent camera edge')
        diff=np.abs(reference[:,:,:3].astype(float)-decoded[i].astype(float))
        global_error=float(diff.mean());assert global_error<4.,(i,'Encoded frame differs from fresh SVG',global_error)
        tree=ET.fromstring(svgs[i]);ids={n.get('id')for n in tree.iter()}
        roi_ids=['hand-left']+(['hand-right']if'hand-right'in ids else[])
        roi=mask(svgs[i],roi_ids);roi_error=float(diff[roi].mean())if np.any(roi)else 0.
        assert roi_error<6.,(i,'Mitten pixel comparison failed',roi_error)
        pupils=[]
        if'eye-white-l'in ids:
            for side in('l','r'):
                white=mask(svgs[i],['eye-white-'+side]);pupil=mask(svgs[i],['pupil-'+side])
                outside=int(np.count_nonzero(pupil&~white));assert outside==0,(i,side,'Pupil escapes aperture',outside)
                pupils.append({'side':side,'outside_pixels':outside})
        images.append({'frame':i,'time':i/FPS,'mean_abs_rgb_error':global_error,'mitten_mean_abs_rgb_error':roi_error,'pupils':pupils})
    audio=check_audio(args.video,args.audio)
    print('QA: decoded pictures and audio reconstruction checked',flush=True)
    assert frozen=={str(p.relative_to(ROOT)):digest(p)for p in files},'A producer/resource changed during QA'
    assert all(digest(ROOT/p)==sha for p,sha in visual_freeze.items()),'A frozen visual producer changed during QA'
    assert all(digest(ROOT/p)==sha for p,sha in protected.items()),'A historical reference changed during QA'
    report={'status':'passed','scope':'Independent emitted geometry, encoded image and audio-signal checks; no artistic approval.',
            'duration':DURATION,'fps':FPS,'frames':COUNT,'dimensions':list(DIMENSIONS),
            'checker_sha256':digest(__file__),'source_sha256':frozen,'historical_sha256':protected,
            'announced_visual_freeze_sha256':visual_freeze,
            'selected_character_rig_sha256':digest(selected_rig),
            'selected_character_palette_sha256':digest(selected_palette),
            'video_sha256':digest(args.video),'silent_video_sha256':digest(args.silent),
            'identical_h264_stream_sha256':video_sha,'all_svg_frames_checked':COUNT,
            'phone_scale_face_occlusions':face_checks,'sink_geometry':sink_checks,'tool_contacts':tools,
            'material_persistence':materials,'drawn_roll_widths':drawn_roll,
            'roll_first_last':[stocks[0],stocks[-1]],'basket_first_last':[counts[0],counts[-1]],
            'final_hold_frames':len(hold),'steam_hold_distinct_states':len(set(steam)),
            'emitted_foot_pose_counts':{key:len(values)for key,values in feet_signatures.items()},
            'fresh_encoded_image_comparisons':images,'audio':audio,
            'limits':'No continuous viewing, listening, perceived mix balance, emotional-recognition or user-approval claim.'}
    atomic_json(args.report,report)
    print(json.dumps({'status':'passed','report':str(args.report),'frames':COUNT,'image_samples':len(images),'tool_samples':len(tools),'sink_cycles':len(sink_checks)}))


if __name__=='__main__':main()
