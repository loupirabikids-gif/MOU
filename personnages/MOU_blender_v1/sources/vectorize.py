"""SVG paint -> clipped, editable polygon contours for the MOU Blender prototype.

Public API: ``vectorize(svg_text, asset_dir, *, samples=128)``. Coordinates stay
in SVG canvas pixels, including all group transforms. No Blender dependency.
Each SVG paint operation has a stable ID and a fixed number of points per ring;
the caller reconciles objects/rings which appear or disappear between frames.
Clip paths are intersected with paint geometry here, before Blender import.

Supported input is deliberately the actor SVG subset: paths, ellipses/circles,
rectangles, lines, polygons/polylines, groups, inline/presentation styles,
transforms, use references, clipPaths, and embedded PNG/JPEG logos. Gradients,
patterns, text, masks, filters, and dashed strokes raise UnsupportedSVGError
rather than silently changing the artwork. Group opacity is distributed to
leaves (exact for the opaque groups used by this actor).
"""

from __future__ import annotations

import base64
import bisect
import hashlib
import io
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageColor
from shapely import affinity, make_valid
from shapely.geometry import GeometryCollection, LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import polygonize, unary_union
from svgpathtools import Line, parse_path


class UnsupportedSVGError(ValueError):
    """An SVG feature cannot be faithfully represented by this converter."""


IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
NUMBER = r"[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"
NUM_RE = re.compile(NUMBER)
INHERITED = {
    "fill", "fill-rule", "fill-opacity", "stroke", "stroke-width",
    "stroke-opacity", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit",
    "stroke-dasharray", "stroke-dashoffset", "color", "visibility", "clip-rule",
}
DEFAULT_STYLE = {
    "fill": "black", "fill-rule": "nonzero", "fill-opacity": "1",
    "stroke": "none", "stroke-width": "1", "stroke-opacity": "1",
    "stroke-linecap": "butt", "stroke-linejoin": "miter",
    "stroke-miterlimit": "4", "color": "black", "visibility": "visible",
    "clip-rule": "nonzero",
}
SHAPES = {"path", "ellipse", "circle", "rect", "polygon", "polyline", "line"}
NONRENDERED = {"defs", "clipPath", "metadata", "title", "desc", "style"}


def _tag(node):
    return node.tag.rsplit("}", 1)[-1]


def _number(value, default=0.0):
    if value is None:
        return default
    value = str(value).strip()
    if value.endswith("%"):
        return float(value[:-1]) / 100.0
    match = NUM_RE.fullmatch(value.removesuffix("px"))
    if not match:
        raise UnsupportedSVGError(f"Unsupported numeric SVG unit: {value!r}")
    return float(match.group())


def _mul(a, b):
    aa, ab, ac, ad, ae, af = a
    ba, bb, bc, bd, be, bf = b
    return (aa*ba+ac*bb, ab*ba+ad*bb, aa*bc+ac*bd, ab*bc+ad*bd,
            aa*be+ac*bf+ae, ab*be+ad*bf+af)


def _point(matrix, point):
    a, b, c, d, e, f = matrix
    x, y = point
    return (a*x+c*y+e, b*x+d*y+f)


def _transform(value):
    matrix = IDENTITY
    for name, args in re.findall(r"([a-zA-Z]+)\s*\(([^)]*)\)", value or ""):
        v = [float(n) for n in NUM_RE.findall(args)]
        if name == "matrix" and len(v) == 6:
            part = tuple(v)
        elif name == "translate" and len(v) in (1, 2):
            part = (1, 0, 0, 1, v[0], v[1] if len(v) == 2 else 0)
        elif name == "scale" and len(v) in (1, 2):
            part = (v[0], 0, 0, v[-1], 0, 0)
        elif name == "rotate" and len(v) in (1, 3):
            angle = math.radians(v[0])
            cs, sn = math.cos(angle), math.sin(angle)
            part = (cs, sn, -sn, cs, 0, 0)
            if len(v) == 3:
                part = _mul((1, 0, 0, 1, v[1], v[2]),
                            _mul(part, (1, 0, 0, 1, -v[1], -v[2])))
        elif name in ("skewX", "skewY") and len(v) == 1:
            skew = math.tan(math.radians(v[0]))
            part = (1, 0, skew, 1, 0, 0) if name == "skewX" else (1, skew, 0, 1, 0, 0)
        else:
            raise UnsupportedSVGError(f"Unsupported SVG transform: {name}({args})")
        matrix = _mul(matrix, part)
    return matrix


