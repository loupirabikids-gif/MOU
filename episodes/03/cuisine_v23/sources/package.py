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
        'episodes/03/developpement/diagnostic_musique_v17.md',
    ]
    files = {ROOT/name for name in required}
    files.update(EP/name for name in ['chronologie.json', 'README.md', 'CONTROLE.txt'])
    for directory in [ROOT/'fonts', EP.parent/'decor', EP/'sources', EP/'audio', EP/'developpement', EP/'assets']:
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    # Current directing evidence stays with the snapshot, without packaging
    # unrelated earlier software probes or the complete expressions gallery.
    for directory in [ROOT/'recherche/2026-10-30_lamput']:
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(ROOT/'bibliotheque/expressions/v1'/n for n in
                 ('intentions_episode.md','critique.md'))
    compact_images = {'planche.png', 'planche_final.png', 'planche_animatique.png',
                      'caption_1s.png', 'caption_mobile.png', 'export_01.png', 'export_03.png',
                      'final_chef.png', 'final_lavabo.png', 'final_final.png',
                      'final_planche.png', 'animatique_planche.png', 'avant_planche.jpg',
                      'final_0210.png', 'final_0675.png', 'final_0970.png'}
    files.update(p for p in (EP/'controle').rglob('*')
                 if p.is_file() and p.name != 'audit_archive.json'
                 and (p.suffix in ('.json', '.md', '.txt', '.py')
                      or p.suffix in ('.png', '.jpg') and (p.name in compact_images
                          or 'planche' in p.stem or 'dense' in p.stem
                          or p.name.startswith('final_contact_'))))
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
                        'MOU — cuisine V23, expressions intégrées et nouveau trio jazz, 48,25 secondes.\n'
                        'Voir episodes/03/cuisine_v23/sources/README.md pour reproduire.\n'
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
