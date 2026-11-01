"""Package reproducible V30 inputs and evidence, without raster caches."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import zipfile

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p / 'mou_rig.py').is_file())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    required = [
        'mou_rig.py', 'requirements.txt', 'AGENTS.md', 'BRIEF_MOU_CODEX.txt',
        'references/MOU_reference.png',
        'episodes/03/test_remuer/sources/animation.py',
        'episodes/03/test_remuer/controle/audit_structure.json',
        'episodes/03/film/sources/animation.py', 'episodes/03/chronologie.json',
    ]
    files = {ROOT / name for name in required}
    files.update(EP / name for name in ('chronologie.json', 'chronologie_reference_v25.json',
                                      'README.md', 'CONTROLE.md'))
    for directory in (ROOT / 'fonts', EP.parent / 'decor', EP / 'sources',
                      EP / 'assets', EP / 'audio/inputs', EP / 'developpement'):
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(p for p in (EP / 'audio').glob('*.json'))
    files.update(p for p in (EP / 'controle').rglob('*') if p.is_file()
                 and p.name != 'audit_archive.json'
                 and p.suffix in ('.py', '.json', '.md', '.txt', '.png', '.jpg'))
    files = sorted(files)
    assert all(p.is_file() for p in files)
    checks = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    destination = EP / 'MOU_Encore_une_feuille_sources.zip'
    temporary = destination.with_name('.' + destination.name)
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr('MANIFESTE_SHA256.json', json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
        archive.writestr('LIRE_MOI.txt',
            'MOU original V30 — jeu accentué, jazz abaissé, sans cuisson.\n'
            'Voir episodes/03/cuisine_v30/sources/README.md pour reproduire.\n'
            'Inputs sonores, dessin et ressources inclus ; aucun service payant.\n'
            'La protection des anciens films se vérifie dans le dépôt complet.\n')
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(name)).hexdigest() == sha for name, sha in checks.items())
    os.replace(temporary, destination)
    report = {'archive': destination.name, 'sha256': digest(destination),
              'bytes': destination.stat().st_size, 'payload_files': len(files),
              'crc_ok': True, 'all_payload_sha256_match': True,
              'limits': 'Archive integrity; cold reproduction is a separate control.'}
    (EP / 'controle/audit_archive.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
