"""Bundle reproducible episode sources, original rig, decor and original sounds."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'mou_rig.py').is_file())
EP=Path(__file__).resolve().parents[1]

def main():
    files={ROOT/p for p in ['mou_rig.py','requirements.txt','AGENTS.md',
        'BRIEF_MOU_CODEX.txt','references/MOU_reference.png',
        'episodes/03/chronologie.json','episodes/03/test_remuer/sources/animation.py',
        'episodes/03/test_remuer/controle/audit_structure.json']}
    for folder in [ROOT/'fonts',ROOT/'episodes/03/decor',ROOT/'episodes/03/developpement',
                   EP/'sources',EP/'audio',EP/'controle']:
        files.update(p for p in folder.rglob('*') if p.is_file()
                     and'__pycache__'not in p.parts and p.suffix not in('.pyc','.mp4'))
    files.update(p for p in [EP/'README.md',EP/'CONTROLE.txt'] if p.exists())
    files=sorted(p for p in files if p.is_file())
    checks={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    dest=EP/'MOU_Encore_une_feuille_sources.zip';tmp=dest.with_name('.'+dest.name)
    with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files:z.write(path,path.relative_to(ROOT).as_posix())
        z.writestr('MANIFESTE_SHA256.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
        z.writestr('LIRE_MOI.txt','Sources MOU — Encore une feuille.\nVoir episodes/03/film/sources/README.md pour les commandes de reproduction.\nLes WAV sont originaux et les dessins proviennent de ce projet.\n')
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(name)).hexdigest()==sha for name,sha in checks.items())
    os.replace(tmp,dest)
    print(json.dumps({'archive':str(dest),'files':len(files),'bytes':dest.stat().st_size,
                      'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()},ensure_ascii=False))

if __name__=='__main__':main()
