"""Le retardateur — production SVG/CairoSVG/FFmpeg, sans service externe.
Run from any working directory; the input rig is the supplied mou_rig.py.
"""
from pathlib import Path
import argparse, base64, concurrent.futures, hashlib, io, json, math, os, re, subprocess, sys
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
EP = ROOT/'episodes'/'01'
sys.path.insert(0,str(ROOT))
from animation import pose_at, motion_at, character_at, intention_at, deformation_at
from mou_rig import PALETTE
import cairosvg
from PIL import Image, ImageDraw, ImageFont
FPS=24
DURATION=14
W,H=1080,1920
FLASH=6.5
INK=PALETTE['outline']
BG='#EEE6FA'
PHOTO=None
CACHE_VERSION='svg-atomic-copy-v2'

def smooth(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def isolated(fragment, prefix):
    ids=re.findall(r'\bid="([^"]+)"',fragment)
    mapping={old:f"{prefix}-{old}" for old in ids}
    fragment=re.sub(r'\bid="([^\"]+)"',lambda m:f'id="{mapping[m[1]]}"',fragment)
    return re.sub(r'url\(#([^)]*)\)',lambda m:f'url(#{mapping.get(m[1],m[1])})',fragment)

def puppet(t,prefix):
    return isolated(character_at(pose_at(t),uid=prefix),prefix)

def photo_svg():
    # The captured pose includes the same body deformation as the main scene.
    # Fit its actual silhouette into the portrait so squash does not crop a
    # hand or the two bumps. Raster alpha is used only to measure SVG bounds.
    avatar=puppet(FLASH,"photo")
    measurement=(f'<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="1240" '
                 f'viewBox="-80 -60 560 620">{avatar}</svg>')
    image=Image.open(io.BytesIO(cairosvg.svg2png(bytestring=measurement.encode()))).convert('RGBA')
    bbox=image.getchannel('A').getbbox()
    assert bbox is not None
    left,top,right,bottom=[bbox[0]/2-80,bbox[1]/2-60,bbox[2]/2-80,bbox[3]/2-60]
    scale=min(432/(right-left),610/(bottom-top))
    cx=(left+right)/2;cy=(top+bottom)/2
    shadow_y=372+(bottom-cy)*scale+9
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="744" viewBox="0 0 480 744">'
            f'<rect width="480" height="744" fill="#E1D1F2"/>'
            f'<ellipse cx="240" cy="{shadow_y:.5f}" rx="205" ry="12" fill="#CBB4E0"/>'
            f'<g transform="translate(240 372) scale({scale:.8f}) translate({-cx:.5f} {-cy:.5f})">{avatar}</g></svg>')

def prepare_photo():
    global PHOTO
    data=cairosvg.svg2png(bytestring=photo_svg().encode())
    (EP/'sources'/'photo_capturee.svg').write_text(photo_svg(),encoding='utf-8')
    (EP/'sources'/'photo_capturee.png').write_bytes(data)
    PHOTO=base64.b64encode(data).decode()
    return PHOTO

def camera(t):
    u=smooth((t-6.85)/.4)*(1-smooth((t-8.85)/.65))
    return (1+2.6*u,-54*u,-3320*u)

