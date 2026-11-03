# Recasting du coffre — critique avant fabrication

Demande courante : remplacer Patchy par le MOU original dans l'épisode du
coffre. La version PATCH V7 sert au récit, aux cadrages et aux contacts ;
elle n'est pas une référence de dessin du personnage à conserver.

La planche `references/MOU_reference.png` a été effectivement ouverte et
le code `mou_rig.py` lu. MOU est vert citron, asymétrique, avec une petite
double bosse, deux grands yeux blancs, des sourcils/pupilles prune, deux
bras terminés par deux moufles et deux petits pieds sombres. Il n'a ni nez,
ni oreilles, ni queue. Le costume de cuisine ne correspond pas à cet épisode.

## Histoire à préserver

MOU enferme son téléphone pour travailler trente minutes. L'attente l'occupe
plus que sa feuille. Il récupère le téléphone avec joie ; les trois cases
vides montrent qu'il n'a rien accompli, puis son écran l'absorbe de nouveau.
La transformation du personnage ne doit pas changer cette petite histoire,
la progression du temps ou supprimer le dernier contraste visuel.

## Risques concrets du transfert

| Portion | Risque lié au nouveau modèle | Vérification demandée |
| --- | --- | --- |
| Début et retour au travail | Des coordonnées pensées pour la tête d'un raton peuvent mettre les yeux de MOU trop bas ou le corps derrière le bureau | Examiner le vrai cadre, pas seulement la matrice ou la couleur |
| Dépôt et reprise du téléphone | Les bouts des bras natifs et les prises héritées peuvent se dédoubler, se couper au poignet ou rester derrière l'objet | Une seule moufle par bras, contour continu et contact lisible ; façade devant les parties réellement entrées |
| 3,20–4,65 s | Le nouveau point d'épaule peut faire traverser le flanc à la même trajectoire de bouton | Revoir les images consécutives : trajet extérieur, raccord visible, LCD entier, contact du bouton préservé |
| Appui de joue vers 13,5 s | La joue de MOU n'est pas au même endroit que celle de Patchy | La moufle doit réellement porter la joue, sans passer dans la bouche ou l'œil |
| Attente basse vers 19–21 s | Le visage du blob peut être caché par le coffre ou la table | Deux yeux dégagés, regard vers le coffre, main/bras séparés du volume solide |
| Joie vers 25 s | Une simple translation peut montrer des jambes héritées ou cacher les petits pieds natifs | Deux pieds prune de MOU, même corps vert, téléphone réellement tenu par les moufles |
| Fin | Le dessin peut encore contenir une queue, une manche, un museau ou un masque de raton sous les nouvelles formes | Inspecter la scène et la source SVG ; pas de raton recoloré |

Les contacts sur le couvercle et le bouton sont voulus : un recouvrement
plausible de la paume sur un bord n'est pas automatiquement un défaut. En
revanche une manche qui disparaît dans un flanc puis rejoint une paume
peinte devant le LCD reste un problème réel, même si les centres sont exacts.

Le modèle articulé natif est la base, avec adaptation des prises nécessaires.
Les expressions et pupilles doivent porter la situation sans dialogue.
Le son retenu pour cette reprise est celui des dix-huit bruitages, sans la
banque vocale synthétique rejetée. Aucune audition n'est revendiquée.

## État de la revue

Cette prerevue ne valide pas une image encore non produite. Il faut ouvrir
les poses composées, puis décoder la vraie animatique avant le HD. Les
corrections retenues et le film effectivement livré seront consignés dans
`controle/critique_finale.md`.
