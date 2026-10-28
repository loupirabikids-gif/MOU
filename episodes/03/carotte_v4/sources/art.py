"""Original SVG kitchen props for MOU's paper-towel episode.

World coordinates are the approved 1080 x 1920 kitchen coordinates.  This
module never changes the approved drawing, character, or production timeline.
All paper balls are deterministic so a landed ball remains visually identical.
"""
from __future__ import annotations

import math

INK = '#382035'
PAPER = '#FFFDF7'
LAVENDER = '#CDB4D0'
BIN_CENTRES = ((140., 1700.), (195., 1620.), (135., 1537.), (195., 1460.))
BIN_RADII = (47., 53., 59., 65.)
BIN_ROTATIONS = (-12., 17., -8., 12.)
# A spoon set on the pan rim remains within the original left hand's reach.
PARKED_BOWL = (337., 1308.)
PARKED_GRIP = (468., 1275.)


def _n(value):
    return f'{float(value):.4f}'


def _clamp(value, low=0., high=1.):
    return max(low, min(high, float(value)))


def _path(d, fill='none', stroke=INK, width=5., **attributes):
    attrs = ' '.join(f'{key.replace("_", "-")}="{value}"'
                     for key, value in attributes.items())
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{_n(width)}" stroke-linecap="round" '
            f'stroke-linejoin="round" {attrs}/>')


def _ellipse(x, y, rx, ry, fill, stroke='none', width=0., **attributes):
    attrs = ' '.join(f'{key.replace("_", "-")}="{value}"'
                     for key, value in attributes.items())
    return (f'<ellipse cx="{_n(x)}" cy="{_n(y)}" rx="{_n(rx)}" '
            f'ry="{_n(ry)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{_n(width)}" {attrs}/>')


def _ball(x, y, radius, rotation=0., seed=1):
    """One crushed sheet silhouette, including persistent asymmetric creases."""
    points = ((-.87, -.31), (-.54, -.74), (-.18, -.67), (.13, -.96),
              (.56, -.77), (.65, -.46), (.94, -.20), (.81, .19),
              (.95, .43), (.51, .77), (.12, .70), (-.22, .88),
              (-.62, .65), (-.65, .25), (-.95, .13))
    # Mirroring alternate balls makes their identities easy to retain.
    mirror = -1. if int(seed) % 2 == 0 else 1.
    pts = [(mirror * a * radius, b * radius) for a, b in points]
    outline = 'M' + ' L'.join(f'{_n(a)} {_n(b)}' for a, b in pts) + ' Z'
    r = radius
    folds = [
        f'M{-.54*r:.4f} {-.66*r:.4f} L{-.18*r:.4f} {-.15*r:.4f} L{-.40*r:.4f} {.40*r:.4f}',
        f'M{.13*r:.4f} {-.86*r:.4f} L{.03*r:.4f} {-.20*r:.4f} L{.52*r:.4f} {.02*r:.4f}',
        f'M{.70*r:.4f} {-.33*r:.4f} L{.33*r:.4f} {.26*r:.4f} L{.48*r:.4f} {.66*r:.4f}',
        f'M{-.62*r:.4f} {.56*r:.4f} L{-.11*r:.4f} {.25*r:.4f} L{.09*r:.4f} {.64*r:.4f}',
    ]
    return (f'<g transform="translate({_n(x)} {_n(y)}) rotate({_n(rotation)}) scale(1.13 1.25)">'
            + _path(outline, PAPER, INK, 4.2)
            + ''.join(_path(d, stroke='#C5B2C3', width=2.4) for d in folds)
            + '</g>')


