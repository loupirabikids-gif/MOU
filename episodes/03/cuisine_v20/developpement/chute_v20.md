# Nouvelle chute — V20

Costume et principe de chute validés par l’utilisatrice avant fabrication.
Seul le dernier petit papier change de destination. Les gestes de cuisine,
les cinq lavages, les bras et mains, la durée de 41 s et le jeu de MOU restent
ceux de la V19. Les quatre premiers papiers restent fixés dans la poubelle.

| Instant | Action visible |
| --- | --- |
| 38,65 s | Même lâcher de la petite boulette, rayon 22, graine visuelle 4. |
| 39,075–39,14 s | Le bas de la boulette touche le sommet réel du tas débordant ; très bref contact tenu, cue au centre à 39,10 s. |
| 39,14–39,85 s | Rebond vers la droite, puis chute à côté de la poubelle. |
| 39,85–40,00 s | Contact au sol, minuscule rebond amorti ; centre final (325, 1805). |
| 40,00–40,25 s | Gros plan tenu sur le papier au sol et la poubelle pleine. |
| 40,25–41,00 s | Retour au plan large : MOU garde sa satisfaction devant sa main propre. |

Le contact réunit les contours réels, et non les seuls centres : la quatrième
boulette a un sommet à (227,403 ; 1403,142). Le papier final tourné à 12°
a un sommet bas décalé de (+0,318 ; +24,808). Son centre au contact est donc
(227,085 ; 1378,334). La courbe de rebond passe au-dessus du tas puis dégage
le bord droit de la poubelle avant la descente ; la fin ne doit pas se lire
comme un simple lancer manqué.

Le contact tenu couvre deux images finales (39,0833 et 39,125 s) et une image
d’animatique (39,0833 s). Il évite qu’un impact théorique à 39,1 s soit sauté
entre deux images de la grille de rendu.

Le plan poubelle utilise la même caméra, prolongée jusqu’à 40,25 s. Le dernier
papier reste au sol dans le plan large ; aucune apparition d’une cinquième
boulette dans la poubelle. Le mouvement des bras n’est pas recalculé.

Correction après animatique : le zoom initial de 2,8 coupait brièvement
la boulette pendant son approche (38,917 et 38,958 s). Le dernier gros plan
emploie désormais un zoom de 2,5, centré sur (220, 1536), pour garder toute
la trajectoire et le sol visibles sans sortir des limites du décor.
Les autres gros plans de poubelle gardent leur cadrage précédent.

Contrôles avant gel : tous les champs historiques d’état sont identiques
à la V19 sur les 928 images avant le lâcher ; seul `scene_state` change parmi
les fonctions préexistantes de l’animation. Les solveurs, le dessin et les
raccords des bras restent identiques au niveau AST. Six images SVG/CairoSVG
fraîches ont été vues aux instants 39,0833 / 39,125 / 39,5 / 39,85 / 40,125 /
40,5 s : contact tenu visible, trajectoire à droite, papier séparé au sol
et persistance dans le plan large. La revue du montage exporté reste à faire.
