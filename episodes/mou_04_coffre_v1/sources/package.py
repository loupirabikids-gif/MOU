"""Archive the reproducible PATCH episode, audio origins and review notes."""
from pathlib import Path
import hashlib
import json
import os
import zipfile

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]


def main():
    files=set()
    for name in ('sources','poses','developpement','controle','assets','audio'):
        files.update(p for p in (EP/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts
                     and p.suffix!='.pyc' and p.name!='archive.json')
    files.update(p for p in EP.iterdir() if p.is_file() and p.suffix in ('.md','.json','.png'))
    files.update(ROOT/n for n in ('requirements.txt','fonts/DejaVuSans-Bold.ttf','fonts/LICENCE_DejaVu.txt'))
    payload={str(p.relative_to(ROOT)):p.read_bytes()for p in sorted(files)}
    sha=lambda v:hashlib.sha256(v).hexdigest()
    checks={name:sha(data)for name,data in payload.items()}
    output=EP/'MOU_Le_coffre_sources.zip';temp=output.with_name('.'+output.name)
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for name,data in payload.items():z.writestr(name,data)
        z.writestr('MANIFESTE_SHA256.json',json.dumps(checks,indent=2)+'\n')
        z.writestr('LIRE_MOI.txt','MOU — Le coffre à concentration.\nVoir episodes/mou_04_coffre_v1/README.md.\n')
    with zipfile.ZipFile(temp)as z:
        assert z.testzip() is None
        assert all(sha(z.read(n))==h for n,h in checks.items())
    os.replace(temp,output)
    r={'file':output.name,'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,
       'payload_files':len(payload),'crc_ok':True,'all_payload_sha256_match':True}
    (EP/'controle/archive.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))


if __name__=='__main__':main()
