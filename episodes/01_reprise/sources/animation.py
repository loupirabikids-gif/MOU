"""Le retardateur : vanité, relâchement prématuré, capture et gêne.

Même silhouette et rig articulé MOU. Les déformations de jeu transforment
corps, bras et visage ensemble, avec les deux pieds fixes hors du groupe.
Le plan et la photo appellent tous character_at().
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from mou_rig import DEFAULT_POSE, PALETTE, character_fragment, _mouth, _eye


def smooth(x):
    x = min(1.0, max(0.0, float(x)))
    return x*x*(3.0-2.0*x)


def state(**changes):
    return {**DEFAULT_POSE, 'grimace': 0.0, 'vanity': 0.0, 'pout': 0.0, 'shame': 0.0, 'surprise': 0.0,
            'warp_sx': 1.0, 'warp_sy': 1.0, 'warp_skew': 0.0,
            'cross': 0.0, 'nervous': 0.0, 'lip_tension': 0.0, 'he_open': 0.0, **changes}


# Gag initial : séduction, faux achèvement du compteur, relâchement trop tôt.
# Aucun clasp ventral ni contact main-joue dans cette reprise.
READY = state(arm_hips=1., eye_open_l=.56, eye_open_r=.65,
              pupil_x=0., pupil_y=.0, brow_l=.05, brow_r=-.95,
              brow_raise=.50, smile=.65, pout=.35, vanity=.65,
              warp_sx=.98, warp_sy=1.065, warp_skew=-.025)
ADMIRE = state(arm_hips=1., eye_open_l=.48, eye_open_r=.60,
               pupil_x=0., pupil_y=.0, brow_l=.18, brow_r=-1.,
               brow_raise=.60, smile=.3, pout=1.,
               warp_sx=.97, warp_sy=1.12, warp_skew=-.035)
PROUD = state(arm_hips=1., eye_open_l=.53, eye_open_r=.68,
              pupil_x=0., pupil_y=.0, brow_l=.15, brow_r=-1.,
              brow_raise=.70, smile=1., vanity=1.,
              warp_sx=.98, warp_sy=1.13, warp_skew=-.025)
WINK = dict(PROUD, eye_open_r=0., brow_r=-.95)
# Il traite le dernier chiffre comme une fin ; soupir puis abandon physique.
SOFTEN = dict(PROUD, arm_hips=.8, eye_open_l=.42, eye_open_r=.55,
              vanity=.50, smile=.4, pupil_x=.45, pupil_y=.65, warp_sy=1.11)
EXHALE = state(arm_hips=.50, eye_open_l=.35, eye_open_r=.43,
               pupil_x=.65, pupil_y=.75, brow_l=.20, brow_r=.28,
               brow_raise=.20, smile=.10, mouth_open=.21,
               warp_sx=.99, warp_sy=1.08, warp_skew=-.015)
ANTICIPATE = state(arm_hips=.28, eye_open_l=.35, eye_open_r=.55,
                   pupil_x=.75, pupil_y=.80, brow_l=.25, brow_r=.35,
                   brow_raise=.28, smile=-.10, mouth_open=.25,
                   warp_sx=.97, warp_sy=1.12, warp_skew=.005)
# La grimace retenue reste un sourire crispé : ni langue sortie ni surprise O.
# pupil_x est la direction commune ; cross rapproche les deux pupilles.
GRIMACE = state(arm_hips=0., eye_open_l=1., eye_open_r=.65,
                pupil_x=0., pupil_y=0., cross=1.,
                brow_l=.68, brow_r=-.05, brow_raise=.30,
                smile=.35, nervous=1., lip_tension=.35,
                warp_sx=1.12, warp_sy=.68, warp_skew=-.07)
# Retour du corps seulement ; les paramètres du visage restent ceux du clic.
RECOVERED = dict(GRIMACE, warp_sx=1.015, warp_sy=.97, warp_skew=.008)
READ_PHOTO = dict(RECOVERED, pupil_y=.85)
FACE_VIEWER = dict(RECOVERED, pupil_y=0.)
SAVE_FACE = dict(FACE_VIEWER, lip_tension=1., brow_l=.82,
                 brow_r=.16, brow_raise=.40)
FINAL = dict(SAVE_FACE)
LAUGHS = ((277/24, .25), (287/24, .25))

FALL_START = 5.75
FIRST_EXTREME = 6.0
FLASH = 6.0
KEYS = [
    (0., READY), (1., ADMIRE), (1.2, ADMIRE), (1.7, PROUD),
    (2.05, PROUD), (2.15, WINK), (2.25, WINK), (2.35, PROUD),
    (5., PROUD), (5.2, SOFTEN), (5.4, EXHALE),
    (FALL_START, ANTICIPATE), (FLASH, GRIMACE), (149/24, GRIMACE),
    (6.75, RECOVERED), (8., RECOVERED), (8.50, READ_PHOTO),
    (9.25, READ_PHOTO), (10.25, FACE_VIEWER), (11.5, SAVE_FACE),
    (12.5, FINAL), (13., FINAL),
]


def pose_at(t):
    """Pose complète. La pose à 6 s est la seule source de la photo figée."""
    for (ta, a), (tb, b) in zip(KEYS, KEYS[1:]):
        if ta <= t <= tb:
            raw = min(1., max(0., (t-ta)/(tb-ta)))
            # Une seule chute accélérée : le grotesque entier n'est atteint
            # au clic144. Aucun rebond.
            u = raw*raw if ta == FALL_START and tb == FIRST_EXTREME else smooth(raw)
            p = dict(b) if raw >= 1.0 else {key: a[key]+(b[key]-a[key])*u for key in a}
            break
    else:
        p = dict(KEYS[0 if t < 0 else -1][1])
    # Le seul clin d'œil est celui de vanité déjà inscrit dans KEYS.
    # Sous .30, le morphing du rig donnerait un contour vert vide. Terminer
    # la fermeture en arc franc évite cet artefact sans redessiner les yeux.
    for side in ('l', 'r'):
        if p['eye_open_'+side] < .30:
            p['eye_open_'+side] = 0.0
    # Deux minuscules contractions soufflées, sans déplacement des pieds.
    # Un seul lobe par syllabe, strictement nul hors de sa fenêtre et avant
    # la demi-seconde finale. Visage, bras et corps partagent cette affine.
    for start, duration in LAUGHS:
        if start < t < start+duration:
            u = (t-start)/duration
            pulse = math.sin(math.pi*u)**2
            p['warp_sy'] -= .006*pulse
            p['he_open'] = pulse
    return p


def motion_at(t):
    """Le jeu physique est dans character_at, également utilisé par la photo."""
    return {'sx': 1.0, 'sy': 1.0, 'dx': 0.0, 'dy': 0.0}


def deformation_at(p):
    """Paramètres affines communs au torse, aux bras et au visage.

    x'=200+sx*(x-200)+skew*(y-437) ; y'=437+sy*(y-437).
    Les pieds sont exclus de ce groupe ; les mains n'en sont jamais exclues.
    sx : .97..1.12 ; sy : .68..1.13 ; skew : -.07...008.
    """
    return {'sx': float(p.get('warp_sx', 1.)),
            'sy': float(p.get('warp_sy', 1.)),
            'skew': float(p.get('warp_skew', 0.)),
            'anchor_x': 200., 'anchor_y': 437.}


def _episode_mouth(p, uid):
    """Même bouche : séduction puis sourire maigre, crispé et oblique."""
    g = min(1., max(0., p.get('grimace', 0.)))
    v = min(1., max(0., p.get('vanity', 0.)))
    pout = min(1., max(0., p.get('pout', 0.)))
    shame = min(1., max(0., p.get('shame', 0.)))
    surprise = min(1., max(0., p.get('surprise', 0.)))
    nervous = min(1., max(0., p.get('nervous', 0.)))
    tension = min(1., max(0., p.get('lip_tension', 0.)))
    he = min(1., max(0., p.get('he_open', 0.)))
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
    # Presque un trait : un coin minuscule et retenu, pas un U heureux.
    shy = [(-13., 2.5), (-4., -1.2), (6., -1.2), (13., 3.),
           (6., -1.2), (-4., -1.2)]
    shocked = [(-17., 0.), (-17., -30.), (17., -30.), (17., 0.), (17., 30.), (-17., 30.)]
    # Sourire retenu et étiré : gauche presque plate, coin droit pincé
    # nettement plus haut. Éviter l'arc en U du premier montage, trop serein.
    # Le pincement augmente pour sauver les apparences, sans autre geste.
    tense = [(-33.-2*tension, 1.-2*tension), (-12., -3*tension),
             (8., 4.-4*tension), (31.+tension, -12.-4*tension),
             (15., 7.-3*tension+2*he), (-17., 5.-2*tension+2*he)]
    for shape, weight in [(grin, v), (lips, pout), (crooked, g), (shy, shame), (shocked, surprise), (tense, nervous)]:
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
    tongue_clip = f'clip-path="url(#{clip})"' if g < .75 else ''
    # Une petite commissure marque le sourire forcé. Elle n'apparaît que
    # dans la nouvelle expression ; les anciens SVG restent identiques.
    crease = ''
    if nervous > .00001:
        x, y = tense[3]
        crease = (f'<path d="M{x:.3f} {y:.3f} q4 -3 7 1" '
                  f'fill="none" stroke="{ink}" stroke-width="2.8" '
                  f'stroke-linecap="round" opacity="{nervous:.5f}"/>')
    return (f'<g id="mouth" transform="translate(205 321)">'
            f'<path d="{d}" fill="{ink}" stroke="{ink}" stroke-width="4.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<defs><clipPath id="{clip}"><path d="{d}"/></clipPath></defs>'
            f'<g {tongue_clip} opacity="{op:.3f}">'
            f'<ellipse cx="{tongue_x:.3f}" cy="{tongue_y:.3f}" rx="{tongue_rx:.3f}" '
            f'ry="{tongue_ry:.3f}" fill="{PALETTE["tongue"]}" '
            f'stroke="{ink}" stroke-width="{2.4*g:.3f}"/>'
            '</g>'+crease+'</g>')


def character_at(p, uid='mou'):
    """Le rig original et son jeu : pieds fixes, torse/bras/visage solidaires."""
    fragment = character_fragment(p, uid=uid)
    assert abs(p.get('arm_clasp',0.))<1e-8, 'Aucun clasp ventral dans cette reprise.'
    # Bras d'origine conservés tels quels dans character_fragment().
    # Les yeux gardent leurs contours et leurs masques d'origine ; seule la
    # direction de chaque pupille diverge de la direction commune. Ne pas
    # modifier le rig partagé pour cette expression locale de l'épisode.
    cross = min(1., max(0., p.get('cross', 0.)))
    if cross > .00001:
        for side, cx, cy, rx, sign in [('l',164,235,34,1), ('r',242,232,33,-1)]:
            original = _eye(cx, cy, rx, side, p, uid)
            directed = dict(p, pupil_x=p.get('pupil_x',0.)+sign*cross)
            assert original in fragment
            fragment = fragment.replace(original, _eye(cx,cy,rx,side,directed,uid), 1)
    if any(p.get(k, 0.) > .00001 for k in ('grimace', 'vanity', 'pout', 'shame', 'surprise', 'nervous')):
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
    if t<1:return 'active le retardateur'
    if t<3:return 'certain d’être magnifique'
    if t<5:return 'conserve sa meilleure pose'
    if t<FALL_START:return 'croit la prise terminée et souffle'
    if t<FLASH:return 'se relâche trop tôt'
    if t<149/24:return 'flash : louche et sourire crispé capturés'
    if t<6.75:return 'se replace sans effacer sa grimace'
    if t<8.:return 'photo exacte, figée et lisible'
    if t<9.25:return 'regarde la photo sous l’objectif'
    if t<10.25:return 'cherche le spectateur en louchant'
    if t<11.5:return 'essaie de sauver les apparences'
    if t<12.5:return 'deux hé soufflés et minuscules secousses'
    return 'sourire maladroit et louche, silence tenu'
