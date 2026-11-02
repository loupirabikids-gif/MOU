"""Independent, local QA of the phone-only correction, including unchanged images."""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET
import cairosvg
import numpy as np
from PIL import Image
from scene import state_at,svg_at,phone_svg,FPS,DURATION

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
OLD=ROOT/'episodes/patch_01_coffre_v4'
WORK=EP/'work/qa';WORK.mkdir(parents=True,exist_ok=True)
WINDOWS=[(1.4,3.55),(23.2,24.7)]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def private_t(t):return any(a<=t<b for a,b in WINDOWS)
def source_hash(ep):
    h=hashlib.sha256()
    for p in sorted((ep/'sources').glob('*')):
        if p.suffix in('.py','.json') and p.name!='controle.py':h.update(p.name.encode());h.update(p.read_bytes())
    h.update((ep/'chronologie.json').read_bytes());return h.hexdigest()
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
def pixels(svg,width=1080):return cairosvg.svg2png(bytestring=svg.encode(),output_width=width,output_height=width*16//9)
def numbers_finite(obj):
    if isinstance(obj,dict):return all(numbers_finite(v)for v in obj.values())
    if isinstance(obj,(list,tuple)):return all(numbers_finite(v)for v in obj)
    if isinstance(obj,float):return math.isfinite(obj)
    return True

def baseline_states():
    code="""from pathlib import Path
import json,sys
sys.path.insert(0,sys.argv[1]);from scene import state_at
out=[]
for i in range(720):
 s=state_at(i/24);out.append({'phone':s['phone'],'deep':s['phone_deep'],'view':s['view'],'remaining':s['remaining'],'completed':s['completed_tasks'],'right':s['actor']['hands']['right'],'lid':s['lid']})
print(json.dumps(out))
"""
    return json.loads(subprocess.check_output([sys.executable,'-c',code,str(OLD/'sources')],cwd=OLD))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preflight',action='store_true');p.add_argument('--final',action='store_true');args=p.parse_args()
    if not(args.preflight or args.final):p.error('Choose --preflight or --final')
    checks=[]
    def check(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})
    states=[state_at(i/FPS)for i in range(720)];old=baseline_states()
    xmls=[svg_at(i/FPS)for i in range(720)]
    roots=[ET.fromstring(x)for x in xmls]
    unique=all(len([e.attrib['id']for e in r.iter()if'id'in e.attrib])==len({e.attrib['id']for e in r.iter()if'id'in e.attrib})for r in roots)
    check('720_finite_states_and_unique_svg_ids',len(states)==720 and all(numbers_finite(s)for s in states)and unique,{'frames':720,'fps':FPS,'duration':DURATION})
    paths=['sources/personnage.py','sources/jeu.py','sources/vues.py','sources/cadres.json','sources/palette.json','sources/scene_base.py','sources/reference_scene.py','chronologie.json','audio/mix.wav']
    unchanged={x:sha(EP/x)==sha(OLD/x)for x in paths}
    bank={str(x.relative_to(OLD)):sha(x)==sha(EP/x.relative_to(OLD))for x in (OLD/'assets').rglob('*')if x.is_file()}
    baseline=json.loads((EP/'controle/baseline.json').read_text());refs={x:sha(ROOT/x)==h for x,h in baseline.items()}
    check('rig_views_timeline_audio_bank_and_original_refs_unchanged',all(unchanged.values())and all(bank.values())and all(refs.values()),{'inputs':unchanged,'bank_files':len(bank),'bank_all_identical':all(bank.values()),'protected_refs':refs})
    errors=[]
    for i,(s,b)in enumerate(zip(states,old)):
        if s['phone']['owner']!=b['phone']['owner']or s['phone']['visible']!=b['phone']['visible']or s['phone_deep']!=b['deep']:errors.append(i)
        if math.dist(s['phone']['center'],b['phone']['center'])>1e-7 or abs(s['phone']['angle']-b['phone']['angle'])>1e-7:errors.append(i)
        if s['view']!=b['view']or s['remaining']!=b['remaining']or s['completed_tasks']!=b['completed']:errors.append(i)
    check('phone_path_ownership_depth_story_and_views_unchanged',not errors,{'bad_frames_zero':sorted(set(errors))})
    corrections=[]
    for lo,hi in WINDOWS:
        ids=[i for i in range(1,720)if lo<=i/FPS<hi and lo<=(i-1)/FPS<hi]
        nr=[abs(states[i]['actor']['hands']['right']['rotation']-states[i-1]['actor']['hands']['right']['rotation'])for i in ids]
        orr=[abs(old[i]['right']['rotation']-old[i-1]['right']['rotation'])for i in ids]
        ng=[abs(states[i]['actor']['hands']['right']['grip']-states[i-1]['actor']['hands']['right']['grip'])for i in ids]
        corrections.append({'window':[lo,hi],'new_max_wrist_degrees_per_frame':max(nr),'old_max_wrist_degrees_per_frame':max(orr),'new_max_grip_per_frame':max(ng)})
    check('wrist_and_grip_no_single_frame_snaps',all(c['new_max_wrist_degrees_per_frame']<23 and c['new_max_grip_per_frame']<.40 for c in corrections),corrections)
    jumps=[]
    for t in (1.7,2.8,24.05,24.7):
        a,b=state_at(t-1e-7),state_at(t+1e-7);jumps.append({'at':t,'phone_center_jump':math.dist(a['phone']['center'],b['phone']['center']),'paw_wrist_jump':abs(a['actor']['hands']['right']['rotation']-b['actor']['hands']['right']['rotation']),'grip_jump':abs(a['actor']['hands']['right']['grip']-b['actor']['hands']['right']['grip'])})
    check('continuous_ownership_and_cut_contacts',all(j['phone_center_jump']<.002 and j['paw_wrist_jump']<.002 and j['grip_jump']<.002 for j in jumps),jumps)
    hold=[state_at(t)for t in(2.8,2.84,2.88,2.919999)]
    retreat=[state_at(t)for t in(2.92,3.,3.1,3.2)]
    closing=[state_at(t)for t in(3.2,3.3,3.4,3.55)]
    hs=[(s['actor']['hands']['right']['x'],s['actor']['hands']['right']['y'])for s in hold]
    ys=[s['actor']['hands']['right']['y']for s in retreat];ls=[s['lid']for s in closing]
    check('settle_pause_retreat_then_lid_closes',all(math.dist(x,(857.,1300.))<1e-7 for x in hs)and all(a>=b for a,b in zip(ys,ys[1:]))and abs(ys[-1]-1095)<1e-6 and all(a>=b for a,b in zip(ls,ls[1:]))and abs(ls[0]-1)<1e-7 and abs(ls[-1])<1e-7,{'held_palms':hs,'retreat_y':ys,'lid':ls})
    aligned=state_at(24.049999)['actor']['hands']['right']['rotation']
    check('paw_oriented_before_retrieval',abs(aligned+90.)<1e-5,{'at':24.049999,'rotation':aligned})
    bad_order=[]
    for i,(s,x)in enumerate(zip(states,xmls)):
        if s['phone']['visible']and s['phone_deep']and s['view']not in('clock','paper','box_insert'):
            if not(x.index('id="patch-character-arms"')<x.index('id="phone"')<x.index('id="box-front"')<x.index('id="patch-character-hands"')):bad_order.append(i)
    check('phone_above_sleeves_below_front_and_palms',not bad_order,{'bad_frames_zero':bad_order})
    turn=[]
    for t in(24.35,24.5,24.6666666667):
        s=state_at(t);svg='<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">'+phone_svg(s)+'</svg>'
        raw=pixels(svg);(WORK/f'phone_isolated_{t:.3f}.png').write_bytes(raw)
        arr=np.asarray(Image.open(io.BytesIO(raw)).convert('RGBA'));area=int((arr[:,:,3]>0).sum())
        turn.append({'t':t,'face':s['phone']['face'],'plane_x':s['phone'].get('plane_scale_x',1.),'rendered_alpha_area':area})
    check('turn_has_real_edge_frame_and_back_before_cut',turn[0]['face']=='screen' and turn[1]['plane_x']<=.056 and turn[1]['rendered_alpha_area']<.25*min(turn[0]['rendered_alpha_area'],turn[2]['rendered_alpha_area'])and turn[2]['face']=='back'and state_at(24.7)['phone']['face']=='back',turn)
    timeline=json.loads((EP/'chronologie.json').read_text());data=(EP/'audio/mix.wav').read_bytes()
    with wave.open(io.BytesIO(data))as wav:params=(wav.getframerate(),wav.getnchannels(),wav.getsampwidth(),wav.getnframes());pcm=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2')
    stems=[]
    for f in sorted((EP/'audio/stems').glob('*.wav')):
        with wave.open(str(f))as wav:stems.append(np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.int32))
    summed=np.clip(sum(stems),-32768,32767).astype(np.int16)
    check('unchanged_30s_audio_18_cues_stems_no_clipping',params==(48000,2,2,1440000)and len(timeline['audio_cues'])==18 and np.array_equal(summed,pcm)and int(np.abs(pcm.astype(np.int32)).max())<32767,{'wav_sha256':sha(EP/'audio/mix.wav'),'cue_count':len(timeline['audio_cues']),'parameters':params,'peak_pcm':int(np.abs(pcm.astype(np.int32)).max())})
    mode='hd'if args.final else'preview'
    current_report=EP/f'controle/rendu_{mode}.json';old_report=OLD/f'controle/rendu_{mode}.json'
    if current_report.exists():
        cr=json.loads(current_report.read_text());orr=json.loads(old_report.read_text());valid=(cr['source_sha256']==source_hash(EP)and orr['source_sha256']==source_hash(OLD))
        all_ids=[i for i in range(720)if not private_t(i/FPS)];diff=[]
        for i in all_ids:
            new=EP/f'work/{mode}/{i+1:04d}.png';prior=OLD/f'work/{mode}/{i+1:04d}.png'
            if not new.exists()or not prior.exists()or sha(new)!=sha(prior):diff.append(i)
        check('all_images_outside_phone_windows_identical',valid and not diff,{'mode':mode,'cache_sources_sha_valid':valid,'protected_frame_count':len(all_ids),'different_frames_zero':diff})
    if args.final:
        video=EP/'PATCH_Le_coffre_V4_telephone.mp4';mute=EP/'PATCH_Le_coffre_V4_telephone_muet.mp4'
        pv,pm=probe(video),probe(mute);v=[s for s in pv['streams']if s['codec_type']=='video'][0];m=[s for s in pm['streams']if s['codec_type']=='video'][0];a=[s for s in pv['streams']if s['codec_type']=='audio']
        fmt=all(s['width']==1080 and s['height']==1920 and s['r_frame_rate']=='24/1'and int(s['nb_frames'])==720 and abs(float(s['duration'])-30)<.001 for s in(v,m))
        check('final_export_formats',fmt and len(a)==1 and abs(float(a[0]['duration'])-30)<.001 and not[s for s in pm['streams']if s['codec_type']=='audio'],{'video_sha256':sha(video),'mute_sha256':sha(mute),'duration':v['duration'],'frames':v['nb_frames'],'aac_present':bool(a)})
        def bitstream(p):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c','copy','-f','h264','-'])).hexdigest()
        check('same_h264_in_sound_and_mute',bitstream(video)==bitstream(mute),{'method':'SHA256 of copied H264 elementary streams'})
        def aacstream(path):return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','adts','-'])).hexdigest()
        newaac,oldaac=aacstream(video),aacstream(OLD/'PATCH_Le_coffre_V4.mp4')
        check('encoded_aac_identical_to_v4',newaac==oldaac,{'sha256':newaac,'v4_sha256':oldaac})
        ids=[40,41,67,68,70,74,575,577,578,588,590,699];expr='+'.join(f'eq(n,{i})'for i in ids);folder=WORK/'decoded';folder.mkdir(exist_ok=True)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{expr}'",'-fps_mode','vfr',str(folder/'%02d.png')],check=True)
        comparisons=[]
        for j,i in enumerate(ids):
            fresh=pixels(svg_at(i/FPS));(WORK/f'fresh_{i:04d}.png').write_bytes(fresh)
            x=np.asarray(Image.open(io.BytesIO(fresh)).convert('RGB'),dtype=np.int16);y=np.asarray(Image.open(folder/f'{j+1:02d}.png').convert('RGB'),dtype=np.int16);error=np.abs(x-y)
            comparisons.append({'frame_zero':i,'mean_error_rgb':round(float(error.mean()),4),'p99':float(np.percentile(error,99))})
        check('12_real_hd_decodes_match_fresh_renders',all(c['mean_error_rgb']<3 and c['p99']<=12 for c in comparisons),comparisons)
        gp=EP/'controle/gel_sources.json'
        gel=json.loads(gp.read_text())if gp.exists()else{'files':{}};gs={k:sha(ROOT/k)==h for k,h in gel['files'].items()}
        check('frozen_producers_unchanged',bool(gs)and all(gs.values()),gs)
    result={'status':'passed'if all(x['passed']for x in checks)else'failed','scope':'final_hd'if args.final else'preflight_preview','checks':checks,'limits':['Contrôle technique ciblé ; la critique visuelle indépendante décide de la lisibilité des gestes.','Aucune audition ni confort sonore certifié.','Identité PNG hors fenêtres contrôlée avant encodage ; le MP4 compressé peut présenter de petites différences ailleurs.']}
    target=EP/'controle/qa.json'if args.final else WORK/'preflight.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(x['passed']for x in checks),'total':len(checks),'failed':[x['name']for x in checks if not x['passed']]}))
    return 0 if result['status']=='passed'else 1

if __name__=='__main__':raise SystemExit(main())
