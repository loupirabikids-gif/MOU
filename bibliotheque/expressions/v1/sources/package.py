"""Package the reusable expressions, gallery and their actual dependencies."""
from pathlib import Path
import hashlib
import json
import zipfile

LIB=Path(__file__).resolve().parents[1]
ROOT=next(p for p in LIB.parents if (p/'mou_rig.py').is_file())


def main():
    target=LIB/'MOU_bibliotheque_expressions_v1.zip'
    files={p for p in LIB.rglob('*') if p.is_file() and p!=target and p.name!='audit_archive.json' and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.zip')}
    files.update(ROOT/name for name in ('mou_rig.py','requirements.txt','AGENTS.md','references/MOU_reference.png',
        'episodes/03/film/sources/animation.py','episodes/03/test_remuer/sources/animation.py','episodes/03/chronologie.json'))
    files.update(p for p in (ROOT/'fonts').rglob('*') if p.is_file())
    assert all(p.is_file() for p in files)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
        for p in sorted(files):out.write(p,p.relative_to(ROOT))
        out.writestr('MANIFESTE_SHA256.json',json.dumps(hashes,ensure_ascii=False,indent=2)+'\n')
        out.writestr('OUVRIR_LA_BIBLIOTHEQUE.txt',
            'Décompresser entièrement cette archive.\n'
            'Ouvrir bibliotheque/expressions/v1/galerie.html dans un navigateur.\n'
            'La galerie fonctionne hors connexion ; les SVG et PNG sont dans exports/.\n'
            'Le README décrit les 36 poses, leurs contextes et les limites de cette étude.\n')
    with zipfile.ZipFile(target) as source:
        assert source.testzip() is None
        assert all(hashlib.sha256(source.read(p)).hexdigest()==h for p,h in hashes.items())
    print(json.dumps({'archive':str(target),'bytes':target.stat().st_size,'files':len(files),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
