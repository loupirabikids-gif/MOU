# Six dépôts libres utiles à MOU

Recherche réelle du **29 octobre 2026**, observations horodatées UTC dans
[preuves.json](preuves.json). README, licences, flux de commits et pages de
release ont été demandés aux dépôts officiels GitHub, par le proxy normal.
Les liens listés ne sont pas des dépôts de sources d’Oggy, Mr Bean ou d’autres
séries : ce sont des **outils de fabrication**. Leur popularité éventuelle
ne démontre pas le succès d’un dessin animé produit avec eux.

| Dépôt et licence vérifiée | Activité visible au moment de la consultation | Utilité concrète pour MOU | Preuve et limite |
| --- | --- | --- | --- |
| [Friction](https://github.com/friction2d/friction) — [GPL-3.0-only](https://github.com/friction2d/friction/blob/main/LICENSE.md) | Dernier commit affiché : **2026-10-28**, `be9471c…`. La page `/releases/latest` mène à [v1.0.0-rc.3](https://github.com/friction2d/friction/releases/tag/v1.0.0-rc.3) ; c’est une version candidate, pas une preuve de stabilité. | Éditer des poses vectorielles et leurs durées, régler les courbes, choisir des dessins de bouche/paupière par flipbook. Bon candidat à un essai d’une seconde de jeu facial. | README et licence lus à nouveau ; méthodes flipbook/morphing documentées dans l’étude précédente. **Aucun import MOU ni épisode rendu avec Friction.** |
| [OpenToonz](https://github.com/opentoonz/opentoonz) — [BSD-3-Clause](https://github.com/opentoonz/opentoonz/blob/master/LICENSE.txt), composants tiers séparés | Dernier commit affiché : **2026-10-28**, `572d59a…`. Dernière release indiquée par la route GitHub : [v1.8.0](https://github.com/opentoonz/opentoonz/releases/tag/v1.8.0), date affichée **2026-06-19**. | Xsheet pour exposer les poses, organiser les vrais arrêts et séparer visage, mains et caméra. Utile pour une fabrication par dessins clés plutôt qu’une interpolation uniforme. | README et licence actuels lus ; Xsheet et courbes étudiées précédemment. **Pas installé ni testé sur MOU.** Son origine Toonz/Ghibli mentionnée dans le README ne prouve pas que les séries adultes sélectionnées l’utilisent. |
| [Blender](https://github.com/blender/blender) — GPL ; le README actuel annonce **GPLv3 pour l’ensemble**, licences compatibles par fichiers | Dernier commit affiché : **2026-10-29**, `40af1cf…`. Pas de release GitHub publiée établie par `/releases/latest` : la route revient à la liste. | Caméra orthographique, montage/compositing, clés et pauses ; employer les images CairoSVG fidèles en calques pour garder l’art de MOU. | Deux imports SVG puis un plan d’image ont réellement été rendus lors de l’étude précédente. Les imports automatiques altéraient masques/contours ; le plan d’image respectait le dessin. **Ce n’est pas un rig MOU transféré et validé.** |
| [Synfig Studio](https://github.com/synfig/synfig) — [GPLv3 annoncée au niveau projet](https://github.com/synfig/synfig/blob/master/LICENSE), fichiers individuels parfois GPLv2-or-later | Dernier commit affiché : **2026-10-27**, `17ffa4c…`. Route GitHub vers [v1.5.5](https://github.com/synfig/synfig/releases/tag/v1.5.5), date affichée **2026-03-16** ; ne pas déduire de cette seule route le statut stable d’une branche. | Piste supplémentaire pour animation vectorielle à interpolation et squelette de cutout ; pourrait offrir une édition directe du jeu et des courbes. | README, licence et sources des outils de squelette/os réellement lus. **Aucune installation, import ni animation MOU testés** ; conservation des masques SVG et des raccords à prouver avant migration. |
| [RaveAnima](https://github.com/vibecoderkz/raveanima) — [MIT](https://github.com/vibecoderkz/raveanima/blob/main/LICENSE) | Dernier commit affiché : **2026-10-20**, `14cfa38…`. Aucune release GitHub publiée établie ; la version locale précédemment testée est 0.2.0. | Documents JSON, commandes CLI/MCP, poses tenues, courbes et exports MP4 ; intéressant pour que l’agent et un humain puissent régler le même document. | Essai antérieur réel : reconstruction de trois masques, maintien puis déplacement, MP4 36 images. **Aucune preuve de jeu expressif abouti ni de production longue.** Projet jeune, à employer pour un test isolé. |
| [Audacity](https://github.com/audacity/audacity) — [GPLv3 au niveau logiciel](https://github.com/audacity/audacity/blob/master/LICENSE.txt), documentation distincte | Dernier commit affiché : **2026-10-29**, `cd9074f…`. Route GitHub vers [Audacity-4.0.1](https://github.com/audacity/audacity/releases/tag/Audacity-4.0.1), date affichée **2026-09-30**. | Écoute comparative, enveloppes de volume, édition fine de l’eau et du papier ; compléter les mesures FFmpeg par une vraie décision d’écoute. | README/licence/release actuels lus. **Pas de mix écouté par le modèle ni de nouvelle session Audacity réalisée.** Le README avertit que `master` subit une refonte importante ; ne pas assimiler le dernier commit à une version prête à utiliser. |

Les dates de commit sont celles du flux Atom officiel observé ; les dates de
release sont les dates affichées dans les pages de destination. Ces indices
montrent une activité de dépôt, pas une assurance de fiabilité ni de qualité
artistique. Aucun compteur de stars n’est inventé ou utilisé comme preuve de
réussite d’un épisode. Aucun outil supplémentaire n’a été installé pour cette
recherche : elle ne modifie ni le modèle ni les films livrés.

## Choix recommandé

Pour MOU maintenant, **garder Python/SVG/CairoSVG/FFmpeg** pour la fidélité,
conserver les sources de poses et de caméras, et améliorer les intentions de
jeu à partir de références réellement visibles. Parmi les nouveaux essais,
**Friction** est la piste prioritaire pour éditer quelques poses et tenues ;
**Synfig** est une seconde piste de cutout à éprouver. Blender sert déjà de
solution de caméra/compositing par images si une interface devient nécessaire.
Aucun changement de logiciel ne remplace le choix d’une bonne pose, d’un axe
lisible et d’un temps de réaction.

Pour le son, Audacity peut permettre à un humain d’entendre et de comparer
les niveaux à volume égal. Le modèle ne peut pas qualifier la douceur d’un
mix qu’il n’a pas entendu. Les mesures actuelles restent des contrôles
matériels, séparés de cette évaluation.

## Sources et reproduction des constats

- [Preuves des accès et des extraits](preuves.json) : URLs, horodatage UTC,
  statut HTTP, SHA256 des réponses et courts extraits ou dates extraites.
- [Essais Blender/RaveAnima antérieurs](../../2026-10-29_professionnel/outils/rapport.md) : scripts et images réellement produits le même jour.
- [Méthodes de jeu et caméra déjà documentées](../../2026-10-29_professionnel/oggy/rapport.md) : propositions pour MOU, distinctes d’un visionnage Oggy.
- [Synfig : source du squelette](https://github.com/synfig/synfig/blob/master/synfig-core/src/synfig/layers/layer_skeleton.cpp) et [outil d’os](https://github.com/synfig/synfig/blob/master/synfig-studio/src/gui/states/state_bone.cpp) réellement consultés.

La tentative `synfig/synfig/master/COPYING` a répondu 404 ; le README
renvoyait au bon fichier `LICENSE`, ensuite récupéré avec succès. Cette
correction est conservée dans les preuves. Les documents externes ont été
traités comme des sources, aucune instruction de README n’a été exécutée.
