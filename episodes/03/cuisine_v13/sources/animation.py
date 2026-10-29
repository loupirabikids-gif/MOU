"""Acting and original-rig articulation for Encore une feuille.

The character is mou_rig, not a new drawing. Every moving limb is one native
_arm, posed through its existing hips/clasp controls and rigid shoulder rotation.
In the sink close-up only, reflection about the shoulder/grip axis turns the
same arm to the near side of the basin without changing its shape or reach.
Only the exterior boundary and ink within twenty-four local pixels of the left
shoulder are joined tangentially to the native body silhouette to remove the
notch explicitly marked by the user. Mitten contours,
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
from mou_rig import DEFAULT_POSE, _arm, _pt, _tangent, _cubic, _mouth, character_fragment

TIMELINE_PATH = Path(__file__).resolve().parents[1] / 'chronologie.json'
PRODUCTION_TIMELINE = json.loads(TIMELINE_PATH.read_text())
# Existing actions retain their approved timing/geometry in scene time.
# Production time drives the opening extension, edit order, stock and sound.
TIMELINE = PRODUCTION_TIMELINE.get('animation_reference', PRODUCTION_TIMELINE)
RETIME = PRODUCTION_TIMELINE.get('retiming', {})
ACTION_REORDER = PRODUCTION_TIMELINE.get('action_reorder', {})
PRODUCTION_SEGMENTS = PRODUCTION_TIMELINE.get('production_segments', [])
DURATION, FPS = PRODUCTION_TIMELINE['duration'], PRODUCTION_TIMELINE['fps']
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
BIN_LANDS = tuple(tuple(p) for p in PRODUCTION_TIMELINE['bin_layout']['centres'])
BIN_RADII = tuple(PRODUCTION_TIMELINE['bin_layout']['radii'])
BIN_ROTATIONS = tuple(PRODUCTION_TIMELINE['bin_layout']['rotations'])
BIN_SEEDS = tuple(PRODUCTION_TIMELINE['bin_layout']['visual_seeds'])
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


def _connect_left_root(fragment, rotation, reflect_axis=None):
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


def soften_left_root(fragment, rotation, reflect_axis=None):
    """Tangent exterior joint; fill/ink change is confined to the 24px root disk."""
    original=fragment
    fragment=_connect_left_root(fragment,rotation,reflect_axis)
    aa,ab,ba,bb=arm_linear_transform(rotation,reflect_axis)
    def body(p):
        dx,dy=p[0]-105.,p[1]-291.;return(105.+aa*dx+ab*dy,291.+ba*dx+bb*dy)
    def local(p):
        dx,dy=p[0]-105.,p[1]-291.;return(105.+aa*dx+ba*dy,291.+ab*dx+bb*dy)
    rawds=re.findall(r'<path d="([^"]+)"',original)
    ds=re.findall(r'<path d="([^"]+)"',fragment)
    def points(d):return[tuple(map(float,p))for p in re.findall(r'(-?[\d.]+) (-?[\d.]+)',d)]
    native=points(rawds[0]);current=points(ds[1])
    # Find the exterior edge at the root. A raised arm can start inside the
    # torso and cross its silhouette after the first point, still within21px.
    # Mirroring the native arm swaps the two endpoints in the sink inserts.
    first,last=body(native[0]),body(native[-1])
    if not _inside_body(first) and first[0]<105.:
        reverse=False
    elif not _inside_body(last) and last[0]<105.:
        reverse=True
    elif reflect_axis is None:
        def exits_near_root(sequence):
            for p in sequence:
                if math.dist(p,(105.,291.))>21.:
                    break
                q=body(p)
                if q[0]<105. and not _inside_body(q):
                    return True
            return False
        if exits_near_root(native):
            reverse=False
        elif exits_near_root(list(reversed(native))):
            reverse=True
        else:
            return fragment
    else:return fragment
    order=list(reversed(native))if reverse else native
    ordered_stroke=list(reversed(current))if reverse else current
    B=None
    for index in range(1,len(order)):
        if math.dist(order[index],(105.,291.))>=21.:
            if index>25:return fragment
            lo,hi=0.,1.
            for _ in range(30):
                mid=(lo+hi)/2.;p=point(order[index-1],order[index],mid)
                if math.dist(p,(105.,291.))<21.:lo=mid
                else:hi=mid
            native_b=point(order[index-1],order[index],(lo+hi)/2.)
            B=body(native_b);break
    if B is None or B[1]<278.:return fragment
    cs=((90.,310.),(100.,284.),(111.,241.),(124.,200.))
    lo,hi=0.,1.
    for _ in range(40):
        u=(lo+hi)/2.;p=_cubic(cs,u)
        if p[1]>271.:lo=u
        else:hi=u
    u=(lo+hi)/2.;A=_cubic(cs,u);tx,ty=_tangent(cs,u);T=(-tx,-ty)
    Q=body(order[index]);P=body(order[index-1]);vx,vy=Q[0]-P[0],Q[1]-P[1];vl=math.hypot(vx,vy);U=(vx/vl,vy/vl)
    span=math.dist(A,B);handle=min(12.,span/3.)
    C=(A[0]+T[0]*handle,A[1]+T[1]*handle);D=(B[0]-U[0]*handle,B[1]-U[1]*handle)
    curve=[_cubic((A,C,D,B),k/32.)for k in range(33)]
    if max(math.dist(p,(105.,291.))for p in curve)>21.1:return fragment
    new_order=[local(p)for p in curve]+order[index:]
    new_fill=list(reversed(new_order))if reverse else new_order
    # Main original ink from B onward. No alteration of the internal cap.
    j=next(j for j,p in enumerate(ordered_stroke)if math.dist(p,(105.,291.))>=21.)
    remain=[native_b]+ordered_stroke[j:]
    main=list(reversed(remain))if reverse else remain
    dfill='M'+' L'.join(f'{x:.3f} {y:.3f}'for x,y in new_fill)+' Z'
    dmain='M'+' L'.join(f'{x:.3f} {y:.3f}'for x,y in main)
    fragment=fragment.replace(ds[0],dfill,1).replace(ds[1],dmain,1)
    # Variable-width join follows the same curve and meets body6px and arm5.2px.
    edge1=[];edge2=[]
    for k,p in enumerate(curve):
        v=k/32.;dx,dy=_tangent((A,C,D,B),v);radius=3.-.4*smooth(v)
        edge1.append(local((p[0]-dy*radius,p[1]+dx*radius)))
        edge2.append(local((p[0]+dy*radius,p[1]-dx*radius)))
    ink=edge1+list(reversed(edge2));dink='M'+' L'.join(f'{x:.3f} {y:.3f}'for x,y in ink)+' Z'
    extra=f'<path d="{dink}" fill="#2B0A24" stroke="none" data-root-join="tangent"/>'
    fragment=fragment.replace('</g>',extra+'</g>',1)
    return fragment

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


# Six facial intentions use the same rig controls as the reviewed expression board.
FACE_STATES = {
    'envie': {'eye_open_l':1.,'eye_open_r':1.,'brow_raise':.30,
              'brow_l':0.,'brow_r':0.,'smile':.68,'mouth_open':.10},
    'doute': {'eye_open_l':.96,'eye_open_r':1.,'brow_raise':.10,
              'brow_l':.22,'brow_r':.04,'smile':-.13,'mouth_open':0.},
    'soulagement': {'eye_open_l':.81,'eye_open_r':.84,'brow_raise':.18,
                    'brow_l':0.,'brow_r':0.,'smile':.58,'mouth_open':0.},
    'concentration': {'eye_open_l':.90,'eye_open_r':.94,'brow_raise':.02,
                      'brow_l':-.23,'brow_r':-.18,'smile':.04,'mouth_open':0.},
    'reflexe': {'eye_open_l':1.,'eye_open_r':1.,'brow_raise':.42,
                'brow_l':.06,'brow_r':.15,'smile':-.10,'mouth_open':.05},
    'resistance': {'eye_open_l':.90,'eye_open_r':.94,'brow_raise':.05,
                   'brow_l':.22,'brow_r':.18,'smile':-.22,'mouth_open':0.},
}
KNIFE_LENGTH = 150.
KNIFE_PARK_GRIP = (500.,1310.)
KNIFE_PARK_ANGLE = math.radians(5.)
KNIFE_CUT_ANGLE = math.radians(20.)
KNIFE_EDGE_LOCAL = (94.,33.)
CARROT_STABILISE = (775.,1342.)


def face(pose, first, second=None, blend=0.):
    a=FACE_STATES[first]
    b=FACE_STATES[second] if second else a
    pose.update({key:mix(a[key],b[key],clamp(blend)) for key in a})


def knife_state(grip, angle=KNIFE_PARK_ANGLE, held=False):
    return {'knife_grip':grip,
            'knife_tip':(grip[0]+KNIFE_LENGTH*math.cos(angle),
                         grip[1]+KNIFE_LENGTH*math.sin(angle)),
            'knife_held':held}


def knife_cut_grip(index):
    """The belly passes completely through the carrot to the board plane."""
    ca,sa=math.cos(KNIFE_CUT_ANGLE),math.sin(KNIFE_CUT_ANGLE)
    a,b=KNIFE_EDGE_LOCAL
    return 655.+20.*index-(a*ca-b*sa),1380.-(a*sa+b*ca)


def roll_state_at(t, cycles=None):
    """Finite paper stock, consumed during pulls; cylinder height stays fixed."""
    stocks=(TIMELINE if cycles is None else PRODUCTION_TIMELINE)['paper_stock']
    remaining=float(stocks[0])
    pulling=False
    for cycle in CYCLES if cycles is None else cycles:
        i=cycle['id'];start,end=cycle['pull']
        if t>=end:
            remaining=float(stocks[i])
        elif t>=start:
            remaining=mix(float(stocks[i-1]),float(stocks[i]),smooth(progress(t,cycle['pull'])))
            pulling=True
            break
        else:break
    radius=math.sqrt(16.**2+(67.**2-16.**2)*remaining)
    return {'remaining':remaining,'empty':remaining<=0.,'pulling':pulling,
            'edge':(876.-radius,1175.),'hand':(876.-radius-2.,1217.),
            'tab_length':40. if remaining<=.006001 else 133.}


def whistle_at(t):
    """Lip opening follows each original audio note, including breath gaps."""
    for index,note in enumerate(TIMELINE.get('whistle_notes',[])):
        start,end=float(note['start']),float(note['end'])
        if start<=t<end:
            amount=smooth((t-start)/.020)*(1.-smooth((t-(end-.035))/.035))
            return {'active':amount>.001,'amount':amount,'note_index':index,
                    'phrase':note.get('phrase'),
                    'frequency_hz':note.get('frequency_hz'),
                    'start':start,'end':end}
    return {'active':False,'amount':0.,'note_index':None,'phrase':None}


def rhythm_at(t, playback_time=None):
    """Small culinary sway; decisive cutting and all cleaning remain still.

    Tomato grasp/flight use nearly the full native reach, so only the face
    plays the beat there. Stirring offsets both the held spoon and the body.
    The carrot preparation sway ends before the hands grip the knife.
    """
    bpm=float(TIMELINE.get('rhythm',{}).get('bpm',108.))
    cooking_windows=((0.,2.1),(8.5,9.3),(15.,17.45),(22.,22.5))
    cooking=any(a<=t<b for a,b in cooking_windows)
    movement_windows=((0.,2.1),(15.,15.30),(22.,22.5))
    clock=t
    if RETIME and t<2.1 and playback_time is not None:
        clock=playback_time
        movement_windows=((0.,RETIME['opening_stir_end']),)
    phase=(clock-.30)*bpm/60.
    envelope=0.
    for start,end in movement_windows:
        if start<=clock<end:
            ramp=min(.16,(end-start)*.32)
            envelope=smooth((clock-start)/ramp)*(1.-smooth((clock-(end-ramp))/ramp))
            break
    dx=12.*math.sin(math.pi*phase)*envelope
    dy=7.*math.cos(math.tau*phase)*envelope
    return {'bpm':bpm,'beat_phase':phase,'cooking':cooking,
            'body_envelope':envelope,'offset':[dx,dy],
            'contact_locked':15.30<=t<17.8 or 8.5<=t<9.3}


def whistling_mouth_svg(pose,amount):
    """One mouth morphs from the native smile into a small pursed O."""
    smile=clamp(pose.get('smile',0.),-1.,1.)
    op=clamp(pose.get('mouth_open',0.))
    width=mix(12.+12.*abs(smile),52.,op)
    yl,yr=mix(-5.*smile,-25.,op),mix(-9.*smile-8.*max(0.,smile),-31.,op)
    upper,lower=mix(20.*smile,-12.,op),mix(20.*smile,52.,op)
    original=[(-width,yl),(-width*.4,upper),(width*.4,upper),(width,yr),
              (width*.9,lower),(-width*.75,lower),(-width,yl)]
    rx,ry=6.5,8.5
    rounded=[(-rx,0.),(-rx,-ry*4./3.),(rx,-ry*4./3.),(rx,0.),
             (rx,ry*4./3.),(-rx,ry*4./3.),(-rx,0.)]
    points=[point(a,b,amount) for a,b in zip(original,rounded)]
    p=lambda q:f'{q[0]:.5f} {q[1]:.5f}'
    d=f'M{p(points[0])} C'+ ' '.join(p(q) for q in points[1:4])+' C'+' '.join(p(q) for q in points[4:])+' Z'
    return ('<g id="mouth" transform="translate(205 321)" data-expression="whistling">'
            f'<path d="{d}" fill="#2B0A24" stroke="#2B0A24" stroke-width="4.6" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')


def carrot_action(t, transform):
    """A chef knife's curved edge reaches the board under two real rounds."""
    left_rest,right_rest=rest_hand('left',transform),rest_hand('right',transform)
    # Lean first, then take the utensil. Both native hands are within reach
    # of the worktop; the knife no longer serves as an overlong diagonal rod.
    right=move(t,(15.35,15.60),right_rest,CARROT_STABILISE)
    left=move(t,(15.38,15.55),left_rest,KNIFE_PARK_GRIP)
    knife=knife_state(KNIFE_PARK_GRIP)
    cut1,cut2=knife_cut_grip(0),knife_cut_grip(1)
    up1,up2=(cut1[0],cut1[1]-72.),(cut2[0],cut2[1]-72.)
    if 15.55 <= t < 15.72:
        u=smooth(progress(t,(15.55,15.72)))
        left=point(KNIFE_PARK_GRIP,up1,u)
        knife=knife_state(left,mix(KNIFE_PARK_ANGLE,KNIFE_CUT_ANGLE,u),True)
    elif 15.72 <= t < 16.05:
        left=move(t,(15.72,16.05),up1,cut1)
        knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 16.05 <= t < 16.13:
        left=cut1;knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 16.13 <= t < 16.42:
        left=move(t,(16.13,16.42),cut1,up2)
        knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 16.42 <= t < 16.75:
        left=move(t,(16.42,16.75),up2,cut2)
        knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 16.75 <= t < 16.86:
        left=cut2;knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 16.86 <= t < 17.06:
        left=move(t,(16.86,17.06),cut2,(cut2[0],cut2[1]-60.))
        knife=knife_state(left,KNIFE_CUT_ANGLE,True)
    elif 17.06 <= t < 17.45:
        u=smooth(progress(t,(17.06,17.45)))
        left=point((cut2[0],cut2[1]-60.),KNIFE_PARK_GRIP,u)
        knife=knife_state(left,mix(KNIFE_CUT_ANGLE,KNIFE_PARK_ANGLE,u),True)
    elif t >= 17.45:
        left=arc_move(t,(17.45,17.8),KNIFE_PARK_GRIP,(475.,1165.),'left',transform)
        right=move(t,(17.45,17.8),CARROT_STABILISE,right_rest)
        knife=knife_state(KNIFE_PARK_GRIP)
    return left,right,knife


