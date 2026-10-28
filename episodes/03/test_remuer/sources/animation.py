"""Four-second silent stirring contact study; the approved decor stays external.

All character artwork comes from mou_rig.  The left canonical arm is rotated
as one piece about its shoulder; the right arm remains the approved clasp.
All coordinates returned for the spoon/contact are world coordinates.
"""
from __future__ import annotations

import math
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'mou_rig.py').is_file())
sys.path.insert(0, str(ROOT))
from mou_rig import DEFAULT_POSE, character_fragment, _arm, _pt, _tangent

DURATION = 4.0
FPS = 24
STIR_START = .20
STIR_END = 3.75
STIR_RAMP = .16
X, Y, SCALE = 80.0, 380.0, 2.3
TRANSFORM = 'translate(80.0000 380.0000) scale(2.3000)'
BASE_POSE = {**DEFAULT_POSE, 'arm_hips': 0.0, 'arm_clasp': 1.0,
             'eye_open_l': 1.0, 'eye_open_r': 1.0,
             'pupil_x': 0.0, 'pupil_y': .18,
             'brow_raise': .08, 'smile': .12}
LEFT_CLASP = .10
SHOULDER_LOCAL = (105., 291.)
SHOULDER_WORLD = (X + SCALE * 105., Y + SCALE * 291.)
PAN_CENTER = (293., 1305.)
PAN_INTERIOR = {'center': (293., 1304.), 'radii': (114., 34.)}
SPOON_LENGTH = 135.0  # bowl centre to the centre of the actual mitten grip


def _clamp(v, a=0., b=1.):
    return max(a, min(b, v))


def _smooth(v):
    v = _clamp(v)
    return v*v*(3. - 2.*v)


def _controls(clasp):
    """Use the original rig's four left-arm control points, unchanged."""
    down = [(105, 291), (80, 311), (70, 341), (76, 367)]
    folded = [(105, 291), (91, 344), (119, 386), (178, 389)]
    return [_pt(a, b, clasp) for a, b in zip(down, folded)]


def _native_grip(clasp=LEFT_CLASP):
    controls = _controls(clasp)
    tx, ty = _tangent(controls, 1.)
    ex, ey = controls[-1]
    # A point inside the rounded end of the ORIGINAL continuous mitten.
    return ex + 12.*tx, ey + 12.*ty


def phase_at(t):
    """A tiny preload, two uneven circuits, then a readable settled hold."""
    t = _clamp(float(t), 0., DURATION)
    start = -.22
    if t < STIR_START:
        return start - .12 * math.sin(math.pi * t / STIR_START)**2
    if t < STIR_END:
        elapsed = t - STIR_START
        length = STIR_END - STIR_START
        # Integrate a near-constant speed with short cosine entrance/exit
        # ramps. Their combined lost area equals one ramp duration.
        if elapsed < STIR_RAMP:
            travelled = .5*(elapsed - STIR_RAMP/math.pi
                              * math.sin(math.pi*elapsed/STIR_RAMP))
        elif elapsed > length - STIR_RAMP:
            remaining = length - elapsed
            tail = .5*(remaining - STIR_RAMP/math.pi
                        * math.sin(math.pi*remaining/STIR_RAMP))
            travelled = length - STIR_RAMP - tail
        else:
            travelled = elapsed - STIR_RAMP/2.
        eased = travelled / (length - STIR_RAMP)
        return start + 4.*math.pi*eased + .13*math.sin(4.*math.pi*eased)
    return start + 4.*math.pi


def contact_at(t):
    phase = phase_at(t)
    bowl = (PAN_CENTER[0] + 35.*math.cos(phase),
            PAN_CENTER[1] + 12.*math.sin(phase))
    native = _native_grip()
    native_vector = (native[0] - SHOULDER_LOCAL[0], native[1] - SHOULDER_LOCAL[1])
    radius = SCALE * math.hypot(*native_vector)
    dx, dy = bowl[0] - SHOULDER_WORLD[0], bowl[1] - SHOULDER_WORLD[1]
    distance = math.hypot(dx, dy)
    along = (radius*radius - SPOON_LENGTH*SPOON_LENGTH + distance*distance)/(2.*distance)
    across = math.sqrt(max(0., radius*radius - along*along))
    # Intersect shoulder/grip and spoon-length circles. Choose the hand to
    # the right of the pan so the implement points naturally into its bowl.
    grip = (SHOULDER_WORLD[0] + along*dx/distance + across*dy/distance,
            SHOULDER_WORLD[1] + along*dy/distance - across*dx/distance)
    arm_angle = math.degrees(math.atan2(grip[1]-SHOULDER_WORLD[1], grip[0]-SHOULDER_WORLD[0])
                             - math.atan2(native_vector[1], native_vector[0]))
    local_grip = ((grip[0]-X)/SCALE, (grip[1]-Y)/SCALE)
    return {'t': float(t), 'phase': phase, 'hand': grip, 'grip': grip,
            'grip_local': local_grip, 'native_grip_local': native,
            'bowl': bowl, 'spoon_length': SPOON_LENGTH,
            'left_clasp': LEFT_CLASP, 'left_rotation_deg': arm_angle,
            'shoulder': SHOULDER_WORLD, 'pan_interior': PAN_INTERIOR,
            'contact': 'left original mitten holds spoon; bowl remains inside pan'}


