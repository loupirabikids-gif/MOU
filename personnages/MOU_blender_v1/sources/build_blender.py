"""Build the editable, flat MOU 2D Blender prototype from clipped vector rings.

Run with Blender 4.3+: blender -b --factory-startup --python sources/build_blender.py
    -- --build --stills --preview-width 540
No SVG import, character image sequence, or render-time Python handler is used.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix

EP = Path(__file__).resolve().parents[1]
SCALE = 0.01
POSES = {12: "assurance", 54: "resistance", 99: "cede"}
ROLE_COLLECTIONS = {
    "body": "02_MOU_corps_et_visage",
    "arms": "04_MOU_bras_et_moufles",
    "prop": "03_Accessoires",
    "grain": "05_Grain",
    "sink": "06_Evier_vectoriel",
}


def cli():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--build", action="store_true", help="build and save the editable .blend")
    p.add_argument("--input", type=Path, default=EP / "assets/vector_frames.json")
    p.add_argument("--output", type=Path, default=EP / "MOU_blender_v1.blend")
    p.add_argument("--stills", action="store_true", help="render three real Blender pose previews")
    p.add_argument("--still-frames", default=None, help="defaults to key_poses from the input JSON")
    p.add_argument("--preview-width", type=int, default=540)
    p.add_argument("--render-dir", type=Path, default=EP / "work/scene/stills")
    p.add_argument("--samples", type=int, default=16)
    return p.parse_args(argv)


def srgb_channel(value):
    value = max(0.0, min(1.0, float(value)))
    return value / 12.92 if value <= 0.04045 else ((value + .055) / 1.055) ** 2.4


def linear_rgba(rgba):
    vals = list(rgba) + [1.0] * (4 - len(rgba))
    if max(vals[:3]) > 1.0:
        vals[:3] = [v / 255 for v in vals[:3]]
    return (*[srgb_channel(v) for v in vals[:3]], float(vals[3]))


def collection(name):
    if name not in bpy.data.collections:
        result = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(result)
    return bpy.data.collections[name]


def link_object(obj, name):
    collection(name).objects.link(obj)
    return obj


def animate(owner, path, frames, values, interpolation="LINEAR", index=-1):
    for frame, value in zip(frames, values):
        if path.startswith('["'):
            owner[path[2:-2]] = value
        else:
            setattr(owner, path, value)
        owner.keyframe_insert(data_path=path, frame=frame, index=index)
    animation_owner = owner if hasattr(owner, "animation_data") else owner.id_data
    full_path = owner.path_from_id(path)
    if animation_owner.animation_data and animation_owner.animation_data.action:
        for curve in animation_owner.animation_data.action.fcurves:
            if curve.data_path == full_path:
                for key in curve.keyframe_points:
                    key.interpolation = interpolation


def driver_variable(driver, name, owner, path):
    var = driver.variables.new()
    var.name = name
    var.type = "SINGLE_PROP"
    var.targets[0].id = owner
    var.targets[0].data_path = path
    return var


def weights_driver(owner, path, controller, prop_names, present=None, own_index=None):
    """Normalize the real shared pose sliders; no per-frame geometry handler."""
    curve = owner.driver_add(path)
    driver = curve.driver
    driver.type = "SCRIPTED"
    if own_index is not None:
        if present is not None and not present[own_index]:
            driver.expression = "0.0"
            return
        driver_variable(driver, "poids", controller, '["' + prop_names[own_index] + '"]')
    if present is None or all(present):
        driver_variable(driver, "total", controller, '["_somme_poses"]')
        denominator = "max(total,0.000001)"
    else:
        terms = []
        for index, (prop, visible) in enumerate(zip(prop_names, present)):
            if visible:
                var = "v" + str(index)
                driver_variable(driver, var, controller, '["' + prop + '"]')
                terms.append(var)
        denominator = "max(" + "+".join(terms or ["0.0"]) + ",0.000001)"
    driver.expression = ("max(poids,0.0)/" + denominator) if own_index is not None else denominator


def is_anchor_point(value):
    return (isinstance(value, (list, tuple)) and len(value) >= 2 and
            all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in value[:2]))


def spoon_is_held(sample):
    return bool(sample.get("spoon_held", sample.get("held", sample.get("anchors", {}).get("spoon_held", False))))


def setup_controls(frames):
    ctrl = link_object(bpy.data.objects.new("CONTROLES_pose", None), "00_Controles")
    ctrl.empty_display_type = "PLAIN_AXES"
    ctrl.empty_display_size = .6
    ctrl["mode_emploi"] = "Poids de poses réels. Clés sur ces propriétés ; dessins dans les Shape Keys des courbes."
    ctrl["limite"] = "Rig de poses 2D ; pas d'IK. Les ancres animent les prises d'accessoires."
    ctrl["spoon_held"] = False
    animate(ctrl, '["spoon_held"]', [f["frame"] for f in frames], [spoon_is_held(f) for f in frames], "CONSTANT")
    ctrl["frame_lecture"] = 1.0
    frame_driver = ctrl.driver_add('["frame_lecture"]').driver
    frame_driver.expression = "frame"
    prop_names = []
    for i, sample in enumerate(frames):
        frame = sample["frame"]
        label = POSES.get(frame, sample.get("label", "etape"))
        prop = "Pose_%03d_%s" % (frame, label)
        prop_names.append(prop)
        ctrl[prop] = 0.0
        ctrl.id_properties_ui(prop).update(min=0., max=1., soft_min=0., soft_max=1.,
                                          description="Poids réel du dessin à l'image %d" % frame)
        animate(ctrl, '["' + prop + '"]', [f["frame"] for f in frames],
                [1.0 if j == i else 0.0 for j in range(len(frames))])
    ctrl["_somme_poses"] = 1.0
    driver = ctrl.driver_add('["_somme_poses"]').driver
    terms = []
    for index, prop in enumerate(prop_names):
        name = "p" + str(index)
        driver_variable(driver, name, ctrl, '["' + prop + '"]')
        terms.append(name)
    driver.expression = "+".join(terms)
    ctrl.animation_data.action.name = "MOU_5_secondes_poids_de_poses"
    ctrl.animation_data.action.use_fake_user = True
    ctrl.animation_data.action.asset_mark()
    ctrl.animation_data.action.asset_data.description = "MOU original : essai muet, poids des dessins vectoriels, 120 images à 24 ips."
    root = link_object(bpy.data.objects.new("CONTROLES_deplacement_MOU", None), "00_Controles")
    root.empty_display_type = "CIRCLE"
    root.empty_display_size = 1.0
    root["usage"] = "Déplacer cet Empty déplace MOU, ses ancres et les accessoires attachés."
    for frame, name in POSES.items():
        bpy.context.scene.timeline_markers.new(name, frame=frame)
    bpy.context.scene.timeline_markers.new("coupe_evier", frame=105)
    return ctrl, root, prop_names


def signed_area(ring):
    return .5 * sum(p[0]*q[1] - q[0]*p[1] for p, q in zip(ring, ring[1:]+ring[:1]))


def resample(ring, count):
    pts = [tuple(map(float, p[:2])) for p in ring]
    if len(pts) > 1 and pts[-1] == pts[0]:
        pts.pop()
    if not pts:
        return [(0.0, 0.0)] * count
    if len(pts) == count:
        return pts
    lengths = [math.dist(p, q) for p, q in zip(pts, pts[1:] + pts[:1])]
    perimeter = sum(lengths)
    if perimeter < 1e-10:
        return [pts[0]] * count
    result = []
    edge = 0
    start = 0.0
    for i in range(count):
        distance = perimeter * i / count
        while edge < len(pts)-1 and distance > start + lengths[edge]:
            start += lengths[edge]
            edge += 1
        a, b = pts[edge], pts[(edge+1) % len(pts)]
        fraction = (distance-start) / lengths[edge] if lengths[edge] else 0.0
        result.append((a[0] + (b[0]-a[0])*fraction, a[1] + (b[1]-a[1])*fraction))
    return result


def align_ring(ring, reference):
    if abs(signed_area(ring)) < 1e-10 or abs(signed_area(reference)) < 1e-10:
        return ring
    if signed_area(ring) * signed_area(reference) < 0:
        ring = ring[::-1]
    count = len(ring)
    best = min(range(count), key=lambda shift: sum(
        (ring[(i+shift) % count][0]-reference[i][0])**2 +
        (ring[(i+shift) % count][1]-reference[i][1])**2 for i in range(count)))
    return ring[best:] + ring[:best]


def normalized_rings(samples):
    valid = [s for s in samples if s and s.get("rings")]
    slots = max(len(s["rings"]) for s in valid)
    counts = [max(max(3, len(s["rings"][i])) for s in valid if i < len(s["rings"])) for i in range(slots)]
    # Keep supplied 128-point contours intact; different inputs are resampled once.
    reference = [None] * slots
    result = []
    for sample in samples:
        rings = sample.get("rings", []) if sample else []
        origin = rings[0][0] if rings and rings[0] else valid[0]["rings"][0][0]
        normalized = []
        for i, count in enumerate(counts):
            if i < len(rings) and rings[i]:
                ring = resample(rings[i], count)
                if reference[i] is not None:
                    ring = align_ring(ring, reference[i])
                reference[i] = ring
            else:
                ring = [tuple(origin)] * count
            normalized.append(ring)
        result.append(normalized)
    return result, counts


def make_material(name, rgba=(1, 1, 1, 1), image=None):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = linear_rgba(rgba)
    material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.name = "Couleur_aplat"
    emission.inputs["Color"].default_value = linear_rgba(rgba)
    emission.inputs["Strength"].default_value = 1.0
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    mix.name = "Opacite"
    mix.inputs[0].default_value = float(rgba[3])
    material.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
    material.node_tree.links.new(emission.outputs[0], mix.inputs[2])
    material.node_tree.links.new(mix.outputs[0], out.inputs["Surface"])
    if image is not None:
        texture = nodes.new("ShaderNodeTexImage")
        texture.image = image
        texture.interpolation = "Linear"
        texture.extension = "CLIP"
        material.node_tree.links.new(texture.outputs["Color"], emission.inputs["Color"])
        material.node_tree.links.new(texture.outputs["Alpha"], mix.inputs[0])
    return material


def animate_visibility(obj, frames, visible):
    animate(obj, "hide_render", frames, [not v for v in visible], "CONSTANT")
    animate(obj, "hide_viewport", frames, [not v for v in visible], "CONSTANT")


def anchor_pose_drivers(obj, values, controller, prop_names):
    """Use the exact shared pose weights, with short native driver expressions."""
    for axis in range(3):
        basis = values[0][axis]
        parts = []
        for start in range(0, len(values), 8):
            terms = []
            prop = "_pose_anchor_%d_%02d" % (axis, start // 8)
            obj[prop] = 0.0
            driver = obj.driver_add('["' + prop + '"]').driver
            for index in range(start, min(start + 8, len(values))):
                delta = values[index][axis] - basis
                if abs(delta) > 1.e-12:
                    variable = "p" + str(index)
                    driver_variable(driver, variable, controller, '["' + prop_names[index] + '"]')
                    terms.append("%s*(%.10g)" % (variable, delta))
            driver.expression = "+".join(terms) or "0.0"
            if len(driver.expression) > 255:
                raise ValueError("Anchor driver exceeds 255 characters: " + obj.name)
            parts.append(prop)
        driver = obj.driver_add("location", axis).driver
        for index, prop in enumerate(parts):
            driver_variable(driver, "a" + str(index), obj, '["' + prop + '"]')
        driver_variable(driver, "total", controller, '["_somme_poses"]')
        driver.expression = "%.12g+(%s)/max(total,0.000001)" % (basis, "+".join("a" + str(i) for i in range(len(parts))))


def make_anchors(frames, root, controller, prop_names):
    names = sorted({name for sample in frames for name, value in sample.get("anchors", {}).items() if is_anchor_point(value)})
    for canonical, alias in (("mainleft", "left"), ("mainright", "right")):
        if canonical in names and alias in names:
            names.remove(alias)
    result = {}
    for name in names:
        objname = {"left": "a.mainleft", "mainleft": "a.mainleft", "right": "a.mainright", "mainright": "a.mainright"}.get(name, name if name.startswith("a.") else "a." + name)
        obj = link_object(bpy.data.objects.new(objname, None), "00_Controles")
        obj.empty_display_type = "SPHERE"
        obj.empty_display_size = .07
        obj.parent = root
        previous = next(s["anchors"][name] for s in frames if is_anchor_point(s.get("anchors", {}).get(name)))
        values = []
        for sample in frames:
            current = sample.get("anchors", {}).get(name)
            if is_anchor_point(current):
                previous = current
            values.append((previous[0]*SCALE, -previous[1]*SCALE, 0.0))
        anchor_pose_drivers(obj, values, controller, prop_names)
        obj["usage"] = "Position pilotée par les mêmes poids de poses que les dessins. La cuillère suit a.spoon_grip par Child Of."
        result[name] = obj
    left = result.get("mainleft", result.get("left"))
    spoon = result.get("spoon_grip")
    right = result.get("mainright", result.get("right"))
    if right is not None:
        result.setdefault("right", right)
        result.setdefault("mainright", right)
    if left is not None:
        result.setdefault("left", left)
        result.setdefault("mainleft", left)
    if spoon is not None and left is not None:
        constraint = spoon.constraints.new("COPY_LOCATION")
        constraint.name = "Tenue_reelle_par_mainleft"
        constraint.target = left
        constraint.owner_space = "WORLD"
        constraint.target_space = "WORLD"
        held_driver = constraint.driver_add("influence").driver
        driver_variable(held_driver, "tenue", controller, '["spoon_held"]')
        held_driver.expression = "tenue"
        spoon["usage"] = "Copy Location de a.mainleft quand tenue ; position source quand garée. La cuillère suit ce contrôle par Child Of."
    return result


def source_origin(sample, attach):
    if not attach:
        return (0.0, 0.0)
    value = sample.get("anchors", {}).get(attach)
    return value[:2] if is_anchor_point(value) else (0.0, 0.0)


def attach_object(obj, root, anchors, attach):
    if attach and attach in anchors:
        constraint = obj.constraints.new("CHILD_OF")
        constraint.name = "Prise_" + anchors[attach].name
        constraint.target = anchors[attach]
        constraint.inverse_matrix = Matrix.Identity(4)
        constraint.set_inverse_pending = False
        constraint.influence = 1.0
        obj["attache_active"] = anchors[attach].name
    else:
        obj.parent = root


def add_shape_keys(obj, coordinates, samples, controller, prop_names, visible):
    basis_index = next(i for i, v in enumerate(visible) if v)
    basis = obj.shape_key_add(name="Basis", from_mix=False)
    for point, co in zip(basis.data, coordinates[basis_index]):
        point.co = co
    for i, (sample, coords) in enumerate(zip(samples, coordinates)):
        label = POSES.get(sample["frame"], sample.get("label", "etape"))
        key = obj.shape_key_add(name="%03d_%s" % (sample["frame"], label), from_mix=False)
        key.relative_key = basis
        for point, co in zip(key.data, coords):
            point.co = co
        weights_driver(key, "value", controller, prop_names, present=visible, own_index=i)
    obj.active_shape_key_index = basis_index + 1
    obj.show_only_shape_key = False


def active_in_shot(entry, sample, default=None):
    shot = entry.get("shot", default) if entry else default
    current = sample.get("shot", "wide" if sample["frame"] < 105 else "sink")
    return shot is None or shot == current


def animate_depth(obj, entries, frames, fallback):
    for entry, sample in zip(entries, frames):
        obj.location.z = float(entry.get("order", fallback) if entry else fallback) * .001
        obj.keyframe_insert("location", index=2, frame=sample["frame"])
    for curve in obj.animation_data.action.fcurves:
        if curve.data_path == "location" and curve.array_index == 2:
            for key in curve.keyframe_points:
                key.interpolation = "CONSTANT"


def make_curve(identifier, entries, frames, controller, root, prop_names, anchors, report):
    first = next(s for s in entries if s and s.get("rings"))
    visible = [bool(s and s.get("rings") and s.get("rgba", [0, 0, 0, 1])[3] > 0 and active_in_shot(s, f, first.get("shot"))) for s, f in zip(entries, frames)]
    normalized, counts = normalized_rings(entries)
    role = first.get("role", "body")
    attach = first.get("attach")
    # The coordinator marks spoon paths explicitly. Nothing else is attached by guess.
    if not attach and role == "prop":
        attach = "spoon_grip" if "spoon_grip" in anchors else "left"
    data = bpy.data.curves.new(identifier + "_dessin", "CURVE")
    data.dimensions = "2D"
    data.fill_mode = "BOTH"
    data.resolution_u = 1
    data.render_resolution_u = 1
    for count in counts:
        spline = data.splines.new("POLY")
        spline.points.add(count-1)
        spline.use_cyclic_u = True
    obj = link_object(bpy.data.objects.new(identifier, data), ROLE_COLLECTIONS.get(role, "02_MOU_corps_et_visage"))
    obj.location.z = float(first.get("order", 0)) * .001
    obj["source_id"] = identifier
    obj["role"] = role
    obj["edition"] = "Shape Keys : choisir une étape, puis Tab pour modifier ses points."
    coords = []
    for sample, rings in zip(frames, normalized):
        origin = source_origin(sample, attach)
        coords.append([((p[0]-origin[0])*SCALE, -(p[1]-origin[1])*SCALE, 0.0) for ring in rings for p in ring])
    for point, co in zip([p for s in data.splines for p in s.points], coords[next(i for i,v in enumerate(visible) if v)]):
        point.co = (*co, 1.0)
    add_shape_keys(obj, coords, frames, controller, prop_names, visible)
    material = make_material(identifier + "_aplat", first.get("rgba", [1, 1, 1, 1]))
    if identifier.startswith("sink__") and any(entry and entry.get("rgba", [0, 0, 0, 1])[3] < 1.0 for entry in entries):
        # Flat 2D alpha blending avoids hashed transparency noise at eight samples.
        material.surface_render_method = "BLENDED"
    data.materials.append(material)
    present_entries = [s or first for s in entries]
    colors = [linear_rgba(s.get("rgba", first.get("rgba", [1, 1, 1, 1]))) for s in present_entries]
    if len(set(colors)) > 1:
        socket = material.node_tree.nodes["Couleur_aplat"].inputs["Color"]
        for sample, color in zip(frames, colors):
            socket.default_value = color
            socket.keyframe_insert("default_value", frame=sample["frame"])
        alpha = material.node_tree.nodes["Opacite"].inputs[0]
        for sample, color in zip(frames, colors):
            alpha.default_value = color[3]
            alpha.keyframe_insert("default_value", frame=sample["frame"])
    animate_visibility(obj, [f["frame"] for f in frames], visible)
    animate_depth(obj, entries, frames, first.get("order", 0))
    attach_object(obj, root, anchors, attach)
    ring_counts = [len(s.get("rings", [])) if s else 0 for s in entries]
    report["curves"].append({"id": identifier, "role": role, "points_per_ring": counts,
                             "sample_ring_counts": ring_counts, "attached_to": attach,
                             "shape_keys": len(data.shape_keys.key_blocks), "driver_count": len(data.shape_keys.animation_data.drivers)})
    return obj


def image_plane(name, path, corners, order, coll="01_Decors_fixes"):
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = "sRGB"
    image.pack()
    mesh = bpy.data.meshes.new(name + "_plan")
    vertices = [(p[0]*SCALE, -p[1]*SCALE, 0.0) for p in corners]
    # JSON corners are TL,TR,BR,BL. UV y is inverted relative to SVG.
    mesh.from_pydata(vertices, [], [(0, 1, 2, 3)])
    mesh.uv_layers.new(name="UVMap")
    uv = [(0., 1.), (1., 1.), (1., 0.), (0., 0.)]
    for poly in mesh.polygons:
        for vertex_index, loop_index in zip(poly.vertices, poly.loop_indices):
            mesh.uv_layers.active.data[loop_index].uv = uv[vertex_index]
    obj = link_object(bpy.data.objects.new(name, mesh), coll)
    obj.location.z = order * .001
    mesh.materials.append(make_material(name + "_image_sRGB", image=image))
    obj["image_emballee"] = True
    return obj


def read_plates(root_dir, frames, report):
    path = root_dir / "assets/plates/plates.json"
    if not path.is_file():
        return
    payload = json.loads(path.read_text())
    plates = payload.get("plates", []) if isinstance(payload, dict) else payload
    body_orders = [float(c.get("order", 0)) for f in frames for c in f.get("curves", []) if c.get("role") == "body"]
    arm_orders = [float(c.get("order", 0)) for f in frames for c in f.get("curves", []) if c.get("role") == "arms"]
    fore_order = 500
    for index, plate in enumerate(plates):
        x, y, w, h = plate["world"]
        corners = [[x,y], [x+w,y], [x+w,y+h], [x,y+h]]
        default_order = fore_order if plate.get("role") in ("front", "foreground") else -1000
        obj = image_plane("Plate_%s_%s" % (plate.get("shot", "wide"), plate.get("role", index)),
                          root_dir / plate["path"], corners, float(plate.get("order", default_order)))
        shot = plate.get("shot", "wide")
        animate_visibility(obj, [1, 104, 105, 120], [shot == "wide", shot == "wide", shot == "sink", shot == "sink"])
        obj["usage"] = "Décor fixe ; personnage vectoriel dans les autres collections."
        report["plates"].append({"name": obj.name, "path": plate["path"], "world": plate["world"], "order": obj.location.z / .001})


def read_images(root_dir, frames, controller, root, prop_names, anchors, report):
    ids = sorted({im["id"] for f in frames for im in f.get("images", [])})
    for identifier in ids:
        entries = [next((im for im in f.get("images", []) if im["id"] == identifier), None) for f in frames]
        first = next(im for im in entries if im)
        if any(im and im["path"] != first["path"] for im in entries):
            raise ValueError("Image sequence forbidden for actor: " + identifier)
        visible = [bool(im and active_in_shot(im, f, first.get("shot"))) for im, f in zip(entries, frames)]
        attach = first.get("attach")
        corners_by_sample = []
        for sample, entry in zip(frames, entries):
            entry = entry or first
            origin = source_origin(sample, attach)
            corners_by_sample.append([((p[0]-origin[0])*SCALE, -(p[1]-origin[1])*SCALE, 0.0) for p in entry["corners"]])
        obj = image_plane(identifier, root_dir / first["path"], first["corners"], float(first.get("order", 0)), "02_MOU_corps_et_visage")
        add_shape_keys(obj, corners_by_sample, frames, controller, prop_names, visible)
        animate_visibility(obj, [f["frame"] for f in frames], visible)
        animate_depth(obj, entries, frames, first.get("order", 0))
        attach_object(obj, root, anchors, attach)
        obj["role"] = first.get("role", "lettering")
        report["images"].append({"id": identifier, "path": first["path"], "shape_keys": len(obj.data.shape_keys.key_blocks)})


def setup_scene(samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "MOU_original_essai_muet_5s"
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.eevee.taa_render_samples = samples
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 120
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.world = bpy.data.worlds.new("Fond_neutre")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (1, 1, 1, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.render.use_file_extension = True
    camera = bpy.data.cameras.new("Camera_orthographique_2D")
    camera.type = "ORTHO"
    camera.clip_start = .01
    camera.clip_end = 1000
    cam = link_object(bpy.data.objects.new("Camera_orthographique_2D", camera), "00_Controles")
    scene.camera = cam
    shots = [(1, (25, 220, 1000, 1777.77778)), (104, (25, 220, 1000, 1777.77778)),
             (105, (0, 925, 270, 480)), (120, (0, 925, 270, 480))]
    animate(cam, "location", [s[0] for s in shots], [((b[0]+b[2]/2)*SCALE, -(b[1]+b[3]/2)*SCALE, 100.) for _, b in shots], "CONSTANT")
    animate(camera, "ortho_scale", [s[0] for s in shots], [b[3]*SCALE for _, b in shots], "CONSTANT")
    return scene


def readable_workspace(controller):
    bpy.context.view_layer.objects.active = controller
    controller.select_set(True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.spaces.active.region_3d.view_perspective = "CAMERA"
                area.spaces.active.shading.type = "MATERIAL"
            elif area.type == "PROPERTIES":
                area.spaces.active.context = "OBJECT"
    text = bpy.data.texts.new("LIRE_MOU_rig")
    text.write("MOU — prototype 2D éditable\n\nLes courbes du personnage sont de vraies CURVE 2D remplies.\n"
               "CONTROLES_pose > Propriétés personnalisées : poids de poses animés, reliés aux clés par drivers.\n"
               "Pose 12 assurance ; pose 54 resistance ; pose 99 cede. Marqueurs dans la timeline.\n"
               "Pour modifier un dessin : sélectionner une courbe, Données > Clés de forme, choisir l'étape, Tab.\n"
               "Pour retoucher un poids au cours du temps : insérer une clé sur la propriété du contrôleur.\n"
               "Déplacement global : CONTROLES_deplacement_MOU. Cuillère : contrainte Child Of sur a.spoon_grip (ou a.mainleft).\n"
               "Rig de poses, pas d'IK ; masques des yeux résolus géométriquement dans les contours.\n"
               "Les PNG emballés concernent les décors fixes et le lettrage.\n")


def build(args):
    payload = json.loads(args.input.read_text())
    if payload.get("key_poses"):
        POSES.clear()
        POSES.update({int(frame): str(name) for name, frame in payload["key_poses"].items()})
    frames = sorted(payload["frames"], key=lambda f: f["frame"])
    if not frames or len({s["frame"] for s in frames}) != len(frames):
        raise ValueError("Sample frame numbers must be unique and nonempty")
    scene = setup_scene(args.samples)
    ctrl, root, prop_names = setup_controls(frames)
    anchors = make_anchors(frames, root, ctrl, prop_names)
    report = {"blender_version": bpy.app.version_string, "input": str(args.input),
              "sample_frames": [f["frame"] for f in frames], "curves": [], "images": [], "plates": [],
              "render": {"size": [1080,1920], "fps":24, "frames":120, "samples":args.samples},
              "rig": "2D CURVE filled polygons, shared animated pose weights and native Shape Key drivers; no IK"}
    read_plates(args.input.parent.parent, frames, report)
    ids = sorted({c["id"] for f in frames for c in f.get("curves", [])})
    for identifier in ids:
        entries = [next((c for c in f.get("curves", []) if c["id"] == identifier), None) for f in frames]
        if not any(c and c.get("rings") and c.get("rgba", [0,0,0,1])[3] > 0 and active_in_shot(c, f) for c, f in zip(entries, frames)):
            continue
        make_curve(identifier, entries, frames, ctrl, root, prop_names, anchors, report)
    read_images(args.input.parent.parent, frames, ctrl, root, prop_names, anchors, report)
    readable_workspace(ctrl)
    scene["source_vectors"] = "assets/vector_frames.json"
    scene["edition"] = "Courbes 2D et poids de poses éditables. Pas d'IK ni de personnage sur vidéo."
    scene.frame_set(12)
    bpy.context.view_layer.update()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(args.output))
    report["blend"] = str(args.output)
    report["packed_images"] = [image.name for image in bpy.data.images if image.packed_file]
    report["objects"] = len(scene.objects)
    report_path = EP / "work/scene/build_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("MOU_BLEND_SAVED=" + str(args.output), flush=True)
    return scene, report


def main():
    args = cli()
    scene, report = build(args)
    if args.stills:
        args.render_dir.mkdir(parents=True, exist_ok=True)
        old_res = scene.render.resolution_percentage
        scene.render.resolution_percentage = max(1, round(args.preview_width / 1080 * 100))
        for frame in ([int(v) for v in args.still_frames.split(",") if v.strip()] if args.still_frames else sorted(POSES)):
            scene.frame_set(frame)
            filename = "%03d_%s.png" % (frame, POSES.get(frame, "controle"))
            scene.render.filepath = str(args.render_dir / filename)
            bpy.ops.render.render(write_still=True)
            print("MOU_STILL=" + scene.render.filepath, flush=True)
        scene.render.resolution_percentage = old_res
    print("MOU_BUILD_OK=" + json.dumps({"curves": len(report["curves"]), "images":len(report["images"]), "poses":len(report["sample_frames"])}), flush=True)


if __name__ == "__main__":
    main()
