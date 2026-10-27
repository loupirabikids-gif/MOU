"""Jeu du pilote : même rig MOU, bouche étirée au relâchement seulement.

Le plan reste frontal et les deux pieds restent au sol. Les valeurs sont
interpolées avec des accélérations douces ; les pauses servent la lecture.
Le rendu principal et la photo doivent tous deux appeler character_at().
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mou_rig import DEFAULT_POSE, PALETTE, character_fragment, _mouth


def smooth(x):
    x = min(1.0, max(0.0, float(x)))
    return x*x*(3.0-2.0*x)


def state(**changes):
    return {**DEFAULT_POSE, 'grimace': 0.0, **changes}


# L'objectif est le téléphone bas-gauche. La pose se lit dès la première image.
READY = state(arm_hips=.58, eye_open_l=.83, eye_open_r=.83,
              pupil_x=-.85, pupil_y=.35, brow_l=.20, brow_r=-.50,
              brow_raise=.20, smile=.55)
PROUD = state(arm_hips=1., eye_open_l=.60, eye_open_r=.60,
              pupil_x=-.85, pupil_y=.35, brow_l=.22, brow_r=-.70,
              brow_raise=.28, smile=.95)
TENSE = state(arm_hips=1., eye_open_l=.74, eye_open_r=.72,
              pupil_x=-.85, pupil_y=.35, brow_l=.12, brow_r=-.48,
              brow_raise=.30, smile=.98, mouth_open=.11)
RELIEF = state(arm_hips=.12, eye_open_l=.06, eye_open_r=.10,
               pupil_x=-.30, pupil_y=.25, brow_l=.25, brow_r=.25,
               brow_raise=.20, smile=-.30, mouth_open=.56, grimace=.30)
GRIMACE = state(arm_hips=0., eye_open_l=.035, eye_open_r=.83,
                pupil_x=.70, pupil_y=.58, brow_l=-.42, brow_r=.72,
                brow_raise=.08, smile=-.80, mouth_open=.86, grimace=1.)
STARTLED = state(arm_hips=0., eye_open_l=1., eye_open_r=1.,
                 pupil_x=-.85, pupil_y=.45, brow_l=.30, brow_r=.30,
                 brow_raise=.90, smile=-.12, mouth_open=.34)
DISCOVER = state(arm_hips=0., eye_open_l=.94, eye_open_r=.94,
                 pupil_x=-.90, pupil_y=.45, brow_l=.60, brow_r=.60,
                 brow_raise=.45, smile=-.58, mouth_open=.08)
ASHAMED = state(arm_clasp=1., eye_open_l=.76, eye_open_r=.76,
                pupil_x=-.85, pupil_y=.40, brow_l=.64, brow_r=.64,
                brow_raise=.17, smile=.21)
FORCED = state(arm_clasp=1., eye_open_l=.82, eye_open_r=.82,
               pupil_x=0., pupil_y=.05, brow_l=.66, brow_r=.66,
               brow_raise=.25, smile=.42)
SIDEGLANCE = state(arm_clasp=1., eye_open_l=.78, eye_open_r=.78,
                   pupil_x=-.78, pupil_y=.38, brow_l=.66, brow_r=.66,
                   brow_raise=.20, smile=.28)

KEYS = [
    (0.00, READY), (.25, READY), (1.25, PROUD),
    (3.85, PROUD), (4.55, TENSE), (5.25, TENSE),
    (5.72, RELIEF), (6.15, GRIMACE), (6.50, GRIMACE),
    (6.625, STARTLED), (7.25, STARTLED),
    (8.75, DISCOVER), (9.50, DISCOVER),
    (10.62, ASHAMED), (10.95, ASHAMED),
    (11.48, FORCED), (12.15, FORCED),
    (12.42, SIDEGLANCE), (12.70, SIDEGLANCE),
    (13.10, FORCED), (14.00, FORCED),
]


def pose_at(t):
    """Pose complète. La pose à 6.5 s est la seule source de la photo figée."""
    for (ta, a), (tb, b) in zip(KEYS, KEYS[1:]):
        if ta <= t <= tb:
            u = smooth((t-ta)/(tb-ta))
            p = {key: a[key]+(b[key]-a[key])*u for key in a}
            break
    else:
        p = dict(KEYS[0 if t < 0 else -1][1])
    # Deux vrais clignements rapides : un pendant la préparation, un de gêne.
    # Aucun clignement autour du flash ou de la découverte de la photo.
    blink = 1.0
    for center, width in [(.58, .065), (11.82, .065)]:
        blink *= 1-.995*math.exp(-((t-center)/width)**2)
    p['eye_open_l'] *= blink
    p['eye_open_r'] *= blink
    # Le rig morphologique produit un anneau vert vide entre l'arc et
    # l'ovale (0 < ouverture < .30). À 24 i/s, terminer franchement le
    # clignement en arc évite ce faux œil creux, sans changer son dessin.
    for side in ('l', 'r'):
        if p['eye_open_'+side] < .30:
            p['eye_open_'+side] = 0.0
    return p


def motion_at(t):
    """Pas de glissement ni de saut : le jeu repose sur les bras et le visage."""
    return {'sx': 1.0, 'sy': 1.0, 'dx': 0.0, 'dy': 0.0}


def _episode_mouth(p, uid):
    """Le contour de bouche du rig est déformé, sans nouvelle anatomie."""
    g = min(1., max(0., p.get('grimace', 0.)))
    smile = max(-1., min(1., p.get('smile', 0.)))
    op = max(0., min(1., p.get('mouth_open', 0.)))
    mix = lambda a, b, u: a+(b-a)*u
    width = mix(12+12*abs(smile), 52, op)
    yl = mix(-5*smile, -25, op)
    yr = mix(-9*smile-8*max(0., smile), -31, op)
    upper = mix(20*smile, -12, op)
    lower = mix(20*smile, 52, op)
    regular = [(-width, yl), (-width*.4, upper), (width*.4, upper),
               (width, yr), (width*.9, lower), (-width*.75, lower)]
    crooked = [(-49., 7.), (-20., -13.), (10., 5.), (43., -19.),
               (56., 31.), (-25., 48.)]
    points = [(mix(a[0],b[0],g),mix(a[1],b[1],g))
              for a,b in zip(regular,crooked)]
    xy = [f'{x:.3f} {y:.3f}' for x,y in points]
    d = f'M{xy[0]} C{xy[1]} {xy[2]} {xy[3]} C{xy[4]} {xy[5]} {xy[0]} Z'
    ink = PALETTE['outline']
    clip = f'{uid}-mouth'
    return (f'<g id="mouth" transform="translate(205 321)">'
            f'<path d="{d}" fill="{ink}" stroke="{ink}" stroke-width="4.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<defs><clipPath id="{clip}"><path d="{d}"/></clipPath></defs>'
            f'<g clip-path="url(#{clip})" opacity="{op:.3f}">'
            f'<ellipse cx="8" cy="25" rx="33" ry="15" fill="{PALETTE["tongue"]}"/>'
            '</g></g>')


def character_at(p, uid='mou'):
    """Le rig original, avec la bouche du seul gag si grimace est non nul."""
    fragment = character_fragment(p, uid=uid)
    if p.get('grimace', 0.) > 0.00001:
        original = _mouth(p, uid)
        assert original in fragment
        fragment = fragment.replace(original, _episode_mouth(p, uid), 1)
    return fragment


def intention_at(t):
    if t < 1.25: return 'préparation'
    if t < 4.0: return 'frime'
    if t < 5.25: return 'sourire crispé'
    if t < 6.15: return 'relâchement trop tôt'
    if t < 6.71: return 'grimace photographiée'
    if t < 9.5: return 'découverte du clic tardif'
    if t < 11.0: return 'gêne devant la photo'
    return 'sourire forcé au spectateur'
