"""Archive this editable prototype and the original vector producers it uses."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    files = set()
    for name in ('sources','assets','developpement','controle','licences','poses'):
        files.update(p for p in (EP/name).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc'
                     and p.name != 'archive.json')
    files.update(p for p in EP.iterdir() if p.is_file() and p.suffix in ('.md','.blend','.png'))
    reference = ROOT/'episodes/03/etude_grain_v1'
    for directory in (reference/'sources',reference/'assets', ROOT/'episodes/03/decor',ROOT/'fonts'):
        files.update(p for p in directory.rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files.update(reference.glob('*.json'))
    files.update(ROOT/name for name in ('mou_rig.py','requirements.txt',
                     'episodes/03/test_remuer/sources/animation.py',
                     'episodes/03/test_remuer/controle/audit_structure.json'))
    payload = {str(p.relative_to(ROOT)):p.read_bytes() for p in sorted(files)}
    output = EP/'MOU_Blender_sources.zip'
    temporary = output.with_name('.'+output.name)
    checks = {name:sha(data) for name,data in payload.items()}
    with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in payload.items():
            z.writestr(name,data)
        z.writestr('MANIFESTE_SHA256.json',json.dumps(checks,indent=2)+'\n')
        z.writestr('LIRE_MOI.txt','Prototype MOU original, Blender 2D éditable.\n'
                   'Voir personnages/MOU_blender_v1/README.md.\n')
    with zipfile.ZipFile(temporary) as z:
        assert z.testzip() is None
        assert all(sha(z.read(name)) == digest for name,digest in checks.items())
    os.replace(temporary,output)
    report = {'file':output.name,'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,
              'payload_files':len(payload),'crc_ok':True,'all_payload_sha256_match':True}
    (EP/'controle/archive.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