def _affine(geometry, matrix):
    a, b, c, d, e, f = matrix
    return affinity.affine_transform(geometry, (a, c, b, d, e, f))


def _own_style(node):
    style = {key: value for key, value in node.attrib.items()
             if key in INHERITED or key in {"opacity", "clip-path", "display",
                                            "filter", "mask", "paint-order", "vector-effect"}}
    for declaration in node.get("style", "").split(";"):
        if ":" in declaration:
            key, value = declaration.split(":", 1)
            style[key.strip()] = value.strip()
    return style


def _style(node, inherited):
    result = {key: value for key, value in inherited.items() if key in INHERITED}
    result.update(_own_style(node))
    return result


def _color(value, style, alpha):
    if value == "none":
        return None
    if "url(" in value:
        raise UnsupportedSVGError(f"Gradient/pattern paint is unsupported: {value}")
    if value == "currentColor":
        value = style.get("color", "black")
    try:
        if value.startswith("rgb") and "%" in value:
            parts = value[value.index("(")+1:value.rindex(")")].replace(",", " ").split()
            rgb = [round(_number(p)*255) for p in parts[:3]]
            rgba = (*rgb, round(_number(parts[3])*255) if len(parts) == 4 else 255)
        else:
            rgba = ImageColor.getcolor(value, "RGBA")
    except (ValueError, TypeError) as exc:
        raise UnsupportedSVGError(f"Unsupported SVG color: {value!r}") from exc
    return [rgba[0]/255, rgba[1]/255, rgba[2]/255,
            min(1.0, max(0.0, alpha*rgba[3]/255))]


def _segment_points(segment, tolerance=0.035):
    if isinstance(segment, Line):
        return [(segment.start.real, segment.start.imag), (segment.end.real, segment.end.imag)]
    result = [(segment.start.real, segment.start.imag)]

    def flatten(t0, p0, t1, p1, depth):
        quarter = [segment.point(t0+(t1-t0)*fraction) for fraction in (.25, .5, .75)]
        delta = p1-p0
        if abs(delta) < 1e-12:
            deviation = max(abs(p-p0) for p in quarter)
        else:
            deviation = max(abs((p-p0).real*delta.imag-(p-p0).imag*delta.real)/abs(delta)
                            for p in quarter)
        if deviation <= tolerance or depth >= 16:
            result.append((p1.real, p1.imag))
        else:
            middle_t, middle_p = (t0+t1)/2, quarter[1]
            flatten(t0, p0, middle_t, middle_p, depth+1)
            flatten(middle_t, middle_p, t1, p1, depth+1)

    flatten(0, segment.start, 1, segment.end, 0)
    return result


def _subpaths(node):
    tag = _tag(node)
    n = lambda key, default=0.0: _number(node.get(key), default)
    if tag == "path":
        path = parse_path(node.get("d", ""))
        result = []
        for subpath in path.continuous_subpaths():
            points = []
            for segment in subpath:
                segment_points = _segment_points(segment)
                points.extend(segment_points if not points else segment_points[1:])
            if points:
                result.append((points, bool(subpath.isclosed())))
        return result
    if tag in {"ellipse", "circle"}:
        cx, cy = n("cx"), n("cy")
        rx, ry = (n("r"), n("r")) if tag == "circle" else (n("rx"), n("ry"))
        if rx <= 0 or ry <= 0:
            return []
        count = max(64, min(2048, math.ceil(math.pi*math.sqrt(max(rx, ry)/.07))))
        return [([(cx+rx*math.cos(2*math.pi*i/count), cy+ry*math.sin(2*math.pi*i/count))
                  for i in range(count)], True)]
    if tag == "rect":
        x, y, width, height = n("x"), n("y"), n("width"), n("height")
        if width <= 0 or height <= 0:
            return []
        rx, ry = n("rx", n("ry")), n("ry", n("rx"))
        rx, ry = min(max(rx, 0), width/2), min(max(ry, 0), height/2)
        if not rx or not ry:
            return [([(x, y), (x+width, y), (x+width, y+height), (x, y+height)], True)]
        points = []
        for cx, cy, start in [(x+width-rx, y+ry, -math.pi/2),
                              (x+width-rx, y+height-ry, 0),
                              (x+rx, y+height-ry, math.pi/2),
                              (x+rx, y+ry, math.pi)]:
            points.extend((cx+rx*math.cos(start+i*math.pi/32),
                           cy+ry*math.sin(start+i*math.pi/32)) for i in range(17))
        return [(points, True)]
    if tag in {"polygon", "polyline"}:
        values = [float(value) for value in NUM_RE.findall(node.get("points", ""))]
        return [(list(zip(values[::2], values[1::2])), tag == "polygon")]
    if tag == "line":
        return [([(n("x1"), n("y1")), (n("x2"), n("y2"))], False)]
    return []


