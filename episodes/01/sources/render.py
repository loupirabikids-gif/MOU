"""La dernière retouche — production SVG/CairoSVG/FFmpeg, sans service externe.
Run from any working directory; the input rig is the supplied mou_rig.py.
"""
from pathlib import Path
import argparse, base64, concurrent.futures, hashlib, io, json, math, os, re, subprocess, sys
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[3]
EP = ROOT/'episodes'/'01'
sys.path.insert(0,str(ROOT))
from animation import pose_at, motion_at, character_at, intention_at, deformation_at, contact_geometry
from mou_rig import PALETTE
import cairosvg
from PIL import Image, ImageDraw, ImageFont
INK=PALETTE['outline']
BG='#EEE6FA'
TIMELINE=json.loads((EP/'chronologie.json').read_text())
REVISION=int(TIMELINE['revision'])
FPS=int(TIMELINE['fps'])
DURATION=float(TIMELINE['duree_secondes'])
NFRAMES=round(FPS*DURATION)
W,H=TIMELINE['width'],TIMELINE['height']
FLASH=float(TIMELINE['flash_time'])
SAMPLES=[0,.8,1.25,1.75,2.8,3.6,4.4,5.4,6.25,FLASH,7.8,9.25,10.2,11.1,12.6]
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

def tap_geometry(t):
    """One continuous rig-style limb, shoulder beyond the cropped frame."""
    offset=260*(1-smooth((t-.10)/1.10))
    return [(1130+offset,2080+offset),(1130+offset,1770+offset),
            (780+offset,1495+offset),(614+offset,1464+offset)]

def tap_arm(t):
    # Reuse the original rig's cubic sampling and single semicircular mitten.
    from mou_rig import _cubic, _tangent
    controls=tap_geometry(t);left=[];right=[]
    for i in range(65):
        u=i/64;x,y=_cubic(controls,u);tx,ty=_tangent(controls,u)
        hand=smooth((u-.75)/.25);r=42+33*hand
        left.append((x-ty*r,y+tx*r));right.append((x+ty*r,y-tx*r))
    ex,ey=controls[-1];tx,ty=_tangent(controls,1)
    tip=[(ex+(-ty*math.cos(math.pi*j/24)+tx*math.sin(math.pi*j/24))*75,
          ey+(tx*math.cos(math.pi*j/24)+ty*math.sin(math.pi*j/24))*75) for j in range(1,25)]
    boundary=left+tip+list(reversed(right[:-1]))
    d='M'+' L'.join(f'{x:.3f} {y:.3f}' for x,y in boundary)
    return (f'<g id="tap-arm"><path data-part="hand" data-side="left" d="{d} Z" fill="{PALETTE["skin"]}"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="20.8" stroke-linejoin="round" stroke-linecap="round"/></g>')

def phone_insert(result=False,t=0):
    a=[f'<g id="phone"><rect x="190" y="220" width="700" height="1480" rx="90" fill="{INK}"/>',
       '<rect x="209" y="239" width="662" height="1442" rx="72" fill="#644565"/>',
       '<rect x="226" y="325" width="628" height="1255" rx="30" fill="#E1D1F2"/>',
       '<circle cx="540" cy="278" r="16" fill="#B9A4CC"/><circle cx="540" cy="278" r="7" fill="#251029"/>']
    if result:
        a += ['<rect x="242" y="378" width="596" height="940" rx="8" fill="#FFFDFD"/>',
              f'<image x="250" y="390" width="580" height="899" href="data:image/png;base64,{PHOTO}"/>',
              '<rect x="491" y="1457" width="98" height="64" rx="10" fill="#FFFDFD"/>',
              f'<path d="M503 1507 L528 1481 L552 1502 L572 1489" fill="none" stroke="{INK}" stroke-width="6"/>']
    else:
        a += [f'<path d="M415 605 H475 L493 580 H573 L594 605 H665 V770 H415 Z" fill="none" stroke="{INK}" stroke-width="16" stroke-linejoin="round"/>',
              f'<circle cx="540" cy="690" r="50" fill="none" stroke="{INK}" stroke-width="14"/>',
              f'<circle cx="540" cy="1030" r="107" fill="none" stroke="{INK}" stroke-width="10"/>',
              f'<path d="M521 898 H559 M540 898 V919 M611 944 L627 928" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>',
              f'<text x="540" y="1081" text-anchor="middle" fill="{INK}" font-family="DejaVu Sans" font-weight="bold" font-size="142">5</text>',
              '<circle cx="540" cy="1450" r="92" fill="none" stroke="#FFFDFD" stroke-width="10"/>',
              f'<circle cx="540" cy="1450" r="72" fill="{PALETTE["skin"] if t>=1.20 else "#FFFDFD"}"/>',
              tap_arm(t)]
    return ''.join(a)+'</g>'