def bin_svg(count: int, flying: dict | None = None) -> str:
    """Open wire basket; previous balls remain at fixed, visible positions.

    The bucket is drawn in front of the island.  The lattice deliberately
    leaves its contents readable at a small preview size.  ``count`` is the
    number of completed arrivals; ``flying`` is only the not-yet-landed ball.
    """
    count = max(0, min(4, int(count)))
    body = 'M55 1495 Q62 1635 86 1760 Q165 1790 244 1760 Q265 1635 275 1495 Z'
    out = [
        '<g id="poubelle-papier">',
        _ellipse(166, 1788, 132, 23, '#BDA6BD', opacity='.42'),
        _path(body, '#E7D8E5', '#745B7C', 6.),
        _ellipse(165, 1495, 110, 39, '#AD91B5', INK, 6.),
        _ellipse(165, 1497, 99, 30, '#DCC8DF', '#85698F', 3.),
    ]
    for index in range(count):
        x, y = BIN_CENTRES[index]
        out.append(_ball(x, y, BIN_RADII[index], BIN_ROTATIONS[index], index + 1))
    if flying is not None:
        out.append(_ball(float(flying['x']), float(flying['y']),
                         float(flying.get('r', BIN_RADII[min(count, 3)])),
                         float(flying.get('rotation', 0.)), count + 1))
    # Only the mesh is clipped; an incoming or overflowing ball stays whole.
    out.append(f'<defs><clipPath id="corbeille-maille"><path d="{body}"/></clipPath></defs>')
    mesh = []
    for x in range(-190, 351, 42):
        mesh.append(_path(f'M{x} 1487 L{x+209} 1776', stroke='#9B80A4', width=2.4, opacity='.55'))
    for x in range(25, 600, 42):
        mesh.append(_path(f'M{x} 1487 L{x-209} 1776', stroke='#9B80A4', width=2.4, opacity='.55'))
    out.append('<g clip-path="url(#corbeille-maille)">' + ''.join(mesh) + '</g>')
    out.extend([
        _path('M55 1495 Q66 1645 86 1760 Q165 1790 244 1760 Q266 1635 275 1495',
              stroke=INK, width=6.),
        _path('M55 1495 C59 1548 271 1548 275 1495', stroke=INK, width=7.),
        _path('M89 1764 Q165 1787 241 1764', stroke='#85698F', width=4.),
        '</g>',
    ])
    return ''.join(out)


def _strip(start, end, width, sag, progress):
    sx, sy = map(float, start)
    ex, ey = map(float, end)
    dx, dy = ex-sx, ey-sy
    length = max(1., math.hypot(dx, dy))
    nx, ny = -dy/length, dx/length
    if ny < 0.:
        nx, ny = -nx, -ny
    top = 10.
    # Grip points sit close to the top edge; paper hangs below the hands.
    a = (sx-top*nx, sy-top*ny)
    b = (ex-top*nx, ey-top*ny)
    c = (ex+width*nx, ey+width*ny)
    d = (sx+width*nx, sy+width*ny)
    dpath = (f'M{_n(a[0])} {_n(a[1])} '
             f'Q{_n((sx+ex)/2)} {_n((sy+ey)/2+sag)} {_n(b[0])} {_n(b[1])} '
             f'L{_n(c[0])} {_n(c[1])} '
             f'Q{_n((c[0]+d[0])/2)} {_n((c[1]+d[1])/2+sag)} {_n(d[0])} {_n(d[1])} Z')
    out = [_path(dpath, PAPER, INK, 4.8)]
    number = max(1, int(length/77.))
    for j in range(1, number+1):
        u = j/(number+1)
        px, py = sx+u*dx, sy+u*dy+2*sag*u*(1-u)
        out.append(_path(f'M{_n(px-6*nx)} {_n(py-6*ny)} '
                         f'L{_n(px+(width-7)*nx)} {_n(py+(width-7)*ny)}',
                         stroke='#CBB6C8', width=2.7, stroke_dasharray='4 7'))
    return ''.join(out)


