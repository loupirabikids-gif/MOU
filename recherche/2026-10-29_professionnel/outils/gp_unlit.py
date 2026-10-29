import bpy,json,math
from pathlib import Path
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT=ROOT/'work/test_outils_pro/blender'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=400;scene.render.resolution_y=500;scene.render.resolution_percentage=100
scene.render.dither_intensity=0.;scene.view_settings.view_transform='Standard';scene.view_settings.look='None'
bpy.ops.wm.grease_pencil_import_svg(filepath=str(OUT/'mou_native.svg'))
object=bpy.context.object;changes=[]
for layer in object.data.layers:
    if hasattr(layer,'use_lights'):
        layer.use_lights=False;changes.append({'layer':layer.name,'use_lights':False})
camera=bpy.data.cameras.new('camera');cam=bpy.data.objects.new('camera',camera);scene.collection.objects.link(cam)
camera.type='ORTHO';camera.ortho_scale=1.3229166269302368;cam.location=(0.,-5.291666507720947,0.)
cam.rotation_euler=(math.pi/2.,0.,0.);scene.camera=cam
scene.render.filepath=str(OUT/'mou_gp_unlit.png');bpy.ops.render.render(write_still=True)
(OUT/'gp_unlit.json').write_text(json.dumps({'changes':changes,'layers':[layer.name for layer in object.data.layers]},indent=2)+'\n')
print('MOU_UNLIT='+json.dumps(changes))