def svg_at(t):
    a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="1080" height="1920" fill="{BG}"/>',
       f'<text x="78" y="174" font-family="DejaVu Sans" font-weight="bold" font-size="76" letter-spacing="-5" fill="{INK}">MOU</text>']
    if t<34/FPS:
        a.append(phone_insert(False,t))
    elif 7<=t<8.8:
        a.append('<g id="result-closeup" transform="translate(540 960) scale(1.4) translate(-540 -960)">'+phone_insert(True,t)+'</g>')
    else:
        a += ['<path d="M110 1600 V880 C110 520 320 410 540 410 C760 410 970 520 970 880 V1600 Z" fill="#E8DBF4"/>',
              '<ellipse cx="540" cy="1580" rx="880" ry="125" fill="#E3D5EF"/>',
              '<ellipse cx="540" cy="1548" rx="352" ry="25" fill="#CCB7E0"/>',
              f'<g id="character" transform="translate(540 1540) scale(3) translate(-200 -450)">{puppet(t,"main")}</g>']
        if t<FLASH:
            a += ['<path d="M92 438 V310 H220 M860 310 H988 V438 M92 1530 V1658 H220 M860 1658 H988 V1530" fill="none" stroke="#AA8DBF" stroke-width="8" stroke-linecap="round"/>']
            digit=next((str(v['number']) for v in TIMELINE['countdown'] if v['time']<=t<v['time']+1),None)
            if digit:
                a += [f'<circle cx="885" cy="379" r="87" fill="{INK}"/>',
                      f'<text x="885" y="418" text-anchor="middle" fill="#FFFDFD" font-family="DejaVu Sans" font-weight="bold" font-size="110">{digit}</text>']
    if FLASH<=t<FLASH+3/FPS:
        op=[.94,.65,.22][min(2,round((t-FLASH)*FPS))]
        a.append(f'<rect id="flash" width="1080" height="1920" fill="#FFFDF9" opacity="{op}"/>')
    return ''.join(a)+'</svg>'

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
    samples=SAMPLES
    b=Image.new('RGB',(1500,1725),BG);d=ImageDraw.Draw(b)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),14)
    for j,t in enumerate(samples):
        im=Image.open(Path(frames)/f'{round(t*FPS):04d}.png').convert('RGB'); im.thumbnail((294,523))
        x=(j%5)*300+(300-im.width)//2;y=(j//5)*575
        b.paste(im,(x,y)); d.text(((j%5)*300+14,y+530),f'{t:.2f} s',font=font,fill=INK)
        d.text(((j%5)*300+14,y+552),intention_at(t),font=font,fill=INK)
    b.save(out)

