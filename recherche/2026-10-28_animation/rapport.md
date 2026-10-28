# Outils gratuits pour rendre MOU plus expressif

Recherche observée le **28 octobre 2026**, entre 16 h 17 et 16 h 24 environ,
fuseau **Africa/Casablanca**. Les requêtes brutes conservent les horodatages UTC.
Document de recherche, pas décision de migration ni nouvelle fabrication du film.

## Recommandation pour MOU

Pour la révision avec carotte, conserver le rig Python/SVG actuel : une migration
ne résout pas à elle seule le jeu, les intentions ou le rythme. Préparer des poses
expressives réutilisables, des regards dirigés et des accélérations dessinées dans
la chronologie reste utile quel que soit l'outil.

Pour la suite, deux pistes concrètes ressortent : **Blender**, déjà installé et
pilotable par Python, pour une bibliothèque de personnage durable ; **Friction**,
pour éditer visuellement des formes SVG et leurs courbes de mouvement. Un test
de quelques secondes sur une copie de MOU doit précéder un changement de moteur.
Il faut comparer le modèle, les deux mains, les raccords, les yeux et les couleurs.

Un cinquième candidat, **RaveAnima**, mérite un essai séparé : il annonce un
pilotage MCP/CLI et l'import SVG. C'est une découverte de la recherche réelle,
pas un outil installé ou un résultat d'animation déjà validé.

## Quatre logiciels examinés