def phone(t):
    # One fixed phone and one integrated support. No separate result card.
    result=t>=FLASH+.125
    a=[f'<g id="phone">',
       '<ellipse cx="165" cy="1470" rx="162" ry="18" fill="#CDB9E2"/>',
       f'<path d="M150 1392 V1454 H84 Q70 1454 70 1466 H260 Q260 1454 246 1454 H180 V1392" fill="#74617E" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>',
       f'<rect x="40" y="974" width="250" height="442" rx="36" fill="{INK}"/>',
       '<rect x="53" y="987" width="224" height="416" rx="26" fill="#5C3D5B"/>',
       '<rect x="65" y="1024" width="200" height="310" rx="9" fill="#E1D1F2"/>',
       '<defs><clipPath id="screen"><rect x="65" y="1024" width="200" height="310" rx="9"/></clipPath></defs>',
       '<g clip-path="url(#screen)">']
    if result:
        a.append(f'<image x="65" y="1024" width="200" height="310" href="data:image/png;base64,{PHOTO}"/>')
    else:
        a += ['<rect x="65" y="1024" width="200" height="310" fill="#E1D1F2"/>',
              f'<g transform="translate(165 1313) scale(.77) translate(-200 -450)">{puppet(t,"preview")}</g>']
        # Four viewfinder corners and a shutter button establish photography.
        a.append('<path d="M81 1060 V1041 H101 M229 1041 H249 V1060 M81 1286 V1305 H101 M229 1305 H249 V1286" fill="none" stroke="#FFFDFD" stroke-width="3" opacity=".8"/>')
        digit = next((str(n) for start,n in [(2,3),(3.1,2),(4.2,1)] if start<=t<start+.8),None)
        if digit:
            a.append(f'<circle cx="165" cy="1081" r="39" fill="{INK}" opacity=".94"/><text x="165" y="1107" text-anchor="middle" fill="#FFFDFD" font-family="DejaVu Sans" font-weight="bold" font-size="71">{digit}</text>')
    a += ['</g>', '<circle cx="165" cy="1006" r="7" fill="#D9D0E7"/><circle cx="165" cy="1006" r="3" fill="#301832"/>']
    if result:
        a += ['<rect x="141" y="1351" width="48" height="33" rx="5" fill="#E1D1F2"/>',
              f'<path d="M150 1375 L162 1363 L171 1372 L178 1366" fill="none" stroke="{INK}" stroke-width="3"/>']
    else:
        a += ['<circle cx="165" cy="1366" r="24" fill="none" stroke="#FFFDFD" stroke-width="3"/><circle cx="165" cy="1366" r="18" fill="#FFFDFD"/>',
              '<path d="M94 1356 H109 L113 1361 H118 V1376 H90 V1361 H94 Z" fill="none" stroke="#DFD0EB" stroke-width="2"/><circle cx="104" cy="1368" r="5" fill="none" stroke="#DFD0EB" stroke-width="2"/>']
    pulse=max([max(0,1-(t-start)/.17) if t>=start else 0 for start in [2,3.1,4.2]])
    if t<5 and pulse:
        a.append(f'<circle cx="253" cy="1006" r="6" fill="#D8F449" opacity="{pulse:.3f}"/>')
    a.append('</g>');return ''.join(a)


def vanity_sparkles(t):
    """Deux accents de glamour, brefs et non anatomiques, près du visage."""
    pieces=[]
    for center,x,y,size in [(1.30,946,788,31),(1.43,992,860,20)]:
        u=(t-(center-.10))/.24
        if 0<u<1:
            k=math.sin(math.pi*u)**.6
            pieces.append(f'<path transform="translate({x} {y}) scale({k:.5f})" d="M0 {-size} Q3 -3 {size} 0 Q3 3 0 {size} Q-3 3 {-size} 0 Q-3 -3 0 {-size}Z" fill="#FFF8CF" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')
    return '<g id="vanity-sparkles">'+''.join(pieces)+'</g>' if pieces else ''

def svg_at(t):
    z,tx,ty=camera(t)
    p=pose_at(t);m=motion_at(t)
    brand_op=1-smooth((z-1)/.9)
    a=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1920" viewBox="0 0 1080 1920">',
       f'<rect width="1080" height="1920" fill="{BG}"/>',
       # Small integrated opening signature; no title card or delayed action.
       f'<g opacity="{brand_op:.5f}">',
       f'<text x="76" y="190" font-family="DejaVu Sans" font-weight="bold" font-size="76" letter-spacing="-5" fill="{INK}">MOU</text>',
       '<text x="81" y="239" font-family="DejaVu Sans" font-size="21" letter-spacing="3.5" fill="#7A5D80">01 / LE RETARDATEUR</text>',
       '</g>',
       f'<g id="world" transform="translate({tx:.5f} {ty:.5f}) scale({z:.5f})">',
       '<path d="M300 1470 V850 C300 520 490 403 682 403 C895 403 1100 537 1100 850 V1470 Z" fill="#E8DBF4"/>',
       '<ellipse cx="565" cy="1485" rx="900" ry="113" fill="#E3D5EF"/>',
       '<ellipse cx="670" cy="1468" rx="337" ry="25" fill="#CCB7E0"/>',
       f'<g id="character" transform="translate({670+m.get("dx",0):.5f} {1460+m.get("dy",0):.5f}) scale({2.35*m["sx"]:.6f} {2.35*m["sy"]:.6f}) translate(-200 -450)">{puppet(t,"main")}</g>',
       vanity_sparkles(t), phone(t), '</g>']
    if FLASH<=t<FLASH+.125:
        op=[.94,.65,.22][min(2,int((t-FLASH)*FPS))]
        a.append(f'<rect id="flash" width="1080" height="1920" fill="#FFFDF9" opacity="{op}"/>')
    a.append('</svg>');return ''.join(a)

