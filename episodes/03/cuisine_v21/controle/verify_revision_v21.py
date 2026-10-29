"""Independent geometry, continuity and audio checks for the V21 acting revision.

These checks do not judge whether an emotion is felt by a viewer. Rendered
acting needs its separate visual review. External V20 comparisons are marked
unavailable when this script is run from a standalone source archive.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import sys
import wave
import xml.etree.ElementTree as ET

import numpy as np

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
PREVIOUS = EP.parent/'cuisine_v20'
RIG_SHA = '7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
COSTUME_SHA = '39bd95eb065c632c16d345f244ba21d66a08e0395cbbbf4bc0cd8e4f952938bb'
BASE19_SHA = '8ddc8746a5ec7ae7d5914a29245eb1033982029c2e1b3b4fd1b7cb415ac5874a'
BASE20_SHA = 'd7170eb6c75f9fa1effeb0de4e2f1a66f4ece2d685afc08d2a6b4a4e57127791'
PRESERVED = ('arms','hands','actor_transform','spoon','spoon_held','tomato',
             'tomato_added','paper','water','lever','bin_count','flying_ball',
             'floor_ball','roll','carrot','salt')
ARM_FUNCTIONS = ('controls','native_grip','world_grip','solve_arm',
                 'arm_linear_transform','_connect_left_root','soften_left_root','draw_arm')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result)
    return result


def pcm(path):
    with wave.open(str(path),'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(48000,2,2)
        return np.frombuffer(source.readframes(source.getnframes()),'<i2').reshape(-1,2)


def wave_sha(samples):
    buffer=io.BytesIO()
    with wave.open(buffer,'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
        out.writeframes(samples.astype('<i2').tobytes())
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def polygon_numbers(path):
    values=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',path)))
    return list(zip(values[::2],values[1::2]))


def cap_polygon(animation,state,side='left'):
    """Read the native rendered cap vertices, then apply its actual rigid pose."""
    meta=state['arm_meta'][side]
    native=ET.fromstring(animation._arm(side,meta['hips'],meta['clasp']))
    points=polygon_numbers(native[0].attrib['d'])[64:89]
    assert len(points)==25
    sx,sy=animation.SHOULDERS[side]
    aa,ab,ba,bb=animation.arm_linear_transform(meta['rotation'],meta.get('reflect_axis'))
    x,y,scale=state['actor_transform']
    return [(x+scale*(sx+aa*(px-sx)+ab*(py-sy)),
             y+scale*(sy+ba*(px-sx)+bb*(py-sy))) for px,py in points]


def distance_to_edge(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    u=max(0.,min(1.,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy)))
    return math.hypot(p[0]-a[0]-u*vx,p[1]-a[1]-u*vy)


def distance_to_polygon(point,polygon):
    return min(distance_to_edge(point,a,polygon[(i+1)%len(polygon)])
               for i,a in enumerate(polygon))


def contains(point,polygon):
    x,y=point;inside=False;previous=polygon[-1]
    for current in polygon:
        ax,ay=previous;bx,by=current
        if (ay>y)!=(by>y) and x<ax+(y-ay)*(bx-ax)/(by-ay):inside=not inside
        previous=current
    return inside


def ball_vertices(art,ball):
    group=ET.fromstring(art._ball(ball['x'],ball['y'],ball['r'],ball['rotation'],ball['visual_seed']))
    tx,ty,angle,sx,sy=map(float,re.findall(r'-?\d+(?:\.\d+)?',group.attrib['transform']))
    ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    return [(tx+ca*sx*x-sa*sy*y,ty+sa*sx*x+ca*sy*y)
            for x,y in polygon_numbers(group[0].attrib['d'])]


def ast_functions(path):
    return {n.name:ast.dump(n,include_attributes=False)
            for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}


def scene_checks(renderer):
    previous_path=PREVIOUS/'sources/render.py'
    previous=module('acting_reference_v20',previous_path) if previous_path.is_file() else None
    if previous:
        old,new=ast_functions(PREVIOUS/'sources/animation.py'),ast_functions(EP/'sources/animation.py')
        for name in ARM_FUNCTIONS:assert old[name]==new[name],(name,'Native articulation changed')
    frames=round(renderer.DURATION*renderer.FPS);assert frames==1068
    spec=renderer.TIMELINE['ending_apron'];start=float(spec['start'])
    body_reference=None;compared=sink_count=visible_paper=wet_frames=cloth_frames=0
    anchor_gaps=[];contact_records=[];wetness=[];phase_samples={};counts=[]
    for index in range(frames):
        t=index/renderer.FPS;state=renderer.animation.scene_state(t)
        vx,vy,vw,vh=renderer.camera_at(state['t'],state)
        assert vx>=-1.e-8 and vy>=-1.e-8 and vx+vw<=1080.+1.e-8 and vy+vh<=1920.+1.e-8,(t,'Camera exits decor')
        body=re.search(r'<g id="body">(.*?)</g>',state['torso'])[1]
        if body_reference is None:body_reference=body
        assert body==body_reference,(t,'Canonical body contour changed')
        assert hashlib.sha256(renderer.costume.costume_svg(state).encode()).hexdigest()==COSTUME_SHA
        if previous and t<start:
            old_state=previous.animation.scene_state(t)
            for name in PRESERVED:assert state[name]==old_state[name],(t,name,'Historical action changed')
            compared+=1
            if state['shot']=='sink':
                assert renderer.svg_at(t)==previous.svg_at(t),(t,'Sink insert changed')
                sink_count+=1
        counts.append(state['bin_count'])
        if 38.65<=t<40.25 or t>=float(spec['waste_look'][0]):
            ball=state.get('flying_ball') or state.get('floor_ball')
            assert ball and ball['id']==5 and ball['r']==22.
            outline=ball_vertices(renderer.art,ball)
            assert all(vx+3<=x<=vx+vw-3 and vy+3<=y<=vy+vh-3 for x,y in outline),(t,'Final paper clipped')
            visible_paper+=1
        if t>=40.:
            ball=state.get('floor_ball')
            assert state['bin_count']==4 and ball and (ball['x'],ball['y'])==(325.,1805.)
        if t<start:continue
        phase=state['ending_phase']
        phase_samples.setdefault(phase,{'first_time':t,'pose':state['pose'],'look_target':state['look_target']})
        drop=state['ending_drop'];amount=float(drop['amount']);anchor=tuple(drop['anchor'])
        assert 0.<=amount<=1.
        cap=cap_polygon(renderer.animation,state)
        for side in ('left','right'):
            assert all(vx+6<=px<=vx+vw-6 and vy+6<=py<=vy+vh-6
                       for px,py in cap_polygon(renderer.animation,state,side)),(t,side,'Ending mitten clipped')
        if amount>0.:
            gap=distance_to_polygon(anchor,cap)
            assert gap<=8.,(t,gap,'Drop detached from native cap ink')
            assert anchor[1]>=max(p[1] for p in cap)-.1,(t,'Drop is not below the fingertip')
            assert vx+10<=anchor[0]<=vx+vw-10 and vy+2<=anchor[1] and anchor[1]+30<=vy+vh,(t,'Drop clipped')
            anchor_gaps.append(gap);wet_frames+=1
        contact=state['contact_apron'];wet=float(state['apron_wetness'])
        assert 0.<=wet<=1.;wetness.append(wet)
        if t<float(contact['contact_time']):
            assert amount==1. and wet==0.,(t,'Water disappears before apron contact')
        if contact['active']:
            point=tuple(contact['point'])
            distance=distance_to_polygon(point,cap)
            overlap=contains(point,cap) or distance<10.
            # A cloth point can leave the cap as it sweeps sideways. Check the
            # whole visible cloth strip as well, independent of metadata.
            x0,y0,scale=state['actor_transform']
            # This interior rectangle lies entirely inside the approved apron
            # front. Clip its lower edge above the foreground island so a
            # hidden cloth overlap cannot be mistaken for visible contact.
            cloth_rect=(x0+175.*scale,y0+357.*scale,
                        x0+226.*scale,min(y0+402.*scale,1255.))
            candidates=[(x,y) for x in np.linspace(cloth_rect[0],cloth_rect[2],13)
                         for y in np.linspace(cloth_rect[1],cloth_rect[3],8)]
            overlap=overlap or any(contains(p,cap) for p in candidates)
            assert overlap,(t,'Native fingertip cap does not reach visible apron')
            cloth_frames+=1
            contact_records.append({'time':t,'cloth_point_distance_to_cap':distance})
    assert counts==sorted(counts) and counts[-1]==4
    assert wetness==sorted(wetness) and wetness[-1]==1.
    assert wet_frames>20 and cloth_frames>=8
    required={'goutte_agacement','reflexe_tube_vide','declic_tablier','essuie_tablier',
              'realise_gaspillage','gene_public','gene_tenue'}
    assert required==set(phase_samples),phase_samples.keys()
    return {'frames':frames,'external_v20_comparison':'passed' if previous else 'unavailable',
            'historical_action_frames_identical':compared,'preserved_fields':list(PRESERVED),
            'sink_svg_frames_identical':sink_count,'native_articulation_functions':list(ARM_FUNCTIONS),
            'body_contour_and_approved_costume_preserved':True,'all_cameras_inside_decor':True,
            'last_paper_fully_visible_during_flight_insert_and_final_wide_frames':visible_paper,
            'four_papers_in_bin_and_fifth_persistent_on_floor':True,
            'drop_attached_frames':wet_frames,'drop_to_native_cap_ink_max_gap_world_units':max(anchor_gaps),
            'apron_contact_frames':cloth_frames,'apron_contacts':contact_records,
            'wet_patch_after_contact_monotonic':True,'phase_samples':phase_samples,
            'limits':'The state/geometry checks do not establish whether viewers understand an emotion.'}


def audio_checks():
    audio=EP/'audio';sound=module('acting_sound_v21',EP/'sources/son.py')
    reference=pcm(audio/'mix_reference_v19.wav')
    assert sha(audio/'mix_reference_v19.wav')==BASE19_SHA
    # Reconstruct V20 independently from the frozen base and original cue;
    # neither use the new mix report nor its baseline helper as evidence.
    mono,_=sound.make_sound('tiny_paper_floor',.12,3041672)
    cue=sound.stereo(mono,-37.5,-.35)
    a=round(39.85*48000);b=a+len(cue)
    baseline=reference.astype(np.int32)
    baseline[a:b]+=np.rint(cue*sound.MASTER_GAIN_EXACT*sound.envelope(len(reference),.008,.035)[a:b,None]*32767.).astype(np.int32)
    assert wave_sha(baseline)==BASE20_SHA
    current=pcm(audio/'mix.wav');assert current.shape==(2136000,2)
    assert np.array_equal(current[:1944000],baseline[:1944000]),'PCM before40.5s changed'
    provenance=json.loads((audio/'provenance_reference_v19.json').read_text())
    params=provenance['background_music']['parameters']
    retained={e['file']:e['sha256'] for e in provenance['events']}
    retained.update({e['file']:e['sha256'] for e in params['stems']})
    retained[params['unattenuated_reference']['file']]=params['unattenuated_reference']['sha256']
    for name,expected in retained.items():assert sha(audio/name)==expected,(name,'Retained sound changed')
    floor_pcm=np.rint(cue*32767.).astype('<i2')
    assert np.array_equal(pcm(audio/'c5_papier_sol.wav'),floor_pcm),'Original floor cue bank changed'
    retained['c5_papier_sol.wav']=sha(audio/'c5_papier_sol.wav')
    provenance21=json.loads((audio/'provenance.json').read_text())
    cloth=next(e for e in provenance21['events'] if e['name']=='tablier_essuie')
    renderer=module('cloth_contact_reference_v21',EP/'sources/render.py')
    contact=renderer.animation.scene_state(42.0833333333333)['contact_apron']
    assert cloth['start']==contact['contact_time'] and abs(cloth['duration']-(contact['stroke_end']-contact['contact_time']))<1.e-8,'Cloth sound does not follow real contact'
    assert len(pcm(audio/'tablier_essuie.wav'))==round(cloth['duration']*48000)
    extension=pcm(audio/'musique_extension_v21.wav').astype(np.float64)/32768.
    assert extension.shape==(192000,2)
    rms_windows={}
    for seconds in (.1,.2):
        n=round(seconds*48000);hop=round(.02*48000)
        values=[]
        for start in range(0,len(extension)-n-round(.25*48000)+1,hop):
            rms=float(np.sqrt(np.mean(extension[start:start+n]**2)))
            values.append(20.*math.log10(max(rms,1.e-15)))
        assert min(values)>-50.,(seconds,min(values),'Musical gap in continuation')
        rms_windows[str(seconds)]={'minimum_pre_master_dbfs':min(values),'maximum_pre_master_dbfs':max(values),'step_seconds':.02}
    normalized=current.astype(np.float64)/32768.
    assert int(np.abs(current.astype(np.int32)).max())<32767
    differences=np.max(np.abs(np.diff(current.astype(np.int32),axis=0)),axis=1)
    neighborhood=differences[round(40.2*48000):round(41.*48000)]
    threshold=max(20.,2.*float(np.quantile(neighborhood,.999)))
    seams={str(t):int(differences[round(t*48000)-1]) for t in (40.5,40.75)}
    assert max(seams.values())<threshold,('Abrupt waveform jump at crossfade boundary',seams,threshold)
    return {'duration_seconds':44.5,'current_mix_sha256':sha(audio/'mix.wav'),
            'v20_reconstructed_wav_sha256':wave_sha(baseline),'pcm_identical_before_seconds':40.5,
            'retained_wav_count':len(retained),'retained_wavs_sha256':retained,
            'cloth_sound_follows_visible_contact_seconds':[cloth['start'],cloth['start']+cloth['duration']],
            'music_continuation_rolling_windows':rms_windows,'crossfade_boundary_jump_lsb':seams,
            'crossfade_jump_threshold_lsb':threshold,'no_clipping':True,
            'peak_dbfs':20.*math.log10(float(np.abs(normalized).max())),
            'limits':'Numerical waveform and file checks only; no listening or phone playback claimed.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final',action='store_true',help='Record final MP4 identities; primary verify.py handles codec/decode.')
    args=parser.parse_args()
    report={'status':'running','scope':'V21 geometry/continuity/audio preservation',
            'limits':'No numerical check is treated as an audience test or proof of expressive acting.'}
    destination=EP/'controle/audit_revision_v21.json'
    # Freeze the dependencies actually read by this QA. Packaging scripts and
    # the primary MP4 verifier can be prepared independently by the coordinator.
    paths=[EP/'sources'/name for name in ('animation.py','art.py','render.py',
           'sink.py','mitten.py','costume.py','son.py','music.py')]
    paths+=[EP/'chronologie.json',ROOT/'mou_rig.py',EP/'audio/mix.wav',
            EP/'assets/Nunito-wght.ttf',EP/'assets/TimGM6mb.sf2']
    frozen={str(p):sha(p) for p in paths}
    try:
        renderer=module('acting_current_v21',EP/'sources/render.py')
        assert sha(ROOT/'mou_rig.py')==RIG_SHA
        report['rig_sha256']=RIG_SHA
        report['scene']=scene_checks(renderer)
        report['audio']=audio_checks()
        report['final_mp4s']='not requested'
        if args.final:
            report['final_mp4s']={name:sha(EP/name) for name in
                ('MOU_Encore_une_feuille.mp4','MOU_Encore_une_feuille_muette.mp4')}
        assert frozen=={str(p):sha(p) for p in paths},'A production input changed during QA'
        report['production_inputs_unchanged']=frozen;report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        raise
    destination.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'historical_frames':report['scene']['historical_action_frames_identical'],
                      'sink_frames':report['scene']['sink_svg_frames_identical'],
                      'drop_frames':report['scene']['drop_attached_frames'],
                      'apron_contact_frames':report['scene']['apron_contact_frames'],
                      'report':str(destination)},indent=2))


if __name__=='__main__':
    main()
