"""Independent targeted checks for the drawn viewpoints and physical PATCH performance.

Use --preflight for sources, or --final after both reviewed HD exports exist.
Only this script, controle/qa.json and ignored work/qa are QA-owned.
Numeric checks do not constitute listening or an audience comprehension test.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import wave
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
PRIVATE=EP/'work/qa'
import scene
import personnage
from copy import deepcopy
from PIL import ImageFilter


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)],text=True))
def stream_hash(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','h264','-'])).hexdigest()
def pcm(path):
    with wave.open(str(path),'rb') as w:
        a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32)
        meta={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'frames':w.getnframes(),'bits':8*w.getsampwidth()}
    return a,meta

def ids_of(svg):
    root=ET.fromstring(svg);entries={};duplicates=[]
    for e in root.iter():
        name=e.get('id')
        if name:
            if name in entries:duplicates.append(name)
            entries[name]=e
    return root,entries,duplicates


def transform_matrix(value):
    result=np.eye(3)
    for name,values in re.findall(r'(matrix|translate|scale|rotate)\(([^)]*)\)',value or ''):
        v=[float(x)for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',values)];m=np.eye(3)
        if name=='matrix':m=np.array([[v[0],v[2],v[4]],[v[1],v[3],v[5]],[0.,0.,1.]])
        elif name=='translate':m[:2,2]=(v[0],v[1]if len(v)>1 else 0.)
        elif name=='scale':m[0,0]=v[0];m[1,1]=v[1]if len(v)>1 else v[0]
        else:
            a=math.radians(v[0]);c,s=math.cos(a),math.sin(a);m=np.array([[c,-s,0.],[s,c,0.],[0.,0.,1.]])
            if len(v)>1:
                t=np.eye(3);t[:2,2]=v[1:3];it=np.eye(3);it[:2,2]=-np.array(v[1:3]);m=t@m@it
        result=result@m
    return result


def transformed_nodes(root):
    result={}
    def visit(node,parent):
        m=parent@transform_matrix(node.get('transform'));result[id(node)]=m
        for child in node:visit(child,m)
    visit(root,np.eye(3));return result


def isolated_component(actor,part):
    layer='torso'if part in ('head','foot-left','foot-right')else'arms'if part.startswith('arm-')else'hands'
    outer=ET.fromstring(personnage.character_svg(actor,'sample',layer=layer))
    wanted='sample-'+part
    def prune(node):
        if node.get('id')==wanted:return True
        if node.tag.endswith('defs'):return True
        kept=False
        for child in list(node):
            if prune(child):kept=True
            else:node.remove(child)
        return kept
    if not prune(outer):raise ValueError('Missing component '+wanted)
    return outer


def alpha_mask(component,view,size=(128,128),fills_only=True):
    e=deepcopy(component)
    if fills_only:
        for node in e.iter():
            node.set('stroke','none')
            if node.get('fill')not in (None,'none'):node.set('fill','#FFFFFF')
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size[0]}" height="{size[1]}" viewBox="'+
         ' '.join(str(v)for v in view)+'">'+ET.tostring(e,encoding='unicode')+'</svg>')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).getchannel('A')


def scene_marker_mask(svg,target,crop,isolated=False):
    """Visible target pixels after the actual scene layering, not anchor presence."""
    root,ids,_=ids_of(svg);component=ids[target]
    for node in component.iter():
        if node.get('fill')not in (None,'none'):node.set('fill','#FF00FF')
        if node.get('stroke')not in (None,'none'):node.set('stroke','#FF00FF')
    if isolated:
        def prune(node):
            if node.get('id')==target or node.tag.endswith('defs'):return True
            kept=False
            for child in list(node):
                if prune(child):kept=True
                else:node.remove(child)
            return kept
        assert prune(root)
    root.set('width','200');root.set('height','200');root.set('viewBox',' '.join(map(str,crop)))
    data=cairosvg.svg2png(bytestring=ET.tostring(root))
    rgb=np.asarray(Image.open(io.BytesIO(data)).convert('RGB'))
    mask=(rgb[:,:,0]>180)&(rgb[:,:,1]<75)&(rgb[:,:,2]>180)
    if not isolated:
        xs=crop[0]+(np.arange(200)+.5)*crop[2]/200
        ys=crop[1]+(np.arange(200)+.5)*crop[3]/200
        mask&=(ys[:,None]>=0)&(ys[:,None]<1920)&(xs[None,:]>=0)&(xs[None,:]<1080)
    return mask


def rendered_contact_samples():
    times=[.3,1.7,2.8,4.1,7.2,7.8,8.7,9.8,11.8,12.45,13.5,15.2,15.35,
           15.5,16.7,18.3,18.7,20.5,23.3,23.6,24.05,24.7,25.08,25.3,25.7,26.3,28.4,29.2]
    rows=[]
    for t in times:
        a=scene.state_at(t)['actor_screen'];anchors=personnage.anchors(a)
        for side in ('left','right'):
            x,y=anchors['wrists'][side];crop=(x-90,y-90,180,180)
            arm=alpha_mask(isolated_component(a,'arm-'+side),crop)
            paw=alpha_mask(isolated_component(a,'hand-'+side),crop)
            aa=np.asarray(arm)>128;bb=np.asarray(paw)>128
            rows.append({'time':t,'side':side,'intersection_pixels':int(np.count_nonzero(aa&bb)),
                         'within_one_pixel':bool(np.any((np.asarray(arm.filter(ImageFilter.MaxFilter(3)))>128)&bb))})
    return rows


def rendered_cheek_samples():
    rows=[]
    for t in (13.,13.5,14.,14.5,15.):
        a=scene.state_at(t)['actor_screen'];h=a['hands']['left'];crop=(h['x']-100,h['y']-100,200,200)
        head=np.asarray(alpha_mask(isolated_component(a,'head'),crop))>128
        paw=np.asarray(alpha_mask(isolated_component(a,'hand-left'),crop))>128
        rows.append({'time':t,'intersection_pixels':int(np.count_nonzero(head&paw))})
    return rows


def visible_jump_feet():
    rows=[]
    for t in (25.2,25.4,25.7,26.,26.3,26.55):
        s=scene.state_at(t);a=s['actor_screen'];svg=scene.svg_at(t)
        for side,(x,y)in personnage.anchors(a)['feet'].items():
            crop=(x-100,y-100,200,200)
            all_pixels=scene_marker_mask(svg,'patch-foot-'+side,crop,True)
            visible=scene_marker_mask(svg,'patch-foot-'+side,crop,False)
            total=int(all_pixels.sum());shown=int(visible.sum());yy,xx=np.where(all_pixels)
            bbox=[crop[0]+int(xx.min()),crop[1]+int(yy.min()),crop[0]+int(xx.max()+1),crop[1]+int(yy.max()+1)]if total else None
            rows.append({'time':t,'side':side,'visible_pixels':shown,'full_foot_pixels':total,
                         'visible_fraction':shown/max(1,total),'screen_bbox':bbox,
                         'above_tabletop':bool(bbox and bbox[3]<s['layout']['desk_y']),
                         'inside_frame':bool(bbox and bbox[0]>=0 and bbox[2]<=1080 and bbox[1]>=0 and bbox[3]<=1920)})
    return rows


def rendered_bilateral_contacts():
    rows=[]
    for t in (25.1,25.4,25.7,26.3,28.2,29.2):
        s=scene.state_at(t);svg=scene.svg_at(t)
        for side,h in s['actor_screen']['hands'].items():
            crop=(h['x']-100,h['y']-100,200,200)
            phone=scene_marker_mask(svg,'phone',crop,True)
            paw=scene_marker_mask(svg,'patch-hand-'+side,crop,True)
            rows.append({'time':t,'side':side,'intersection_pixels':int((phone&paw).sum())})
    return rows


def reaction_eye_visibility():
    rows=[]
    for t in (23.3,23.6,24.1,24.5):
        svg=scene.svg_at(t);root,ids,_=ids_of(svg);positions=transformed_nodes(root)
        for side in ('l','r'):
            eye=ids['patch-eye-outline-'+side];center=positions[id(eye)]@np.array([float(eye.get('cx')),float(eye.get('cy')),1.])
            crop=(float(center[0])-110,float(center[1])-110,220,220)
            full=scene_marker_mask(svg,'patch-eye-outline-'+side,crop,True)
            visible=scene_marker_mask(svg,'patch-eye-outline-'+side,crop,False)
            rows.append({'time':t,'side':side,'outline_visible_fraction':int(visible.sum())/max(1,int(full.sum()))})
    return rows


def head_framing_samples():
    rows=[]
    for t in (.3,4.9,7.5,9.8,11.9,13.5,15.35,16.7,18.7,20.5,24.75,25.12,25.3,25.7,26.3,29.2):
        a=scene.state_at(t)['actor_screen'];view=(-300.,-300.,1800.,2400.)
        mask=alpha_mask(isolated_component(a,'head'),view,(450,600),fills_only=False);box=mask.getbbox()
        bounds=[view[k%2]+v*4 for k,v in enumerate(box)]
        rows.append({'time':t,'bbox':bounds,'inside':bounds[0]>=-4 and bounds[1]>=-4 and bounds[2]<=1084 and bounds[3]<=1924})
    return rows


def source_scan():
    issues={k:[]for k in ('svg_structure','story_time_and_countdown','paper_goal','phone_grip_and_orientation','eye_framing')}
    records=[];last_elapsed=-1.;maximum_grip=0.;maximum_bilateral=0.
    nonactors={'clock','box_insert','paper'};starts={int(c['frame_start'])-1:c for c in scene.TIMELINE['time_representation']['minute_checks']}
    current_minute=0;start_index=0;view_frames={};paper_frames=0
    for index in range(720):
        t=index/24.;s=scene.state_at(t);svg=scene.svg_at(t);root,ids,dups=ids_of(svg);positions=transformed_nodes(root);view=s['view']
        view_frames[view]=view_frames.get(view,0)+1
        if index in starts:current_minute=starts[index]['elapsed_minute'];start_index=index
        expected_elapsed=(0. if index<96 else t-4 if index<144 else current_minute*60+(index-start_index)/24 if index<528 else 1799+(index-528)/24 if index<552 else 1800+(index-552)/24)
        expected_remaining=1800 if index<96 else max(0,math.ceil(1800-expected_elapsed-1.e-8));display=f'{expected_remaining//60:02d}:{expected_remaining%60:02d}'
        if abs(s['story_elapsed_seconds']-expected_elapsed)>1.e-7 or s['story_elapsed_seconds']<last_elapsed or s['display']!=display or s['locked']!=(96<=index<552):issues['story_time_and_countdown'].append(index+1)
        last_elapsed=s['story_elapsed_seconds']
        if dups or re.search(r'\b(?:nan|inf)\b',svg,re.I) or any(x not in ids for x in re.findall(r'url\(#([^)]*)\)',svg)):issues['svg_structure'].append(index+1)
        expected_actor=view not in nonactors
        for part in ('eye-white-l','eye-white-r','hand-left','hand-right','arm-left','arm-right'):
            if ('patch-'+part in ids)!=expected_actor:issues['svg_structure'].append(index+1)
        if (ids.get('timer')is not None)!=(view not in ('clock','paper')):issues['svg_structure'].append(index+1)
        if 'timer'in ids and ids['timer'].get('data-display')!=display:issues['story_time_and_countdown'].append(index+1)
        if 'wall-clock'in ids and abs(float(ids['wall-clock'].get('data-elapsed-seconds'))-expected_elapsed)>1.e-6:issues['story_time_and_countdown'].append(index+1)
        if view!='clock':
            paper=ids.get('paper');boxes=[ids.get(f'todo-box-{i}')for i in range(3)]
            if paper is None or paper.get('data-completed')!='0' or paper.get('data-has-marks')!='0' or any(b is None or b.get('data-checked')!='0'for b in boxes)or ids['todo-header'].get('data-text')!='TO DO':issues['paper_goal'].append(index+1)
        if view=='paper':paper_frames+=1
        if expected_actor:
            # Full ellipse bounds are used so the test does not infer visibility
            # from a clipped pupil centre. Intentional lock/face close crops differ.
            if view not in ('lock_insert','face_box'):
                for side in ('l','r'):
                    eye=ids['patch-eye-white-'+side];m=positions[id(eye)];ex,ey,rx,ry=map(float,(eye.get('cx'),eye.get('cy'),eye.get('rx'),eye.get('ry')))
                    center=m@np.array([ex,ey,1.]);dx=math.hypot(m[0,0]*rx,m[0,1]*ry);dy=math.hypot(m[1,0]*rx,m[1,1]*ry)
                    if not(0<=center[0]-dx and center[0]+dx<=1080 and 0<=center[1]-dy and center[1]+dy<=1920):issues['eye_framing'].append(index+1)
        phone=ids.get('phone');expected_phone=s['phone']['visible']and view not in ('clock','paper')
        if (phone is not None)!=expected_phone:issues['phone_grip_and_orientation'].append(index+1)
        if phone is not None and s['phone']['owner']=='right':
            m=positions[id(phone)]
            offset=(25.,-30.)if t<24.7 else s['phone_binding']['offset_from_right']
            contact=m@np.array([-offset[0],-offset[1],1.]);h=s['actor_screen']['hands']['right'];err=math.hypot(contact[0]-h['x'],contact[1]-h['y']);maximum_grip=max(maximum_grip,err)
            if err>.002 or phone.get('data-owner')!='right':issues['phone_grip_and_orientation'].append(index+1)
            if t>=24.7:
                if phone.get('data-face')!='back':issues['phone_grip_and_orientation'].append(index+1)
                if s['phone']['bilateral']:
                    for side,x in [('left',-42.),('right',42.)]:
                        point=m@np.array([x,15.,1.]);h=s['actor_screen']['hands'][side];error=math.hypot(point[0]-h['x'],point[1]-h['y']);maximum_bilateral=max(maximum_bilateral,error)
                        if error>.002:issues['phone_grip_and_orientation'].append(index+1)
        records.append({'t':t,'view':view,'gaze':s['actor']['gaze'],'left_y':s['actor']['hands']['left']['y'],'pencil_held':s['pencil_held']})
    return issues,{'frames':720,'view_frames':view_frames,'paper_insert_frames':paper_frames,'maximum_svg_right_grip_error_px':maximum_grip,'maximum_svg_bilateral_error_px':maximum_bilateral},records


def gaze_checks(records):
    first=[r for r in records if 7.<=r['t']<8.];second=[r for r in records if 8.<=r['t']<10.]
    rows=[]
    for number,seq in enumerate((first,second),1):
        rows.append({'minute':number,'visible_frames':len(seq),'all_actor_visible':all(r['view']=='medium'for r in seq),'maximum_gaze_x':max(r['gaze'][0]for r in seq),'final_gaze_x':seq[-1]['gaze'][0],'pencil_descends_px':seq[-1]['left_y']-seq[0]['left_y']})
    return rows


def audio_checks(check):
    cues=scene.TIMELINE['audio_cues'];bank=json.loads((EP/'assets/son/bank.json').read_text());provenance=json.loads((EP/'assets/son/provenance.json').read_text());actual={c['id']:c for c in json.loads((EP/'audio/cues.json').read_text())};report=json.loads((EP/'audio/mix_report.json').read_text());wanted={c['id']:c for c in cues}
    mismatch=[name for name,v in bank['sounds'].items()if digest(EP/'assets/son'/v['file'])!=v['sha256']]+[v['id']for v in provenance['sources']if digest(EP/'assets/son'/v['file'])!=v['sha256']]
    good=set(actual)==set(wanted)and all(actual[k]['sound']==v['sound']and abs(actual[k]['at']-v['at'])<1e-8 and actual[k]['start_sample']==round(v['at']*48000)and actual[k]['sound_sha256']==bank['sounds'][v['sound']]['sha256']for k,v in wanted.items())
    check('18_cues_assets_and_timeline_match',len(cues)==18 and not mismatch and good and report['timeline_sha256']==digest(EP/'chronologie.json')and report['sha256']==digest(EP/'audio/mix.wav'),{'cue_count':len(cues),'mismatches':mismatch,'cue_contacts_match':good})
    mixed,meta=pcm(EP/'audio/mix.wav');peak=int(np.max(np.abs(mixed)));clipped=int(np.count_nonzero(np.abs(mixed)>=32767))
    check('pcm_30s_48khz_stereo_unclipped',meta=={'sample_rate':48000,'channels':2,'frames':1440000,'bits':16}and clipped==0,{**meta,'peak_dbfs':20*math.log10(peak/32768),'clipped_samples':clipped})
    error=int(np.max(np.abs(sum(pcm(EP/f'audio/stems/{s}.wav')[0]for s in ('foley','ui','tick'))-mixed)))
    check('stems_recombine',error<=2,{'maximum_error_lsb':error})
    check('sound_bank_and_mix_preserved_from_v3',digest(EP/'audio/mix.wav')==digest(ROOT/'episodes/patch_01_coffre_v3/audio/mix.wav'),{'mix_sha256':digest(EP/'audio/mix.wav')})


def frame_comparisons(video):
    folder=PRIVATE/'fresh_decoded';folder.mkdir(parents=True,exist_ok=True)
    frames=[20,97,156,183,286,325,402,493,541,568,617,699]
    filters='+'.join(f'eq(n\\,{f-1})'for f in frames)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+filters,'-fps_mode','vfr',str(folder/'%03d.png')],check=True)
    rows=[]
    for j,f in enumerate(frames,1):
        actual=np.asarray(Image.open(folder/f'{j:03d}.png').convert('RGB'),dtype=np.int16)
        fresh=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=scene.svg_at((f-1)/24).encode(),output_width=1080,output_height=1920))).convert('RGB'),dtype=np.int16)
        delta=np.abs(actual-fresh);rows.append({'frame':f,'mean_abs_rgb_error':float(delta.mean()),'p99_rgb_error':float(np.quantile(delta,.99))})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preflight',action='store_true');p.add_argument('--final',action='store_true');p.add_argument('--visual-only',action='store_true');args=p.parse_args()
    if not args.preflight and not args.final:p.error('Choose --preflight or --final')
    if args.final and args.visual_only:p.error('Final reports must include audio')
    PRIVATE.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,passed,evidence):checks.append({'check':name,'passed':bool(passed),'evidence':evidence})
    baseline=json.loads((EP/'controle/baseline.json').read_text());changed=[name for name,h in baseline.items()if digest(ROOT/name)!=h]
    check('v3_and_concept_untouched',not changed,{'files':len(baseline),'changed':changed})
    check('palette_preserved_and_rig_extended',digest(EP/'sources/palette.json')==digest(ROOT/'episodes/patch_01_coffre_v3/sources/palette.json')and hasattr(personnage,'feet_local'),{'palette_sha256':digest(EP/'sources/palette.json'),'rig_sha256':digest(EP/'sources/personnage.py')})
    issues,stats,records=source_scan()
    for name,failures in issues.items():check(name,not failures,{'failing_frames':sorted(set(failures))[:35],**stats})
    glances=gaze_checks(records);check('first_two_visible_checks_return_to_paper',all(r['all_actor_visible']and r['maximum_gaze_x']>.8 and r['final_gaze_x']<0 and r['pencil_descends_px']>15 for r in glances),glances)
    minutes=scene.TIMELINE['time_representation']['minute_checks'];counts=[sum(1 for r in records if c['elapsed_minute']*60<=scene.state_at(r['t'])['story_elapsed_seconds']<(c['elapsed_minute']+1)*60)for c in minutes]
    check('29_story_minutes_and_last_values_represented',len(minutes)==29 and all(n>0 for n in counts)and all(n>=16 for n in counts[-3:]),{'minute_frame_counts':counts})
    cuffs=rendered_contact_samples();check('56_rendered_sleeve_paw_connections',all(r['intersection_pixels']>0 or r['within_one_pixel']for r in cuffs),cuffs)
    cheek=rendered_cheek_samples();check('5_rendered_cheek_paw_supports',all(r['intersection_pixels']>0 for r in cheek),cheek)
    feet=visible_jump_feet();check('two_actual_feet_visible_above_desk_in_jump',all(r['visible_fraction']>.85 and r['above_tabletop']and r['inside_frame']for r in feet),feet)
    contacts=rendered_bilateral_contacts();check('both_phone_grips_overlap_real_rendered_phone',all(r['intersection_pixels']>100 for r in contacts),contacts)
    eyes=reaction_eye_visibility();check('reaction_eyes_remain_partly_visible_in_intentional_close_crop',all(r['outline_visible_fraction']>.25 for r in eyes),eyes)
    heads=head_framing_samples();check('full_head_silhouettes_fit_non_insert_views',all(r['inside']for r in heads),heads)
    from vues import scene_layers
    tops={v:scene_layers(v,0.,0.)['tabletop']for v in ('wide_high','medium','low')};check('different_drawn_tabletop_surfaces',len(set(tops.values()))==3 and all(len(v)>100 for v in tops.values()),{'tabletop_sha256':{k:hashlib.sha256(v.encode()).hexdigest()for k,v in tops.items()},'limit':'Different geometry verified; perspective and emotional staging also require the separate visual critique.'})
    if not args.visual_only:audio_checks(check)
    if(EP/'controle/gel_sources.json').exists():
        frozen=json.loads((EP/'controle/gel_sources.json').read_text())['files'];changed=[n for n,h in frozen.items()if digest(ROOT/n)!=h];check('frozen_sources_unchanged',not changed,{'files':len(frozen),'changed':changed})
    if args.final:
        video=EP/'PATCH_Le_coffre_V4.mp4';silent=EP/'PATCH_Le_coffre_V4_muet.mp4';a,b=probe(video),probe(silent)
        sv=[x for x in a['streams']if x['codec_type']=='video'];mv=[x for x in b['streams']if x['codec_type']=='video'];sa=[x for x in a['streams']if x['codec_type']=='audio'];ma=[x for x in b['streams']if x['codec_type']=='audio']
        valid=lambda v:v['width']==1080 and v['height']==1920 and v['r_frame_rate']=='24/1'and int(v['nb_read_frames'])==720 and abs(float(v['duration'])-30)<1e-6
        check('hd_exports_720_frames_30s',len(sv)==len(mv)==1 and valid(sv[0])and valid(mv[0])and len(sa)==1 and not ma and sa[0]['sample_rate']=='48000'and sa[0]['channels']==2 and abs(float(sa[0]['duration'])-30)<.05,{'sound_video':sv,'silent_video':mv,'audio':sa})
        hashes=[stream_hash(v)for v in (video,silent)];check('identical_h264_in_sound_and_silent',hashes[0]==hashes[1],{'h264_sha256':hashes})
        comparisons=frame_comparisons(video);check('12_hd_decoded_frames_match_fresh_renders',all(r['mean_abs_rgb_error']<3.5 and r['p99_rgb_error']<=16 for r in comparisons),comparisons)
    report={'status':'passed'if all(c['passed']for c in checks)else'failed','scope':'final_exports'if args.final else'visual_preflight'if args.visual_only else'preflight','observed_at':datetime.now(ZoneInfo('Africa/Casablanca')).isoformat(),'checks':checks,'limits':['Checks do not establish comedy or audience approval; separate visual critique applies.','No real listening or audio comfort approval claimed.']}
    if args.final:report['files']={str(v.relative_to(ROOT)):digest(v)for v in (video,silent,EP/'audio/mix.wav',EP/'chronologie.json')}
    destination=EP/'controle/qa.json'if args.final else PRIVATE/'preflight.json';destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['check']for c in checks if not c['passed']],'report':str(destination)},ensure_ascii=False))
    if report['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
