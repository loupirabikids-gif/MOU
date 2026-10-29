"""Replace only music/audio, copying the verified V14 picture stream.

This shortcut needs V14 in the full checkout. Standalone archives can instead
run son.py then render.py to recreate the complete episode from its sources.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]
BASE = EP.parent/'cuisine_v14'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    baseline=json.loads((BASE/'controle/audit_final.json').read_text())
    assert baseline['status']=='passed'
    for name in ('animation.py','art.py','render.py','sink.py','mitten.py'):
        assert digest(EP/'sources'/name)==digest(BASE/'sources'/name),name
    assert (EP/'chronologie.json').read_bytes()==(BASE/'chronologie.json').read_bytes()
    assert digest(BASE/'MOU_Encore_une_feuille_muette.mp4')==baseline['silent_video']['file_sha256']
    dependencies=[EP/'sources'/name for name in ('animation.py','art.py','render.py','sink.py','mitten.py','son.py','music.py')]
    dependencies += [EP/'chronologie.json',ROOT/'fonts/DejaVuSans-Bold.ttf',EP/'assets/TimGM6mb.sf2']
    frozen={str(p):digest(p) for p in dependencies}
    for tag,suffix in [('final',''),('animatique','_animatique')]:
        silent=f'MOU_Encore_une_feuille{suffix}_muette.mp4'
        shutil.copy2(BASE/silent,EP/silent)
        destination=EP/f'MOU_Encore_une_feuille{suffix}.mp4'
        temporary=destination.with_name('.'+destination.name)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i',str(EP/silent),'-i',str(EP/'audio/mix.wav'),
            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
            '-t','41','-movflags','+faststart',str(temporary)],check=True)
        os.replace(temporary,destination)
        manifest={'sha256':frozen,'output':str(destination),
                  'method':'New music mix muxed with the unchanged verified V14 H264 stream.'}
        (EP/'controle'/f'sources_{tag}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    comparison=EP/'comparaison';comparison.mkdir(exist_ok=True)
    for label,episode in [('avant',BASE),('apres',EP)]:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i',str(BASE/'MOU_Encore_une_feuille_animatique_muette.mp4'),
            '-i',str(episode/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0',
            '-t','10.5','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',
            str(comparison/f'MOU_musique_{label}.mp4')],check=True)
    assert frozen=={str(p):digest(p) for p in dependencies},'source modified during mux'
    print(json.dumps({'final':str(EP/'MOU_Encore_une_feuille.mp4'),'unchanged_silent_sha256':digest(EP/'MOU_Encore_une_feuille_muette.mp4')}))


if __name__=='__main__':
    main()
