"""Check deliverable consistency and preserve the production MOU model."""
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import cairosvg

LIB=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(LIB/'sources'))
import render
import animer

RIG_SHA='7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    root=render.ROOT;data=render.catalogue();assert len(data['poses'])==data['pose_count']
    assert sha(root/'mou_rig.py')==RIG_SHA
    for filename in ('sources_images.json','sources_transitions.json'):
        frozen=json.loads((LIB/'controle'/filename).read_text())['frozen_sources_sha256']
        for path,digest in frozen.items():assert sha(root/path)==digest,(path,'Changed after rendering')
    ids=set();face_hashes=set();checks=[]
    for p in data['poses']:
        assert p['id'] not in ids;ids.add(p['id'])
        path=LIB/'exports/svg'/f'{p["id"]}.svg';doc=ET.fromstring(path.read_text())
        # Namespace-aware comparisons use serialized canonical elements.
        all_ids=[n.attrib['id'] for n in doc.iter() if 'id' in n.attrib]
        assert len(all_ids)==len(set(all_ids)),p['id']
        for reference in re.findall(r'url\(#([^)]*)\)',path.read_text()):assert reference in all_ids,(p['id'],reference)
        elements={n.attrib.get('id'):n for n in doc.iter() if 'id' in n.attrib}
        assert len([n for n in doc.iter() if n.attrib.get('data-part')=='hand'])==2
        assert {'body','arm-left','arm-right','foot-l','foot-r','face','mouth'}.issubset(elements)
        # Geometry comparison ignores XML namespace serialization details.
        baseline=ET.fromstring('<svg>'+render.actor({},'baseline')+'</svg>')
        expected={n.attrib.get('id'):n for n in baseline.iter() if 'id' in n.attrib}
        def strip_namespace(n):
            value={'tag':n.tag.split('}')[-1],'attributes':n.attrib,'children':[strip_namespace(c) for c in n]}
            return value
        for key in ('body','arm-left','arm-right','foot-l','foot-r'):
            assert strip_namespace(elements[key])==strip_namespace(expected[key]),(p['id'],key)
        # All differences must originate in the face adapter, not the model.
        face_hashes.add(sha(LIB/'exports/png'/f'{p["id"]}.png'))
        checks.append({'id':p['id'],'svg_sha256':sha(path),'png_sha256':sha(LIB/'exports/png'/f'{p["id"]}.png')})
    assert len(face_hashes)==len(data['poses']),'Duplicate rendered poses require review'
    for i in range(len(animer.SCENES)*animer.PER_SCENE):
        s=animer.svg_at(i);doc=ET.fromstring(s)
        assert sum(n.attrib.get('data-part')=='hand' for n in doc.iter())==2
        assert sum(n.attrib.get('id')=='mouth' for n in doc.iter())==1
        ids_here=[n.attrib['id'] for n in doc.iter() if 'id' in n.attrib]
        assert len(ids_here)==len(set(ids_here))
        assert all(ref in ids_here for ref in re.findall(r'url\(#([^)]*)\)',s))
    video=LIB/'MOU_transitions_visage.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]))
    assert len(probe['streams'])==1
    v=probe['streams'][0];assert [v['width'],v['height'],v['r_frame_rate'],v['nb_read_frames']]==[720,960,'24/1','432']
    assert abs(float(v['duration'])-18.)<.001
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    samples=[i*72+j for i in range(6) for j in (5,16,27,38,59,69)]
    fresh_checks=[]
    for k,index in enumerate(samples,1):
        actual=np.asarray(Image.open(LIB/'controle'/f'transition_{k:02d}.png').convert('RGB'))
        fresh=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=animer.svg_at(index).encode()))).convert('RGB'))
        difference=np.abs(actual.astype(np.int16)-fresh.astype(np.int16))
        full=float(difference.mean());mouth=float(difference[512:662,270:475].mean())
        assert full<3. and mouth<3.,(index,full,mouth,'Encoded frame does not match current face')
        fresh_checks.append({'frame':index,'mean_abs_rgb_error':full,'mouth_mean_abs_rgb_error':mouth})
    html=(LIB/'galerie.html').read_text();script=re.search(r'<script>(.*)</script>',html,re.S)[1]
    checkfile=root/'work/expressions_gallery_check.js';checkfile.write_text(script)
    subprocess.run(['node','--check',str(checkfile)],check=True)
    protected=json.loads((LIB/'controle/production_reference.json').read_text())
    available_production={};unavailable_production=[]
    for path,digest in protected.items():
        if (root/path).is_file():
            assert sha(root/path)==digest,(path,'Production changed during library work')
            available_production[path]=digest
        else:
            # A standalone expressions ZIP deliberately omits old full episodes.
            unavailable_production.append(path)
    report={'status':'passed','rig_sha256':RIG_SHA,'poses':len(data['poses']),'families':len(data['families']),'images_unique':len(face_hashes),
            'native_body_feet_arms_identical':True,'two_native_hands_all_full_body_states':True,
            'episode_sources_video_and_audio_unchanged':available_production,
            'external_episode_files_not_in_this_checkout':unavailable_production,
            'single_clipped_face_during_432_transition_frames':True,
            'video':{'sha256':sha(video),'dimensions':[720,960],'fps':24,'frames':432,'duration':18.,'audio':False,'full_decode_passed':True},
            'decoded_video_vs_uncached_cairo':fresh_checks,
            'gallery_embedded_javascript_syntax':'passed','rendered_poses':checks,
            'limits':'Technical checks do not certify emotional interpretation or audience comprehension. Independent visual critique is separate.'}
    (LIB/'controle/audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','poses','families','native_body_feet_arms_identical')}))


if __name__=='__main__':main()