def _winding(point, points):
    px, py = point
    winding = 0
    for (x0, y0), (x1, y1) in zip(points, points[1:]+points[:1]):
        cross = (x1-x0)*(py-y0)-(px-x0)*(y1-y0)
        if y0 <= py < y1 and cross > 0:
            winding += 1
        elif y1 <= py < y0 and cross < 0:
            winding -= 1
    return winding


def _filled(subpaths, rule="nonzero"):
    rings = [points for points, _closed in subpaths if len(points) >= 3]
    if not rings:
        return GeometryCollection()
    if len(rings) == 1:
        simple = Polygon(rings[0])
        if simple.is_valid:
            return simple
    boundaries = [LineString(points+[points[0]]) for points in rings]
    faces = polygonize(unary_union(boundaries))
    selected = []
    for face in faces:
        p = face.representative_point()
        winding = sum(_winding((p.x, p.y), points) for points in rings)
        if winding % 2 != 0 if rule == "evenodd" else winding != 0:
            selected.append(face)
    return unary_union(selected) if selected else GeometryCollection()


def _polygons(geometry):
    if geometry.is_empty:
        return []
    if isinstance(geometry, Polygon):
        return [geometry] if geometry.area > 1e-10 else []
    result = []
    for child in getattr(geometry, "geoms", []):
        result.extend(_polygons(child))
    return result


def _resample_ring(ring, anchor, count, positive):
    points = list(ring.coords)
    area = sum(x0*y1-x1*y0 for (x0, y0), (x1, y1) in zip(points, points[1:]))
    if (area > 0) != positive:
        points.reverse()
    line = LineString(points)
    start = line.project(Point(anchor))
    # Start at the projected original SVG path start. Split its segment so the
    # reference remains exact, rather than choosing a potentially shifting vertex.
    running = 0.0
    for index, (p0, p1) in enumerate(zip(points, points[1:])):
        length = math.dist(p0, p1)
        if start <= running+length+1e-9:
            fraction = (start-running)/length if length else 0.0
            projected = (p0[0]+fraction*(p1[0]-p0[0]), p0[1]+fraction*(p1[1]-p0[1]))
            points = [projected]+points[index+1:-1]+points[:index+1]
            break
        running += length
    clean = []
    for point in points:
        if not clean or math.dist(clean[-1], point) > 1e-9:
            clean.append(point)
    if len(clean) > 1 and math.dist(clean[-1], clean[0]) < 1e-9:
        clean.pop()
    points = clean
    count_vertices = len(points)
    if count_vertices < 3:
        return [[round(points[0][0], 5), round(points[0][1], 5)]]*count
    lengths = [math.dist(points[i], points[(i+1) % count_vertices]) for i in range(count_vertices)]
    turns = []
    for i, current in enumerate(points):
        previous, following = points[(i-1) % count_vertices], points[(i+1) % count_vertices]
        incoming = (current[0]-previous[0], current[1]-previous[1])
        outgoing = (following[0]-current[0], following[1]-current[1])
        turns.append(abs(math.atan2(incoming[0]*outgoing[1]-incoming[1]*outgoing[0],
                                    incoming[0]*outgoing[0]+incoming[1]*outgoing[1])))
    total_length, total_turn = sum(lengths), sum(turns)
    # Reserve points for curvature as well as length. Pure arc-length sampling
    # erases a 2px round cap on a 500px arm stroke even at 128 vertices.
    weights = [.55*length/total_length+.45*(turns[i]+turns[(i+1) % count_vertices])/(2*total_turn)
               for i, length in enumerate(lengths)]
    cumulative = [0.0]
    for weight in weights:
        cumulative.append(cumulative[-1]+weight)
    positions = [i/count for i in range(count)]
    # Retain actual sharp corners without changing the number of points.
    claimed = {0}
    for vertex, turn in sorted(enumerate(turns), key=lambda pair: -pair[1]):
        if turn < .4 or vertex == 0 or len(claimed) >= count//3:
            continue
        at = cumulative[vertex]
        nearest = min((i for i in range(1, count) if i not in claimed),
                      key=lambda i: abs(positions[i]-at))
        positions[nearest] = at
        claimed.add(nearest)
    result = []
    for position in sorted(positions):
        i = min(count_vertices-1, bisect.bisect_right(cumulative, position)-1)
        fraction = (position-cumulative[i])/weights[i] if weights[i] else 0.0
        p0, p1 = points[i], points[(i+1) % count_vertices]
        result.append([round(p0[0]+fraction*(p1[0]-p0[0]), 5),
                       round(p0[1]+fraction*(p1[1]-p0[1]), 5)])
    return result


