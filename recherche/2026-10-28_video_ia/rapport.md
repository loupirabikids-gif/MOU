# Pilotage et IA vidéo — recherche du28octobre2026

Observation :28octobre2026, fuseau Africa/Casablanca. Recherche GitHub publique
« blender mcp animation », puis lecture des README et licences officiels.
URL, statut HTTP, heure, SHA et extraits sont dans `sources.json` et `preuves/`.
Les pages de recherche complètes restent dans `work/` ; leurs résultats utiles
sont extraits sans champs de session. Aucun outil de recherche Web général
n’est disponible ici ; aucune source inaccessible n’est présentée comme consultée.
Les deux requêtesMCP de ce sous-dossier ont réponduHTTP200, mais leur extraction
n’a pas fourni de liste de dépôts exploitable. Il ne faut pas lire cela comme
« aucun résultat sur GitHub ». Les outils ci-dessous ont donc été consultés
directement ; les recherches positives et résultats de découverte sont conservés
dans les dossiers animation et son.

## Blender MCP : pont de pilotage, pas moteur gratuit de génération

- Dépôt : [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp).
- [Licence MIT vérifiée](https://github.com/ahujasid/blender-mcp/blob/main/LICENSE).
- Le README courant décrit notamment `execute_blender_code`, `look` et
  `get_scene_info` : écrire du Python dans Blender, voir caméra/poses et lire
  la scène. Le nom de paquet indiqué dans cette version est `mcp-for-blender`.
- Cela peut aider des agents à manipuler un personnage et contrôler des images.
  Le plugin ne crée pas automatiquement un bon jeu ni un rig fidèle à MOU.
- Son outil `generate_3d` propose des services cloud, dont certains sont payants.
  Le code MIT ne rend pas ces services gratuits. Pour ce projet, retenir seulement
  le contrôle local des dessins et de l’animation ; aucun modèle3D généré n’est
  nécessaire pour conserver le personnage2D.
- Plugin non installé, non connecté et non testé dans ce chat. Blender lui-même
  est présent et peut déjà être piloté ici par son API Python en mode headless.
  Le coût éventuel du client/agent IA reste distinct de la licence du plugin.

## ComfyUI et Wan2.2 : essais génératifs possibles

| Candidat | Preuves lues | Possibilité utile | Limite pratique |
| --- | --- | --- | --- |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | README et [GPLv3](https://github.com/comfyanonymous/ComfyUI/blob/master/LICENSE), HTTP200. Le README liste les modèles vidéo Wan2.1/2.2. | Construire un pipeline local réutilisable d’image vers vidéo et tester une animation à partir de la référence de MOU. | Logiciel libre, mais licences des modèles et éventuels nœuds/API distinctes. Aucun pipeline installé ni calcul réalisé ici. Les affirmations de faible VRAM des auteurs ne constituent pas une mesure de notre projet. |
| [Wan2.2](https://github.com/Wan-Video/Wan2.2) | README et [Apache2.0](https://github.com/Wan-Video/Wan2.2/blob/main/LICENSE.txt), HTTP200. Le README indique explicitement que les modèles du dépôt sont sous Apache2.0. | Les modes image-vers-vidéo partent d’une image ; Animate-14B décrit une réplication de mouvements et d’expressions à partir d’une référence et d’une vidéo pilote. | Aucun essai sur MOU : fidélité au blob, deux yeux, deux mains et raccords non démontrés. Les contacts précis couteau/carotte/robinet ne sont pas garantis. Les exemples officiels TI2V-5B annoncent24Go VRAM ; les commandes I2V-A14B consultées annoncent80Go. Ces chiffres ne sont pas transposés à toutes les variantes ou quantifications. |

Le guide de prétraitement Animate prévoit une option `--use_flux` utilisant
`FLUX.1-Kontext-dev`. Sa licence n’est pas déduite de celle de Wan. Le guide
avertit lui-même que ce prétraitement ne garantit pas la cohérence ni une pose
correcte. Un éventuel essai doit choisir explicitement ses composants et leurs
licences ; aucune chaîne commerciale complète n’est déclarée validée ici.

Sources : [guide de prétraitement](https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/UserGuider.md),
[code des options](https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/preprocess_data.py).

## État réel de cet environnement

- **Blender4.3.2 présent** ; l’autre recherche a testé l’import du SVG MOU sans
  créer de nouveau film. Fidélité visuelle et transfert du rig non validés.
- **Kdenlive24.12.3 présent**, confirmé par `--version` en mode offscreen.
- **FFmpeg présent** et déjà utilisé par le projet.
- Aucun `nvidia-smi` ni périphérique `/dev/nvidia*` détecté par nos contrôles.
  Cela ne constitue pas un inventaire de tout matériel possible ; aucune
  capacité de calcul GPU pour Wan n’est établie ici.
- Aucun poids IA, nouveau plugin ou logiciel téléchargé/installé. Les logiciels
  gratuits n’incluent pas automatiquement une machine GPU ou un hébergement gratuit.

## Choix recommandé

Pour la carotte, conserver le modèle corrigé et le pipeline actuel, préparer
des intentions de jeu distinctes et des bruitages reconnaissables. Tester ensuite
Blender déjà disponible sur une courte scène isolée avant toute migration.
Friction est une alternative2D/SVG à examiner, et RaveAnima une piste MCP récente
documentée dans le rapport animation. ComfyUI/Wan restent des pistes de test,
pas une garantie de conservation du personnage ni une solution déjà opérationnelle.
