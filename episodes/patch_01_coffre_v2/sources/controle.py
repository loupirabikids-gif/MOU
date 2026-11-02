"""Independent targeted checks for the thirty-minute PATCH revision.

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


def source_scan():
    issues={k:[] for k in ('svg_structure','story_time_and_countdown','captions_and_units','paper_goal','phone_box_and_grip')}
    records=[];last_elapsed=-1;normal_paper=None;paper_insert_frames=0;max_grip=0.
    checks=scene.TIMELINE['time_representation']['minute_checks']
    starts={int(c['frame_start'])-1:c for c in checks}
    current_minute=0;start_index=0
    for index in range(720):
        t=index/24.;s=scene.state_at(t);svg=scene.svg_at(t);root,ids,dups=ids_of(svg)
        if index in starts:current_minute=starts[index]['elapsed_minute'];start_index=index
        expected_elapsed=(0. if index<96 else t-4 if index<144 else current_minute*60+(index-start_index)/24 if index<528 else 1799+(index-528)/24 if index<552 else 1800+(index-552)/24)
        expected_remaining=1800 if index<96 else max(0,math.ceil(1800-expected_elapsed-1.e-8))
        expected_display=f'{expected_remaining//60:02d}:{expected_remaining%60:02d}'
        if abs(s['story_elapsed_seconds']-expected_elapsed)>1.e-7 or s['story_elapsed_seconds']<last_elapsed or s['display']!=expected_display or s['locked']!=(96<=index<552):issues['story_time_and_countdown'].append(index+1)
        last_elapsed=s['story_elapsed_seconds']
        if dups or re.search(r'\b(?:nan|inf)\b',svg,re.I) or any(x not in ids for x in re.findall(r'url\(#([^)]*)\)',svg)):issues['svg_structure'].append(index+1)
        paper=ids.get('paper');boxes=[ids.get(f'todo-box-{i}') for i in range(3)]
        if paper is None or paper.get('data-completed')!='0' or paper.get('data-has-marks')!='0' or any(b is None or b.get('data-checked')!='0' for b in boxes) or ids.get('todo-header') is None or ids['todo-header'].get('data-text')!='TO DO':issues['paper_goal'].append(index+1)
        if s['paper_insert']:
            paper_insert_frames+=1
            if any(x in ids for x in ('phone','timer','patch-eye-white-l')):issues['svg_structure'].append(index+1)
        else:
            required=['patch-eye-white-l','patch-eye-white-r','patch-pupil-l','patch-pupil-r','patch-hand-left','patch-hand-right','patch-arm-left','patch-arm-right','wall-clock','timer','box-duration','box-units']
            if any(x not in ids for x in required):issues['svg_structure'].append(index+1)
            timer=ids.get('timer')
            if timer is not None and (timer.get('data-display')!=expected_display or int(timer.get('data-remaining'))!=expected_remaining):issues['story_time_and_countdown'].append(index+1)
            if ids['box-duration'].get('data-text')!='30 MIN' or ids['box-units'].get('data-text')!='MIN:SEC':issues['captions_and_units'].append(index+1)
            paper_bytes=ET.tostring(paper)
            if normal_paper is None:normal_paper=paper_bytes
            if paper_bytes!=normal_paper:issues['paper_goal'].append(index+1)
            if abs(float(ids['wall-clock'].get('data-elapsed-seconds'))-expected_elapsed)>1.e-6:issues['story_time_and_countdown'].append(index+1)
            hidden=3.55<=t<23.2
            phone=ids.get('phone')
            if hidden==(phone is not None):issues['phone_box_and_grip'].append(index+1)
            if 3.55<=t<23.2 and abs(float(ids['lid'].get('data-open')))>1.e-5:issues['phone_box_and_grip'].append(index+1)
            if t>=23.75 and abs(float(ids['lid'].get('data-open'))-1.)>1.e-5:issues['phone_box_and_grip'].append(index+1)
            if phone is not None and (1.7<=t<2.8 or t>=24.05):
                # Independently reconstruct rigid phone contact from SVG translate/rotate.
                v=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)',phone.get('transform'))]
                x,y,ang=v[:3];ang=math.radians(ang)
                contact=(x-25*math.cos(ang)-30*math.sin(ang),y-25*math.sin(ang)+30*math.cos(ang))
                palm=s['actor']['hands']['right'];error=math.hypot(contact[0]-palm['x'],contact[1]-palm['y']);max_grip=max(max_grip,error)
                if phone.get('data-owner')!='right' or error>.002:issues['phone_box_and_grip'].append(index+1)
        caption=ids.get('time-caption');actual='' if caption is None else caption.get('data-caption')
        expected_caption=''
        if 4<=t<5.2:expected_caption='30 MINUTES'
        if 6<=t<7.25:expected_caption='1 MIN LATER'
        elif 8<=t<22:expected_caption=f'{min(30,int(expected_elapsed//60))} MIN ELAPSED'
        elif 22<=t<23:expected_caption='LAST SECOND'
        elif 23<=t<25.4 or t>=27.9:expected_caption='30 MIN LATER'
        if actual!=expected_caption:issues['captions_and_units'].append(index+1)
        records.append({'t':t,'gaze':s['actor']['gaze'],'left_y':s['actor']['hands']['left']['y'],'pencil_held':s['pencil_held']})
    minutes=[]
    for c,nextc in zip(checks,checks[1:]+[{'frame_start':529}]):
        seq=records[c['frame_start']-1:nextc['frame_start']-1]
        x=[r['gaze'][0] for r in seq];m=c['elapsed_minute']
        row={'minute':m,'frame_start':c['frame_start'],'frames':len(seq),'gaze_x_first':x[0],'gaze_x_last':x[-1],'gaze_x_max':max(x),'gaze_range':max(x)-min(x)}
        if m<3:row.update(pencil_y_first=seq[0]['left_y'],pencil_y_last=seq[-1]['left_y'],returned_to_paper=x[-1]<0 and seq[-1]['left_y']>seq[0]['left_y']+15)
        minutes.append(row)
    return issues,{'frames':720,'paper_insert_frames':paper_insert_frames,'maximum_grip_error_px':max_grip},minutes


def frame_comparisons(video):
    folder=PRIVATE/'fresh_decoded';folder.mkdir(parents=True,exist_ok=True)
    frames=[1,68,86,97,145,190,239,295,495,529,578,651]
    filters='+'.join(f'eq(n\\,{f-1})'for f in frames)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+filters,'-fps_mode','vfr',str(folder/'%03d.png')],check=True)
    rows=[]
    for j,frame in enumerate(frames,1):
        actual=np.asarray(Image.open(folder/f'{j:03d}.png').convert('RGB'),dtype=np.int16)
        rendered=cairosvg.svg2png(bytestring=scene.svg_at((frame-1)/24).encode(),output_width=1080,output_height=1920)
        fresh=np.asarray(Image.open(io.BytesIO(rendered)).convert('RGB'),dtype=np.int16)
        delta=np.abs(actual-fresh)
        rows.append({'frame':frame,'mean_abs_rgb_error':float(delta.mean()),'p99_rgb_error':float(np.quantile(delta,.99))})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preflight',action='store_true');p.add_argument('--final',action='store_true');args=p.parse_args()
    if not args.preflight and not args.final:p.error('Choose --preflight or --final')
    PRIVATE.mkdir(parents=True,exist_ok=True);checks=[]
    def check(name,passed,evidence):checks.append({'check':name,'passed':bool(passed),'evidence':evidence})
    baseline=json.loads((EP/'controle/baseline.json').read_text());changed=[n for n,h in baseline.items()if digest(ROOT/n)!=h]
    check('v1_and_concept_untouched',not changed,{'files':len(baseline),'changed':changed})
    check('same_patch_rig',digest(EP/'sources/personnage.py')==baseline['episodes/patch_01_coffre/sources/personnage.py'],{'sha256':digest(EP/'sources/personnage.py')})
    issues,stats,minutes=source_scan()
    for name,failures in issues.items():check(name,not failures,{'failing_frames':failures[:25],**stats})
    check('all_29_minutes_have_directed_glances',len(minutes)==29 and [r['minute']for r in minutes]==list(range(1,30)) and all(r['gaze_range']>.45 for r in minutes if r['minute']!=3),minutes)
    check('first_two_checks_return_to_work',all(r.get('returned_to_paper') for r in minutes[:2]),minutes[:2])
    check('last_three_minute_values_held_longer',all(r['frames']>=16 for r in minutes[-3:]),minutes[-3:])
    cues=scene.TIMELINE['audio_cues'];bank=json.loads((EP/'assets/son/bank.json').read_text());provenance=json.loads((EP/'assets/son/provenance.json').read_text());cue_rows=json.loads((EP/'audio/cues.json').read_text());mix_report=json.loads((EP/'audio/mix_report.json').read_text())
    actual={c['id']:c for c in cue_rows};wanted={c['id']:c for c in cues}
    mismatches=[name for name,v in bank['sounds'].items()if digest(EP/'assets/son'/v['file'])!=v['sha256']]+[v['id']for v in provenance['sources']if digest(EP/'assets/son'/v['file'])!=v['sha256']]
    cue_ok=set(actual)==set(wanted) and all(actual[k]['sound']==v['sound'] and abs(actual[k]['at']-v['at'])<1e-8 and actual[k]['start_sample']==round(v['at']*48000) and actual[k]['sound_sha256']==bank['sounds'][v['sound']]['sha256'] for k,v in wanted.items())
    check('audio_assets_18_cues_and_frozen_timeline_agree',len(cues)==18 and not mismatches and cue_ok and mix_report['timeline_sha256']==digest(EP/'chronologie.json') and mix_report['sha256']==digest(EP/'audio/mix.wav'),{'cue_count':len(cues),'asset_mismatches':mismatches,'cue_offsets_match':cue_ok})
    mixed,meta=pcm(EP/'audio/mix.wav');peak=int(np.max(np.abs(mixed)));check('pcm_30_seconds_stereo_48k_unclipped',meta=={'sample_rate':48000,'channels':2,'frames':1440000,'bits':16} and peak<27853,{**meta,'peak_linear':peak/32768,'clipped_samples':int(np.count_nonzero(np.abs(mixed)>=32767))})
    residual=int(np.max(np.abs(sum(pcm(EP/f'audio/stems/{s}.wav')[0]for s in ('foley','ui','tick'))-mixed)))
    check('stems_recombine_with_quantization_tolerance',residual<=2,{'maximum_residual_lsb':residual})
    if args.final:
        video=EP/'PATCH_Le_coffre_30min.mp4';silent=EP/'PATCH_Le_coffre_30min_muet.mp4'
        a,b=probe(video),probe(silent)
        sv=[v for v in a['streams']if v['codec_type']=='video'];mv=[v for v in b['streams']if v['codec_type']=='video'];sa=[v for v in a['streams']if v['codec_type']=='audio'];ma=[v for v in b['streams']if v['codec_type']=='audio']
        valid=lambda v:v['width']==1080 and v['height']==1920 and v['r_frame_rate']=='24/1' and int(v['nb_read_frames'])==720 and abs(float(v['duration'])-30)<1e-6
        check('hd_sound_and_silent_exports',len(sv)==len(mv)==1 and valid(sv[0]) and valid(mv[0]) and len(sa)==1 and not ma and sa[0]['sample_rate']=='48000' and sa[0]['channels']==2 and abs(float(sa[0]['duration'])-30)<.05,{'sound_video':sv,'silent_video':mv,'audio':sa})
        h1,h2=stream_hash(video),stream_hash(silent);check('sound_and_silent_same_h264',h1==h2,{'sound_h264_sha256':h1,'silent_h264_sha256':h2})
        comparisons=frame_comparisons(video);check('12_decoded_hd_frames_match_independent_fresh_renders',all(r['mean_abs_rgb_error']<3.5 and r['p99_rgb_error']<=16 for r in comparisons),comparisons)
    report={'status':'passed'if all(c['passed']for c in checks)else'failed','scope':'final_exports'if args.final else'preflight','observed_at':datetime.now(ZoneInfo('Africa/Casablanca')).isoformat(),'checks':checks,'limits':['Contrôles numériques sans écoute ni confort sonore certifié.','Le mouvement mesuré des pupilles ne prouve pas la compréhension ou la comédie ; critique distincte du vrai montage.']}
    if args.final:report['files']={str(q.relative_to(ROOT)):digest(q)for q in (video,silent,EP/'audio/mix.wav',EP/'chronologie.json')}
    dest=EP/'controle/qa.json'if args.final else PRIVATE/'preflight.json';dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['check']for c in checks if not c['passed']],'report':str(dest)},ensure_ascii=False))
    if report['status']!='passed':raise SystemExit(1)

if __name__=='__main__':main()
