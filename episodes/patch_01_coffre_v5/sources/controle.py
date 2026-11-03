"""Independent V5 checks of session time, held acting and rendered prop depth.

Run --preflight before the HD render, then --final after encoding. Pixel
comparisons test the solid box and actual visible palms, not just anchors.
They complement the independent artistic review; no audio audition is made.
"""
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
from PIL import Image, ImageDraw, ImageFilter
from scene import state_at, svg_at, FPS, DURATION

EP = Path(__file__).resolve().parents[1]
ROOT = EP.parents[1]
OLD = ROOT / 'episodes/patch_01_coffre_v4_telephone'
WORK = EP / 'work/qa'
WINDOWS = [(1.4, 3.55), (23.2, 24.7)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hash():
    h = hashlib.sha256()
    for p in sorted((EP / 'sources').glob('*')):
        if p.suffix in ('.py', '.json') and p.name != 'controle.py':
            h.update(p.name.encode())
            h.update(p.read_bytes())
    h.update((EP / 'chronologie.json').read_bytes())
    return h.hexdigest()


def rgb(svg, width=1080):
    raw = cairosvg.svg2png(bytestring=svg.encode(), output_width=width,
                          output_height=width * 16 // 9)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))


def without(svg, ids):
    root = ET.fromstring(svg)
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get('id') in ids:
                parent.remove(child)
    return ET.tostring(root, encoding='unicode')


def finite(value):
    if isinstance(value, dict):
        return all(finite(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite(v) for v in value)
    return not isinstance(value, float) or math.isfinite(value)


def previous_states():
    code = """import json,sys
sys.path.insert(0,sys.argv[1])
from scene import state_at
print(json.dumps([state_at(i/24) for i in range(720)]))
"""
    return json.loads(subprocess.check_output(
        [sys.executable, '-c', code, str(OLD / 'sources')], cwd=OLD))


def reversals(values):
    signs = [int(np.sign(b-a)) for a, b in zip(values, values[1:]) if abs(b-a) > 1e-6]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))


def stream_hash(path, kind, fmt):
    return hashlib.sha256(subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', kind,
        '-c', 'copy', '-f', fmt, '-'])).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preflight', action='store_true')
    p.add_argument('--final', action='store_true')
    args = p.parse_args()
    if not (args.preflight or args.final):
        p.error('Choose --preflight or --final')
    WORK.mkdir(parents=True, exist_ok=True)
    checks = []

    def check(name, ok, detail):
        checks.append({'name': name, 'passed': bool(ok), 'detail': detail})

    states = [state_at(i/FPS) for i in range(720)]
    old = previous_states()
    xmls = [svg_at(i/FPS) for i in range(720)]
    roots = [ET.fromstring(x) for x in xmls]
    unique = all(len([e.attrib['id'] for e in r.iter() if 'id' in e.attrib]) ==
                 len({e.attrib['id'] for e in r.iter() if 'id' in e.attrib}) for r in roots)
    check('720_finite_states_and_unique_svg_ids', all(finite(s) for s in states) and unique,
          {'frames': len(states), 'fps': FPS, 'duration': DURATION})

    bad = []
    for i, s in enumerate(states):
        elapsed, remaining, clock = s['story_elapsed_seconds'], s['remaining'], s['clock_seconds']
        valid = (isinstance(elapsed, int) and isinstance(remaining, int) and
                 0 <= elapsed <= 1800 and elapsed + remaining == 1800 and
                 clock == 32400 + elapsed and s['display'] == f'{remaining//60:02d}:{remaining%60:02d}' and
                 s['clock_display'] == f'{clock//3600:02d}:{clock%3600//60:02d}' and
                 s['time_state']['session_elapsed'] == elapsed)
        if not valid:
            bad.append(i)
    seq = [s['story_elapsed_seconds'] for s in states]
    check('one_integer_session_clock_timer_and_labels', not bad and all(a <= b for a,b in zip(seq,seq[1:])),
          {'bad_frames_zero': bad, 'clock_start': 32400, 'session_seconds': 1800})
    endpoints = {str(t): state_at(t)['time_state'] for t in (0., 4., 16.25, 22., 23., 29.958333333)}
    check('time_montage_endpoints_and_clock_freeze',
          [state_at(t)['story_elapsed_seconds'] for t in (16.25,22.,23.)] == [960,1799,1800] and
          all(s['clock_display']=='09:30' and s['remaining']==0 for s in states if s['t']>=23.), endpoints)

    metadata_bad = []
    numeric_clock_frames = 0
    for i, (s, root) in enumerate(zip(states, roots)):
        byid = {e.attrib['id']: e for e in root.iter() if 'id' in e.attrib}
        if 'timer' in byid and (byid['timer'].get('data-display') != s['display'] or
                               int(byid['timer'].get('data-remaining')) != s['remaining']):
            metadata_bad.append(i)
        if 'wall-clock' in byid and float(byid['wall-clock'].get('data-elapsed-seconds')) != s['story_elapsed_seconds']:
            metadata_bad.append(i)
        numeric_clock_frames += int('wall-clock-time' in byid or 'clock-readable-time' in byid)
    check('rendered_timer_and_wall_clock_use_session_time', not metadata_bad and numeric_clock_frames>300,
          {'bad_frames_zero': metadata_bad, 'frames_with_numeric_clock':numeric_clock_frames,
           'method':'Inspect actual full-frame SVG element data and presence of rasterized clock labels.'})

    late = [s['actor'] for s in states if 16.25 <= s['t'] < 21.7]
    motion = {'gaze_x': reversals([a['gaze'][0] for a in late]),
              'gaze_y': reversals([a['gaze'][1] for a in late]),
              'head_tilt': reversals([a['head_tilt'] for a in late])}
    held = [s['actor'] for s in states if 19.125<=s['t']<21.7]
    spans = {key: max(a[key] for a in held)-min(a[key] for a in held) for key in ('head_tilt','blink')}
    gaze_span = [max(a['gaze'][k] for a in held)-min(a['gaze'][k] for a in held) for k in (0,1)]
    late_caption = [s['caption'] for s in states if 17.15<=s['t']<22.]
    check('late_wait_has_one_approach_and_no_minute_gaze_loops',
          motion['gaze_x']<=1 and motion['gaze_y']==0 and motion['head_tilt']<=1 and
          all(abs(x)<1e-9 for x in [*spans.values(),*gaze_span]) and not any(late_caption),
          {'direction_reversals': motion, 'held_head_and_blink_span':spans,
           'held_gaze_xy_span':gaze_span,'held_window':[19.125,21.7],
           'late_numeric_minute_captions':sum(bool(x) for x in late_caption)})

    protected = [i for i in range(720) if any(lo<=i/FPS<hi for lo,hi in WINDOWS)]
    changed = []
    for i in protected:
        for key in ('actor','actor_screen','phone','phone_deep','lid','layout','view'):
            # JSON normalizes tuples from the live source exactly as in baseline subprocess.
            if json.loads(json.dumps(states[i][key])) != old[i][key]:
                changed.append({'frame_zero':i,'key':key})
    check('validated_phone_contact_states_preserved',not changed,
          {'windows':WINDOWS,'protected_frames':len(protected),'differences':changed})
    paths=['sources/personnage.py','sources/jeu.py','sources/vues.py','sources/telephone.py',
           'sources/cadres.json','sources/palette.json','sources/reference_scene.py','audio/mix.wav']
    unchanged={x:sha(EP/x)==sha(OLD/x) for x in paths}
    baseline=json.loads((EP/'controle/baseline.json').read_text())
    refs={x:sha(ROOT/x)==h for x,h in baseline.items()}
    check('rig_phone_cameras_audio_and_8_old_references_preserved', all(unchanged.values()) and len(refs)==8 and all(refs.values()),
          {'inputs':unchanged,'protected_refs':refs})

    pixel_rows=[]
    for t in (13.5,19.3,20.,21.):
        s=state_at(t); svg=svg_at(t);full=rgb(svg)
        no_limbs=rgb(without(svg,{'patch-character-arms','patch-character-hands'}))
        no_right=rgb(without(svg,{'patch-hand-right'}))
        # Difference of real composed pixels measures the visible paw footprint.
        visible=np.any(full!=no_right,axis=2)
        ys,xs=np.where(visible)
        layout=s['layout'];scale=layout['scale'];tx=layout['tx']+layout.get('box_shift_x',0);ty=layout['ty']+layout.get('box_shift_y',0)
        polygon=[(x*scale+tx,y*scale+ty) for x,y in ((662,1205),(952,1205),(990,1295),(990,1465),(700,1465),(662,1375))]
        mask=Image.new('L',(1080,1920));ImageDraw.Draw(mask).polygon(polygon,fill=255)
        inner=np.asarray(mask.filter(ImageFilter.MinFilter(5)))>0
        bleed=int((np.any(full!=no_limbs,axis=2)&inner).sum())
        # At the resting-paw height its rightmost visible pixel must precede the nearest side.
        min_side_x=min(x for x,y in polygon)
        right_edge=int(xs.max()) if len(xs) else -1
        pixel_rows.append({'t':t,'solid_box_limb_pixels':bleed,'visible_right_paw_pixels':int(visible.sum()),
                           'visible_right_paw_right_edge':right_edge,'nearest_box_x':min_side_x,
                           'right_paw_fully_left_of_side':right_edge<min_side_x})
        Image.fromarray(full).save(WORK/f'pixel_proof_{t:.2f}.png')
    check('real_composed_paw_clearance_and_solid_box_occlusion',
          all(r['solid_box_limb_pixels']==0 and r['visible_right_paw_pixels']>700 and r['right_paw_fully_left_of_side'] for r in pixel_rows),pixel_rows)

    # Full-body joy and bilateral phone are retained rather than redesigned.
    joy=[state_at(t) for t in (25.2,25.7,26.5)]
    joy_ids=[{e.get('id') for e in ET.fromstring(svg_at(s['t'])).iter()} for s in joy]
    check('joy_two_feet_bilateral_phone_and_blank_work',
          all(s['actor'].get('airborne') and s['phone']['bilateral'] and s['phone']['face']=='back' for s in joy) and
          all({'patch-foot-left','patch-foot-right'}<=ids for ids in joy_ids) and
          all(s['completed_tasks']==0 for s in states),
          {'joy_samples':[s['t'] for s in joy],'completed_tasks_max':max(s['completed_tasks'] for s in states)})

    timeline=json.loads((EP/'chronologie.json').read_text())
    with wave.open(str(EP/'audio/mix.wav')) as w:
        params=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
    stems=[]
    for f in sorted((EP/'audio/stems').glob('*.wav')):
        with wave.open(str(f)) as w:stems.append(np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.int32))
    reconstructed=np.clip(sum(stems),-32768,32767).astype(np.int16)
    ar=json.loads((EP/'audio/mix_report.json').read_text())
    controls=json.loads((EP/'audio/controls.json').read_text())
    timeline_ok=all(report.get('timeline_sha256')==sha(EP/'chronologie.json') for report in (ar,controls))
    check('audio_18_cues_no_clip_reconstructed_and_current_timeline',
          params==(48000,2,2,1440000) and len(timeline['audio_cues'])==18 and
          np.array_equal(reconstructed,pcm) and int(np.abs(pcm.astype(np.int32)).max())<32767 and timeline_ok,
          {'wav_sha256':sha(EP/'audio/mix.wav'),'parameters':params,'cues':len(timeline['audio_cues']),
           'peak_pcm':int(np.abs(pcm.astype(np.int32)).max()),'timeline_reports_current':timeline_ok,
           'listening_performed':False})

    mode='hd' if args.final else 'preview'
    rp=EP/f'controle/rendu_{mode}.json'
    if rp.exists():
        report=json.loads(rp.read_text())
        check('render_cache_has_current_source_hash',report['source_sha256']==source_hash(),
              {'mode':mode,'report':report['source_sha256'],'current':source_hash()})

    if args.final:
        video=EP/'PATCH_Le_coffre_V5.mp4';mute=EP/'PATCH_Le_coffre_V5_muet.mp4'
        pv,pm=probe(video),probe(mute)
        v=[s for s in pv['streams'] if s['codec_type']=='video'][0]
        m=[s for s in pm['streams'] if s['codec_type']=='video'][0]
        a=[s for s in pv['streams'] if s['codec_type']=='audio']
        fmt=all(s['width']==1080 and s['height']==1920 and s['r_frame_rate']=='24/1' and
                int(s['nb_frames'])==720 and abs(float(s['duration'])-30)<.001 for s in (v,m))
        check('final_1080x1920_24fps_30s_sound_and_mute',fmt and len(a)==1 and abs(float(a[0]['duration'])-30)<.001 and
              not any(s['codec_type']=='audio' for s in pm['streams']),
              {'video_sha256':sha(video),'mute_sha256':sha(mute),'video_frames':v['nb_frames'],'audio_duration':a[0]['duration']})
        hv,hm=stream_hash(video,'0:v:0','h264'),stream_hash(mute,'0:v:0','h264')
        check('same_h264_in_sound_and_mute',hv==hm,{'sound_h264_sha256':hv,'mute_h264_sha256':hm})
        av,ab=stream_hash(video,'0:a:0','adts'),stream_hash(OLD/'PATCH_Le_coffre_V4_telephone.mp4','0:a:0','adts')
        check('aac_unchanged_from_validated_phone_film',av==ab,{'new_aac_sha256':av,'baseline_aac_sha256':ab})
        ids=[40,68,156,324,390,411,438,455,463,504,540,617]
        folder=WORK/'decoded';folder.mkdir(exist_ok=True)
        expr='+'.join(f'eq(n,{i})' for i in ids)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{expr}'",'-fps_mode','vfr',str(folder/'%02d.png')],check=True)
        rows=[]
        for j,i in enumerate(ids):
            fresh=rgb(svg_at(i/FPS)).astype(np.int16)
            decoded=np.asarray(Image.open(folder/f'{j+1:02d}.png').convert('RGB'),dtype=np.int16)
            error=np.abs(fresh-decoded)
            rows.append({'frame_zero':i,'mean_rgb_error':round(float(error.mean()),4),'p99':float(np.percentile(error,99))})
            Image.fromarray(fresh.astype(np.uint8)).save(WORK/f'fresh_{i:04d}.png')
        check('12_actual_hd_decodes_match_current_fresh_renders',all(r['mean_rgb_error']<3 and r['p99']<=12 for r in rows),rows)
        gp=EP/'controle/gel_sources.json'
        gel=json.loads(gp.read_text()) if gp.exists() else {}
        manifest=gel.get('files',gel)
        frozen={k:sha(ROOT/k)==h for k,h in manifest.items()}
        check('frozen_producers_unchanged',bool(frozen) and all(frozen.values()),frozen)

    result={'status':'passed' if all(c['passed'] for c in checks) else 'failed',
            'scope':'final_hd' if args.final else 'preflight_preview','checks':checks,
            'limits':['Mesures ciblées complétées par critique visuelle du vrai montage ; aucun succès public certifié.',
                      'Aucune audition, génération vocale ni confort d’écoute revendiqué.',
                      'Contrôle du temps par données et rendu SVG ; la lisibilité sur téléphone doit rester soumise à la revue artistique.']}
    target=EP/'controle/qa.json' if args.final else WORK/'preflight.json'
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(c['passed'] for c in checks),'total':len(checks),
                      'failed':[c['name'] for c in checks if not c['passed']]}))
    return 0 if result['status']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
