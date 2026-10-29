"""Independent V17 checks for the real stop/start regressions found in V16.

No synthesizer is run here: exports, written notes and the scalar envelope
are inspected. Numeric continuity is a safeguard, not perceptual approval.
Run after the production sources/WAVs are frozen; --final also checks MP4.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
BASE=EP.parent/'cuisine_v16'
REPORT=EP/'controle/audit_audio_v17.json'
SR=48000
MASTER=2.124210976406158
KNOWN_GAPS=(14.65,15.85,16.45,29.0)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db(x):
    return None if x<=0. else float(20.*math.log10(x))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if x.size else 0.


def pcm(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2),path
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).copy()


def command(args):
    return subprocess.check_output(args,stderr=subprocess.PIPE)


def bitstream(path):
    raw=command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy',
                 '-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def rolling_levels(data,seconds,hop=.02,start=.15,end=40.8):
    """RMS windows identified by START, with cumulative sums, no resynthesis."""
    power=np.square(data).mean(axis=1) if data.ndim==2 else np.square(data)
    integral=np.concatenate(([0.],np.cumsum(power,dtype=np.float64)))
    size=round(seconds*SR)
    starts=np.arange(round(start*SR),min(round(end*SR),len(power))-size+1,round(hop*SR))
    values=np.sqrt(np.maximum(0.,(integral[starts+size]-integral[starts])/size))
    levels=20.*np.log10(np.maximum(values,1.e-15))
    return [{'start':float(a/SR),'end':float((a+size)/SR),'dbfs':float(b)}
            for a,b in zip(starts,levels)]


def summary(rows):
    values=np.array([v['dbfs'] for v in rows])
    return {'windows':len(rows),'minimum':min(rows,key=lambda r:r['dbfs']),
            'percentiles_dbfs':{str(p):float(np.percentile(values,p)) for p in (5,10,50,90,95)},
            'p95_minus_p5_db':float(np.percentile(values,95)-np.percentile(values,5))}


def phoneband(path):
    raw=command(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
        '-af','pan=mono|c0=0.5*c0+0.5*c1,highpass=f=180,lowpass=f=6000','-ac','1','-ar',str(SR),
        '-c:a','pcm_f32le','-f','f32le','-'])
    return np.frombuffer(raw,'<f4').astype(np.float64)*MASTER


def score_checks(module,specification,parameters,duration):
    minimal={'bpm':float(specification['bpm']),'duration':duration}
    original=module.compose(copy.deepcopy(specification))
    bare=module.compose(copy.deepcopy(minimal))
    changed={**copy.deepcopy(specification),'original_cooking_windows':[[2.13,3.27],[9.19,12.44]],
             'old_windows':[[4.77,6.22]],'windows':[[5.,6.]],
             'duck_intervals':[[1.34,2.43],[17.28,19.66]],'duck_db':-13.}
    alternate=module.compose(changed)
    canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
    assert canonical(original)==canonical(bare)==canonical(alternate), 'composition still depends on visual windows or ducking'
    assert canonical(original)==canonical(parameters['notes']), 'written score differs from generated/exported score'
    assert original and all(0.<=float(e['start'])<duration and float(e['duration'])>0.
        and float(e['start'])+float(e['duration'])<=duration+1.e-7 for e in original)
    bass=[e for e in original if e['track']=='basse']
    assert bass,'no bass pulse'
    beat=60./minimal['bpm']
    errors=[abs(e['start']/beat-round(e['start']/beat))*beat for e in bass]
    assert max(errors)<1.e-6,('bass phase is not a single global grid',max(errors))
    bass_beats={round(e['start']/beat) for e in bass}
    required=set(range(1,math.floor((duration-1.)/beat)))
    assert required.issubset(bass_beats),('missing interior bass pulses',sorted(required-bass_beats))
    return {'notes':len(original),'composition_invariant_to_visual_windows_and_ducking':True,
        'composition_requires_only_bpm_and_duration':True,'bass_notes':len(bass),
        'maximum_bass_grid_error_seconds':max(errors),'interior_pulse_beats_checked':len(required),
        'beat_seconds':beat,'score_sha256':hashlib.sha256(canonical(original).encode()).hexdigest()}


def preservation():
    files=('chronologie.json','sources/animation.py','sources/art.py','sources/render.py','sources/sink.py','sources/mitten.py')
    result={}
    for name in files:
        assert sha(EP/name)==sha(BASE/name),name
        result[name]=sha(EP/name)
    assert sha(ROOT/'mou_rig.py')=='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    return result


def audio_checks():
    timeline=json.loads((EP/'chronologie.json').read_text());duration=float(timeline['duration']);n=round(duration*SR)
    previous=json.loads((BASE/'audio/provenance.json').read_text())
    current=json.loads((EP/'audio/provenance.json').read_text())
    audit=json.loads((EP/'controle/audit_son.json').read_text())
    old={e['name']:e for e in previous['events']};new={e['name']:e for e in current['events']}
    assert len(old)==len(new)==64 and old.keys()==new.keys()
    assert abs(audit['master_gain_linear_exact']-MASTER)<1.e-14,'foreground master changed'
    foreground=np.zeros((n,2),dtype=np.float64);preserved=[]
    for name,event in old.items():
        if event['kind']=='background_music':continue
        e=new[name]
        for key in ('kind','start','duration','peak_dbfs','pan','cycle','seed','start_sample','samples','end_seconds'):
            assert e[key]==event[key],(name,key)
        assert sha(EP/'audio'/e['file'])==sha(BASE/'audio'/event['file'])==e['sha256'],name
        data=pcm(EP/'audio'/e['file']).astype(np.float64);start=int(e['start_sample'])
        foreground[start:start+len(data)]+=data;preserved.append(name)
    assert len(preserved)==63
    event=next(e for e in new.values() if e['kind']=='background_music');parameters=event['parameters']
    music_pcm=pcm(EP/'audio'/event['file']);raw_pcm=pcm(EP/'audio/musique_sans_baisse.wav');mix_pcm=pcm(EP/'audio/mix.wav')
    assert music_pcm.shape==raw_pcm.shape==mix_pcm.shape==(n,2)
    assert sha(EP/'audio'/event['file'])==event['sha256'] and sha(EP/'audio/mix.wav')==audit['mix_sha256']
    assert not mix_pcm[0].any() and not mix_pcm[-1].any()
    assert not np.count_nonzero(np.abs(mix_pcm.astype(np.int32))>=32767),'PCM clipping'
    mix=mix_pcm.astype(np.float64)/32768.;music=music_pcm.astype(np.float64)/32768.;raw=raw_pcm.astype(np.float64)/32768.
    assert np.abs(mix).max()<.95 and np.max(np.abs(mix.mean(axis=0)))<.001
    error=np.abs((foreground+music_pcm)*MASTER-mix_pcm)[round(.01*SR):round((duration-.04)*SR)]
    assert float(error.max())<12.,('foreground mix changed',float(error.max()))
    spec=importlib.util.spec_from_file_location('independent_v17_music',EP/'sources/music.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    specification=parameters['effective_specification']
    score=score_checks(module,specification,parameters,duration)
    gain=np.asarray(module.gain_envelope(duration,specification),dtype=np.float64)
    assert gain.shape==(n,) and np.isfinite(gain).all()
    target=10.**(-3./20.)
    assert float(specification['duck_db'])==-3.
    assert abs(float(specification['duck_attack_seconds'])-.5)<1.e-9
    assert abs(float(specification['duck_release_seconds'])-.7)<1.e-9
    assert abs(float(gain.min())-target)<1.e-9 and abs(float(gain.max())-1.)<1.e-9
    quant_error=np.abs(raw_pcm.astype(np.float64)*gain[:,None]-music_pcm)
    assert float(quant_error.max())<2.,'exported music is not raw times the sole duck envelope'
    assert float(np.abs(np.diff(gain)).max())<.00005,'fast gain jump'
    times=np.arange(n)/SR;allowed=np.zeros(n,dtype=bool);sinks=[]
    for c in timeline['cycles']:
        a,b=c['sink'];sl=slice(round(a*SR),round(b*SR));g=gain[sl]
        assert np.allclose(g,target,atol=1.e-9)
        allowed|=(times>=a-.5-1./SR)&(times<=b+.7+1./SR)
        assert abs(db(rms(music[sl])/rms(raw[sl]))+3.)<.05
        water=new[f'c{c["id"]}_eau'];wa=round(water['start']*SR);wb=round(water['end_seconds']*SR)
        water_level=rms(pcm(EP/'audio'/water['file']).astype(np.float64)/32768.)
        music_level=rms(music[wa:wb])
        sinks.append({'cycle':c['id'],'seconds':[a,b],'export_measured_duck_db':db(rms(music[sl])/rms(raw[sl])),
            'music_rms_dbfs_postmaster':db(music_level*MASTER),
            'water_minus_music_rms_db':db(water_level/music_level)})
    assert np.allclose(gain[~allowed],1.,atol=1.e-12),'extra music dips outside wash ramps'
    raw_post=raw*MASTER;music_post=music*MASTER
    raw_rows=rolling_levels(raw_post,.2);music_rows=rolling_levels(music_post,.2)
    raw100=rolling_levels(raw_post,.1);music100=rolling_levels(music_post,.1)
    assert min(e['dbfs'] for e in raw_rows)>=-45.,('near-silent 200ms raw',min(raw_rows,key=lambda e:e['dbfs']))
    assert min(e['dbfs'] for e in music_rows)>=-48.,('near-silent 200ms music',min(music_rows,key=lambda e:e['dbfs']))
    assert min(e['dbfs'] for e in raw100)>=-52. and min(e['dbfs'] for e in music100)>=-55.,'100ms musical dropout'
    raw_level=db(rms(raw_post[round(.15*SR):round((duration-.2)*SR)]))
    assert -33.5<=raw_level<=-28.5,('normal music floor/level unsuitable for target',raw_level)
    assert summary(raw_rows)['p95_minus_p5_db']<=12.,'excessive short-term level variation'
    regressions=[]
    old_pcm=pcm(BASE/'audio/musique_cuisine.wav').astype(np.float64)/32768.*MASTER
    for start in KNOWN_GAPS:
        sl=slice(round(start*SR),round((start+.2)*SR))
        regressions.append({'seconds':[start,start+.2],'v16_dbfs':db(rms(old_pcm[sl])),
            'v17_music_dbfs':db(rms(music_post[sl])),'v17_raw_dbfs':db(rms(raw_post[sl]))})
        assert db(rms(music_post[sl]))>=-48.,('known dropout regression',start)
    phone=phoneband(EP/'audio/musique_sans_baisse.wav')
    assert len(phone)==n
    phone_level=db(rms(phone[round(.15*SR):round((duration-.2)*SR)]))
    assert phone_level>=-41.,('midrange bed too weak for phoneband safeguard',phone_level)
    contacts=[]
    for name in ('carotte_coupe_1','carotte_coupe_2','couteau_pose','contact_tomate','sel_pince','sel_saupoudre'):
        e=new[name];data=pcm(EP/'audio'/e['file']).astype(np.float64)/32768.
        onset=round(e['start']*SR);length=min(len(data),round(.2*SR));background=rms(music[onset:onset+length])
        contacts.append({'event':name,'start':e['start'],'foley_peak_minus_music_rms_db':db(float(np.abs(data[:length]).max())/background),
                         'potential_masking_flag':bool(float(np.abs(data[:length]).max())<background*10.**(3./20.))})
    assets=list((EP/'assets').glob('*.sf2'));assert len(assets)==1
    assert sha(assets[0]) in json.dumps(parameters) and 'fluidsynth' in json.dumps(parameters).lower()
    return {'nonmusic_wavs_byte_identical':len(preserved),'master_gain_linear_exact':MASTER,
        'mix_reconstruction_max_error_pcm':float(error.max()),'mix_reconstruction_rms_error_pcm':float(np.sqrt(np.mean(error*error))),
        'mix_sha256':sha(EP/'audio/mix.wav'),'music_sha256':sha(EP/'audio'/event['file']),
        'raw_sha256':sha(EP/'audio/musique_sans_baisse.wav'),'score':score,
        'gain_min_max':[float(gain.min()),float(gain.max())],'raw_times_gain_max_error_pcm':float(quant_error.max()),
        'wash_checks':sinks,'raw_normal_rms_dbfs_postmaster':raw_level,
        'rolling_200ms_raw':summary(raw_rows),'rolling_200ms_music':summary(music_rows),
        'rolling_100ms_raw':summary(raw100),'rolling_100ms_music':summary(music100),
        'window_hop_seconds':.02,'known_v16_dropout_regressions':regressions,
        'phoneband_180_6000hz_raw_rms_dbfs_postmaster':phone_level,
        'phoneband_loss_db':raw_level-phone_level,'contact_level_context':contacts,
        'mix_peak_dbfs':db(float(np.abs(mix).max())),'clipped_samples':0,
        'mix_dc_mean_left_right':mix.mean(axis=0).tolist(),
        'limits':'Signal/score safeguards and phone-band approximation; these numbers do not prove perceptual listening or preference.'}


def video_checks():
    f=EP/'MOU_Encore_une_feuille.mp4';old=BASE/f.name;silent=EP/'MOU_Encore_une_feuille_muette.mp4'
    stream=bitstream(old);assert bitstream(f)==bitstream(silent)==stream
    assert sha(silent)==sha(BASE/silent.name)
    info=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(f)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],int(v['nb_read_frames']))==(1080,1920,984) and v['r_frame_rate']=='24/1'
    assert abs(float(info['format']['duration'])-41.)<.025 and a['codec_name']=='aac'
    assert (int(a['sample_rate']),int(a['channels']))==(SR,2) and abs(float(a['duration'])-41.)<.025
    raw=command(['ffmpeg','-v','error','-xerror','-i',str(f),'-map','0:a:0','-t','41','-ar',str(SR),'-ac','2','-c:a','pcm_f32le','-f','f32le','-'])
    decoded=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64);reference=pcm(EP/'audio/mix.wav').astype(np.float64)/32768.
    assert decoded.shape==reference.shape and np.isfinite(decoded).all() and np.abs(decoded).max()<.999
    corr=float(np.dot(decoded.ravel(),reference.ravel())/math.sqrt(float(np.square(decoded).sum())*float(np.square(reference).sum())))
    assert corr>.98
    packets=json.loads(command(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(f)]))['packets']
    gaps=[float(b['pts_time'])-(float(a['pts_time'])+float(a['duration_time'])) for a,b in zip(packets,packets[1:])]
    assert max(gaps)<2.e-6,'AAC transport gap'
    return {'mp4_sha256':sha(f),'h264_byte_identical_to_v16':stream,'silent_mp4_byte_identical':True,
        'aac_vs_current_wav_correlation':corr,'aac_peak_dbfs':db(float(np.abs(decoded).max())),
        'aac_packets':len(packets),'maximum_aac_packet_gap_seconds':max(gaps)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--final',action='store_true');args=p.parse_args()
    report={'status':'in_progress','scope':'V17 known audible-gap regressions: independent score, short-window PCM, envelope and transport safeguards',
        'limits':'No perceptual listening, phone playback or artistic approval is claimed. Passing numbers alone cannot establish continuous musical feel.'}
    tracked=[EP/'sources'/name for name in ('music.py','son.py','render.py','animation.py','art.py','sink.py','mitten.py')]
    tracked+=[EP/'audio'/name for name in ('mix.wav','musique_cuisine.wav','musique_sans_baisse.wav')]
    frozen={str(x):sha(x) for x in tracked}
    try:
        report['visual_preservation']=preservation();report['audio']=audio_checks()
        if args.final:report['final_video']=video_checks()
        assert frozen=={str(x):sha(x) for x in tracked},'production files changed during audit'
        report['tested_source_and_audio_sha256']=frozen;report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n');raise
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'report':str(REPORT),'final_checked':args.final,
        'raw_normal_rms':report['audio']['raw_normal_rms_dbfs_postmaster'],
        'minimum_200ms_music':report['audio']['rolling_200ms_music']['minimum'],
        'phoneband_rms':report['audio']['phoneband_180_6000hz_raw_rms_dbfs_postmaster']}))


if __name__=='__main__':main()
