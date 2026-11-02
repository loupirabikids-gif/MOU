"""Archive the silent study's actual producers, assets and proof files."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())


def main():
    files = {ROOT/p for p in ('mou_rig.py', 'requirements.txt', 'AGENTS.md',
              'episodes/03/test_remuer/sources/animation.py',
              'episodes/03/test_remuer/controle/audit_structure.json')}
    for directory in (EP/'sources', EP/'assets', EP/'developpement', ROOT/'fonts', EP.parent/'decor'):
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(p for p in EP.glob('*') if p.suffix in ('.json', '.md', '.png', '.svg'))
    files.update(p for p in (EP/'controle').rglob('*') if p.is_file()
                 and p.name != 'archive.json' and p.suffix in ('.json', '.md'))
    files = sorted(files)
    checks = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    output = EP/'MOU_Le_grain_sources.zip'
    temporary = output.with_name('.'+output.name)
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in files:
            z.write(path, path.relative_to(ROOT))
        z.writestr('MANIFESTE_SHA256.json', json.dumps(checks, indent=2)+'\n')
        z.writestr('LIRE_MOI.txt', 'MOU original — Le grain, essai muet de cinq secondes.\nVoir episodes/03/etude_grain_v1/README.md.\n')
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(p)).hexdigest() == sha for p, sha in checks.items())
    os.replace(temporary, output)
    report = {'file': output.name, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
              'bytes': output.stat().st_size, 'payload_files': len(files),
              'crc_ok': True, 'all_payload_sha256_match': True}
    (EP/'controle/archive.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
