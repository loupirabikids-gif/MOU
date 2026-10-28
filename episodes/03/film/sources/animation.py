"""Acting and original-rig articulation for Encore une feuille.

The character is mou_rig, not a new drawing. Every moving limb is one native
_arm, posed through its existing hips/clasp controls and rigid shoulder rotation.
In the sink close-up only, reflection about the shoulder/grip axis turns the
same arm to the near side of the basin without changing its shape or reach.
Only the ink within twenty-four local pixels of the left shoulder is joined to
the native body silhouette to remove the notch explicitly marked by the user. Mitten contours,
the right arm drawing, body and face are unchanged.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import re
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'mou_rig.py').is_file())
sys.path.insert(0, str(ROOT))
from mou_rig import DEFAULT_POSE, _arm, _pt, _tangent, _cubic, character_fragment

TIMELINE_PATH = ROOT / 'episodes/03/chronologie.json'
TIMELINE = json.loads(TIMELINE_PATH.read_text())
DURATION, FPS = TIMELINE['duration'], TIMELINE['fps']
CYCLES = TIMELINE['cycles']
_spec = importlib.util.spec_from_file_location('approved_stir_contact', ROOT / 'episodes/03/test_remuer/sources/animation.py')
_stir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stir)

BASE = {**DEFAULT_POSE, 'arm_clasp': 1., 'smile': .12, 'brow_raise': .08,
        'pupil_x': -.4, 'pupil_y': .8}
SCALE = 2.3
PARK_BOWL, PARK_GRIP = (337., 1308.), (468., 1275.)
TOMATO_START = (530., 1268.)
ROLL_EDGE = (810., 1175.)
ROLL_HAND = (807., 1217.)
BIN_LANDS = ((140., 1690.), (195., 1585.), (145., 1480.))
BIN_RADII = (55., 61., 65.)
BIN_ROTATIONS = (-12., 17., -8.)
SHOULDERS = {'left': (105., 291.), 'right': (297., 291.)}
GENERIC_HIPS = .7
GRIP_DEPTH = 16.  # Inside the original 19px rounded tip; no new palm or fingers.


def clamp(v, a=0., b=1.):
    return max(a, min(b, v))


def smooth(v):
    v = clamp(v)
    return v * v * (3. - 2. * v)


def progress(t, interval):
    return clamp((t - interval[0]) / max(.0001, interval[1] - interval[0]))


def mix(a, b, u):
    return a + (b - a) * u


def point(a, b, u):
    return (mix(a[0], b[0], u), mix(a[1], b[1], u))


def move(t, interval, a, b):
    return point(a, b, smooth(progress(t, interval)))


def arc_point(a, b, u, side, transform):
    """Travel around the shoulder, never through its unreachable inner circle."""
    x, y, scale = transform
    sx, sy = SHOULDERS[side]
    origin = (x + sx * scale, y + sy * scale)
    av, bv = (a[0] - origin[0], a[1] - origin[1]), (b[0] - origin[0], b[1] - origin[1])
    start, end = math.atan2(av[1], av[0]), math.atan2(bv[1], bv[0])
    delta = (end - start + math.pi) % (2. * math.pi) - math.pi
    angle, radius = start + delta * u, mix(math.hypot(*av), math.hypot(*bv), u)
    return origin[0] + radius * math.cos(angle), origin[1] + radius * math.sin(angle)


def arc_move(t, interval, a, b, side, transform):
    return arc_point(a, b, smooth(progress(t, interval)), side, transform)


def controls(side, hips, clasp):
    if side == 'left':
        down = [(105, 291), (80, 311), (70, 341), (76, 367)]
        hip = [(105, 291), (24, 307), (40, 344), (118, 356)]
        fold = [(105, 291), (91, 344), (119, 386), (178, 389)]
    else:
        down = [(297, 291), (321, 310), (332, 340), (325, 367)]
        hip = [(297, 291), (377, 307), (361, 344), (283, 356)]
        fold = [(297, 291), (311, 344), (281, 386), (225, 389)]
    return [_pt(_pt(a, b, hips), c, clasp) for a, b, c in zip(down, hip, fold)]


def native_grip(side, hips, clasp, depth=GRIP_DEPTH):
    cs = controls(side, hips, clasp)
    tx, ty = _tangent(cs, 1.)
    return cs[-1][0] + depth * tx, cs[-1][1] + depth * ty


def world_grip(side, hips, clasp, angle, transform, depth=GRIP_DEPTH):
    sx, sy = SHOULDERS[side]
    px, py = native_grip(side, hips, clasp, depth)
    rad = math.radians(angle)
    dx, dy = px - sx, py - sy
    local = (sx + dx * math.cos(rad) - dy * math.sin(rad),
             sy + dx * math.sin(rad) + dy * math.cos(rad))
    x, y, scale = transform
    return x + local[0] * scale, y + local[1] * scale


def rest_hand(side, transform):
    return world_grip(side, 0., 1., 0., transform)


def solve_arm(side, target, transform, hips=GENERIC_HIPS):
    """Match radial reach using native clasp; never stretch or scale a limb."""
    x, y, scale = transform
    sx, sy = SHOULDERS[side]
    dx, dy = (target[0] - x) / scale - sx, (target[1] - y) / scale - sy
    desired = math.hypot(dx, dy)
    def radius(c):
        p = native_grip(side, hips, c)
        return math.hypot(p[0] - sx, p[1] - sy)
    lo, hi = 0., 1.
    for _ in range(30):
        mid = (lo + hi) / 2.
        if radius(mid) < desired:
            lo = mid
        else:
            hi = mid
    clasp = (lo + hi) / 2.
    native = native_grip(side, hips, clasp)
    angle = math.degrees(math.atan2(dy, dx) - math.atan2(native[1] - sy, native[0] - sx))
    hand = world_grip(side, hips, clasp, angle, transform)
    return {'hips': hips, 'clasp': clasp, 'rotation': angle, 'hand': hand,
            'target': target, 'contact_error': math.dist(target, hand), 'grip_depth': GRIP_DEPTH}


def _body_polygon():
    """Sample the unchanged canonical body's cubic path for local intersections."""
    source = character_fragment(BASE, uid='body-geometry')
    data = re.search(r'<g id="body"><path d="([^"]+)"', source)[1]
    tokens = re.findall(r'[MCZ]|-?[\d.]+', data)
    assert tokens[0] == 'M'
    current, result = (float(tokens[1]), float(tokens[2])), []
    index = 3
    while index < len(tokens):
        command = tokens[index]
        index += 1
        if command == 'Z':
            break
        assert command == 'C'
        points = [current] + [(float(tokens[index+j]), float(tokens[index+j+1])) for j in (0, 2, 4)]
        result.extend(_cubic(points, k / 64.) for k in range(64))
        current, index = points[-1], index + 6
    result.append(current)
    return tuple(result)