def _scene_state(t, playback_time=None, production_cycle=None):
    t=clamp(float(t),0.,DURATION)
    playback_time=t if playback_time is None else playback_time
    c=cycle_at(t)
    ordinal=production_cycle['id'] if production_cycle else (5 if c and c['id']==4 else c['id'] if c else 0)
    sink=c is not None and c['sink'][0] <= t < c['sink'][1]
    lean=smooth(progress(t,(15.,15.38)))*(1.-smooth(progress(t,(17.45,17.8))))
    rhythm=rhythm_at(t,playback_time)
    whistle=whistle_at(playback_time)
    dx,dy=rhythm['offset']
    transform=(140.,380.,SCALE) if sink else (80.+45.*lean+dx,380.+75.*lean+dy,SCALE)
    left,right=rest_hand('left',transform),rest_hand('right',transform)
    pose,paper,fly=dict(BASE),None,None
    face(pose,'envie')
    spoon={'grip':PARK_GRIP,'bowl':PARK_BOWL}
    spoon_held,wet_hand=False,False
    tomato=TOMATO_START if t < 9. else None
    tomato_added=t >= 9.3
    shot,phase,water,lever='wide','cuisine',False,0.
    intention,look='Préparer puis manger son plat.',(293.,1305.)
    left_override=None
    roll=roll_state_at(playback_time,PRODUCTION_TIMELINE['cycles'])
    roll_edge,roll_hand=roll['edge'],roll['hand']
    carrot={'body':(635.,1360.),'cuts':sum(t >= q for q in TIMELINE['carrot']['cut_times']),
            'cut_times':TIMELINE['carrot']['cut_times'],'t':t,
            **knife_state(KNIFE_PARK_GRIP)}

    if t < 2.1:
        contact_time=t*3.75/2.1
        if RETIME:
            loop=RETIME['native_stir_loop_seconds']
            contact_time=(playback_time%loop)*3.75/loop
        old=_stir.contact_at(contact_time)
        # The unchanged native arm and the held spoon share the body's sway.
        # This avoids keeping the old world-space grip while moving the torso.
        offset=(transform[0]-80.,transform[1]-380.)
        left=(old['grip'][0]+offset[0],old['grip'][1]+offset[1])
        left_override={'hips':0.,'clasp':.10,'rotation':old['left_rotation_deg'],
                       'hand':left,'target':left,'contact_error':0.,'grip_depth':12.}
        spoon,spoon_held={'grip':left,'bowl':(old['bowl'][0]+offset[0],old['bowl'][1]+offset[1])},True
        phase='remuer'
    elif t < 2.5:
        u=smooth(progress(t,(2.1,2.45)))
        old=_stir.contact_at(3.75)
        parked_meta=solve_arm('left',PARK_GRIP,transform)
        hips,clasp=mix(0.,parked_meta['hips'],u),mix(.10,parked_meta['clasp'],u)
        angle,depth=mix(old['left_rotation_deg'],parked_meta['rotation'],u),mix(12.,GRIP_DEPTH,u)
        left=world_grip('left',hips,clasp,angle,transform,depth)
        left_override={'hips':hips,'clasp':clasp,'rotation':angle,'hand':left,
                       'target':left,'contact_error':0.,'grip_depth':depth}
        raw_bowl=point(old['bowl'],PARK_BOWL,u)
        vx,vy=raw_bowl[0]-left[0],raw_bowl[1]-left[1]
        length=math.hypot(vx,vy)
        spoon={'grip':left,'bowl':(left[0]+135.*vx/length,left[1]+135.*vy/length)}
        spoon_held=t<2.45
        phase,intention='poser_cuillere','Poser la cuillère avant le premier rituel.'
        look=PARK_GRIP if t<2.42 else left
        face(pose,'envie','doute',smooth(progress(t,(2.30,2.50))))

    if c is not None:
        i=c['id']
        if i==2 and t<c['inspect'][0]:
            phase,intention='ajouter_tomate','Ajouter la tomate puis se surprendre à vouloir nettoyer.'
            if t<8.72:
                left=move(t,(8.5,8.72),rest_hand('left',transform),TOMATO_START)
                tomato=TOMATO_START
                look=TOMATO_START
            elif t<9.:
                left=move(t,(8.72,9.),TOMATO_START,(365.,1215.))
                tomato=left
                look=(301.,1300.)
            elif t<9.3:
                u=progress(t,(9.,9.3))
                left=arc_move(t,(9.,9.3),(365.,1215.),(465.,1170.),'left',transform)
                tomato=(mix(365.,301.,u),mix(1215.,1300.,u)-45.*math.sin(math.pi*u))
                look=(301.,1300.)
            else:
                left=move(t,(9.3,9.75),(465.,1170.),(475.,1165.))
                tomato=None
                look=left
                face(pose,'envie','doute',smooth(progress(t,(9.45,9.75))))
        elif i==3 and t<c['inspect'][0]:
            phase,intention='decouper_carotte','Deux coupes, couteau posé, puis le réflexe repart.'
            left,right,knife=carrot_action(t,transform)
            carrot.update(knife)
            face(pose,'concentration')
            look=(655.,1360.) if t<16.13 else (675.,1360.)
            if 16.75<=t<17.06:
                face(pose,'concentration','soulagement',.60)
                look=(627.,1374.)
            elif t>=17.06:
                look=KNIFE_PARK_GRIP if t<17.45 else left
                face(pose,'soulagement','doute',smooth(progress(t,(17.45,17.8))))
        elif i==4 and t<c['inspect'][0]:
            phase,intention='retoucher_manche','Reprendre le manche propre ; la main repart malgré lui.'
            if t<22.5:
                left=move(t,(22.,22.5),rest_hand('left',transform),PARK_GRIP)
                look=PARK_GRIP
            else:
                left=move(t,(22.56,22.85),PARK_GRIP,(475.,1165.))
                look=left if t>22.65 else PARK_GRIP
                face(pose,'reflexe')

        if c['inspect'][0] <= t < c['inspect'][1]:
            phase,intention='inspecter_main','Le contact suspend son plaisir ; regarder la même main.'
            if i==1:
                left=move(t,c['inspect'],PARK_GRIP,(475.,1165.))
            else:left=(475.,1165.)
            look=left if t<c['inspect'][1]-.06 else (102.,1130.)
            if i==1 and RETIME:
                look=left if playback_time<RETIME['opening_look_sink_from'] else (102.,1130.)
            face(pose,'reflexe' if i==4 else 'doute')

        if sink:
            shot,phase,intention='sink','laver','Ouvrir, laver la main qui vient de toucher, puis fermer.'
            control,wash_centre,initial=(215.,1100.),(102.,1166.),(535.,1165.)
            right=rest_hand('right',transform)
            opening,closing=c['open'],c['close']
            contact_t=opening[0]+.58*(opening[1]-opening[0])
            if t<contact_t:
                left=arc_move(t,(opening[0],contact_t),initial,control,'left',transform)
            elif t<opening[1]:
                left=control;lever=smooth(progress(t,(contact_t,opening[1])))
            elif t<c['wash'][0]:
                left=move(t,(opening[1],c['wash'][0]),control,wash_centre);lever=1.
            elif t<c['wash'][1]:
                u=progress(t,c['wash'])
                left=(wash_centre[0]+2.*math.sin(4.*math.pi*u),wash_centre[1]+2.*math.sin(6.*math.pi*u))
                lever=1.
            elif t<c['water'][1]:
                reach_end=c['water'][1]-.12
                left=move(t,(closing[0],reach_end),wash_centre,control)
                lever=1.-smooth(progress(t,(reach_end,c['water'][1])))
            else:
                left=arc_move(t,(c['water'][1],c['sink'][1]),control,initial,'left',transform)
            water=c['water'][0] <= t < c['water'][1]
            wet_hand=t>=c['wash'][0]
            look=left;face(pose,'doute')

        if c['paper'][0] <= t < c['paper'][1]:
            phase,intention='papier','Dérouler trop de papier, sécher, retrouver brièvement sa satisfaction.'
            wet_hand=t<c['wipe'][0]+.15
            reach,pull,wipe,crumple=c['reach'],c['pull'],c['wipe'],c['crumple']
            left_wait=(535.,1230.)
            face(pose,'doute')
            amount=float((production_cycle or c)['amount'])
            pull_finish=(520.-30.*(i-1),1280.)
            if t<reach[1]:
                left=move(t,reach,(475.,1165.),left_wait)
                right=arc_move(t,reach,rest_hand('right',transform),roll_hand,'right',transform)
                look=roll_hand
            elif t<pull[1]:
                u=progress(t,pull)
                if u<.42:
                    right=arc_point(roll_hand,(565.,1230.),smooth(u/.42),'right',transform)
                    left=left_wait;end=right
                else:
                    right=arc_point((565.,1230.),roll_hand,smooth((u-.42)/.45),'right',transform)
                    left=point(left_wait,pull_finish,smooth((u-.42)/.58));end=left
                paper={'mode':'pull','start':roll_edge,'end':end,'progress':u,'amount':amount}
                look=end
            elif t<wipe[1]:
                u=progress(t,wipe)
                settle=smooth(clamp(u/.28))
                left=point(pull_finish,(495.,1220.),settle)
                right=arc_point(roll_hand,(578.,1235.),settle,'right',transform)
                oscillation=math.sin(5.*math.pi*u)*math.sin(math.pi*u)
                right=(right[0]+13.*oscillation,right[1]-9.*oscillation)
                paper={'mode':'wipe','start':left,'end':right,'progress':u,'amount':amount}
                look=left
                face(pose,'doute','soulagement',smooth(clamp((u-.65)/.35)))
            else:
                u=progress(t,crumple)
                left=point((495.,1220.),(490.,1230.),smooth(u))
                right=point((578.,1235.),(555.,1230.),smooth(u))
                paper={'mode':'crumple','start':left,'end':right,'progress':u,'amount':amount}
                look=left;face(pose,'soulagement')

            if i==4:
                phase,intention='dernier_bout','Après trois grandes bandes, soigner le minuscule dernier bout.'
                tiny_hold=(690.,1235.)
                left=(500.,1220.)
                if t<reach[1]:
                    left=move(t,reach,(475.,1165.),(500.,1220.))
                    right=arc_move(t,reach,rest_hand('right',transform),roll_hand,'right',transform)
                    paper=None;look=roll_hand
                elif t<pull[1]:
                    u=smooth(progress(t,pull))
                    right=(roll_hand[0],mix(roll_hand[1],1225.,u))
                    paper={'mode':'tiny_pull','center':(right[0]-10.,right[1]-35.),
                           'start':roll_edge,'end':right,'progress':u,'amount':amount,'in_front':True}
                    look=right
                    face(pose,'doute')
                elif t<c['reveal'][1]:
                    right=move(t,(pull[1],25.30),(roll_hand[0],1225.),tiny_hold)
                    paper={'mode':'tiny','center':(right[0]-10.,right[1]-35.),
                           'start':right,'end':right,'progress':1.,'amount':amount,'in_front':True}
                    look=(876.,1175.) if 25.30<=t<25.55 else (right[0]-10.,right[1]-20.)
                    face(pose,'reflexe')
                elif t<wipe[1]:
                    u=progress(t,wipe)
                    if t<26.10:
                        right=move(t,(wipe[0],26.10),tiny_hold,(526.,1225.))
                        left=move(t,(wipe[0],26.10),(500.,1220.),(508.,1220.))
                    else:
                        rubbing=progress(t,(26.10,wipe[1]))
                        osc=math.sin(4.*math.pi*rubbing)*math.sin(math.pi*rubbing)
                        left=(508.,1220.)
                        right=(526.+10.*osc,1225.+5.*osc)
                    paper={'mode':'tiny_wipe','center':(right[0]-10.,right[1]-35.),
                           'start':left,'end':right,'progress':u,'amount':amount,'in_front':True}
                    look=(left[0]+10.,left[1]-15.)
                    face(pose,'concentration','soulagement',smooth(clamp((u-.72)/.28)))
                else:
                    u=progress(t,crumple)
                    left=point((508.,1220.),(500.,1230.),smooth(u))
                    right=point((526.,1225.),(520.,1230.),smooth(u))
                    centre=point((516.,1190.),left,smooth(u))
                    paper={'mode':'crumple','center':centre,'start':left,'end':right,
                           'progress':u,'amount':amount,'in_front':True}
                    look=left;face(pose,'soulagement')
                wet_hand=t<26.10

        if c['throw'][0] <= t < c['throw'][1]:
            phase,intention='jeter','Lâcher la boulette dans la même poubelle, qui garde les papiers précédents.'
            release,land=c['release'],c['land'];start=c['throw'][0]
            left=move(t,(start,release),(500. if i==4 else 490.,1230.),(430.,1215.))
            right=move(t,(start,release+.15),(520. if i==4 else 555.,1230.),rest_hand('right',transform))
            if t<release:
                paper={'mode':'ball','start':left,'end':left,'progress':progress(t,(start,release)),
                       'amount':float(c['amount']),'in_front':i==4}
            elif t<land:
                u=progress(t,(release,land))
                origin=solve_arm('left',(430.,1215.),transform)['hand']
                destination=BIN_LANDS[ordinal-1]
                control=(mix(origin[0],destination[0],.4),min(origin[1],destination[1])-145.)
                x=(1.-u)**2*origin[0]+2.*(1.-u)*u*control[0]+u**2*destination[0]
                y=(1.-u)**2*origin[1]+2.*(1.-u)*u*control[1]+u**2*destination[1]
                fly={'x':x,'y':y,'r':BIN_RADII[ordinal-1],
                     'rotation':(360.+BIN_ROTATIONS[ordinal-1])*u,'id':ordinal,
                     'visual_seed':BIN_SEEDS[ordinal-1]}
                left=move(t,(release,release+.28),(430.,1215.),rest_hand('left',transform))
            else:left=rest_hand('left',transform)
            if c['zoom'][0] <= t < c['zoom'][1]:shot='bin'
            look=(165.,1520.);face(pose,'soulagement')

    interception=False
    if t>=TIMELINE['final'][0]:
        phase,intention='satisfaction_derisoire','Admirer sa main propre, satisfait, devant le rouleau vide et le plat à peine avancé.'
        left=move(t,(28.5,28.95),rest_hand('left',transform),(475.,1165.))
        right=rest_hand('right',transform)
        look=left
        face(pose,'soulagement')

    # Actual original-arm geometry supplies each final grip and prop contact.
    lm=left_override if left_override is not None else solve_arm('left',left,transform)
    rm=solve_arm('right',right,transform)
    actual_left,actual_right=lm['hand'],rm['hand']
    if sink:
        shoulder=(transform[0]+105.*SCALE,transform[1]+291.*SCALE)
        lm['reflect_axis']=math.degrees(math.atan2(actual_left[1]-shoulder[1],actual_left[0]-shoulder[0]))
        lm['isometry_determinant']=-1.
    if spoon_held:spoon['grip']=actual_left
    if carrot['knife_held']:
        dx,dy=actual_left[0]-carrot['knife_grip'][0],actual_left[1]-carrot['knife_grip'][1]
        carrot['knife_grip']=actual_left
        carrot['knife_tip']=(carrot['knife_tip'][0]+dx,carrot['knife_tip'][1]+dy)
    if paper is not None:
        paper.update({'cycle':ordinal,'r':BIN_RADII[ordinal-1],'rotation':0.,
                      'tiny':bool((production_cycle or c).get('tiny',i==4)),
                      'visual_seed':BIN_SEEDS[ordinal-1]})
        if paper['mode']=='pull':paper['end']=actual_right if progress(t,c['pull'])<.42 else actual_left
        elif paper['mode'] in ('tiny_pull','tiny','tiny_wipe'):
            paper['center']=(actual_right[0]-10.,actual_right[1]-35.)
            paper['end']=actual_right
        else:paper['start'],paper['end']=actual_left,actual_right if paper['mode']!='ball' else actual_left
    if tomato is not None and 8.72<=t<9.:tomato=actual_left
    look_at(pose,look,transform)
    # Blinks stay off decisive contacts/cuts. Expressions keep their own lids.
    for centre in (.95,12.85,20.6):
        b=max(0.,1.-abs(t-centre)/.07)
        if b>0.:
            factor=1.-.92*smooth(b)
            pose['eye_open_l']*=factor;pose['eye_open_r']*=factor
            break
    if rhythm['cooking']:
        beat=rhythm['beat_phase']
        pose['brow_raise']+=.035*math.sin(math.tau*beat)
        pose['brow_l']+=.025*math.sin(math.pi*beat)
        pose['brow_r']-=.025*math.sin(math.pi*beat)
        enjoyment=.96+.04*math.cos(math.tau*beat)
        pose['eye_open_l']*=enjoyment
        pose['eye_open_r']*=enjoyment
    uid='mou-cuisine-v6'
    torso=character_fragment(pose,uid=uid)
    if whistle['amount']>0.:
        old_mouth=_mouth(pose,uid)
        assert torso.count(old_mouth)==1
        torso=torso.replace(old_mouth,whistling_mouth_svg(pose,whistle['amount']),1)
    for side in ('left','right'):
        native=_arm(side,pose['arm_hips'],pose['arm_clasp'])
        assert torso.count(native)==1
        torso=torso.replace(native,'',1)
    arms=draw_arm('left',lm)+draw_arm('right',rm)
    bin_count=sum(playback_time>=item['land'] for item in PRODUCTION_TIMELINE['cycles'])
    return {'t':t,'shot':shot,'phase':phase,'cycle':c['id'] if c else 0,
            'actor_transform':transform,'torso':torso,'arms':arms,
            'hands':{'left':actual_left,'right':actual_right},'arm_meta':{'left':lm,'right':rm},
            'spoon':spoon,'spoon_held':spoon_held,'tomato':tomato,'tomato_added':tomato_added,
            'paper':paper,'water':water,'lever':lever,'bin_count':bin_count,'flying_ball':fly,
            'wet_hand':wet_hand,'intention':intention,'pose':pose,'carrot':carrot,
            'interception':interception,'look_target':look,'roll':roll,
            'rhythm':rhythm,'whistle':whistle,
            'left_root_correction':{'scope_local_radius':24.,'method':'unchanged tangent native-body exterior join',
                                    'fill_changed':True,'fill_scope_local_radius':24.,'mitten_changed':False},
            'bin_lands':BIN_LANDS,'bin_radii':BIN_RADII}


