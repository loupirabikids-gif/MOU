"""Décor original MOU : cuisine fixe, SVG et calques PNG reproductibles."""
from pathlib import Path
import json, hashlib
import cairosvg
from PIL import Image

OUT=Path(__file__).resolve().parents[1]
INK='#382035'
W,H=1080,1920
layers={}

def path(d,fill='none',stroke=INK,sw=7,**attrs):
    a=' '.join(f'{k.replace("_","-")}="{v}"'for k,v in attrs.items())
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {a}/>'
def rect(x,y,w,h,fill,rx=0,stroke=INK,sw=7,**attrs):
    a=' '.join(f'{k.replace("_","-")}="{v}"'for k,v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {a}/>'
def ell(x,y,rx,ry,fill,stroke='none',sw=0,**attrs):
    a=' '.join(f'{k.replace("_","-")}="{v}"'for k,v in attrs.items())
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {a}/>'
def group(name,items,**attrs):
    a=' '.join(f'{k.replace("_","-")}="{v}"'for k,v in attrs.items())
    return f'<g id="{name}" {a}>'+''.join(items)+'</g>'

DEFS='''<defs>
<linearGradient id="wall" x2="0" y2="1"><stop stop-color="#FFF4E5"/><stop offset="1" stop-color="#EEDDDC"/></linearGradient>
<linearGradient id="wood" x2="0" y2="1"><stop stop-color="#F7E3C2"/><stop offset="1" stop-color="#EBC59E"/></linearGradient>
<linearGradient id="paper" x2="1" y2="0"><stop stop-color="#EFE4E5"/><stop offset=".25" stop-color="#FFFDF7"/><stop offset=".75" stop-color="#FFFDF7"/><stop offset="1" stop-color="#E4D5DC"/></linearGradient>
<linearGradient id="sky" x2="0" y2="1"><stop stop-color="#BDD7DD"/><stop offset="1" stop-color="#E2ECE6"/></linearGradient>
<clipPath id="window-clip"><rect x="93" y="304" width="232" height="394" rx="91"/></clipPath>
</defs>'''

# Architecture et fond : le centre est volontairement calme.
back=[rect(0,0,W,H,'url(#wall)',stroke='none',sw=0),
      path('M0 1667 H1080 V1920 H0 Z','#E4D6DD','none',0),
      path('M0 1667 H1080',stroke='#D3BDC9',sw=5),
      path('M0 1791 H1080 M0 1902 H1080',stroke='#D6C2CB',sw=3),
      path('M165 1667 L72 1920 M476 1667 L453 1920 M789 1667 L850 1920',stroke='#D6C2CB',sw=3)]
back += [path('M187 690 L396 690 L772 1317 L455 1317 Z','#FFF8E8','none',0,opacity='.55')]
# Fenêtre sur le côté, ciel, soleil et deux nuages.
window=[rect(80,289,257,430,'#D8B99F',113,sw=8),
        rect(93,304,232,394,'url(#sky)',91,sw=5)]
sky=[ell(264,407,39,39,'#FFF1C7'),
     path('M81 468 Q100 440 128 458 Q134 429 162 438 Q184 438 190 462 Q212 455 229 472 Z','#F8F6EA','none',0),
     path('M237 553 Q256 528 278 540 Q291 516 315 536 Q342 537 347 558 Z','#F8F6EA','none',0),
     path('M88 655 Q145 621 198 643 Q253 602 334 632 V720 H88 Z','#9BB9AF','none',0)]
window.append(group('vue-exterieure',sky,clip_path='url(#window-clip)'))
window += [path('M209 306 V697 M97 499 H322',stroke='#6E5362',sw=8),
           path('M80 706 Q205 695 340 705 L352 730 Q215 745 71 731 Z','#F4D8B7',sw=7)]
back.append(group('fenetre',window))
# Étagère et bocaux de fond, au-dessus de l'espace de jeu.
shelf=[path('M432 474 V502 M739 474 V502',stroke='#926E75',sw=9),
       path('M411 456 Q579 449 764 456 L760 479 Q578 486 415 478 Z','#C99375',sw=7),
       path('M439 451 V384 Q439 368 454 368 H485 Q500 368 500 384 V451 Z','#E6D4BB',sw=5),
       rect(436,354,67,23,'#A67564',8,sw=5),
       path('M447 448 V411 Q470 402 492 412 V448 Z','#D5A06E','none',0),
       path('M529 449 V402 Q529 388 541 388 H571 Q583 388 583 402 V449 Z','#EADFD0',sw=5),
       rect(526,376,60,22,'#C49C79',7,sw=5),
       path('M535 446 V420 Q557 411 577 419 V446 Z','#AFC1AF','none',0),
       path('M622 451 V361 Q622 345 637 345 H677 Q692 345 692 361 V451 Z','#F0E5D4',sw=5),
       rect(618,332,78,24,'#AD8586',8,sw=5),
       path('M630 447 V397 Q657 388 684 395 V447 Z','#D5B0A3','none',0),
       path('M450 389 V401 M637 368 V384',stroke='#FFF8EA',sw=5)]
back.append(group('etagere',shelf))
# Meuble mural latéral.
cab=[path('M840 337 L1029 337 L1045 355 V739 H840 Z','#A888AD',sw=8),
     rect(820,337,209,400,'#CDB4D0',22,sw=8),
     path('M925 349 V724',stroke='#AE8FB5',sw=5),
     rect(843,365,61,282,'#D8C3D9',14,stroke='#B59ABB',sw=4),
     rect(945,365,61,282,'#D8C3D9',14,stroke='#B59ABB',sw=4),
     ell(904,556,8,13,'#C28F6D',INK,4),ell(946,556,8,13,'#C28F6D',INK,4)]
back.append(group('meuble-haut',cab))
# Suspension arrondie ; lumière suggérée sans filtre raster.
lamp=[path('M620 0 V215',stroke='#6C5365',sw=7),
      path('M593 218 Q620 199 647 218 L655 244 H584 Z','#BE8D68',sw=6),
      path('M584 239 Q510 262 494 327 Q614 354 746 327 Q728 262 655 239 Z','#D4B0C0',sw=8),
      ell(620,327,126,24,'#F8E7BF',INK,7),
      ell(620,331,59,11,'#FFF5D7'),
      path('M521 300 Q538 270 569 261',stroke='#E6CDDC',sw=8)]
back.append(group('suspension',lamp,transform='translate(0 -50)'))
# Crédence latérale : pas de joints sombres derrière le futur visage.
tile=[]
for x0,x1 in [(0,302),(803,1080)]:
    tile.append(rect(x0,925,x1-x0,211,'#E6D6D5',stroke='none',sw=0))
    for y in (925,995,1065,1135):tile.append(path(f'M{x0} {y} H{x1}',stroke='#D3BEC5',sw=3))
    for y in (925,995,1065):
        for x in range(x0+34+(35 if y==995 else 0),x1,100):
            tile.append(path(f'M{x} {y} V{y+70}',stroke='#D3BEC5',sw=3))
back.append(group('credence-laterale',tile))
# Arrière-plan de cuisine : évier et petite zone d'épices.
rear=[path('M-30 1165 L18 1115 H304 V1192 H-30 Z','#DABDA8',sw=7),
      path('M0 1187 H303 V1490 H0 Z','#C4ADCA',sw=7),
      path('M170 1202 V1450',stroke='#A68AAF',sw=4),
      path('M45 1246 H105 M215 1246 H264',stroke='#65495F',sw=7),
      ell(158,1142,98,26,'#FFF3E4',INK,6),
      ell(158,1145,74,16,'#B5BFC1','#807B89',4),
      path('M159 1121 V1054 Q159 1017 128 1017 Q102 1017 102 1045 V1069',stroke='#5E5267',sw=15),
      path('M159 1121 V1054 Q159 1027 139 1025',stroke='#C1B9C9',sw=5),
      path('M202 1124 V1106 L221 1095',stroke='#6D596E',sw=8),
      path('M799 1124 H1115 V1188 H799 Z','#DABDA8',sw=7),
      path('M799 1188 H1080 V1480 H799 Z','#C4ADCA',sw=7),
      path('M890 1205 V1460',stroke='#A68AAF',sw=4),
      path('M929 1236 H1004',stroke='#65495F',sw=7)]
back.append(group('arriere-cuisine',rear))
# Deux ustensiles latéraux de fond.
tools=[path('M917 800 H1026',stroke='#9A7A8D',sw=6),
       path('M941 809 V845',stroke='#705567',sw=5),
       path('M940 841 Q963 864 946 899 L948 993 Q940 1003 933 993 L935 899 Q916 865 940 841 Z','#C49B7B',sw=5),
       path('M1002 809 V865 M1002 900 V986',stroke='#705567',sw=7),
       path('M980 858 L1023 858 L1021 909 Q1002 921 982 909 Z','#9FB1AD',sw=5),
       path('M992 870 V899 M1003 870 V899 M1013 870 V899',stroke='#D3D8CE',sw=3)]
back.append(group('ustensiles-fond',tools))
back += [ell(540,1772,496,54,'#CBB9CA',opacity='.55')]
layers['fond_cuisine']=group('fond-cuisine',back)

# Îlot au premier plan, séparé pour accueillir ensuite le personnage.
island=[path('M113 1447 H973 L950 1723 Q544 1756 134 1723 Z','#B59ABE',sw=8),
        path('M144 1707 Q540 1734 949 1706 L947 1743 Q540 1765 147 1740 Z','#6E5478',sw=6),
        path('M157 1488 H516 V1683 Q333 1698 161 1681 Z','#C9B2D0',sw=6),
        path('M555 1488 H928 L915 1681 Q737 1698 555 1684 Z','#C9B2D0',sw=6),
        path('M180 1510 H491 M580 1510 H902',stroke='#DFCEE1',sw=4),
        rect(272,1537,111,22,'#C39074',11,sw=5),
        rect(684,1537,111,22,'#C39074',11,sw=5),
        path('M115 1273 Q129 1260 154 1260 H928 Q950 1260 960 1277 L1030 1419 Q1041 1445 1014 1453 H66 Q39 1447 51 1421 Z','url(#wood)',sw=9),
        path('M66 1453 H1014 V1480 Q1013 1494 992 1496 H85 Q63 1494 63 1476 Z','#D6A885',sw=8),
        path('M119 1288 H940',stroke='#FFF0D5',sw=5),
        path('M87 1434 Q540 1437 1005 1434',stroke='#F8E5C3',sw=5)]
layers['ilot_cuisine']=group('ilot-cuisine',island)

# Plaque, poêle et planche : accessoires amovibles.
hob=[path('M161 1285 H467 L519 1414 H119 Z','#81667F',sw=7),
     path('M173 1297 H458 L498 1400 H140 Z','#67546D',sw=4),
     ell(292,1320,107,36,'none','#AA8EAA',4),
     ell(292,1320,84,27,'none','#AA8EAA',3),
     ell(200,1396,10,6,'#D9BFA9',INK,3),
     ell(245,1396,10,6,'#D9BFA9',INK,3),
     ell(290,1396,10,6,'#D9BFA9',INK,3),
     ell(337,1396,4,4,'#F5B794')]
pan=[path('M421 1312 L466 1312 L570 1356 Q585 1366 576 1377 Q572 1386 559 1382 L447 1348 L416 1332 Z','#4D3B52',sw=7),
     path('M472 1327 L557 1365',stroke='#887188',sw=5),
     path('M162 1307 Q166 1354 202 1371 Q285 1406 376 1369 Q422 1351 425 1307 Z','#68536D',sw=7),
     ell(293,1307,132,48,'#473A50',INK,8),
     ell(293,1304,114,34,'#73657B','#9D8CA3',3),
     path('M203 1301 Q231 1284 270 1283',stroke='#A398AA',sw=5),
     path('M185 1345 Q291 1389 407 1341',stroke='#8C7390',sw=4)]
board=[path('M605 1331 L748 1327 Q763 1326 766 1340 L770 1389 Q770 1403 750 1405 L609 1411 Q590 1410 588 1396 L585 1349 Q585 1334 605 1331 Z','#DDAA81',sw=5),
       path('M607 1344 L744 1341 M609 1397 L747 1391',stroke='#EDC69E',sw=3),
       ell(748,1345,5,4,'#8C6162'),
       path('M631 1355 L668 1387 M672 1355 L698 1380 M709 1355 L732 1376',stroke='#BC896C',sw=2,opacity='.6')]
# Rouleau d'essuie-tout : silhouette haute, cœur et feuille déroulée.
roll=[ell(877,1350,90,24,'#BD936F',INK,6),
      ell(877,1345,72,14,'#DDBA91','#896776',3),
      path('M809 1108 C806 1163 807 1263 812 1320 Q876 1346 941 1320 V1108 Z','url(#paper)',sw=7),
      path('M928 1128 V1308',stroke='#D3C1CE',sw=3),
      ell(876,1108,67,25,'#FFFDF6',INK,6),
      ell(876,1109,16,7,'#B19493','#796274',4),
      path('M876 1079 V1105',stroke='#A37E64',sw=13),
      ell(876,1077,7,5,'#C29B7C',INK,3),
      path('M810 1140 Q797 1152 790 1190 L770 1282 Q797 1299 825 1295 L844 1207 Q852 1166 847 1144 Z','#FFFCF5',sw=5),
      path('M783 1230 Q807 1243 835 1240',stroke='#C4ACBC',sw=2.8,stroke_dasharray='4 7'),
      path('M824 1135 V1160',stroke='#E5D8DF',sw=2)]
for x,y in [(867,1161),(897,1199),(871,1245),(899,1286)]:
    roll.append(path(f'M{x-5} {y} q5 -7 10 0 q-5 7 -10 0',stroke='#E7DBDF',sw=2))
layers['accessoires_cuisine']=group('accessoires-cuisine',[
    group('plaque-cuisson',hob),group('poele',pan),
    group('planche-preparation',board),group('essuie-tout',roll)])

def svg(parts):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+DEFS+''.join(parts)+'</svg>'

def main():
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'calques').mkdir(exist_ok=True)
    master=svg(layers.values())
    (OUT/'MOU_cuisine_decor.svg').write_text(master)
    cairosvg.svg2png(bytestring=master.encode(),write_to=str(OUT/'MOU_cuisine_decor.png'))
    for name,content in layers.items():
        data=svg([content]);(OUT/'calques'/f'{name}.svg').write_text(data)
        cairosvg.svg2png(bytestring=data.encode(),write_to=str(OUT/'calques'/f'{name}.png'))
    master_image=Image.open(OUT/'MOU_cuisine_decor.png').convert('RGBA')
    assert master_image.getchannel('A').getextrema()==(255,255)
    assert '<image ' not in master
    image=master_image.convert('RGB')
    image.resize((540,960),Image.Resampling.LANCZOS).save(OUT/'MOU_cuisine_apercu.png')
    manifest={'episode':'03','etape':'decor_fixe_uniquement','version':1,
        'dimensions':[W,H],'personnage_present':False,'animation':False,'audio':False,
        'palette':{'outline':INK,'cream':'#FFF4E5','lavender':'#CDB4D0','paper':'#FFFDF7','wood':'#EBC59E'},
        'zones':{'jeu_futur_mou':{'x':[340,750],'y':[650,1300]},
                 'surface_plan_de_travail':{'y':[1260,1453]},
                 'poele':{'centre':[293,1307]},
                 'papier':{'centre':[876,1225]},
                 'accumulation_future_papier':{'x':[0,330],'y':[1500,1900]}},
        'calques':list(layers),'sources':'sources/decor.py',
        'outils':['Python','SVG','CairoSVG','Pillow'],
        'limites':'Proposition de décor ; aucune animation ni interaction des mains avec les accessoires validée.'}
    (OUT/'DECOR.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    assert image.size==(1080,1920)
    # Compositing des calques PNG : mêmes dessins que le master SVG.
    result=Image.new('RGBA',(W,H),(0,0,0,0))
    for name in layers:result=Image.alpha_composite(result,Image.open(OUT/'calques'/f'{name}.png').convert('RGBA'))
    import numpy as np
    delta=np.abs(np.asarray(result.convert('RGB')).astype(float)-np.asarray(image).astype(float))
    assert delta.mean()<.6
    report={'dimensions':[W,H],'master_opaque':True,'layers':3,
        'png_layer_composite_mean_delta_0_255':float(delta.mean()),
        'no_character':True,'no_embedded_raster_inputs':True,
        'sha256':hashlib.sha256((OUT/'MOU_cuisine_decor.png').read_bytes()).hexdigest()}
    (OUT/'controle/audit_decor.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
