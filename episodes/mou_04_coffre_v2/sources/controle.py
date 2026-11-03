"""Independent technical checks for MOU lockbox V2, without claiming audition.

Run after producer freeze: --preflight, then --final --reuse-preflight-lcd.
Actual composed pixels and decoded MP4 images complement the pose checks.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import concurrent.futures
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scene import state_at, svg_at, FPS, DURATION
from cadrage import SHOTS, framing_at
from personnage import anchors, face_parameters
import mou_rig_original as rig

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
WORK=EP/'work/qa'
LIMBS={'continuous-mou-arm','mou-arm','mou-hand','mitten-paw','attached-sleeve'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def norm(x):return json.loads(json.dumps(x))
def finite(x):
    if isinstance(x,dict):return all(finite(v) for v in x.values())
    if isinstance(x,(tuple,list)):return all(finite(v) for v in x)
    return not isinstance(x,float) or math.isfinite(x)
def source_hash():
    h=hashlib.sha256()
    for p in sorted((EP/'sources').glob('*')):
        if p.suffix in ('.py','.json') and p.name!='controle.py':h.update(p.name.encode());h.update(p.read_bytes())
    h.update((EP/'chronologie.json').read_bytes());return h.hexdigest()
def rgba(svg,width=1080,height=1920):
    raw=cairosvg.svg2png(bytestring=svg.encode()if isinstance(svg,str)else svg,output_width=width,output_height=height)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))
def wav(p):
    with wave.open(str(p))as w:
        params=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy().reshape(-1,w.getnchannels())
    return params,pcm
def isolated(tree,target):
    path=[]
    def walk(n,parents):
        if n.get('id')==target:path.extend(parents+[n]);return True
        return any(walk(c,parents+[n])for c in n)
    if not walk(tree,[]):raise ValueError('Missing rendered object '+target)
    out=ET.Element(tree.tag,tree.attrib)
    for n in tree.iter():
        if n.tag.endswith('defs'):out.append(deepcopy(n))
    current=out
    for parent in path[1:-1]:current=ET.SubElement(current,parent.tag,parent.attrib)
    current.append(deepcopy(path[-1]));return ET.tostring(out)
def visible_overlap(svg,hand,obj):
    tree=ET.fromstring(svg);full=rgba(svg)[:,:,:3].astype(np.int16)
    mask=rgba(isolated(tree,obj))[:,:,3]>230;bare=deepcopy(tree);removed=0
    for parent in list(bare.iter()):
        for child in list(parent):
            if child.get('id')==hand:parent.remove(child);removed+=1
    diff=np.max(np.abs(full-rgba(ET.tostring(bare))[:,:,:3].astype(np.int16)),axis=2)>3
    return {'hand':hand,'object':obj,'removed':removed,'pixels':int(np.count_nonzero(mask&diff))}
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
def stream_hash(p,kind,fmt):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map',kind,'-c','copy','-f',fmt,'-'])).hexdigest()

def lcd_job(args):
    frame,svg,layout,camera=args
    cx,cy,cw,_=camera;zoom=1080./cw
    x=(754.*layout['scale']+layout['tx']+layout.get('box_shift_x',0.)-cx)*zoom
    y=(1335.*layout['scale']+layout['ty']+layout.get('box_shift_y',0.)-cy)*zoom
    scale=layout['scale']*zoom;w,h=200.*scale,86.*scale
    row={'frame_zero':frame,'visible_pixels':0,'limb_pixels_in_lcd':0,'lcd_projection':[x,y,w,h]}
    tree=ET.fromstring(svg)
    if x>=1080 or x+w<=0 or y>=1920 or y+h<=0 or not any(n.get('id')=='timer'for n in tree.iter()):return row
    tree.set('viewBox',f'{x} {y} {w} {h}');tree.set('width','200');tree.set('height','86')
    normal=rgba(ET.tostring(tree),200,86)[:,:,:3].astype(np.int16);bare=deepcopy(tree)
    for parent in list(bare.iter()):
        for child in list(parent):
            if child.get('data-part')in LIMBS:parent.remove(child)
    clean=rgba(ET.tostring(bare),200,86)[:,:,:3].astype(np.int16)
    yy,xx=np.mgrid[:86,:200]
    visible=(x+(xx+.5)*scale>=0)&(x+(xx+.5)*scale<1080)&(y+(yy+.5)*scale>=0)&(y+(yy+.5)*scale<1920)
    visible&=(xx>=3)&(xx<197)&(yy>=3)&(yy<83)
    row.update(visible_pixels=int(visible.sum()),limb_pixels_in_lcd=int(np.count_nonzero(visible&(np.max(np.abs(normal-clean),axis=2)>3))))
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true');parser.add_argument('--final',action='store_true')
    parser.add_argument('--reuse-preflight-lcd',action='store_true');args=parser.parse_args()
    if not(args.preflight or args.final):parser.error('Run --preflight or --final after producer freeze')
    WORK.mkdir(parents=True,exist_ok=True);checks=[];initial=source_hash()
    def check(name,ok,detail):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    states=[state_at(i/FPS)for i in range(720)];svgs=[svg_at(i/FPS)for i in range(720)];trees=[ET.fromstring(v)for v in svgs]
    timeline=json.loads((EP/'chronologie.json').read_text())
    check('720_finite_states_unique_svg_ids',FPS==24 and DURATION==30 and all(finite(s)for s in states)and
          all(len(ids)==len(set(ids))for ids in [[n.get('id')for n in tr.iter()if n.get('id')]for tr in trees]),{'frames':720,'fps':FPS,'duration':DURATION})
    expected=[{'id':s[0],'start':s[1],'end':s[2],'view':s[3]}for s in SHOTS]
    views=[{'id':v['plan'] if isinstance(v['plan'],str)else f"P{v['plan']:02d}",'start':v['at'][0],'end':v['at'][1],'view':v['view']}for v in timeline['views']]
    covered=SHOTS[0][1]==0 and SHOTS[-1][2]==30 and len(SHOTS)==13 and all(a[2]==b[1]for a,b in zip(SHOTS,SHOTS[1:]))
    check('thirteen_shots_camera_and_timeline_agree',covered and norm(expected)==norm(timeline['shots'])==norm(views)and all(abs(s['camera'][3]/s['camera'][2]-16/9)<1e-8 for s in states),{'camera_shots':expected,'timeline_matches':norm(expected)==norm(timeline['shots']),'views_match':norm(expected)==norm(views)})
    native=ET.fromstring('<svg>'+rig.character_fragment(rig.DEFAULT_POSE,'qa-native')+'</svg>');native_body=next(n for n in native if n.get('id')=='body')[0].get('d')
    identity_bad=[];actor_frames=0
    for i,tr in enumerate(trees):
        if states[i]['view']in('clock','box_insert'):continue
        actor_frames+=1;ids={n.get('id'):n for n in tr.iter()if n.get('id')}
        names=['mou-body','mou-face','mou-arm-left','mou-arm-right','mou-hand-left','mou-hand-right','mou-foot-left','mou-foot-right','mou-eye-display-l','mou-eye-display-r']
        ok=all(x in ids for x in names)and ids.get('mou-body')is not None
        ok=ok and ids['mou-body'][0].get('d')==native_body and ids['mou-body'][0].get('fill')=='#D8F449'
        ok=ok and not any(n.get('data-character','').startswith('patch')for n in tr.iter())
        if not ok:identity_bad.append(i)
    check('native_mou_geometry_and_two_eyes_arms_mittens_feet',not identity_bad,{'actor_frames':actor_frames,'bad_frames':identity_bad,'occlusion_or_crop_not_claimed_as_visible_identity':True})
    check('canonical_rig_and_adapter_unchanged',sha(ROOT/'mou_rig.py')==sha(EP/'sources/mou_rig_original.py')=='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'and sha(EP/'sources/personnage.py')=='445ef02a57dfa58245d6298fde6bcbbad48a835b8b47e2b8fc10c39657d988b3',{'rig':sha(EP/'sources/mou_rig_original.py'),'adapter':sha(EP/'sources/personnage.py')})
    time_bad=[i for i,s in enumerate(states)if s['remaining']+s['time_state']['session_elapsed']!=1800 or s['clock_seconds']!=32400+s['time_state']['session_elapsed']]
    elapsed=[s['time_state']['session_elapsed']for s in states]
    check('clock_countdown_single_monotonic_1800_second_session',not time_bad and elapsed==sorted(elapsed)and all(s['remaining']==0 and s['clock_display']=='09:30'for s in states[552:]),{'bad_frames':time_bad,'first':elapsed[0],'last':elapsed[-1]})
    grip_rows=[]
    for t in (25.041666667,25.1,25.3,25.4,25.7,26.65,28.5,29.5):
        s=state_at(t);layout=s['layout'];h=s['actor_screen']['hands'];px,py=s['phone']['center']
        center=(px*layout['scale']+layout['tx'],py*layout['scale']+layout['ty']+layout.get('box_shift_y',0.))
        errors=[math.dist((h[side]['x'],h[side]['y']),(center[0]+sign*42*layout['scale'],center[1]+15*layout['scale']))for side,sign in [('left',-1),('right',1)]]
        actual=anchors(s['actor_screen']);anchor_errors=[math.dist(actual['hands'][side],(h[side]['x'],h[side]['y']))for side in ('left','right')]
        grip_rows.append({'t':t,'view':s['view'],'bilateral':s['phone']['bilateral'],'projected_edge_errors':errors,'native_anchor_errors':anchor_errors})
    check('bilateral_grips_share_phone_projection_in_extended_recovery',all(r['bilateral']and max(r['projected_edge_errors']+r['native_anchor_errors'])<.001 for r in grip_rows),grip_rows)
    late=states[618:];stable=all(norm(s['actor']['hands'])==norm(late[0]['actor']['hands'])and norm(s['actor']['lean'])==norm(late[0]['actor']['lean'])for s in late)
    check('seated_satisfaction_without_airborne_hold_or_26_65_reset',all(s['actor'].get('seated')and not s['actor'].get('airborne')and s['actor'].get('jump_spread',0)==0 for s in states[593:])and stable,{'stable_from_seconds':25.75,'stable_hand_and_body_state':stable,'post_recovery_frames':len(states[593:])})
    final=[s for s in states if s['t']>=27];first=framing_at(27);last=framing_at(29.5)
    check('same_frontal_perspective_paper_pullback_and_hold',all(s['view']=='phone_final'and s['completed_tasks']==0 and not s['paper_has_marks']for s in final)and first['viewport']==framing_at(27.9)['viewport']and last['viewport']==framing_at(29.2)['viewport']and first['viewport'][2]<last['viewport'][2],{'start_viewport':first['viewport'],'end_viewport':last['viewport'],'paper_completed':states[-1]['completed_tasks'],'final_clock':states[-1]['clock_display'],'no_new_3d_angle_claimed':True})
    paper_rows=[]
    for t in (0.5,27.5,29.5):
        tr=ET.fromstring(svg_at(t));boxes=[n for n in tr.iter()if(n.get('id')or'').startswith('todo-box-')]
        paper_rows.append({'t':t,'boxes':len(boxes),'all_empty':all(n.get('data-checked')=='0'for n in boxes),'header_present':any(n.get('data-text')=='TO DO'for n in tr.iter())})
    check('same_three_empty_todo_boxes_no_written_marks',all(x['boxes']==3 and x['all_empty']and x['header_present']for x in paper_rows),paper_rows)
    overlap=[]
    for t in (1.75,2.75,24.1,25.1,25.3,25.7,29.5):
        for side in(('left','right')if t>=25.1 else('right',)):
            overlap.append(dict(t=t,**visible_overlap(svg_at(t),'mou-hand-'+side,'phone')))
    for t in(3.9,4.):overlap.append(dict(t=t,**visible_overlap(svg_at(t),'mou-hand-right','start-button')))
    check('real_composed_mitten_pixels_touch_phone_and_button',all(x['removed']==1 and x['pixels']>5 for x in overlap),overlap)
    pupils=[]
    for t in(.7,5.15,8.5,13.5,19.3,23.3,24.3,25.7,29.5):
        s=state_at(t);face=face_parameters(s['actor_screen']);svg=svg_at(t);full=rgba(svg)[:,:,:3].astype(np.int16)
        for side in('l','r'):
            openness=face['open_'+side]*s['actor_screen'].get('blink',1.)
            if openness<.35:
                pupils.append({'t':t,'side':side,'intentional_closure':True,'openness':openness});continue
            tree=ET.fromstring(svg);eye=next(n for n in tree.iter()if n.get('id')=='mou-eye-display-'+side);removed=0
            for parent in list(eye.iter()):
                for child in list(parent):
                    if child.tag.endswith('ellipse')and child.get('fill')=='#2B0A24':parent.remove(child);removed+=1
            diff=np.max(np.abs(full-rgba(ET.tostring(tree))[:,:,:3].astype(np.int16)),axis=2)>3
            pupils.append({'t':t,'side':side,'removed':removed,'visible_pixels':int(np.count_nonzero(diff))})
    check('both_open_pupils_visible_in_actual_story_reading_crops',all(r.get('intentional_closure')or(r['removed']==1 and r['visible_pixels']>20)for r in pupils),pupils)
    coverage=[]
    for i in sorted(set(range(0,720,36))|{647,671,690,708,719}):
        alpha=rgba(svgs[i],270,480)[:,:,3];coverage.append({'frame_zero':i,'transparent_pixels':int(np.count_nonzero(alpha<255))})
    check('global_recrops_have_full_background_coverage',all(r['transparent_pixels']==0 for r in coverage),coverage)
    if args.reuse_preflight_lcd:
        pre=json.loads((WORK/'preflight.json').read_text())
        if pre['producer_source_sha256']!=initial:raise RuntimeError('Producer changed after preflight')
        lcd=json.loads((WORK/'lcd_all_frames.json').read_text())
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=4)as pool:lcd=list(pool.map(lcd_job,[(i,svgs[i],states[i]['layout'],states[i]['camera'])for i in range(720)]))
        (WORK/'lcd_all_frames.json').write_text(json.dumps(lcd,indent=2)+'\n')
    bad=[r for r in lcd if r['limb_pixels_in_lcd']]
    partial=[r for r in lcd if r['visible_pixels']and(r['lcd_projection'][0]<-1 or r['lcd_projection'][0]+r['lcd_projection'][2]>1081 or r['lcd_projection'][1]<-1 or r['lcd_projection'][1]+r['lcd_projection'][3]>1921)]
    check('lcd_entire_or_outside_after_global_camera_no_limbs',len(lcd)==720 and not bad and not partial,{'frames_with_visible_lcd':sum(r['visible_pixels']>0 for r in lcd),'limb_failures':bad,'partially_cropped_lcd':partial})
    cues=timeline['audio_cues'];report=json.loads((EP/'audio/mix_report.json').read_text());params,mix=wav(EP/'audio/mix.wav')
    expected_sounds=['phone_vibration','phone_place','lid_close','button','lock_engage','pencil_place','lock_release','lid_hinge']
    check('eight_motivated_foley_cues_no_rejected_voice_music_or_ticks',len(cues)==8 and [c['sound']for c in cues]==expected_sounds and not timeline.get('voice_cues')and report['voice']is False and report['music']is False and report.get('ducking')is False and report.get('compressor')is False,{'sounds':[c['sound']for c in cues],'listening_performed':False})
    stem_files=sorted((EP/'audio/stems').glob('cue_*.wav'));stem_sum=sum(wav(p)[1].astype(np.int32)for p in stem_files);stem_error=int(np.max(np.abs(stem_sum-mix.astype(np.int32))))
    check('current_48k_stereo_pcm_mix_equals_eight_cues_no_clipping',params==(48000,2,2,1440000)and len(stem_files)==8 and stem_error<=4 and np.max(np.abs(mix.astype(np.int32)))<32767 and report['sha256']==sha(EP/'audio/mix.wav')and report['timeline_sha256']==sha(EP/'chronologie.json'),{'parameters':params,'cue_stems':len(stem_files),'max_quantized_stem_error':stem_error,'peak_pcm':int(np.max(np.abs(mix.astype(np.int32)))),'mix_sha256':sha(EP/'audio/mix.wav')})
    bank=json.loads((EP/'assets/son_v2/bank.json').read_text());provenance=json.loads((EP/'assets/son_v2/provenance.json').read_text())
    origins=[{'id':s['id'],'hash_matches':sha(EP/'assets/son_v2'/s['file'])==s['sha256'],'license':s.get('license',s.get('licence')),'evidence_matches':sha(EP/'assets/son_v2'/s['license_evidence'])==s['license_evidence_sha256'],'used':s.get('used_in_v2',False)}for s in provenance['sources']]
    bank_ok=all(sha(EP/'assets/son_v2'/s['file'])==s['sha256']for s in bank['sounds'].values())
    check('eight_distinct_recorded_sources_hashes_and_license_evidence',sum(s['used']for s in origins)==8 and len({s['source']for s in bank['sounds'].values()})==8 and bank_ok and all(s['hash_matches']and s['evidence_matches']and s['license']=='CC0-1.0'for s in origins)and(EP/'assets/son_v2/LICENCES.md').exists(),{'sources':origins,'notice_file':'assets/son_v2/LICENCES.md','phone_vibration_is_disclosed_fan_motor_substitute':bank['sounds']['phone_vibration']['source']=='small_fan','audition_not_performed':True})
    refs=json.loads((EP/'controle/baseline.json').read_text());preserved={p:sha(ROOT/p)==h for p,h in refs.items()}
    check('seven_v1_and_native_rig_baselines_unchanged',len(preserved)==7 and all(preserved.values()),preserved)
    if args.final:
        video=EP/'MOU_Le_coffre_V2.mp4';mute=EP/'MOU_Le_coffre_V2_muet.mp4';pv,pm=probe(video),probe(mute)
        v=next(x for x in pv['streams']if x['codec_type']=='video');m=next(x for x in pm['streams']if x['codec_type']=='video');audio=[x for x in pv['streams']if x['codec_type']=='audio']
        fmt=all(x['width']==1080 and x['height']==1920 and x['r_frame_rate']=='24/1'and int(x['nb_frames'])==720 and abs(float(x['duration'])-30)<.001 for x in(v,m))
        check('hd_portrait_24fps_30s_sound_and_mute',fmt and len(audio)==1 and audio[0]['sample_rate']=='48000'and abs(float(audio[0]['duration'])-30)<.001 and not any(x['codec_type']=='audio'for x in pm['streams']),{'sound':sha(video),'mute':sha(mute)})
        hv,hm=stream_hash(video,'0:v:0','h264'),stream_hash(mute,'0:v:0','h264');check('identical_h264_sound_mute',hv==hm,{'sound_h264':hv,'mute_h264':hm})
        fresh_audio=WORK/'fresh_foley_audio.m4a';subprocess.run(['ffmpeg','-v','error','-y','-i',str(EP/'audio/mix.wav'),'-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(fresh_audio)],check=True)
        actual_aac=stream_hash(video,'0:a:0','adts');fresh_aac=stream_hash(fresh_audio,'0:a:0','adts');check('aac_is_current_new_foley_mix',actual_aac==fresh_aac,{'actual_aac':actual_aac,'fresh_aac':fresh_aac})
        for p in(video,mute):subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        ids=[17,64,84,94,123,328,408,479,577,606,660,708];folder=WORK/'decoded';folder.mkdir(exist_ok=True)
        select='+'.join(f'eq(n,{i})'for i in ids);subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}'",'-fps_mode','vfr',str(folder/'%02d.png')],check=True)
        board=Image.new('RGB',(1440,2120),'#FAF5EC');draw=ImageDraw.Draw(board);font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),15);rows=[]
        for j,i in enumerate(ids):
            fresh=rgba(svgs[i])[:,:,:3].astype(np.int16);decoded=np.asarray(Image.open(folder/f'{j+1:02d}.png').convert('RGB'),dtype=np.int16);err=np.abs(fresh-decoded)
            cached=np.asarray(Image.open(EP/f'work/hd/{i+1:04d}.png').convert('RGB'),dtype=np.int16)
            rows.append({'frame_zero':i,'mean_rgb_error':float(err.mean()),'p99':float(np.percentile(err,99)),'cache_max_rgb_error':int(np.max(np.abs(fresh-cached)))})
            board.paste(Image.fromarray(decoded.astype(np.uint8)).resize((360,640)),((j%4)*360,(j//4)*700));draw.text(((j%4)*360+8,(j//4)*700+651),f'f{i} / {i/FPS:.3f}s',font=font,fill='#302D35')
        board.save(WORK/'actual_hd_review.png');check('twelve_decoded_hd_frames_match_fresh_producers_and_cache',all(r['mean_rgb_error']<3 and r['p99']<=12 and r['cache_max_rgb_error']==0 for r in rows),rows)
        render=json.loads((EP/'controle/rendu_hd.json').read_text());check('render_producer_hash_current',render['source_sha256']==initial,{'render':render['source_sha256'],'current':initial})
        freeze=json.loads((EP/'controle/gel_sources.json').read_text());freeze=freeze.get('files',freeze);frozen={p:sha(ROOT/p)==h for p,h in freeze.items()};check('frozen_producer_inputs_intact',bool(frozen)and all(frozen.values()),frozen)
    final_hash=source_hash();check('producer_inputs_unchanged_during_qa',initial==final_hash,{'start':initial,'end':final_hash})
    result={'status':'passed'if all(c['passed']for c in checks)else'failed','scope':'final_hd'if args.final else'preflight','producer_source_sha256':initial,'checks':checks,'limits':['No actual audio audition, source recognition or perceived comfort certified.','Technical QA is separate from artistic critique and audience understanding.','Visible composed hand pixels support, but do not alone certify, believable limb acting.']}
    target=EP/'controle/qa.json'if args.final else WORK/'preflight.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(c['passed']for c in checks),'total':len(checks),'failed':[c['name']for c in checks if not c['passed']]}));return 0 if result['status']=='passed'else 1

if __name__=='__main__':raise SystemExit(main())