def scene_time(t):
    """Map production time to the reviewed native actions without slowing them.

    V12 translates three segments to put the carrot before the tomato. The
    other material keeps V9's opening extension and exact 120-frame offset;
    sound and the opening sway use real playback time.
    """
    t=clamp(float(t),0.,DURATION)
    for segment in PRODUCTION_SEGMENTS:
        start,end=segment['output']
        if start<=t<end or t==DURATION==end:
            a,b=segment['source']
            if abs((end-start)-(b-a))<1.e-9:
                frame=round(t*FPS)
                shift=start-a
                if abs(t*FPS-frame)<1.e-8 and abs(shift*FPS-round(shift*FPS))<1.e-8:
                    return (frame-round(shift*FPS))/FPS
            return a+(t-start)*(b-a)/(end-start)
    for segment in ACTION_REORDER.get('segments', []):
        if segment['output'][0]<=t<segment['output'][1]:
            shift=segment['output'][0]-segment['source'][0]
            frame=round(t*FPS)
            if abs(t*FPS-frame)<1.e-8:
                return (frame-round(shift*FPS))/FPS
            return t-shift
    if not RETIME:
        return t
    if t<RETIME['opening_stir_end']:
        return t*2.1/RETIME['opening_stir_end']
    if t<RETIME['opening_hand_hold_from']:
        shift=RETIME['added_stir_seconds']
    elif t<RETIME['opening_inspect_end']:
        return CYCLES[0]['inspect'][1]-1.e-9
    else:
        shift=RETIME['later_shift_seconds']
    # Preserve exact frame-time values instead of accumulating float offsets.
    frame=round(t*FPS)
    if abs(t*FPS-frame)<1.e-8:
        return (frame-round(shift*FPS))/FPS
    return t-shift


