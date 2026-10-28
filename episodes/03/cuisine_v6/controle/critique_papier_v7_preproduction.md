# Critique ciblée — dernier morceau de papier, avant correction V7

28 octobre 2026. Périmètre : lisibilité du dernier morceau seulement.
Le tablier, les bras, les mains, le débit d’eau, les sons et les 30 secondes
du montage restent ceux de la version cuisine approuvée pour retour.

## Observation réelle

Une image du MP4 livré au commit
`0e188a34a94613d094f2bd87bd9dd9ddf3d59456` a été décodée à 26,5 s puis ouverte
en résolution native. Elle est conservée dans
`critique_papier_v7_images/avant_26_5.png`.

Le dernier papier est visible, mais il n’occupe qu’environ 35 × 54 pixels
dans l’image 1080 × 1920 : les dimensions source sont 26 × 40 unités, avec
un zoom voisin de 1,36. À 432 pixels de large, cela représente environ
14 × 22 pixels. Sa petite silhouette verticale peut se perdre entre les
grandes moufles. Ce constat correspond au retour de l’utilisatrice ; il ne
nécessite pas de modifier le geste, le cadrage ou le récit.

## Correction recommandée

Porter le morceau à **64 × 88 unités** autour du même point de prise.
Avec le même cadrage, il occupera environ 87 × 120 pixels dans l’export et
35 × 48 pixels dans un aperçu de 432 pixels de large. Ce reste demeure
nettement plus petit que les longues bandes gaspillées, mais sa fonction
de papier tenu et frotté devient plus facile à reconnaître.

Porter sa boulette à **r = 22**, dans la main, pendant le vol puis dans la
poubelle. Les trois anciennes boulettes restent à 47, 53 et 59. Le dernier
déchet reste le plus petit et conserve la même identité au raccord.

Le froissage doit partir du nouveau morceau et converger vers r22 ; ne pas
laisser la branche des petites feuilles dépendre de `r < 15`, qui deviendrait
fausse avec cette correction. La condition explicite `cycle == 4` préserve
la bonne branche sans toucher les autres papiers. Garder les mêmes mains,
ancrages et trajectoires ; vérifier que le contour dépasse clairement de la
prise sans être lu comme un morceau flottant devant les mains.

**Avis favorable à cette correction ciblée avant fabrication.** Il s’agit
d’une recommandation fondée sur l’image actuelle et les dimensions prévues,
pas d’un avis sur les nouvelles images, qui restent à examiner.

Les deux références YouTube sont suivies séparément par le veilleur. Aucun
contenu de ces vidéos ni aucune écoute n’est déduit de leur seul lien.
