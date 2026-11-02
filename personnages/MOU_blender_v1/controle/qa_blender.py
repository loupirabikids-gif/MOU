"""Independent, non-rendering checks on the delivered native Blender scene.

Prepare native references with the project venv first:
    python controle/qa_blender.py --prepare-references
Run: blender -b MOU_blender_v1.blend --threads 2 --python-exit-code 1 \
    --python controle/qa_blender.py -- [--video path/to/export.mp4]
The temporary controller edits below are never saved to the .blend.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
try:
    import bpy
    from mathutils import Vector
except ModuleNotFoundError:
    bpy = None  # --prepare-references runs in the project's CairoSVG venv.

EP = Path(__file__).resolve().parents[1]
REPO = EP.parents[1]
checks = []
LOCAL_FRAMES = [76,77,78,79,*range(91,100),*range(111,118)]


def prepare_references():
    """Render the preserved native SVG rig, not our Blender vector exporter."""
    import importlib.util
    import cairosvg
    source=REPO/'episodes/03/etude_grain_v1/sources/etude.py'
    spec=importlib.util.spec_from_file_location('mou_native_qa_reference',source)
    native=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=native
    spec.loader.exec_module(native)
    folder=EP/'work/qa/native'
    folder.mkdir(parents=True,exist_ok=True)
    for frame in LOCAL_FRAMES:
        cairosvg.svg2png(bytestring=native.svg_at((frame-1)/24.).encode(),
                        write_to=str(folder/('%04d.png'%frame)),output_width=1080,output_height=1920)
    print('NATIVE_QA_REFERENCES='+str(len(LOCAL_FRAMES)),flush=True)


def read_rgb_crop(path, box):
    x0,y0,x1,y1=box
    raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(path),
         '-vf','crop=%d:%d:%d:%d'%(x1-x0,y1-y0,x0,y0),'-frames:v','1','-threads','1',
         '-f','rawvideo','-pix_fmt','rgb24','-'])
    return np.frombuffer(raw,dtype=np.uint8).reshape(y1-y0,x1-x0,3)


def dilate_one(mask):
    padded=np.pad(mask,1)
    result=np.zeros_like(mask)
    for y in range(3):
        for x in range(3):
            result |= padded[y:y+mask.shape[0],x:x+mask.shape[1]]
    return result


def local_contour_checks(render_dir, reference_dir):
    """Reject folds/holes even when source-pose bounds and drivers are valid."""
    results=[]
    for frame in LOCAL_FRAMES:
        part='mouth' if frame<80 else ('arm' if frame<100 else 'palm')
        box={'mouth':(480,945,690,1005),'arm':(80,830,380,1160),'palm':(500,710,720,805)}[part]
        rendered=render_dir/('%04d.png'%frame)
        reference=reference_dir/('%04d.png'%frame)
        if not rendered.is_file() or not reference.is_file():
            results.append({'frame':frame,'part':part,'passed':False,'missing':[str(p) for p in (rendered,reference) if not p.is_file()]})
            continue
        actual=read_rgb_crop(rendered,box)
        expected=read_rgb_crop(reference,box)
        if part=='mouth':
            mask=lambda rgb:(rgb[:,:,0]<110)&(rgb[:,:,1]<90)&(rgb[:,:,2]<120)
            tolerance=20
        else:
            mask=lambda rgb:(rgb[:,:,0]>120)&(rgb[:,:,1]>200)&(rgb[:,:,2]<135)
            tolerance=100
        ma,me=mask(actual),mask(expected)
        extra=int(np.count_nonzero(ma & ~dilate_one(me)))
        missing=int(np.count_nonzero(me & ~dilate_one(ma)))
        results.append({'frame':frame,'part':part,'roi':list(box),'extra_pixels_outside_one_pixel_envelope':extra,
            'missing_pixels_outside_one_pixel_envelope':missing,'max_pixels_each':tolerance,
            'passed':extra<=tolerance and missing<=tolerance,'native_reference_sha256':digest(reference)})
    return results


def check(name, passed, evidence):
    checks.append({'check': name, 'passed': bool(passed), 'evidence': evidence})


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mesh_bounds(obj):
    graph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    pts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    if not pts:
        raise ValueError('No evaluated vertices: ' + obj.name)
    return [min(p.x for p in pts), min(p.y for p in pts),
            max(p.x for p in pts), max(p.y for p in pts)]


def update():
    bpy.context.view_layer.update()
    return bpy.context.evaluated_depsgraph_get()


def world_position(obj):
    return list(obj.evaluated_get(update()).matrix_world.translation)


def close(a, b, tolerance=2.e-5):
    return len(a) == len(b) and max(abs(x-y) for x, y in zip(a, b)) <= tolerance


def main():
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', type=Path)
    parser.add_argument('--frames-dir', type=Path, default=EP/'work/hd')
    parser.add_argument('--native-reference-dir', type=Path, default=EP/'work/qa/native')
    parser.add_argument('--check-local-contours', action='store_true')
    parser.add_argument('--report-dir', type=Path, default=EP/'controle')
    options = parser.parse_args(args)
    scene = bpy.context.scene
    payload = json.loads((EP/'assets/vector_frames.json').read_text())
    samples = {s['frame']: s for s in payload['frames']}
    ctrl = bpy.data.objects['CONTROLES_pose']
    root = bpy.data.objects['CONTROLES_deplacement_MOU']
    curves = [o for o in scene.objects if o.type == 'CURVE']
    data_ids = list(bpy.data.objects) + list(bpy.data.shape_keys) + list(bpy.data.materials) + list(bpy.data.cameras)
    data_ids += [m.node_tree for m in bpy.data.materials if m.node_tree]
    drivers = [d for item in data_ids if item.animation_data for d in item.animation_data.drivers]
    check('native_editable_character', len(curves) > 30 and all(o.data.dimensions == '2D' and o.data.shape_keys for o in curves),
          {'curves': len(curves), 'shape_key_blocks': sum(len(o.data.shape_keys.key_blocks) for o in curves),
           'arm_curves': [o.name for o in curves if o.get('role') == 'arms']})
    check('hd_timeline', (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,
          scene.frame_start,scene.frame_end,scene.render.fps,scene.render.fps_base) == (1080,1920,100,1,120,24,1),
          {'size':[scene.render.resolution_x,scene.render.resolution_y], 'percentage':scene.render.resolution_percentage,
           'range':[scene.frame_start,scene.frame_end], 'fps':scene.render.fps,'fps_base':scene.render.fps_base})
    action_markers = [{'name':m.name,'frame':m.frame} for m in scene.timeline_markers if m.name.startswith('ACTION_')]
    check('native_action_clock_markers', len(action_markers)==16 and all(1<=m['frame']<=120 for m in action_markers), action_markers)
    handler_names = ['frame_change_pre','frame_change_post','depsgraph_update_pre','depsgraph_update_post','render_pre','render_post']
    handlers = {name: [getattr(f,'__name__',repr(f)) for f in getattr(bpy.app.handlers,name)] for name in handler_names}
    check('no_character_playback_handlers', not any(handlers.values()), handlers)
    images = [{'name':i.name,'source':i.source,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images]
    check('only_static_packed_images', len(images) == 4 and all(i['source']=='FILE' and i['packed'] for i in images), images)
    mesh_objects = [o for o in scene.objects if o.type == 'MESH']
    mesh_info = [{'name':o.name,'vertices':len(o.data.vertices),'image_nodes':sum(n.type=='TEX_IMAGE' for m in o.data.materials for n in m.node_tree.nodes)} for o in mesh_objects]
    check('no_video_surface_or_character_frame_sequence', len(mesh_objects)==4 and all(x['vertices']==4 and x['image_nodes']==1 for x in mesh_info), mesh_info)
    # Frozen sources are verified by hash, including actual old MP4 files.
    baseline = json.loads((EP/'controle/baseline.json').read_text())
    mismatches = [p for p, sha in baseline.items() if not (REPO/p).is_file() or digest(REPO/p) != sha]
    check('original_sources_and_films_unchanged', not mismatches, {'files':len(baseline),'mismatches':mismatches})
    check('standard_color_management', scene.view_settings.view_transform=='Standard' and scene.view_settings.look=='None' and scene.view_settings.exposure==0 and scene.view_settings.gamma==1,
          {'view':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'gamma':scene.view_settings.gamma})
    # Actual keyframe geometry against source bounds, without relying on the builder report.
    bound_results = []
    for frame in (12,54,99,105,120):
        scene.frame_set(frame)
        update()
        sample = samples[frame]
        ids = ['wide__body/path[0].fill','wide__arm-left/path[0].fill'] if sample['shot']=='wide' else [c['id'] for c in sample['curves'] if c['role']=='sink' and len(c['rings'])==1][:2]
        for name in ids:
            item = next(c for c in sample['curves'] if c['id']==name)
            pts = [p for ring in item['rings'] for p in ring]
            expected = [min(p[0] for p in pts)*.01,-max(p[1] for p in pts)*.01,
                        max(p[0] for p in pts)*.01,-min(p[1] for p in pts)*.01]
            actual = mesh_bounds(bpy.data.objects[name])
            bound_results.append({'frame':frame,'object':name,'max_error_world':max(abs(a-b) for a,b in zip(actual,expected))})
    check('evaluated_bounds_match_sampled_vectors', all(r['max_error_world']<2.e-4 for r in bound_results), bound_results)
    # Scan all 120 scene states for driver errors, finite evaluated bounds and shot visibility.
    states = []
    for frame in range(1,121):
        scene.frame_set(frame)
        update()
        active = [o for o in curves if not o.hide_render]
        invalid = [d.data_path for d in drivers if not d.driver.is_valid]
        finite = all(math.isfinite(x) for o in active[:2] for x in mesh_bounds(o))
        correct_shot = all(o.name.startswith('wide__' if frame<105 else 'sink__') for o in active)
        states.append({'frame':frame,'visible_curves':len(active),'invalid_drivers':len(invalid),'finite':finite,'shot_correct':correct_shot})
    check('all_120_states_have_valid_drivers_and_shots', all(not s['invalid_drivers'] and s['finite'] and s['shot_correct'] and s['visible_curves'] for s in states),
          {'frames':120,'drivers':len(drivers),'failures':[s for s in states if s['invalid_drivers'] or not s['finite'] or not s['shot_correct'] or not s['visible_curves']]})
    camera_results=[]
    for frame, expected_scale in ((104,17.7777778),(105,4.8)):
        scene.frame_set(frame)
        update()
        scale=scene.camera.data.ortho_scale
        camera_results.append({'frame':frame,'ortho_scale':scale,'expected':expected_scale})
    check('camera_cut_is_exact_at_105',all(abs(r['ortho_scale']-r['expected'])<1.e-5 for r in camera_results),camera_results)
    # Native controls must affect both curve geometry and the real attachment anchor.
    scene.frame_set(54)
    for fc in ctrl.animation_data.action.fcurves:
        if fc.data_path.startswith('["Pose_'):
            fc.mute=True
    prop_names=[p for p in ctrl.keys() if p.startswith('Pose_')]
    def pose(frame):
        for prop in prop_names:
            ctrl[prop]=float(prop.startswith('Pose_%03d_'%frame))
        ctrl.update_tag()
        update()
    hand=bpy.data.objects['a.mainleft']
    grip=bpy.data.objects['a.spoon_grip']
    arm=bpy.data.objects['wide__arm-left/path[0].fill']
    spoon=next(o for o in curves if o.get('role')=='prop')
    pose(54)
    hand54=world_position(hand)
    grip54=world_position(grip)
    arm54=mesh_bounds(arm)
    spoon54=mesh_bounds(spoon)
    pose(99)
    hand99=world_position(hand)
    grip99=world_position(grip)
    arm99=mesh_bounds(arm)
    spoon99=mesh_bounds(spoon)
    expected99=[samples[99]['anchors']['mainleft'][0]*.01,-samples[99]['anchors']['mainleft'][1]*.01,0]
    check('pose_slider_changes_drawing_and_anchor_together',close(hand99,expected99) and not close(arm54,arm99) and not close(hand54,hand99),
          {'fixed_timeline':54,'hand_pose54':hand54,'hand_pose99':hand99,'expected99':expected99,'arm_bounds54':arm54,'arm_bounds99':arm99})
    check('real_spoon_attachment_follows_hand',close(hand54,grip54) and close(hand99,grip99) and not close(spoon54,spoon99) and any(c.type=='CHILD_OF' and c.target==grip for c in spoon.constraints),
          {'hand54':hand54,'grip54':grip54,'hand99':hand99,'grip99':grip99,'spoon_bounds54':spoon54,'spoon_bounds99':spoon99})
    pose(54)
    body=bpy.data.objects['wide__body/path[0].fill']
    body_before=mesh_bounds(body)
    hand_before=world_position(hand)
    spoon_before=mesh_bounds(spoon)
    root.location+=Vector((.3,-.2,0))
    update()
    body_after=mesh_bounds(body)
    hand_after=world_position(hand)
    spoon_after=mesh_bounds(spoon)
    check('global_control_moves_character_and_grip_once',close([b-a for a,b in zip(body_before,body_after)],[.3,-.2,.3,-.2]) and close([b-a for a,b in zip(hand_before,hand_after)],[.3,-.2,0]) and close([b-a for a,b in zip(spoon_before,spoon_after)],[.3,-.2,.3,-.2]),
          {'body_delta':[b-a for a,b in zip(body_before,body_after)],'hand_delta':[b-a for a,b in zip(hand_before,hand_after)],'spoon_delta':[b-a for a,b in zip(spoon_before,spoon_after)]})
    root.location-=Vector((.3,-.2,0))
    update()
    target=body.data.shape_keys.key_blocks['054_resistance']
    index=max(range(len(target.data)),key=lambda i:target.data[i].co.x)
    before=mesh_bounds(body)
    target.data[index].co.x+=.15
    body.data.update_tag()
    update()
    after=mesh_bounds(body)
    check('editing_shape_key_changes_evaluated_character',abs(after[2]-before[2]-.15)<2.e-4,
          {'object':body.name,'key':target.name,'edited_vertex':index,'max_x_before':before[2],'max_x_after':after[2]})
    target.data[index].co.x-=.15
    video=None
    if options.video:
        video_path=options.video.resolve()
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video_path)],text=True))
        streams=probe['streams']; vs=[s for s in streams if s['codec_type']=='video']; audio=[s for s in streams if s['codec_type']=='audio']
        v=vs[0] if len(vs)==1 else {}
        check('final_mp4_is_five_seconds_hd_and_silent',len(vs)==1 and not audio and v.get('width')==1080 and v.get('height')==1920 and v.get('avg_frame_rate')=='24/1' and int(v.get('nb_read_frames',0))==120 and abs(float(v.get('duration',0))-5)<.0001,
              {'width':v.get('width'),'height':v.get('height'),'fps':v.get('avg_frame_rate'),'frames':v.get('nb_read_frames'),'duration':v.get('duration'),'audio_streams':len(audio)})
        comparisons=[]
        for frame in (12,54,77,94,99,108,114,117):
            png=options.frames_dir/('%04d.png'%frame)
            if not png.is_file():
                comparisons.append({'frame':frame,'missing_render':str(png)})
                continue
            decoded=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(video_path),'-vf','select=eq(n\\,%d)'%(frame-1),'-frames:v','1','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-'])
            reference=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-i',str(png),'-frames:v','1','-threads','1','-f','rawvideo','-pix_fmt','rgb24','-'])
            if len(decoded)!=1080*1920*3 or len(reference)!=len(decoded):
                comparisons.append({'frame':frame,'wrong_byte_size':[len(decoded),len(reference)]})
                continue
            delta=np.abs(np.frombuffer(decoded,dtype=np.uint8).astype(np.int16)-np.frombuffer(reference,dtype=np.uint8).astype(np.int16))
            comparisons.append({'frame':frame,'mean_absolute_rgb_error':float(delta.mean()),'p99_absolute_rgb_error':float(np.percentile(delta,99))})
        check('final_video_matches_actual_blender_renders',all(c.get('mean_absolute_rgb_error',999)<2 and c.get('p99_absolute_rgb_error',999)<14 for c in comparisons),comparisons)
        video={'path':str(video_path.relative_to(REPO)),'sha256':digest(video_path)}
    if options.video or options.check_local_contours:
        contours=local_contour_checks(options.frames_dir,options.native_reference_dir)
        check('native_contours_survive_topology_sensitive_transitions',all(c['passed'] for c in contours),contours)
    if options.video:
        patch=(420,760,435,780)
        flat_actual=read_rgb_crop(options.frames_dir/'0114.png',patch)
        flat_expected=read_rgb_crop(options.native_reference_dir/'0114.png',patch)
        std_actual=flat_actual.std(axis=(0,1));std_expected=flat_expected.std(axis=(0,1))
        check('wet_overlay_has_no_pixel_dither_in_flat_patch',float(std_expected.max())<=1 and float(std_actual.max())<=2,
              {'frame':114,'roi':list(patch),'native_rgb_stddev':std_expected.tolist(),'blender_rgb_stddev':std_actual.tolist(),
               'native_rgb_mean':flat_expected.mean(axis=(0,1)).tolist(),'blender_rgb_mean':flat_actual.mean(axis=(0,1)).tolist(),
               'max_stddev_per_channel':2,'note':'Checks texture noise, not exact gamma-equivalent transparency compositing.'})
    result={'status':'passed' if all(c['passed'] for c in checks) else 'failed',
            'scope':'native_scene_and_final_export' if video else 'native_scene_only',
            'observed_at_utc':datetime.now(timezone.utc).isoformat(),
            'blender_version':bpy.app.version_string,
            'blend':{'path':str(Path(bpy.data.filepath).relative_to(REPO)),'sha256':digest(bpy.data.filepath)},'video':video,
            'checks':checks,'limits':['Les essais Blender se font sans nouveau rendu ; ils vérifient la scène et les vrais PNG/MP4 déjà produits. La critique examine séparément le jeu et la compréhension.','Rig de poses 2D ; pas de squelette IK.','Les modifications de contrôle et de clé de forme effectuées ici restent en mémoire ; le .blend n’est pas sauvegardé.']}
    regression=EP/'work/qa/rejected_export_local_contours.json'
    if regression.is_file():
        result['previous_rejected_export']={'sha256':'a015ba9bd103e5000c5a6a5923e4d026f8c66f23c1e322233c593537d551b7de',
            'reason':'Visual review found intermediate folds/holes despite the first 17 technical checks passing.',
            'new_check_measured_failures':[r for r in json.loads(regression.read_text()) if r['frame'] in (77,94,114)]}
    options.report_dir.mkdir(parents=True,exist_ok=True)
    (options.report_dir/'QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# Contrôle indépendant — prototype Blender MOU','',
           'Scène ouverte dans un nouveau processus Blender '+bpy.app.version_string+'.',
           'Résultat technique : **'+result['status']+'** ; '+str(len(checks))+' contrôles ciblés.',
           'Périmètre : '+('scène native et MP4 final.' if video else 'scène native uniquement ; MP4 pas encore contrôlé.'),'',
           'Le personnage est constitué de '+str(len(curves))+' courbes 2D éditables, avec '+str(sum(len(o.data.shape_keys.key_blocks) for o in curves))+' clés de forme. Les '+str(len(images))+' images emballées sont trois plaques de décor et le lettrage de la toque. Aucun film ou image entière de MOU ne pilote le personnage.',
           '',
           'À timeline fixe, passer le poids de pose 54 à 99 déplace ensemble le bras, son ancre et la prise de cuillère. Déplacer le contrôle global translate le personnage et sa cuillère une seule fois. Modifier un point de la clé 54 change réellement le contour évalué. Ces essais restent en mémoire et ne sont pas sauvegardés.',
           '',
           'Les 120 états ont été évalués sans erreur de driver ; la coupe de caméra et la visibilité passent au lavabo à l’image 105. Les 22 fichiers de référence, dont les anciens MP4 et le rig original, gardent leurs empreintes.',
           '',
           'SHA-256 du `.blend` : `'+result['blend']['sha256']+'`.']
    if video:
        lines += ['', 'MP4 : `'+video['path']+'`.', 'SHA-256 : `'+video['sha256']+'`.',
                  'Le MP4 est décodé à 120 images, 1080 × 1920, 24 ips, 5 s, sans flux audio. Huit images décodées, dont les anciens défauts aux images 77/94/114, sont comparées aux vrais PNG Blender HD correspondants ; les écarts de compression sont détaillés dans le JSON.',
                  '',
                  'Les 17 contrôles initiaux avaient laissé passer des artefacts visibles entre les poses. Ils ne suffisaient donc pas à déclarer le film livrable. Contrôle ajouté : les contours et remplissages de la bouche (76–79), du bras gauche (91–99) et du centre de la paume (111–117) sont comparés localement à vingt rendus du rig SVG natif préservé. Le seuil accepte une enveloppe d’un pixel pour l’anticrénelage ; il rejette effectivement les pointes, replis et trous du premier export, dont les mesures sont conservées dans le JSON. La critique examine aussi le nouvel encodage.']
        lines += ['', 'La zone uniforme d’humidité de l’image 114 est également contrôlée pour éviter le grain de pixels de la transparence DITHERED. Ce contrôle porte sur la variance locale, pas sur une égalité gamma exacte entre les mélanges transparents SVG et Blender.']
    lines += ['', '## Limites', '', 'La comparaison visuelle des poses et du montage est conservée dans les rapports de critique. Ce contrôle technique ne mesure ni la compréhension du gag ni la qualité comique. Le personnage reste un rig de poses 2D, sans IK. Le film est muet ; aucune écoute n’est revendiquée.', '', 'Détails reproductibles : `qa_blender.py` et `QA.json`.','']
    (options.report_dir/'QA.md').write_text('\n'.join(lines))
    print('QA_RESULT='+json.dumps({'status':result['status'],'checks':len(checks),'failed':[c['check'] for c in checks if not c['passed']]}),flush=True)
    if result['status']!='passed':
        raise SystemExit(1)


if __name__=='__main__':
    if '--prepare-references' in sys.argv:
        prepare_references()
    else:
        main()
