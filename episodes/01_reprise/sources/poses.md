# Jeu courant — Le retardateur, révision3

Source commune : `../chronologie.json`, 13s à24i/s, clic et flash image144
à6s. Le modèle original `../../../mou_rig.py` reste inchangé : deux yeux,
deux bras àune main chacun, deux petits pieds. Cette révision corrige
la capture et la réaction finale selon la demande de l’utilisatrice.

## Intentions et temps

- 0–5,75s : jeu précédent strictement conservé. Activation du téléphone,
  séduction, clin d’œil de vanité, beau sourire ; au1 il souffle et abandonne
  sa pose trop tôt. Les139SVG aux temps images0à138 sont identiques.
- 5,75–6s : même chute accélérée du corps, sans rebond et avec pieds fixes.
  Le visage aboutit àun œil grand ouvert et l’autre légèrement baissé,
  deux pupilles rapprochées vers le centre, sourire mince oblique et crispé.
  La déformation extrême n’est atteinte qu’au clic.
- 6–6,208s : arrêt sur la pose exacte de la capture. Le flash se dissipe
  sans changer l’expression. La photo emploie strictement `character_at(pose_at(6))`.
- 6,208–6,75s : le corps se replace, tout en gardant les mêmes paramètres
  du visage. Il ne passe plus par une surprise enO ni une langue pendante.
- 6,75–8s : photo figée pendant1,25s. La pose vivante est hors champ.
- 8–8,5s : les pupilles descendent ensemble vers le résultat, tout en
  conservant leur convergence horizontale. Lecture du résultat jusqu’à9,25s.
- 9,25–10,25s : le regard remonte vers le spectateur ; MOU louche toujours.
- 10,25–11,5s : il essaie de sauver les apparences, sourire légèrement
  plus tendu et sourcils gênés. Aucun geste des bras n’est ajouté.
- À277/24s et287/24s : deux minuscules contractions de0,25s, synchrones
  des deux «hé» soufflés. La bouche s’entrouvre très peu sans effacer le
  sourire ; les yeux restent ouverts et continuent de loucher.
- 12,5–13s : pose finale strictement immobile. Le mix garde le silence.

## Paramètres et construction

APIs conservées : `pose_at`, `character_at`, `motion_at`, `deformation_at`,
`intention_at`. Les nouveaux paramètres d’expression sont àzéro avant5,75s :

- `cross` : de0à1, décalage indépendant et opposé des pupilles. À1,
  la pupille gauche est à+15unités de son centre et la droite à−15.
- `nervous` : adaptation locale de la bouche vers un sourire mince et
  décentré, sans nouvelle anatomie ni dents ajoutées.
- `lip_tension` : resserrement discret de la courbe du sourire final.
- `he_open` : minuscule ouverture ponctuelle pendant les deux sons.

`mou_rig._eye` reste l’unique dessin des yeux : même ovale, même pupille,
mêmes paupières et même masque. Seul `pupil_x` est différent pour chaque œil,
via une copie locale des paramètres. Àla capture et dans la pose finale,
`eye_open_l=1`, `eye_open_r=0.65`, `cross=1`, `nervous=1`.

Les bras sont exactement ceux de `mou_rig.character_fragment` / `_arm`,
sans adaptateur de forme, raccourcissement ni masque de racine. Les valeurs
`arm_hips` et `arm_clasp` du montage précédent sont conservées pour toute
la durée. Les deux mains restent l’extrémité de leurs bras d’origine.

L’affine commune transforme corps, bras et visage ensemble ; les pieds
restent àl’extérieur et gardent leur géométrie. La capture descend à0,68
avec largeur1,12 et cisaillement−0,07, comme avant cette correction.
Les deux contractions du rire ne changent `warp_sy` que de0,006 au maximum,
en un seul lobe par syllabe, sans déplacer les pieds. `motion_at` reste
identité. Aucun mouvement n’est ajouté après12,5s.

## Vérification préparatoire

`../controle/audit_fin_scope.json` contrôle les312poses :
bras canoniques, exactement deux mains, SVG et anciens paramètres identiques
jusqu’à5,75s inclus, maintien de la capture et pose finale immobile.
`../controle/fin_jeu.png` montre les étapes du visage.
La critique du montage réellement encodé et les audits de livraison sont
conservés séparément dans `../controle/` par la coordination.

Les descriptions des révisions1et2 et du rétablissement antérieur des bras
restent dans l’historique Git et les rapports de contrôle de ces révisions.
Leurs anciennes surprises enO et fins aux yeux baissés ne sont plus le jeu
courant demandé par l’utilisatrice.

## Correction après examen du premier montage de cette fin

Le coordinateur et le critique ont observé un sourire encore trop doux,
enU, dans le vrai montage léger. Seule la forme locale `tense` de la bouche
et sa petite commissure ont été corrigées : gauche presque plate, sourire
étiré, coin droit pincé et relevé. Le pincement s’accentue entre10,25et11,5s.
Les312dictionnaires de pose et tous les SVG hors du groupe `mouth` restent
identiques aupremier montage ; les139SVG initiaux restent identiques enentier.
Comparaison : `../controle/fin_sourire_avant_apres.png` ; preuve
ciblée : `../controle/audit_fin_sourire_correction.json`.
