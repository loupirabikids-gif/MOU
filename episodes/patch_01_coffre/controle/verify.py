"""Independent SVG/contact/export checks; no production file is modified.

python controle/verify.py --preflight
python controle/verify.py --video PATCH_Le_coffre.mp4 --silent PATCH_Le_coffre_muet.mp4
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
sys.path.insert(0,str(EP/'sources'))
import scene

NUMBER=r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def matrix(text):
    m=np.eye(3)
    for command,args in re.findall(r'(\w+)\(([^)]*)\)',text or ''):
        v=[float(x)for x in re.findall(NUMBER,args)];a=np.eye(3)
        if command=='translate':a[0,2]=v[0];a[1,2]=v[1]if len(v)>1 else 0.
        elif command=='scale':a[0,0]=v[0];a[1,1]=v[1]if len(v)>1 else v[0]
        elif command=='matrix':a=np.array([[v[0],v[2],v[4]],[v[1],v[3],v[5]],[0,0,1.]])
        elif command=='rotate':
            r=math.radians(v[0]);c,s=math.cos(r),math.sin(r)
            a=np.array([[c,-s,0],[s,c,0],[0,0,1.]])
            if len(v)==3:
                p=np.eye(3);p[0,2],p[1,2]=v[1:]
                q=np.eye(3);q[0,2],q[1,2]=-v[1],-v[2]
                a=p@a@q
        else:raise ValueError('Unsupported transform '+command)
        m=m@a
    return m


def points(d):
    """Sample the actual M/L/H/V/C/Q/Z paths in cuffs and paw contours."""
    tokens=re.findall(r'[A-Za-z]|'+NUMBER,d);i=0;p=(0.,0.);start=p;out=[]
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd=='Z':p=start;out.append(p);continue
        count={'M':2,'L':2,'H':1,'V':1,'C':6,'Q':4}[cmd]
        v=list(map(float,tokens[i:i+count]));i+=count
        if cmd in ('M','L'):p=tuple(v);out.append(p);start=p if cmd=='M'else start
        elif cmd=='H':p=(v[0],p[1]);out.append(p)
        elif cmd=='V':p=(p[0],v[0]);out.append(p)
        else:
            a=np.array(p);b=np.array(v[:2]);c=np.array(v[2:4]);end=np.array(v[-2:])
            for u in np.linspace(0,1,17)[1:]:
                z=(1-u)**2*a+2*(1-u)*u*b+u*u*c if cmd=='Q'else (1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*end
                out.append(tuple(z))
            p=tuple(end)
    return out


def transform_points(m,pts):return [(m@np.array([x,y,1.]))[:2]for x,y in pts]


def flatten(root):
    entries={};duplicates=[]
    def walk(node,m):
        m=m@matrix(node.get('transform',''))
        name=node.get('id')
        if name:
            if name in entries:duplicates.append(name)
            entries[name]=(node,m)
        for child in node:walk(child,m)
    walk(root,np.eye(3));return entries,duplicates


def within(p,poly):
    x,y=p;inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y)and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside


def segment_distance(p,a,b):
    p,a,b=np.asarray(p),np.asarray(a),np.asarray(b);d=b-a
    t=np.clip(np.dot(p-a,d)/max(np.dot(d,d),1.e-12),0.,1.)
    return float(np.linalg.norm(p-a-t*d))


def gap(a,b):
    if any(within(p,b)for p in a)or any(within(p,a)for p in b):return 0.
    return min(min(segment_distance(p,u,v)for u,v in zip(b,b[1:]+b[:1]))for p in a)


def state_scan():
    fail={k:[]for k in ('svg','timer','phone','grip','cuffs','paper','lid')}
    first_paper=None;max_gap=0.;max_grip=0.;n_phone=0
    for frame in range(1,481):
        t=(frame-1)/24.;svg=scene.svg_at(t);root=ET.fromstring(svg);ids,dups=flatten(root)
        references=re.findall(r'url\(#([^)]*)\)',svg)
        if dups or any(x not in ids for x in references)or any(x not in ids for x in ['patch-eye-white-l','patch-eye-white-r','patch-pupil-l','patch-pupil-r','patch-hand-left','patch-hand-right','patch-arm-left','patch-arm-right']):fail['svg'].append(frame)
        if re.search(r'\b(?:nan|inf)\b',svg,re.I):fail['svg'].append(frame)
        expected=10 if frame<=97 else max(0,14-math.floor(t+1.e-8))
        actual=int(ids['timer'][0].get('data-remaining'))
        if actual!=expected or ids['timer'][0].get('data-display')!=f'00:{expected:02d}':fail['timer'].append(frame)
        locked=ids['lock'][0].get('data-locked')=='1'
        if locked!=(4.<=t<14.):fail['timer'].append(frame)
        hidden=3.55<=t<14.2
        phone=ids.get('phone');n_phone+=phone is not None
        if hidden==(phone is not None):fail['phone'].append(frame)
        if phone:
            node,m=phone;owner=node.get('data-owner')
            holding=(1.70<=t<2.80 or t>=15.05)
            if holding:
                # The point where the palm grips the rigid phone is read from
                # actual SVG transforms, without using the producer's helper.
                pg=(m@np.array([-25.,30.,1.]))[:2]
                palm=(ids['patch-hand-right'][1]@np.array([0.,0.,1.]))[:2]
                error=float(np.linalg.norm(pg-palm));max_grip=max(max_grip,error)
                if owner!='right'or error>.002:fail['grip'].append(frame)
            elif 2.80<=t<15.05:
                center=(m@np.array([0,0,1.]))[:2]
                if owner!='box'or not(713<=center[0]<=975 and 1228<=center[1]<=1312):fail['phone'].append(frame)
            elif owner!='desk':fail['phone'].append(frame)
        lid=float(ids['lid'][0].get('data-open'))
        if 3.55<=t<14.2 and abs(lid)>1.e-5:fail['lid'].append(frame)
        if t>=14.75 and abs(lid-1)>1.e-5:fail['lid'].append(frame)
        paper=ET.tostring(ids['paper'][0])
        if first_paper is None:first_paper=paper
        if paper!=first_paper or ids['paper'][0].get('data-has-marks')!='0':fail['paper'].append(frame)
        for side in ('left','right'):
            arm,am=ids['patch-arm-'+side];cuff=next(child for child in arm if child.tag.endswith('g'))
            cm=am@matrix(cuff.get('transform'));cp=next(iter(cuff))
            cuff_poly=transform_points(cm,points(cp.get('d')))
            paw,pm=ids['patch-hand-'+side];pp=next(iter(paw))
            paw_poly=transform_points(pm,points(pp.get('d')))
            value=gap(cuff_poly,paw_poly);max_gap=max(max_gap,value)
            if value>6.8:fail['cuffs'].append({'frame':frame,'side':side,'gap_world_pixels':value})
    return fail,{'svg_frames':480,'phone_visible_frames':n_phone,'maximum_grip_error_px':max_grip,'maximum_cuff_paw_fill_gap_px':max_gap}


def continuity():
    rows=[]
    for time,part in ((1.7,'phone'),(2.8,'phone'),(15.05,'phone'),(8.05,'pencil')):
        values=[]
        for t in (time-1.e-6,time+1.e-6):
            ids,_=flatten(ET.fromstring(scene.svg_at(t)));values.append(ids[part][1])
        rows.append({'time':time,'part':part,'max_transform_delta':float(np.max(np.abs(values[0]-values[1])))})
    return rows


def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)],text=True))


def stream_hash(path):
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','h264','-'])
    return hashlib.sha256(data).hexdigest()


def compare_frames(video):
    folder=PRIVATE/'decoded';folder.mkdir(parents=True,exist_ok=True)
    frames=[1,42,68,86,97,194,265,337,362,380,466,480]
    filters='+'.join(f'eq(n\\,{f-1})'for f in frames)
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+filters,'-vsync','0',str(folder/'%03d.png')],check=True)
    result=[]
    for j,frame in enumerate(frames,1):
        actual=np.asarray(Image.open(folder/f'{j:03d}.png').convert('RGB'),dtype=np.int16)
        fresh=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=scene.svg_at((frame-1)/24).encode(),output_width=1080,output_height=1920))).convert('RGB')
        target=np.asarray(fresh,dtype=np.int16);delta=np.abs(actual-target)
        result.append({'frame':frame,'mean_abs_rgb_error':float(delta.mean()),'p99_rgb_error':float(np.quantile(delta,.99))})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight',action='store_true');p.add_argument('--video',type=Path);p.add_argument('--silent',type=Path)
    args=p.parse_args();PRIVATE.mkdir(parents=True,exist_ok=True)
    if not args.preflight and not(args.video and args.silent):p.error('Use --preflight or both --video and --silent')
    checks=[]
    def check(name,passed,evidence):checks.append({'check':name,'passed':bool(passed),'evidence':evidence})
    baseline=json.loads((EP/'controle/baseline.json').read_text())
    changed=[name for name,expected in baseline.items()if not(ROOT/name).is_file()or digest(ROOT/name)!=expected]
    check('six_original_references_unchanged',not changed,{'files':len(baseline),'changed':changed})
    fail,stats=state_scan()
    for name,failures in fail.items():check('all_480_'+name,not failures,{'failures':failures[:25],**stats})
    rows=continuity();check('rigid_prop_handoffs_continuous',all(r['max_transform_delta']<.002 for r in rows),rows)
    timeline=json.loads((EP/'chronologie.json').read_text())
    cues=timeline['audio_cues']
    check('audio_has_no_writing_music_or_voice_cues',not any(any(word in str(c).lower()for word in ('writing','music','voice','ecriture'))for c in cues),{'cue_count':len(cues),'sounds':sorted({c['sound']for c in cues})})
    if args.video:
        args.video=args.video.resolve();args.silent=args.silent.resolve()
        info=probe(args.video);mute=probe(args.silent)
        vs=[s for s in info['streams']if s['codec_type']=='video'];audio=[s for s in info['streams']if s['codec_type']=='audio']
        mv=[s for s in mute['streams']if s['codec_type']=='video'];ma=[s for s in mute['streams']if s['codec_type']=='audio']
        valid=lambda v:v.get('width')==1080 and v.get('height')==1920 and v.get('r_frame_rate')=='24/1'and int(v.get('nb_read_frames',0))==480 and abs(float(v.get('duration',0))-20)<.0001
        check('final_sound_and_silent_mp4_format',len(vs)==len(mv)==1 and valid(vs[0])and valid(mv[0])and len(audio)==1 and not ma and audio[0]['sample_rate']=='48000'and audio[0].get('channels')==2 and abs(float(audio[0].get('duration',0))-20)<.05,{'video':vs,'silent':mv,'audio':audio})
        sound_h264,silent_h264=stream_hash(args.video),stream_hash(args.silent)
        check('mux_copies_the_same_h264_picture',sound_h264==silent_h264,{'sound_h264_sha256':sound_h264,'silent_h264_sha256':silent_h264})
        with wave.open(str(EP/'audio/mix.wav'),'rb')as w:
            samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768.
            wav={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'samples_per_channel':w.getnframes(),'peak_linear':float(np.abs(samples).max())}
        check('mix_is_20_seconds_48k_stereo_without_clipping',wav['sample_rate']==48000 and wav['channels']==2 and wav['samples_per_channel']==960000 and wav['peak_linear']<.85,wav)
        bank=json.loads((EP/'assets/son/bank.json').read_text())
        provenance=json.loads((EP/'assets/son/provenance.json').read_text())
        cue_rows=json.loads((EP/'audio/cues.json').read_text())
        mix_report=json.loads((EP/'audio/mix_report.json').read_text())
        bank_mismatch=[name for name,value in bank['sounds'].items()if digest(EP/'assets/son'/value['file'])!=value['sha256']]
        original_mismatch=[value['id']for value in provenance['sources']if digest(EP/'assets/son'/value['file'])!=value['sha256']]
        wanted={str(c['id']):c for c in cues};actual={c['id']:c for c in cue_rows}
        cue_ok=set(wanted)==set(actual)and all(abs(float(actual[k]['at'])-float(v['at']))<1.e-7 and actual[k]['sound']==v['sound']and actual[k]['start_sample']==round(float(v['at'])*48000) and actual[k]['sound_sha256']==bank['sounds'][v['sound']]['sha256']for k,v in wanted.items())
        check('audio_assets_cues_and_frozen_timeline_agree',not bank_mismatch and not original_mismatch and cue_ok and mix_report['timeline_sha256']==digest(EP/'chronologie.json')and mix_report['sha256']==digest(EP/'audio/mix.wav'),{'bank_mismatches':bank_mismatch,'original_mismatches':original_mismatch,'cue_count':len(cue_rows),'cue_offsets_and_assets_match':cue_ok,'timeline_hash_matches':mix_report['timeline_sha256']==digest(EP/'chronologie.json')})
        pcm=[]
        for stem in ('foley','ui','tick'):
            with wave.open(str(EP/f'audio/stems/{stem}.wav'),'rb')as w:
                pcm.append(np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32))
        with wave.open(str(EP/'audio/mix.wav'),'rb')as w:
            mixed=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32)
        residual=int(np.max(np.abs(sum(pcm)-mixed)))
        check('three_declared_stems_reproduce_mix_with_quantization_tolerance',residual<=2,{'maximum_pcm_residual_lsb':residual,'tolerance_lsb':2,'stems':['foley','ui','tick']})
        comparisons=compare_frames(args.video)
        check('twelve_decoded_frames_match_fresh_cairo_renders',all(r['mean_abs_rgb_error']<3.5 and r['p99_rgb_error']<=16 for r in comparisons),comparisons)
    report={'status':'passed'if all(c['passed']for c in checks)else'failed','scope':'preflight_only'if args.preflight else'final_exports',
            'observed_at':datetime.now(ZoneInfo('Africa/Casablanca')).isoformat(),'checks':checks,
            'limits':['Contrôles numériques et contours sans écoute ; aucun confort sonore certifié.','La lecture du gag est réservée à la critique indépendante du montage.']}
    if args.video:report['files']={str(q.relative_to(ROOT)):digest(q)for q in (args.video,args.silent,EP/'audio/mix.wav')}
    destination=PRIVATE/'preflight.json'if args.preflight else EP/'controle/QA.json'
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not args.preflight:
        lines=['# Contrôle indépendant — PATCH / Le coffre','',f'**{report["status"]}** : {len(checks)} contrôles ciblés.','',
               'Les 480 SVG ont été examinés : compteur réel, téléphone unique et prises continues, couvercle, papier sans marques, yeux/clips et chevauchement manche/patte. Les six références protégées gardent leurs empreintes.',
               '', 'Les versions son et muette contiennent 480 images à24ips,1080×1920,20s. Le mux conserve le même flux H.264. Douze images décodées ont été comparées à des rendus Cairo frais, sans lire les PNG du cache.',
               '', 'Le WAV contient20s,48kHz stéréo, sans saturation. Il ne contient que les cues déclarés ; aucune écoute ni qualité subjective du mix n’est certifiée.',
               '', 'La critique du montage reste distincte de ces contrôles. Détails et empreintes dans QA.json.','']
        (EP/'controle/QA.md').write_text('\n'.join(lines))
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[c['check']for c in checks if not c['passed']],'report':str(destination)},ensure_ascii=False))
    if report['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
