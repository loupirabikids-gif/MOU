# Rig Blender 2D de MOU

Le constructeur `sources/build_blender.py` crée une scène Blender 4.3.2 de
120 images à 24 images/s, 1080 × 1920. Le personnage est formé de vraies
courbes 2D remplies, avec des contours polygonaux et des clés de forme.
Les décors fixes et le lettrage utilisent des images emballées dans le `.blend`.
Aucun film ni rendu complet du personnage n'est utilisé comme surface animée.

## Commande de reconstruction

Depuis `personnages/MOU_blender_v1/` :

```sh
blender --background --factory-startup --threads 4 \
  --python sources/build_blender.py -- --build --stills \
  --preview-width 540 --samples 16
```

Entrée : `assets/vector_frames.json`. Décors : `assets/plates/plates.json`.
Sortie : `MOU_blender_v1.blend`. Aperçus : `work/scene/stills/`.
Les options `--input`, `--output`, `--render-dir` et `--still-frames` permettent
de changer ces chemins et les images rendues. `--stills` rend de vraies images
Blender après sauvegarde de la scène HD. Sans cette option, seul le `.blend`
est construit ; un rendu complet peut ensuite être lancé avec Blender `-a`.

## Ce qui pilote réellement le dessin

`CONTROLES_pose` contient un poids animé pour chaque état source, sous la forme
`Pose_012_assurance`, `Pose_054_resistance`, `Pose_099_cede`, etc. Ces propriétés
ont des clés Blender natives. Des drivers les normalisent et pilotent les
`value` des clés de forme de toutes les courbes et des plans de lettrage.
Changer les poids modifie donc réellement le personnage. Les marqueurs
`assurance`, `resistance`, `cede` permettent de retrouver les trois poses.
L'action `MOU_5_secondes_poids_de_poses` est conservée comme asset Blender.

Pour retoucher un poids dans l'animation, sélectionner le contrôleur, ouvrir
ses propriétés personnalisées et insérer une clé sur le poids modifié.
Pour mélanger les dessins librement, désactiver les F-curves correspondantes
avant de régler les poids. Un ensemble de poids nuls revient à la forme Basis.
`frame_lecture` affiche l'image courante par un driver natif.

`CONTROLES_deplacement_MOU` est le parent des éléments mobiles. Sa transformation
agit réellement sur le personnage et ses ancres. Les objets `a.mainleft` et
`a.mainright` sont des repères dont les positions sont pilotées par les mêmes
poids normalisés que les courbes. Un changement de poids déplace donc ensemble
le dessin de la main et son ancre. Les sommes sont réparties en petits drivers
natifs, sans handler ni expression dépassant 255 caractères. La cuillère est exprimée dans les
coordonnées locales de `a.spoon_grip` et utilise une contrainte **Child Of**
active sur cette ancre. `a.spoon_grip` utilise **Copy Location** vers
`a.mainleft` lorsque `spoon_held` vaut vrai dans les états source ; l'influence
est pilotée par la propriété réelle `spoon_held` du contrôleur, elle-même
animée avec une interpolation constante. La cuillère suit donc la position
de la main résultant des poids actifs. Lorsqu'elle est garée, l'ancre de cuillère
retrouve sa trajectoire source. Ces ancres ne sont pas un système IK des bras.

## Modifier une expression ou une moufle

1. Aller à la pose voulue dans la timeline.
2. Sélectionner une courbe de `02_MOU_corps_et_visage` ou
   `04_MOU_bras_et_moufles`.
3. Dans Données > Clés de forme, sélectionner la clé de l'étape concernée.
4. Passer en mode Édition avec Tab et déplacer ses points.

La clé de cette étape est modifiée dans l'objet vectoriel. Le mode d'isolation
d'une clé de forme permet de travailler un dessin sans le mélange courant.
Les poids sont partagés entre les objets ; leurs dessins restent éditables
séparément. C'est un rig de poses 2D, sans squelette ni IK. Les silhouettes
des bras et moufles viennent des bras natifs de MOU, sans redessin automatique.