def render_job(args):
    i,scale,out=args
    data=svg_at(i/FPS).encode()
    key=hashlib.sha256(CACHE_VERSION.encode()+data+str(scale).encode()).hexdigest()
    cache=EP/'cache'/f'{key}.png'
    dest=Path(out)/f'{i:04d}.png'
    if not cache.exists():
        raw=cairosvg.svg2png(bytestring=data,output_width=round(W*scale),output_height=round(H*scale))
        tmp=cache.with_name(f'{key}.{os.getpid()}.tmp');tmp.write_bytes(raw);tmp.replace(cache)
    # Read/copy instead of hard-linking an atomically replaced cache entry:
    # some overlay filesystems race on link+rename from separate workers.
    cached=cache.read_bytes()
    if not dest.exists() or dest.read_bytes()!=cached:
        tmp_dest=dest.with_name(f".{dest.name}.{os.getpid()}.tmp")
        tmp_dest.write_bytes(cached)
        tmp_dest.replace(dest)
    return i

def board(frames,out):
    samples=[0,.9,2.2,3.3,4.5,5.5,6.25,6.5,6.75,7.65,9.6,10.6,11.6,12.6,13.8]
    b=Image.new('RGB',(1500,1725),BG);d=ImageDraw.Draw(b)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),17)
    for j,t in enumerate(samples):
        im=Image.open(Path(frames)/f'{round(t*FPS):04d}.png').convert('RGB'); im.thumbnail((294,523))
        x=(j%5)*300+(300-im.width)//2;y=(j//5)*575
        b.paste(im,(x,y)); d.text(((j%5)*300+14,y+530),f'{t:.2f} s',font=font,fill=INK)
        d.text(((j%5)*300+14,y+552),intention_at(t),font=font,fill=INK)
    b.save(out)

