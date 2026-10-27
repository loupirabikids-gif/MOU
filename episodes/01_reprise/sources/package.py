"""Sources de la nouvelle réalisation uniquement, références et équipe communes."""
from pathlib import Path
import hashlib,json,os,zipfile
ROOT=Path(__file__).resolve().parents[3]
EP=Path(__file__).resolve().parents[1]
IGNORED={'.git','.venv','work','cache','frames','__pycache__'}

def main():
    archive=EP/'MOU_le_retardateur_sources.zip';collected=[]
    bases=[EP]+[ROOT/n for n in ['AGENTS.md','BRIEF_MOU_CODEX.txt','PILOTE_01.txt','mou_rig.py','verification.py','requirements.txt','README.md','SOURCES.txt','fonts','references','output','equipe','.codex','editorial','publication']]
    for base in bases:
        if base.is_file():collected.append(base);continue
        if not base.is_dir():continue
        for directory,dirs,names in os.walk(base):
            dirs[:]=[d for d in dirs if d not in IGNORED]
            for name in names:
                p=Path(directory)/name
                if p.suffix=='.pyc' or p==archive:continue
                if p.parent==EP and (p.suffix=='.mp4' or p.name=='LIVRAISON.json'):continue
                assert p.resolve().is_relative_to(ROOT)
                collected.append(p)
    collected=sorted(set(collected))
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=8)as z:
        for p in collected:z.write(p,'MOU/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None
        for n in ['sources/animation.py','sources/render.py','sources/son.py','sources/verify.py','sources/package.py','chronologie.json','CONTROLE.txt','controle/audit_final.json']:
            assert 'MOU/'+EP.relative_to(ROOT).as_posix()+'/'+n in z.namelist()
    def describe(p):return {'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    t=json.loads((EP/'chronologie.json').read_text());stem=t['file_stem']
    result={'titre':t['titre'],'nouvelle_realisation':True,'revision':t['revision'],'duree_secondes':t['duree_secondes'],'resolution':[t['width'],t['height']],'fps':t['fps'],
            'fichiers':{n:describe(EP/n)for n in [f'{stem}.mp4',f'{stem}_muet.mp4']},
            'sources':archive.name,'archive_sources':{**describe(archive),'fichiers':len(collected)},'bilan':'CONTROLE.txt',
            'apercu_github':{'fichier':'MOU_le_retardateur_apercu.gif','muet':True,'width':270,'height':480,'duration_seconds':t['duree_secondes']}}
    (EP/'LIVRAISON.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
