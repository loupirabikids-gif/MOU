"""Independent checks for MOU's music-only revision; never synthesizes audio.

Run in the full checkout after the sound files have been frozen. --final
also checks the exported MP4 and its preserved H.264 video stream. Musical
taste and listening quality cannot be established by these numeric checks.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS = EP.parent/'cuisine_v14'
REPORT = EP/'controle/audit_audio_v15.json'
SR = 48000


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db(value):
    return None if value <= 0. else round(20.*math.log10(float(value)), 9)


def rms(value):
    return float(np.sqrt(np.mean(np.square(value)))) if value.size else 0.


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(), source.getnchannels(), source.getsampwidth()) == (SR,2,2),path
        samples = np.frombuffer(source.readframes(source.getnframes()), '<i2').reshape(-1,2).copy()
    return samples


def command(args):
    return subprocess.check_output(args, stderr=subprocess.PIPE)


def bitstream(path):
    raw = command(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0',
        '-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])
    return {'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}


def visual_preservation():
    result={}
    for name in ('chronologie.json','sources/animation.py','sources/art.py',
                 'sources/sink.py','sources/mitten.py'):
        assert digest(EP/name) == digest(PREVIOUS/name),name
        result[name]={'byte_identical':True,'sha256':digest(EP/name)}
    # Renderer metadata/source-freeze bookkeeping may be adapted. The actual
    # emitted scene and camera functions must remain the same.
    def definitions(path):
        tree=ast.parse(path.read_text())
        return {n.name:ast.dump(n,include_attributes=False) for n in tree.body
                if isinstance(n,ast.FunctionDef)}
    before=definitions(PREVIOUS/'sources/render.py')
    after=definitions(EP/'sources/render.py')
    assert digest(EP/'sources/render.py')==digest(PREVIOUS/'sources/render.py'),'visual renderer changed'
    for name in ('svg_at','camera_at','caption_svg_at','caption_image'):
        assert before[name]==after[name],('visual renderer changed',name)
    result['sources/render.py']={'byte_identical':digest(EP/'sources/render.py')==digest(PREVIOUS/'sources/render.py'),
        'scene_camera_caption_functions_identical':True}
    return result


def audio_checks():
    timeline=json.loads((EP/'chronologie.json').read_text())
    before=json.loads((PREVIOUS/'audio/provenance.json').read_text())
    after=json.loads((EP/'audio/provenance.json').read_text())
    old_events={e['name']:e for e in before['events']}
    new_events={e['name']:e for e in after['events']}
    assert len(old_events)==len(new_events)==64
    assert old_events.keys()==new_events.keys()
    preserved=[]
    for name,old in old_events.items():
        if old['kind']=='background_music':
            continue
        current=new_events[name]
        for key in ('kind','start','duration','peak_dbfs','pan','cycle','seed',
                    'start_sample','samples','end_seconds'):
            assert current[key]==old[key],(name,key)
        assert digest(EP/'audio'/current['file'])==digest(PREVIOUS/'audio'/old['file']),name
        assert digest(EP/'audio'/current['file'])==current['sha256'],name
        preserved.append(name)
    assert len(preserved)==63
    old_music=next(e for e in old_events.values() if e['kind']=='background_music')
    music_event=next(e for e in new_events.values() if e['kind']=='background_music')
    assert digest(EP/'audio'/music_event['file'])!=digest(PREVIOUS/'audio'/old_music['file'])
    old_mix=pcm(PREVIOUS/'audio/mix.wav');mix=pcm(EP/'audio/mix.wav')
    music=pcm(EP/'audio'/music_event['file'])
    previous_music=pcm(PREVIOUS/'audio'/old_music['file'])
    n=round(timeline['duration']*SR)
    assert old_mix.shape==mix.shape==music.shape==previous_music.shape==(n,2)
    mask=np.zeros(n,dtype=bool)
    windows=timeline['background_music']['windows']
    for a,b in windows:
        mask[round(a*SR):round(b*SR)]=True
    assert not music[~mask].any(),'music outside cooking windows'
    assert np.array_equal(mix[~mask],old_mix[~mask]),'nonmusical mix changed: master or Foley levels moved'
    assert np.count_nonzero(mix[mask]!=old_mix[mask])>0,'mix not updated with new music'
    assert not mix[0].any() and not mix[-1].any()
    assert not np.count_nonzero(np.abs(mix.astype(np.int32))>=32767),'clipping'
    normalized=mix.astype(np.float64)/32768.
    dc=normalized.mean(axis=0)
    assert np.max(np.abs(dc))<.001,('excessive DC',dc)
    assert float(np.abs(normalized).max())<.95,'insufficient PCM headroom'
    # Check all forbidden action ranges, not merely the gap mask.
    forbidden=[]
    for cycle in timeline['cycles']:
        for action in ('sink','wash','wipe','crumple','throw','zoom'):
            a,b=cycle[action]
            segment=music[round(a*SR):round(b*SR)]
            assert not segment.any(),(cycle['id'],action,'music should be absent')
            forbidden.append({'cycle':cycle['id'],'action':action,'seconds':[a,b],'nonzero_samples':0})
    a,b=timeline['final'];assert not music[round(a*SR):round(b*SR)].any()
    transitions=[]
    for a,b in windows:
        start,end=round(a*SR),round(b*SR)
        assert not music[start].any() and not music[end-1].any(),'music ramps must reach zero at cuts'
        # These sample steps address the cut boundary; they do not claim
        # that the whole performance has been perceptually checked for pops.
        in_step=float(np.abs(music[start].astype(np.int32)-(music[start-1] if start else 0)).max())
        out_step=float(np.abs(music[end-1].astype(np.int32)-(music[end] if end<n else 0)).max())
        transitions.append({'seconds':[a,b],'first_last_samples_zero':True,
            'maximum_boundary_step_pcm':max(in_step,out_step),
            'first_10ms_rms_dbfs':db(rms(music[start:min(start+480,end)].astype(np.float64)/32768.)),
            'last_10ms_rms_dbfs':db(rms(music[max(start,end-480):end].astype(np.float64)/32768.))})
    # Sum unchanged foreground stems for level context. This does not infer
    # intelligibility from an RMS number or replace a phone-speaker audition.
    foreground=np.zeros((n,2),dtype=np.float64)
    for name in preserved:
        e=new_events[name]
        if e['kind']=='frying':continue
        stem=pcm(EP/'audio'/e['file']).astype(np.float64)/32768.
        start=int(e['start_sample'])
        foreground[start:start+len(stem)]+=stem
    levels=[]
    for j,(a,b) in enumerate(windows,1):
        sl=slice(round(a*SR),round(b*SR))
        value=music[sl].astype(np.float64)/32768.
        levels.append({'window':j,'seconds':[a,b],
            'new_music_rms_dbfs_before_master':db(rms(value)),
            'old_music_rms_dbfs_before_master':db(rms(previous_music[sl].astype(np.float64)/32768.)),
            'unchanged_foreground_rms_dbfs_before_master':db(rms(foreground[sl])),
            'new_mix_rms_dbfs':db(rms(normalized[sl])),
            'old_mix_rms_dbfs':db(rms(old_mix[sl].astype(np.float64)/32768.))})
    opening_whistle=[]
    for e in new_events.values():
        if e['kind']!='whistle':continue
        sl=slice(e['start_sample'],e['start_sample']+e['samples'])
        whistle=pcm(EP/'audio'/e['file']).astype(np.float64)/32768.
        opening_whistle.append({'name':e['name'],'seconds':[e['start'],e['end_seconds']],
            'whistle_rms_dbfs_before_master':db(rms(whistle)),
            'music_rms_dbfs_during_note_before_master':db(rms(music[sl].astype(np.float64)/32768.))})
    parameters=music_event.get('parameters',{})
    score=parameters.get('notes',[])
    assert score,'score notes missing from music provenance'
    signatures={}
    for j,(a,b) in enumerate(windows,1):
        notes=[note for note in score if note.get('window')==j]
        assert notes,('empty score window',j)
        for note in notes:
            assert note['start']>=a-1e-7 and note['start']+note['duration']<=b+1e-7,('note spills outside window',note)
        signature=[(round(note['start']-a,4),note.get('midi_note'),note.get('instrument')) for note in notes]
        signatures[str(j)]=signature
    assert len({json.dumps(v,sort_keys=True) for v in signatures.values()})>=2,'score has no window variation'
    assets=list((EP/'assets').rglob('*.sf2'))
    assert len(assets)==1,'one bundled SF2 expected'
    asset=assets[0]
    credits='\n'.join(p.read_text(errors='replace') for p in (EP/'assets').rglob('*')
                      if p.is_file() and p.suffix.lower()!='.sf2')
    assert 'Tim Brechbill' in credits,'SF2 attribution missing'
    assert 'GPL-2' in credits or 'GNU GENERAL PUBLIC LICENSE' in credits,'SF2 free-software license missing'
    parameter_text=json.dumps(parameters,ensure_ascii=False)
    assert digest(asset) in parameter_text,'actual SF2 checksum missing from music provenance'
    assert 'fluidsynth' in parameter_text.lower(),'synthesis engine missing from music provenance'
    return {'events':64,'nonmusic_events_byte_identical':preserved,
        'master_preservation':'All mix PCM samples outside musical windows match V14 exactly.',
        'outside_music_window_changed_mix_samples':0,'music_file_sha256':digest(EP/'audio'/music_event['file']),
        'mix_sha256':digest(EP/'audio/mix.wav'),'music_windows_seconds':windows,
        'outside_window_nonzero_music_samples':0,'forbidden_music_intervals':forbidden,
        'final_music_silent':True,'music_cut_boundary_checks':transitions,
        'mix_peak_dbfs':db(float(np.abs(normalized).max())),
        'mix_dc_mean_left_right':dc.tolist(),'clipped_samples':0,
        'window_level_context':levels,'opening_whistle_level_context':opening_whistle,
        'window_score_signatures':signatures,
        'bundled_sf2':{'file':str(asset.relative_to(ROOT)),'sha256':digest(asset),'attribution_and_license_present':True},
        'music_parameters':parameters}


def final_video_checks():
    current=EP/'MOU_Encore_une_feuille.mp4'
    old=PREVIOUS/current.name
    silent=EP/'MOU_Encore_une_feuille_muette.mp4'
    expected=bitstream(old)
    assert bitstream(current)==expected,'video frames were reencoded or changed'
    assert bitstream(silent)==expected,'silent video differs from V14'
    assert digest(silent)==digest(PREVIOUS/silent.name),'silent MP4 should be copied unchanged'
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
    assert correlation>.98,('AAC does not match new mix',correlation)
    assert np.isfinite(decoded).all() and float(np.abs(decoded).max())<.999
    return {'video_sha256':digest(current),'video_size_bytes':current.stat().st_size,
        'video_h264_bitstream_identical_to_v14':expected,'silent_mp4_byte_identical_to_v14':True,
        'dimensions':[1080,1920],'duration_seconds':41.,'frames':984,
        'new_aac_vs_wav_correlation':correlation,'new_aac_peak_dbfs':db(float(np.abs(decoded).max()))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true')
    args=parser.parse_args()
    report={'status':'in_progress','scope':'Music-only revision; V14 image and Foley preservation',
        'limits':'Numeric PCM, score, attribution and bitstream checks. No claimed listening, public test or artistic guarantee.'}
    try:
        report['visual_preservation']=visual_preservation()
        report['audio']=audio_checks()
        if args.final:report['final_video']=final_video_checks()
        report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        raise
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'final_video_checked':args.final,
        'report':str(REPORT),'nonmusic_wav_preserved':len(report['audio']['nonmusic_events_byte_identical'])},ensure_ascii=False))


if __name__=='__main__':
    main()
