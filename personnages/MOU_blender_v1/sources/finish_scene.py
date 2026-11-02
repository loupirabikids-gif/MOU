"""Finish action markers and flat water transparency in the editable scene."""
from pathlib import Path
import json
import sys
import bpy

EP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(EP/'sources'))
from beats import compile_beats

for beat in compile_beats():
    label='ACTION_'+beat['action']
    existing=bpy.context.scene.timeline_markers.get(label)
    if existing:
        bpy.context.scene.timeline_markers.remove(existing)
    bpy.context.scene.timeline_markers.new(label,frame=beat['frame_start'])
bpy.context.scene['action_clock']='Named actions and held thoughts; five seconds, 24 fps.'
payload=json.loads((EP/'assets/vector_frames.json').read_text())
flat_water={c['id'] for frame in payload['frames'] for c in frame['curves']
            if c['id'].startswith('sink__') and c['rgba'][3] < 1.}
changed=[]
for obj in bpy.context.scene.objects:
    if obj.get('source_id') in flat_water:
        for material in obj.data.materials:
            material.surface_render_method='BLENDED'
        changed.append(obj.name)
bpy.context.scene['flat_water_transparency']='BLENDED; flat 2D overlays without stochastic dots'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
print('MOU_FINISH_SAVED='+json.dumps({'flat_water_material_objects':changed}),flush=True)