def pose_at(t):
    p = dict(BASE_POSE)
    phase = phase_at(t)
    # The eyes follow the near-left pan; the body and both feet are fixed.
    p['pupil_x'] = -.56 + .045*math.cos(phase)
    p['pupil_y'] = .83 + .045*math.sin(phase)
    p['brow_raise'] = .10 + .035*_smooth((t-.30)/.35)
    p['smile'] = .12 + .055*_smooth((t-2.75)/.8)
    # One short natural blink while keeping the action visible.
    blink = max(0., 1.-abs(float(t)-2.64)/.09)
    p['eye_open_l'] = p['eye_open_r'] = 1. - .97*_smooth(blink)
    return p


def character_at(p, uid='mou-remuer'):
    """Return the canonical, undeformed character fragment for a pose."""
    return character_fragment(p, uid=uid)


def actor_layers_at(t, uid='mou-remuer'):
    p = pose_at(t)
    torso = character_fragment(p, uid=uid)
    for side in ('left', 'right'):
        original_arm = _arm(side, p['arm_hips'], p['arm_clasp'])
        assert torso.count(original_arm) == 1
        torso = torso.replace(original_arm, '', 1)
    angle = contact_at(t)['left_rotation_deg']
    left = (f'<g id="left-shoulder-articulation" transform="rotate({angle:.9f} 105 291)">'
            + _arm('left', 0., LEFT_CLASP) + '</g>')
    right = _arm('right', 0., 1.)
    return {'torso': torso, 'arms_back': '', 'arms_front': left + right,
            'transform': TRANSFORM, 'pose': p}


def spoon_geometry_at(t):
    c = contact_at(t)
    hx, hy = c['grip']
    bx, by = c['bowl']
    vx, vy = (hx-bx)/SPOON_LENGTH, (hy-by)/SPOON_LENGTH
    butt = (hx + 28.*vx, hy + 28.*vy)
    angle = math.degrees(math.atan2(vy, vx))
    # Handle is behind the actual mitten. A short butt remains visible on
    # the other side of that same original hand, making the grip readable.
    svg = (f'<g id="cuillere-remuer">'
           f'<path d="M{bx:.6f} {by:.6f} L{butt[0]:.6f} {butt[1]:.6f}" '
           f'fill="none" stroke="#382035" stroke-width="14" stroke-linecap="round"/>'
           f'<path d="M{bx:.6f} {by:.6f} L{butt[0]:.6f} {butt[1]:.6f}" '
           f'fill="none" stroke="#DDAA81" stroke-width="8" stroke-linecap="round"/>'
           f'<ellipse cx="{bx:.6f}" cy="{by:.6f}" rx="17" ry="9" '
           f'transform="rotate({angle:.6f} {bx:.6f} {by:.6f})" '
           f'fill="#EDC69E" stroke="#382035" stroke-width="4"/>'
           '</g>')
    return {**c, 'butt': butt, 'angle_deg': angle, 'svg': svg,
            'layer': 'after unchanged decor accessories, before actor arms'}


def motion_at(t):
    return {'translate': (X, Y), 'scale': SCALE, 'body_deformation': None,
            'left_rotation_deg': contact_at(t)['left_rotation_deg'],
            'left_clasp': LEFT_CLASP, 'right_clasp': 1.}


def intention_at(t):
    if t < STIR_START:
        return 'Regarder la poêle et préparer un premier tour, cuillère déjà en prise.'
    if t < STIR_END:
        return 'Remuer deux fois dans la poêle en suivant son geste des yeux.'
    return 'Terminer le geste et tenir la cuillère dans la poêle.'