BODY_POLYGON = _body_polygon()


def _inside_body(p):
    x, y = p
    inside = False
    previous = BODY_POLYGON[-1]
    for current in BODY_POLYGON:
        ax, ay = previous
        bx, by = current
        if (ay > y) != (by > y):
            if x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
        previous = current
    return inside


def _boundary_between(a, b):
    flag = _inside_body(a)
    lo, hi = 0., 1.
    for _ in range(34):
        u = (lo + hi) / 2.
        if _inside_body(point(a, b, u)) == flag:
            lo = u
        else:
            hi = u
    return point(a, b, (lo + hi) / 2.)


def arm_linear_transform(rotation, reflect_axis=None):
    """Orthogonal articulation: native size retained, determinant +1 or -1."""
    theta = math.radians(rotation)
    ca, sa = math.cos(theta), math.sin(theta)
    if reflect_axis is None:
        return ca, -sa, sa, ca
    phi = math.radians(2. * reflect_axis)
    a, b = math.cos(phi), math.sin(phi)
    return a * ca + b * sa, -a * sa + b * ca, b * ca - a * sa, -b * sa - a * ca


def soften_left_root(fragment, rotation, reflect_axis=None):
    """Meet body silhouette with local ink only; no fill/mask/mitten change.

    A rotated native arm may begin with an ink cap inside the torso. Where the
    first edge crosses the body within24px of the shoulder, start the ink exactly
    at that crossing. An edge already outside is extended back to the crossing.
    The original internal arm line in an ordinary folded pose remains intact if
    there is no body intersection within this strictly local budget.
    """
    aa, ab, ba, bb = arm_linear_transform(rotation, reflect_axis)
    def body_space(p):
        dx, dy = p[0] - 105., p[1] - 291.
        return (105. + aa * dx + ab * dy, 291. + ba * dx + bb * dy)
    def arm_space(p):
        dx, dy = p[0] - 105., p[1] - 291.
        return (105. + aa * dx + ba * dy, 291. + ab * dx + bb * dy)
    def connect_start(points):
        first = body_space(points[0])
        if not _inside_body(first):
            intersection = arm_space(_boundary_between((105., 291.), first))
            assert math.dist(intersection, (105., 291.)) <= 24.
            return [intersection] + points
        previous = first
        for index, p in enumerate(points[1:], 1):
            if math.dist(p, (105., 291.)) > 24.:
                break
            transformed = body_space(p)
            if not _inside_body(transformed):
                intersection = arm_space(_boundary_between(previous, transformed))
                assert all(math.dist(q, (105., 291.)) <= 24. for q in points[:index])
                return [intersection] + points[index:]
            previous = transformed
        return points
    def repair(match):
        pts = [(float(x), float(y)) for x, y in re.findall(r'(-?[\d.]+) (-?[\d.]+)', match[2])]
        result = list(reversed(connect_start(list(reversed(connect_start(pts))))))
        d = 'M' + ' L'.join(f'{px:.3f} {py:.3f}' for px, py in result)
        return match[1] + d + match[3]
    repaired, count = re.subn(r'(<path d=")([^"]+)(" fill="none" stroke=)', repair, fragment)
    assert count == 1
    return repaired


