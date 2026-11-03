# MOU dans « Le coffre » — adaptation du personnage

L'utilisatrice demande de remplacer Patchy par le MOU original. La référence
`references/MOU_reference.png` a été ouverte : silhouette vert citron à double
bosse, deux grands yeux ovales blancs, sourcils et pupilles prune, deux bras
avec leur extrémité arrondie et deux petits pieds sombres. Aucun nez, oreille,
queue ou vêtement du raton laveur n'est conservé.

## Source du dessin

`sources/mou_rig_original.py` est une copie octet pour octet du `mou_rig.py`
canonique. Son corps, ses deux pieds et les fonctions `_eye`, `_brows`,
`_mouth` sont réutilisés. La silhouette n'est pas une recoloration de PATCH.
Les paramètres de jeu hérités sont un vocabulaire de données provenant de
`jeu_support.py` ; aucune de ses primitives de dessin n'est appelée.

`sources/personnage.py` adapte ce dessin aux positions du téléphone, du
crayon et du bouton. Sa matrice native est fondée sur le canevas 400 × 500 :
échelle `2 * actor.scale`, centre `actor.cx - 35 * actor.scale + lean.x`,
plancher `actor.floor_y - 150 * actor.scale + lean.y`, pivot natif `(205,449)`.
Les épaules sont les points natifs `(105,291)` et `(297,291)`. Les contrôles
de mains et les objets gardent leurs positions dans le monde.

Le coordinateur élargit le seul plan visage/coffre, car le nouvel œil gauche
plus large était rogné par l'ancien cadrage. Le dernier rendu des poses prend
en compte ce nouveau plan ; le corps entier, les deux yeux et l'affichage
utile se lisent ensemble.

## Bras continus et mains

La construction des bras reprend la topologie native : un ruban cubique de
rayon 10,5 unités, qui s'élargit progressivement à 19 unités au bout, avec
une demi-circonférence terminale. Il n'y a pas de manche, de couture de
poignet ni de nouvelle paume indépendante.

Les points de contrôle sont articulés vers les contacts du film. Pour une
courte portée, la tangente se redresse vers l'axe épaule/main ; le contrôle
du coude reste à distance du bout. Cette règle corrige le petit crochet
observé à 19,3 s et la boucle vue au bord du téléphone à 25,3 s dans une
première planche. La largeur de la moufle et la continuité du contour restent
celles de la construction native.

Le décor a besoin d'un bras derrière l'objet et d'un bout de main devant
l'objet pendant une prise. Le calque `arms` contient donc le contour continu.
Le calque `hands` redessine exactement la même extrémité, découpée dans ce
contour par un clip distal. Il ne crée pas de deuxième main ni de trait de
séparation. La façade peut ensuite masquer cette extrémité quand la main
entre dans le coffre avec le téléphone.

Identifiants du rendu : `mou-arm-left/right`, `mou-hand-left/right` et
`mou-foot-left/right`. Le conteneur indique `data-character="mou"` et
`data-rig="mou_rig_original"`. Les repères retournés par `anchors` suivent
les vraies épaules, le point de prise à l'intérieur de l'extrémité native,
son poignet et les deux pieds.

## Expressions et revue

Les regards, ouvertures des yeux, sourcils et sourire sont traduits vers
les contrôles du MOU original. Les faibles ouvertures finissent sur l'arc
fermé natif : la première version laissait une lentille verte vide quand
l'aperture rétrécissait plus vite que la paupière. La surprise utilise une
bouche ronde sans nouvelle anatomie ; les autres bouches viennent du rig.

Douze poses réellement composées ont été rendues et ouvertes : début,
prise, dépôt, bouton, retour au travail, ennui, bras repliés, bâillement,
approche basse, ouverture, joie et pose au téléphone. La planche corrigée
est conservée dans `work/rig/planche_12_corrigee.png`. Les détails à 19,3 s
et 25,3 s ont aussi été examinés par la critique indépendante, qui ne retient
plus les crochets provisoires. Les deux petits pieds restent visibles dans
la joie. La revue des transitions du vrai montage appartient à une étape
distincte avant la livraison ; aucune audition n'est revendiquée ici.

## Correctif après la première animatique

La critique des vraies images a trouvé un petit triangle interne dans la
moufle gauche libre vers 24,75–24,92 s, avant la prise bilatérale du téléphone.
L'ancien contrôle de coude orientait la tangente terminale vers l'arrière
du bras pendant ce très court retour sur le ventre. Pour la main gauche
dans cette anticipation de joie, la tangente est maintenant contrainte vers
le cône avant de sa portée. Le contour reste celui du même ruban et de son
extrémité native ; aucune paume ni aucun masque de cache ne sont ajoutés.

Sept images sont modifiées, de f593 à f599 à 24 ips (24,708–24,958 s).
Le bras droit est identique sur les 720 états, les centres de prise des deux
mains et du téléphone ne sont pas déplacés. Treize images composées entre
f592 et f604 ont été rendues ; la critique a ouvert la planche et les détails
f596, f599 et f600 et ne retient plus le triangle ou de nouvelle boucle.
Cette correction du rendu ne change ni le rig canonique ni le scénario.
