"""Bundle the revised episode sources without caches or decoded video frames."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP = Path(__file__).resolve().parents[1]


def main():
    required = [
        'mou_rig.py', 'requirements.txt', 'AGENTS.md', 'BRIEF_MOU_CODEX.txt',
        'references/MOU_reference.png',
        'episodes/03/test_remuer/sources/animation.py',
        'episodes/03/test_remuer/controle/audit_structure.json',
        'episodes/03/film/sources/animation.py',
        'episodes/03/chronologie.json',
    ]
    files = {ROOT/name for name in required}
    files.update(EP/name for name in ['chronologie.json', 'README.md', 'CONTROLE.txt'])
    for directory in [ROOT/'fonts', EP.parent/'decor', EP.parent/'developpement',
                      EP/'sources', EP/'audio', EP/'etudes', EP/'developpement']:
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(p for p in (EP/'controle').rglob('*')
                 if p.is_file() and p.suffix in ('.json', '.md', '.txt', '.png', '.py'))
    files = sorted(files)
    assert all(p.is_file() for p in files)
    checks = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in files}
    destination = EP/'MOU_Encore_une_feuille_sources.zip'
    temporary = destination.with_name('.'+destination.name)
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr('MANIFESTE_SHA256.json', json.dumps(checks, ensure_ascii=False, indent=2)+'\n')
        archive.writestr('LIRE_MOI.txt',
                        'MOU — cuisine, carotte et réflexe, version 5.\n'
                        'Voir episodes/03/carotte_v5/sources/README.md pour reproduire.\n'
                        'Les dessins et les sons originaux sont inclus. Aucun service payant.\n')
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest()==sha
                   for name,sha in checks.items())
    os.replace(temporary, destination)
    print(json.dumps({'archive':str(destination), 'files':len(files),
                      'bytes':destination.stat().st_size,
                      'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
