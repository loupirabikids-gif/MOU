"""Bundle the new episode with local art, sound inputs and editable sources."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'fonts/DejaVuSans-Bold.ttf').is_file())


def main():
    files={ROOT/'requirements.txt',ROOT/'fonts/DejaVuSans-Bold.ttf',ROOT/'fonts/LICENCE_DejaVu.txt',
           EP.parent/'decor/MOU_cuisine_decor.svg'}
    files.update(EP/n for n in ('chronologie.json','REFERENCE.md','README.md','CONTROLE.md'))
    for name in ('sources','assets','developpement'):
        files.update(p for p in (EP/name).rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc')
    files.update(p for p in (EP/'controle').glob('*')if p.is_file()and p.name!='audit_archive.json'
                 and p.suffix in ('.py','.md','.json'))
    files.update(p for p in (EP/'audio/inputs').rglob('*')if p.is_file())
    files.update(p for p in (EP/'audio').glob('*.json')if p.is_file())
    files.update(p for p in (EP/'audio').glob('*.mid')if p.is_file())
    files=sorted(files)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
    output=EP/'Galet_Cuisine_sources.zip';tmp=output.with_name('.'+output.name)
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as archive:
        for p in files:archive.write(p,str(p.relative_to(ROOT)))
        archive.writestr('MANIFESTE_SHA256.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        archive.writestr('LIRE_MOI.txt','Galet en cuisine — Just cooking. Mostly washing.\n38 secondes,1080x1920,24fps.\nVoir episodes/03/galet_cuisine_v1/README.md.\nImages, musique et bruitages se reconstruisent localement, sans ancien rig MOU ni API.\n')
    with zipfile.ZipFile(tmp)as archive:
        assert archive.testzip()is None
        assert all(hashlib.sha256(archive.read(k)).hexdigest()==v for k,v in manifest.items())
    tmp.replace(output)
    print(json.dumps({'archive':str(output),'files':len(manifest),'bytes':output.stat().st_size,
                      'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
