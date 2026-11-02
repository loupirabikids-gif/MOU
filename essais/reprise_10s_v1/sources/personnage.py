"""MOU compact in flat SVG colours, with shared analytic face parameters.

The body contour and tall eyes retain the existing Galet study. This module
adds no arms or hands and does not import or modify the old production rig.
The coordinator owns the scene, cameras, chronology, props and renderer.
"""
from __future__ import annotations

import copy
import html
import json
import math
from pathlib import Path

PALETTE = json.loads(Path(__file__).with_name('palette.json').read_text())
# Exact contour from personnages/galet_v1/sources/rig.py.
BODY_PATH = ('M-235 25 C-245 -80 -195 -175 -78 -194 '
             'C40 -215 166 -196 220 -120 C280 -34 246 88 190 146 '
             'C130 206 -34 210 -140 168 C-208 139 -235 84 -235 25 Z')
BODY_PIVOT = (0., 190.)

BASE_FACE = dict(open_l=1., open_r=1., pupil=1.,
                 brow_l0=0., brow_lq=-17., brow_l1=0.,
                 brow_r0=0., brow_rq=-17., brow_r1=0.,
                 brow_raise_l=0., brow_raise_r=0.,
                 mouth_width=90., mouth_smile=.1, mouth_skew=0., mouth_open=0.,
                 mouth_y=91., blush=0., sweat=0.,
                 body_lean=0., body_sx=1., body_sy=1.)


def _pose(**changes):
    return dict(BASE_FACE, **changes)


POSES = {
    'neutre': _pose(),
    'assurance': _pose(open_l=.58, open_r=.69, pupil=1.08,
                       brow_l0=3., brow_lq=-12., brow_l1=11.,
                       brow_r0=-4., brow_rq=-25., brow_r1=3.,
                       brow_raise_r=7., mouth_width=115., mouth_smile=.9,
                       mouth_skew=.5, body_lean=-4., body_sx=1.025, body_sy=.985),
    'attention': _pose(open_l=1., open_r=1., pupil=.88,
                       brow_l0=3., brow_lq=-19., brow_l1=-4.,
                       brow_r0=-4., brow_rq=-19., brow_r1=3.,
                       brow_raise_l=8., brow_raise_r=8., mouth_width=47.,
                       mouth_smile=-.08, body_lean=3., body_sx=.99, body_sy=1.025),
    'panique': _pose(open_l=1., open_r=1., pupil=.64,
                     brow_l0=12., brow_lq=-20., brow_l1=-18.,
                     brow_r0=-18., brow_rq=-20., brow_r1=12.,
                     brow_raise_l=15., brow_raise_r=15., mouth_width=46.,
                     mouth_open=.74, mouth_y=90., sweat=1.,
                     body_lean=2., body_sx=.94, body_sy=1.065),
    'soulagement': _pose(open_l=.47, open_r=.47, pupil=1.05,
                         brow_l0=6., brow_lq=-10., brow_l1=4.,
                         brow_r0=4., brow_rq=-10., brow_r1=6.,
                         mouth_width=108., mouth_smile=.62,
                         body_lean=-2., body_sx=1.055, body_sy=.96),
    'gene': _pose(open_l=.65, open_r=.9, pupil=.95,
                  brow_l0=13., brow_lq=-12., brow_l1=-13.,
                  brow_r0=-5., brow_rq=-27., brow_r1=3.,
                  brow_raise_r=6., mouth_width=111., mouth_smile=.70,
                  mouth_skew=.95, blush=.36, sweat=.6,
                  body_lean=5., body_sx=.985, body_sy=.975),
}


def default_state():
    """blink=1 is open, 0 closed; hop>0 raises body and both feet."""
    return dict(pose='neutre', gaze=(0., 0.), blink=1., cx=540., floor_y=1370.,
                scale=1.20, sx=1., sy=1., tilt=0., hop=0., pose_posture=True)


def _n(value):
    return f'{float(value):.5f}'


def _clamp(value, low, high):
    return max(low, min(high, float(value)))


