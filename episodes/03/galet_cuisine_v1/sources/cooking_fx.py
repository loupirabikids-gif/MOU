"""V26 cooking: the same vegetables roast, scorch and finally smoke.

All coordinates use the approved kitchen's world space. This module draws
neither MOU nor his hands and never changes the approved pan silhouette.
The production clock drives the cooking; reused action clips cannot reset it.
"""
from __future__ import annotations

import math

VEGETABLES = ((233., 1302., -13.), (282., 1314., 17.),
              (329., 1296., -18.), (358., 1308., 9.), (274., 1293., -15.))
ROUNDS = ((251., 1313.), (308., 1305.))
TOMATO = (301., 1300., .66)


def _clamp(v):
    return max(0., min(1., float(v)))


def _smooth(v):
    v = _clamp(v)
    return v*v*(3.-2.*v)


def _lerp_color(a, b, amount):
    u = _clamp(amount)
    aa = tuple(int(a[i:i+2], 16) for i in (1, 3, 5))
    bb = tuple(int(b[i:i+2], 16) for i in (1, 3, 5))
    return '#' + ''.join(f'{round(x+(y-x)*u):02X}' for x, y in zip(aa, bb))


def cooking_state(t):
    """Expose the actual continuous progress used by both drawing layers."""
    t = float(t)
    roast = _smooth((t-10.)/10.)
    scorch = _smooth((t-19.5)/10.75)
    smoke = _smooth((t-24.2)/1.5)
    stage = ('carbonise' if t >= 30.25 else 'fume_grise' if t >= 25.55
             else 'bruni' if t >= 19.5 else 'dore' if t >= 15. else 'frais')
    return {'roast': roast, 'scorch': scorch, 'smoke': smoke, 'stage': stage,
            'tomato_default_added': t >= 15.58}


def _cooked_color(fresh, golden, black, roast, scorch):
    return _lerp_color(_lerp_color(fresh, golden, roast), black, scorch)


def food_svg(t, state, base_art):
    """Draw exactly one food group, with the original ingredient geometry.

    ``state['tomato_added']`` owns the tomato's persistence. There is no
    second plate, charcoal block or instantaneous replacement at the reveal.
    """
    level = cooking_state(t)
    roast, scorch = level['roast'], level['scorch']
    out = [f'<g id="legumes-poele" data-cook-phase="{level["stage"]}" '
           f'data-roast="{roast:.6f}" data-scorch="{scorch:.6f}">']
    # A thin residue develops under the unchanged ingredient positions.
    # Its silhouette stays inside the pan cavity and grows continuously.
    if scorch > 0.:
        crust = _lerp_color('#A16A45', '#302832', scorch)
        out.append(base_art._path(
            'M205 1308 Q235 1290 270 1296 Q304 1288 337 1296 '
            'Q373 1294 389 1310 Q365 1329 331 1324 '
            'Q294 1331 259 1325 Q223 1326 205 1308 Z',
            crust, 'none', 0., opacity=f'{.72*scorch:.6f}'))
    vegetable = _cooked_color('#ABC28F', '#BD9659', '#2C2530', roast, scorch)
    edge = _cooked_color('#546747', '#80603F', '#211D25', roast, scorch)
    highlight = _cooked_color('#D4DDA7', '#E1BA79', '#81747B', roast, scorch)
    for index, (x, y, angle) in enumerate(VEGETABLES):
        out.append(f'<g data-food="vegetable-{index}" '
                   f'transform="translate({x:.4f} {y:.4f}) rotate({angle:.4f})">'
                   + base_art._path('M-16 -4 Q0 -15 17 -4 L12 6 Q0 12 -13 5 Z',
                                    vegetable, edge, 2.8)
                   + base_art._path('M-10 0 Q0 -5 11 0', stroke=highlight, width=2.))
        if scorch > .08:
            out.append(base_art._path('M-7 -3 l3 5 M5 -4 l3 5',
                                      stroke='#211D25', width=2.1,
                                      opacity=f'{.8*scorch:.6f}'))
        out.append('</g>')
    round_fill = _cooked_color('#EDC77E', '#C58A48', '#302731', roast, scorch)
    round_edge = _cooked_color('#AD8057', '#885238', '#211D25', roast, scorch)
    for index, (x, y) in enumerate(ROUNDS):
        out.append(base_art._ellipse(x, y, 9., 5.3, round_fill, round_edge, 2.3,
                                     data_food=f'round-{index}'))
    tomato_added = bool(state.get('tomato_added', level['tomato_default_added']))
    if tomato_added:
        fragment = base_art.tomato_svg(*TOMATO)
        for fresh, golden, black in (
            ('#DD745E', '#BE6B45', '#342731'),
            ('#F6AC7E', '#CC8C55', '#65505A'),
            ('#BD6259', '#8B4D3B', '#27202A'),
            ('#FFF0BA', '#E1BF7E', '#9B8582'),
            ('#382035', '#382035', '#211D25'),
        ):
            fragment = fragment.replace(fresh, _cooked_color(
                fresh, golden, black, roast, scorch))
        out.append('<g data-food="tomato">'+fragment+'</g>')
    out.append('</g>')
    return ''.join(out)


def steam_svg(t, state=None):
    """Sparse rising curls, deliberately to the left of the face and hands.

    The world-space envelope stays inside x=200..382 and y>990. The renderer places
    this layer before the native arms. No fog overlay or blur covers MOU.
    The plume keeps moving during the final body hold.
    """
    t = float(t)
    level = cooking_state(t)
    smoke = level['smoke']
    activity = _smooth((t-10.)/12.)
    color = _lerp_color('#DDD1DC', '#655667', smoke)
    rise = 76. + 108.*activity + 15.*smoke
    centers = (235., 291., 337., 355.)
    out = [f'<g id="vapeur-cuisson" data-smoke="{smoke:.6f}" '
           f'data-cook-phase="{level["stage"]}">']
    for j in range(4):
        presence = (1. if j < 2 else _smooth((t-11.)/1.5) if j == 2
                    else _smooth((t-23.8)/1.5))
        u = (t*.37 + j*.263) % 1.
        alpha = presence*(.26 + .16*activity + .15*smoke)*math.sin(math.pi*u)
        if alpha <= .003:
            continue
        x = centers[j] + (4.+5.*smoke)*math.sin(t*1.2+j*.8)
        y = 1270. - u*rise
        bend = 7. + 6.*activity + 3.*smoke
        height = 28. + 12.*activity
        d = (f'M{x:.5f} {y:.5f} '
             f'c{-bend:.5f} {-height*.30:.5f} {-bend:.5f} {-height*.65:.5f} '
             f'0 {-height:.5f} '
             f'c{bend:.5f} {-height*.30:.5f} {bend:.5f} {-height*.65:.5f} '
             f'0 {-height:.5f}')
        width = 3.2 + 2.0*activity + 4.5*smoke
        out.append(f'<path data-steam-curl="{j}" d="{d}" fill="none" '
                   f'stroke="{color}" stroke-width="{width:.5f}" '
                   f'stroke-linecap="round" opacity="{alpha:.6f}"/>')
    out.append('</g>')
    return ''.join(out)
