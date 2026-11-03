"""MOU green: an independent, continuously poseable SVG puppet.

Coordinates use a 400 x 500 local canvas.  No raster artwork is embedded.
The two continuous limb contours include their mitten end; there is no
separate palm outline or wrist seam which could suggest another hand.
"""
from __future__ import annotations

import html
import math

PALETTE = {
    'outline': '#2B0A24', 'skin': '#D8F449',
    'eye_white': '#FFFDFD', 'tongue': '#F491A1',
    'background': '#EEE6FA', 'shadow': '#CEBCE6',
}


def _n(x):
    return f'{float(x):.3f}'


def _clamp(x, lo=0., hi=1.):
    return max(lo, min(hi, float(x)))


def _mix(a, b, t):
    return a + (b-a)*t


def _pt(a, b, t):
    return (_mix(a[0], b[0], t), _mix(a[1], b[1], t))


def _attrs(attrs):
    return ' '.join(f'{k.replace("_", "-")}="{html.escape(str(v), quote=True)}"'
                    for k, v in attrs.items())


def _path(d, fill='none', stroke=None, sw=5.2, **attrs):
    if stroke is None:
        stroke = PALETTE['outline']
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" {_attrs(attrs)}/>')


def _ellipse(cx, cy, rx, ry, fill, stroke='none', sw=0, **attrs):
    return (f'<ellipse cx="{_n(cx)}" cy="{_n(cy)}" '
            f'rx="{_n(rx)}" ry="{_n(ry)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" {_attrs(attrs)}/>')


def _cubic(points, t):
    a, b, c, d = points
    u = 1-t
    return (u*u*u*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t*t*t*d[0],
            u*u*u*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t*t*t*d[1])


def _tangent(points, t):
    a, b, c, d = points
    u = 1-t
    dx = 3*u*u*(b[0]-a[0])+6*u*t*(c[0]-b[0])+3*t*t*(d[0]-c[0])
    dy = 3*u*u*(b[1]-a[1])+6*u*t*(c[1]-b[1])+3*t*t*(d[1]-c[1])
    length = max(.00001, math.hypot(dx, dy))
    return dx/length, dy/length


def _arm(side, hips, clasp):
    # The same four control points are interpolated throughout every pose.
    # The forearm remains a single continuous widening ribbon and round end.
    if side == 'left':
        down = [(105, 291), (80, 311), (70, 341), (76, 367)]
        hip = [(105, 291), (24, 307), (40, 344), (118, 356)]
        folded = [(105, 291), (91, 344), (119, 386), (178, 389)]
    else:
        down = [(297, 291), (321, 310), (332, 340), (325, 367)]
        hip = [(297, 291), (377, 307), (361, 344), (283, 356)]
        folded = [(297, 291), (311, 344), (281, 386), (225, 389)]
    controls = [_pt(_pt(a, b, hips), c, clasp)
                for a, b, c in zip(down, hip, folded)]
    left, right = [], []
    count = 64
    for i in range(count+1):
        t = i/count
        x, y = _cubic(controls, t)
        tx, ty = _tangent(controls, t)
        # A narrow wrist leads to one rounded mitten, with no elbow lobe.
        hand = _clamp((t-.75)/.25)
        hand = hand*hand*(3-2*hand)
        radius = 10.5 + 8.5*hand
        left.append((x-ty*radius, y+tx*radius))
        right.append((x+ty*radius, y-tx*radius))
    ex, ey = controls[-1]
    tx, ty = _tangent(controls, 1)
    # Semicircle beyond the wrist: the single mitten end of the limb.
    tip = []
    for j in range(1, 25):
        a = math.pi*j/24
        tip.append((ex + (-ty*math.cos(a)+tx*math.sin(a))*19,
                    ey + (tx*math.cos(a)+ty*math.sin(a))*19))
    boundary = left + tip + list(reversed(right[:-1]))
    d = 'M'+' L'.join(f'{_n(x)} {_n(y)}' for x, y in boundary)+' Z'
    # Fill closes the shoulder; only the two sides and the tip are outlined.
    # Omitting a crosswise shoulder stroke gives a seamless torso attachment.
    stroke_d = 'M'+' L'.join(f'{_n(x)} {_n(y)}' for x, y in boundary)
    return (f'<g id="arm-{side}">'
            + _path(d, PALETTE['skin'], 'none', 0,
                    data_part='hand', data_side=side)
            + _path(stroke_d, sw=5.2)
            + '</g>')