def face_parameters(state):
    """Optional pose_weights gives safe scalar blends, never polygon morphs.

    An optional face dict can override individual numeric parameters.
    """
    weights = state.get('pose_weights')
    if weights:
        items = [(name, max(0., float(weight))) for name, weight in weights.items()]
        if any(name not in POSES for name, _ in items):
            raise ValueError('Unknown pose in pose_weights')
        total = sum(weight for _, weight in items)
        if total <= 0:
            raise ValueError('pose_weights must contain a positive weight')
        result = {key:sum(POSES[name][key]*weight for name, weight in items)/total
                  for key in BASE_FACE}
    else:
        result = copy.deepcopy(POSES[state.get('pose', 'neutre')])
    for key, value in state.get('face', {}).items():
        if key not in BASE_FACE:
            raise ValueError('Unknown face parameter: '+key)
        result[key] = float(value)
    return result


def body_matrix(state):
    face = face_parameters(state)
    posture = bool(state.get('pose_posture', True))
    scale = float(state.get('scale', 1.2))
    sx = scale*float(state.get('sx', 1.))*(face['body_sx'] if posture else 1.)
    sy = scale*float(state.get('sy', 1.))*(face['body_sy'] if posture else 1.)
    angle = math.radians(float(state.get('tilt', 0.))+(face['body_lean'] if posture else 0.))
    c, s = math.cos(angle), math.sin(angle)
    a, b, cc, d = c*sx, s*sx, -s*sy, c*sy
    px, py = BODY_PIVOT
    x = float(state.get('cx', 540.))
    y = float(state.get('floor_y', 1370.))-float(state.get('hop', 0.))-42.*scale
    return a, b, cc, d, x-a*px-cc*py, y-b*px-d*py


def body_to_world(point, state):
    a, b, c, d, tx, ty = body_matrix(state)
    x, y = point
    return a*x+c*y+tx, b*x+d*y+ty


def _path(d, fill='none', width=7., stroke=None, extra=''):
    if stroke is None:
        stroke = PALETTE['ink']
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{_n(width)}" '
            f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def _ellipse(cx, cy, rx, ry, fill, extra=''):
    return (f'<ellipse cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" '
            f'ry="{_n(ry)}" fill="{fill}" {extra}/>')


def _eye_svg(side, cx, cy, face, state, uid):
    rx, ry = 58., 78.
    blink = _clamp(state.get('blink', 1.), 0., 1.)
    closing = 1.-blink
    # A shared pair of cubic curves closes into one shallow line. Its contour
    # stays analytically matched; no separately sampled fill/outline morph.
    upper = cy-ry*4./3.*blink+6.*closing
    lower = cy+ry*4./3.*blink+6.*closing
    edge_y = cy+6.*closing
    shape = (f'M{_n(cx-rx)} {_n(edge_y)} '
             f'C{_n(cx-rx)} {_n(upper)} {_n(cx+rx)} {_n(upper)} {_n(cx+rx)} {_n(edge_y)} '
             f'C{_n(cx+rx)} {_n(lower)} {_n(cx-rx)} {_n(lower)} {_n(cx-rx)} {_n(edge_y)} Z')
    clip = f'{uid}-eye-clip-{side}'
    parts = [f'<defs><clipPath id="{clip}"><path d="{shape}"/></clipPath></defs>',
             _path(shape, PALETTE['white'], 0., 'none', f'id="{uid}-eye-white-{side}"')]
    gx, gy = state.get('gaze', (0., 0.))
    px, py = _clamp(gx, -1., 1.)*20., _clamp(gy, -1., 1.)*21.
    pr = _clamp(face['pupil'], .45, 1.5)
    parts.append(f'<g clip-path="url(#{clip})">')
    parts.append(_ellipse(cx+px, cy+py, 16.*pr, 24.*pr, PALETTE['ink'],
                          f'id="{uid}-pupil-{side}"'))
    parts.append(_ellipse(cx+px-3., cy+py-6., 3., 4., PALETTE['white']))
    opening = _clamp(face['open_'+side], 0., 1.)
    if opening < .999:
        lid_y = cy-ry+2.*ry*(1.-opening)
        parts.append(_path(f'M{cx-rx-12} {cy-ry-14} H{cx+rx+12} V{lid_y+3} '
                           f'Q{cx} {lid_y-5} {cx-rx-12} {lid_y-3} Z',
                           PALETTE['body'], 0., 'none'))
        parts.append(_path(f'M{cx-rx-9} {lid_y-3} Q{cx} {lid_y-7} {cx+rx+9} {lid_y+3}', width=5.8))
    parts.append('</g>')
    parts.append(_path(shape, width=6.5, extra=f'id="{uid}-eye-outline-{side}"'))
    by = cy-ry-24.-face['brow_raise_'+side]
    parts.append(_path(f'M{cx-42} {by+face["brow_"+side+"0"]} '
                       f'Q{cx} {by+face["brow_"+side+"q"]} '
                       f'{cx+42} {by+face["brow_"+side+"1"]}',
                       width=9., extra=f'id="{uid}-brow-{side}"'))
    return ''.join(parts)