def paper_svg(paper: dict | None, t: float = 0.) -> str:
    """Long pulled band, folded wiping band, or its progressive crushed ball.

    ``start`` and ``end`` are world grip points.  ``center`` may optionally
    override the crushing/ball anchor; otherwise the active ``start`` hand
    remains the anchor, avoiding a jump when that same hand throws the ball.
    """
    if not paper:
        return ''
    mode = paper.get('mode', 'pull')
    start = tuple(paper.get('start', (810., 1180.)))
    end = tuple(paper.get('end', (520., 1210.)))
    progress = _clamp(paper.get('progress', 0.))
    amount = float(paper.get('amount', 1.))
    width = 96. + 8.*_clamp(amount-1., 0., 3.)
    if mode == 'pull':
        result = _strip(start, end, width, 21.+17.*progress, progress)
    elif mode == 'wipe':
        # A folded bridge between the actual hands and an excessive hanging
        # tail makes the quantity remain visible during the drying gesture.
        sx, sy = map(float, start)
        ex, ey = map(float, end)
        midx, midy = (sx+ex)/2., (sy+ey)/2.
        tail_length = 137. + 25.*_clamp(amount-1., 0., 3.)
        tail = (f'M{_n(midx-26)} {_n(midy+27)} '
                f'L{_n(midx+53)} {_n(midy+35)} '
                f'L{_n(midx+29)} {_n(midy+25.+tail_length)} '
                f'L{_n(midx-51)} {_n(midy+14.+tail_length)} Z')
        result = (_path(tail, '#F5EFF2', INK, 4.5)
                  + _path(f'M{_n(midx-35)} {_n(midy+104)} l71 10',
                          stroke='#CBB6C8', width=2.5, stroke_dasharray='4 7')
                  + _strip(start, end, 72., 7., progress))
    elif mode == 'crumple':
        cx, cy = map(float, paper.get('center', start))
        # A single contracting silhouette, not a crossfade to a second object.
        r = float(paper.get('r', 55.))
        cycle = int(paper.get('cycle', 1))
        mirror = -1. if cycle % 2 == 0 else 1.
        jagged = ((-.87, -.31), (-.54, -.74), (-.18, -.67), (.13, -.96),
                  (.56, -.77), (.65, -.46), (.94, -.20), (.81, .19),
                  (.95, .43), (.51, .77), (.12, .70), (-.22, .88),
                  (-.62, .65), (-.65, .25), (-.95, .13))
        rectangle = ((-43,-28),(-13,-28),(15,-28),(43,-28),(65,-18),
                     (65,16),(65,51),(53,85),(38,132),(7,150),
                     (-21,146),(-48,132),(-61,93),(-62,45),(-56,10))
        pts = [((1-progress)*a+progress*mirror*b*r, (1-progress)*c+progress*d*r)
               for (a,c),(b,d) in zip(rectangle,jagged)]
        outline='M'+' L'.join(f'{_n(x)} {_n(y)}'for x,y in pts)+' Z'
        result=(f'<g transform="translate({_n(cx)} {_n(cy)}) scale({_n(1.+.13*progress)} {_n(1.+.25*progress)})">'
                +_path(outline,PAPER,INK,4.5)
                +_path(f'M{-26+7*progress:.4f} -14 L{14+3*progress:.4f} 21 '
                       f'L{-15+5*progress:.4f} {97-69*progress:.4f}',
                       stroke='#C5B2C3',width=2.5)+'</g>')
    elif mode == 'ball':
        cx, cy = map(float, paper.get('center', start))
        result = _ball(cx, cy, float(paper.get('r',55.)),
                       float(paper.get('rotation', 0.)), int(paper.get('cycle',1)))
    else:
        raise ValueError(f'Unknown paper mode: {mode}')
    return '<g id="papier-en-main">'+result+'</g>'


def water_svg(t: float, on: bool, hand: tuple | None = None) -> str:
    """Vertical tap stream in the real sink, with modest original droplets."""
    if not on:
        return ''
    t = float(t)
    ripple = 1.8*math.sin(t*21.)
    out = [
        '<g id="eau-robinet">',
        _path(f'M99 1070 Q{102+ripple:.4f} 1104 100 1141 '
              f'Q102 1145 107 1141 Q{105+ripple:.4f} 1102 105 1070 Z',
              '#B5DFE5', '#7FAFBA', 1.7, opacity='.92'),
        _path('M102 1074 V1134',stroke='#E8FBF9',width=2.2,opacity='.85'),
        _ellipse(103,1145,16,3.7,'none','#89B8BE',1.7,opacity='.75'),
    ]
    # Splashes are added around the hands, which will occlude the stream.
    hx, hy = (102., 1112.) if hand is None else map(float,hand)
    for j, side in enumerate((-1.,1.,-1.,1.)):
        u=(t*2.7+j*.247)%1.
        px=hx+side*(23.+u*24.)
        py=min(1143.,hy+2.+u*31.-13.*math.sin(math.pi*u))
        if py < 1144.:
            out.append(_ellipse(px,py,2.3,4.3,'#AFD8DF',opacity=_n(.8*(1.-u))))
    out.append('</g>')
    return ''.join(out)


def lever_tip(amount: float) -> tuple[float, float]:
    a=math.radians(-63.*_clamp(amount))
    return 202.+19.*math.cos(a)+11.*math.sin(a),1106.+19.*math.sin(a)-11.*math.cos(a)


def lever_svg(amount: float) -> str:
    """Replace only the original single lever path; keep the tap itself."""
    x,y=lever_tip(amount)
    return ('<g id="commande-robinet">'
            +_path('M202 1124 V1106',stroke='#6D596E',width=8.)
            +_ellipse(202,1106,5.,5.,'#857081','#6D596E',1.7)
            +_path(f'M202 1106 L{_n(x)} {_n(y)}',stroke='#6D596E',width=8.)
            +'</g>')


