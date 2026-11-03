"""Independent integration checks for PATCH V6 vocalisations.

Use --final after producer freeze and HD encoding. Numeric audio measurements
and decoded images are evidence of integration, not an audition of the voice.
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
from PIL import Image, ImageDraw, ImageFont
from scene import state_at, svg_at, FPS, DURATION

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]
OLD=ROOT/'episodes/patch_01_coffre_v5'
WORK=EP/'work/qa'
FACE_KEYS={'face','pose_weights','mouth_shape','mouth_o_scale','blink','voice_event','voice_envelope'}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(v):return json.loads(json.dumps(v))


def body_only(actor):return {k:norm(v) for k,v in actor.items() if k not in FACE_KEYS}


def previous_states():
    code="import json,sys;sys.path.insert(0,sys.argv[1]);from scene import state_at;print(json.dumps([state_at(i/24) for i in range(720)]))"
    return json.loads(subprocess.check_output([sys.executable,'-c',code,str(OLD/'sources')],cwd=OLD))


def finite(v):
    if isinstance(v,dict):return all(finite(x) for x in v.values())
    if isinstance(v,(tuple,list)):return all(finite(x) for x in v)
    return not isinstance(v,float) or math.isfinite(v)


def wav(path):
    with wave.open(str(path)) as w:
        params=(w.getframerate(),w.getnchannels(),w.getsampwidth(),w.getnframes())
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy().reshape(-1,w.getnchannels())
    return params,pcm


def rgb(svg):
    raw=cairosvg.svg2png(bytestring=svg.encode(),output_width=1080,output_height=1920)
    return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))


def stream_hash(path,kind,fmt):
    return hashlib.sha256(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map',kind,'-c','copy','-f',fmt,'-'])).hexdigest()


def source_hash():
    h=hashlib.sha256()
    for p in sorted((EP/'sources').glob('*')):
        if p.suffix in ('.py','.json') and p.name!='controle.py':h.update(p.name.encode());h.update(p.read_bytes())
    h.update((EP/'chronologie.json').read_bytes())
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    if not (args.preflight or args.final):parser.error('Use --preflight or --final')
    WORK.mkdir(parents=True,exist_ok=True)
    checks=[]
    def check(name,ok,detail):checks.append({'name':name,'passed':bool(ok),'detail':detail})

    timeline=json.loads((EP/'chronologie.json').read_text())
    gestures=json.loads((EP/'sources/voix_gestes.json').read_text())
    events=gestures['events'];cues=timeline.get('voice_cues',[])
    if not events or not cues:raise RuntimeError('Vocal producers are not ready; refusing placeholder QA')
    states=[state_at(i/FPS) for i in range(720)]
    old=previous_states()
    check('30_seconds_720_finite_states',FPS==24 and DURATION==30 and len(states)==720 and all(finite(s) for s in states),
          {'frames':len(states),'fps':FPS,'duration':DURATION})
    timing_keys=['story_elapsed_seconds','remaining','display','clock_seconds','clock_display','time_state','view','layout','lid','phone','phone_deep','completed_tasks']
    timing_bad=[];actor_bad=[]
    for i,(s,o) in enumerate(zip(states,old)):
        timing_bad.extend({'frame_zero':i,'key':key} for key in timing_keys if norm(s[key])!=o[key])
        for key in ('actor','actor_screen'):
            if body_only(s[key])!=body_only(o[key]):actor_bad.append({'frame_zero':i,'key':key})
    check('timer_clock_views_phone_lid_and_blank_work_unchanged',not timing_bad,{'differences':timing_bad})
    check('hands_elbows_body_and_prop_contact_unchanged_all_720',not actor_bad,{'differences':actor_bad,'allowed_changes':sorted(FACE_KEYS)})
    old_timeline=json.loads((OLD/'chronologie.json').read_text())
    check('18_foley_ui_cues_retained_and_five_sparse_vocals',timeline['audio_cues']==old_timeline['audio_cues'] and len(cues)==5 and len(events)==5 and
          {c['sound'] for c in cues}=={'resolve_hm','bored_exhale','sleepy_yawn','surprise_inhale','relief_chuckle'} and
          all(b['at']-a['at']>1. for a,b in zip(cues,cues[1:])),
          {'base_cues':len(timeline['audio_cues']),'voice_cues':len(cues),'events':len(events),'starts':[c['at'] for c in cues]})
    # No visual modification is permitted away from the declared voice gestures.
    outside=[i for i in range(720) if not any(e['start']<=i/FPS<=e['end'] for e in events)]
    outside_bad=[]
    for i in outside:
        if norm(states[i]['actor'])!=old[i]['actor'] or norm(states[i]['actor_screen'])!=old[i]['actor_screen']:
            outside_bad.append(i)
    check('facial_state_changes_limited_to_declared_voice_windows',not outside_bad,{'frames_outside':len(outside),'changed_frames':outside_bad})
    prior_paths=['sources/attente.py','sources/telephone.py','sources/jeu.py','sources/vues.py','sources/cadres.json','sources/temps.py','sources/palette.json']
    prior={p:sha(EP/p)==sha(OLD/p) for p in prior_paths}
    baseline=json.loads((EP/'controle/baseline.json').read_text())
    refs={p:sha(ROOT/p)==h for p,h in baseline.items()}
    check('validated_rig_controls_and_seven_old_references_preserved',all(prior.values()) and len(refs)==7 and all(refs.values()),{'controls':prior,'references':refs})

    bank_root=EP/'assets/voix';bank=json.loads((bank_root/'bank.json').read_text())
    voice_rows=json.loads((EP/'audio/voice_cues.json').read_text())
    vr={r['id']:r for r in voice_rows}
    asset_rows=[];alignment=[]
    for cue in cues:
        entry=bank['sounds'][cue['sound']];params,pcm=wav(bank_root/entry['file'])
        mono=pcm.mean(axis=1).astype(float)/32767.
        rate=params[0]
        # A 20-ms RMS envelope locates the actual waveform's energetic accent.
        window=max(1,round(.020*rate));energy=np.convolve(mono*mono,np.ones(window)/window,mode='same')
        declared_points=[float(x) for x in entry.get('accent_points_seconds',[entry['accent_seconds']])]
        edges=[0.]+[(a+b)/2. for a,b in zip(declared_points,declared_points[1:])]+[len(mono)/rate]
        measured_points=[]
        for lo,hi in zip(edges,edges[1:]):
            i0,i1=round(lo*rate),round(hi*rate)
            measured_points.append((i0+int(np.argmax(energy[i0:i1])))/rate)
        peak=measured_points[0]
        declared=float(entry['accent_seconds'])
        visual=float(cue['visual_accent'])
        aligned=float(cue['at'])+declared
        e=next(e for e in events if e['id']==cue['id'])
        curve=np.asarray(e['envelope'],float)
        curve_peaks=[]
        for lo,hi in zip(edges,edges[1:]):
            part=curve[(curve[:,0]>=cue['at']+lo)&(curve[:,0]<=cue['at']+hi)]
            curve_peaks.append(float(part[np.argmax(part[:,1]),0]))
        env_peak=curve_peaks[0]
        vocal_peak_errors=[abs(a-b)*FPS for a,b in zip(measured_points,declared_points)]
        facial_peak_errors=[abs(a-(cue['at']+b))*FPS for a,b in zip(curve_peaks,declared_points)]
        asset_rows.append({'sound':cue['sound'],'file':entry['file'],'sha_ok':sha(bank_root/entry['file'])==entry['sha256'],
                           'parameters':params,'peak_pcm':int(np.abs(pcm.astype(np.int32)).max()),
                           'first_last_pcm':[int(pcm[0,0]),int(pcm[-1,0])],
                           'measured_rms_peak_seconds':round(peak,6),'declared_accent_seconds':declared})
        alignment.append({'id':cue['id'],'sound':cue['sound'],'visual_accent':visual,'file_accent_in_film':aligned,
                          'declared_error_frames':abs(aligned-visual)*FPS,
                          'energetic_peak_error_frames':max(vocal_peak_errors),
                          'gesture_peak_error_frames':max(facial_peak_errors),
                          'declared_points_seconds':declared_points,'measured_points_seconds':measured_points,
                          'facial_points_in_film':curve_peaks,
                          'sample_start_error':abs(vr[cue['id']]['start_sample']-round(cue['at']*rate))})
    check('selected_vocal_assets_valid_pcm_sha_and_silent_boundaries',all(r['sha_ok'] and r['parameters'][:3]==(48000,1,2) and r['peak_pcm']<32767 and r['first_last_pcm']==[0,0] for r in asset_rows),asset_rows)
    check('actual_vocal_accents_and_facial_envelopes_align_within_frame',all(r['declared_error_frames']<=1.001 and r['energetic_peak_error_frames']<=1.001 and r['gesture_peak_error_frames']<=1.001 and r['sample_start_error']==0 for r in alignment),alignment)

    params,mix=wav(EP/'audio/mix.wav');bp,base_mix=wav(EP/'audio/base_mix.wav');vp,voice=wav(EP/'audio/stems/voice.wav')
    _,old_mix=wav(OLD/'audio/mix.wav')
    residual=mix.astype(np.int32)-base_mix.astype(np.int32)-voice.astype(np.int32)
    active=np.zeros(len(mix),dtype=bool)
    for row in voice_rows:active[row['start_sample']:row['start_sample']+round(row['duration']*48000)]=True
    outside_audio_equal=bool(np.array_equal(mix[~active],old_mix[~active]))
    old_stems={f.name:sha(f)==sha(EP/'audio/stems'/f.name) for f in (OLD/'audio/stems').glob('*.wav')}
    report=json.loads((EP/'audio/mix_report.json').read_text())
    check('base_foley_pcm_stems_and_nonvocal_samples_exactly_preserved',np.array_equal(base_mix,old_mix) and outside_audio_equal and all(old_stems.values()),
          {'base_mix_identical':bool(np.array_equal(base_mix,old_mix)),'outside_voice_equal':outside_audio_equal,'base_stems':old_stems})
    check('voice_plus_base_reconstruct_mix_no_clips_and_current_timeline',params==bp==vp==(48000,2,2,1440000) and int(np.max(np.abs(residual)))<=1 and
          int(np.max(np.abs(mix.astype(np.int32))))<32767 and report['timeline_sha256']==sha(EP/'chronologie.json') and report['compressor'] is False and report['music'] is False and report['voice'] is True,
          {'parameters':params,'max_reconstruction_pcm_error':int(np.max(np.abs(residual))),'peak_pcm':int(np.max(np.abs(mix.astype(np.int32)))),
           'voice_active_seconds':float(active.sum()/48000.),'listening_performed':False,'report_current':report['timeline_sha256']==sha(EP/'chronologie.json')})
    # Independent reconstruction of the exact waveform placements and fixed gains.
    expected=np.zeros_like(voice,dtype=float)
    for row in voice_rows:
        entry=bank['sounds'][row['sound']];_,pcm=wav(bank_root/entry['file']);mono=pcm[:,0].astype(float)/32767.
        gain=10.**(row['gain_db']/20.);angle=(row['pan']+1.)*np.pi/4.
        stereo=mono[:,None]*gain*np.array([np.cos(angle),np.sin(angle)])[None,:]
        start=row['start_sample'];expected[start:start+len(stereo)]+=stereo
    expected_pcm=np.rint(expected*32767.).astype(np.int32)
    placement_error=int(np.max(np.abs(expected_pcm-voice.astype(np.int32))))
    check('fixed_gain_voice_placements_reconstruct_exact_stem',placement_error<=1,{'max_pcm_error':placement_error,'voice_cues':len(voice_rows),'no_scene_ducking':True})

    if args.final:
        engine=bank['engine']
        receipt=(bank_root/'controle/engine.txt').read_text()
        recipe=(bank_root/'sources/generate.R').read_text()
        desc=(bank_root/'licences/soundgen-DESCRIPTION.txt').read_text()
        gpl=(bank_root/'licences/GPL-2.txt').read_text()
        variants=[]
        for name,entry in bank['variants'].items():
            path=bank_root/entry['file'];params,pcm=wav(path)
            variants.append({'name':name,'sha_ok':sha(path)==entry['sha256'],
                             'parameters_ok':params[:3]==(48000,1,2),
                             'duration_error_samples':abs(params[3]-round(entry['duration']*48000)),
                             'recipe_exists':(bank_root/entry['parameter_file']).exists(),
                             'peak_pcm':int(np.max(np.abs(pcm.astype(np.int32))))})
        source_ok=(engine['name']=='Soundgen' and engine['version']=='3.0.0' and engine['executed'] is True and
                   engine['models_or_voice_recordings_used'] is False and 'soundgen=3.0.0' in receipt and
                   'do.call(soundgen,pars)' in recipe and 'License: GPL' in desc and 'GNU GENERAL PUBLIC LICENSE' in gpl)
        check('real_soundgen_six_intents_twelve_seeded_takes_and_licenses',source_ok and len(bank['sounds'])==6 and len(variants)==12 and
              all(v['sha_ok'] and v['parameters_ok'] and v['duration_error_samples']==0 and v['recipe_exists'] and v['peak_pcm']<32767 for v in variants),
              {'engine':engine,'engine_receipt_sha256':sha(bank_root/'controle/engine.txt'),'script_sha256':sha(bank_root/'sources/generate.R'),
               'license_description_sha256':sha(bank_root/'licences/soundgen-DESCRIPTION.txt'),'variants':variants,'listening_performed':False})
        video=EP/'PATCH_Le_coffre_V6_voix.mp4';mute=EP/'PATCH_Le_coffre_V6_voix_muet.mp4'
        pv,pm=probe(video),probe(mute);v=next(s for s in pv['streams'] if s['codec_type']=='video');m=next(s for s in pm['streams'] if s['codec_type']=='video');aud=[s for s in pv['streams'] if s['codec_type']=='audio']
        fmt=all(s['width']==1080 and s['height']==1920 and s['r_frame_rate']=='24/1' and int(s['nb_frames'])==720 and abs(float(s['duration'])-30)<.001 for s in (v,m))
        check('final_hd_vertical_24fps_30s_sound_and_mute',fmt and len(aud)==1 and abs(float(aud[0]['duration'])-30)<.001 and not any(s['codec_type']=='audio' for s in pm['streams']),
              {'video_sha256':sha(video),'mute_sha256':sha(mute),'audio_duration':aud[0]['duration']})
        hv,hm=stream_hash(video,'0:v:0','h264'),stream_hash(mute,'0:v:0','h264')
        check('identical_h264_in_sound_and_mute',hv==hm,{'sound_h264_sha256':hv,'mute_h264_sha256':hm})
        # Decode the whole final film; a valid header alone does not prove playback.
        subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
        subprocess.run(['ffmpeg','-v','error','-i',str(mute),'-f','null','-'],check=True)
        ids=[68,114,156,318,420,432,439,463,555,603,608,684]
        folder=WORK/'decoded';folder.mkdir(exist_ok=True)
        expr='+'.join(f'eq(n,{i})' for i in ids)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf',f"select='{expr}'",'-fps_mode','vfr',str(folder/'%02d.png')],check=True)
        rows=[];board=Image.new('RGB',(1440,2120),'#FAF5EC');draw=ImageDraw.Draw(board);font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),15)
        for j,i in enumerate(ids):
            fresh=rgb(svg_at(i/FPS)).astype(np.int16);decoded=np.asarray(Image.open(folder/f'{j+1:02d}.png').convert('RGB'),dtype=np.int16);error=np.abs(fresh-decoded)
            rows.append({'frame_zero':i,'mean_rgb_error':round(float(error.mean()),4),'p99':float(np.percentile(error,99))})
            im=Image.fromarray(decoded.astype(np.uint8));board.paste(im.resize((360,640)),((j%4)*360,(j//4)*700));draw.text(((j%4)*360+8,(j//4)*700+651),f'f{i} / {i/FPS:.3f} s',font=font,fill='#302D35')
        board.save(WORK/'actual_hd_review.png')
        check('12_real_hd_frames_match_fresh_source_renders',all(r['mean_rgb_error']<3 and r['p99']<=12 for r in rows),rows)
        missing=[];png_bad=[]
        for i in outside:
            name=f'{i+1:04d}.png';a=EP/'work/hd'/name;b=OLD/'work/hd'/name
            if not(a.exists() and b.exists()):missing.append(i)
            elif sha(a)!=sha(b):png_bad.append(i)
        check('all_cached_hd_png_outside_voice_windows_identical_v5',not missing and not png_bad,{'frames_checked':len(outside),'missing':missing,'changed':png_bad})
        render=json.loads((EP/'controle/rendu_hd.json').read_text())
        check('final_render_source_hash_current',render['source_sha256']==source_hash(),{'render':render['source_sha256'],'current':source_hash()})
        gel=json.loads((EP/'controle/gel_sources.json').read_text());gel=gel.get('files',gel)
        frozen={p:sha(ROOT/p)==h for p,h in gel.items()}
        check('frozen_productive_inputs_intact',bool(frozen) and all(frozen.values()),frozen)

    result={'status':'passed' if all(x['passed'] for x in checks) else 'failed','scope':'final_hd' if args.final else 'preflight','checks':checks,
            'limits':['No audio audition or perceived naturalness/comfort validated.','Waveforms, sample placements and decoded visuals were checked; public comic response is not measured.','Soundgen generation provenance is checked separately from artistic listening.']}
    target=EP/'controle/qa.json' if args.final else WORK/'preflight.json';target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':sum(x['passed'] for x in checks),'total':len(checks),'failed':[x['name'] for x in checks if not x['passed']]}))
    return 0 if result['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