def _distal_tip(side, meta, transform):
    """The original rounded cap's furthest point, not an invented fingertip."""
    return world_grip(side,meta['hips'],meta['clasp'],meta['rotation'],transform,19.)


def _solve_tip(side, target, transform):
    """Aim the native cap while retaining the existing arm solver unchanged."""
    meta=solve_arm(side,target,transform)
    for _ in range(8):
        tip=_distal_tip(side,meta,transform)
        adjusted=(meta['hand'][0]+target[0]-tip[0],meta['hand'][1]+target[1]-tip[1])
        meta=solve_arm(side,adjusted,transform)
    return meta


def _salt_motion(t):
    spec=PRODUCTION_TIMELINE['salt'];bowl=tuple(spec['bowl'])
    lean=smooth(progress(t,spec['reach']))*(1.-smooth(progress(t,spec['carry'])))
    transform=(80.+45.*lean,380.+75.*lean,SCALE)
    base_transform=(80.,380.,SCALE)
    resting=_distal_tip('left',solve_arm('left',rest_hand('left',base_transform),base_transform),base_transform)
    sprinkle=(365.,1230.)
    if t<spec['pinch'][0]:
        # Clear the bowl with the supporting hand before the pinch arrives.
        # This small staging gap makes the source of the grains visible.
        desired=arc_move(t,(spec['reach'][0]+.12,spec['reach'][1]),resting,bowl,'left',transform);phase='reach'
    elif t<spec['pinch'][1]:
        desired=bowl;phase='pinch'
    elif t<spec['sprinkle'][0]:
        desired=arc_move(t,spec['carry'],bowl,sprinkle,'left',transform);phase='carry'
    elif t<spec['sprinkle'][1]:
        u=progress(t,spec['sprinkle']);osc=math.sin(6.*math.pi*u)*math.sin(math.pi*u)
        desired=(sprinkle[0]+2.*osc,sprinkle[1]+4.*osc);phase='sprinkle'
    else:
        desired=move(t,(spec['sprinkle'][1],spec['inspect'][0]),sprinkle,(475.,1165.));phase='inspect'
    left=_solve_tip('left',desired,transform)
    right_rest=rest_hand('right',base_transform)
    if t<spec['reach'][1]:
        right_target=arc_move(t,(spec['reach'][0],spec['reach'][0]+.12),right_rest,CARROT_STABILISE,'right',transform)
    elif t<spec['sprinkle'][1]:
        right_target=CARROT_STABILISE
    else:
        right_target=arc_move(t,(spec['sprinkle'][1],spec['end']),CARROT_STABILISE,right_rest,'right',transform)
    right=solve_arm('right',right_target,transform)
    return transform,left,right,phase


