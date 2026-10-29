"""Real Blender 4.3 SVG/render/camera probe. No project production file is changed."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT=ROOT/'work/test_outils_pro/blender'
REPORT=ROOT/'recherche/2026-10-29_professionnel/outils'


def reset():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.render.engine='BLENDER_EEVEE_NEXT'
    scene.render.resolution_x=400;scene.render.resolution_y=500
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.film_transparent=False
    scene.view_settings.view_transform='Standard'
    scene.view_settings.look='None'
    scene.view_settings.exposure=0.;scene.view_settings.gamma=1.
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1.,1.,1.,1.)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
    return scene


def camera_fit(objects):
    bpy.context.view_layer.update()
    points=[obj.matrix_world@Vector(corner) for obj in objects for corner in obj.bound_box]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    centre=(lo+hi)*.5;span=hi-lo
    data=bpy.data.cameras.new('ProbeCamera');obj=bpy.data.objects.new('ProbeCamera',data)
    bpy.context.collection.objects.link(obj);data.type='ORTHO'
    if span.z<max(span.x,span.y)*.02:
        obj.location=(centre.x,centre.y,centre.z+max(span.x,span.y)*4.)
        obj.rotation_euler=(0.,0.,0.);data.ortho_scale=span.y
    else:
        obj.location=(centre.x,centre.y-max(span.x,span.z)*4.,centre.z)
        obj.rotation_euler=(math.pi/2.,0.,0.);data.ortho_scale=span.z
    bpy.context.scene.camera=obj
    return {'bbox_min':list(lo),'bbox_max':list(hi),'camera_scale':data.ortho_scale,
            'camera_location':list(obj.location),'camera_euler':list(obj.rotation_euler)}


results={'blender_version':bpy.app.version_string,'background':bpy.app.background,'imports':[]}
for mode in ('gp','curves'):
    try:
        scene=reset()
        op=bpy.ops.wm.grease_pencil_import_svg if mode=='gp' else bpy.ops.import_curve.svg
        result=op(filepath=str(OUT/'mou_native.svg'))
        imported=list(scene.objects)
        if mode=='curves':
            # Supply deterministic SVG paint order, without altering a path.
            for index,obj in enumerate(imported):
                obj.location.z+=index*1.e-6
                for material in obj.data.materials:
                    color=tuple(material.diffuse_color)
                    material.use_nodes=True
                    tree=material.node_tree;tree.nodes.clear()
                    output=tree.nodes.new('ShaderNodeOutputMaterial')
                    emission=tree.nodes.new('ShaderNodeEmission')
                    emission.inputs['Color'].default_value=color
                    tree.links.new(emission.outputs[0],output.inputs['Surface'])
        entry={'mode':mode,'result':sorted(result),'objects':len(imported),
               'object_types':sorted(set(o.type for o in imported)),**camera_fit(imported)}
        scene.render.filepath=str(OUT/f'mou_{mode}.png')
        bpy.ops.render.render(write_still=True)
        entry['rendered_png']=scene.render.filepath
        results['imports'].append(entry)
    except Exception as error:
        results['imports'].append({'mode':mode,'error':repr(error)})

# Faithful raster reference as a real 2D plane: test camera/keyframe interchange.
scene=reset()
vertices=[(0.,0.,0.),(400.,0.,0.),(400.,500.,0.),(0.,500.,0.)]
mesh=bpy.data.meshes.new('NativeMouPlane');mesh.from_pydata(vertices,[],[(0,1,2,3)])
mesh.uv_layers.new(name='UVMap')
for polygon in mesh.polygons:
    for index,loop in enumerate(polygon.loop_indices):
        mesh.uv_layers.active.data[loop].uv=((0.,0.),(1.,0.),(1.,1.),(0.,1.))[index]
plane=bpy.data.objects.new('NativeMouPlane',mesh);bpy.context.collection.objects.link(plane)
material=bpy.data.materials.new('NativePixels');material.use_nodes=True
nodes=material.node_tree.nodes;nodes.clear()
output=nodes.new('ShaderNodeOutputMaterial');emission=nodes.new('ShaderNodeEmission')
texture=nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(OUT/'mou_cairo.png'))
texture.interpolation='Closest'
material.node_tree.links.new(texture.outputs['Color'],emission.inputs['Color'])
material.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
plane.data.materials.append(material)
camera=bpy.data.cameras.new('Orthographic2D');cam=bpy.data.objects.new('Orthographic2D',camera)
bpy.context.collection.objects.link(cam);cam.location=(200.,250.,1000.)
camera.type='ORTHO';camera.ortho_scale=500.;scene.camera=cam
scene.render.filepath=str(OUT/'mou_image_plane.png');bpy.ops.render.render(write_still=True)
# Deliberate hold, then a composition change with explicit easing handles.
scene.render.fps=24;scene.frame_start=1;scene.frame_end=48
for frame,scale,location in [(1,500.,(200.,250.,1000.)),(18,500.,(200.,250.,1000.)),
                            (26,300.,(215.,270.,1000.)),(48,300.,(215.,270.,1000.))]:
    camera.ortho_scale=scale;camera.keyframe_insert('ortho_scale',frame=frame)
    cam.location=location;cam.keyframe_insert('location',frame=frame)
for owner in (camera,cam):
    for curve in owner.animation_data.action.fcurves:
        for key in curve.keyframe_points:
            key.interpolation='BEZIER';key.handle_left_type='AUTO_CLAMPED';key.handle_right_type='AUTO_CLAMPED'
scene.frame_set(30);scene.render.filepath=str(OUT/'mou_camera_closeup.png');bpy.ops.render.render(write_still=True)
results['image_plane']={'source':'mou_cairo.png','camera':'orthographic','keyframes':[1,18,26,48],
                        'holds':[[1,18],[26,48]],'closeup_frame':30,'curves':'Bezier AUTO_CLAMPED',
                        'geometry_changed':False,'note':'Image plane preserves native art but is not a new facial rig.'}
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mou_camera_probe.blend'))
(REPORT/'blender_test.json').write_text(json.dumps(results,indent=2)+'\n')
print('MOU_BLENDER_TEST='+json.dumps(results))
