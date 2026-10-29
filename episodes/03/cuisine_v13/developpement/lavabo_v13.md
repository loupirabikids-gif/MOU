# Lavabo et bout de moufle — V13

La demande porte sur le rinçage du bout des doigts, geste quotidien bref
après un contact en cuisine. MOU garde sa moufle originale, sans création de
doigts humains : son bord arrondi distal seul effleure le jet. Le poignet
reste levé à droite du filet, clairement hors de l’eau.

Le nouveau gros plan conserve le robinet et la palette du décor. La cuve
possède maintenant un rebord, une paroi intérieure et une bonde, ce qui rend
sa profondeur plus lisible. Le fort débit demandé reste volontairement
excessif pour ce minuscule rinçage ; l’eau non interceptée tombe dans la cuve.
Les petites projections partent du bout de la moufle et restent au-dessus du
bassin. Aucun visage, corps ou ustensile de cuisine n’entre dans l’insert.

La main approche la commande, accompagne le levier pendant l’ouverture,
présente son extrémité sous le jet avec un très petit frottement, revient
fermer le robinet puis sort du cadre. Les mêmes repères d’événements sont
utilisés pour les cinq lavages, dont les durées suivent leur accélération.

## Construction conservée

`sink.py` emploie directement `_arm('left', 0, 1)` du rig canonique.
Son contour n’est ni redessiné, ni étiré, ni tronqué. Une seule rotation et
translation, avec l’échelle uniforme `2.3 × 0.70 = 1.61`, placent l’extrémité
dans l’insert. Le bras continue hors cadre à droite. La couleur humide est
strictement découpée par le contour original et par la zone du filet : elle
ne remplace pas la main. Le gros plan montre une seule main ; le personnage
complet conserve toujours ses deux moufles dans les plans larges.

Le changement de cuve s’applique au gros plan uniquement ; le décor validé
des plans larges reste celui du projet. Cadrage : `viewBox 0 925 270 480`,
exportable en 1080 × 1920 ou 540 × 960 sans modifier la géométrie.

## Études et vérification

`controle/etude_lavabo_v13/planche_cinq_lavages.png` contient quinze poses
rendues : ouverture, rinçage et fermeture pour chacun des cinq cycles.
La planche et les images 8,600 s /8,170 s ont été réellement examinées.
Le bout de moufle est au contact du jet ; le poignet et le reste du bras
restent à droite et secs. Le contact du levier et la profondeur du bassin
sont visibles. Le critique indépendant a donné un avis favorable sur les
études 8,600 /8,050 /9,990 s, à confirmer sur le véritable montage exporté.

`geometry_at` expose le contour canonique, ses contrôles, la matrice affine,
le poignet, l’extrémité, le demi-cercle distal et la géométrie du jet pour une
vérification indépendante. Le SVG porte les identifiants
`lavabo-main-native`, `lavabo-jet-primary` et `lavabo-wet-tip`. Une affirmation
numérique n’est pas substituée à l’examen des images ; les contrôles de
chevauchement et la relecture des exports relèvent des audits de la révision.

Ces études sont des images calculées ; elles ne constituent ni une lecture
continue du film ni une écoute perceptive du son.
