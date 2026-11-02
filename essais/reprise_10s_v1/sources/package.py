"""Package this self-contained SVG study and its production notes."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]


def main():
    files=set()
    for name in ('sources','poses','developpement','controle'):
        files.update(p for p in (EP/name).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='archive.json')
    files.update(p for p in EP.iterdir() if p.is_file() and p.suffix in ('.md','.json','.png'))
    files.update(ROOT/name for name in ('requirements.txt','fonts/DejaVuSans-Bold.ttf','fonts/LICENCE_DejaVu.txt',
                                        'equipe/PIPELINE_HEBDOMADAIRE.md'))
    data={str(p.relative_to(ROOT)):p.read_bytes() for p in sorted(files)}
    sha=lambda value:hashlib.sha256(value).hexdigest()
    checks={name:sha(value) for name,value in data.items()}
    output=EP/'MOU_Poids_plume_sources.zip';temp=output.with_name('.'+output.name)
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,value in data.items():z.writestr(name,value)
        z.writestr('MANIFESTE_SHA256.json',json.dumps(checks,indent=2)+'\n')
        z.writestr('LIRE_MOI.txt','MOU — Poids plume, essai muet 10 s.\nVoir essais/reprise_10s_v1/README.md.\n')
    with zipfile.ZipFile(temp) as z:
        assert z.testzip() is None
        assert all(sha(z.read(name))==digest for name,digest in checks.items())
    os.replace(temp,output)
    report={'file':output.name,'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,
            'payload_files':len(data),'crc_ok':True,'all_payload_sha256_match':True}
    (EP/'controle/archive.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