def draw_arm(side, meta):
    sx, sy = SHOULDERS[side]
    fragment = _arm(side, meta['hips'], meta['clasp'])
    reflect_axis = meta.get('reflect_axis')
    if side == 'left':
        fragment = soften_left_root(fragment, meta['rotation'], reflect_axis)
    if reflect_axis is None:
        transform = f'rotate({meta["rotation"]:.8f} {sx} {sy})'
    else:
        aa, ab, ba, bb = arm_linear_transform(meta['rotation'], reflect_axis)
        ex, ey = sx - aa * sx - ab * sy, sy - ba * sx - bb * sy
        transform = f'matrix({aa:.10f} {ba:.10f} {ab:.10f} {bb:.10f} {ex:.10f} {ey:.10f})'
    return (f'<g id="articulation-{side}" transform="{transform}">'
            + fragment + '</g>')


def cycle_at(t):
    for c in CYCLES:
        if c['trigger_start'] <= t < c['throw'][1]:
            return c
    return None


def look_at(pose, target, transform):
    x, y, scale = transform
    eye = (x + scale * 202., y + scale * 234.)
    dx, dy = target[0] - eye[0], target[1] - eye[1]
    pose['pupil_x'] = clamp(dx / 310., -.92, .92)
    pose['pupil_y'] = clamp(dy / 340., -.88, .88)