def tomato_svg(x: float, y: float, scale: float = 1.) -> str:
    """A small chopped tomato wedge, not a face or symbolic icon."""
    return (f'<g transform="translate({_n(x)} {_n(y)}) scale({_n(scale)})">'
            +_path('M-23 1 Q-13 -19 7 -17 Q22 -11 23 4 Q3 20 -23 1 Z',
                   '#DD745E',INK,3.8)
            +_path('M-17 1 Q0 -7 16 3 Q0 12 -17 1 Z','#F6AC7E','#BD6259',2.)
            +_ellipse(-7,1,2.,1.5,'#FFF0BA')+_ellipse(6,3,2.,1.4,'#FFF0BA')
            +'</g>')


def tomato_dish_svg(occupied: bool = False) -> str:
    """Small preparation saucer within reach of the original left hand.

    By default the animation owns the tomato, so only its persistent saucer
    is drawn. ``occupied`` is convenient for an isolated prop study.
    """
    return ('<g id="coupelle-tomate">'
            +_ellipse(530,1274,35,12,'#EBD8D0',INK,3.5)
            +_ellipse(530,1272,28,7,'#FFF6E9','#C9ACB3',2.)
            +(tomato_svg(530,1268) if occupied else '')+'</g>')


def food_svg(t: float, tomato_added: bool = False) -> str:
    """Stable little vegetables entirely inside the approved pan's cavity."""
    out=['<g id="legumes-poele">']
    for x,y,angle in ((233,1302,-13),(282,1314,17),(329,1296,-18),
                      (358,1308,9),(274,1293,-15)):
        out.append(f'<g transform="translate({x} {y}) rotate({angle})">'
                   +_path('M-16 -4 Q0 -15 17 -4 L12 6 Q0 12 -13 5 Z',
                          '#ABC28F','#546747',2.8)
                   +_path('M-10 0 Q0 -5 11 0',stroke='#D4DDA7',width=2.)+'</g>')
    for x,y in ((251,1313),(308,1305)):
        out.append(_ellipse(x,y,9.,5.3,'#EDC77E','#AD8057',2.3))
    if tomato_added:
        out.append(tomato_svg(301,1300,.66))
    # One subdued rising curl establishes cooking without obscuring the actor.
    for j in range(2):
        u=(float(t)*.45+j*.5)%1.
        x=267.+j*57.+4.*math.sin(float(t)*2.+j)
        y=1268.-u*53.
        opacity=.30*math.sin(math.pi*u)
        out.append(_path(f'M{_n(x)} {_n(y)} q-7 -10 0 -19 q7 -9 0 -17',
                         stroke='#DDD1DC',width=3.2,opacity=_n(opacity)))
    out.append('</g>')
    return ''.join(out)


def spoon_svg(grip, bowl) -> str:
    """The original stirring-study spoon artwork, in world coordinates."""
    hx,hy=map(float,grip)
    bx,by=map(float,bowl)
    length=max(1e-9,math.hypot(hx-bx,hy-by))
    vx,vy=(hx-bx)/length,(hy-by)/length
    butt=(hx+28.*vx,hy+28.*vy)
    angle=math.degrees(math.atan2(vy,vx))
    return ('<g id="cuillere-cuisine">'
            +_path(f'M{_n(bx)} {_n(by)} L{_n(butt[0])} {_n(butt[1])}',
                   stroke=INK,width=14.)
            +_path(f'M{_n(bx)} {_n(by)} L{_n(butt[0])} {_n(butt[1])}',
                   stroke='#DDAA81',width=8.)
            +f'<ellipse cx="{_n(bx)}" cy="{_n(by)}" rx="17" ry="9" '
             f'transform="rotate({_n(angle)} {_n(bx)} {_n(by)})" '
             f'fill="#EDC69E" stroke="{INK}" stroke-width="4"/>'
            +'</g>')


def parked_spoon_svg() -> str:
    return spoon_svg(PARKED_GRIP,PARKED_BOWL)