def _eye(cx, cy, rx, side, p, uid):
    op = _clamp(p.get('eye_open_'+side, p.get('eye_open', 1)))
    laugh = _clamp(p.get('laugh', 0))
    op *= 1-laugh
    ry = 45
    # Keep the full oval for normal/half-lidded eyes. At the very end of
    # closure, morph its two contours into the same arc instead of fading
    # between two drawings (which would create a ghost oval over the arc).
    closing = 1-_clamp(op/.30)
    closing = closing*closing*(3-2*closing)
    clip = f'{uid}-eye-{side}'
    ink, white, skin = (PALETTE['outline'], PALETTE['eye_white'], PALETTE['skin'])
    xlook = _clamp(p.get('pupil_x', 0), -1, 1)*15
    ylook = _clamp(p.get('pupil_y', 0), -1, 1)*13
    lid = cy-ry+2*ry*(1-op)
    slant = 2 if side == 'l' else -2
    curve = _mix(2, -19, laugh)
    end_y = cy+6
    control_y = end_y+(curve-6)*2/3
    open_points = [(cx-rx, cy), (cx-rx, cy-ry*4/3),
                   (cx+rx, cy-ry*4/3), (cx+rx, cy),
                   (cx+rx, cy+ry*4/3), (cx-rx, cy+ry*4/3)]
    closed_points = [(cx-rx*.85, end_y), (cx-rx*.85/3, control_y),
                     (cx+rx*.85/3, control_y), (cx+rx*.85, end_y),
                     (cx+rx*.85/3, control_y), (cx-rx*.85/3, control_y)]
    points = [_pt(a, b, closing) for a, b in zip(open_points, closed_points)]
    coords = [' '.join((_n(x), _n(y))) for x, y in points]
    shape = f'M{coords[0]} C{coords[1]} {coords[2]} {coords[3]} C{coords[4]} {coords[5]} {coords[0]} Z'
    aperture = _path(shape, 'white', 'none', 0)
    out = [f'<defs><clipPath id="{clip}">{aperture}</clipPath></defs>',
           _path(shape, white, 'none', 0),
           f'<g clip-path="url(#{clip})">',
           _ellipse(cx+xlook, cy+2+ylook+17*(1-op), 9.3, 15, ink),
           _path(f'M{cx-rx-8} {cy-ry-8} H{cx+rx+8} '
                 f'V{_n(lid+slant)} Q{cx} {_n(lid+2)} '
                 f'{cx-rx-8} {_n(lid-slant)} Z', skin, 'none', 0),
           _path(f'M{cx-rx-6} {_n(lid-slant)} Q{cx} {_n(lid+2)} '
                 f'{cx+rx+6} {_n(lid+slant)}', sw=4.5,
                 opacity=_n(_clamp((1-op)*8))),
           '</g>', _path(shape, 'none', ink, 4.5)]
    return ''.join(out)


def _brows(p):
    base = 177-_clamp(p.get('brow_raise', 0), -1, 1)*14
    out = []
    for side, cx in [('l', 164), ('r', 242)]:
        b = _clamp(p.get('brow_'+side, 0), -1, 1)
        outer = base+b*15
        inner = base-b*15
        ya, yb = (outer, inner) if side == 'l' else (inner, outer)
        out.append(_path(f'M{cx-22} {_n(ya)} '
                         f'Q{cx} {_n(base-16+abs(b)*8)} {cx+22} {_n(yb)}', sw=7))
    return '<g id="brows">'+''.join(out)+'</g>'