def _rings(geometry, anchor, count):
    # Keep tiny islands last: if a self-intersection creates/removes a subpixel
    # island, the principal rings retain their slots in the animation.
    polygons = sorted(_polygons(make_valid(geometry)),
                      key=lambda p: (-round(p.area, 6),
                                     round(p.exterior.distance(Point(anchor)), 6),
                                     p.centroid.x, p.centroid.y))
    rings = []
    for polygon in polygons:
        polygon = orient(polygon, sign=1.0)
        rings.append(_resample_ring(polygon.exterior, anchor, count, True))
        holes = sorted(polygon.interiors, key=lambda r: (-Polygon(r).area, r.centroid.x, r.centroid.y))
        rings.extend(_resample_ring(hole, anchor, count, False) for hole in holes)
    return rings


def _role(name):
    name = name.lower()
    if any(word in name for word in ("grain", "salt")):
        return "grain"
    if any(word in name for word in ("sink", "lavabo", "water", "faucet")):
        return "sink"
    if any(word in name for word in ("arm", "hand", "moufle", "articulation")):
        return "arms"
    if any(word in name for word in ("spoon", "cuill", "prop")):
        return "prop"
    return "body"


class _Converter:
    def __init__(self, root, asset_dir, samples):
        self.root, self.asset_dir, self.samples = root, Path(asset_dir), samples
        self.ids = {node.get("id"): node for node in root.iter() if node.get("id")}
        self.curves, self.images = [], []
        self.order = 0
        self.paths = {}
        self.shape_cache = {}
        self.clip_cache = {}
        self._assign_paths(root, "")

    def _assign_paths(self, node, parent_path):
        # Explicit IDs reset the semantic path. Anonymous children are counted
        # before visibility/clipping, so one disappearing leaf cannot rename others.
        name = node.get("id") or _tag(node)
        path = name if node.get("id") else (parent_path+"/"+name).strip("/")
        self.paths[node] = path
        counters = {}
        for child in node:
            tag = _tag(child)
            index = counters.get(tag, 0)
            counters[tag] = index+1
            self._assign_paths(child, path)
            if not child.get("id"):
                old = self.paths[child]
                replacement = old+f"[{index}]"
                for descendant in child.iter():
                    if self.paths[descendant] == old or self.paths[descendant].startswith(old+"/"):
                        self.paths[descendant] = replacement+self.paths[descendant][len(old):]

    def shape(self, node):
        if node not in self.shape_cache:
            self.shape_cache[node] = _subpaths(node)
        return self.shape_cache[node]

    def raw(self, node, matrix=IDENTITY, trail=()):
        if node in trail:
            raise UnsupportedSVGError("Cyclic SVG use reference")
        tag = _tag(node)
        matrix = _mul(matrix, _transform(node.get("transform")))
        if tag in SHAPES:
            subpaths = self.shape(node)
            geometries = [_filled(subpaths)]
            geometries.extend(LineString(points) for points, _closed in subpaths if len(points) >= 2)
            return _affine(unary_union(geometries), matrix)
        if tag == "image":
            x, y = _number(node.get("x")), _number(node.get("y"))
            w, h = _number(node.get("width")), _number(node.get("height"))
            return _affine(Polygon([(x, y), (x+w, y), (x+w, y+h), (x, y+h)]), matrix)
        if tag == "use":
            ref = self.ids.get((node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#"))
            if ref is None:
                raise UnsupportedSVGError("Unresolved SVG use reference")
            matrix = _mul(matrix, (1, 0, 0, 1, _number(node.get("x")), _number(node.get("y"))))
            return self.raw(ref, matrix, trail+(node,))
        return unary_union([self.raw(child, matrix, trail+(node,)) for child in node
                            if _tag(child) not in NONRENDERED])

    def clip(self, value, matrix, node):
        match = re.fullmatch(r"url\(\s*['\"]?#([^)'\"\s]+)['\"]?\s*\)", value.strip())
        if not match or match[1] not in self.ids:
            raise UnsupportedSVGError(f"Unresolved SVG clip-path: {value}")
        clip_node = self.ids[match[1]]
        if _tag(clip_node) != "clipPath":
            raise UnsupportedSVGError(f"Clip reference is not a clipPath: {value}")
        if clip_node.get("clipPathUnits", "userSpaceOnUse") == "objectBoundingBox":
            # The bbox belongs to the referencing element's own coordinate system.
            base = unary_union([self.raw(child) for child in node if _tag(child) not in NONRENDERED]) \
                if _tag(node) not in SHAPES | {"image", "use"} else self.raw(node, _inverse(_transform(node.get("transform"))))
            if base.is_empty:
                return GeometryCollection()
            x0, y0, x1, y1 = base.bounds
            matrix = _mul(matrix, (x1-x0, 0, 0, y1-y0, x0, y0))
        key = (match[1], matrix)
        if key not in self.clip_cache:
            self.clip_cache[key] = self.clip_geometry(clip_node, matrix, DEFAULT_STYLE, ())
        return self.clip_cache[key]

    def clip_geometry(self, node, parent_matrix, inherited, trail):
        if node in trail:
            raise UnsupportedSVGError("Cyclic SVG clip reference")
        style = _style(node, inherited)
        if style.get("display") == "none":
            return GeometryCollection()
        matrix = _mul(parent_matrix, _transform(node.get("transform")))
        tag = _tag(node)
        if tag in SHAPES:
            geometry = _affine(_filled(self.shape(node), style.get("clip-rule", "nonzero")), matrix)
        elif tag == "use":
            ref = self.ids.get((node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#"))
            if ref is None:
                raise UnsupportedSVGError("Unresolved SVG clip use")
            matrix = _mul(matrix, (1, 0, 0, 1, _number(node.get("x")), _number(node.get("y"))))
            geometry = self.clip_geometry(ref, matrix, style, trail+(node,))
        else:
            geometry = unary_union([self.clip_geometry(child, matrix, style, trail+(node,)) for child in node
                                    if _tag(child) not in NONRENDERED])
        if style.get("clip-path", "none") != "none":
            geometry = geometry.intersection(self.clip(style["clip-path"], matrix, node))
        return geometry

    def image(self, node, matrix, opacity, clipping, name, role):
        href = node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or ""
        if not href.startswith("data:image/") or ";base64," not in href:
            raise UnsupportedSVGError("Only embedded base64 PNG/JPEG actor logos are allowed")
        header, encoded = href.split(",", 1)
        data = base64.b64decode(encoded, validate=False)
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in {"PNG", "JPEG"}:
                raise UnsupportedSVGError(f"Unsupported embedded logo format: {image.format}")
            iw, ih = image.size
            extension = ".png" if image.format == "PNG" else ".jpg"
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        target = self.asset_dir/(hashlib.sha256(data).hexdigest()[:20]+extension)
        if not target.exists():
            target.write_bytes(data)
        x, y = _number(node.get("x")), _number(node.get("y"))
        w, h = _number(node.get("width"), iw), _number(node.get("height"), ih)
        aspect = node.get("preserveAspectRatio", "xMidYMid meet").split()
        if aspect[0] != "none":
            scale = min(w/iw, h/ih)
            if len(aspect) > 1 and aspect[1] == "slice":
                raise UnsupportedSVGError("Embedded logo preserveAspectRatio=slice requires cropping")
            dw, dh = w-iw*scale, h-ih*scale
            x += dw*(0 if "xMin" in aspect[0] else 1 if "xMax" in aspect[0] else .5)
            y += dh*(0 if "YMin" in aspect[0] else 1 if "YMax" in aspect[0] else .5)
            w, h = iw*scale, ih*scale
        corners = [_point(matrix, p) for p in ((x, y), (x+w, y), (x+w, y+h), (x, y+h))]
        if clipping is not None and not clipping.buffer(1e-6).covers(Polygon(corners)):
            raise UnsupportedSVGError(f"Clipped embedded image needs explicit raster crop: {name}")
        # asset_dir is EP/assets/images; preserve an EP-relative path in the IR.
        relative = target.relative_to(self.asset_dir.parent.parent).as_posix()
        self.images.append({"id": name, "path": relative, "corners": corners,
                            "order": self.order, "role": role, "opacity": opacity})
        self.order += 1

    def visit(self, node, parent_matrix, inherited, opacity=1.0, clipping=None,
              use_prefix="", trail=(), inherited_role=None):
        tag = _tag(node)
        if tag in NONRENDERED:
            return
        if node in trail:
            raise UnsupportedSVGError("Cyclic SVG use reference")
        style = _style(node, inherited)
        if style.get("display") == "none":
            return
        for unsupported in ("filter", "mask"):
            if style.get(unsupported, "none") != "none":
                raise UnsupportedSVGError(f"Unsupported SVG {unsupported}: {style[unsupported]}")
        matrix = _mul(parent_matrix, _transform(node.get("transform")))
        opacity *= _number(_own_style(node).get("opacity"), 1.0)
        if style.get("clip-path", "none") != "none":
            own_clip = self.clip(style["clip-path"], matrix, node)
            clipping = own_clip if clipping is None else clipping.intersection(own_clip)
        name = use_prefix+self.paths[node]
        inherited_role = node.get("data-role") or inherited_role
        role = inherited_role or _role(name)
        if tag == "use":
            ref = self.ids.get((node.get("href") or node.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#"))
            if ref is None:
                raise UnsupportedSVGError("Unresolved SVG use")
            matrix = _mul(matrix, (1, 0, 0, 1, _number(node.get("x")), _number(node.get("y"))))
            self.visit(ref, matrix, style, opacity, clipping, name+"/", trail+(node,), inherited_role)
            return
        if tag == "image":
            if style.get("visibility") != "hidden" and opacity > 0:
                self.image(node, matrix, opacity, clipping, name, role)
            return
        if tag in SHAPES:
            subpaths = self.shape(node)
            if not subpaths or not subpaths[0][0] or style.get("visibility") == "hidden":
                return
            anchor = _point(matrix, subpaths[0][0][0])
            fill = _filled(subpaths, style.get("fill-rule", "nonzero"))
            fill_rgba = _color(style.get("fill", "black"), style,
                               opacity*_number(style.get("fill-opacity"), 1.0))
            stroke_rgba = _color(style.get("stroke", "none"), style,
                                 opacity*_number(style.get("stroke-opacity"), 1.0))
            paints = [("fill", fill, fill_rgba)]
            if stroke_rgba is not None and _number(style.get("stroke-width"), 1.0) > 0:
                if style.get("stroke-dasharray", "none") not in {"none", "0"}:
                    raise UnsupportedSVGError(f"Dashed SVG stroke is unsupported: {name}")
                cap = {"round": 1, "butt": 2, "square": 3}.get(style.get("stroke-linecap"), 2)
                join = {"round": 1, "miter": 2, "bevel": 3}.get(style.get("stroke-linejoin"), 2)
                lines = [LineString(points+([points[0]] if closed and points[-1] != points[0] else []))
                         for points, closed in subpaths if len(points) >= 2]
                if style.get("vector-effect", "none") == "non-scaling-stroke":
                    stroke = unary_union([_affine(line, matrix) for line in lines]).buffer(
                        _number(style.get("stroke-width"), 1.0)/2,
                        quad_segs=24, cap_style=cap, join_style=join,
                        mitre_limit=_number(style.get("stroke-miterlimit"), 4))
                    paints.append(("stroke", stroke, stroke_rgba))
                else:
                    stroke = unary_union([line.buffer(_number(style.get("stroke-width"), 1.0)/2,
                        quad_segs=24, cap_style=cap, join_style=join,
                        mitre_limit=_number(style.get("stroke-miterlimit"), 4)) for line in lines])
                    paints.append(("stroke", stroke, stroke_rgba))
            if style.get("paint-order", "normal").startswith("stroke"):
                paints.reverse()
            for kind, geometry, rgba in paints:
                order = self.order
                self.order += 1
                if rgba is None or rgba[3] <= 0:
                    continue
                if not (kind == "stroke" and style.get("vector-effect") == "non-scaling-stroke"):
                    geometry = _affine(geometry, matrix)
                if clipping is not None:
                    geometry = make_valid(geometry).intersection(clipping)
                rings = _rings(geometry, anchor, self.samples)
                if rings:
                    self.curves.append({"id": name+"."+kind, "rgba": rgba,
                                        "rings": rings, "role": role, "order": order})
            return
        if tag not in {"svg", "g", "a", "symbol", "switch"}:
            raise UnsupportedSVGError(f"Unsupported SVG rendered element: {tag}")
        for child in node:
            self.visit(child, matrix, style, opacity, clipping, use_prefix, trail+(node,), inherited_role)


def _inverse(matrix):
    a, b, c, d, e, f = matrix
    determinant = a*d-b*c
    if abs(determinant) < 1e-15:
        raise UnsupportedSVGError("Singular SVG transform")
    return (d/determinant, -b/determinant, -c/determinant, a/determinant,
            (c*f-d*e)/determinant, (b*e-a*f)/determinant)


def vectorize(svg_text, asset_dir, *, samples=128):
    """Return ``{'curves': [...], 'images': [...]}`` with real SVG clipping.

    ``asset_dir`` is the episode's ``assets/images`` folder. The function does
    not write JSON or reconcile topology across frames. Rings contain exactly
    ``samples`` vertices, omit the duplicate closing vertex, and are oriented
    exterior CCW / holes CW in the numeric SVG coordinate system.
    """
    if samples < 16:
        raise ValueError("At least 16 samples per ring are required")
    root = ET.fromstring(svg_text)
    if _tag(root) != "svg":
        raise ValueError("Expected an SVG root element")
    if any(_tag(node) == "style" and (node.text or "").strip() for node in root.iter()):
        raise UnsupportedSVGError("CSS stylesheets require explicit presentation/inline styles")
    converter = _Converter(root, asset_dir, int(samples))
    # Inputs use a canvas-sized viewBox; the returned IR preserves that user
    # coordinate system even if the SVG carries a different display resolution.
    converter.visit(root, IDENTITY, DEFAULT_STYLE)
    all_ids = [item["id"] for item in converter.curves+converter.images]
    if len(all_ids) != len(set(all_ids)):
        raise UnsupportedSVGError("Duplicate semantic paint IDs in SVG")
    return {"curves": converter.curves, "images": converter.images}


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--asset-dir", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=128)
    args = parser.parse_args()
    result = vectorize(args.svg.read_text(), args.asset_dir, samples=args.samples)
    args.output.write_text(json.dumps(result, separators=(",", ":")))
    print(f"{len(result['curves'])} clipped vector paints; {len(result['images'])} embedded logos")
