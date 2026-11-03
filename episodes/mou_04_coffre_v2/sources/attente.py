"""V5: one continuous wait, with resting paws clear of the solid lockbox.

This post-performance correction uses film time only. It does not change the
rig, the prop contacts, or the phone actions before 4.25 s and from 23 s on.
All palm/elbow coordinates are the canonical world coordinates, before camera
mapping. The scene must draw the waiting arms and palms behind the whole box.
"""
from __future__ import annotations

from copy import deepcopy
import math

from personnage import BASE, POSES, face_parameters


def _ease(t, start, end):
    p = max(0., min(1., (t - start) / (end - start)))
    return p * p * (3. - 2. * p)


def _lerp(a, b, p):
    return a + (b - a) * p


def _blink(t, start, end):
    if start < t < end:
        return 1. - .99 * math.sin(math.pi * (t - start) / (end - start))
    return 1.


def apply_waiting(t, actor):
    """Return an independent actor; leave validated phone contacts intact."""
    out = deepcopy(actor)
    if not 4.25 <= t < 23.:
        return out

    # 608 + the mitten's approximately 44 px extent leaves visible air before
    # the box's nearest solid edge at x=662. Crossed arms are already clear.
    # Preserve the source's continuous transitions, shifting the same endpoint
    # and its elbow instead of redrawing or resizing the approved mitten.
    rest = _ease(t, 4.25, 4.65) * (1. - _ease(t, 15.2, 15.43))
    low = _ease(t, 18.15, 18.82)
    release = 1. - _ease(t, 22.42, 23.)
    if rest > 0.:
        # Crossed-arm interpolation already moves the source endpoint away
        # from the box. Fade its full 48 px cheek correction once, rather than
        # fading an already shrinking distance and bowing the paw toward it.
        rest_dx = (48. if t >= 15.2 else
                   max(0., out['hands']['right']['x'] - 608.))
        dx = rest_dx * rest
    else:
        dx = 62. * low
    dx *= release
    out['hands']['right']['x'] -= dx
    if 'right' in out.get('elbows', {}):
        ex, ey = out['elbows']['right']
        out['elbows']['right'] = (ex - .5 * dx, ey)

    if t < 16.25:
        return out

    # Continue the previous held look, rather than restarting it on minute 16.
    # The crossed-arms frustration slowly goes slack, then the existing body
    # descent brings PATCH down to the tabletop. One single wake-up follows.
    droop = _ease(t, 16.65, 17.70)
    descend = _ease(t, 18.15, 18.82)
    wake = _ease(t, 18.94, 19.10)
    resume = _ease(t, 22.42, 23.)
    tired = _ease(t, 16.60, 17.35)
    gaze_x = _lerp(.98, .84, tired)
    gaze_y = _lerp(1., .30, tired)
    gaze_x = _lerp(gaze_x, .88, descend)
    gaze_y = _lerp(gaze_y, -.10, descend)
    out['gaze'] = tuple(_lerp(value, old, resume)
                        for value, old in zip((gaze_x, gaze_y), actor['gaze']))
    tilt = _lerp(1.9, 1.2, droop)
    tilt = _lerp(tilt, 3.6, descend)
    out['head_tilt'] = _lerp(tilt, actor.get('head_tilt', 0.), resume)

    impatient = dict(POSES['impatient'])
    sleepy = dict(POSES['ennui'], open_l=.28, open_r=.32)
    eager = POSES['suppliant']
    waiting_face = {key: _lerp(impatient[key], sleepy[key], droop)
                    for key in BASE}
    waiting_face = {key: _lerp(waiting_face[key], eager[key], wake)
                    for key in BASE}
    source_face = face_parameters(actor)
    out.pop('pose_weights', None)
    out['face'] = {key: _lerp(waiting_face[key], source_face[key], resume)
                   for key in BASE}
    # A deliberate blink belongs to the awakening, never to a minute number.
    out['blink'] = _lerp(_blink(t, 18.84, 19.10),
                         actor.get('blink', 1.), resume)
    tail = 8. * math.sin((t - 15.43) * 5.6) * (1. - droop)
    out['tail_angle'] = _lerp(tail, actor.get('tail_angle', 0.), resume)
    out['performance_state'] = ('continuous_crossed_wait' if t < 18.15
                                else 'continuous_low_wait')
    return out
