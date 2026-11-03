"""Independent checks for recasting the lockbox episode with the native MOU.

Run only after producer freeze. Pixel checks and decoded pictures demonstrate
integration; they are not an audition or certification of comic quality.
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
import re
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scene import state_at, svg_at, FPS, DURATION
from personnage import anchors, character_svg, face_parameters
import mou_rig_original as rig

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
OLD=ROOT/'episodes/patch_01_coffre_v7'
WORK=EP/'work/qa'
NS='{http://www.w3.org/2000/svg}'
LIMB_PARTS={'continuous-mou-arm','mou-arm','mou-hand','mitten-paw','attached-sleeve'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def norm(value):return json.loads(json.dumps(value))
def finite(value):
    if isinstance(value,dict):return all(finite(x) for x in value.values())
    if isinstance(value,(tuple,list)):return all(finite(x) for x in value)
    return not isinstance(value,float) or math.isfinite(value)


def source_hash():
    h=hashlib.sha256()
    for p in sorted((EP/'sources').glob('*')):
        if p.suffix in ('.py','.json') and p.name!='controle.py':h.update(p.name.encode());h.update(p.read_bytes())
    h.update((EP/'chronologie.json').read_bytes())
    return h.hexdigest()


def previous_states():
    code="import sys,json;sys.path.insert(0,sys.argv[1]);from scene import state_at;print(json.dumps([state_at(i/24)for i in range(720)]))"
    return json.loads(subprocess.check_output([sys.executable,'-c',code,str(OLD/'sources')],cwd=OLD))


def rgba(svg,width=1080,height=1920):
    raw=cairosvg.svg2png(bytestring=svg.encode() if isinstance(svg,str) else svg,output_width=width,output_height=height)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'))


def wav(path):
    with wave.open(str(path)) as w:
        params=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy().reshape(-1,w.getnchannels())
    return params,pcm


def isolated(tree, target, only_ellipses=False):
    """Keep the actual target's complete ancestor transform chain and defs."""
    path=[]
    def walk(node,parents):
        if node.get('id')==target:
            path.extend(parents+[node]);return True
        return any(walk(child,parents+[node]) for child in node)
    if not walk(tree,[]):raise ValueError('Missing rendered part '+target)
    out=ET.Element(tree.tag,tree.attrib)
    for node in tree.iter():
        if node.tag.endswith('defs'):out.append(deepcopy(node))
    current=out
    for ancestor in path[1:-1]:
        child=ET.SubElement(current,ancestor.tag,ancestor.attrib);current=child
    part=deepcopy(path[-1])
    if only_ellipses:
        for node in list(part):
            if not node.tag.endswith('ellipse'):part.remove(node)
    current.append(part)
    return ET.tostring(out)


def lcd_job(args):
    frame,svg,layout=args
    x=754.*layout['scale']+layout['tx']+layout.get('box_shift_x',0.)
    y=1335.*layout['scale']+layout['ty']+layout.get('box_shift_y',0.)
    scale=layout['scale'];w=200.*scale;h=86.*scale
    row={'frame_zero':frame,'visible_pixels':0,'limb_pixels_in_lcd':0}
    tree=ET.fromstring(svg)
    if x>=1080 or x+w<=0 or y>=1920 or y+h<=0 or not any(n.get('id')=='timer' for n in tree.iter()):return row
    tree.set('viewBox',f'{x} {y} {w} {h}');tree.set('width','200');tree.set('height','86')
    normal=rgba(ET.tostring(tree),200,86)[:,:,:3].astype(np.int16)
    bare=deepcopy(tree);removed=0
    for parent in list(bare.iter()):
        for child in list(parent):
            if child.get('data-part') in LIMB_PARTS:parent.remove(child);removed+=1
    empty=rgba(ET.tostring(bare),200,86)[:,:,:3].astype(np.int16)
    yy,xx=np.mgrid[:86,:200]
    visible=(x+(xx+.5)*scale>=0)&(x+(xx+.5)*scale<1080)&(y+(yy+.5)*scale>=0)&(y+(yy+.5)*scale<1920)
    visible&=(xx>=3)&(xx<197)&(yy>=3)&(yy<83)
    delta=np.max(np.abs(normal-empty),axis=2)
    row.update(visible_pixels=int(visible.sum()),limb_pixels_in_lcd=int(np.count_nonzero(visible&(delta>3))),removed_parts=removed)
    return row


