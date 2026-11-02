"""Render the editable Blender curves, without altering the saved scene.

blender -b MOU_blender_v1.blend --python-exit-code 1 \
  --python sources/render_frames.py -- --width 1080 --output work/hd
"""
from pathlib import Path
import argparse
import json
import sys
import time

import bpy

EP = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--width', type=int, default=1080)
parser.add_argument('--samples', type=int, default=8)
parser.add_argument('--output', type=Path, default=EP/'work/hd')
parser.add_argument('--frames', help='Comma-separated frame numbers; default: all 120')
parser.add_argument('--resume', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
scene = bpy.context.scene
assert scene.frame_start == 1 and scene.frame_end == 120 and scene.render.fps == 24
assert args.width > 0 and args.width % 9 == 0, 'Use a width divisible by 9'
scene.render.resolution_x = args.width
scene.render.resolution_y = args.width*16//9
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '8'
scene.render.film_transparent = False
scene.eevee.taa_render_samples = args.samples
frames = [int(value) for value in args.frames.split(',')] if args.frames else range(1,121)
args.output.mkdir(parents=True, exist_ok=True)
started = time.time()
rendered = []
for frame in frames:
    assert 1 <= frame <= 120
    target = args.output/f'{frame:04d}.png'
    if not (args.resume and target.is_file()):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
    rendered.append(frame)
    print('MOU_RENDER_FRAME='+str(frame), flush=True)
(args.output/'render.json').write_text(json.dumps({
    'blender':bpy.app.version_string, 'blend':Path(bpy.data.filepath).name,
    'width':scene.render.resolution_x, 'height':scene.render.resolution_y,
    'fps':scene.render.fps, 'frames':rendered, 'samples':args.samples,
    'elapsed_seconds':round(time.time()-started,2),
    'renderer':'Blender native editable CURVE and shape keys',
}, indent=2)+'\n')
