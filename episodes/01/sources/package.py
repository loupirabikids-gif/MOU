"""Archive reproductible des sources et inventaire des livrables courants."""
from pathlib import Path
import hashlib
import json
import os
import zipfile
ROOT=Path(__file__).resolve().parents[3]
EP=ROOT/'episodes/01'

def main():
    archive=EP/'MOU_01_sources.zip'
    collected=[]
    for directory,dirs,names in os.walk(ROOT):
        dirs[:]=[d for d in dirs if d not in {'.git','.venv','work','cache','frames','__pycache__'}]
        for name in names:
            p=Path(directory)/name
            if p==archive or p.suffix=='.pyc':continue
            if p.parent==EP and (p.suffix=='.mp4' or p.name=='LIVRAISON.json'):continue
            assert p.resolve().is_relative_to(ROOT),str(p)
            collected.append(p)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in sorted(collected):z.write(p,'MOU/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name in ['sources/animation.py','sources/render.py','sources/son.py','sources/verify.py','sources/package.py','chronologie.json','CONTROLE.txt','controle/audit_final.json']:
            assert 'MOU/episodes/01/'+name in z.namelist()
    def describe(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    timeline=json.loads((EP/'chronologie.json').read_text())
    result={'titre':'MOU 01 — '+timeline['titre'],'revision':timeline['revision'],'duree_secondes':timeline['duree_secondes'],'resolution':[1080,1920],'fps':24,
            'fichiers':{n:describe(EP/n) for n in ['MOU_01_le_retardateur.mp4','MOU_01_le_retardateur_muet.mp4']},
            'sources':archive.name,'bilan':'CONTROLE.txt','archive_sources':{**describe(archive),'fichiers':len(collected)},
            'apercu_github':{'fichier':'MOU_01_apercu.gif','muet':True,'width':270,'height':480,'duration_seconds':timeline['duree_secondes']}}
    (EP/'LIVRAISON.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
