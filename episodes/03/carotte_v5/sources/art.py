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
BIN_CENTRES = ((140., 1700.), (195., 1620.), (135., 1537.), (140., 1455.))
BIN_RADII = (47., 53., 59., 11.)
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
            + _path(outline, PAPER, INK, 2.5 if radius<15. else 4.2)
            + ''.join(_path(d, stroke='#C5B2C3', width=1.3 if radius<15. else 2.4) for d in folds)
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
    if mode in ('tiny','tiny_pull','tiny_wipe'):
        cx,cy=map(float,paper.get('center',end))
        # A real small scrap, not a downscaled giant sheet. The lower tail
        # remains readable beyond the grip; optional front overlay can show it
        # against the coloured mitten without inventing fingers.
        width,height=26.,40.
        result=(_path(f'M{_n(cx-13.)} {_n(cy-5.)} L{_n(cx+13.)} {_n(cy-5.)} '
                      f'L{_n(cx+13.)} {_n(cy+27.)} L{_n(cx+6.)} {_n(cy+35.)} '
                      f'L{_n(cx-13.)} {_n(cy+35.)} Z',PAPER,INK,2.7)
                +_path(f'M{_n(cx+6.)} {_n(cy+35.)} V{_n(cy+27.)} h7',
                       stroke='#C5B2C3',width=1.7))
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
        cycle = int(paper.get('cycle', 1))
        mirror = -1. if cycle % 2 == 0 else 1.
        jagged = ((-.87, -.31), (-.54, -.74), (-.18, -.67), (.13, -.96),
                  (.56, -.77), (.65, -.46), (.94, -.20), (.81, .19),
                  (.95, .43), (.51, .77), (.12, .70), (-.22, .88),
                  (-.62, .65), (-.65, .25), (-.95, .13))
        rectangle = ((-43,-28),(-13,-28),(15,-28),(43,-28),(65,-18),
                     (65,16),(65,51),(53,85),(38,132),(7,150),
                     (-21,146),(-48,132),(-61,93),(-62,45),(-56,10))
        small= r<15.
        xscale,yscale=(.20,.267) if small else (1.,1.)
        pts = [((1-progress)*a*xscale*(mirror if small else 1.)+progress*mirror*b*r,
                (1-progress)*c*yscale+progress*d*r)
               for (a,c),(b,d) in zip(rectangle,jagged)]
        outline='M'+' L'.join(f'{_n(x)} {_n(y)}'for x,y in pts)+' Z'
        result=(f'<g transform="translate({_n(cx)} {_n(cy)}) scale({_n(1.+.13*progress)} {_n(1.+.25*progress)})">'
                +_path(outline,PAPER,INK,2.7 if small else 4.5)
                +_path(f'M{(-26+7*progress)*xscale:.4f} {-14*yscale:.4f} '
                       f'L{(14+3*progress)*xscale:.4f} {21*yscale:.4f} '
                       f'L{(-15+5*progress)*xscale:.4f} {(97-69*progress)*yscale:.4f}',
                       stroke='#C5B2C3',width=1.3 if small else 2.5)+'</g>')
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
