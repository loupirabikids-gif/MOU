"""Independent audit of continuous music and washing-only ducking.

Run after the composer freezes the V16 sources and WAVs. --final also checks
the delivered MP4. This script reads exports and the scalar gain envelope;
it never synthesizes audio and cannot establish musical taste by measurement.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS = EP.parent/'cuisine_v15'
REPORT = EP/'controle/audit_audio_v16.json'
SR = 48000
MASTER = 2.124210976406158


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db(value):
    return None if value <= 0. else round(20.*math.log10(float(value)), 9)


def rms(value):
    return float(np.sqrt(np.mean(np.square(value)))) if value.size else 0.


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(SR,2,2),path
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2).copy()


def command(args):
    return subprocess.check_output(args,stderr=subprocess.PIPE)


def bitstream(path):
    raw=command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0',
        '-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def visual_preservation():
    result={}
    for name in ('chronologie.json','sources/animation.py','sources/art.py',
                 'sources/render.py','sources/sink.py','sources/mitten.py'):
        assert digest(EP/name)==digest(PREVIOUS/name),name
        result[name]={'byte_identical':True,'sha256':digest(EP/name)}
    assert digest(ROOT/'mou_rig.py')=='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    return result


def audio_checks():
    timeline=json.loads((EP/'chronologie.json').read_text())
    before=json.loads((PREVIOUS/'audio/provenance.json').read_text())
    after=json.loads((EP/'audio/provenance.json').read_text())
    audit=json.loads((EP/'controle/audit_son.json').read_text())
    old_events={e['name']:e for e in before['events']}
    new_events={e['name']:e for e in after['events']}
    assert len(old_events)==len(new_events)==64
    assert old_events.keys()==new_events.keys()
    assert abs(float(audit['master_gain_linear_exact'])-MASTER)<1e-14,'master gain changed'
    n=round(timeline['duration']*SR)
    foreground=np.zeros((n,2),dtype=np.float64)
    preserved=[]
    for name,old in old_events.items():
        if old['kind']=='background_music':continue
        current=new_events[name]
        for key in ('kind','start','duration','peak_dbfs','pan','cycle','seed',
                    'start_sample','samples','end_seconds'):
            assert current[key]==old[key],(name,key)
        path=EP/'audio'/current['file']
        assert digest(path)==digest(PREVIOUS/'audio'/old['file']),name
        assert digest(path)==current['sha256'],name
        samples=pcm(path).astype(np.float64)/32767.
        start=int(current['start_sample'])
        foreground[start:start+len(samples)]+=samples
        preserved.append(name)
    assert len(preserved)==63
    event=next(e for e in new_events.values() if e['kind']=='background_music')
    parameters=event['parameters']
    music_pcm=pcm(EP/'audio'/event['file'])
    raw_pcm=pcm(EP/'audio/musique_sans_baisse.wav')
    mix_pcm=pcm(EP/'audio/mix.wav')
    assert music_pcm.shape==raw_pcm.shape==mix_pcm.shape==(n,2)
    assert digest(EP/'audio'/event['file'])==event['sha256']
    assert digest(EP/'audio/mix.wav')==audit['mix_sha256']
    music=music_pcm.astype(np.float64)/32767.
    raw=raw_pcm.astype(np.float64)/32767.
    mix=mix_pcm.astype(np.float64)/32767.
    assert not mix_pcm[0].any() and not mix_pcm[-1].any()
    assert not np.count_nonzero(np.abs(mix_pcm.astype(np.int32))>=32767),'mix clipping'
    assert np.max(np.abs(mix.mean(axis=0)))<.001,'excessive DC'
    assert np.abs(mix).max()<.95,'insufficient PCM headroom'
    # Quantized event WAVs approximate their original float stems. Reconstruct
    # the interior of the delivered mix to detect a changed foreground gain.
    reconstructed=(foreground+music)*MASTER*32767.
    interior=slice(round(.010*SR),round((timeline['duration']-.040)*SR))
    error=np.abs(reconstructed[interior]-mix_pcm[interior])
    assert float(error.max())<=12.,('mix is not unchanged foreground + ducked music',float(error.max()))
    # No synth is called: only its documented scalar ducking envelope is read.
    spec=importlib.util.spec_from_file_location('audit_music_gain_v16',EP/'sources/music.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    specification=parameters['effective_specification']
    gain=np.asarray(module.gain_envelope(float(timeline['duration']),specification),dtype=np.float64)
    assert gain.shape==(n,) and np.isfinite(gain).all()
    target_duck_db=float(specification['duck_db'])
    assert abs(target_duck_db+6.)<1e-9,'the agreed washing reduction is -6 dB'
    target_gain=10.**(target_duck_db/20.)
    assert abs(float(gain.min())-target_gain)<1e-9 and float(gain.max())<=1.+1e-12
    assert not np.any(gain<=0.),'music gated to zero'
    quantization_error=np.abs(raw_pcm.astype(np.float64)*gain[:,None]-music_pcm.astype(np.float64))
    assert float(quantization_error.max())<=2.,('raw/envelope does not match delivered music',float(quantization_error.max()))
    assert float(np.max(np.abs(np.diff(gain))))<.001,'gain discontinuity'
    times=np.arange(n)/SR
    allowed_transition=np.zeros(n,dtype=bool)
    sinks=[]
    for cycle in timeline['cycles']:
        a,b=cycle['sink'];start,end=round(a*SR),round(b*SR)
        g=gain[start:end]
        assert float(g.max()-g.min())<1e-9,'washing level should have a constant duck plateau'
        attenuation=db(float(g.mean()))
        assert attenuation is not None and abs(attenuation-target_duck_db)<.05,(cycle['id'],attenuation)
        measured=db(rms(music[start:end])/rms(raw[start:end]))
        assert measured is not None and abs(measured-attenuation)<.15,(cycle['id'],measured,attenuation)
        assert rms(music[start:end])>10.**(-85./20.),'music absent in sink insert'
        allowed_transition |= (times>=a-.120-1./SR)&(times<b+.180+1./SR)
        water=new_events[f'c{cycle["id"]}_eau']
        wa,wb=round(water['start']*SR),round(water['end_seconds']*SR)
        water_rms=rms(pcm(EP/'audio'/water['file']).astype(np.float64)/32767.)
        music_rms=rms(music[wa:wb])
        sinks.append({'cycle':cycle['id'],'seconds':[a,b],
            'scalar_gain':float(g.mean()),'attenuation_db':attenuation,
            'measured_export_attenuation_db':measured,'music_present':True,
            'water_rms_dbfs_before_master':db(water_rms),
            'music_rms_dbfs_during_water_before_master':db(music_rms),
            'water_minus_music_rms_db':db(water_rms/music_rms)})
    assert np.allclose(gain[~allowed_transition],1.,atol=1e-12),'extra level drops outside washes'
    # These intervals used to be music-free. The new request replaces that
    # rule: the score must continue through wiping, crumpling, bin shots/end.
    continued=[]
    for cycle in timeline['cycles']:
        for action in ('wipe','crumple','throw','zoom'):
            a,b=cycle[action];sl=slice(round(a*SR),round(b*SR))
            level=rms(music[sl]);assert level>10.**(-85./20.),(cycle['id'],action,'music unexpectedly absent')
            continued.append({'cycle':cycle['id'],'action':action,'seconds':[a,b],
                'music_rms_dbfs_before_master':db(level),'music_present':True})
    a,b=timeline['final'];assert rms(music[round(a*SR):round((b-.15)*SR)])>10.**(-85./20.)
    # Overlapping half-second windows catch the residual 33.75--34.25 s gap
    # found during composition. This does not pretend each sample is a note.
    bins=[]
    for start in range(0,n-SR//2+1,SR//4):
        end=min(n,start+SR//2);level=rms(music[start:end])
        assert level>10.**(-75./20.),('unexpected near-silent half-second',start/SR,end/SR,db(level))
        bins.append({'seconds':[start/SR,end/SR],'music_rms_dbfs_before_master':db(level)})
    score=parameters['notes'];assert score,'missing score'
    assert parameters['windows_seconds']==[[0.,float(timeline['duration'])]],'music still divided into visual windows'
    assert parameters['one_global_clock'] is True and parameters['visual_cut_restarts']==0
    assert all(0.<=note['start']<float(timeline['duration']) and
               note['start']+note['duration']<=float(timeline['duration'])+1e-7
               for note in score),'notes outside the continuous score'
    for cycle in timeline['cycles']:
        a,b=cycle['sink']
        assert any(a<=note['start']<b for note in score),(cycle['id'],'score stopped at wash')
    assets=list((EP/'assets').glob('*.sf2'));assert len(assets)==1
    credits='\n'.join(p.read_text(errors='replace') for p in (EP/'assets').glob('*')
                     if p.is_file() and p.suffix!='.sf2')
    assert 'Tim Brechbill' in credits and ('GPL-2' in credits or 'GNU GENERAL PUBLIC LICENSE' in credits)
    assert digest(assets[0]) in json.dumps(parameters),'instrument checksum missing'
    assert 'fluidsynth' in json.dumps(parameters).lower(),'engine provenance missing'
    return {'events':64,'nonmusic_events_byte_identical':preserved,
        'master_gain_linear_exact':MASTER,
        'mix_reconstruction_from_quantized_event_wavs_max_error_pcm':float(error.max()),
        'mix_reconstruction_rms_error_pcm':float(np.sqrt(np.mean(error*error))),
        'raw_stem_sha256':digest(EP/'audio/musique_sans_baisse.wav'),
        'music_sha256':digest(EP/'audio'/event['file']),'mix_sha256':digest(EP/'audio/mix.wav'),
        'raw_times_scalar_gain_max_error_pcm':float(quantization_error.max()),
        'minimum_gain':float(gain.min()),'maximum_gain':float(gain.max()),
        'max_gain_sample_step':float(np.max(np.abs(np.diff(gain)))),
        'washing_duck_checks':sinks,'music_continues_during_former_silent_actions':continued,
        'half_second_continuity_levels':bins,'continuity_window_hop_seconds':.25,
        'continuity_floor_dbfs_before_master':-75.,'music_present_in_final':True,
        'mix_peak_dbfs':db(float(np.abs(mix).max())),
        'mix_dc_mean_left_right':mix.mean(axis=0).tolist(),'clipped_samples':0,
        'score_note_count':len(score),'single_music_window_seconds':[0.,float(timeline['duration'])],
        'global_clock_without_visual_cut_restarts':True,'music_parameters':parameters,
        'bundled_sf2_sha256':digest(assets[0])}


def final_video_checks():
    current=EP/'MOU_Encore_une_feuille.mp4';old=PREVIOUS/current.name
    silent=EP/'MOU_Encore_une_feuille_muette.mp4'
    expected=bitstream(old)
    assert bitstream(current)==expected,'video changed or reencoded'
    assert bitstream(silent)==expected
    assert digest(silent)==digest(PREVIOUS/silent.name),'silent MP4 changed'
    info=json.loads(command(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(current)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],int(v['nb_read_frames']))==(1080,1920,984)
    assert v['r_frame_rate']=='24/1' and abs(float(info['format']['duration'])-41.)<.025
    assert a['codec_name']=='aac' and (int(a['sample_rate']),int(a['channels']))==(SR,2)
    raw=command(['ffmpeg','-v','error','-xerror','-i',str(current),'-map','0:a:0',
        '-t','41','-ar',str(SR),'-ac','2','-c:a','pcm_f32le','-f','f32le','-'])
    decoded=np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)
    reference=pcm(EP/'audio/mix.wav').astype(np.float64)/32768.
    assert decoded.shape==reference.shape
    correlation=float(np.dot(decoded.ravel(),reference.ravel())/math.sqrt(
        float(np.square(decoded).sum())*float(np.square(reference).sum())))
    assert correlation>.98 and np.isfinite(decoded).all() and np.abs(decoded).max()<.999
    return {'video_sha256':digest(current),'video_size_bytes':current.stat().st_size,
        'video_h264_bitstream_identical_to_v15':expected,'silent_mp4_byte_identical_to_v15':True,
        'dimensions':[1080,1920],'duration_seconds':41.,'frames':984,
        'new_aac_vs_wav_correlation':correlation,'new_aac_peak_dbfs':db(float(np.abs(decoded).max()))}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    report={'status':'in_progress','scope':'Continuous music with washing-only ducking; V15 image/Foley preservation',
        'limits':'PCM, gain envelope, written score, provenance and bitstream checks; no listening or artistic preference claimed.'}
    tracked=[EP/'sources'/name for name in ('music.py','son.py','render.py','animation.py','art.py','sink.py','mitten.py')]
    tracked += [EP/'audio/mix.wav',EP/'audio/musique_cuisine.wav',EP/'audio/musique_sans_baisse.wav']
    frozen={str(p):digest(p) for p in tracked}
    try:
        report['visual_preservation']=visual_preservation();report['audio']=audio_checks()
        if args.final:report['final_video']=final_video_checks()
        assert frozen=={str(p):digest(p) for p in tracked},'sources/audio changed during audit'
        report['tested_sources_and_audio_sha256']=frozen;report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'final_video_checked':args.final,
        'report':str(REPORT),'preserved_nonmusic_wavs':len(report['audio']['nonmusic_events_byte_identical']),
        'duck_db':[v['measured_export_attenuation_db'] for v in report['audio']['washing_duck_checks']]},ensure_ascii=False))


if __name__=='__main__':
    main()
