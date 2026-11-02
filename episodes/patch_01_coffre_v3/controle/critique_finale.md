# Critique du montage — PATCH / reconstruction du jeu

2 novembre 2026, Africa/Casablanca. Revue indépendante des images réellement
produites pour la reconstruction inspirée de la référence utilisateur.
Les étapes examinées sont distinguées ci-dessous. Aucune audition réelle
n'est revendiquée.

## Revue des nouvelles poses

Deux planches de travail réellement rendues ont été ouvertes :
`work/rig/poses_jeu.png`, puis `work/rig/poses_integrees.png`. La première
présente les attitudes ; la seconde les place dans les plans et le décor.
Ces fichiers de travail ne sont pas les exports finaux.

- **Joue portée :** la paume reste de taille normale et touche la joue. Le
  coude dirigé vers le plateau donne une impression d'appui ; les paupières
  lourdes et la bouche descendante portent ensemble l'ennui.
- **Bras croisés :** les deux manches et les deux pattes sont identifiables
  sur le hoodie. La pose exprime une tentative de maîtriser son attente.
- **Menton bas :** la tête descend réellement vers le niveau du bureau ; les
  grands yeux restent visibles et le compteur n'est pas caché. Le changement
  de posture vers l'objet désiré est distinct de la seule pose d'impatience.
- **Joie :** le relèvement du corps et des pattes crée un contraste avec
  l'attente. La bouche trop mince de la première planche a été corrigée ;
  la planche intégrée montre un sourire ouvert propre.

Aucun trou de raccord bloquant n'a été observé sur ces poses fixes. Cela ne
prouve pas leur continuité en mouvement. Les transitions à contrôler sont
les entrées/sorties d'appui, le croisement, la descente et le retour au geste
d'ouverture, puis le suivi du téléphone pendant le rebond.

## Correction de cadrage demandée avant l'animatique

Sur la première planche intégrée, le sommet du rebond de joie sort les oreilles
du cadre et le carton `30 MIN LATER` recouvre une partie du front. Son effet
est concret : la réaction principale paraît coupée et son regard est moins
facile à suivre.

Correction retenue : remonter la caméra de ce plan et enlever ce carton
pendant le rebond. Le repère des trente minutes est déjà établi lors du
déverrouillage et revient au bilan final. Aucun geste ou texte supplémentaire
n'est nécessaire. Son application est vérifiée dans l'animatique ci-dessous.

## Animatique complète effectivement examinée

Fichier : `PATCH_Le_coffre_V3_animatique_muette.mp4`.

SHA-256 :
`b507f74ee51b56da4b135adda7ec39373904fef5fc7cc275066a8b4a33c247d9`.

Format sondé : 540 × 960, 24 images/s, 720 images, trente secondes, sans son.
Les 720 images ont été décodées en PNG. Soixante vues d'ensemble espacées
d'une demi-seconde et vingt vues rapprochées des transitions ont été ouvertes
en planches ; le sommet de la joie a aussi été ouvert plein cadre. Le fait de
décoder chaque image ne signifie pas que chacune a été observée séparément.

| Passage | Observation sur le montage rendu |
| --- | --- |
| Début et verrouillage | `FOCUS TIME`, liste, crayon et téléphone montrent le contexte de travail. Le téléphone est déposé dans le coffre avant sa fermeture. `30 MIN`, `30:00` et `MIN:SEC` rendent le délai identifiable. |
| Premières minutes | Les yeux et le crayon reviennent vers la feuille après les premiers regards. La troisième vérification aboutit au crayon posé et à la main libre. |
| 12,3–15,5 s | L'installation de la joue dans la patte est progressive ; la paume arrive au visage et les paupières s'alourdissent. L'appui reste lisible dans le décor. |
| 15,2–15,8 s | La patte quitte la joue puis les deux bras se croisent devant le hoodie. Les images intermédiaires ouvertes ne montrent pas de membre supplémentaire ni de manche détachée. |
| 18,15–18,83 s | Les bras se déplient, les paumes trouvent le bord et la tête descend ; les yeux s'ouvrent et restent orientés vers le coffre. L'envie succède visiblement à l'ennui contrarié. |
| 22,42–24,7 s | La pose basse se libère vers le geste d'ouverture. Le coffre reste fermé pendant `00:01`, puis le téléphone est réellement repris après zéro. |
| 24,7–26,65 s | La préparation basse, le redressement, le sommet bref et la retombée rendent la joie corporelle identifiable. Le téléphone reste porté par la paume dans les échantillons rapprochés. |
| 26,65–30 s | La même liste, sans coche, reçoit son insert lisible ; le retour montre PATCH satisfait devant son écran. Le travail resté intact donne la conséquence de l'attente. |

