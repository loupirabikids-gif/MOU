"""Prepare original MOU vector poses and static plates for Blender.

Character paths come from the unchanged 2D rig. SVG clips are resolved into
real contours before Blender, instead of relying on its incomplete SVG import.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import cairosvg

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
REFERENCE = ROOT/'episodes/03/etude_grain_v1'
spec = importlib.util.spec_from_file_location('original_mou_grain', REFERENCE/'sources/etude.py')
study = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = study
spec.loader.exec_module(study)
ET.register_namespace('', 'http://www.w3.org/2000/svg')
NS = '{http://www.w3.org/2000/svg}'
# Keep the native contours at the three topology-sensitive transitions.
# Sparse polygon morphs there folded the mouth/arm and crossed the sink palm.
FRAMES = sorted(set([1,4,7,9,10,12,13,14,16,18,19,23,26,32,37,48,49,54,62,63,66,71,75,80,81,82,91,99,104,
          105,108,111,112,113,116,117,118,120] + list(range(76,80)) + list(range(92,99)) + [114,115]))


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.name == 'vector_frames.json':
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(',',':'))+'\n')
    else:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def svg_root():
    return ET.Element(NS+'svg', {'width':'1080','height':'1920','viewBox':'0 0 1080 1920'})


def find(root, name):
    return next((e for e in root.iter() if e.attrib.get('id') == name), None)


def group(name, role, fragment=''):
    node = ET.Element(NS+'g', {'id':name, 'data-role':role})
    if fragment:
        wrapper = ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg">'+fragment+'</svg>')
        for child in wrapper:
            node.append(child)
    return node


def actor_svg(t):
    full = ET.fromstring(study.svg_at(t))
    out = svg_root()
    for node in full:
        if node.tag.rsplit('}',1)[-1] == 'defs':
            out.append(copy.deepcopy(node))
    if t < 4.30:
        for identifier, role in [('mou-corps','body'), ('mou-bras','arms')]:
            node = copy.deepcopy(find(full, identifier))
            node.attrib['data-role'] = role
            out.append(node)
        spoon = study.spoon_at(t) or {'grip':study.PARK_GRIP,'bowl':study.PARK_BOWL}
        out.append(group('cuillere-action','prop', study.ART.spoon_svg(spoon['grip'],spoon['bowl'])))
        grain = find(full, 'grain-sel')
        node = group('grain-acteur','grain')
        if grain is not None:
            node.append(copy.deepcopy(grain))
        out.append(node)
        state = study.state_at(t)
        for j, start in enumerate((.12,.25,.38,.51)):
            node = group(f'sel-verse-{j}','prop')
            if start <= t < start+.24:
                u = study.progress(t,start,start+.24)
                hx,hy = state['hands']['left']
                x,y = study.point((hx,hy+8.),(293.+13.*j,1305.),u)
                node.append(ET.Element(NS+'ellipse',{'cx':str(x),'cy':str(y),'rx':'3','ry':'4',
                            'fill':'#FFFDF3','stroke':'#B5A7AA','stroke-width':'1'}))
            out.append(node)
    else:
        for index, node in enumerate(full):
            identifier = node.attrib.get('id','')
            if node.tag.rsplit('}',1)[-1] == 'defs' or identifier in ('fond-cuisine','lavabo-profond'):
                continue
            node = copy.deepcopy(node)
            if not identifier:
                node.attrib['id'] = 'contour-main-lavabo'
            node.attrib['data-role'] = 'grain' if 'grain-' in identifier else 'sink'
            out.append(node)
    return ET.tostring(out, encoding='unicode')


def plates():
    r, art = study.R, study.ART
    root = '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="2400" viewBox="0 0 1080 2400">'
    back = root+r.DEFS+r.FLOOR_EXTENSION+r.BACKGROUND+art.lever_svg(0.)+'</svg>'
    s = study.state_at(.45)
    fore = (root+r.DEFS+r.GROUPS['ilot-cuisine']+r.PROPS_WITHOUT_ROLL+art.roll_svg(s['roll'])
            +r.cooking_fx.food_svg(1.,s,art)+art.tomato_dish_svg(occupied=False)
            +art.tomato_svg(*study.A.TOMATO_START)+art.carrot_svg(s['carrot'])
            +art.salt_svg(s['salt'],s['reference_clock'],layer='bowl')
            +art.bin_svg(0,None,None)+'</svg>')
    macro = ET.fromstring(study.svg_at(4.50))
    for node in list(macro):
        if node.tag.rsplit('}',1)[-1] != 'defs' and node.attrib.get('id') not in ('fond-cuisine','lavabo-profond'):
            macro.remove(node)
    folder = EP/'assets/plates'
    for name, svg, size in [('wide_background',back,(1080,2400)),('wide_foreground',fore,(1080,2400)),
                            ('sink_background',ET.tostring(macro,encoding='unicode'),(1080,1920))]:
        (folder/(name+'.svg')).write_text(svg)
        cairosvg.svg2png(bytestring=svg.encode(),write_to=str(folder/(name+'.png')),
                        output_width=size[0],output_height=size[1])
    dump(folder/'plates.json', [
        {'path':'assets/plates/wide_background.png','world':[0,0,1080,2400],'shot':'wide','role':'back','order':-1000},
        {'path':'assets/plates/wide_foreground.png','world':[0,0,1080,2400],'shot':'wide','role':'front','order':500},
        {'path':'assets/plates/sink_background.png','world':[0,925,270,480],'shot':'sink','role':'back','order':-1000},
    ])


def frame_record(frame):
    t = (frame-1)/24.
    s = study.state_at(t)
    shot = 'wide' if t < 4.30 else 'sink'
    spoon = study.spoon_at(t) or {'grip':study.PARK_GRIP,'bowl':study.PARK_BOWL}
    anchors = {'mainleft':list(s['hands']['left']), 'mainright':list(s['hands']['right']),
               'left':list(s['hands']['left']), 'right':list(s['hands']['right']),
               'spoon_grip':list(spoon['grip']), 'spoon_bowl':list(spoon['bowl']),
               'spoon_held':study.spoon_at(t) is not None}
    if shot == 'sink':
        g = study.R.sink.geometry_at(study.sink_clock(t),s,study.A)
        anchors['sink_tip'] = list(g['tip'])
    return {'frame':frame,'t':t,'shot':shot,'anchors':anchors,
            'study_phase':s.get('study_phase','')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vectorize',action='store_true')
    parser.add_argument('--skip-film-check',action='store_true',
                        help='For the source ZIP, which omits previous MP4s; Python sources remain checked')
    args = parser.parse_args()
    for name, expected in json.loads((EP/'controle/baseline.json').read_text()).items():
        if args.skip_film_check and Path(name).suffix == '.mp4':
            continue
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    plates()
    records = []
    for frame in FRAMES:
        record = frame_record(frame)
        name = f'frame_{frame:04d}.svg'
        svg = actor_svg(record['t'])
        (EP/'assets/vector_poses'/name).write_text(svg)
        record['svg'] = 'assets/vector_poses/'+name
        records.append(record)
    dump(EP/'assets/pose_bank.json', {'canvas':[1080,1920],'fps':24,'duration':5,
          'frames':records,'key_poses':{'assurance':12,'resistance':54,'cede':99}})
    if not args.vectorize:
        print(json.dumps({'actor_svgs':len(records),'plates':3}));return
    sys.path.insert(0,str(EP/'sources'))
    from vectorize import vectorize
    role_base = {'body':0,'prop':600,'arms':700,'sink':0,'grain':950}
    for record in records:
        data = vectorize((EP/record['svg']).read_text(),EP/'assets/images')
        counts = {}
        for entity in data['curves']+data['images']:
            role = entity.get('role','body')
            entity['order'] = role_base[role]+counts.get(role,0)
            counts[role] = counts.get(role,0)+1
            entity['id'] = record['shot']+'__'+entity['id']
            entity['shot'] = record['shot']
            if 'path' in entity and Path(entity['path']).is_absolute():
                entity['path'] = str(Path(entity['path']).relative_to(EP))
        record.update(data)
        print('vectorized',record['frame'],len(data['curves']),flush=True)
    dump(EP/'assets/vector_frames.json', {'canvas':[1080,1920],'fps':24,'duration':5,
         'frames':records,'key_poses':{'assurance':12,'resistance':54,'cede':99}})


if __name__ == '__main__':
    main()