def knife_svg(grip, tip) -> str:
    """Kitchen knife held by its actual grip; tip is the lower cutting corner.

    Its rigid blade extends above the grip-to-tip direction. The animation
    moves the whole prop with the hand; no fingers or extra hand are drawn.
    """
    gx, gy = map(float, grip)
    tx, ty = map(float, tip)
    length = max(1.e-9, math.hypot(tx-gx, ty-gy))
    dx, dy = (tx-gx)/length, (ty-gy)/length
    nx, ny = -dy, dx
    def at(distance, offset):
        return gx+dx*distance+nx*offset, gy+dy*distance+ny*offset
    lower = at(26., 5.)
    upper = at(26., -22.)
    back = (tx-nx*22.-dx*7., ty-ny*22.-dy*7.)
    blade = (f'M{_n(lower[0])} {_n(lower[1])} '
             f'L{_n(tx)} {_n(ty)} Q{_n(tx-dx*3.-nx*10.)} {_n(ty-dy*3.-ny*10.)} '
             f'{_n(back[0])} {_n(back[1])} L{_n(upper[0])} {_n(upper[1])} Z')
    a, b = at(-28., 0.), at(28., 0.)
    highlight_a, highlight_b = at(38., -15.), at(length-20., -15.)
    return ('<g id="couteau-carotte">'
            +_path(blade,'#D9D5DE',INK,3.4)
            +_path(f'M{_n(highlight_a[0])} {_n(highlight_a[1])} '
                   f'L{_n(highlight_b[0])} {_n(highlight_b[1])}',
                   stroke='#F9F5F6',width=3.)
            +_path(f'M{_n(a[0])} {_n(a[1])} L{_n(b[0])} {_n(b[1])}',
                   stroke=INK,width=14.)
            +_path(f'M{_n(a[0])} {_n(a[1])} L{_n(b[0])} {_n(b[1])}',
                   stroke='#A77E70',width=8.)
            +'</g>')


def carrot_svg(carrot: dict | None) -> str:
    """Carrot cut from its left end; two separated rounds persist on the board.

    body is the original left end, normally (650,1360). The native right hand
    stabilises the leafy right half while the left holds the knife. cuts=0/1/2
    changes the remaining body. Optional t and cut_times slide a new round away
    from its cut point instead of making it appear at its final destination.
    """
    if not carrot or not carrot.get('visible', True):
        return ''
    x,y=map(float,carrot.get('body',(650.,1360.)))
    cuts=max(0,min(2,int(carrot.get('cuts',0))))
    edge=x+12.*cuts
    radius=7.+2.*cuts
    end=x+95.
    out=['<g id="carotte-planche">',
         _ellipse(x+51.,y+15.,57.,8.,'#BA8E71',opacity='.22'),
         _path(f'M{_n(edge)} {_n(y-radius)} '
               f'Q{_n(x+48.)} {_n(y-16.)} {_n(end)} {_n(y-14.)} '
               f'Q{_n(end+9.)} {_n(y)} {_n(end)} {_n(y+14.)} '
               f'Q{_n(x+48.)} {_n(y+16.)} {_n(edge)} {_n(y+radius)} Z',
               '#E89A56',INK,3.8),
         _path(f'M{_n(max(edge+9.,x+20.))} {_n(y-5.)} '
               f'Q{_n(x+53.)} {_n(y-11.)} {_n(end-9.)} {_n(y-7.)}',
               stroke='#F7BD7D',width=3.8),
         _path(f'M{_n(x+50.)} {_n(y+3.)} l-3 6 M{_n(x+73.)} {_n(y+5.)} l-3 6',
               stroke='#C4784B',width=2.6),
         _path(f'M{_n(end)} {_n(y-6.)} q13 -17 19 -8 q0 7 -14 12 '
               f'q19 -8 22 0 q-3 9 -22 6 q14 7 10 14 q-10 4 -17 -14 Z',
               '#ABC28F','#546747',2.8)]
    if cuts:
        out.append(_ellipse(edge,y,5.5,radius,'#F8C487','#B97249',2.6))
    times=carrot.get('cut_times',(16.05,16.75))
    now=carrot.get('t')
    for j in range(cuts):
        u=1. if now is None else _clamp((float(now)-times[j])/.16)
        u=u*u*(3.-2.*u)
        start=(x+12.*(j+1),y)
        target=(x-23.-25.*j,y+14.)
        cx,cy=(start[0]+(target[0]-start[0])*u,
               start[1]+(target[1]-start[1])*u-5.*math.sin(math.pi*u))
        out.extend([_ellipse(cx,cy+3.,12.,8.,'#C8794B',INK,2.8),
                    _ellipse(cx,cy,12.,8.,'#F6BD7B',INK,2.8),
                    _ellipse(cx,cy,5.7,3.8,'#E99D5E','#E1A368',1.4)])
    out.append('</g>')
    grip=carrot.get('knife_grip',(540.,1245.))
    tip=carrot.get('knife_tip',(650.,1360.))
    out.append(knife_svg(grip,tip))
    return ''.join(out)
