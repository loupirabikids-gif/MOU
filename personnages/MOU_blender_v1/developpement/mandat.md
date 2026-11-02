# Prototype Blender — MOU original

Le 2 novembre 2026, l'utilisatrice autorise trois poses et un essai muet de
cinq secondes dans Blender, avec les techniques utiles de doodle-anim.
Le dessin citron, deux yeux, deux bras continus, les moufles et le costume
doivent rester reconnaissables. Les fichiers existants sont préservés.

Le personnage est reconstruit en courbes 2D éditables à partir de son rig
actuel. Les masques SVG des yeux et de la bouche deviennent de vrais contours
clippés. Les poids de poses pilotent des clés de forme Blender ; les décors
fixes et le lettrage restent des images. Ce n'est pas un film ou une suite
d'images de MOU placée dans la scène.

Le même petit gag sert de comparaison : MOU veut cuisiner malgré un grain
sur sa moufle, reprend la cuillère, s'arrête, puis va le laver. Les actions,
attentes et regards précèdent les mouvements suivants. Le plan d'action est
déclaré dans beats.py et repéré sur la timeline Blender.

L'inspiration de doodle-anim porte sur les actions nommées, les attentes et
l'accès à un temps précis. Ses personnages, ses dessins et ses gags ne sont
pas copiés. Aucune bulle d'émotion ni voix n'est ajoutée à cet essai.

Le transfert ne constitue pas une amélioration comique démontrée. Trois
images Blender réelles seront jugées avant le rendu complet ; puis le vrai
MP4 sera examiné. Le livrable doit permettre une édition dans Blender et
une comparaison visible, avec ses limites annoncées (pas d'IK complet).

## Répartition des fichiers

Le coordinateur possède prepare_assets.py, beats.py, finish_scene.py, assets,
le découpage, les exports et l'archive. La vectorisation possède vectorize.py
et requirements-vector.txt. L'agent Blender possède build_blender.py et la
note du rig. La critique possède ses deux rapports. Aucune modification
simultanée d'un même producteur ; contrôles et médias restent distincts.