def audit():
    rig_hash=hashlib.sha256((ROOT/'mou_rig.py').read_bytes()).hexdigest()
    assert rig_hash=='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    report={'original_rig_sha256':rig_hash,'frames':FPS*DURATION,'fps':FPS,'duration':DURATION,'flash_frame':156,
            'photo_pose_time':FLASH,'photo_sha256':hashlib.sha256((EP/'sources/photo_capturee.png').read_bytes()).hexdigest()}
    deformations=[]
    fixed_feet=None
    for i in range(FPS*DURATION):
        t=i/FPS;p=pose_at(t);root=ET.fromstring(svg_at(t))
        ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids)==len(set(ids)),(t,'duplicate IDs')
        refs=re.findall(r'url\(#([^)]*)\)',svg_at(t))
        assert all(ref in ids for ref in refs),(t,'missing clip reference')
        main=next(e for e in root.iter() if e.attrib.get('id')=='character')
        hands=[e for e in main.iter() if e.attrib.get('data-part')=='hand']
        assert len(hands)==2,(t,'hands')
        assert {'main-arm-left','main-arm-right','main-face','main-main-eye-l','main-main-eye-r'} <= set(ids),(t,'anatomy')
        assert all(math.isfinite(v) for v in p.values())
        assert p['lift_l']==0 and p['lift_r']==0
        d=deformation_at(p);deformations.append(d)
        assert all(math.isfinite(v) for v in d.values())
        assert d['anchor_y']==437.0
        warp=next((e for e in main.iter() if e.attrib.get('id')=='main-body-warp'),None)
        assert (warp is not None)==any(abs(d[k]-v)>1e-10 for k,v in [('sx',1.),('sy',1.),('skew',0.)])
        feet=[ET.tostring(e) for e in main.iter() if e.attrib.get('id') in {'main-foot-l','main-foot-r'}]
        if fixed_feet is None: fixed_feet=feet
        assert feet==fixed_feet,(t,'feet changed')
        if warp is not None:
            warp_ids={e.attrib.get('id') for e in warp.iter()}
            assert {'main-body','main-arm-left','main-arm-right','main-face'}<=warp_ids
            assert not {'main-foot-l','main-foot-r'} & warp_ids
        assert len([e for e in main.iter() if e.attrib.get('id','').endswith(('foot-l','foot-r'))])==2
    confident=deformation_at(pose_at(3.3));collapsed=deformation_at(pose_at(FLASH))
    assert confident['sy']>=1.1 and collapsed['sy']<=.72
    assert confident['sy']-collapsed['sy']>=.38
    assert pose_at(155/FPS)==pose_at(FLASH)
    report.update(revision=2,vanity_vertical_scale=confident['sy'],collapse_vertical_scale=collapsed['sy'],
                  collapse_horizontal_scale=collapsed['sx'],
                  body_scale_peak_to_collapse=round(max(d['sy'] for d in deformations)-collapsed['sy'],4),
                  feet_excluded_from_body_deformation=True,feet_geometry_fixed_all_frames=True,body_arms_face_warp_together=True,
                  unique_ids_all_frames=True,two_hands_all_frames=True,two_grounded_feet_all_frames=True,all_clip_references_resolved=True,
                  frozen_photo=True,original_rig_unchanged=True)
    (EP/'controle'/'audit_structure.json').write_text(json.dumps(report,indent=2))
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--stills',action='store_true');ap.add_argument('--workers',type=int,default=3)
    a=ap.parse_args();(EP/'cache').mkdir(exist_ok=True);(EP/'controle').mkdir(exist_ok=True)
    prepare_photo();report=audit();scale=.5 if a.preview else 1
    frames=EP/'frames'/('preview' if a.preview else 'final');frames.mkdir(parents=True,exist_ok=True)
    samples=[0,.9,2.2,3.3,4.5,5.5,6.25,6.5,6.75,7.65,9.6,10.6,11.6,12.6,13.8]
    indices=sorted({round(t*FPS) for t in samples}) if a.stills else range(FPS*DURATION)
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        list(pool.map(render_job,[(i,scale,str(frames)) for i in indices]))
    # Validate destinations after all workers finish: no shared inodes, no
    # frame overwritten through an old cache hardlink.
    for i in indices:
        data=svg_at(i/FPS).encode()
        key=hashlib.sha256(CACHE_VERSION.encode()+data+str(scale).encode()).hexdigest()
        dest=frames/f'{i:04d}.png'
        assert dest.stat().st_nlink==1,(i,'shared frame inode')
        assert dest.read_bytes()==(EP/'cache'/f'{key}.png').read_bytes(),(i,'frame/cache mismatch')
    board(frames,EP/'controle'/('planche_preview.png' if a.preview else 'planche_finale.png'))
    if a.stills: print(json.dumps(report));return
    tag='premier_montage' if a.preview else 'MOU_01_le_retardateur'
    mute=EP/f'{tag}_muet.mp4';final=EP/f'{tag}.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(frames/'%04d.png'),'-frames:v',str(FPS*DURATION),'-c:v','libx264','-threads','3','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mute)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(mute),'-i',str(EP/'sons/mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t','14','-movflags','+faststart',str(final)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
    (EP/'controle'/f'probe_{tag}.json').write_text(json.dumps(probe,indent=2))
    print(json.dumps({'file':str(final),**report}))
if __name__=='__main__': main()