def scene_state(t):
    t = clamp(float(t), 0., DURATION)
    c = cycle_at(t)
    sink = c is not None and c['sink'][0] <= t < c['sink'][1]
    transform = (140., 380., SCALE) if sink else (80., 380., SCALE)
    left, right = rest_hand('left', transform), rest_hand('right', transform)
    pose, paper, fly = dict(BASE), None, None
    spoon = {'grip': PARK_GRIP, 'bowl': PARK_BOWL}
    spoon_held, wet_hand = False, False
    tomato = TOMATO_START if t < 10.4 else None
    tomato_added = t >= 10.85
    shot, phase, water, lever = 'wide', 'cuisine', False, 0.
    intention, look = 'Cuisiner avec plaisir.', (293., 1305.)
    left_override = None

    if t < 2.2:
        old_t = t * 3.75 / 2.2
        old = _stir.contact_at(old_t)
        left = old['grip']
        left_override = {'hips': 0., 'clasp': .10, 'rotation': old['left_rotation_deg'],
                         'hand': left, 'target': left, 'contact_error': 0., 'grip_depth': 12.}
        spoon, spoon_held = {'grip': left, 'bowl': old['bowl']}, True
        phase = 'remuer'
    elif t < 2.6:
        u = smooth((t - 2.2) / .4)
        old = _stir.contact_at(3.75)
        parked_meta = solve_arm('left', PARK_GRIP, transform)
        hips, clasp = mix(0., parked_meta['hips'], u), mix(.10, parked_meta['clasp'], u)
        angle, depth = mix(old['left_rotation_deg'], parked_meta['rotation'], u), mix(12., GRIP_DEPTH, u)
        left = world_grip('left', hips, clasp, angle, transform, depth)
        left_override = {'hips': hips, 'clasp': clasp, 'rotation': angle, 'hand': left,
                         'target': left, 'contact_error': 0., 'grip_depth': depth}
        raw_bowl = point(old['bowl'], PARK_BOWL, u)
        vx, vy = raw_bowl[0] - left[0], raw_bowl[1] - left[1]
        length = math.hypot(vx, vy)
        spoon = {'grip': left, 'bowl': (left[0] + 135. * vx / length, left[1] + 135. * vy / length)}
        spoon_held = t < 2.58
        phase, intention = 'poser_cuillere', 'Poser la cuillère dans la poêle avant de se laver.'

    if c is not None:
        i = c['id']
        if i == 2 and t < c['inspect'][0]:
            phase, intention = 'ajouter_tomate', 'Ajouter une tomate avec la main gauche.'
            if t < 10.05:
                left = move(t, (9.75, 10.05), rest_hand('left', transform), TOMATO_START)
                tomato = TOMATO_START
            elif t < 10.4:
                left = move(t, (10.05, 10.4), TOMATO_START, (365., 1215.))
                tomato = left
            elif t < 10.85:
                u = progress(t, (10.4, 10.85))
                left = arc_move(t, (10.4, 10.85), (365., 1215.), (465., 1170.), 'left', transform)
                tomato = (mix(365., 301., u), mix(1215., 1300., u) - 45. * math.sin(math.pi * u))
            else:
                left = move(t, (10.85, 11.1), (465., 1170.), (475., 1165.))
                tomato = None
            look = tomato if tomato is not None else (301., 1300.)
        elif i == 3 and t < c['inspect'][0]:
            phase, intention = 'retoucher_manche', 'Reprendre le manche propre, puis douter de sa main.'
            if t < 17.55:
                left = move(t, (17.1, 17.55), rest_hand('left', transform), PARK_GRIP)
            else:
                left = move(t, (17.7, 18.), PARK_GRIP, (475., 1165.))
            look = PARK_GRIP if t < 17.7 else left
            spoon_held = False  # He only touches the resting handle before abandoning it again.

        if c['inspect'][0] <= t < c['inspect'][1]:
            phase, intention = 'inspecter_main', 'Inspecter la main après le contact de cuisine.'
            if i == 1:
                left = move(t, c['inspect'], PARK_GRIP, (475., 1165.))
            else:
                left = (475., 1165.)
            look = left
            pose['smile'], pose['brow_raise'] = .02, .20

        if sink:
            shot, phase, intention = 'sink', 'laver', 'Ouvrir le robinet, laver la main gauche, puis fermer.'
            control = (215., 1100.)
            wash_centre = (102., 1166.)
            initial = (535., 1165.)
            right = rest_hand('right', transform)
            opening, closing = c['open'], c['close']
            contact_t = opening[0] + .58 * (opening[1] - opening[0])
            if t < contact_t:
                left = arc_move(t, (opening[0], contact_t), initial, control, 'left', transform)
                lever = 0.
            elif t < opening[1]:
                left = control
                lever = smooth(progress(t, (contact_t, opening[1])))
            elif t < c['wash'][0]:
                left = move(t, (opening[1], c['wash'][0]), control, wash_centre)
                lever = 1.
            elif t < c['wash'][1]:
                u = progress(t, c['wash'])
                left = (wash_centre[0] + 2. * math.sin(4. * math.pi * u),
                        wash_centre[1] + 2. * math.sin(6. * math.pi * u))
                lever = 1.
            elif t < c['water'][1]:
                reach_end = c['water'][1] - .12
                left = move(t, (closing[0], reach_end), wash_centre, control)
                lever = 1. - smooth(progress(t, (reach_end, c['water'][1])))
            else:
                left = arc_move(t, (c['water'][1], c['sink'][1]), control, initial, 'left', transform)
                lever = 0.
            water = c['water'][0] <= t < c['water'][1]
            wet_hand = t >= c['wash'][0]
            look = left
            pose['smile'], pose['brow_raise'] = .05, .12

        if c['paper'][0] <= t < c['paper'][1]:
            phase, intention = 'papier', 'Prendre une bande excessive, sécher la main et froisser.'
            wet_hand = t < c['wipe'][0] + .15
            reach, pull, wipe, crumple = c['reach'], c['pull'], c['wipe'], c['crumple']
            left_wait = (535., 1230.)
            if t < reach[1]:
                left = move(t, reach, (475., 1165.), left_wait)
                right = arc_move(t, reach, rest_hand('right', transform), ROLL_HAND, 'right', transform)
                look = ROLL_HAND
            elif t < pull[1]:
                u = progress(t, pull)
                if u < .42:
                    right = arc_point(ROLL_HAND, (565., 1230.), smooth(u / .42), 'right', transform)
                    left = left_wait
                    end = right
                else:
                    right = arc_point((565., 1230.), ROLL_HAND, smooth((u - .42) / .45), 'right', transform)
                    left = point(left_wait, (440., 1280.), smooth((u - .42) / .58))
                    end = left
                paper = {'mode': 'pull', 'start': ROLL_EDGE, 'end': end,
                         'progress': u, 'amount': 3. + .8 * (i - 1)}
                look = end
            elif t < wipe[1]:
                u = progress(t, wipe)
                settle = smooth(clamp(u / .28))
                left = point((440., 1280.), (495., 1220.), settle)
                right = arc_point(ROLL_HAND, (578., 1235.), settle, 'right', transform)
                oscillation = math.sin(5. * math.pi * u) * math.sin(math.pi * u)
                right = (right[0] + 13. * oscillation, right[1] - 9. * oscillation)
                paper = {'mode': 'wipe', 'start': left, 'end': right,
                         'progress': u, 'amount': 3. + .8 * (i - 1)}
                look = left
            else:
                u = progress(t, crumple)
                left = point((495., 1220.), (490., 1230.), smooth(u))
                right = point((578., 1235.), (555., 1230.), smooth(u))
                paper = {'mode': 'crumple', 'start': left, 'end': right,
                         'progress': u, 'amount': 3. + .8 * (i - 1)}
                look = left

        if c['throw'][0] <= t < c['throw'][1]:
            phase, intention = 'jeter', 'Jeter la grosse boulette et voir la poubelle se remplir.'
            release, land = c['release'], c['land']
            start = c['throw'][0]
            left = move(t, (start, release), (490., 1230.), (430., 1215.))
            right = move(t, (start, release + .15), (555., 1230.), rest_hand('right', transform))
            if t < release:
                paper = {'mode': 'ball', 'start': left, 'end': left,
                         'progress': progress(t, (start, release)), 'amount': 3. + .8 * (i - 1)}
            elif t < land:
                u = progress(t, (release, land))
                # Flight begins at the actual original mitten's grip, not a detached origin.
                origin = solve_arm('left', (430., 1215.), transform)['hand']
                destination = BIN_LANDS[i - 1]
                control = (mix(origin[0], destination[0], .4), min(origin[1], destination[1]) - 145.)
                x = (1. - u) ** 2 * origin[0] + 2. * (1. - u) * u * control[0] + u ** 2 * destination[0]
                y = (1. - u) ** 2 * origin[1] + 2. * (1. - u) * u * control[1] + u ** 2 * destination[1]
                fly = {'x': x, 'y': y, 'r': BIN_RADII[i - 1],
                       'rotation': (360. + BIN_ROTATIONS[i - 1]) * u, 'id': i}
                left = move(t, (release, release + .28), (430., 1215.), rest_hand('left', transform))
            else:
                left = rest_hand('left', transform)
            if c['zoom'][0] <= t < c['zoom'][1]:
                shot = 'bin'
            look = (165., 1520.)
            pose['smile'] = .17

    if t >= 24.2:
        phase, intention = 'satisfaction', 'Admirer sa main impeccable puis reprendre la cuisine.'
        if t < 24.7:
            left = move(t, (24.2, 24.7), rest_hand('left', transform), (475., 1165.))
        elif t < 25.05:
            left = (475., 1165.)
        elif t < 25.65:
            left = move(t, (25.05, 25.65), (475., 1165.), PARK_GRIP)
        else:
            u = progress(t, (25.65, 26.))
            left = (PARK_GRIP[0] + 4. * math.sin(math.pi * u), PARK_GRIP[1] - 4. * math.sin(math.pi * u))
            spoon_held = True
            spoon = {'grip': left, 'bowl': PARK_BOWL}
        look = left if t < 25.2 else (293., 1305.)
        pose['smile'], pose['brow_raise'] = .34, .12

    # Original arm geometry drives the final, actual contact coordinates.
    lm = left_override if left_override is not None else solve_arm('left', left, transform)
    rm = solve_arm('right', right, transform)
    actual_left, actual_right = lm['hand'], rm['hand']
    if sink:
        shoulder = (transform[0] + 105. * SCALE, transform[1] + 291. * SCALE)
        lm['reflect_axis'] = math.degrees(math.atan2(actual_left[1] - shoulder[1], actual_left[0] - shoulder[0]))
        lm['isometry_determinant'] = -1.
    if spoon_held:
        spoon['grip'] = actual_left
        if t >= 25.65:
            vx, vy = PARK_BOWL[0] - actual_left[0], PARK_BOWL[1] - actual_left[1]
            length = math.hypot(vx, vy)
            spoon['bowl'] = (actual_left[0] + 135. * vx / length,
                             actual_left[1] + 135. * vy / length)
    if paper is not None:
        paper['cycle'] = c['id']
        paper['r'] = BIN_RADII[c['id'] - 1]
        paper['rotation'] = 0.
        if paper['mode'] == 'pull':
            paper['end'] = actual_right if progress(t, c['pull']) < .42 else actual_left
        else:
            paper['start'], paper['end'] = actual_left, actual_right if paper['mode'] != 'ball' else actual_left
    if tomato is not None and 10.05 <= t < 10.4:
        tomato = actual_left
    look_at(pose, look, transform)
    # Brief blinks during transitions, not at the decisive contact/jet.
    for centre in (2.65, 11.15, 18.10, 24.55):
        b = max(0., 1. - abs(t - centre) / .085)
        pose['eye_open_l'] = pose['eye_open_r'] = 1. - .95 * smooth(b)
        if b > 0.:
            break
    torso = character_fragment(pose, uid='mou-papier')
    for side in ('left', 'right'):
        native = _arm(side, pose['arm_hips'], pose['arm_clasp'])
        assert torso.count(native) == 1
        torso = torso.replace(native, '', 1)
    arms = draw_arm('left', lm) + draw_arm('right', rm)
    bin_count = sum(t >= item['land'] for item in CYCLES)
    return {'t': t, 'shot': shot, 'phase': phase, 'cycle': c['id'] if c else 0,
            'actor_transform': transform, 'torso': torso, 'arms': arms,
            'hands': {'left': actual_left, 'right': actual_right}, 'arm_meta': {'left': lm, 'right': rm},
            'spoon': spoon, 'spoon_held': spoon_held, 'tomato': tomato,
            'tomato_added': tomato_added, 'paper': paper, 'water': water,
            'lever': lever, 'bin_count': bin_count, 'flying_ball': fly,
            'wet_hand': wet_hand, 'intention': intention, 'pose': pose,
            'left_root_correction': {'scope_local_radius': 24., 'method': 'native-body silhouette intersection',
                                     'fill_changed': False, 'mitten_changed': False},
            'bin_lands': BIN_LANDS, 'bin_radii': BIN_RADII}


def pose_at(t):
    return scene_state(t)['pose']


def intention_at(t):
    return scene_state(t)['intention']


if __name__ == '__main__':
    samples = []
    for k in range(round(DURATION * FPS)):
        state = scene_state(k / FPS)
        samples.append({key: value for key, value in state.items() if key not in ('torso', 'arms')})
    print(json.dumps({'duration': DURATION, 'fps': FPS, 'samples': samples}, ensure_ascii=False))
