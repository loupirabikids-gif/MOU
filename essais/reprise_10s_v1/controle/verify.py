"""Targeted independent checks for Poids plume, without touching producers.

Run --preflight before HD; run --video FINAL.mp4 after the export is frozen.
The final check renders fresh SVG frames; it never trusts the renderer cache.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
PRIVATE=EP/'work/qa'
sys.path.insert(0,str(EP/'sources'))
import scene


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def finite(value):
    if isinstance(value,dict):return all(finite(v) for v in value.values())
    if isinstance(value,(list,tuple)):return all(finite(v) for v in value)
    if isinstance(value,(int,float)):return math.isfinite(value)
    return True


def path_samples(path):
    """Read this native M/C/Z path from the actual SVG, independently of rig helpers."""
    tokens=re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?',path)
    i=0;current=(0.,0.);points=[]
    while i<len(tokens):
        cmd=tokens[i];i+=1
        if cmd=='M':
            current=(float(tokens[i]),float(tokens[i+1]));i+=2;points.append(current)
        elif cmd=='C':
            p=[current]+[(float(tokens[i+j]),float(tokens[i+j+1])) for j in (0,2,4)]
            i+=6
            for k in range(129):
                t=k/128.;v=1.-t
                points.append(tuple(v**3*p[0][d]+3*v*v*t*p[1][d]+3*v*t*t*p[2][d]+t**3*p[3][d] for d in (0,1)))
            current=p[3]
        elif cmd!='Z':raise ValueError('Unexpected body command '+cmd)
    return np.array(points)


def svg_geometry(root):
    indexed={node.get('id'):node for node in root.iter() if node.get('id')}
    group=indexed['mou-body'];outline=indexed['mou-body-outline']
    matrix=[float(v) for v in re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)',group.get('transform'))]
    a,b,c,d,tx,ty=matrix
    local=path_samples(outline.get('d'))
    world=local@np.array([[a,b],[c,d]])+np.array([tx,ty])
    radius=float(outline.get('stroke-width'))/2.
    margins=(radius*math.hypot(a,c),radius*math.hypot(b,d))
    return indexed,world,margins


def check_all(video=None):
    checks=[]
    def add(name,passed,evidence):checks.append({'check':name,'passed':bool(passed),'evidence':evidence})
    baseline=json.loads((EP/'controle/baseline.json').read_text())
    mismatches=[p for p,digest in baseline.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=digest]
    add('previous_rigs_and_films_preserved',not mismatches,{'files':len(baseline),'mismatches':mismatches})
    states=[];bad_svg=[];feet_errors=[];before_gaps=[];contact_gaps=[];clipped=[]
    for frame in range(1,241):
        t=(frame-1)/24.;state=scene.state_at(t);states.append(state)
        root=ET.fromstring(scene.svg_at(t));ids=[n.get('id') for n in root.iter() if n.get('id')]
        indexed,body,(margin_x,margin_y)=svg_geometry(root)
        references=re.findall(r'url\(#([^)]*)\)',ET.tostring(root,encoding='unicode'))
        eye_ids=[name for name in ids if re.fullmatch(r'mou-eye-white-[lr]',name)]
        pupil_ids=[name for name in ids if re.fullmatch(r'mou-pupil-[lr]',name)]
        foot_ids=[name for name in ids if re.fullmatch(r'mou-foot-[lr]',name)]
        if (len(ids)!=len(set(ids)) or any(ref not in indexed for ref in references)
            or len(eye_ids)!=2 or len(pupil_ids)!=2 or len(foot_ids)!=2
            or any(re.search(r'hand|arm|mitten|moufle|bras',name) for name in ids)):
            bad_svg.append(frame)
        for name in foot_ids:
            foot=indexed[name]
            angle=float(re.findall(r'[-+]?(?:\d*\.\d+|\d+\.?\d*)',foot.get('transform'))[0])*math.pi/180.
            ellipse=next(iter(foot));cy=float(ellipse.get('cy'));rx=float(ellipse.get('rx'));ry=float(ellipse.get('ry'))
            bottom=cy+math.hypot(rx*math.sin(angle),ry*math.cos(angle))
            feet_errors.append(abs(bottom-(1500.-state['actor']['hop'])))
        # The fixed wide shot must contain the entire body before the deliberate reaction insert.
        if t<7.75:
            x,y,w,h=state['camera']
            if not (body[:,0].min()-margin_x>x and body[:,0].max()+margin_x<x+w
                    and body[:,1].min()-margin_y>y and 1500.<=y+h):clipped.append(frame)
        feather=state['feather']
        if t<5.55:
            # Find the top outline where the feather's actual shaft tip is, not the rig's head helper.
            closest=np.abs(body[:,0]-feather['x'])
            upper=body[closest<max(3.,closest.min()+.1),1].min()-margin_y
            gap=upper-feather['y']-1.8*.78
            if t<3.5:before_gaps.append((frame,float(gap)))
            else:contact_gaps.append((frame,float(gap)))
    add('all_svg_states_are_finite',all(finite(s) for s in states),{'frames':240})
    add('two_eyes_two_feet_no_arms_and_valid_unique_clips',not bad_svg,{'frames':240,'failed_frames':bad_svg})
    add('feet_rest_on_ground_and_follow_only_the_intended_hop',max(feet_errors)<1.e-3,
        {'max_error_world_pixels':max(feet_errors),'hop_window_seconds':[1.96,2.38]})
    add('whole_body_visible_in_wide_shot',not clipped,{'failed_frames':clipped,'reaction_insert_seconds':7.75})
    add('feather_does_not_touch_before_impact',all(gap>0 for _,gap in before_gaps),
        {'minimum_gap_pixels':min(gap for _,gap in before_gaps),'last_preimpact_frame':before_gaps[-1]})
    add('feather_stays_on_the_actual_drawn_head_during_load',all(abs(gap)<3.5 for _,gap in contact_gaps),
        {'contact_frame_range':[contact_gaps[0][0],contact_gaps[-1][0]],'gap_range_pixels':[min(g for _,g in contact_gaps),max(g for _,g in contact_gaps)],
         'measurement':'Native SVG outline sampled, transformed and expanded by stroke; feather shaft cap included.'})
    before=[s['actor']['sy'] for s in states if s['t']<3.5]
    impact=[s['actor']['sy'] for s in states if 3.5<=s['t']<=3.625]
    add('large_squash_starts_at_contact_not_during_approach',min(before)>.9 and min(impact)<.5,
        {'minimum_sy_before_contact':min(before),'minimum_sy_first_three_impact_frames':min(impact)})
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((EP/'sources').glob('*')) if p.suffix in ('.py','.json')}
    result={'observed_at_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'checks':checks,'video':None,
            'limits':['Contrôle technique distinct de la lecture du gag par la critique et du jugement du public.',
                      'Film muet ; aucun son ni confort d’écoute certifié.','Le dernier plan est un recadrage volontaire ; la vérification de silhouette entière porte sur le plan large.']}
    if video is not None:
        video=Path(video).resolve()
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(video)],text=True))
        videos=[s for s in probe['streams'] if s['codec_type']=='video'];audio=[s for s in probe['streams'] if s['codec_type']=='audio']
        v=videos[0] if len(videos)==1 else {}
        add('final_mp4_is_hd_ten_seconds_and_silent',len(videos)==1 and not audio and
            (v.get('width'),v.get('height'),v.get('avg_frame_rate'),int(v.get('nb_read_frames',0)))==(1080,1920,'24/1',240)
            and abs(float(v.get('duration',0))-10.)<.0001,
            {'width':v.get('width'),'height':v.get('height'),'fps':v.get('avg_frame_rate'),'frames':v.get('nb_read_frames'),'duration':v.get('duration'),'audio_streams':len(audio)})
        sample_frames=[71,85,88,108,135,167,216,240]
        decoded=PRIVATE/'decoded';decoded.mkdir(parents=True,exist_ok=True)
        select='+'.join('eq(n\\,%d)'%(f-1) for f in sample_frames)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video),'-vf','select='+select,
                        '-fps_mode','vfr','-threads','2',str(decoded/'%02d.png')],check=True)
        errors=[]
        for ordinal,frame in enumerate(sample_frames,1):
            fresh=cairosvg.svg2png(bytestring=scene.svg_at((frame-1)/24.).encode(),output_width=1080,output_height=1920)
            reference=np.asarray(Image.open(io.BytesIO(fresh)).convert('RGB')).astype(np.int16)
            actual=np.asarray(Image.open(decoded/f'{ordinal:02d}.png').convert('RGB')).astype(np.int16)
            error=np.abs(reference-actual)
            errors.append({'frame':frame,'mean_abs_rgb_8bit':float(error.mean()),'p99_abs_rgb_8bit':float(np.percentile(error,99))})
        add('decoded_export_matches_fresh_renders_not_cache',all(e['mean_abs_rgb_8bit']<3. and e['p99_abs_rgb_8bit']<15 for e in errors),errors)
        result['video']={'path':str(video.relative_to(ROOT)),'sha256':sha(video)}
    result['status']='passed' if all(c['passed'] for c in checks) else 'failed'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--video',type=Path)
    args=parser.parse_args()
    if not args.preflight and args.video is None:parser.error('Use --preflight or --video FINAL.mp4')
    PRIVATE.mkdir(parents=True,exist_ok=True)
    result=check_all(None if args.preflight else args.video)
    output=PRIVATE/'preflight.json' if args.preflight else EP/'controle/QA.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    if not args.preflight:
        rows=['# Contrôle indépendant — Poids plume','',
              '**'+result['status']+'** : '+str(len(result['checks']))+' contrôles ciblés.','',
              'Les 240 états SVG ont été vérifiés : deux yeux, deux pupilles clippées, deux pieds et aucun bras ; identifiants et références de clips valides. Les pieds restent au sol et suivent le petit saut prévu.',
              '',
              'Le contact est mesuré sur le contour réellement dessiné, indépendamment du repère de tête du producteur. La plume reste séparée avant l’impact, puis suit le sommet pendant l’écrasement. Le plan large conserve le corps entier.',
              '',
              'L’export final contient 240 images à 24 images/s, 1080 × 1920, durée 10 s, sans piste audio. Huit images décodées ont été comparées à de nouveaux rendus Cairo, sans utiliser les PNG du cache.',
              '',
              'Les six fichiers de référence conservent leur empreinte. Les détails et erreurs mesurées sont dans QA.json.',
              '',
              'MP4 SHA-256 : `'+result['video']['sha256']+'`.','',
              'Ce contrôle technique ne certifie ni le jeu comique ni une approbation du public. Voir la critique du vrai montage. Aucun son n’a été ajouté ou écouté.','']
        if result['status']!='passed':
            rows=['# Contrôle indépendant — Poids plume','',
                  '**Échec : cet export demande une correction.**','',
                  'Contrôles en échec : '+', '.join(c['check'] for c in result['checks'] if not c['passed'])+'.','',
                  'Les preuves et mesures sont dans QA.json. Aucune validation de livraison ni artistique n’est donnée.','']
        (EP/'controle/QA.md').write_text('\n'.join(rows))
    print(json.dumps({'status':result['status'],'scope':'preflight' if args.preflight else 'final',
                      'checks':len(result['checks']),'failed':[c['check'] for c in result['checks'] if not c['passed']]}),flush=True)
    if result['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
