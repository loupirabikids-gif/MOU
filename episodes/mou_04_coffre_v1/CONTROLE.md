# Contrôles — MOU dans Le coffre

Le changement porte sur le personnage et les ajustements nécessaires à ses
proportions. Les anciens films et le rig canonique MOU restent intacts.

## Identité et image

- Le corps, le visage et les pieds utilisent le rig MOU original, dont la
  copie incluse est identique à `mou_rig.py`. Silhouette vert citron à deux
  bosses arrondies, deux yeux, deux bras continus avec extrémités arrondies
  et deux petits pieds prune. Aucun raton recoloré, nez, oreille, queue ou vêtement.
- Les poses puis la vraie animatique sont examinées. L'œil rogné du gros
  plan, les crochets de moufle, les ovales verts du clignement et le petit
  triangle dans la transition de joie sont corrigés avant le rendu final.
- Les prises de téléphone et la pression du bouton sont contrôlées dans
  l'image réellement composée. La cible du bouton est adaptée au bout de
  moufle MOU ; un centre théorique de prise ne suffisait pas à prouver le contact.
- Le gros plan conserve les deux yeux. Le coffre est réaligné sur le
  plateau après changement d'échelle. Au début de son ouverture, le bras
  reste visible sur le panneau ; un clip limité à la façade protège le LCD.
  Cacher la main derrière toute la boîte avait supprimé le contact et a
  été écarté après revue de l'image.
- Le contrôle du LCD couvre toutes les images : sur les 612 où il est
  dessiné et visible, aucun pixel de membre ne recouvre son intérieur.
  Les pupilles des yeux ouverts, les semelles de la joie, les contacts
  visibles et l'unicité des identifiants SVG sont vérifiés séparément.

## Histoire, son et fichiers

La session reste de trente minutes dans un film de trente secondes.
Horloge et minuterie partagent le même temps ; la liste comporte toujours
trois cases vides. Le téléphone, les fenêtres narratives et la succession
des plans sont comparés à l'épisode précédent. Le placement du gros plan
est adapté au MOU plus large.

Le mix comporte 18 bruitages à gains fixes, sans voix synthétiques ou musique.
Son WAV est identique au Foley antérieur, sans échantillon écrêté ; les
rapports conservent la nouvelle chronologie. La présence de la bonne piste
audio dans le vrai MP4 est contrôlée, sans audition réelle revendiquée.

Les MP4 son et muet sont décodés, vérifiés en 1080 × 1920, 24 ips,
720 images / 30 s, avec le même flux vidéo. Des images HD décodées sont
comparées à des rendus frais. Le gel des entrées et les références historiques
sont vérifiés. CRC et manifeste SHA256 du ZIP sont contrôlés ; sa reproduction
isolée compare des PNG et le WAV, sans garantir l'identité binaire d'un
nouvel encodage MP4.

Voir [QA](controle/qa.json), [critique du vrai montage](controle/critique_finale.md),
[adaptation du modèle](developpement/adaptation_mou.md),
[placement et corrections](developpement/ajustements_placement.md) et
[mesures audio](audio/controls.json).

Les mesures techniques ne constituent pas une validation du comique ou du
succès public. La référence dessinée et le rig vectoriel ne sont pas identiques
pixel pour pixel. Aucun plan ou son de la vidéo privée de référence n'est livré.
