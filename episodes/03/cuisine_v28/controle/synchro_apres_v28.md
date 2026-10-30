# Vérification des deux accents visuels — animatique V28

30 octobre 2026. Fichier réellement examiné :
`MOU_Encore_une_feuille_animatique.mp4`, 38 s, 540 × 960, 24 images/s,
912 images, avec piste audio. SHA256 :
`d53cb9b141d9a4e437d8f831e8edde0c0aa70755276b34f242da8f0e6e240526`.

## Examen et portée

Vingt-deux images du MP4 V28 ont été décodées, mises en comparaison avec
les mêmes images du MP4 V27 et réellement ouvertes : huit autour de
l'inspiration, dix autour de l'expiration, quatre autour du choc.
Preuves privées dans `work/synchro_v28/` :
`inspiration_avant_apres.png`, `expiration_avant_apres.png`,
`choc_avant_apres.png` et `verification_after.json`.

Les paramètres de bouche évalués sur la même grille complètent cet examen ;
ils ne remplacent pas les images encodées. Les repères d'énergie vocale
proviennent de l'audit précédent, le WAV étant conservé selon le contrat de
révision. Ce rapport est une vérification visuelle ciblée, pas une nouvelle
vérification complète PCM/AAC, une écoute ou une lecture continue.

## Inspiration : réserve levée

Dans V27, la bouche se refermait pendant le son : ouverture 0,333 à 25,667 s,
puis 0,201 à 25,792 s. Dans le vrai MP4 V28, l'ouverture en O reste clairement
exposée entre 25,667 et 25,875 s et se referme ensuite. Les comparaisons à
25,708 /25,750 /25,792 /25,833 s montrent le maintien de cette forme, et
l'image 25,917 s retrouve l'ouverture plus faible de la transition suivante.

Le maximum d'énergie précédemment mesuré à 25,766771 s tombe donc dans la
pose ouverte. Il est à 0,40 image du repère 25,750 s, au sein du plateau ;
il ne coïncide plus avec une fermeture. L'attention va toujours à la fumée,
puis retourne à la décision de sécher. Aucun déplacement global de la
bande-son ni nouvelle reprise narrative n'est nécessaire sur ce point.

## Expiration : réserve levée

Dans V27, la bouche restait fermée et l'acteur figé sur le souffle. Le MP4
V28 montre maintenant une petite ouverture à 32,792 s, une petite bouche O
à 32,833 s, puis un retour progressif à la bouche retombée, terminé avant
33,083 s. La modification est discrète et reste liée à la déception ; elle
n'anticipe pas la fierté ni la présentation des mains.

Le maximum vocal mesuré à 32,809271 s se situe entre les deux images où
l'ouverture se forme, à 0,58 image du maximum visuel 32,833 s. Cet indice de
souffle rend visible l'accent qui manquait. Aucune augmentation de mouvement
corporel, de volume sonore ou de durée n'est demandée après cette correction.

## Choc préservé

Les paires réellement ouvertes à 31,750 /31,833 /31,875 /31,958 s conservent
l'ouverture de bouche et l'extrême corporel de V27. Le maximum vocal 31,865 s
reste dans l'extrême exposé 31,833–31,958 s. L'animation n'a pas été déplacée
pour corriger un décalage global qui n'était pas établi.

## Avis

Les deux réserves locales de couplage relevées dans l'audit précédent sont
levées sur les images du nouveau MP4. Avis favorable au rendu HD pour ces
corrections ; pas de nouvelle reprise demandée. La critique des mains et
les contrôles de l'export final restent des vérifications distinctes.
Aucune écoute, reconnaissance d'émotion par un public ou validation du
naturel de la voix n'est revendiquée.
