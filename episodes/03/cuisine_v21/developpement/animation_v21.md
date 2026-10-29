# Jeu de MOU et nouvelle clôture — V21

Référence : costume et construction V20 conservés. La demande vise une
animation émotionnelle plus lisible et la découverte du tablier après le
dernier papier tombé au sol. Aucun nouveau dessin de corps, de bras ou de
moufle ; les contrôles de paupières, sourcils, bouche et regard restent natifs.

## Réactions antérieures

- 7–7,75 s : le plaisir est interrompu, regard tenu sur la main, étonnement
  puis sourcils serrés et bouche contrariée avant de regarder le lavabo.
- Inspections des rituels 2 à 5 : une seule crispation brève, progressivement
  plus appuyée, sans comprimer plusieurs émotions dans leurs 0,2 secondes.
- 36,05–36,8 s : découverte déçue du dernier papier, regard au tube, puis
  détermination ; le sourire de soulagement ne reste pas pendant tout le geste.

Ces réactions changent seulement le visage et le regard. Les 966 états
historiques avant 40,25 s gardent leurs bras, mains, transformation du corps,
objets, rouleau et trajectoire de papier.

## Clôture

| Temps | Intention et jeu |
| --- | --- |
| 40,25–40,75 s | Découvrir la goutte sur la gauche ; sourcils levés puis agacement, petit recul global. |
| 40,75–41,4 s | Regard au tube avant le geste ; la droite répète le réflexe de prendre du papier puis s’arrête devant le vide. |
| 41,4–41,85 s | Regard vers le tablier d’abord, yeux/sourcils s’ouvrent ensuite ; MOU se redresse de 60 pixels avec son rig entier avant de déplacer la gauche. |
| 41,85–42,0 s | Approcher la calotte humide du haut du tablier. |
| 42,0–42,4 s | Une passe simple : grip gauche relatif de (535,1208) à (575,1208), translation verticale −60 commune au rig, sans allonger le bras. La goutte s’absorbe en 120 ms. |
| 42,4–42,65 s | Ramener les deux mains à la pose native jointe devant le ventre et laisser voir la trace ; bref soulagement. |
| 42,65–43,25 s | Le sourire tombe ; regarder le tas gaspillé, corps entier qui s’affaisse du redressement −60 à la position +14 pixels, avec une courte translation vers la poubelle. |
| 43,25–43,75 s | Revenir vers le spectateur, puis petit sourire embarrassé avec sourcils inquiets et yeux encore assez ouverts. |
| 43,75–44,5 s | Tenir ce regard sans nouveau clignement ni mouvement gratuit. |

Une première variante à demi-paupières lisait davantage un air suffisant.
Après examen de trois poses réellement rendues, la direction indépendante
retient d’abord une variante plus ouverte. Une lecture à froid de la succession
demande ensuite un geste plus loin du menton et moins d’assurance finale :
le redressement rend le tissu visible, les mains reviennent au ventre et les
deux sourcils restent inquiets (0,90/0,90). Les paupières finales 0,91/0,94 et
le sourire réduit à 0,13, ouverture 0,015, évitent la demi-paupière sceptique.
Ce petit sourire arrive seulement après le regard au spectateur. Six nouvelles
images de cuisine réellement rendues ont été vues à 41,65 / 42,1 / 42,35 /
42,7 / 43,15 / 44 s : la main passe sur la poche du tablier et se retire du
menton ; la revue du nouveau mouvement exporté reste à faire.

## Champs exposés au rendu

- `ending_phase`, `emotion_stage`, `ending_camera=True`.
- `ending_drop.anchor` : plus bas sommet réel de la calotte gauche, transformé
  dans le monde, plus la demi-largeur du trait. `amount` reste 1 jusqu’à
  42,0 s puis s’efface sur 120 ms au contact du tissu.
- `apron_wetness` : progression 0→1 après ce contact, puis persistante.
- `contact_apron.active` : 42,0–42,4 s ; `point`/`native_point` donnent le centre
  du tissu (195,385), `point_world`/`point_local` l’ancrage réel mobile de goutte,
  `contact_time` et `stroke_end` les deux bornes.
- `acting_body_offset` : seulement une translation commune du rig, des bras,
  des mains et du costume. Aucun changement de forme du personnage.

Pendant la passe, l’ancrage réel court de (506,19 ; 1203,31) à
(549,13 ; 1204,92), soit localement x185,30→203,97 / y384,05→384,75.
La main droite se tient à côté du tissu pendant l’essuyage pour dégager la
trace, puis les deux mains retrouvent ensemble la pose native de repos.

Le temps des accessoires historiques est figé au début de la clôture pour
qu’aucune ancienne action ne réapparaisse après la 41e seconde. La cinquième
boulette reste au sol et les quatre grandes restent dans la poubelle.

Contrôles avant gel : fonctions natives de géométrie et raccord identiques
au niveau AST ; anciens bras/objets identiques sur 966 images ; deux mains,
une bouche et contacts finis sur les 102 images de clôture. Le geste ne
déplace pas la main humide à travers le corps vers le rouleau ; seule la
droite déjà à portée cherche le papier. La critique du montage réellement
produit reste indépendante et précède le final.