**Correction du cadre confirmée :** à 25,292 s, l'image complète montre les
deux oreilles entières et aucun carton sur le visage. Le sourire ouvert reste
propre. Le retrait du texte pendant le rebond ne supprime pas le repère des
trente minutes, établi à l'ouverture et repris dans le plan final.

Le changement de jeu se constate dans trois attitudes d'attente distinctes,
puis dans une joie portée par le corps. Le dessin de PATCH, la causalité de
l'enfermement et les cases vides sont conservés. Les erreurs de la référence
utilisateur n'ont pas été reprises dans les images examinées.

**Décision après animatique : passer au HD.** Aucun défaut visuel bloquant
n'a été observé sur les séquences et transitions inspectées. Cette revue
interne ne constitue pas une approbation du public ou de l'utilisatrice.

## Revue du véritable export HD

Les deux fichiers ont été sondés après le rendu final :

- `PATCH_Le_coffre_V3_muet.mp4`, SHA-256
  `06ee0d3032f19870143b70b9cf0c49e56ad98fcf5877df8dd2ac1218b266bcf4`.
- `PATCH_Le_coffre_V3.mp4`, SHA-256
  `ef4e807907f60182682d43bfb8e107ce8cc1fbdfa73487225981b38a4ce6b566`.

Chacun contient 720 images H264, 1080 × 1920, à 24 images/s, pour trente secondes.
Le second contient une piste AAC de trente secondes. Cette présence audio
ne constitue pas une audition.

Trente images ont été directement décodées du MP4 avec son, puis ouvertes
en trois planches : intention initiale, notification, dépôt et fermeture,
trente minutes, retours à la page, dépôt du crayon, appui joue, passage aux
bras croisés, descente près du coffre, dernière seconde, ouverture et reprise,
préparation de joie, sommet du rebond, amortissement, papier et pose finale.
Trois de ces images ont aussi été ouvertes en plein cadre : bras croisés
à 15,792 s, sommet à 25,292 s et insert de la liste à 27,208 s.

Les intentions et transitions observées dans l'animatique sont conservées.
Les pattes et manches restent identifiables sur les images rapprochées
examinées. Le téléphone est porté par la patte pendant la joie. Le sommet
garde les deux oreilles dans le cadre, avec les yeux et la bouche dégagés.
La liste finale affiche trois cases vides et aucune marque de travail.
Le retour à PATCH absorbé par le téléphone ferme le contraste du récit.

**Verdict final visuel : livrable pour cette reconstruction.** Aucun nouveau
défaut visuel bloquant n'a été observé sur les passages HD inspectés. La
référence fournie a conduit à des attitudes corporelles plus distinctes,
tout en conservant le choix d'enfermer le téléphone, les trente minutes et
la liste intacte qui rendent le gag compréhensible.

## Portée et limites

Cette revue examine des images extraites des véritables montages. Elle ne
prétend pas à une inspection individuelle de chaque image ou à une projection
auprès d'un public. Les contrôles numériques de contacts et masques
complètent cette lecture ; ils ne valent pas validation comique du public
ou de l'utilisatrice.

Aucune écoute réelle n'est revendiquée pour la référence, l'animatique ou le
HD avec son. La présence d'une piste audio ou un niveau sans saturation ne
prouve pas le confort d'écoute, le naturel des bruitages ou leur effet comique.
