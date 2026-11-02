# MOU original — prototype Blender 2D

Trois poses et un essai **muet de 5 secondes**, 1080 × 1920, 24 images/s.
MOU veut continuer à cuisiner malgré un seul grain sur sa moufle. Il reprend
la cuillère, s'arrête, puis cède et va le laver. Ce petit gag reprend l'étude
SVG précédente pour comparer le passage à Blender.

- [Voir la vidéo](MOU_Blender_5s_muet.mp4?raw=true)
- [Trois poses](MOU_Blender_trois_poses.png?raw=true)
- [Ouvrir la scène Blender](MOU_blender_v1.blend?raw=true)
- [Sources complètes ZIP](MOU_Blender_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

Le personnage contient de vraies courbes remplies, des clés de forme et des
poids de poses animés. Les masques des yeux et de la bouche sont résolus dans
la géométrie. Le décor fixe et le lettrage « MOU » de la toque sont des images
emballées dans la scène. Le personnage n'est pas une vidéo sur un plan.

## Retoucher le jeu dans Blender

Ouvrir `MOU_blender_v1.blend` dans Blender 4.3.2. Espace lance les cinq secondes.
La scène s'ouvre sur MOU et le contrôleur `CONTROLES_pose`.

Les repères d'assurance, de résistance et de décision sont aux images **12,
54 et 99**. Les marqueurs `ACTION_…` indiquent les gestes et les pauses.
`CONTROLES_pose` expose les poids communs : `Pose_012_assurance`,
`Pose_054_resistance`, `Pose_099_cede`, ainsi que les étapes intermédiaires.
Modifier une valeur puis insérer une clé pour changer l'animation. Pour
mélanger librement les poses, désactiver d'abord leurs courbes d'animation.

Pour corriger un sourcil, une pupille ou une moufle : sélectionner sa courbe
dans la collection correspondante, choisir la clé de forme de l'étape, passer
en mode Édition et déplacer ses points. Voir [le guide détaillé](developpement/rig_blender.md).
Les ancres de mains suivent les mêmes poids ; la cuillère suit sa prise.

Ce premier rig permet de corriger les dessins et les poses. Il ne comporte
pas encore de squelette IK qui reconstruirait automatiquement le bras en
déplaçant seulement la main. Le passage à Blender ne valide pas, à lui seul,
le jeu comique ; [la critique](controle/critique_finale.md) précise la lecture
du montage produit.

## Reconstruire et rendre

Depuis ce dossier, avec **Blender 4.3.2** et **FFmpeg** installés :

```sh
blender -b --factory-startup --threads 4 --python-exit-code 1 \
  --python sources/build_blender.py -- --build
blender -b MOU_blender_v1.blend --threads 4 --python-exit-code 1 \
  --python sources/finish_scene.py
blender -b MOU_blender_v1.blend --threads 4 --python-exit-code 1 \
  --python sources/render_frames.py -- --width 1080 --samples 8 --output work/hd
ffmpeg -y -framerate 24 -start_number 1 -i work/hd/%04d.png \
  -frames:v 120 -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -an -movflags +faststart MOU_Blender_5s_muet.mp4
```

La reconstruction Blender utilise le JSON vectoriel et les plates déjà
fournis ; aucun module Python supplémentaire ni compte en ligne n'est requis.
Pour régénérer ces ressources depuis le rig SVG original, extraire toute
l'archive en conservant ses dossiers, installer les dépendances Python du
projet ainsi que `sources/requirements-vector.txt`, puis lancer
`python sources/prepare_assets.py --vectorize --skip-film-check`.
Cette option omet uniquement les deux anciens MP4, exclus de l'archive ;
les empreintes de leurs producteurs Python restent contrôlées. Dans un clone
complet du dépôt, omettre l'option pour contrôler aussi les anciens films.

Blender rend les 120 images à partir de ses courbes et clés natives ; FFmpeg
les encode. Les rendus de travail restent dans `work/`, hors Git.
Les producteurs SVG antérieurs nécessaires sont inclus dans le ZIP.

Pour relancer les contrôles complets depuis un clone du dépôt, préparer les
références avec `python controle/qa_blender.py --prepare-references`, puis :

```sh
blender -b MOU_blender_v1.blend --threads 2 --python-exit-code 1 \
  --python controle/qa_blender.py -- --video MOU_Blender_5s_muet.mp4
```

Ce contrôle vérifie aussi les anciens films conservés dans le dépôt, qui ne
sont pas inclus dans le ZIP des sources.

## Ce qui vient de doodle-anim

La référence technique est [feitangyuan/doodle-anim](https://github.com/feitangyuan/doodle-anim).
L'idée retenue est une liste d'actions nommées avec des attentes explicites,
exposée dans `sources/beats.py` et sur la timeline Blender. Les dessins,
personnages et gags du dépôt ne sont pas réutilisés. Voir les [crédits](licences/CREDITS.md).
