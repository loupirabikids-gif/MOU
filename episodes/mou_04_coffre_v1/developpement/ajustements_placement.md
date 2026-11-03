# Adaptation au coffre

Le corps et le visage MOU proviennent du rig original ; ses membres doivent
être dirigés vers les accessoires déjà animés. Les positions antérieures
du téléphone et du coffre ne sont pas une justification d'un contact raté.

Le gros plan `face_box` rognait l'œil gauche quand les anciennes coordonnées
de caméra étaient appliquées au MOU plus large. Son échelle devient 1,55,
sa translation −430 / −550. Le corps reçoit −25 unités supplémentaires vers
la gauche dans ce seul plan ; les cibles de paumes et le téléphone restent
sur leurs accessoires. Les deux yeux sont lisibles jusqu'à la coupe vers la joie.

La moufle native se termine près du repère de prise, alors que la paume de
Patchy dépassait davantage ce repère. Garder x690 laissait donc un espace
devant le bouton. Le gros plan réellement rendu a révélé ce défaut. La cible
de pression est avancée à x715 entre 3,88 et 4,02 s : l'extrémité arrondie
touche le bouton sans masquer le LCD. Le reste de la trajectoire contourne
le flanc comme auparavant ; l'accent de bouton reste à 3,9 s.

Les premiers essais avaient des crochets dus à la courbure distale des bras
et des ovales verts au clignement. L'adaptateur corrige ces passages en
gardant les contours continus et en terminant la fermeture des yeux par des
arcs. Les poses corrigées puis le vrai montage sont revus séparément.

Le changement d'échelle du gros plan imposait aussi de réaligner le coffre
sur le plateau : son ancien décalage vertical de −250 le laissait flotter.
Le nouveau décalage −63 donne un bas de façade à1657,75, pour un bureau à1658.
Le téléphone et la main gardent le même décalage que le coffre. Pendant
l'ouverture23–23,75s, bras et paume restent devant le panneau, mais un clip
limité à la façade les empêche de couvrir l'affichage. Les cacher derrière
panneau et façade aurait supprimé le contact visible : cette solution
provisoire a été écartée après revue réelle.

Le vrai montage a aussi révélé un petit triangle dans la moufle gauche libre
avant la prise à deux mains (24,75–24,92s). Le contrôle de tangente distale
est corrigé sur sept images ; les cibles de mains et de téléphone restent
fixes. Treize images composées et trois détails ont été revus avant rendu.

Enfin, le déport horizontal du corps hérité du raton plaçait l'épaule MOU
sous le couvercle. Même une main visible pouvait alors sembler partir du
panneau. Dans le seul plan `face_box`, le lean horizontal du corps est annulé,
sans déplacer les paumes ni le téléphone. Le bras part désormais de la
silhouette à gauche et rejoint sa cible sur le couvercle. Les deux yeux
restent entiers pendant ce changement de placement.
