# Bilan du prototype Blender

Le prototype conserve le MOU original et le petit gag de l'étude du grain.
Son objectif est de disposer d'un personnage réellement retouchable dans
Blender, avec une comparaison à dessin et scénario constants.

**Technique vérifiée.** La scène a été ouverte dans un nouveau processus
Blender, sans handler de lecture. Les courbes et leurs clés sont éditables.
Modifier un poids déplace ensemble le dessin du bras, l'ancre et la prise de
cuillère ; retoucher un point modifie réellement le personnage évalué.
Les quatre images intégrées sont les trois plates fixes et le lettrage.
Les 22 fichiers de référence, dont les deux anciens films, restent inchangés.

Le MP4 contient 120 images, 5 secondes à 24 images/s, 1080 × 1920, sans piste
audio. Cinq images décodées correspondent aux vrais rendus HD Blender.
Les [19 contrôles indépendants](controle/QA.md) sont passés.

**Reproduction vérifiée.** L'archive a été extraite dans un dossier séparé.
La régénération Python/SVG a reproduit les 61 ressources comparées avec des
empreintes identiques. Voir [le rapport](controle/reproduction.json).

**Revue visuelle.** Les trois poses Blender ont été examinées avant le rendu
complet, puis six images intermédiaires et les images décodées du montage.
Le détail des intentions et des limites du jeu se trouve dans la
[critique des poses](developpement/critique_poses.md) et la
[critique du montage](controle/critique_finale.md).

La résolution géométrique des clips corrige les défauts des anciens imports
SVG : yeux et bouche ne dépendent plus de masques ignorés par l'importeur.
Les ancres utilisent les mêmes poids que les courbes, pour rester liées aux
mains lorsqu'une pose est corrigée. Aucun redessin des bras n'a été appliqué.

La première revue du MP4 a fait corriger des défauts entre les poses fixes :
pointes de bouche à77, raccord du bras à92–98 et trou de paume à114. Les
contours natifs de ces transitions sont désormais des états explicites.
Vingt comparaisons locales vérifient leur correction ; ce contrôle rejette
les défauts de l'ancien export. Les transparences d'eau utilisent un mélange
plat pour supprimer la trame de pixels observée dans le premier rendu.

Ce rig de poses 2D ne comporte pas encore d'IK. Le fonctionnement de l'outil
ne constitue pas une validation du jeu comique par l'utilisatrice. Le film
est volontairement muet ; aucun contrôle d'écoute n'est revendiqué.

Empreintes des livrables principaux :

```text
MOU_blender_v1.blend
24f2cf8f0c18ab8df817704a3a403272f8b83e00efa65ea8b0e04922385f6378
MOU_Blender_5s_muet.mp4
2e29234ec7852c7fadf7e942c41da732357dc4ab1fb38f318bdfe437d22ecf48
```
