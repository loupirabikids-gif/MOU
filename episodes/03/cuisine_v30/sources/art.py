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
BIN_CENTRES = ((140., 1700.), (195., 1590.), (135., 1480.))
BIN_RADII = (58., 70., 82.)
BIN_ROTATIONS = (-12., 17., -8.)
# V26 has three large persistent balls; the fourth, small scrap rebounds
# from their heap and remains on the floor. Their identities do not reset.
BIN_VISUAL_SEEDS = (1, 2, 3)
LAST_PAPER_WIDTH, LAST_PAPER_HEIGHT = 64., 88.
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
            + _path(outline, PAPER, INK, 3.2 if radius<30. else 4.2)
            + ''.join(_path(d, stroke='#C5B2C3', width=1.6 if radius<30. else 2.4) for d in folds)
            + '</g>')


def bin_svg(count: int, flying: dict | None = None,
            floor_ball: dict | None = None) -> str:
    """Open wire basket; previous balls remain at fixed, visible positions.

    The bucket is drawn in front of the island.  The lattice deliberately
    leaves its contents readable at a small preview size.  ``count`` is the
    number of completed arrivals in the basket. The fourth small sheet can
    rebound from the full heap and persist separately as ``floor_ball``.
    """
    count = max(0, min(len(BIN_CENTRES), int(count)))
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
        out.append(_ball(x, y, BIN_RADII[index], BIN_ROTATIONS[index], BIN_VISUAL_SEEDS[index]))
    if flying is not None:
        out.append(_ball(float(flying['x']), float(flying['y']),
                         float(flying.get('r', BIN_RADII[min(count, len(BIN_RADII)-1)])),
                         float(flying.get('rotation', 0.)),
                         int(flying.get('visual_seed', BIN_VISUAL_SEEDS[min(count, len(BIN_VISUAL_SEEDS)-1)]))))
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
    if floor_ball is not None:
        x, y = float(floor_ball['x']), float(floor_ball['y'])
        out.extend([
            '<g id="dernier-papier-au-sol" data-paper-ordinal="4">',
            _ellipse(x, 1831., 32., 8., '#BDA6BD', opacity='.35'),
            _ball(x, y, float(floor_ball.get('r', 22.)),
                  float(floor_ball.get('rotation', 12.)),
                  int(floor_ball.get('visual_seed', 4))),
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


def _last_sheet_points():
    """A bowed, softly torn sheet, with the original 64 x 88 extent.

    Fifteen clockwise anchors match the final ball's winding and vertex
    count.  The same outline starts the crush, so there is no replacement
    frame or folded document corner at the handoff.
    """
    sx, sy = LAST_PAPER_WIDTH/64., LAST_PAPER_HEIGHT/88.
    return tuple((x*sx,y*sy) for x,y in (
        (-32,-5),(-13,-2),(10,-3),(29,-5),(27,19),
        (31,43),(32,67),(25,80),(11,77),(0,83),
        (-9,79),(-23,81),(-28,64),(-31,40),(-28,16)))


def _soft_paper_outline(points, rounding=.22):
    """Round short corner sections without changing the winding order."""
    rounding=_clamp(rounding,0.,.45)
    def toward(a,b):
        return (a[0]+rounding*(b[0]-a[0]),a[1]+rounding*(b[1]-a[1]))
    first=toward(points[0],points[-1])
    out=[f'M{_n(first[0])} {_n(first[1])}']
    for i,point in enumerate(points):
        before=toward(point,points[i-1])
        after=toward(point,points[(i+1)%len(points)])
        out.append(f'L{_n(before[0])} {_n(before[1])} '
                   f'Q{_n(point[0])} {_n(point[1])} {_n(after[0])} {_n(after[1])}')
    return ' '.join(out)+' Z'


def _last_sheet_creases():
    # Curves follow the small drape around the existing mitten. They are
    # short material bends rather than a ruled line or a folded-over corner.
    return (_path('M-20 13 Q-7 25 -15 45',stroke='#CBB6C8',width=1.8)
            +_path('M19 31 Q10 49 19 65',stroke='#CBB6C8',width=1.8))


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
    if mode in ('tiny','tiny_pull','tiny_wipe'):
        cx,cy=map(float,paper.get('center',end))
        # The last piece stays smaller than the wasted bands, but remains
        # legible on a phone. Its grip and the native hands do not move.
        result=(f'<g transform="translate({_n(cx)} {_n(cy)})">'
                +_path(_soft_paper_outline(_last_sheet_points()),PAPER,INK,3.2)
                +_last_sheet_creases()+'</g>')
    elif mode == 'pull':
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
        visual_seed = int(paper.get('visual_seed', paper.get('cycle', 1)))
        mirror = -1. if visual_seed % 2 == 0 else 1.
        jagged = ((-.87, -.31), (-.54, -.74), (-.18, -.67), (.13, -.96),
                  (.56, -.77), (.65, -.46), (.94, -.20), (.81, .19),
                  (.95, .43), (.51, .77), (.12, .70), (-.22, .88),
                  (-.62, .65), (-.65, .25), (-.95, .13))
        rectangle = ((-43,-28),(-13,-28),(15,-28),(43,-28),(65,-18),
                     (65,16),(65,51),(53,85),(38,132),(7,150),
                     (-21,146),(-48,132),(-61,93),(-62,45),(-56,10))
        small= bool(paper.get('tiny', visual_seed==4))
        xscale,yscale=1.,1.
        # Mirroring reverses winding for a large ball too. Restore traversal
        # without changing its final silhouette, preventing crossed material
        # in the second ritual as well as the preserved final tiny scrap.
        if mirror < 0.:
            jagged=jagged[4::-1]+jagged[:4:-1]
        if small:
            rectangle=_last_sheet_points()
        pts = [((1-progress)*a*xscale+progress*mirror*b*r,
                (1-progress)*c*yscale+progress*d*r)
               for (a,c),(b,d) in zip(rectangle,jagged)]
        outline=(_soft_paper_outline(pts,.22*(1.-progress)) if small else
                 'M'+' L'.join(f'{_n(x)} {_n(y)}'for x,y in pts)+' Z')
        if small:
            # Keep the held bends at the exact start, then replace them with
            # the crushed texture as the material contracts. The silhouette
            # remains one object throughout.
            crease=(f'<g opacity="{_n(1.-progress)}">'+_last_sheet_creases()+'</g>'
                    +f'<g opacity="{_n(progress)}">'
                    +_path(f'M{-.54*r:.4f} {-.66*r:.4f} L{-.18*r:.4f} {-.15*r:.4f} L{-.40*r:.4f} {.40*r:.4f}',
                           stroke='#C5B2C3',width=1.6)+'</g>')
            # Bends belong to the shrinking material, never the hand or the
            # plate behind it. Use this exact current silhouette as their mask.
            crease=('<defs><clipPath id="papier-dernier-plis-clip" clipPathUnits="userSpaceOnUse">'
                    f'<path d="{outline}"/></clipPath></defs>'
                    '<g clip-path="url(#papier-dernier-plis-clip)">'+crease+'</g>')
        else:
            crease=(f'M{(-26+7*progress)*xscale:.4f} {-14*yscale:.4f} '
                    f'L{(14+3*progress)*xscale:.4f} {21*yscale:.4f} '
                    f'L{(-15+5*progress)*xscale:.4f} {(97-69*progress)*yscale:.4f}')
        result=(f'<g transform="translate({_n(cx)} {_n(cy)}) scale({_n(1.+.13*progress)} {_n(1.+.25*progress)})">'
                +_path(outline,PAPER,INK,3.2 if small else 4.5)
                +(crease if small else _path(crease,stroke='#C5B2C3',width=2.5))+'</g>')
    elif mode == 'ball':
        cx, cy = map(float, paper.get('center', start))
        result = _ball(cx, cy, float(paper.get('r',55.)),
                       float(paper.get('rotation', 0.)),
                       int(paper.get('visual_seed', paper.get('cycle',1))))
    else:
        raise ValueError(f'Unknown paper mode: {mode}')
    return '<g id="papier-en-main">'+result+'</g>'


def water_svg(t: float, on: bool, hand: tuple | None = None) -> str:
    """An exaggerated, fast jet; all spray lands within the existing basin.

    The outlet stays at102,1069. The renderer may extend the group vertically
    by15px about the outlet when the small mitten is underneath; splash y is
    therefore capped at1145 here, still inside the basin after that transform.
    The native mitten, tap and basin are not changed by this drawing.
    """
    if not on:
        return ''
    t = float(t)
    ripple = 2.1*math.sin(t*31.)
    lower = 11.8+1.1*math.sin(t*27.)
    out = [
        '<g id="eau-robinet" data-water-flow="exaggerated">',
        '<defs><clipPath id="eau-zone-bassin">'
        '<path d="M84 1089 H232 V1141 Q158 1149 84 1141 Z"/>'
        '</clipPath></defs>',
        _path(f'M94.5 1070 Q{91.5+ripple:.4f} 1103 {102.-lower:.4f} 1138 '
              f'Q102 1145 {102.+lower:.4f} 1138 '
              f'Q{113.4+ripple:.4f} 1102 109.5 1070 Z',
              '#A8DCE5', '#679DAE', 1.8, opacity='.96'),
        _path(f'M99 1072 Q{98+ripple*.25:.4f} 1105 97 1137',
              stroke='#E9FCFF',width=4.1,opacity='.96'),
        _path(f'M106 1075 Q{107+ripple*.4:.4f} 1106 108 1137',
              stroke='#C7F1F5',width=3.,opacity='.88'),
        '<g clip-path="url(#eau-zone-bassin)">',
    ]
    # Short white streaks move quickly down the broad continuous jet. The
    # hand is drawn later and naturally occludes their impact on its surface.
    for j in range(3):
        u=(t*7.2+j/3.)%1.
        x=100.5+3.7*math.sin(j*2.4+t*4.)
        y=1077.+u*54.
        out.append(_path(f'M{_n(x)} {_n(y)} l.8 7',
                         stroke='#F2FFFF',width=2.3,opacity='.85'))
    for j in range(12):
        u=(t*4.8+j*.08333)%1.
        side=-1. if j%4==0 else 1.
        distance=(13.+2.*(j%3)) if side<0 else (37.+10.*(j%5))
        x=103.+side*distance*u
        y=1139.-(25.+4.*(j%4))*math.sin(math.pi*u)+2.*u
        out.append(_ellipse(x,y,2.1+.45*(j%3),3.7+1.1*(j%2),
                            '#9CCFD9','#719FAE',.65,
                            opacity=_n(.83*(1.-u*.72))))
    # Concentric ripples and little impact arcs remain within the sink;
    # the surrounding countertop never becomes wet or flooded.
    for j in range(2):
        u=(t*3.8+j*.5)%1.
        out.append(_ellipse(137.+u*14.,1140.,25.+u*35.,2.2+u*.8,
                            'none','#75AAB7',1.9,opacity=_n(.72*(1.-u))))
    out.append(_path('M91 1135 q8 -10 17 0 M113 1138 q11 -12 22 -2',
                     stroke='#ECFDFF',width=3.1,opacity='.9'))
    out.append('</g>')
    out.append('</g>')
    return ''.join(out)


def apron_svg(state: dict | None = None) -> str:
    """MOU's requested cooking apron in native local character coordinates.

    Render this with the same actor transform as the torso, below both native
    arms and the foreground island. Its bib starts below the mouth; shoulder
    roots and face are left uncovered. No part of the character is redrawn.
    """
    coral, seam, cream = '#D9947D', '#975F64', '#FFF0DC'
    out=['<g id="tablier-cuisine" data-costume="apron">',
         # Broad enough to read as fabric, but away from the mouth and roots.
         _path('M144 295 Q151 308 169 345 L178 342 Q160 310 153 292 Z',
               coral,INK,2.7),
         _path('M267 293 Q259 311 240 345 L249 348 Q268 316 276 296 Z',
               coral,INK,2.7),
         _path('M150 296 Q159 315 173 342 M271 297 Q260 319 245 344',
               stroke=cream,width=1.6,opacity='.8'),
         _path('M130 356 Q205 351 283 357 L282 368 Q204 364 130 368 Z',
               coral,INK,2.8),
         _path('M164 341 Q204 337 246 342 '
               'L252 367 Q264 387 273 412 '
               'Q208 430 138 412 Q149 388 157 366 Z',
               coral,INK,3.6),
         _path('M165 348 Q205 345 244 349',stroke=cream,width=1.7),
         _path('M146 410 Q208 423 265 410',stroke=seam,width=2.),
         _ellipse(170,346,3.2,3.2,cream,INK,1.6),
         _ellipse(241,347,3.2,3.2,cream,INK,1.6),
         _path('M184 373 Q205 370 228 374 L226 393 '
               'Q205 403 185 392 Z',cream,INK,2.4),
         _path('M188 378 Q205 375 224 379',stroke=seam,width=1.5),
         _path('M189 382 V390 Q205 397 222 390 V382',
               stroke=seam,width=1.1,stroke_dasharray='2 2'),
         '</g>']
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


def salt_particles(salt: dict | None, t: float) -> list[dict]:
    """Deterministic small grains, anchored to the actual mitten tip.

    The animator may provide per-emission origins evaluated at the instant
    the grain leaves the moving hand. Otherwise the current tip is used;
    the explicit source/target coordinates remain available for the audit.
    """
    if not salt or not salt.get('visible', True):
        return []
    start, end = map(float, salt.get('sprinkle', (28.05, 28.55)))
    duration = float(salt.get('fall_duration', .24))
    if duration <= 0. or not start <= float(t) <= end+duration:
        return []
    origin = tuple(map(float, salt.get('pinch_tip', salt.get('hand', (365., 1190.)))))
    target = tuple(map(float, salt.get('target', (301., 1300.))))
    emissions = salt.get('emission_origins')
    if emissions is None:
        emissions = [{'time':start+j*(end-start)/10., 'origin':origin}
                     for j in range(11)]
    out = []
    for j, emission in enumerate(emissions):
        born = float(emission['time'])
        age = float(t)-born
        if not 0. <= age < duration:
            continue
        ox, oy = map(float, emission.get('origin', origin))
        tx, ty = map(float, emission.get('target',
                          (target[0]+(-16., -7., 4., 13., -2.)[j%5],
                           target[1]+(-5., 3., -1., 6.)[j%4])))
        u = age/duration
        # Each speck follows the same release point, then fans inside the pan.
        # Vertical acceleration gives a short falling sprinkle, not a beam.
        x = ox+(tx-ox)*u
        y = oy+(ty-oy)*(.20*u+.80*u*u)
        out.append({'index':j, 'emission_time':born, 'origin':(ox,oy),
                    'target':(tx,ty), 'progress':u, 'x':x, 'y':y,
                    'radius':3.2+.40*(j%3),
                    'opacity':1.-_clamp((u-.88)/.12)})
    return out


def salt_svg(salt: dict | None, t: float = 0., layer: str = 'all') -> str:
    """Open salt bowl behind the hands, grains in front of the active mitten.

    ``layer='bowl'`` belongs with the worktop props. ``layer='grains'`` is
    drawn after the existing arms, keeping the sprinkle visibly attached.
    The bowl persists from the opening; no title or explanatory symbol is used.
    """
    if not salt or not salt.get('visible', True):
        return ''
    if layer not in ('all', 'bowl', 'grains'):
        raise ValueError(('salt layer', layer))
    out = []
    cx, cy = map(float, salt.get('bowl', (590., 1284.)))
    if layer in ('all', 'bowl'):
        out.extend([
            '<g id="coupelle-sel" data-prop="salt-bowl">',
            _ellipse(cx,cy+20.,25.,5.,'#A789A0',opacity='.22'),
            _path(f'M{_n(cx-22.)} {_n(cy)} '
                  f'Q{_n(cx-17.)} {_n(cy+18.)} {_n(cx)} {_n(cy+18.)} '
                  f'Q{_n(cx+17.)} {_n(cy+18.)} {_n(cx+22.)} {_n(cy)} Z',
                  '#CDB4D0',INK,3.2),
            _ellipse(cx,cy,22.,7.5,'#E8DBE5',INK,3.2),
            _path(f'M{_n(cx-17.)} {_n(cy)} '
                  f'Q{_n(cx-9.)} {_n(cy-11.)} {_n(cx+2.)} {_n(cy-8.)} '
                  f'Q{_n(cx+12.)} {_n(cy-8.)} {_n(cx+17.)} {_n(cy)} Z',
                  '#FFFDF7','#B5A0B3',1.25),
        ])
        for j,(dx,dy) in enumerate(((-13.,-.5),(-6.,-4.),(1.,-5.5),(9.,-3.),
                                    (14.,.8),(-3.,.8),(5.,1.5))):
            out.append(_ellipse(cx+dx,cy+dy,1.1+.15*(j%2),.8,
                                '#FFFFFF','#B5A0B3',.45))
        out.extend([_path(f'M{_n(cx-19.)} {_n(cy+3.)} Q{_n(cx)} {_n(cy+10.)} {_n(cx+19.)} {_n(cy+3.)}',
                          stroke='#A98BAD',width=1.5), '</g>'])
    if layer in ('all', 'grains'):
        out.append('<g id="grains-sel" data-prop="salt-grains">')
        if salt.get('grains_on_hand'):
            hx,hy=map(float,salt.get('pinch_tip',salt.get('hand',(365.,1190.))))
            # A little white pinch reads against MOU's green tip; it never
            # substitutes a second hand or adds drawn human fingers.
            for j,(dx,dy) in enumerate(((-3.,-2.),(2.,-3.),(5.,1.))):
                out.append(_ellipse(hx+dx,hy+dy,2.,1.6,'#FFFDF7','#B9A8B4',.55,
                                    data_grain='pinch',data_grain_index=j))
        for grain in salt_particles(salt,t):
            ox,oy=grain['origin'];tx,ty=grain['target']
            out.append(_ellipse(grain['x'],grain['y'],grain['radius'],grain['radius']*.72,
                                '#FFFDF7','#9B849B',.65,
                                id=f'grain-sel-{grain["index"]:02d}',
                                opacity=_n(grain['opacity']),data_grain='fall',
                                data_grain_index=grain['index'],
                                data_emission_time=_n(grain['emission_time']),
                                data_origin_x=_n(ox),data_origin_y=_n(oy),
                                data_target_x=_n(tx),data_target_y=_n(ty),
                                data_progress=_n(grain['progress'])))
        out.append('</g>')
    return ''.join(out)


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


def knife_edge_point(grip, tip):
    """Actual belly of the cutting edge, in the rigid knife's local geometry.

    The canonical knife length grip-to-tip is150px. Animation should use this
    edge point at the board rather than make the tip stab the carrot.
    """
    gx,gy=map(float,grip);tx,ty=map(float,tip)
    length=max(1.e-9,math.hypot(tx-gx,ty-gy))
    dx,dy=(tx-gx)/length,(ty-gy)/length
    return gx+94.*dx-33.*dy,gy+94.*dy+33.*dx


def knife_svg(grip, tip) -> str:
    """A broad chef's knife with a separate dark wooden handle and curved edge."""
    gx, gy = map(float, grip)
    tx, ty = map(float, tip)
    length = max(1.e-9, math.hypot(tx-gx, ty-gy))
    dx, dy = (tx-gx)/length, (ty-gy)/length
    nx, ny = -dy, dx
    def at(distance, offset):
        return gx+dx*distance+nx*offset, gy+dy*distance+ny*offset
    def coords(distance,offset):
        p=at(distance,offset);return f'{_n(p[0])} {_n(p[1])}'
    # The two quadratic segments meet exactly at local(94,33), the contact
    # point exposed by knife_edge_point. The tip curves up away from the board.
    blade=(f'M{coords(28,-17)} L{coords(112,-17)} L{coords(150,0)} '
           f'Q{coords(132,8)} {coords(94,33)} '
           f'Q{coords(60,34)} {coords(28,26)} Z')
    handle=(f'M{coords(-31,-9)} Q{coords(-36,0)} {coords(-30,10)} '
            f'L{coords(23,10)} L{coords(29,6)} L{coords(29,-8)} Z')
    out=['<g id="couteau-carotte">',_path(blade,'#D3D4D8',INK,3.8),
         _path(f'M{coords(38,-9)} L{coords(110,-9)} Q{coords(128,-7)} {coords(138,0)}',
               stroke='#FBFAF6',width=3.2),
         _path(f'M{coords(34,23)} Q{coords(65,29)} {coords(94,28)}',
               stroke='#A7A6AF',width=2.1),
         _path(handle,'#936E61',INK,3.8),
         _path(f'M{coords(-25,-4)} L{coords(18,-4)}',stroke='#B69883',width=2.2),
         _path(f'M{coords(25,-10)} L{coords(25,11)}',stroke='#D2C7C5',width=5.)]
    for d in (-19.,10.):
        px,py=at(d,1.)
        out.append(_ellipse(px,py,2.4,2.4,'#D7C6AD',INK,1.2))
    out.append('</g>')
    return ''.join(out)


def carrot_svg(carrot: dict | None) -> str:
    """Carrot cut from its left end; two separated rounds persist on the board.

    body is the original left end, normally (650,1360). The native right hand
    stabilises the leafy right half while the left holds the knife. cuts=0/1/2
    changes the remaining body. Optional t and cut_times slide a new round away
    from its cut point instead of making it appear at its final destination.
    """
    if not carrot or not carrot.get('visible', True):
        return ''
    x,y=map(float,carrot.get('body',(635.,1360.)))
    cuts=max(0,min(2,int(carrot.get('cuts',0))))
    edge=x+20.*cuts
    radius=(3.,12.,17.)[cuts]
    end=x+140.
    out=['<g id="carotte-planche">',
         _ellipse(x+73.,y+23.,81.,8.,'#BA8E71',opacity='.23'),
         _path(f'M{_n(edge)} {_n(y-radius)} '
               f'Q{_n(x+62.)} {_n(y-24.)} {_n(end)} {_n(y-20.)} '
               f'Q{_n(end+10.)} {_n(y)} {_n(end)} {_n(y+20.)} '
               f'Q{_n(x+65.)} {_n(y+25.)} {_n(edge)} {_n(y+radius)} Z',
               '#EC9550',INK,4.2),
         _path(f'M{_n(max(edge+12.,x+25.))} {_n(y-7.)} '
               f'Q{_n(x+80.)} {_n(y-17.)} {_n(end-11.)} {_n(y-13.)}',
               stroke='#FBC383',width=4.3),
         _path(f'M{_n(x+69.)} {_n(y+3.)} l-4 8 M{_n(x+103.)} {_n(y+7.)} l-3 7',
               stroke='#C16D39',width=2.9),
         _path(f'M{_n(end)} {_n(y-8.)} q17 -23 26 -17 q6 8 -17 20 '
               f'q28 -14 34 -4 q3 10 -26 12 q21 7 16 17 q-8 8 -33 -12 Z',
               '#98B87C','#546747',3.)]
    if cuts:
        out.append(_ellipse(edge,y,5.8,radius,'#F8C487','#B97249',2.8))
    times=carrot.get('cut_times',(16.05,16.75))
    now=carrot.get('t')
    for j in range(cuts):
        u=1. if now is None else _clamp((float(now)-times[j])/.16)
        u=u*u*(3.-2.*u)
        start=(x+20.*(j+1),y)
        target=(x-25.+40.*j,y+22.+3.*j)
        cx,cy=(start[0]+(target[0]-start[0])*u,
               start[1]+(target[1]-start[1])*u-5.*math.sin(math.pi*u))
        rx,ry=(15.,10.) if j==0 else (18.,12.)
        out.extend([_ellipse(cx,cy+4.,rx,ry,'#C8794B',INK,2.8),
                    _ellipse(cx,cy,rx,ry,'#F7BF7D',INK,2.8),
                    _ellipse(cx,cy,rx*.48,ry*.48,'#EB9A50','#E1A368',1.4)])
    out.append('</g>')
    grip=carrot.get('knife_grip',(540.,1245.))
    tip=carrot.get('knife_tip',(650.,1360.))
    if not carrot.get('knife_hidden',False):
        out.append(knife_svg(grip,tip))
    return ''.join(out)


def roll_geometry(state=None):
    """Paper thickness decreases in radius; the cardboard and height stay put."""
    state=state or {}
    if 'radius_scale' in state:
        radius=max(16.,67.*_clamp(state['radius_scale']))
    else:
        remaining=_clamp(state.get('remaining',1.))
        radius=math.sqrt(16.**2+(67.**2-16.**2)*remaining)
    empty=bool(state.get('empty',False)) or radius<=16.01
    return {'radius':radius,'empty':empty,'centre_x':876.,'top':1108.,'bottom':1320.,
            'edge':(876.-radius,1175.),'hand':(876.-radius-2.,1217.)}


def roll_svg(state=None):
    """Original stand plus a physically narrowing roll, or its bare cardboard."""
    state=state or {};g=roll_geometry(state)
    cx,top,bottom,r=876.,1108.,1320.,g['radius']
    rx,ry=r,25.*r/67.
    left,right=cx-r,cx+r
    body=(f'M{_n(left)} {_n(top)} L{_n(left)} {_n(bottom)} '
          f'Q{_n(cx)} {_n(bottom+25.*r/67.)} {_n(right)} {_n(bottom)} '
          f'L{_n(right)} {_n(top)} Z')
    out=['<g id="essuie-tout-variable">',
         _ellipse(877,1350,90,24,'#BD936F',INK,6.),
         _ellipse(877,1345,72,14,'#DDBA91','#896776',3.)]
    fill='#BD9977' if g['empty'] else '#FFFDF6'
    out.extend([_path(body,fill,INK,5.5),
                _path(f'M{_n(right-8.)} 1130 V1307',stroke='#A88773' if g['empty'] else '#D6C7CF',width=2.6),
                _ellipse(cx,top,rx,ry,'#CEAC87' if g['empty'] else '#FFFDF6',INK,5.),
                _ellipse(cx,top+1.,16.,7.,'#B19493','#796274',3.),
                _ellipse(cx,top+1.,8.5,3.5,'#8B6D6D',width=0.)])
    if not g['empty']:
        # Quiet embossing stays within the cylinder, even when little is left.
        for index,py in enumerate((1162.,1216.,1270.)):
            px=cx+(-1. if index%2==0 else 1.)*min(19.,r*.24)
            out.append(_path(f'M{_n(px-4.)} {_n(py)} q4 -5 8 0 q-4 5 -8 0',
                             stroke='#E8DDE2',width=1.8))
        if not state.get('pulling',False):
            near_end=r<18.
            length=_clamp(state.get('tab_length',40. if near_end else 133.),0.,175.)
            if near_end:length=min(40.,length)
            if length:
                x,y=left,(1175. if near_end else 1143.)
                width=26. if near_end else min(43.,max(25.,r*.60))
                if near_end:
                    flap=(f'M{_n(x-6.)} {_n(y)} h26 '
                          f'L{_n(x+18.)} {_n(y+length)} L{_n(x-8.)} {_n(y+length)} Z')
                else:
                    flap=(f'M{_n(x)} {_n(y)} Q{_n(x-6.)} {_n(y+15.)} {_n(x-10.)} {_n(y+42.)} '
                          f'L{_n(x-24.)} {_n(y+length)} Q{_n(x-6.)} {_n(y+length+12.)} {_n(x+width-17.)} {_n(y+length+8.)} '
                          f'L{_n(x+width-4.)} {_n(y+43.)} Q{_n(x+width+2.)} {_n(y+14.)} {_n(x+width)} {_n(y)} Z')
                out.append(_path(flap,'#FFFCF5',INK,4.3))
                if length>72.:
                    out.append(_path(f'M{_n(x-18.)} {_n(y+length-35.)} q20 8 {_n(width-3.)} 7',
                                     stroke='#C4ACBC',width=2.5,stroke_dasharray='4 7'))
    out.extend([_path('M876 1079 V1105',stroke='#A37E64',width=13.),
                _ellipse(876,1077,7,5,'#C29B7C',INK,3.),'</g>'])
    return ''.join(out)