def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def stream_hash(path,kind,fmt):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map',kind,'-c','copy','-f',fmt,'-'])).hexdigest()


def visible_overlap(svg, hand_id, object_id):
    """Pixels truly repainted by the foreground hand over a prop's projection."""
    tree=ET.fromstring(svg);full=rgba(svg)[:,:,:3].astype(np.int16)
    obj=rgba(isolated(tree,object_id));mask=obj[:,:,3]>230
    bare=deepcopy(tree);removed=0
    for parent in list(bare.iter()):
        for child in list(parent):
            if child.get('id')==hand_id:parent.remove(child);removed+=1
    pixels=rgba(ET.tostring(bare))[:,:,:3].astype(np.int16)
    changed=np.max(np.abs(full-pixels),axis=2)>3
    return {'hand_id':hand_id,'object_id':object_id,'removed_parts':removed,
            'visible_hand_pixels_over_prop':int(np.count_nonzero(mask&changed))}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight',action='store_true');p.add_argument('--final',action='store_true')
    p.add_argument('--reuse-preflight-lcd',action='store_true')
    args=p.parse_args()
    if not (args.preflight or args.final):p.error('Use --preflight or --final after producer freeze')
    WORK.mkdir(parents=True,exist_ok=True);checks=[]
    initial_hash=source_hash()
    def check(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})

    states=[state_at(i/FPS)for i in range(720)]
    svgs=[svg_at(i/FPS)for i in range(720)]
    trees=[ET.fromstring(x)for x in svgs]
    if not any(n.get('data-rig')=='mou_rig_original'for n in trees[0].iter()):
        raise RuntimeError('Native MOU renderer not ready; refusing placeholder QA')
    old=previous_states();timeline=json.loads((EP/'chronologie.json').read_text())
    check('30_seconds_720_finite_unique_id_states',FPS==24 and DURATION==30 and all(finite(s)for s in states) and
          all(len(ids)==len(set(ids))for ids in [[n.get('id')for n in tree.iter()if n.get('id')]for tree in trees]),
          {'frames':len(states),'fps':FPS,'duration':DURATION})
    native=ET.fromstring('<svg>'+rig.character_fragment(rig.DEFAULT_POSE,'qa-native')+'</svg>')
    native_body=next(n for n in native if n.get('id')=='body')[0].get('d')
    identities=[];identity_bad=[]
    for i,tree in enumerate(trees):
        actor_present=states[i]['view']not in ('clock','paper','box_insert')
        ids={n.get('id'):n for n in tree.iter()if n.get('id')}
        if actor_present:
            expected=['mou-body','mou-face','mou-arm-left','mou-arm-right','mou-hand-left','mou-hand-right','mou-foot-left','mou-foot-right','mou-eye-display-l','mou-eye-display-r']
            ok=all(x in ids for x in expected)
            body=ids.get('mou-body')
            ok=ok and body is not None and body[0].get('d')==native_body and body[0].get('fill')=='#D8F449'
            ok=ok and not any(n.get('data-character','').startswith('patch')for n in tree.iter())
            if not ok:identity_bad.append(i)
            identities.append(i)
        elif any(n.get('data-character','').startswith('mou')for n in tree.iter()):identity_bad.append(i)
    check('native_lime_body_two_eyes_two_continuous_arms_hands_and_feet',not identity_bad,
          {'actor_frames':len(identities),'bad_frames':identity_bad,'native_body_path_unchanged':not identity_bad,
           'source_rig_sha256':sha(ROOT/'mou_rig.py'),'included_rig_sha256':sha(EP/'sources/mou_rig_original.py')})
    check('canonical_mou_rig_included_byte_for_byte',sha(ROOT/'mou_rig.py')==sha(EP/'sources/mou_rig_original.py'),
          {'original':sha(ROOT/'mou_rig.py'),'copy':sha(EP/'sources/mou_rig_original.py')})
    prop_keys=['story_elapsed_seconds','remaining','display','clock_seconds','clock_display','time_state','view','lid','phone','phone_deep','completed_tasks']
    prop_bad=[{'frame_zero':i,'key':k}for i,(s,o)in enumerate(zip(states,old))for k in prop_keys if norm(s[k])!=o[k]]
    check('story_views_timer_clock_phone_lid_and_blank_work_preserved',not prop_bad,{'differences':prop_bad})
    time_bad=[i for i,s in enumerate(states)if s['remaining']+s['time_state']['session_elapsed']!=1800 or s['clock_seconds']!=32400+s['time_state']['session_elapsed']]
    check('timer_clock_share_integer_session_and_freeze_at_thirty_minutes',not time_bad and all(s['remaining']==0 and s['clock_display']=='09:30'for s in states[552:]),{'bad_frames':time_bad})

    contact_rows=[]
    for t in (1.75,2.8,3.9,13.5,19.3,24.08,25.3,28.5):
        s=state_at(t);a=anchors(s['actor_screen'])
        errors={side:math.dist(a['hands'][side],(s['actor_screen']['hands'][side]['x'],s['actor_screen']['hands'][side]['y']))for side in ('left','right')}
        contact_rows.append({'t':t,'actual_mou_grip_to_world_target_error':errors,'phone_owner':s['phone']['owner'],'phone_bilateral':s['phone']['bilateral']})
    check('actual_mou_grip_anchors_follow_accessory_targets',all(max(x['actual_mou_grip_to_world_target_error'].values())<.001 for x in contact_rows),contact_rows)
    two_hand=[]
    for t in (25.3,25.7,28.5,29.5):
        s=state_at(t);h=s['actor']['hands'];center=s['phone']['center']
        errors=[math.dist((h[side]['x'],h[side]['y']),(center[0]+sign*42.,center[1]+15.))for side,sign in [('left',-1),('right',1)]]
        two_hand.append({'t':t,'bilateral':s['phone']['bilateral'],'edge_errors':errors})
    check('phone_recovered_and_held_with_both_mou_hands',all(x['bilateral'] and max(x['edge_errors'])<.001 for x in two_hand),two_hand)

    overlap=[]
    for t in (1.75,2.75,24.1,25.3,28.5):
        for side in (('left','right')if t>=25.3 else('right',)):
            overlap.append(dict(t=t,**visible_overlap(svg_at(t),'mou-hand-'+side,'phone')))
    for t in (3.9,4.):overlap.append(dict(t=t,**visible_overlap(svg_at(t),'mou-hand-right','start-button')))
    check('visible_mou_mitten_pixels_meet_phone_and_press_button',all(x['removed_parts']==1 and x['visible_hand_pixels_over_prop']>5 for x in overlap),overlap)

    # Delete only the pupil in the actual composed scene. A source eye can
    # exist yet be covered by a lid/box or fall outside the frame.
    pupil_rows=[]
    for t in (.7,4.875,13.5,19.3,23.3,25.3,28.5):
        s=state_at(t);f=face_parameters(s['actor_screen']);svg=svg_at(t);full=rgba(svg)[:,:,:3].astype(np.int16)
        for side in ('l','r'):
            openness=f['open_'+side]*s['actor_screen'].get('blink',1.)
            if openness<.35:
                pupil_rows.append({'t':t,'side':side,'skipped':'intentional eyelid closure','native_openness':openness})
                continue
            tree=ET.fromstring(svg)
            eye=next(n for n in tree.iter()if n.get('id')=='mou-eye-display-'+side)
            removed=0
            for parent in list(eye.iter()):
                for child in list(parent):
                    if child.tag.endswith('ellipse')and child.get('fill')=='#2B0A24':
                        parent.remove(child);removed+=1
            bare=rgba(ET.tostring(tree))[:,:,:3].astype(np.int16)
            changed=int(np.count_nonzero(np.max(np.abs(full-bare),axis=2)>3))
            pupil_rows.append({'t':t,'side':side,'removed_pupil_elements':removed,'visible_pupil_pixels':changed})
    check('both_pupils_actually_visible_at_open_eye_story_reading_poses',all(x.get('skipped')or(x['removed_pupil_elements']==1 and x['visible_pupil_pixels']>20) for x in pupil_rows),pupil_rows)

    foot_rows=[]
    for t in (25.3,25.7,26.3):
        svg=svg_at(t);tree=ET.fromstring(svg);full=rgba(svg)[:,:,:3].astype(np.int16)
        for side in ('left','right'):
            pad=rgba(isolated(tree,'mou-foot-'+side,True));mask=pad[:,:,3]>245
            matched=mask&(np.max(np.abs(full-pad[:,:,:3].astype(np.int16)),axis=2)<4)
            foot_rows.append({'t':t,'side':side,'expected_pad_pixels':int(mask.sum()),'visible_pad_pixels':int(matched.sum()),'visible_fraction':float(matched.sum()/max(1,mask.sum()))})
    check('two_small_dark_feet_actually_visible_in_joy',all(x['expected_pad_pixels']>100 and x['visible_fraction']>.80 for x in foot_rows),foot_rows)

    if args.reuse_preflight_lcd:
        pre=json.loads((WORK/'preflight.json').read_text())
        if pre['status']!='passed' or pre['producer_source_sha256']!=source_hash():raise RuntimeError('Cannot reuse LCD checks after producer changes')
        lcd=json.loads((WORK/'lcd_all_frames.json').read_text());assert len(lcd)==720
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=4)as pool:
            lcd=list(pool.map(lcd_job,[(i,svgs[i],states[i]['layout'])for i in range(720)]))
        (WORK/'lcd_all_frames.json').write_text(json.dumps(lcd,indent=2)+'\n')
    lcd_bad=[x for x in lcd if x['limb_pixels_in_lcd']]
    check('all_drawn_visible_lcd_frames_clear_of_composited_mou_limbs',not lcd_bad,
          {'frames_considered':720,'frames_with_drawn_visible_lcd':sum(x['visible_pixels']>0 for x in lcd),'failures':lcd_bad,'method':'True composed LCD minus same view without MOU arm/hand groups; contact button excluded.'})

    base_timeline=json.loads((OLD/'chronologie.json').read_text())
    report=json.loads((EP/'audio/mix_report.json').read_text());params,mix=wav(EP/'audio/mix.wav')
    stems=sorted((EP/'audio/stems').glob('*.wav'));stem_sum=sum(wav(x)[1].astype(np.int32)for x in stems)
    stem_error=int(np.max(np.abs(stem_sum-mix.astype(np.int32))))
    check('18_existing_foley_cues_without_rejected_synthetic_voices_or_music',timeline['audio_cues']==base_timeline['audio_cues'] and len(timeline['audio_cues'])==18 and not timeline.get('voice_cues')and
          report['voice']is False and report['music']is False and not (EP/'audio/stems/voice.wav').exists(),
          {'cues':len(timeline['audio_cues']),'voice':report['voice'],'music':report['music'],'stems':[x.name for x in stems]})
    check('pcm_mix_stems_no_clips_and_current_timeline',params==(48000,2,2,1440000)and stem_error<=1 and int(np.max(np.abs(mix.astype(np.int32))))<32767 and
          report['sha256']==sha(EP/'audio/mix.wav')and report['timeline_sha256']==sha(EP/'chronologie.json')and sha(EP/'audio/mix.wav')=='b09ec672aba907961c386be03e2df22c13f36d9ee5d39d94171ad5a3c364ad41',
          {'parameters':params,'max_stem_pcm_error':stem_error,'peak_pcm':int(np.max(np.abs(mix.astype(np.int32)))),'mix_sha256':sha(EP/'audio/mix.wav'),'listening_performed':False})
    refs=json.loads((EP/'controle/baseline.json').read_text());preserved={x:sha(ROOT/x)==h for x,h in refs.items()}
    check('previous_patch_mou_films_rig_and_reference_unchanged',bool(preserved)and all(preserved.values()),preserved)

    if args.final:
        video=EP/'MOU_Le_coffre.mp4';mute=EP/'MOU_Le_coffre_muet.mp4';pv,pm=probe(video),probe(mute)
        v=next(x for x in pv['streams']if x['codec_type']=='video');m=next(x for x in pm['streams']if x['codec_type']=='video');audio=[x for x in pv['streams']if x['codec_type']=='audio']
        fmt=all(x['width']==1080 and x['height']==1920 and x['r_frame_rate']=='24/1'and int(x['nb_frames'])==720 and abs(float(x['duration'])-30)<.001 for x in (v,m))
        check('vertical_hd_24fps_30_seconds_audio_and_mute',fmt and len(audio)==1 and abs(float(audio[0]['duration'])-30)<.001 and not any(x['codec_type']=='audio'for x in pm['streams']),{'video_sha256':sha(video),'mute_sha256':sha(mute)})
        hv,hm=stream_hash(video,'0:v:0','h264'),stream_hash(mute,'0:v:0','h264')
        check('identical_h264_in_sound_and_mute',hv==hm,{'sound_h264_sha256':hv,'mute_h264_sha256':hm})
        fresh_audio=WORK/'fresh_foley_audio.m4a'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(EP/'audio/mix.wav'),'-c:a','aac','-b:a','192k','-t','30','-movflags','+faststart',str(fresh_audio)],check=True)
        actual_aac=stream_hash(video,'0:a:0','adts');fresh_aac=stream_hash(fresh_audio,'0:a:0','adts')
        check('actual_mp4_audio_is_current_foley_without_stale_vocal_mux',actual_aac==fresh_aac,
              {'actual_aac_sha256':actual_aac,'fresh_foley_aac_sha256':fresh_aac})
        for file in (video,mute):subprocess.run(['ffmpeg','-v','error','-i',str(file),'-f','null','-'],check=True)
        ids=[17,64,84,94,110,324,432,464,559,577,608,685];folder=WORK/'decoded';folder.mkdir(exist_ok=True)
        select='+'.join(f'eq(n,{i})'for i in ids)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{select}'",'-fps_mode','vfr',str(folder/'%02d.png')],check=True)
        board=Image.new('RGB',(1440,2120),'#FAF5EC');draw=ImageDraw.Draw(board);font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),15);rows=[]
        for j,i in enumerate(ids):
            fresh=rgba(svgs[i])[:,:,:3].astype(np.int16);decoded=np.asarray(Image.open(folder/f'{j+1:02d}.png').convert('RGB'),dtype=np.int16);error=np.abs(fresh-decoded)
            rows.append({'frame_zero':i,'mean_rgb_error':float(error.mean()),'p99':float(np.percentile(error,99))})
            board.paste(Image.fromarray(decoded.astype(np.uint8)).resize((360,640)),((j%4)*360,(j//4)*700));draw.text(((j%4)*360+8,(j//4)*700+651),f'f{i} / {i/FPS:.3f}s',font=font,fill='#302D35')
        board.save(WORK/'actual_hd_review.png')
        check('12_decoded_hd_frames_match_current_fresh_render',all(x['mean_rgb_error']<3 and x['p99']<=12 for x in rows),rows)
        render=json.loads((EP/'controle/rendu_hd.json').read_text())
        check('final_renderer_producer_hash_current',render['source_sha256']==source_hash(),{'render':render['source_sha256'],'current':source_hash()})
        freeze=json.loads((EP/'controle/gel_sources.json').read_text());freeze=freeze.get('files',freeze)
        frozen={x:sha(ROOT/x)==h for x,h in freeze.items()}
        check('frozen_producers_intact',bool(frozen)and all(frozen.values()),frozen)

    current_hash=source_hash()
    check('producer_inputs_unchanged_during_qa',initial_hash==current_hash,{'start':initial_hash,'end':current_hash})
    result={'status':'passed'if all(x['passed']for x in checks)else'failed','scope':'final_hd'if args.final else'preflight','producer_source_sha256':initial_hash,'checks':checks,
            'limits':['No audio audition or perceived naturalness claimed.','Native geometry, composited pixels and decoded frames are inspected separately from audience or comic quality.','Grip anchors alone do not prove a believable pose; independent visual critique covers contact and limb continuity.']}
    target=EP/'controle/qa.json'if args.final else WORK/'preflight.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(x['passed']for x in checks),'total':len(checks),'failed':[x['name']for x in checks if not x['passed']]}))
    return 0 if result['status']=='passed'else 1


if __name__=='__main__':raise SystemExit(main())
