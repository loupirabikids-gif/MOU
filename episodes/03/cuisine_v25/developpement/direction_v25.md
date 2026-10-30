# Jeu coordonné du visage et du corps — V25

30 octobre 2026, Africa/Casablanca. L'utilisatrice demande une musique douce
et un vrai travail des expressions, de l'animation et des mouvements.
La priorité sonore seule des précédentes études ne limite plus cette reprise.

La durée reste43s et les contacts de cuisine, les cinq rituels et la chute
du papier conservent leurs instants. Les poses sont choisies pour montrer
une pensée, avec un regard vers sa cause, un mouvement bref et un arrêt.

## Actions et intentions

| Passage | Jeu visible | Construction et pause |
| --- | --- | --- |
| 0–6,6s, remuer | MOU est absorbé par le plat ; une seule inclinaison vers la poêle accompagne son plaisir. La moufle libre s'ouvre légèrement puis revient. | Les trois notes sifflées initiales sont conservées. Après1,85s, inclination jusqu'à−1,7° à2,35s, tenue jusqu'à3,8s, retour à4,55s. L'ancien déplacement périodique de tout le personnage est retiré. |
| 7–7,75s, première inspection | La main attire d'abord les yeux. Le buste se retire, la main se présente un peu plus haut, les yeux s'ouvrent et la bouche se crispe. | Quatre images de regard avant la réaction ; recul+2,8° atteint vers7,375s et exposé avant les yeux vers le lavabo. Les deux mains sont libres après la cuillère posée. |
| Premier essuyage puis retour | Le lavage reste concentré ; l'apaisement vient seulement après la fin effective du séchage. | Visage et inclinaison−1,25° à partir de12,25s ; une pose lisible après12,4s, puis retour au geste. |
| Carotte, tomate, sel et répétitions | L'attention et la bouche serrée progressent vers l'impatience. L'asymétrie des sourcils et l'ouverture des yeux remplacent la même longue mine triste. | Les inspections ont priorité sur les anciennes branches carotte/sel qui masquaient leur réaction. Inclinaisons choisies+1,5° et+1,8° aux inspections3 et4 ; aucune gesticulation à chaque cycle. |
| 31,1–32,25s, quatrième essuyage | MOU veut reprendre la cuisine : le corps se penche vers la poêle, les yeux vont vers elle puis reviennent au papier. Une petite bouche serrée et des sourcils plus tendus portent cette attitude. | Inclinaison−3,3° atteinte à31,35s, tenue jusqu'à32s, retour avant32,25s. Regard poêle31,3–31,5s puis papier31,65s ; visage comprimé formé et relâché en0,22s. Aucun changement de prise ou boucle de gestes. |
| 35,35–38,1s, petit morceau | Assurance avant le tirage, puis vraie surprise après le petit papier visible ; application déterminée au séchage. | Surprise après le regard, boucheO modérée, puis bouche serrée et yeux aux moufles. Pas de contrariété permanente pendant toute la dernière action. |
| 38,1–40,25s | Après le séchage achevé, MOU croit avoir réglé le problème ; il regarde sa moufle et se détend. Le spectateur voit la boulette tomber avant lui. | Soulagement à partir de38,1s, petite inclinaison−1,3°. Trajectoire, contact du tas39,1s et sol39,85s conservés. |
| 40,25–41,333s | Encore soulagé au premier instant, MOU regarde ensuite les déchets ; le corps se bloque et recule avec les yeux grands ouverts et une boucheO. | Images locales0–2 : main propre ;3–7 : yeux au sol ;8–14 : recul vers la droite, loin des déchets à gauche, jusqu'à+3,7°. Découverte exposée jusqu'à la coupe. |
| 41,333–43s | La coupe montre la même pensée ; les yeux rejoignent le public avant la bouche qui se referme. La réaction devient préoccupée, prise sur le fait. | Cible basse au début de la coupe, regard frontal atteint à l'image34 ; fermeture de réaction à partir de36. Corps et mains se posent vers49, puis quinze dernières images strictement tenues. Aucun sourire final. |

## Modèle et mouvements

Le personnage, la forme du corps, les deux bras/moufles et les pieds restent
ceux du rig canonique. Aucun membre n'est redessiné, étiré ou ajouté.
Les fonctions natives des bras et du raccord gauche sont inchangées.