def _face_svg(face, state, uid):
    parts = [_eye_svg('l', -82., -42., face, state, uid),
             _eye_svg('r', 88., -48., face, state, uid)]
    width, y = face['mouth_width'], face['mouth_y']
    skew, smile, op = face['mouth_skew'], face['mouth_smile'], face['mouth_open']
    if op > .055:
        parts.append(_ellipse(4., y, width*.5, max(3., op*39.), PALETTE['ink'],
                              f'id="{uid}-mouth"'))
    else:
        parts.append(_path(f'M{4-width*.5} {y-skew*5} '
                           f'Q{4+skew*8} {y+smile*39} {4+width*.5} {y+skew*5}',
                           width=6.8, extra=f'id="{uid}-mouth"'))
    if face['blush'] > .005:
        for cx in (-151., 157.):
            parts.append(_ellipse(cx, 49., 25., 10., PALETTE['blush'],
                                  f'opacity="{_n(face["blush"])}"'))
    if face['sweat'] > .005:
        # One explicit stress cue, not a repeated shower of symbols.
        parts.append(_path('M191 -82 C190 -69 176 -57 180 -46 C183 -33 201 -34 204 -46 C207 -57 197 -70 191 -82 Z',
                           PALETTE['water'], 3.5, extra=f'opacity="{_n(face["sweat"])}" id="{uid}-sweat"'))
    return '<g id="'+uid+'-face">'+''.join(parts)+'</g>'


def character_svg(state, uid='mou'):
    """Return just the reusable character fragment, including local SVG defs.

    All supplied dimensions/positions are world SVG pixels. Feet stay anchored
    during squash/lean; hop translates the entire character off the floor.
    `pose_posture=False` leaves all body performance to the caller.
    """
    uid = html.escape(str(uid), quote=True)
    face = face_parameters(state)
    scale = float(state.get('scale', 1.2))
    cx = float(state.get('cx', 540.))
    fy = float(state.get('floor_y', 1370.))-float(state.get('hop', 0.))
    parts = [f'<g id="{uid}-character" data-character="mou-compact">']
    for side, dx, angle in (('l', -103., -7.), ('r', 109., 6.)):
        theta = math.radians(angle)
        vertical_radius = scale*math.hypot(40.*math.sin(theta), 16.*math.cos(theta))
        x, y = cx+dx*scale, fy-vertical_radius
        parts.append(f'<g id="{uid}-foot-{side}" data-part="foot" '
                     f'transform="rotate({angle} {_n(x)} {_n(y)})">'+
                     _ellipse(x, y, 40.*scale, 16.*scale, PALETTE['ink'])+'</g>')
    transform = ' '.join(_n(v) for v in body_matrix(state))
    parts.append(f'<g id="{uid}-body" transform="matrix({transform})">')
    parts.append(_path(BODY_PATH, PALETTE['body'], 8.5, extra=f'id="{uid}-body-outline"'))
    parts.append(_face_svg(face, state, uid))
    parts.append('</g></g>')
    return ''.join(parts)