def _torso_for_pose(pose,whistle):
    uid='mou-cuisine-v6'
    torso=character_fragment(pose,uid=uid)
    if whistle['amount']>0.:
        torso=torso.replace(_mouth(pose,uid),whistling_mouth_svg(pose,whistle['amount']),1)
    for side in ('left','right'):
        torso=torso.replace(_arm(side,pose['arm_hips'],pose['arm_clasp']),'',1)
    return torso


def _salt_emission_origins():
    spec=PRODUCTION_TIMELINE['salt'];out=[]
    for index in range(8):
        when=spec['sprinkle'][0]+index*.06
        tr,lm,_,_=_salt_motion(when)
        out.append({'time':when,'origin':_distal_tip('left',lm,tr),'target':tuple(spec['target'])})
    return tuple(out)


SALT_EMISSIONS=_salt_emission_origins()


def scene_state(t):
    playback_time=clamp(float(t),0.,DURATION)
    cycles=PRODUCTION_TIMELINE['cycles']
    cycle=next((c for c in cycles if c['trigger_start']<=playback_time<c['throw'][1]),None)
    state=_scene_state(scene_time(playback_time),playback_time,cycle)
    state.update(production_time=playback_time,production_cycle=cycle,native_cycle=state['cycle'],
                 cycle=cycle['id'] if cycle else 0)
    # All persistent objects follow the story clock, not a reused action clip.
    state['tomato_added']=playback_time>=PRODUCTION_TIMELINE['cooking_events']['tomato_contact']
    if playback_time<21.72:state['tomato']=TOMATO_START
    elif state['tomato_added']:state['tomato']=None
    if playback_time>=ACTION_REORDER['carrot_finished']:
        state['carrot'].update(cuts=2,t=TIMELINE['carrot']['end'])
    pose=state['pose'];look=state['look_target'];changed=False
    salt=PRODUCTION_TIMELINE['salt']
    if salt['start']<=playback_time<salt['end']:
        transform,left,right,salt_phase=_salt_motion(playback_time)
        state.update(actor_transform=transform,arm_meta={'left':left,'right':right},
                     hands={'left':left['hand'],'right':right['hand']},phase='ajouter_sel',shot='wide',
                     spoon=None,spoon_held=False,paper=None,wet_hand=False,water=False,lever=0.,
                     intention='Prendre une pincée de sel, assaisonner, puis vouloir rincer seulement le bout de la moufle.')
        state['arms']=draw_arm('left',left)+draw_arm('right',right)
        face(pose,'envie' if salt_phase in ('reach','pinch','carry','sprinkle') else 'reflexe')
        look=tuple(salt['bowl']) if salt_phase in ('reach','pinch') else tuple(salt['target']) if salt_phase in ('carry','sprinkle') else left['hand']
        state['salt_phase']=salt_phase;changed=True
    if 7.<=playback_time<7.75:
        face(pose,'reflexe');pose.update(brow_raise=.66,brow_l=.22,brow_r=.12,smile=-.22,mouth_open=.06)
        look=state['hands']['left'] if playback_time<7.5 else (102.,1130.)
        state['intention']='Le plaisir s’arrête net : fixer sa moufle avant de regarder le lavabo.';changed=True
    reveal=cycles[-1]['reveal']
    if reveal[0]<=playback_time<reveal[1]:
        u=progress(playback_time,reveal)
        look=(876.,1175.) if .24<=u<.61 else state['paper']['center']
        face(pose,'reflexe','concentration',smooth(clamp((u-.62)/.38)))
        pose['brow_raise']=mix(.62,-.08,smooth(clamp((u-.62)/.38)))
        if u>=.62:pose.update(eye_open_l=.72,eye_open_r=.76)
        state['intention']='Mesurer le dernier bout, vérifier le tube vide, puis décider de s’appliquer quand même.';changed=True
    if cycles[-1]['wipe'][0]<=playback_time<cycles[-1]['wipe'][1]:
        u=progress(playback_time,cycles[-1]['wipe'])
        if u<.72:pose.update(eye_open_l=.72,eye_open_r=.76,brow_l=-.28,brow_r=-.23)
        changed=True
    if playback_time>=PRODUCTION_TIMELINE['final'][0]:
        face(pose,'soulagement');pose.update(smile=.84,eye_open_l=.70,eye_open_r=.74,brow_raise=.24)
        look=state['hands']['left']
        a,b=PRODUCTION_TIMELINE['acting_polish']['proud_nod']
        u=progress(playback_time,(a,b));nod=5.*math.sin(math.pi*u)**2 if a<=playback_time<b else 0.
        if nod:
            x,y,scale=state['actor_transform'];state['actor_transform']=(x,y+nod,scale)
            state['hands']={side:(p[0],p[1]+nod) for side,p in state['hands'].items()}
            for meta in state['arm_meta'].values():
                for key in ('hand','target'):
                    meta[key]=(meta[key][0],meta[key][1]+nod)
            look=state['hands']['left']
        state['proud_nod_offset']=nod;changed=True
    if changed:
        state['look_target']=look;look_at(pose,look,state['actor_transform'])
        state['torso']=_torso_for_pose(pose,state['whistle'])
    left_meta=state['arm_meta']['left'];tip=_distal_tip('left',left_meta,state['actor_transform'])
    state['salt']={'bowl':tuple(salt['bowl']),'active':salt['start']<=playback_time<salt['end'],
                   'phase':state.get('salt_phase','idle'),'hand_side':'left','hand':state['hands']['left'],
                   'pinch_tip':tip,'pinch':salt['pinch'],'sprinkle':salt['sprinkle'],
                   'target':tuple(salt['target']),'progress':progress(playback_time,salt['sprinkle']),
                   'grains_on_hand':salt['pinch'][1]<=playback_time<salt['sprinkle'][1],
                   'emission_origins':SALT_EMISSIONS}
    return state


def pose_at(t):return scene_state(t)['pose']


def intention_at(t):return scene_state(t)['intention']


if __name__=='__main__':
    print(json.dumps({'duration':DURATION,'fps':FPS,'samples':[
        {k:v for k,v in scene_state(i/FPS).items() if k not in ('torso','arms')}
        for i in range(round(DURATION*FPS))]},ensure_ascii=False))
