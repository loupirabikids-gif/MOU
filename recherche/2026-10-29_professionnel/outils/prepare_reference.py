"""Prepare the unchanged native character as a local technical probe input."""
from pathlib import Path
import hashlib
import json
import sys

import cairosvg

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
sys.path.insert(0,str(ROOT))
from mou_rig import DEFAULT_POSE, character_fragment

OUT=ROOT/'work/test_outils_pro/blender'
OUT.mkdir(parents=True,exist_ok=True)
rig=ROOT/'mou_rig.py';before=hashlib.sha256(rig.read_bytes()).hexdigest()
pose={**DEFAULT_POSE,'arm_clasp':1.,'eye_open_l':.40,'eye_open_r':.60,
      'pupil_x':.85,'pupil_y':-.15,'brow_l':.65,'brow_r':.20,'smile':.15}
svg=('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="500" viewBox="0 0 400 500">'
     '<rect width="400" height="500" fill="#FFF8ED"/>'
     +character_fragment(pose,uid='import-test')+'</svg>')
(OUT/'mou_native.svg').write_text(svg)
(OUT/'mou_cairo.png').write_bytes(cairosvg.svg2png(bytestring=svg.encode()))
assert before==hashlib.sha256(rig.read_bytes()).hexdigest()
print(json.dumps({'rig_unchanged':True,'rig_sha256':before,'work_directory':str(OUT)}))
