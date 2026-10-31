# Contrôles du premier galet

31 octobre 2026. Prototype muet de **5 secondes**, 1080 × 1920, 24 images/s,
120 images. Nom et apparence encore proposés, pas de validation artistique
de l'utilisatrice déduite du choix du concept.

## Revues du dessin et de l'animation

Six poses ont été rendues avant le film. Les premières moufles semblaient collées
aux flancs ; elles ont été éloignées, et l'action de prise écartée de l'œil.
Le constat a reçu une surprise plus nette, puis un sourire final moins assuré
que celui du départ.

Le premier MP4 réduit a révélé un autre défaut : la main passait devant les yeux
au retrait. L'approche et le retour passent désormais sous le visage, par le bas
du corps. Le critique a ouvert de nouvelles séries consécutives du vrai MP4 à
270 px de large ; sa réserve a été levée. Une dernière revue de six images HD
décodées n'a identifié aucune nouvelle réserve sur les passages examinés.

Les critiques avant, pendant et après sont conservées dans `developpement/`
et `controle/`. Examen d'images successives, pas une lecture continue ni un
test public de reconnaissance des émotions.

## QA indépendante passée

- 120 SVG : deux yeux/pupilles masquées, deux moufles flottantes, deux pieds,
  une miette, aucun bras ; identifiants et références SVG contrôlés.
- Neuf contacts mesurés sur les silhouettes réellement émises. La miette reste
  liée à sa porteuse ; les deux moufles la touchent avant le transfert. Pas de
  saut géométrique au changement de main à 1,60 s.
- Quatorze images du vrai MP4 comparées à CairoSVG frais : erreur RGB moyenne
  maximale 1,506/255 pour l'image entière et 2,864/255 sur mains/miette.
- Aucun débordement de pupille ni masquage des yeux aux repères contrôlés.
- Échelle des moufles constante, pieds fixes et douze dernières poses identiques.
- Sources gelées, ancien rig MOU et film V28 protégés sans modification.

Détails : `controle/QA.json` et `controle/QA.md`. Le contrôle complet de protection
des anciens fichiers MOU s'exécute dans le dépôt complet ; ces anciens médias
ne sont pas recopiés dans le petit ZIP du nouveau personnage.

Le film est volontairement muet : aucune bande-son ou identité vocale n'est
évaluée. Ces contrôles ne prouvent ni qualité professionnelle ni succès de chaîne.
L'essai doit être jugé sur son dessin, son geste et sa réaction par l'utilisatrice.

## Sources

SVG et Python originaux ; CairoSVG, Pillow et FFmpeg pour les rendus et l'export.
Seule la police DejaVu sert aux légendes de la planche ; sa licence est incluse.
L'archive contient les producteurs, la palette, les six poses SVG et les bilans,
avec manifeste SHA256. Elle n'exige aucun service ou ancien rig pour refaire
le dessin et la vidéo. Le contrôle séparé de son extraction est dans
`controle/audit_archive.json` lorsqu'il a été effectué.
