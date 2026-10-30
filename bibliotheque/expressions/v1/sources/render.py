"""Render reusable MOU face studies with the approved body and native arms.

No production rig, episode source or sound file is modified. The catalogue
describes proposed acting choices, not a measured emotional taxonomy.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import html
import importlib.util
import io
import json
import sys
import textwrap
import xml.etree.ElementTree as ET

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
LIB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(LIB/'sources'))
import mou_rig as rig
import face

spec=importlib.util.spec_from_file_location('expression_native_arms',ROOT/'episodes/03/film/sources/animation.py')
arms=importlib.util.module_from_spec(spec);spec.loader.exec_module(arms)
BG='#FFF8ED';INK='#2B0A24'


def catalogue():
    return json.loads((LIB/'catalogue.json').read_text())


def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def actor(params,uid='library',include_arms=True):
    native={**rig.DEFAULT_POSE,'arm_clasp':1.}
    fragment=rig.character_fragment(native,uid=uid+'-native')
    for side in ('left','right'):
        original=rig._arm(side,0.,1.)
        assert fragment.count(original)==1
        fragment=fragment.replace(original,'',1)
    prefix,sep,_=fragment.partition('<g id="face">');assert sep
    limb=''.join(arms.draw_arm(side,{'hips':0.,'clasp':1.,'rotation':0.}) for side in ('left','right'))
    return prefix+(limb if include_arms else '')+face.face_fragment(params,uid)


def svg(params,uid='library',portrait=False,background=False):
    vb='105 132 205 248' if portrait else '45 105 310 355'
    w,h=(492,595) if portrait else (620,710)
    rect=f'<rect x="0" y="0" width="400" height="500" fill="{BG}"/>' if background else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">{rect}{actor(params,uid,include_arms=not portrait)}</svg>'


def raster(data,w=None,h=None):
    options={}
    if w:options['output_width']=w
    if h:options['output_height']=h
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode(),**options))).convert('RGBA')


def font(size,bold=True):
    name='DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    return ImageFont.truetype(str(ROOT/'fonts'/name),size)


def title(entry):return entry.get('label',entry.get('name',entry['id']))


def board(entries,path,heading,blind=False):
    columns=3;cw,ch=360,400;rows=(len(entries)+columns-1)//columns
    image=Image.new('RGB',(cw*columns,rows*ch+105),BG);d=ImageDraw.Draw(image)
    d.text((20,15),heading,font=font(27),fill=INK)
    d.text((20,58),'MOU · modèle et deux moufles conservés · étude de visage',font=font(16,False),fill='#73516B')
    for i,p in enumerate(entries):
        x=i%columns*cw;y=100+i//columns*ch
        im=raster(svg(p['params'],p['id'],portrait=True),320,344)
        image.paste(im,(x+20,y),im)
        label=f'{i+1:02d}' if blind else title(p)
        for j,line in enumerate(textwrap.wrap(label,26)[:2]):
            d.text((x+18,y+347+j*22),line,font=font(18),fill=INK)
    image.save(path)


def gallery(data):
    entries=[]
    for p in data['poses']:
        full=svg(p['params'],p['id'],False,False)
        portrait=svg(p['params'],p['id']+'-preview',True,True)
        uri=lambda s:'data:image/svg+xml;base64,'+base64.b64encode(s.encode()).decode()
        entries.append({'id':p['id'],'family':p['family'],'intensity':p['intensity'],
                        'label':title(p),'intention':p.get('intention',''),
                        'context':p.get('context',''),'portrait':uri(portrait),'full':uri(full)})
    payload=json.dumps(entries,ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOU — bibliothèque d'expressions</title><style>
*{box-sizing:border-box}body{margin:0;background:#fff8ed;color:#2b0a24;font:17px system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:24px}h1{font-size:30px;margin:0 0 12px}p{line-height:1.5}
.filters{display:flex;gap:12px;flex-wrap:wrap;margin:22px 0}input,select,button,a.button{padding:12px;border:1px solid #bba7ba;border-radius:12px;background:white;color:#2b0a24;font:inherit}
input{flex:1;min-width:220px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}
article{background:white;border:1px solid #e6dce7;border-radius:20px;padding:14px;display:flex;flex-direction:column}
article img{width:100%;aspect-ratio:205/248;object-fit:contain}h2{font-size:18px;margin:12px 0 5px}small{line-height:1.5}
article a{margin-top:12px;text-decoration:none;text-align:center}.count{color:#73516b}dialog{border:0;border-radius:20px;max-width:90vw;background:#fff8ed}dialog img{max-height:70vh;max-width:75vw;display:block;margin:auto}
</style><main><h1>MOU — expressions et intentions</h1><p>36 poses de visage proposées, réparties en 12 familles. Une émotion devient claire grâce au regard, à l'objet et au geste qui l'accompagnent.</p>
<div class="filters"><input id="query" type="search" placeholder="Chercher une expression ou une situation" aria-label="Rechercher"><select id="family" aria-label="Famille"><option value="">Toutes les familles</option></select><select id="level" aria-label="Intensité"><option value="">Toutes les intensités</option><option value="leger">Légère</option><option value="franc">Franche</option><option value="exagere">Exagérée</option></select></div>
<p id="count" class="count"></p><div id="grid" class="grid"></div><p>Pour une scène claire, choisis aussi la cible du regard et le geste qui accompagne l'expression.</p></main>
<dialog id="detail"><button id="close">Fermer</button><h2 id="detailTitle"></h2><img id="full" alt="MOU en pied"><a id="download" class="button">Télécharger le SVG</a></dialog><script>
const entries=PAYLOAD;
const $=id=>document.getElementById(id);
const labels=FAMILY_LABELS;
Object.entries(labels).forEach(([id,label])=>{const o=document.createElement('option');o.value=id;o.textContent=label;$('family').append(o)});
function show(p){$('detailTitle').textContent=p.label;$('full').src=p.full;$('download').href=p.full;$('download').download=p.id+'.svg';$('detail').showModal()}
const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
function render(){const q=norm($('query').value);const result=entries.filter(p=>(!$('family').value||p.family===$('family').value)&&(!$('level').value||p.intensity===$('level').value)&&(!q||norm(p.label+' '+p.intention+' '+p.context+' '+p.family+' '+labels[p.family]).includes(q)));$('grid').replaceChildren();$('count').textContent=result.length+' expression'+(result.length>1?'s':'');result.forEach(p=>{const c=document.createElement('article'),im=document.createElement('img'),h=document.createElement('h2'),s=document.createElement('small'),b=document.createElement('button');im.src=p.portrait;im.alt=p.label;h.textContent=p.label;s.textContent=p.intention;b.textContent='Voir MOU en pied';b.onclick=()=>show(p);c.append(im,h,s,b);$('grid').append(c)})}
['query','family','level'].forEach(id=>$(id).addEventListener('input',render));$('close').onclick=()=>$('detail').close();render();
</script></html>'''
    families={f['id']:f.get('label',f['id']) for f in data['families']}
    page=page.replace('PAYLOAD',payload).replace('FAMILY_LABELS',json.dumps(families,ensure_ascii=False))
    page=page.replace('36 poses de visage proposées, réparties en 12 familles.',f'{len(entries)} poses de visage proposées, réparties en {len(families)} familles.')
    (LIB/'galerie.html').write_text(page)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--draft',action='store_true');args=parser.parse_args()
    data=catalogue();poses=data['poses'];assert len(poses)==data['pose_count'] and len({p['id'] for p in poses})==len(poses)
    sources=[ROOT/'mou_rig.py',ROOT/'episodes/03/film/sources/animation.py',LIB/'sources/face.py',LIB/'sources/render.py',LIB/'catalogue.json']
    frozen={str(p.relative_to(ROOT)):digest(p) for p in sources}
    for folder in ('exports/svg','exports/png','planches','controle'):(LIB/folder).mkdir(parents=True,exist_ok=True)
    for p in poses:
        s=svg(p['params'],p['id']);ET.fromstring(s)
        (LIB/'exports/svg'/f'{p["id"]}.svg').write_text(s)
        raster(s).save(LIB/'exports/png'/f'{p["id"]}.png')
    for j in range(0,len(poses),9):
        board(poses[j:j+9],LIB/'planches'/f'{j//9+1:02d}_expressions.png',f'MOU — expressions · planche {j//9+1}/{(len(poses)+8)//9}')
    heroes=[p for p in poses if p['intensity']=='franc'];assert len(heroes)==len(data['families'])
    board(heroes,LIB/'MOU_expressions_apercu.png',f'MOU — {len(heroes)} familles de jeu')
    board(heroes,LIB/'controle/lecture_sans_labels.png','MOU — lecture des expressions',blind=True)
    gallery(data)
    assert frozen=={p:digest(ROOT/p) for p in frozen},'Sources changed during rendering'
    (LIB/'controle/sources_images.json').write_text(json.dumps({'status':'draft' if args.draft else 'rendered','frozen_sources_sha256':frozen,'poses':len(poses),'families':len(data['families']),'limits':'Visual prototype, not audience approval; body/arms fixed for comparison.'},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'poses':len(poses),'families':len(data['families']),'gallery':str(LIB/'galerie.html'),'preview':str(LIB/'MOU_expressions_apercu.png')}))


if __name__=='__main__':main()