## Masques, couleurs, plans et ressources

Les masques des pupilles et les clips SVG sont résolus géométriquement par
`sources/vectorize.py`, avant création des courbes. Chaque contour extérieur
et chaque trou deviennent une spline fermée du même objet. Un rééchantillonnage
et un alignement cyclique ne changent que la distribution des points, pas
l'orientation du dessin. Les séries de contours ont un nombre de points fixe.
Les noms et images des trois poses sont lus dans `key_poses` du JSON.
Une forme absente reçoit un contour effondré et une visibilité animée constante.
Les poids des états absents sont exclus du mélange de cet objet, pour éviter
un rétrécissement visible juste avant sa disparition.

Les matériaux utilisent des aplats d'émission. Les valeurs RGB sRGB des sources
sont converties en linéaire avant l'émission, puis affichées avec Standard,
sans contraste ajouté ni exposition. Les images sont lues comme sRGB.
La caméra orthographique utilise le cadre source `[25,220,1000,1777.77778]`
jusqu'à l'image 104, puis `[0,925,270,480]` dès l'image 105. La coupe est une
clé constante, comme le changement de visibilité entre les deux plans.

L'ordre des surfaces est explicite : fond −1000, personnage 0–399,
premier plan 500, cuillère 600–650, bras 700–899 et grain 950 ou plus.
Le lavabo utilise son propre fond et ses surfaces vectorielles.
Les coordonnées SVG sont converties en unités Blender à 1/100, avec Y inversé.
Toutes les textures chargées sont emballées ; aucun chemin temporaire n'est
nécessaire pour ouvrir le `.blend` livré. Aucun handler Python n'est requis
pour la lecture de l'animation.

## Vérifications réalisées sur les primitives

Blender 4.3.2 a effectivement rendu une courbe à trou et sa clé de forme dans
`work/scene/probe_hole.png`. Un deuxième essai construit par le véritable
constructeur a produit une courbe trouée animée, une cuillère vectorielle et
la coupe de caméra à l'image 105. L'image source verte `[0.25,0.7,0.1]` ressort
aux environs de `[64,179,26]` hors bord, conformément à la conversion sRGB.
Ces essais de primitives sont distincts de la revue des vraies poses MOU et
ne constituent pas une validation artistique du prototype.

Un probe supplémentaire a construit le vrai IR de 38 états sans rendu. À
l’image54 maintenue fixe, remplacer le poids de résistance par celui de cède
a déplacé à la fois le contour évalué du bras gauche et son ancre : X de
l’ancre 4,488220 → 1,816776 unités, conformément aux deux états source. La
prise de cuillère a suivi la même position. Les 3779 drivers étaient valides ;
la plus longue expression comptait 159 caractères. Rapport privé :
`work/scene/probe_real_pose_anchors.json`.

## Correction des transitions pendant la revue du film

Le premier essai utilisait 38 états. La critique du MP4 a repéré des défauts
entre les poses : fines pointes de bouche à77, coin et repli du contour de
bras à92–98, et trou de paume à114. Le polygone interpolé de la paume
s'auto-intersectait à114 et115, alors que les dessins SVG natifs étaient propres.

La banque finale ajoute les contours natifs aux images76–79,92–98,114–115,
soit51 états. Aucun dessin de bras, gag ou timing n'est changé. La région
76–120 est rendue à nouveau pour couvrir les transitions après ces insertions.
Ce problème rappelle qu'un morph de contours exige une revue des images
intermédiaires ; les poses fixes et les drivers valides ne suffisent pas.

Les courbes du plan lavabo dont au moins un état est translucide utilisent
le mode de surface `BLENDED` : eau, humidité et grains qui s’effacent. Ce mode
produit un aplat transparent sans tramage aléatoire à huit samples. Le tri
reste celui des objets 2D étagés en Z. Un probe réel de l’image114 à540px a
été revu sans défaut de tri visible. Cette scène émissive n’utilise pas les
passes de raytracing incompatibles avec ce mode.
