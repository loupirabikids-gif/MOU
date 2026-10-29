# Sel, cinquième gaspillage et continuité matière V13

Ajouts demandés : une pincée de sel prise dans une petite coupelle puis
saupoudrée dans la poêle, suivie d’un nouveau lavage. Le modèle et les deux
moufles ne sont pas redessinés. `art.py` dessine les accessoires ; les prises,
les bras et l’origine des émissions restent fournis par l’animation native.

## Sel visible sans texte

La coupelle ouverte est présente dès l’ouverture, à (590,1284). Elle reprend
le prune, le lavande et le crème du décor ; le petit monticule blanc et ses
grains indiquent un condiment de cuisine, sans lettre ni pictogramme.
`art.salt_svg(salt, playback_time, layer='bowl')` est placé avec les objets
sur le plan de travail, derrière les bras. Le calque `layer='grains'` passe
après les bras. Le temps transmis est celui du film, pas l’ancienne horloge
des actions réutilisées.

Huit émissions sont fournies par l’animation avec leur heure, l’extrémité
réelle de la moufle à cet instant et leur point d’arrivée dans la poêle.
Chaque grain suit son propre départ, une chute courte de 0,24 s et une cible
intérieure à la poêle. Les coordonnées sont conservées comme attributs SVG
pour les contrôles indépendants. Aucun grain ne provient d’une main fantôme.
La petite pincée blanche reste attachée à la moufle pendant le transport.

La première étude a révélé une coupelle masquée par la moufle droite au repos.
La position de cette main d’appui pendant le sel est corrigée par l’animateur,
sans agrandir ni étirer les membres. Les grains initiaux étaient très discrets
sur les vignettes téléphone ; leur rayon est augmenté modérément de 2,2–2,9
à 3,2–4 unités. Les huit émissions et leurs origines restent identiques.
La nouvelle étude montre la main droite dégagée vers sa pose native d’appui
sur le plan de travail : la coupelle est visible pendant le transport, puis
les grains quittent la moufle gauche au-dessus de la poêle. Le léger zoom
du réalisateur rend ces indices plus lisibles sans changer le dessin de MOU.

## Poubelle de zéro à cinq boulettes

Centres : (140,1700), (195,1620), (135,1537), (201,1472), (201,1400).
Rayons : 47,53,59,61,22. Rotations : -12,17,-8,14,12 degrés.
Les trois premières grosses boulettes restent aux mêmes emplacements. La
quatrième est un nouveau gaspillage ; la cinquième reste le petit bout final.
Les silhouettes sont déterministes avec les graines visuelles 1,2,3,3,4,
indépendantes du numéro de rituel. La petite boulette conserve ainsi son
ancien contour miroir V11 en main, en vol et dans le panier.

Les études de pile ont repéré une cinquième boulette flottant à (155,1390),
puis un écart résiduel à (201,1382) dû à la rotation du gros papier. Le centre
final (201,1400) est choisi après rendu et examen des véritables silhouettes :
le petit papier repose visiblement sur le quatrième. Les positions de vol et
de réception sont synchronisées avec l’animateur, pas retouchées seulement
sur l’image de poubelle.

## Froissage et dernier morceau conservé

La petite feuille reste de 64 × 88, avec ses côtés incurvés, son bord déchiré
et ses deux plis souples. La propriété `paper['tiny']` remplace l’hypothèse
« quatrième cycle = petit papier » ; `visual_seed` identifie son contour.
Cela garde le même morceau et la même boulette après ajout du cinquième cycle.

Le diagnostic géométrique a aussi confirmé que l’ancien grand froissage
miroir du deuxième rituel associait des contours de sens opposés : surface
initiale positive et cible miroir négative. Le parcours des points cibles est
inversé, sans changer la silhouette finale ou les bandes tenues. Cette
correction locale évite un contour qui se croise pendant la contraction.
Le petit froissage conserve son parcours déjà corrigé et le masque qui
contient les plis dans la matière.

## Études et portée

`controle/etude_accessoires_v13/` conserve les premières preuves et leurs
corrections, notamment `poubelle_contact_candidats.png`, la planche de
froissage entier et les poses de sel. Les images examinées sont des SVG
rendus par CairoSVG ; les véritables MP4 seront relus après export par le
critique indépendant et contrôlés par le coordinateur. Ces études ne sont
ni une écoute ni un test de compréhension auprès d’un public.

Dernière relecture réellement effectuée : `sel_planche_corrigee.png` (neuf
poses de 0,5 à 28,8 s), détails natifs à 27,55 et 28,3 s, contact de pile
finale dans `poubelle_contact_candidats.png`, et silhouettes de froissage
non rognées dans `froissage_continu_entier.png`. La pile définitive de zéro
à cinq est `poubelle_cinq_etats_final.png`. Les versions intermédiaires
restent conservées pour expliquer les deux défauts observés et corrigés.
