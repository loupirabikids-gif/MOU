"""Build the portable twelve-sound proposal gallery and its labelled audition."""
from __future__ import annotations
import argparse
import hashlib
import html
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import wave
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import sound_bank
SR=sound_bank.SR
SLOT=1.5
LEAD=.30
FONT=HERE/'fonts/DejaVuSans-Bold.ttf'
ZIP_NAME='MOU_Bibliotheque_Sons_v1.zip'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_wav(path,signal):
    values=np.rint(np.asarray(signal)*32768.).astype(np.int32)
    assert np.abs(values).max()<32767
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(values.astype('<i2').tobytes())


def save_json(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def build_sounds():
    (HERE/'audio').mkdir(exist_ok=True)
    master=np.zeros((round(12*SLOT*SR),2),dtype=np.float64)
    entries=[]
    for i,spec in enumerate(sound_bank.SPECS):
        signal,metadata=sound_bank.render(spec['id'])
        repeated,again=sound_bank.render(spec['id'])
        assert np.array_equal(signal,repeated) and metadata==again
        path=HERE/'audio'/f"{spec['id']}.wav";write_wav(path,signal)
        metadata.update(file=path.relative_to(HERE).as_posix(),sha256=sha(path),
            attack_energy_point_sample=metadata['anchor_sample'],
            audition_slot_s=[i*SLOT,(i+1)*SLOT],audition_sound_start_s=i*SLOT+LEAD,
            audition_energy_anchor_s=i*SLOT+LEAD+metadata['anchor_seconds'])
        a=round((i*SLOT+LEAD)*SR);master[a:a+len(signal)]+=signal
        entries.append(metadata)
    assert len({e['sha256'] for e in entries})==12
    write_wav(HERE/'audition_complete.wav',master)
    catalogue={'name':'MOU — bibliothèque de sons v1','status':'proposition_non_validee',
        'purpose':'Choisir une identité sonore par écoute avant de réutiliser les sons dans les épisodes.',
        'sample_rate':SR,'channels':2,'families':6,'variants_per_family':2,'sounds':entries,
        'audition':{'file':'audition_complete.wav','duration_s':18.,'slot_duration_s':SLOT,'lead_in_s':LEAD,
                    'music':False,'sha256':sha(HERE/'audition_complete.wav')},
        'alignment':{'formula':'cue_start_s = visible_event_s - anchor_sample / sample_rate',
            'definition':'Première séquence de 2 ms au-dessus de 25 % du maximum RMS 4 ms. Repère numérique, pas seuil perceptif validé.',
            'check':'Regarder puis écouter le geste avec le son retenu ; ajuster selon le contexte.'},
        'source_provenance':'sources/provenance.json',
        'limits':'Aucune écoute par le modèle. Intention, caractère non verbal, naturel et confort restent à valider par l’utilisatrice ; auteur et méthode des assets initiaux non vérifiés.'}
    save_json(HERE/'CATALOGUE.json',catalogue)
    return catalogue


def build_html(catalogue):
    groups=[]
    for family,label,mouth,when,avoid in sound_bank.FAMILIES:
        cards=[]
        for e in catalogue['sounds']:
            if e['family']!=family:continue
            cards.append(f'''<article><h3>{html.escape(e['variant'].capitalize())}</h3>
            <p>{e['duration_seconds']:.2f} s · repère à {e['anchor_seconds']*1000:.0f} ms</p>
            <audio controls preload="none" src="{e['file']}"></audio>
            <a download href="{e['file']}">Télécharger le WAV</a>
            <p class="small">{html.escape(e['id'])} · proposition non validée</p></article>''')
        groups.append(f'<section><h2>{html.escape(label)}</h2><p>{html.escape(when)}</p><div class="pair">'+''.join(cards)+'</div></section>')
    embedded=json.dumps(catalogue,ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>MOU — essais de sons</title><style>
    body{margin:0;background:#fff8ed;color:#382035;font:17px/1.5 system-ui,sans-serif}main{max-width:980px;margin:auto;padding:28px}
    h1{font-size:2.1rem;line-height:1.15}h2{border-left:7px solid #d8f449;padding-left:14px}.badge{display:inline-block;background:#e7ecd0;padding:6px 12px;border-radius:20px}
    .pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}article{background:#fffdf7;border:2px solid #dacbd5;border-radius:16px;padding:18px}
    audio{width:100%;max-width:460px}a{color:#67436c}.small{font-size:.85rem;color:#745b7c}.notice{max-width:72ch}section{margin-top:34px}
    @media(max-width:620px){.pair{grid-template-columns:1fr}main{padding:20px}}</style><main>
    <span class="badge">12 propositions à écouter</span><h1>MOU — essais de sons</h1>
    <p class="notice">Six intentions, deux variantes chacune. Le nom décrit l'intention recherchée ; il ne garantit pas qu'elle soit reconnue à l'écoute.</p>
    <h2>Comparaison complète — 18 secondes</h2><audio controls preload="none" src="audition_complete.wav"></audio>
    <p>Sans musique. Chaque créneau dure 1,5 s ; le son arrive après 0,3 s. <a href="MOU_Bibliotheque_Sons_v1.mp4">Voir les cartes vidéo</a></p>
    '''+''.join(groups)+'''
    <section><h2>Utiliser le bon repère</h2><p>Placer l'ancre d'énergie sur le geste voulu : départ du son = temps du geste − repère indiqué. Écouter ensuite le résultat avec l'image.</p>
    <p class="small">Sources CC0 créditées dans sources/provenance.json. Auteur initial et méthode de création non vérifiés. Aucune écoute ou validation émotionnelle par le modèle.</p></section>
    <script type="application/json" id="catalogue">'''+embedded+'''</script></main></html>'''
    (HERE/'index.html').write_text(page)


def wrap(text,font,width):
    lines=[];line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if font.getlength(trial)>width and line:lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines


def build_video(catalogue):
    width,height,fps=540,960,24
    fonts={size:ImageFont.truetype(str(FONT),size) for size in (17,20,23,28,35,48)}
    cards=[]
    for n,e in enumerate(catalogue['sounds']):
        im=Image.new('RGB',(width,height),'#FFF8ED');d=ImageDraw.Draw(im)
        d.rounded_rectangle((32,35,508,114),20,fill='#D8F449')
        d.text((52,52),'MOU — essais de voix',font=fonts[28],fill='#382035')
        d.text((38,148),'PROPOSITION À ÉCOUTER',font=fonts[20],fill='#745B7C')
        d.text((38,218),e['family_label'],font=fonts[48],fill='#382035')
        d.text((38,287),e['variant'].capitalize(),font=fonts[28],fill='#67436C')
        d.text((38,337),f"{n+1:02d} /12  •  {e['duration_seconds']:.2f} s",font=fonts[20],fill='#745B7C')
        y=407
        for line in wrap(e['preferred_when'],fonts[23],464):d.text((38,y),line,font=fonts[23],fill='#382035');y+=33
        signal,_=sound_bank.render(e['id']);mono=signal.mean(axis=1)
        bins=np.array_split(mono,216);envelope=np.array([max(abs(b)) for b in bins]);envelope/=max(float(envelope.max()),1e-9)
        d.line((38,640,502,640),fill='#D9CAD4',width=2)
        for j,value in enumerate(envelope):
            x=40+j*2.13;d.line((x,640-value*57,x,640+value*57),fill='#67436C',width=2)
        anchor_x=40+460*e['anchor_seconds']/e['duration_seconds'];d.line((anchor_x,568,anchor_x,712),fill='#839E24',width=3)
        d.text((38,737),f"Repère d'énergie : {e['anchor_seconds']*1000:.0f} ms",font=fonts[20],fill='#67436C')
        d.text((38,783),'Intention non encore validée',font=fonts[20],fill='#745B7C')
        d.text((38,883),'Sans musique • 2 variantes par intention',font=fonts[17],fill='#745B7C')
        cards.append(im)
    destination=HERE/'MOU_Bibliotheque_Sons_v1.mp4';temporary=HERE/'.audition.tmp.mp4'
    command=['ffmpeg','-y','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{width}x{height}',
        '-framerate',str(fps),'-i','pipe:0','-i',str(HERE/'audition_complete.wav'),'-frames:v','432',
        '-c:v','libx264','-threads','3','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
        '-t','18','-movflags','+faststart',str(temporary)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for frame in range(432):
            slot=frame//36;local=(frame%36)/36
            im=cards[slot].copy();d=ImageDraw.Draw(im)
            d.rounded_rectangle((38,837,502,852),7,fill='#E2D6DE')
            if local>0:d.rounded_rectangle((38,837,38+464*local,852),7,fill='#91AA32')
            process.stdin.write(im.tobytes())
        process.stdin.close();assert process.wait()==0
    except BaseException:
        process.kill();process.wait();raise
    os.replace(temporary,destination)
    cards[0].save(HERE/'apercu_catalogue.png')


def audit(catalogue):
    entries=[]
    for e in catalogue['sounds']:
        with wave.open(str(HERE/e['file']),'rb') as f:
            assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
            data=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2)
        assert len(data)==e['samples'] and not data[0].any() and not data[-1].any()
        assert np.abs(data.astype(np.int32)).max()<32767
        markers=sound_bank.energy_markers(data/32768.)
        assert markers['anchor_sample']==e['anchor_sample'] and 0<=e['anchor_sample']<len(data)
        entries.append({'id':e['id'],'sha256':sha(HERE/e['file']),'anchor_sample':e['anchor_sample'],'samples':len(data)})
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(HERE/'MOU_Bibliotheque_Sons_v1.mp4')]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert (video['width'],video['height'],int(video['nb_frames']))==(540,960,432)
    assert abs(float(probe['format']['duration'])-18)<.01
    report={'status':'passed','generated_sounds':12,'families':6,'source_count':3,'same_render_twice':True,
        'unique_wav_hashes':len({e['sha256'] for e in entries}), 'audition_duration_s':18.,'video_frames':432,
        'sample_rate':SR,'no_pcm_clipping':True,'energy_anchors_recomputed_from_written_pcm':True,
        'no_model_listening':True,'all_sounds_status':sound_bank.STATUS,'entries':entries,
        'limits':'Technical audit only; no approval of naturalness, emotion or wordlessness perceived.'}
    save_json(HERE/'CONTROLE.json',report)


def make_zip():
    paths=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'
           and p.name!=ZIP_NAME and not p.name.startswith('.')]
    checks={p.relative_to(HERE).as_posix():sha(p) for p in paths}
    temporary=HERE/'.sources.tmp.zip'
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths:z.write(p,p.relative_to(HERE).as_posix())
        z.writestr('MANIFESTE_SHA256.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(name)).hexdigest()==digest for name,digest in checks.items())
    os.replace(temporary,HERE/ZIP_NAME)
    print(json.dumps({'archive':str(HERE/ZIP_NAME),'files':len(paths),'bytes':(HERE/ZIP_NAME).stat().st_size,
        'sha256':sha(HERE/ZIP_NAME)}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--package-only',action='store_true');args=parser.parse_args()
    if not args.package_only:
        catalogue=build_sounds();build_html(catalogue);build_video(catalogue);audit(catalogue)
    make_zip()


if __name__=='__main__':main()