def _mouth(p, uid):
    smile = _clamp(p.get('smile', 0), -1, 1)
    op = _clamp(p.get('mouth_open', 0))
    width = _mix(12+12*abs(smile), 52, op)
    yl = _mix(-5*smile, -25, op)
    yr = _mix(-9*smile-8*max(0., smile), -31, op)
    upper = _mix(20*smile, -12, op)
    lower = _mix(20*smile, 52, op)
    d = (f'M{-width:.3f} {yl:.3f} '
         f'C{-width*.4:.3f} {upper:.3f} {width*.4:.3f} {upper:.3f} '
         f'{width:.3f} {yr:.3f} '
         f'C{width*.9:.3f} {lower:.3f} {-width*.75:.3f} {lower:.3f} '
         f'{-width:.3f} {yl:.3f} Z')
    ink = PALETTE['outline']
    clip = f'{uid}-mouth'
    # The open and closed states share one outline topology.
    return ('<g id="mouth" transform="translate(205 321)">'
            + _path(d, ink, ink, 4.6)
            + f'<defs><clipPath id="{clip}">{_path(d, "white", "none", 0)}</clipPath></defs>'
            + f'<g clip-path="url(#{clip})" opacity="{_n(op)}">'
            + _ellipse(8, 25, 33, 15, PALETTE['tongue'])
            + '</g></g>')


def character_fragment(p: dict, uid='mou') -> str:
    """Return an SVG fragment, authored for the local viewBox 0 0 400 500.

    All pose values are continuous.  brow_l=brow_r=-1 forms angry V brows.
    Supported values are documented in the task and listed in DEFAULT_POSE.
    """
    p = {**DEFAULT_POSE, **p}
    hips = _clamp(p['arm_hips'])
    clasp = _clamp(p['arm_clasp'])
    ink = PALETTE['outline']
    skin = PALETTE['skin']
    out = []
    for side, cx in [('l', 151), ('r', 252)]:
        lift = _clamp(p['lift_'+side], 0, 20)
        y = 437-lift
        out.append(f'<g id="foot-{side}">')
        out.append(_path(f'M{cx-13} 402 L{cx-15} {_n(y)} '
                         f'L{cx+18} {_n(y)} L{cx+12} 402 Z', ink, ink, 2))
        out.append(_ellipse(cx, y, 27, 12, ink))
        out.append('</g>')
    body = ('M90 310 C100 284 111 241 124 200 '
            'C141 148 175 123 208 125 '
            'C224 124 234 128 246 132 '
            'C265 119 290 121 300 137 '
            'C310 152 304 171 301 188 '
            'C305 225 313 267 319 305 '
            'C331 350 321 388 297 403 '
            'C265 424 147 426 112 405 '
            'C82 390 74 350 90 310 Z')
    out.append('<g id="body">'+_path(body, skin, sw=6)+'</g>')
    out.append(_arm('left', hips, clasp))
    out.append(_arm('right', hips, clasp))
    out.append('<g id="face">')
    out.append(_eye(164, 235, 34, 'l', p, uid))
    out.append(_eye(242, 232, 33, 'r', p, uid))
    out.append(_brows(p))
    out.append(_mouth(p, uid))
    out.append('</g>')
    return ''.join(out)


DEFAULT_POSE = {
    'arm_hips': 0., 'arm_clasp': 0.,
    'eye_open_l': 1., 'eye_open_r': 1.,
    'pupil_x': 0., 'pupil_y': 0.,
    'brow_l': 0., 'brow_r': 0., 'brow_raise': 0.,
    'smile': 0., 'mouth_open': 0., 'laugh': 0.,
    'lift_l': 0., 'lift_r': 0.,
}
