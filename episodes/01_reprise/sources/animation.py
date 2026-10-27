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
from mou_rig import (DEFAULT_POSE, PALETTE, character_fragment, _mouth, _arm,
                     _cubic, _tangent, _clamp, _pt, _n, _path)


def smooth(x):
    x = min(1.0, max(0.0, float(x)))
    return x*x*(3.0-2.0*x)


def state(**changes):
    return {**DEFAULT_POSE, 'grimace': 0.0, 'vanity': 0.0, 'pout': 0.0, 'shame': 0.0, 'surprise': 0.0,
            'warp_sx': 1.0, 'warp_sy': 1.0, 'warp_skew': 0.0, **changes}


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
GRIMACE = state(arm_hips=0., eye_open_l=0., eye_open_r=.83,
                pupil_x=.70, pupil_y=.68, brow_l=-.48, brow_r=.83,
                brow_raise=-.10, smile=-1., mouth_open=1., grimace=1.,
                warp_sx=1.12, warp_sy=.68, warp_skew=-.07)
STARTLED = state(arm_hips=0., eye_open_l=1., eye_open_r=1.,
                 pupil_x=0., pupil_y=.05, brow_l=.30, brow_r=.30,
                 brow_raise=.90, smile=-.12, mouth_open=0., surprise=1.)
DISCOVER = state(arm_hips=0., eye_open_l=.94, eye_open_r=.94,
                 pupil_x=0., pupil_y=.80, brow_l=.60, brow_r=.60,
                 brow_raise=.45, smile=-.58, mouth_open=.08)
DISAPPOINTED = state(arm_hips=0., eye_open_l=.83, eye_open_r=.83,
                     pupil_x=0., pupil_y=.90, brow_l=.70, brow_r=.70,
                     brow_raise=.16, smile=-.55, mouth_open=0.)
ASHAMED = state(arm_hips=0., eye_open_l=.62, eye_open_r=.68,
                pupil_x=-.70, pupil_y=.95, brow_l=.85, brow_r=.85,
                brow_raise=.05, smile=0., shame=1.,
                warp_sx=1.015, warp_sy=.97, warp_skew=.008)
# Il évite toujours l'objectif ; aucun regard final serein ou satisfait.
ADMITTED = dict(ASHAMED, pupil_x=-.78, pupil_y=.98,
                eye_open_l=.65, eye_open_r=.70)

FALL_START = 5.75
FIRST_EXTREME = 6.0
FLASH = 6.0
KEYS = [
    (0., READY), (1., ADMIRE), (1.2, ADMIRE), (1.7, PROUD),
    (2.05, PROUD), (2.15, WINK), (2.25, WINK), (2.35, PROUD),
    (5., PROUD), (5.2, SOFTEN), (5.4, EXHALE),
    (FALL_START, ANTICIPATE), (FLASH, GRIMACE), (6.125, GRIMACE),
    (6.50, STARTLED), (8.75, STARTLED), (9.15, DISCOVER),
    (9.85, DISAPPOINTED), (10.75, ASHAMED), (11.25, ADMITTED),
    (13., ADMITTED),
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
    """Même bouche : moue puis grand sourire ; après, mâchoire pendante."""
    g = min(1., max(0., p.get('grimace', 0.)))
    v = min(1., max(0., p.get('vanity', 0.)))
    pout = min(1., max(0., p.get('pout', 0.)))
    shame = min(1., max(0., p.get('shame', 0.)))
    surprise = min(1., max(0., p.get('surprise', 0.)))
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
    for shape, weight in [(grin, v), (lips, pout), (crooked, g), (shy, shame), (shocked, surprise)]:
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
    return (f'<g id="mouth" transform="translate(205 321)">'
            f'<path d="{d}" fill="{ink}" stroke="{ink}" stroke-width="4.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<defs><clipPath id="{clip}"><path d="{d}"/></clipPath></defs>'
            f'<g {tongue_clip} opacity="{op:.3f}">'
            f'<ellipse cx="{tongue_x:.3f}" cy="{tongue_y:.3f}" rx="{tongue_rx:.3f}" '
            f'ry="{tongue_ry:.3f}" fill="{PALETTE["tongue"]}" '
            f'stroke="{ink}" stroke-width="{2.4*g:.3f}"/>'
            '</g></g>')


def arm_controls(side,hips):
    if side=='left':
        down=[(105,291),(78,311),(71,336),(81,354)]
        hip=[(105,291),(24,307),(42,335),(119,351)]
    else:
        down=[(297,291),(328,311),(340,337),(329,354)]
        hip=[(297,291),(377,307),(368,335),(284,351)]
    return [_pt(a,b,_clamp(hips))for a,b in zip(down,hip)]


def episode_arm(side,hips,uid):
    controls=arm_controls(side,hips);left=[];right=[]
    for i in range(65):
        t=i/64;x,y=_cubic(controls,t);tx,ty=_tangent(controls,t)
        hand=_clamp((t-.75)/.25);hand=hand*hand*(3-2*hand);radius=10.5+8.5*hand
        left.append((x-ty*radius,y+tx*radius));right.append((x+ty*radius,y-tx*radius))
    ex,ey=controls[-1];tx,ty=_tangent(controls,1)
    tip=[(ex+(-ty*math.cos(math.pi*j/24)+tx*math.sin(math.pi*j/24))*19,ey+(tx*math.cos(math.pi*j/24)+ty*math.sin(math.pi*j/24))*19)for j in range(1,25)]
    boundary=left+tip+list(reversed(right[:-1]));d='M'+' L'.join(f'{_n(x)} {_n(y)}'for x,y in boundary)
    # The internal root is hidden under the torso, the visible emergence is on the flank.
    body='M90 310 C100 284 111 241 124 200 C141 148 175 123 208 125 C224 124 234 128 246 132 C265 119 290 121 300 137 C310 152 304 171 301 188 C305 225 313 267 319 305 C331 350 321 388 297 403 C265 424 147 426 112 405 C82 390 74 350 90 310 Z'
    sx,sy=controls[0];clip=f'{uid}-arm-root-{side}'
    hide=(f'<defs><clipPath id="{clip}"><path d="{body}"/></clipPath></defs>'
          f'<circle cx="{sx}" cy="{sy}" r="22" fill="{PALETTE["skin"]}" clip-path="url(#{clip})"/>')
    return f'<g id="arm-{side}">'+_path(d+' Z',PALETTE['skin'],'none',0,data_part='hand',data_side=side)+_path(d,sw=5.2)+hide+'</g>'



def character_at(p, uid='mou'):
    """Le rig original et son jeu : pieds fixes, torse/bras/visage solidaires."""
    fragment = character_fragment(p, uid=uid)
    assert abs(p.get('arm_clasp',0.))<1e-8, 'Aucun clasp ventral dans cette reprise.'
    hips=_clamp(p.get('arm_hips',0.))
    for side in ('left','right'):
        original_arm=_arm(side,hips,_clamp(p.get('arm_clasp',0.)))
        assert original_arm in fragment
        fragment=fragment.replace(original_arm,episode_arm(side,hips,uid),1)
    if any(p.get(k, 0.) > .00001 for k in ('grimace', 'vanity', 'pout', 'shame', 'surprise')):
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
    if t<6.125:return 'flash sur la déformation'
    if t<6.75:return 'le clic le surprend'
    if t<8.75:return 'photo exacte, figée et lisible'
    if t<10:return 'regarde le résultat sous l’objectif'
    if t<11:return 'son assurance tombe'
    return 'réaction gênée, mains baissées'