def audit():
    rig_hash=hashlib.sha256((ROOT/'mou_rig.py').read_bytes()).hexdigest()
    assert rig_hash=='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'
    fixed_feet=None
    gaps=[]
    for i in range(NFRAMES):
        t=i/FPS;p=pose_at(t);data=svg_at(t);root=ET.fromstring(data)
        ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
        assert len(ids)==len(set(ids)),(t,'duplicate IDs')
        assert all(ref in ids for ref in re.findall(r'url\(#([^)]*)\)',data)),(t,'missing clip')
        avatar=ET.fromstring('<svg>'+puppet(t,'audit')+'</svg>')
        hands=[e for e in avatar.iter() if e.attrib.get('data-part')=='hand']
        assert len(hands)==2,(t,'puppet hands')
        assert all(math.isfinite(v) for v in p.values())
        assert p['lift_l']==0 and p['lift_r']==0
        feet=[ET.tostring(e) for e in avatar.iter() if e.attrib.get('id') in {'audit-foot-l','audit-foot-r'}]
        assert len(feet)==2
        if fixed_feet is None:fixed_feet=feet
        assert feet==fixed_feet,(t,'feet changed')
        geom=contact_geometry(p)
        for side in ('left','right'):
            if geom[side]['in_contact']:
                gaps.append(geom[side]['contact_gap'])
                assert geom[side]['contact_gap']<1e-6,(t,side,'cheek contact')
        expected=1 if t<34/FPS else 0 if 7<=t<8.8 else 2
        assert sum(e.attrib.get('data-part')=='hand' for e in root.iter())==expected
    assert [e['frame'] for e in TIMELINE['countdown']]==[34,58,82,106,130]
    assert pose_at(FLASH-1/FPS)!=pose_at(FLASH),'last retouch must still move into capture'
    assert pose_at(12.5)['smile']<=.05
    assert all(contact_geometry(pose_at(86/FPS))[side]['in_contact'] for side in ('left','right'))
    assert all(contact_geometry(pose_at(FLASH))[side]['in_contact'] for side in ('left','right'))
    from mou_rig import _tangent
    controls=tap_geometry(30/FPS);tx,ty=_tangent(controls,1)
    tip=(controls[-1][0]+75*tx,controls[-1][1]+75*ty)
    tap_error=math.dist(tip,(540,1450));assert tap_error<1
    report={'revision':REVISION,'original_rig_sha256':rig_hash,'original_rig_unchanged':True,
            'frames':NFRAMES,'fps':FPS,'duration':DURATION,'flash_frame':TIMELINE['flash_frame'],
            'photo_pose_time':FLASH,'photo_sha256':hashlib.sha256((EP/'sources/photo_capturee.png').read_bytes()).hexdigest(),
            'unique_ids_all_frames':True,'two_hands_in_puppet_all_frames':True,
            'visible_hand_count_matches_framing':True,'feet_geometry_fixed_all_frames':True,
            'all_clip_references_resolved':True,'countdown_regular_seconds':True,
            'last_retouch_moves_into_capture':True,'photo_absent_before_capture':True,
            'cheek_contact_frames_sides':len(gaps),'cheek_contact_max_gap_local':max(gaps),
            'first_rubbing_both_hands_in_contact':True,'tap_tip_error_pixels':tap_error,
            'limits':'Structure et source partagée ; lisibilité et contacts examinés séparément sur rendu.'}
    (EP/'controle'/'audit_structure.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--stills',action='store_true');ap.add_argument('--workers',type=int,default=3)
    a=ap.parse_args();(EP/'cache').mkdir(exist_ok=True);(EP/'controle').mkdir(exist_ok=True)
    prepare_photo();report=audit();scale=.5 if a.preview else 1
    frames=EP/'frames'/('preview' if a.preview else 'final');frames.mkdir(parents=True,exist_ok=True)
    samples=SAMPLES
    indices=sorted({round(t*FPS) for t in samples}) if a.stills else range(NFRAMES)
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
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(frames/'%04d.png'),'-frames:v',str(NFRAMES),'-c:v','libx264','-threads','3','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(mute)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(mute),'-i',str(EP/'sons/mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(DURATION),'-movflags','+faststart',str(final)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(final)]))
    (EP/'controle'/f'probe_{tag}.json').write_text(json.dumps(probe,indent=2))
    print(json.dumps({'file':str(final),**report}))
if __name__=='__main__': main()
