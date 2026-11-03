"""Small, seated MOU reactions for the thirteen-shot lockbox edit.

This layer follows the inherited prop actions. It replaces the old suspended
jump, not the original MOU drawing or the validated pickup/locking gestures.
All coordinates below are the common world coordinates, before camera layout.
"""
from __future__ import annotations

from copy import deepcopy
import math

from jeu_support import BASE, POSES, face_parameters


def _ease(t, a, b):
    u = max(0., min(1., (t-a)/(b-a)))
    return u*u*(3.-2.*u)


def _lerp(a, b, p):
    return a+(b-a)*p


def _point(a, b, p):
    return tuple(_lerp(x, y, p) for x, y in zip(a, b))


def _rotate(xy, angle):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    return (xy[0]*c-xy[1]*s, xy[0]*s+xy[1]*c)


def _blink(t, a, b):
    if not a < t < b:
        return 1.
    return 1.-.99*math.sin(math.pi*(t-a)/(b-a))


def apply_mou_acting(t, actor):
    """Return an independent pose; do not change props or the native rig."""
    out = deepcopy(actor)

    # A short certainty beat belongs to the decision to lock the phone away.
    # Hold it long enough to read, then settle into work without a new gesture.
    if 4.6 <= t < 5.75:
        p = _ease(t, 5.3, 5.75)
        out['face'] = {key: _lerp(POSES['satisfait'][key], POSES['concentre'][key], p)
                       for key in BASE}

    # Two inherited pose boundaries used to restart a smile in the middle of
    # giving up. Keep the emotion continuous across the cut and the cheek move.
    if 9.5 <= t < 10.3:
        face = face_parameters(out)
        p = _ease(t, 9.5, 9.9)
        out['face'] = {key: _lerp(face[key], POSES['impatient'][key], p)
                       for key in BASE}
    if 12. <= t < 12.86:
        p = _ease(t, 12.3, 12.86)
        out['face'] = {key: _lerp(POSES['impatient'][key], POSES['ennui'][key], p)
                       for key in BASE}

    # One sustained look replaces the old minute-by-minute head resets. Keep
    # the cheek approach and the subsequent transition into folded arms intact.
    if 12.3 <= t < 15.2:
        hold = _ease(t, 12.3, 12.76)
        out['gaze'] = _point(out.get('gaze', (.9, .9)), (.92, .9), hold)
        out['head_tilt'] = _lerp(out.get('head_tilt', 0.), -7.2, hold)
        out['blink'] = min(out.get('blink', 1.), _blink(t, 14.24, 14.46))

    # The extended opening shot used to force a round mouth even after MOU
    # recovered his phone. Let recognition become a modest, closed smile.
    if 24.35 <= t < 24.7:
        out.pop('mouth_shape', None)
        out.pop('mouth_o_scale', None)
        face = face_parameters(out)
        p = _ease(t, 24.35, 24.7)
        face['mouth_open'] = _lerp(.18, .02, p)
        face['mouth_smile'] = _lerp(.2, .86, p)
        face['mouth_width'] = 63.
        out['face'] = face

    if t < 24.7:
        return out

    out.pop('pose_weights', None)
    out.pop('mouth_shape', None)
    out.pop('mouth_o_scale', None)
    # No airborne translation: a three-pixel release of breath is enough.
    grip = _ease(t, 24.84, 25.04)
    settle = _ease(t, 25.15, 25.75)
    pulse = max(0., min(1., (t-24.7)/.7))
    breath = 3.*math.sin(math.pi*pulse)**2*(1.-settle)
    # The old high retrieval let the left forearm share the smile's outline.
    # Lower the whole prop-and-two-palm assembly, with a separate elbow follow,
    # until it joins the unchanged final reading pose. The body does not drop.
    phone_drop = 85.*_ease(t, 24.7, 24.93)*(1.-_ease(t, 25.2, 25.75))

    right = {
        'x': _lerp(_lerp(750., 742., grip), 582., settle),
        'y': _lerp(_lerp(1190., 1155., grip)+breath, 1255., settle)+phone_drop,
        'rotation': _lerp(-10., 0., grip),
        'grip': _lerp(1., .85, settle),
    }
    # This is the very same moving phone binding used by jeu.phone_binding.
    # Once the second mitten touches, both palms share a rigid phone pose.
    offset = _point((25., -30.), (-42., -15.), grip)
    dx, dy = _rotate(offset, right['rotation'])
    phone = (right['x']+dx, right['y']+dy)
    dx, dy = _rotate((-42., 15.), right['rotation'])
    bound_left = (phone[0]+dx, phone[1]+dy)
    lift = _ease(t, 24.7, 24.84)
    approaching_left = (_lerp(390., 454., lift),
                        _lerp(1310., 1190., lift)+breath+phone_drop)
    left_xy = _point(approaching_left, bound_left, grip)
    out['hands'] = {
        'right': right,
        'left': {'x': left_xy[0], 'y': left_xy[1],
                 'rotation': _lerp(-12., -28., grip), 'grip': .85*grip},
    }
    out['elbows'] = {
        'left': _point((478., 1270.+breath), (434., 1295.), settle),
        'right': _point((718., 1250.+breath), (630., 1295.), settle),
    }
    for side in out['elbows']:
        x, y = out['elbows'][side]
        out['elbows'][side] = (x, y+.85*phone_drop)
    out.update(pose='joie', lean=(0., breath*(1.-settle)),
               head_shift=(0., 0.), head_tilt=_lerp(-2., -3., lift), head_scale=1.,
               body_tilt=0., tail_angle=0., seated=True, airborne=False,
               jump_spread=0., _phone_progress=grip,
               screen_glow=_lerp(.18*grip, .62, settle))

    # Pleasure remains directed at the phone. No broad laugh and no glance to
    # the audience: his absorption is the final irony against the blank paper.
    smile = _ease(t, 24.7, 25.15)
    face = {key: _lerp(POSES['joie'][key], POSES['idee'][key], settle)
            for key in BASE}
    face.update(open_l=_lerp(.94, 1., settle), open_r=_lerp(.94, 1., settle),
                mouth_open=.10*math.sin(math.pi*smile)**2,
                mouth_width=_lerp(63., 70., settle),
                mouth_smile=_lerp(.86, 1., smile),
                sparkle=_lerp(.25, .3, settle))
    out['face'] = face
    out['blink'] = _blink(t, 24.88, 25.08)
    out['gaze'] = _point(_point((1., .8), (.86, .56), lift), (.26, 1.), settle)
    # This legacy label also enables the native mitten's forward tangent
    # constraint. Keep it throughout the lowered return so the contour never
    # switches construction mid-gesture; it does not imply any jump here.
    out['performance_state'] = 'whole_body_joy'
    out['acting_intent'] = 'content_phone_series'
    return out
