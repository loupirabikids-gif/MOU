"""Le retardateur : vanité, maintien forcé, effondrement élastique, gêne.

Même silhouette et rig articulé MOU. Les déformations de jeu transforment
corps, bras et visage ensemble, avec les deux pieds fixes hors du groupe.
Le plan, l'aperçu du téléphone et la photo appellent tous character_at().
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
    return {**DEFAULT_POSE, 'grimace': 0.0, 'vanity': 0.0, 'pout': 0.0,
            'warp_sx': 1.0, 'warp_sy': 1.0, 'warp_skew': 0.0, **changes}


# Téléphone bas-gauche : MOU admire son propre aperçu. Ses mains sont déjà
# aux hanches, menton haut et buste fier, avant même son premier sourire.
READY = state(arm_hips=1., eye_open_l=.56, eye_open_r=.65,
              pupil_x=-.95, pupil_y=.12, brow_l=.05, brow_r=-.95,
              brow_raise=.50, smile=.65, pout=.35, vanity=.65,
              warp_sx=.98, warp_sy=1.065, warp_skew=-.025)
ADMIRE = state(arm_hips=1., eye_open_l=.48, eye_open_r=.60,
               pupil_x=-1., pupil_y=.30, brow_l=.18, brow_r=-1.,
               brow_raise=.60, smile=.3, pout=1.,
               warp_sx=.97, warp_sy=1.12, warp_skew=-.035)
PROUD = state(arm_hips=1., eye_open_l=.53, eye_open_r=.68,
              pupil_x=-.95, pupil_y=.20, brow_l=.15, brow_r=-1.,
              brow_raise=.70, smile=1., vanity=1.,
              warp_sx=.98, warp_sy=1.13, warp_skew=-.025)
WINK = dict(PROUD, eye_open_r=0., brow_r=-.95)
TENSE = state(arm_hips=1., eye_open_l=.76, eye_open_r=.80,
              pupil_x=-.90, pupil_y=.28, brow_l=.12, brow_r=-.72,
              brow_raise=.40, smile=1., mouth_open=.14, vanity=.50,
              warp_sx=.99, warp_sy=1.10, warp_skew=-.025)
# Le bref étirement précède la chute, sans déplacement des pieds.
STRETCH = state(arm_hips=.18, eye_open_l=0., eye_open_r=.38,
                pupil_x=.55, pupil_y=.70, brow_l=.30, brow_r=.75,
                brow_raise=.35, smile=-.80, mouth_open=.75, grimace=.65,
                warp_sx=.94, warp_sy=1.18, warp_skew=.005)
SPLAT = state(arm_hips=.28, eye_open_l=0., eye_open_r=.92,
              pupil_x=.80, pupil_y=.75, brow_l=-.40, brow_r=.82,
              brow_raise=-.05, smile=-1., mouth_open=1., grimace=1.,
              warp_sx=1.12, warp_sy=.65, warp_skew=-.07)
REBOUND = state(arm_hips=0., eye_open_l=0., eye_open_r=.70,
                pupil_x=.80, pupil_y=.65, brow_l=-.40, brow_r=.75,
                brow_raise=.08, smile=-1., mouth_open=1., grimace=1.,
                warp_sx=1.04, warp_sy=.84, warp_skew=-.035)
GRIMACE = state(arm_hips=0., eye_open_l=0., eye_open_r=.83,
                pupil_x=.80, pupil_y=.68, brow_l=-.48, brow_r=.83,
                brow_raise=-.10, smile=-1., mouth_open=1., grimace=1.,
                warp_sx=1.12, warp_sy=.68, warp_skew=-.07)
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
    (0.00, READY), (.12, READY), (.60, ADMIRE), (.82, ADMIRE),
    (1.28, PROUD), (1.48, PROUD), (1.58, WINK), (1.66, WINK),
    (1.78, PROUD), (3.85, PROUD), (4.55, TENSE), (5.25, TENSE),
    (5.40, STRETCH), (5.62, SPLAT), (5.83, REBOUND),
    (6.15, GRIMACE), (6.50, GRIMACE),
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
    # Clin d'œil de vanité dans KEYS ; le clignement de gêne reste inchangé.
    blink = 1.0
    for center, width in [(11.82, .065)]:
        blink *= 1-.995*math.exp(-((t-center)/width)**2)
    p['eye_open_l'] *= blink
    p['eye_open_r'] *= blink
    # Sous .30, le morphing du rig donnerait un contour vert vide. Terminer
    # la fermeture en arc franc évite cet artefact sans redessiner les yeux.
    for side in ('l', 'r'):
        if p['eye_open_'+side] < .30:
            p['eye_open_'+side] = 0.0
    return p


def motion_at(t):
    """Le jeu physique est dans character_at, également utilisé par la photo."""
    return {'sx': 1.0, 'sy': 1.0, 'dx': 0.0, 'dy': 0.0}


def deformation_at(p):
    """Paramètres affines communs au torse, aux bras et au visage.

    x'=200+sx*(x-200)+skew*(y-437) ; y'=437+sy*(y-437).
    Les pieds sont exclus de ce groupe ; les mains n'en sont jamais exclues.
    sx : .94..1.12 ; sy : .65..1.18 ; skew : -.07...005.
    """
    return {'sx': float(p.get('warp_sx', 1.)),
            'sy': float(p.get('warp_sy', 1.)),
            'skew': float(p.get('warp_skew', 0.)),
            'anchor_x': 200., 'anchor_y': 437.}


def _episode_mouth(p, uid):
    """Même bouche : moue puis grand sourire ; après, mâchoire pendante."""
    g = min(1., max(0., p.get('grimace', 0.)))
    v = min(1., max(0., p.get('vanity', 0.)))
    pout = min(1., max(0., p.get('pout', 0.)))
    smile = max(-1., min(1., p.get('smile', 0.)))
    op = max(0., min(1., p.get('mouth_open', 0.)))
    mix = lambda a, b, u: a+(b-a)*u
    width = mix(12+12*abs(smile), 52, op)
    yl = mix(-5*smile, -25, op)
    yr = mix(-9*smile-8*max(0., smile), -31, op)
    upper = mix(20*smile, -12, op)
    lower = mix(20*smile, 52, op)
    points = [(-width, yl), (-width*.4, upper), (width*.4, upper),
              (width, yr), (width*.9, lower), (-width*.75, lower)]
    grin = [(-37., 2.), (-17., 27.), (20., 27.), (39., -20.),
            (30., 21.), (-24., 28.)]
    lips = [(-11., -2.), (-3., -10.), (9., -6.), (14., -2.),
            (7., 6.), (-5., 5.)]
    # Grand bas de bouche mou et oblique : ne doit pas lire un sourire.
    crooked = [(-44., 7.), (-29., -38.), (10., -30.), (39., 26.),
               (46., 58.), (-49., 78.)]
    for shape, weight in [(grin, v), (lips, pout), (crooked, g)]:
        points = [(mix(a[0],b[0],weight),mix(a[1],b[1],weight))
                  for a,b in zip(points,shape)]
    xy = [f'{x:.3f} {y:.3f}' for x,y in points]
    d = f'M{xy[0]} C{xy[1]} {xy[2]} {xy[3]} C{xy[4]} {xy[5]} {xy[0]} Z'
    ink = PALETTE['outline']
    clip = f'{uid}-mouth'
    tongue_y = mix(25., 64., g)
    tongue_x = mix(8., 20., g)
    tongue_rx = mix(33., 15., g)
    tongue_ry = mix(15., 24., g)
    # La même langue, désormais molle et sortie : une seule forme rose,
    # jamais dédoublée. Ses proportions reviennent avec le relâchement.
    tongue_clip = f'clip-path="url(#{clip})"' if g <= .00001 else ''
    return (f'<g id="mouth" transform="translate(205 321)">'
            f'<path d="{d}" fill="{ink}" stroke="{ink}" stroke-width="4.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<defs><clipPath id="{clip}"><path d="{d}"/></clipPath></defs>'
            f'<g {tongue_clip} opacity="{op:.3f}">'
            f'<ellipse cx="{tongue_x:.3f}" cy="{tongue_y:.3f}" rx="{tongue_rx:.3f}" '
            f'ry="{tongue_ry:.3f}" fill="{PALETTE["tongue"]}" '
            f'stroke="{ink}" stroke-width="{2.4*g:.3f}"/>'
            '</g></g>')


def character_at(p, uid='mou'):
    """Le rig original et son jeu : pieds fixes, torse/bras/visage solidaires."""
    fragment = character_fragment(p, uid=uid)
    if any(p.get(k, 0.) > .00001 for k in ('grimace', 'vanity', 'pout')):
        original = _mouth(p, uid)
        assert original in fragment
        fragment = fragment.replace(original, _episode_mouth(p, uid), 1)
    warp = deformation_at(p)
    if any(abs(warp[k]-v) > 1e-10 for k,v in [('sx',1.),('sy',1.),('skew',0.)]):
        # Le rig émet les deux groupes pied, puis body, les bras et le visage.
        # Garder les pieds frères du groupe affine, jamais ses descendants.
        marker = '<g id="body">'
        feet, rest = fragment.split(marker, 1)
        assert 'foot-l' in feet and 'foot-r' in feet and 'arm-' not in feet
        transform = (f'translate(200 437) matrix({warp["sx"]:.6f} 0 '
                     f'{warp["skew"]:.6f} {warp["sy"]:.6f} 0 0) '
                     'translate(-200 -437)')
        fragment = (feet + f'<g id="body-warp" transform="{transform}">'
                    + marker + rest + '</g>')
    return fragment


def intention_at(t):
    if t < .9: return 'auto-admiration'
    if t < 4.0: return 'certain d’être beau'
    if t < 5.25: return 'sourire crispé'
    if t < 6.15: return 'effondrement trop tôt'
    if t <= 6.50: return 'grimace photographiée'
    if t < 9.5: return 'découverte du clic tardif'
    if t < 11.0: return 'gêne devant la photo'
    return 'sourire forcé au spectateur'
