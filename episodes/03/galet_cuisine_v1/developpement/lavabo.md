# Lavabo du galet — réalisation ciblée

31 octobre 2026. Module `sources/sink_galet.py`, indépendant de l'ancien rig
MOU, de `mitten.py` et de tout avant-bras. Une seule moufle est émise par
`character.hand_svg`, avec le même dessin à pouce arrondi que le prototype.

## Mise en scène

Les quatre inserts suivent la chronologie locale : approche de la commande,
contact au bout du levier, ouverture, rinçage des bouts, retour au levier,
fermeture et retrait. Le jet ne démarre qu'à la fin de l'ouverture et s'arrête
après la fermeture. Les petits mouvements du pouce et une rotation de ±2°
sont calés dans le rinçage ; ils ne consistent pas à déplacer la paume entière
sous l'eau. Les deux premiers lavages ont trois petits frottements, les deux
derniers deux frottements plus brefs.

Le cadre conserve `viewBox="0 925 270 480"`. Le bassin et le robinet reprennent
le dessin de l'insert approuvé. La moufle utilise une échelle de 0,70 dans ce
cadre : sa largeur est voisine de 70 unités, contre environ 200 pour le bassin.
Elle n'occupe donc pas toute la cuve. Le pouce se trouve au-dessus du bloc
arrondi ; aucune pointe ou doigt humain supplémentaire n'est dessiné.

## Contacts exposés

`geometry_at(t,cycle)` donne la pose de main, son vrai point de contour `tip`,
la cible, les contrôles Bézier locaux et mondiaux, des polygones échantillonnés,
la paume de référence, le levier et les limites du jet/bassin. Le point `tip`
est le nœud 15 du contour réellement déformé, transformé par la vraie matrice
de main ; il n'est pas une correction de métadonnée appliquée à un autre dessin.
La moufle est ancrée sur ce point à chaque image, y compris quand le pouce bouge.

Pendant l'ouverture et la fermeture, ce point suit exactement la commande.
Pendant le rinçage, il reste près de (102,1125), avec des déplacements d'environ
un pixel de monde. Le centre de paume reste à droite du jet. Un clip du contour
réel limite la légère couleur humide à la partie qui intersecte l'eau.

IDs stables : `hand-left`, `hand-outline-left`, `commande-robinet`,
`lavabo-jet-primary`, `lavabo-wet-tip`. Aucune main droite, aucun corps ou visage
n'est émis dans ces inserts. Le module accepte les définitions et le fond du
renderer ; il ajoute le gradient du nouveau personnage uniquement s'il manque.

## Contrôle local effectivement réalisé

Douze images ont été rendues et ouvertes : contact, rinçage et fermeture pour
chacun des quatre cycles. Preuves privées : `work/lavabo_galet/`.
Les SVG de ces douze repères ont une seule moufle et des IDs uniques.

Sur tous les repères 24 images/s de ces inserts : erreur maximale entre ancre
et contour calculé 2,30e-13 unité ; écart maximal au vrai levier 2,85e-14.
Pendant le rinçage, la référence de paume est au moins à x=132,52 ; la limite
droite nominale du jet est x=116. Le pouce atteint une fermeture d'environ
0,64, avec des extrêmes visibles sans changement de taille de la moufle.

Ces mesures et images fixes sont un contrôle local, pas une revue du montage
continu ou de sa bande-son. La critique du vrai MP4 et la QA indépendante du
renderer complet restent nécessaires avant la livraison de l'épisode.
