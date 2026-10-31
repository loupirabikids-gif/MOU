"""Make a small self-contained source snapshot for the pebble prototype."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent;EP=HERE.parent
ROOT=next(p for p in EP.parents if (p/'fonts/DejaVuSans-Bold.ttf').is_file())


def main():
    files=[ROOT/'requirements.txt',ROOT/'fonts/DejaVuSans-Bold.ttf',ROOT/'fonts/LICENCE_DejaVu.txt']
    for name in ('REFERENCE.md','README.md','CONTROLE.md'):
        files.append(EP/name)
    for folder in ('sources','poses','developpement','controle'):
        files.extend(p for p in (EP/folder).rglob('*')if p.is_file()
                     and p.suffix in ('.py','.json','.svg','.md')and'__pycache__'not in p.parts
                     and p.name!='audit_archive.json')
    files=sorted(set(files));manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
    target=EP/'Galet_sources.zip';temp=target.with_name('.'+target.name)
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in files:z.write(p,p.relative_to(ROOT).as_posix())
        z.writestr('MANIFESTE_SHA256.json',json.dumps(manifest,indent=2)+'\n')
        z.writestr('LIRE_MOI.txt','Galet, prototype original de cinq secondes.\nVoir personnages/galet_v1/README.md.\nPython, SVG, CairoSVG, Pillow et FFmpeg ; aucune API ni ancien rig MOU requis.\n')
    with zipfile.ZipFile(temp)as z:
        assert z.testzip()is None
        assert all(hashlib.sha256(z.read(k)).hexdigest()==v for k,v in manifest.items())
    temp.replace(target)
    print(json.dumps({'archive':str(target),'files':len(manifest),'bytes':target.stat().st_size,
                      'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
