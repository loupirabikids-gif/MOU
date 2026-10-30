"""Six short silent face studies: attention, expression, then exposure."""
from pathlib import Path
import concurrent.futures
import hashlib
import html
import importlib.util
import json
import math
import subprocess
import sys

LIB=Path(__file__).resolve().parents[1]
ROOT=next(p for p in LIB.parents if (p/'mou_rig.py').is_file())
sys.path.insert(0,str(LIB/'sources'))
import render
FPS=24;PER_SCENE=72
SCENES=[
    ('plaisir','Le plaisir de cuisiner','neutre','joie_franc',(70.,285.)),
    ('inspection','Quelque chose sur la main','joie_franc','doute_franc',(360.,330.)),
    ('agacement','Encore un lavage','doute_franc','contrariete_franc',(80.,160.)),
    ('decouverte','Un tout petit morceau','fierte_franc','surprise_franc',(360.,330.)),
    ('soulagement','La main est propre','peur_franc','soulagement_franc',(360.,330.)),
    ('gene','Le gaspillage est visible','neutre','gene_franc',(70.,330.)),
]
CAT=render.catalogue();POSES={p['id']:p['params'] for p in CAT['poses']}
POSES['neutre']=CAT['neutral']['params']


def ease(value):
    x=max(0.,min(1.,value));return x*x*(3.-2.*x)


def state_at(index):
    scene=min(len(SCENES)-1,index//PER_SCENE);local=index%PER_SCENE
    sid,label,first,last,target=SCENES[scene]
    a,b=dict(POSES[first]),dict(POSES[last])
    dx,dy=target[0]-203.,target[1]-235.;n=max(1.,math.hypot(dx,dy))
    gaze={'pupil_x':dx/n*.88,'pupil_y':dy/n*.88}
    if local<10:
        p=a;phase='Avant'
    elif local<18:
        p=dict(a);u=ease((local-10)/7.)
        for key,value in gaze.items():p[key]=a.get(key,0.)+(value-a.get(key,0.))*u
        phase='Le regard se dirige'
    else:
        a.update(gaze);b.update(gaze)
        p=render.face.blend_face_params(a,b,ease((local-18)/13.))
        phase='La réaction se forme' if local<32 else 'La pose reste lisible'
    # A single short blink during an established hold. No face crossfade.
    if 44<=local<48:
        factor={44:.45,45:.04,46:.04,47:.45}[local]
        for side in ('l','r'):p['eye_open_'+side]=p.get('eye_open_'+side,1.)*factor
    return {'scene':sid,'label':label,'local_frame':local,'params':p,'target':target,'phase':phase}


def svg_at(index):
    s=state_at(index);x,y=s['target'];label=html.escape(s['label']);phase=html.escape(s['phase'])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="960" viewBox="0 0 400 533.333333">'
            f'<rect width="400" height="534" fill="{render.BG}"/>'
            f'<text x="200" y="36" font-family="DejaVu Sans" font-size="16" text-anchor="middle" fill="{render.INK}">{label}</text>'
            f'<text x="200" y="60" font-family="DejaVu Sans" font-size="10" text-anchor="middle" fill="#73516B">Étude du visage · le point indique la cible du regard</text>'
            f'<circle cx="{x}" cy="{y}" r="11" fill="#E6D7EE" stroke="#9C7B9C" stroke-width="1.5"/>'
            +render.actor(s['params'],'demo')
            +f'<text x="200" y="497" font-family="DejaVu Sans" font-size="13" text-anchor="middle" fill="{render.INK}">{phase}</text>'
            +'</svg>')


def frame_job(index):
    import cairosvg
    frames=ROOT/'work/expressions_v1_frames';frames.mkdir(parents=True,exist_ok=True)
    data=svg_at(index).encode();key=hashlib.sha256(data).hexdigest()
    target=frames/f'{index:04d}.png';stamp=target.with_suffix('.sha256')
    if not stamp.exists() or stamp.read_text()!=key or not target.exists():
        cairosvg.svg2png(bytestring=data,write_to=str(target));stamp.write_text(key)
    return index


def main():
    paths=[LIB/'catalogue.json',LIB/'sources/face.py',LIB/'sources/render.py',LIB/'sources/animer.py',ROOT/'mou_rig.py',ROOT/'episodes/03/film/sources/animation.py']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    frozen={str(p.relative_to(ROOT)):sha(p) for p in paths}
    n=len(SCENES)*PER_SCENE
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
        for count,_ in enumerate(pool.map(frame_job,range(n)),1):
            if count%72==0:print(f'visages: {count}/{n}',flush=True)
    assert frozen=={p:sha(ROOT/p) for p in frozen},'Sources changed during face-study render'
    output=LIB/'MOU_transitions_visage.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(ROOT/'work/expressions_v1_frames/%04d.png'),
                    '-frames:v',str(n),'-c:v','libx264','-threads','3','-preset','medium','-crf','15','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(output)],check=True)
    # Individual clips can be used without playing the complete review reel.
    for i,scene in enumerate(SCENES):
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(i*3),'-i',str(output),'-t','3',
                        '-c:v','libx264','-threads','2','-crf','15','-pix_fmt','yuv420p','-an',
                        str(LIB/'exports'/f'transition_{scene[0]}.mp4')],check=True)
    (LIB/'controle/sources_transitions.json').write_text(json.dumps({'frozen_sources_sha256':frozen,'fps':FPS,'frames':n,'duration':n/FPS,
        'scenes':[{'id':s[0],'label':s[1],'start_seconds':i*3,'duration_seconds':3,'from':s[2],'to':s[3],'target':s[4]} for i,s in enumerate(SCENES)],
        'limits':'Facial studies with fixed native body/arms. No audio, episode edit or audience validation.'},ensure_ascii=False,indent=2)+'\n')
    # Export real decoded sequence samples for independent review.
    indices=[i*72+j for i in range(len(SCENES)) for j in (5,16,27,38,59,69)]
    command='select='+'+'.join(f'eq(n\\,{j})' for j in indices)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(output),'-vf',command,'-fps_mode','passthrough',str(LIB/'controle/transition_%02d.png')],check=True)
    print(json.dumps({'video':str(output),'frames':n,'duration':n/FPS,'scenes':6}))


if __name__=='__main__':main()