`performance.py` produit une rotation rigide du haut du personnage autour
du point natif(205,420). Le rendu applique cette même rotation au corps,
au visage, à la toque, au tablier et aux deux bras. Les deux fragments
natifs des pieds sont extraits du torse et rendus hors de cette rotation,
au même sol. Le recouvrement natif des jambes par le corps est conservé.

Les gestes libres se limitent à la droite pendant le plaisir de cuisiner,
à la présentation de la main lors de la première inspection et à la petite
ouverture des mains lors de la découverte finale. Des mains sans objet
suivent aussi le buste aux inspections choisies. Les autres mains gardent
leurs cibles mondes : le contrôleur inverse la rotation du corps, puis
emploie seulement les contrôles natifs hips/clasp/rotation pour retrouver
la prise. Une demande hors de portée réduit l'inclinaison, sans agrandir
un bras. Le solveur tient compte du faible minimum de rayon du bras presque
droit utilisé pour remuer et conserve la profondeur de prise d'origine.

Pendant l'ouverture, retirer le balancement périodique implique de rebaser
ensemble le corps, les mains et la cuillère : le chemin natif approuvé de
remuage est restauré par rapport à la poêle fixe. Aucun glissement volontaire
d'un ustensile dans la moufle n'est ajouté. Les inserts lavabo sont inchangés.

Le regard subit l'inverse de la rotation corporelle, puis l'inverse de la
rotation faciale, avant le calcul des pupilles. Les directions génériques
de la bibliothèque ne remplacent pas la vraie cible du plan. Les surcharges
de visage sont exposées dans `expression.performance_face_overrides`.

## Examen préparatoire et gel

Douze poses ont été rendues par CairoSVG avec le renderer courant, puis la
planche a été réellement ouverte : `work/acting_v25/planche_jeu_v25.png`.
Elle montre notamment le contraste soulagement38,29/40,25s, découverte et
recul40,83/41,33s, puis réaction finale sans sourire. Le cadre visage élargi
par le coordinateur laisse le nom de la toque lisible pendant le recul.
Ces images ne constituent pas une lecture continue à vitesse réelle.

Contrôles préparatoires sur1032états : erreur maximale des mains contraintes
2,1×10⁻⁹px ; prise cuillère/couteau2,5×10⁻¹⁰px. Une comparaison isolée avec
V24 des105images de séchage donne des mains strictement identiques,
erreur0px : les placements des frottements audio restent utilisables.
Les quinze derniers SVG sont identiques. Angles réellement atteints :
−1,7° à+3,7°. Les preuves privées sont dans `work/acting_v25/check.json`.

Après examen du premier MP4 complet, le critique a trouvé la fin plus claire
mais le quatrième essuyage encore trop frontal et proche du troisième.
Une seule correction a été retenue : l'attitude de31,1 à32,25s décrite dans
le tableau. Les huit poses de `work/acting_v25/wipe4/planche.png` ont été
réellement rendues et ouvertes ; elles montrent le regard vers la poêle,
le retour au papier et l'inclinaison tenue. La nouvelle amplitude minimale
est−3,3°. Les prises restent inchangées (écart de solve inférieur à3×10⁻⁹px,
coordonnées mondes canoniques conservées pour le papier). Ce contrôle de
poses précède la nouvelle critique du passage dans le vrai MP4 exporté.

La critique indépendante examine ensuite l'animatique complète réellement
exportée. Les chiffres de géométrie ne prouvent pas le naturel, les émotions
reconnues ou le succès comique. Aucune écoute par cet agent n'est revendiquée.

### Sources gelées

- `animation.py` : `32e61db35f9bc04edea631213552939108897bffa7b759f1347f5d756a305e09`
- `jeu_visage.py` : `2725f1dc7e4be5eb8bea7565b03b2cd23c723a4019ccfb3270b8d47f3970ef07`
- `performance.py` : `6a3e64adfce3445ed9acd78721c5dda813325d9f7ef7865ab4156971855c281b`
- `acting.py` : `cb6ccd1d7f759a6ef8758ba54fae63f02557d30c701de2b12b5cc7b4cf3c9d5f`
- `poses.json` : `ba81b9a395f650f4d21e51e2052af39933ff19dba69402d2f8aea48f42170db7`
