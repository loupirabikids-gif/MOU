"""Thirteen motivated 2D framings of the existing MOU lockbox drawings.

Every viewport transforms the whole staged image. No limb, prop or background
is repositioned by this module, and no crop is presented as a new 3D angle.
"""
from __future__ import annotations


def ease(t, a, b):
    u=max(0.,min(1.,(t-a)/(b-a)))
    return u*u*(3.-2.*u)


def box(x, y, width):
    return (float(x),float(y),float(width),float(width)*16./9.)


SHOTS=(
    ('P01',0.,2.1,'wide_high',box(220,620,760),
     'Lire le projet de travail, puis le regard attiré vers le téléphone.'),
    ('P02',2.1,4.6,'lock_insert',box(100,200,780),
     'Voir la privation volontaire : dépôt, couvercle, bouton et trente minutes.'),
    ('P03',4.6,6.,'medium',box(70,500,740),
     'La confiance revient vers la feuille ; le coffre reste une présence latérale.'),
    ('P04',6.,7.,'clock',box(80,160,920),
     'Une seule minute écoulée contredit sa certitude.'),
    ('P05',7.,10.,'medium',box(70,500,740),
     'La tentative de travailler se bloque avant le regard vers le coffre.'),
    ('P06',10.,12.25,'work_close',box(80,420,900),
     'Isoler la main qui abandonne le crayon et la réaction qui suit.'),
    ('P07',12.25,15.2,'medium',box(160,610,570),
     'Les yeux et la joue appuyée rendent le renoncement prioritaire.'),
    ('P08',15.2,18.4,'medium',box(0,0,1080),
     'Révéler la posture fermée, la feuille vide et le passage du temps.'),
    ('P09',18.4,21.7,'low',box(240,550,825),
     'Le coffre prend toute son attention ; un rapprochement court puis une pause.'),
    ('P10',21.7,23.,'box_insert',box(40,450,900),
     'Attendre la dernière seconde avec le verrou, sans détour du regard.'),
    ('P11',23.,25.4,'face_box',box(0,70,1080),
     'Garder la cause et la réaction ensemble pendant ouverture et reprise.'),
    ('P12',25.4,27.,'phone_final',box(160,500,710),
     'La satisfaction absorbée remplace le long maintien en l’air.'),
    ('P13',27.,30.,'phone_final',box(90,1490,180),
     'Les trois cases vides, puis MOU heureux au téléphone et l’heure dans le même angle.'),
)


def framing_at(t):
    t=max(0.,min(30.-1.e-8,float(t)))
    selected=next((item for item in SHOTS if item[1]<=t<item[2]),SHOTS[-1])
    identifier,start,end,view,viewport,intent=selected
    movement='hold'
    if identifier=='P09':
        # The desire becomes legible, then movement stops before the last digit.
        u=ease(t,18.55,19.25);x,y,w,h=viewport
        smaller=w*(1.-.03*u);dh=h-smaller*16./9.
        viewport=box(x+(w-smaller)*.5,y+dh*.5,smaller)
        movement='push_in_2d_then_hold'
    elif identifier=='P13':
        # The paper remains in the exact frontal desk perspective throughout.
        u=ease(t,28.,29.2);finish=box(0,60,1080)
        viewport=tuple(a+(b-a)*u for a,b in zip(viewport,finish))
        movement='paper_reveal_pullback_2d_then_hold'
    return {'shot_id':identifier,'start':start,'end':end,'view':view,
            'viewport':viewport,'intent':intent,'movement':movement}
