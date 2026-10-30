# Mains finales — critique visuelle indépendante avant correction V28

30 octobre 2026. Demande examinée : « Les mains sont bizarres vers la fin ».
Le modèle et les deux bras/moufles doivent être conservés. Ce rapport propose
une correction de pose, sans redessiner ni fabriquer de nouvelles mains.

## Examen réellement effectué

Lecture d'AGENTS.md, du dessin canonique `references/MOU_reference.png`, de
`mou_rig.py` et du contrôleur V27, dont les images sont celles de V26.
Extraction et ouverture d'une planche de onze images décodées du vrai MP4 V27 :
33 ; 33,5 ; 34 ; 34,5 ; 35 ; 35,5 ; 36 ; 36,5 ; 37 ; 37,5 et 37,958 secondes.
Preuve privée : `work/critique_mains_v28/fin_reelle.png`.
Cet examen ne constitue pas une lecture continue ni un test auprès du public.
Aucune écoute de la bande-son n'a été effectuée.

## Cause observée

À 33–33,5 s, les mains sont encore proches du ventre, dans une organisation
semblable aux gestes usuels du modèle. À 34 s, la main gauche à l'écran est
déjà à hauteur des yeux ; à 34,5 s, le second bras décrit une grande courbe
latérale. Dès 35 s, les deux extrémités sont presque horizontales, de part et
d'autre de la tête. Cette attitude persiste jusqu'à la fin.

Le code confirme les grandes cibles de présentation : gauche `(150,950)` et
droite `(970,920)` en coordonnées monde, atteintes par deux arcs courts.
Le solveur oriente les bras natifs entiers pour rejoindre ces points. Or la
moufle fait partie du même ruban élargi que l'avant-bras : le grand pivot change
sa direction avec celle du bras. Les bouts arrondis se lisent alors comme des
prolongements horizontaux ou des palettes près des oreilles, tandis que les
longues courbes étroites redescendent aux attaches des épaules.

C'est un défaut de pose et de lisibilité : aucune main détachée, aucun doigt
supplémentaire ou troisième membre n'est visible dans les images examinées.
Le fait que le contour reste techniquement canonique ne suffit donc pas à
rendre cette attitude convaincante. La référence dessinée montre davantage
d'extrémités rondes près du ventre ou des hanches, avec une relation plus
courte et immédiatement lisible entre bras et moufle.

Effet probable sur le spectateur, à distinguer d'une mesure : l'œil peut lire
une extension étrange de la silhouette plutôt que « MOU présente ses mains
propres ». La grande levée détourne alors l'attention du contraste avec le
repas raté. Le problème persistant dans la pose finale, il ne relève pas
seulement de deux images extrêmes destinées à l'élasticité.

## Une correction prioritaire

**Présenter les deux moufles devant le torse et sous la bouche, avec un
écartement modéré, au lieu de les monter latéralement près des oreilles.**

Conserver la séquence de pensée : regarder la première main, la présenter
par un petit arc ; regarder la seconde, la présenter ; retrouver son sourire
puis regarder le public. Employer les contrôles natifs de pliage, hanches et
rotation, avec des cibles réellement atteignables par le même rig. Les coudes
restent dans une attitude basse ; le bout arrondi de chaque moufle doit se
lire séparément sans ajout d'un contour de paume ou d'une articulation.

La hauteur et l'écartement exacts doivent être choisis sur deux ou trois
poses rendues, pas imposés par des coordonnées approximatives hors de portée.
Les mains ne doivent couvrir ni la bouche ni la preuve du repas noir ; les
regards doivent suivre leurs nouvelles positions. La durée, le costume, les
cadrages utiles et l'intention de fausse victoire ne demandent pas de reprise.

## Vérification attendue

Comparer l'avant/après sur les images réellement encodées de 33,5 à 38 s,
en petit format, et examiner densément les deux petits arcs pour éviter un
nouveau pivot ou une accélération brusque. Vérifier deux bras continus, deux
moufles, extrémités rondes, prises et masques cohérents. Le présent rapport
n'affirme pas que cette correction est déjà fabriquée ou approuvée.

Le décalage sonore signalé par l'utilisatrice doit recevoir son propre contrôle
des débuts perceptibles des sons face aux mouvements ; cette revue visuelle
ne permet ni de l'écarter ni d'inventer un retard audio mesuré.
