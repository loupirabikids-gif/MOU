"""Placement fixe de MOU dans le décor de cuisine validé. Aucun mouvement."""
from pathlib import Path
import hashlib,io,json,re,sys,xml.etree.ElementTree as ET
import cairosvg
from PIL import Image
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'mou_rig.py').is_file())
sys.path.insert(0,str(ROOT))
from mou_rig import DEFAULT_POSE, character_fragment, _arm
OUT=Path(__file__).resolve().parents[1]
DECOR=OUT.parent/'decor'
W,H=1080,1920
RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
DECOR_PNG_SHA='3148c402d57d24c1dc8ef5c5731aa2c07346c3d03fcade74e84c9a7e7ec2f585'
DECOR_SVG_SHA='7e5292c066a8bdafca4ae42586fbf89ca62f6a45dcbca468bf9b748f19da2d49'
VALIDATED_COMMIT='795563c2855866993ed4d4a610616544d6e92dac'
X,Y,SCALE=80.,380.,2.30
POSE={**DEFAULT_POSE,'arm_hips':0.,'arm_clasp':1.,
      'eye_open_l':1.,'eye_open_r':1.,'pupil_x':0.,'pupil_y':.18,
      'brow_raise':.08,'smile':.12}

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def document(parts):
    return(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">'+''.join(parts)+'</svg>')
def image(data):
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=data.encode()))).convert('RGBA')

def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'controle').mkdir(exist_ok=True)
    assert digest(ROOT/'mou_rig.py')==RIG_SHA
    assert digest(DECOR/'MOU_cuisine_decor.png')==DECOR_PNG_SHA
    assert digest(DECOR/'MOU_cuisine_decor.svg')==DECOR_SVG_SHA
    before={p.relative_to(DECOR).as_posix():digest(p)for p in[
        DECOR/'MOU_cuisine_decor.png',DECOR/'MOU_cuisine_decor.svg',
        *sorted((DECOR/'calques').glob('*.svg')),*sorted((DECOR/'calques').glob('*.png'))]}
    ET.register_namespace('','http://www.w3.org/2000/svg')
    approved=ET.fromstring((DECOR/'MOU_cuisine_decor.svg').read_text())
    serial=lambda e:ET.tostring(e,encoding='unicode')
    defs=serial(next(e for e in approved if e.tag.endswith('defs')))
    groups={e.attrib['id']:serial(e)for e in approved if'id'in e.attrib}
    back=groups['fond-cuisine'];island=groups['ilot-cuisine'];props=groups['accessoires-cuisine']
    canonical=character_fragment(POSE,uid='mou-cuisine')
    arms=[_arm(side,POSE['arm_hips'],POSE['arm_clasp'])for side in('left','right')]
    torso=canonical
    for part in arms:
        assert torso.count(part)==1
        torso=torso.replace(part,'',1)
    transform=f'translate({X:.4f} {Y:.4f}) scale({SCALE:.4f})'
    behind=f'<g id="mou-arriere" transform="{transform}">{torso}</g>'
    front=f'<g id="mou-bras-premier-plan" transform="{transform}">'+''.join(arms)+'</g>'
    vector=document([defs,back,behind,island,front,props])
    # Re-empiler les bras d'origine, une fois chacun, permet de voir les mains
    # sur le plan de travail sans toucher à leur dessin ou à leurs racines.
    assert all(vector.count(a)==1 for a in arms)
    root=ET.fromstring(vector);ids=[e.attrib['id']for e in root.iter()if'id'in e.attrib]
    assert len(ids)==len(set(ids))
    assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',vector))
    assert sum(e.attrib.get('data-part')=='hand'for e in root.iter())==2
    (OUT/'MOU_cuisine_placement.svg').write_text(vector)
    im=image(vector);im.save(OUT/'MOU_cuisine_placement.png')
    im.resize((540,960),Image.Resampling.LANCZOS).save(OUT/'MOU_cuisine_placement_apercu.png')
    original=Image.open(DECOR/'MOU_cuisine_decor.png').convert('RGBA')
    rerender=image(document([defs,back,island,props]))
    baseline_delta=np.abs(np.asarray(rerender).astype(float)-np.asarray(original).astype(float))
    assert baseline_delta.max()==0.,'approved decor changed while importing'
    # Vérifier que tous les pixels hors de MOU restent ceux du décor.
    a0=np.asarray(image(document([behind])).getchannel('A'),float)/255.
    a1=np.asarray(image(document([front])).getchannel('A'),float)/255.
    island_a=np.asarray(Image.open(DECOR/'calques/ilot_cuisine.png').getchannel('A'),float)/255.
    props_a=np.asarray(Image.open(DECOR/'calques/accessoires_cuisine.png').getchannel('A'),float)/255.
    visible=1.-(1.-a0*(1.-island_a)*(1.-props_a))*(1.-a1*(1.-props_a))
    error=np.abs(np.asarray(im).astype(float)-np.asarray(original).astype(float))
    outside=visible==0.;assert float(error[outside].max())<=1.
    assert before=={name:digest(DECOR/name)for name in before}
    metadata={'etape':'placement_fixe_uniquement','dimensions':[W,H],
        'decor_valide_commit':VALIDATED_COMMIT,'decor_png_sha256':DECOR_PNG_SHA,
        'decor_svg_sha256':DECOR_SVG_SHA,
        'personnage':'mou_rig.py original, sans déformation',
        'transform':{'translate':[X,Y],'scale':SCALE},'pose':POSE,
        'ordre_calques':['fond','MOU corps/visage/pieds','ilot','MOU bras originaux','accessoires'],
        'animation':False,'audio':False,
        'limite':'Image de placement ; aucune prise d’objet ni action de cuisine validée.'}
    (OUT/'PLACEMENT.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    report={'dimensions':[W,H],'original_rig_sha256':RIG_SHA,
        'two_original_arm_fragments_exact_once':True,'two_hands':True,
        'unique_ids_and_valid_clip_references':True,'decor_files_unchanged':before,
        'decor_without_character_pixel_identical':True,
        'maximum_pixel_error_outside_visible_character':float(error[outside].max()),
        'source_sha256':digest(Path(__file__)),'placement_png_sha256':digest(OUT/'MOU_cuisine_placement.png'),
        'limits':'Géométrie originale conservée ; vue fixe de taille et position, sans animation ni validation de saisie.'}
    (OUT/'controle/audit_placement.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'dimensions':[W,H],'decor_unchanged':True,'two_original_hands':True,
        'outside_character_max_error':float(error[outside].max()),
        'output':str(OUT/'MOU_cuisine_placement.png')},ensure_ascii=False))
if __name__=='__main__':main()