| Outil | Licence vérifiée | Apport concret au jeu de MOU | Effort et limite pour ce projet |
| --- | --- | --- | --- |
| **[Blender](https://github.com/blender/blender)** | GPL ; les sources Grease Pencil portent `GPL-2.0-or-later`. `COPYING` renvoie au texte GPLv2. | Grease Pencil et courbes permettent d'organiser un personnage 2D, ses poses, déformations et animations. Python et le mode sans interface sont utiles pour rendre et reproduire les épisodes. | Déjà présent ici en 4.3.2. Import basique du SVG testé, mais le rig Python existant n'est pas automatiquement converti en contrôleurs Blender. Gradients approximés et identité visuelle à contrôler. Construction du rig et bibliothèque d'expressions restent à faire. |
| **[Friction](https://github.com/friction2d/friction)** | **GPL-3.0-only**, README et `LICENSE.md`. | Importe les SVG en formes éditables, anime leurs paramètres par images clés, propose une vue de courbes avec tangentes et easing. Intéressant pour régler directement sourcils, yeux, bouche, anticipation, rebond et pauses. | Pas présent dans le PATH ici ; application graphique à installer/évaluer dans un environnement adapté. L'import visuel de MOU n'a pas été essayé. Les possibilités d'export SVG sont partielles ; un export vidéo/PNG peut être préférable. Aucun transfert automatique du rig n'est démontré. |
| **[Synfig Studio](https://github.com/synfig/synfig)** | **GPLv3**, README et `LICENSE`. | Animation vectorielle/bitmap avec interpolation et outil d'os/squelette. Peut organiser un personnage articulé et diminuer les manipulations image par image. | Non installé ici. Il faut reconstituer la hiérarchie, les pivots et les contrôles d'expressions, puis vérifier l'import des dessins. Les sources du logiciel confirment l'outil d'os ; elles ne prouvent pas que le rig actuel de MOU s'importe sans travail. |
| **[OpenToonz](https://github.com/opentoonz/opentoonz)** | **BSD-3-Clause** pour le logiciel principal ; composants tiers et brosses ont leurs notices. Le README autorise explicitement l'usage professionnel ou personnel. | Outils Skeleton, cinématique inverse, poses de découpe et déformation Plastic ; remplacement de dessins dans les niveaux. Convient à une production 2D avec expressions et poses dessinées contrôlées. | Non installé ici. Plus de préparation et d'apprentissage pour MOU ; il faut organiser des calques/niveaux et un squelette. Ne pas promettre un import direct de notre SVG avec tous ses masques et dégradés. Une conversion en calques ou un dessin vectoriel adapté devra être évalué. |

Ces licences permettent un usage commercial du logiciel. Cela ne donne aucun
droit automatique sur des personnages, textures, modèles ou sons de tiers. La
GPL d'un logiciel d'animation ne rend pas à elle seule les images de MOU GPL : le
texte distingue l'exécution du programme et le contenu de sa sortie. Les coûts
éventuels de matériel/calcul restent distincts du prix nul des licences.

## Test local réel : Blender 4.3.2

Commandes exécutées sans installation, avec configuration/cache dans
`work/recherche_animation/` et `--factory-startup` :

- `blender --version` : **Blender 4.3.2**.
- Le mode `--background` fonctionne.
- `bpy.ops.wm.grease_pencil_import_svg` et `bpy.ops.import_curve.svg` sont disponibles.
- Import du fichier existant `episodes/03/placement/MOU_cuisine_placement.svg` :
  **FINISHED**, un objet Grease Pencil, **cinq calques**.
- Second import via courbes : **FINISHED**, **155 objets de type CURVE**.
- Avertissement réel du premier import :
  **« SVG has gradients, Grease Pencil color will be approximated »**.
- Le SVG source est identique à sa version GitHEAD après le test.

**Conclusion précise : import de données testé ; fidélité visuelle et transfert
du rig non validés.** Aucun rendu d'image ou de film, aucun fichier `.blend` et
aucune modification de l'épisode n'ont été produits. Les masques d'yeux, les
gradients, les contours, l'ordre de profondeur et les raccords devront notamment
être comparés sur un rendu de test avant d'envisager une migration.

Preuve : [`preuves/blender_local_probe.json`](preuves/blender_local_probe.json).
Le nombre de matériaux de cette preuve inclut les matériaux orphelins du test
précédent ; il ne faut pas l'interpréter comme une mesure fidèle de la palette.

La source officielle actuelle de l'importeur confirme que les dégradés ne sont
pas entièrement supportés et qu'ils sont approximés. Ce constat documentaire
sur la branche actuelle complète l'avertissement effectivement observé dans 4.3.2 ;
il ne remplace pas un test de rendu avec notre personnage.

## Candidat MCP : RaveAnima

[Dépôt](https://github.com/vibecoderkz/raveanima) ·
[README](https://github.com/vibecoderkz/raveanima/blob/main/README.md) ·
[LicenceMIT](https://github.com/vibecoderkz/raveanima/blob/main/LICENSE).

Le README décrit un éditeur vectoriel local avec import SVG en formes éditables,
images clés, morphing de chemins, easing, export MP4/GIF/SVG/Lottie, commandes
annulables et serveur MCP. Il annonce une exécution sans fenêtre avec rendu
Skia et FFmpeg. Les outils nommés incluent `doc_import`, `command_run`, `export`,
`render_preview` et `render_contact_sheet`.

Cette piste correspond bien au besoin d'agents qui pilotent un dessin conservé,
plutôt que de regénérer MOU à chaque plan. **Cela reste une capacité annoncée par
le projet : aucun de ces outils n'a été installé, connecté ou testé ici.**
La recherche GitHub filtrée `created:>2026-10-01` retrouve le dépôt : il est très
récent au jour d'observation. Sa stabilité, sa compatibilité SVG et la qualité
d'une animation articulée de MOU restent à éprouver sur un petit cas isolé.

Prérequis annoncés : Node 22.12+ et FFmpeg pour le CLI, Rust/Tauri pour l'application
de bureau. Node 24.19.0 et FFmpeg sont présents ici. Cela rend un essai technique
plausible, sans le rendre déjà validé. Le coût d'un modèle/agent d'IA utilisé pour
piloter le MCP n'est pas rendu gratuit par la licence MIT du logiciel.

## Autre piste considérée

[Inochi Creator](https://github.com/Inochi2D/inochi-creator), licence
[BSD-2-Clause](https://github.com/Inochi2D/inochi-creator/blob/main/LICENSE), permet
de construire des marionnettes à textures 2D déformées en temps réel. Le README
cible surtout les jeux et le VTubing. C'est intéressant pour un avatar expressif,
mais moins directement adapté à notre montage de cuisine, aux objets saisis et
au SVG existant. Aucun import automatique de notre rig n'est établi.

## Sources officielles directement consultées

1. Blender : [README](https://github.com/blender/blender/blob/main/README.md),
   [COPYING](https://github.com/blender/blender/blob/main/COPYING),
   [texteGPL](https://github.com/blender/blender/blob/main/doc/license/GPL-license.txt),
   [Grease Pencil et SPDX](https://github.com/blender/blender/blob/main/source/blender/blenkernel/BKE_grease_pencil.hh),
   [importSVG](https://github.com/blender/blender/blob/main/source/blender/io/grease_pencil/intern/grease_pencil_io_import_svg.cc),
   [argumentsPython/background](https://github.com/blender/blender/blob/main/source/creator/creator_args.cc).
2. Friction : [README](https://github.com/friction2d/friction/blob/main/README.md),
   [licence](https://github.com/friction2d/friction/blob/main/LICENSE.md),
   [import et images clés](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/usage.md),
   [techniques](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/animation_techniques.md),
   [expressions programmables](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/expressions.md),
   [limites d'exportSVG](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/export.md).
   Ici « expressions » désigne des formules de paramètres, pas une promesse
   d'expressions faciales automatiques.
3. Synfig : [README](https://github.com/synfig/synfig/blob/master/README.md),
   [licence](https://github.com/synfig/synfig/blob/master/LICENSE),
   [outil d'os dans la source](https://github.com/synfig/synfig/blob/master/synfig-studio/src/gui/states/state_bone.cpp).
4. OpenToonz : [README](https://github.com/opentoonz/opentoonz/blob/master/README.md),
   [licence](https://github.com/opentoonz/opentoonz/blob/master/LICENSE.txt),
   [cutout/Skeleton/IK](https://github.com/opentoonz/opentoonz_docs/blob/master/source/creating_cutout_animation.rst),
   [outilPlastic](https://github.com/opentoonz/opentoonz_docs/blob/master/source/create_animations_using_plastic_tool.rst).

Les statuts des réponses, courts extraits, erreurs 404 de chemins explorés, empreintes SHA256 et
horodatages sont conservés dans [`preuves/`](preuves/). Une recherche GitHub
publique sur « 2d vector animation svg » a réellement été effectuée, puis les
README, licences et documentations officielles ont été lus. Les pages HTML ont
été réduites à leurs résultats utiles, sans conserver les champs de session.

Limites : pas de moteur de recherche Web général disponible dans les outils de
la session ; réseau limité aux hôtes autorisés. L'étude s'appuie donc surtout
sur GitHub et les documents officiels accessibles. Aucun site bloqué n'a été
contourné, aucun visionnage vidéo, score de qualité, coût de calcul ou retour
d'audience n'est inventé. Aucun logiciel supplémentaire n'a été installé.
