"""Isolated mitten/thumb motion proposal; never writes the episode or rig.

Run from the checkout root with its Python dependencies and FFmpeg installed:
  .venv/bin/python episodes/03/etudes_geste/moufle_pouce/render.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import cairosvg
from PIL import Image

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT = Path(__file__).resolve().parent
WORK = ROOT/'work/moufle_pouce_validation'
FPS, DURATION, WIDTH, HEIGHT = 24, 4., 720, 960
INK, SKIN = '#2B0A24', '#D8F449'
REFERENCE = ROOT/'episodes/03/cuisine_v13/sources/render.py'
spec = importlib.util.spec_from_file_location('reference_moufle_pouce', REFERENCE)
ref = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ref
spec.loader.exec_module(ref)
state = ref.animation.scene_state(8.75)
native = ref.sink.geometry_at(8.75, state, ref.animation)
MATRIX = ' '.join(f'{v:.8f}' for v in native['matrix'])

# One continuous mitten outline, including a short protruding thumb.
# The four other fingers remain a single rounded volume. Each pose has the
# same cubic topology. The unchanged native forearm continues to the right.
OPEN = (
    (174.,1087.60),
    (161.,1084.),(151.,1082.),(143.,1080.),
    (137.,1078.5),(133.,1067.),(122.,1067.),
    (110.,1067.),(106.,1077.),(112.,1085.),
    (115.,1089.),(119.,1091.),(123.,1095.),
    (110.,1093.),(97.,1099.),(94.,1110.),
    (89.,1126.),(104.,1137.),(122.,1138.),
    (142.,1140.),(156.,1132.),(174.,1126.8),
)
CONTACT = (
    (174.,1087.60),
    (161.,1084.),(151.,1082.),(143.,1080.),
    (136.,1078.5),(123.,1084.),(113.,1085.),
    (102.,1086.),(98.,1093.),(106.,1099.),
    (111.,1103.),(120.,1103.),(127.,1106.),
    (115.,1101.),(101.,1104.),(96.,1114.),
    (91.,1128.),(105.,1137.),(122.,1138.),
    (142.,1140.),(156.,1132.),(174.,1126.8),
)


def smooth(v):
    v=max(0.,min(1.,v))
    return v*v*(3.-2.*v)


def gesture_at(t):
    """Hold readable silhouette, converge, three local rubs, release, hold."""
    if t<.65:
        amount=0.; phase='pose_moufle'
    elif t<1.10:
        amount=smooth((t-.65)/.45); phase='contact_pouce'
    elif t<2.90:
        amount=1.; phase='frottement'
    elif t<3.35:
        amount=1.-smooth((t-2.90)/.45); phase='relachement'
    else:
        amount=0.; phase='pose_moufle'
    points=[[a[0]+amount*(b[0]-a[0]),a[1]+amount*(b[1]-a[1])]
            for a,b in zip(OPEN,CONTACT)]
    if phase=='frottement':
        u=(t-1.10)/1.80
        wave=math.sin(6.*math.pi*u)
        # The thumb moves relative to the finger bundle. The wrist and arm
        # are fixed: this is not a translation of an otherwise static mitten.
        for i,weight in ((4,.2),(5,.75),(6,1.),(7,1.),(8,1.),(9,1.),(10,.7),(11,.3)):
            points[i][0]+=2.1*wave*weight
            points[i][1]+=.75*math.sin(12.*math.pi*u)*weight
        for i,weight in ((13,.3),(14,.7),(15,1.),(16,.5)):
            points[i][1]-=.6*wave*weight
    d=f'M{points[0][0]:.6f} {points[0][1]:.6f} '
    for i in range(1,len(points),3):
        d+='C'+' '.join(f'{x:.6f} {y:.6f}' for x,y in points[i:i+3])+' '
    return {'time':t,'phase':phase,'amount':amount,'points':points,'path':d.strip()}


def svg_at(t):
    pose=gesture_at(t); d=pose['path']
    parts=[ref.DEFS,
        '<defs><clipPath id="avant-bras-conserve"><rect x="170" y="900" width="500" height="600"/></clipPath>'
        f'<clipPath id="moufle-contour"><path d="{d} Z"/></clipPath></defs>',
        ref.sink._background_without_sink(ref.BACKGROUND),ref.sink._sink_decor(),ref.art.lever_svg(1.),
        ref.sink._water(t),
        f'<g clip-path="url(#avant-bras-conserve)"><g transform="matrix({MATRIX})">{native["native_arm_svg"]}</g></g>',
        f'<path id="moufle-pouce-distinct" d="{d} Z" fill="{SKIN}" stroke="none"/>',
        f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="8.372" stroke-linecap="round" stroke-linejoin="round"/>',
        '<g clip-path="url(#moufle-contour)"><path d="M94 1069 H110 L114 1167 H90 Z" fill="#B8E2E4" opacity=".32"/></g>',
        '<ellipse cx="104" cy="1168" rx="20" ry="4.4" fill="none" stroke="#83AFBB" stroke-width="1.4"/>',
        '<ellipse cx="108" cy="1169" rx="29" ry="6.5" fill="none" stroke="#CDE6E8" stroke-width="1.2"/>']
    if pose['phase']=='frottement':
        for j in range(4):
            u=(t*4+j*.25)%1.
            x=100.-11.*u+j*1.8
            y=1115.+29.*u-7.*math.sin(math.pi*u)
            parts.append(f'<ellipse cx="{x:.4f}" cy="{y:.4f}" rx="1.2" ry="1.8" fill="#D9F7F8" stroke="#86B3BE" stroke-width=".5"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            'viewBox="0 965 270 360">'+''.join(parts)+'</svg>')


def main():
    WORK.mkdir(parents=True,exist_ok=True)
    total=round(FPS*DURATION)
    for i in range(total):
        svg=svg_at(i/FPS)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(WORK/f'{i:04d}.png'))
    for name,t in [('MOU_moufle_pouce',.30),('MOU_moufle_contact',1.40)]:
        svg=svg_at(t)
        (OUT/f'{name}.svg').write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(OUT/f'{name}.png'))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),
        '-i',str(WORK/'%04d.png'),'-an','-c:v','libx264','-crf','14','-preset','medium',
        '-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'MOU_essai_moufle_pouce.mp4')],check=True)
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
        '-i',str(OUT/'MOU_essai_moufle_pouce.mp4'),
        '-filter_complex','fps=12,scale=480:640:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse',
        '-loop','0',str(OUT/'MOU_essai_moufle_pouce.gif')],check=True)
    # Proof images are decoded from the actual delivered MP4, not the source.
    for frame in (7,25,34,39,44,49,54,59,64,70,86):
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i',str(OUT/'MOU_essai_moufle_pouce.mp4'),'-vf',f'select=eq(n\\,{frame})',
            '-frames:v','1',str(WORK/f'export_{frame:04d}.png')],check=True)
    sheet=Image.new('RGB',(720*4,960*3),'#FFF3E4')
    for i,path in enumerate(sorted(WORK.glob('export_*.png'))):
        sheet.paste(Image.open(path).convert('RGB'),((i%4)*720,(i//4)*960))
    sheet.resize((1440,1440),Image.Resampling.LANCZOS).save(WORK/'planche_export.png')
    report={'duration':DURATION,'fps':FPS,'frames':total,'size':[WIDTH,HEIGHT],
        'silent':True,'scope':'Etude isolee, episode et rig non modifies',
        'cycles_relative_thumb_motion':3,
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in OUT.iterdir() if p.suffix in ('.png','.svg','.gif','.mp4','.py')}}
    (OUT/'controle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
