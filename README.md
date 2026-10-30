# MOU

**V25 rejetée par l'utilisatrice : version de travail conservée, publication
déconseillée en l'état.** Le [réexamen éditorial](episodes/03/developpement/reprise_editoriale/)
reprend la progression du gag et le jeu de MOU. Les contrôles techniques
ci-dessous ne constituent pas une approbation artistique.

**[Bibliothèque d’expressions de MOU](bibliotheque/expressions/v1/)** — 36 poses, 12 familles, galerie SVG/PNG et six transitions de visage.

**Encore une feuille — Just cooking. Mostly washing. — V25, 43 secondes.**

MOU cuisine, mais chaque contact relance son lavage et son gaspillage de papier.
Carotte, tomate, pincée de sel… le rouleau finit vide et la poubelle déborde.
La dernière boulette tombe au sol ; MOU regarde les déchets puis le public.

La V25 reprend le jeu : corps et visage agissent ensemble, les mains libres
accompagnent les intentions et des pauses exposent les réactions. Après le
dernier essuyage, le soulagement précède la découverte des déchets et le recul ;
MOU rejoint ensuite le spectateur du regard. Le modèle, les contours natifs
des deux bras/moufles, le costume et les gros plans de lavabo sont conservés.

Le fond musical est un duo piano-contrebasse aux attaques enveloppées,
sans mélodie aiguë ni percussion. Il reste continu et son niveau moyen est
environ 6 dB plus bas que V24. Les événements papier utilisent des prises et
textures libres documentées, avec leurs coupes alignées aux gestes.

[![Attitudes et regards extraits du film V25](episodes/03/cuisine_v25/controle/planche_jeu_final.png)](episodes/03/cuisine_v25/MOU_Encore_une_feuille.mp4?raw=true)

- **[Film avec son — 1080 × 1920](episodes/03/cuisine_v25/MOU_Encore_une_feuille.mp4?raw=true)**
- [Aperçu du jeu et de la fin — 8 secondes](episodes/03/cuisine_v25/MOU_test_mise_en_scene.mp4?raw=true)
- [Version muette](episodes/03/cuisine_v25/MOU_Encore_une_feuille_muette.mp4?raw=true)
- [Sources ZIP](episodes/03/cuisine_v25/MOU_Encore_une_feuille_sources.zip?raw=true) · [Contrôles et limites](episodes/03/cuisine_v25/CONTROLE.txt)
- [Direction et critiques V25](episodes/03/cuisine_v25/)
- [Recherche : outils libres réellement testés et techniques retenues](recherche/2026-10-29_professionnel/README.md)
- [Repérage animation adulte : chaînes, pages et dépôts GitHub](recherche/2026-10-29_animation_adulte/README.md)
- [Accès YouTube après activation du 30 octobre et recherche documentaire](recherche/2026-10-30_acces_youtube/README.md)
- [Lamput : analyse visuelle du fichier fourni et propositions pour MOU](recherche/2026-10-30_lamput/README.md)

Blender et RaveAnima ont été essayés ; leurs imports automatiques altèrent les
masques du SVG. Le film garde son rendu CairoSVG. Friction et OpenToonz
fournissent des méthodes de poses, d’exposition et de courbes documentées.
L’accès officiel à Oggy est bloqué : aucun visionnage n’est revendiqué.
Le modèle ne peut pas écouter le mix ; les mesures ne certifient pas le confort
sur téléphone. Les critiques portent sur les images et les séquences décodées.

[V24 rejetée](episodes/03/cuisine_v24/) · [V23](episodes/03/cuisine_v23/) · [V22](episodes/03/cuisine_v22/) · [V21 rejetée](episodes/03/cuisine_v21/) · [V20](episodes/03/cuisine_v20/) ·
[V19](episodes/03/cuisine_v19/) · [Versions de 35 secondes](episodes/03/cuisine_v6/).
Les épisodes abandonnés restent conservés :
[Le retardateur](episodes/01_reprise/), [Le torchon](episodes/02/).

## Équipe et dossier de création

[Règles durables et rôles](AGENTS.md) · [Profils Codex](.codex/config.toml) ·
[Compatibilité](equipe/compatibilite_agents.md) · [Coordination](equipe/README.md).
Les rôles sont appliqués par mandats distincts dans la session ; la présence
des fichiers ne prouve pas leur activation native dans tous les clients.

- [Archives : scénario et découpage du Torchon](episodes/02/developpement/)
- [Critique avant fabrication](episodes/02/developpement/critique_scenario.md) et [critique du montage rendu](episodes/02/controle/critique_montage.md)
- [Critiques initiales conservées](episodes/01_reprise/controle/critique.md)
- [Archives : corrections retenues](episodes/02/developpement/corrections.md)
- [Veille datée et limites](editorial/veille_2026-10-27.md) · [Suivi après diffusion](publication/README.md)

Outils de production gratuits/open source : Python, SVG, CairoSVG, Pillow,
NumPy, FFmpeg et FluidSynth. Partition originale, banque d’instruments libre
[FluidR3 MIT créditée](episodes/03/cuisine_v23/assets/FluidR3_README.md), bruitages originaux ; trois notes sifflées
uniquement au départ, aucun dialogue ni musique téléchargée.
La [recherche de réalisation actuelle](recherche/2026-10-29_professionnel/README.md)
conserve les essais et les preuves d’accès. Aucune statistique, écoute ou
observation d’une vidéo inaccessible n’est inventée. Les critiques par images
et les contrôles audio numériques ne valent pas test public ou écoute sur téléphone.

## Base du projet

Base de lancement de la série de courts gags visuels de MOU.

Le personnage vert à deux yeux est retenu. Ce dossier contient le modèle
articulé utilisé dans le test, sa référence, les contrôles et les consignes
pour fabriquer le premier épisode.

## Commencer

Lire `AGENTS.md`, `BRIEF_MOU_CODEX.txt` puis `PILOTE_01.txt`.
Le texte à transmettre à Codex est dans `DEMARRER_CODEX.txt`.

## Reproduire le test déjà livré

Prérequis : Python 3.11 ou plus, FFmpeg et les bibliothèques système nécessaires
à CairoSVG/Cairo. La police DejaVu fournie dans `fonts` permet de conserver
le lettrage lorsqu'elle est installée sur le système de rendu.

```bash
python3 -m pip install -r requirements.txt
python3 verification.py --preview
python3 verification.py
```

La première commande de rendu produit une planche. La seconde exporte les
216 images de travail et le test de neuf secondes avec son.

## Repères

- `mou_rig.py` : géométrie paramétrique du personnage.
- `verification.py` : poses, transitions, sons et export du test.
- `references/MOU_reference.png` : étude visuelle de référence.
- `references/MOU_intentions_12.png` : intentions de jeu de l'ancienne planche ;
  suivre le modèle vérifié pour les raccords des bras et des mains.
- `output/MOU_verification_9_secondes.mp4` : test de construction.
- `output/MOU_controle_des_poses.png` : poses extraites du test.
- `output/RAPPORT_VERIFICATION.txt` : contrôles effectués et limites.
- `SOURCES.txt` : références et liens techniques.

Les poses SVG et les sons du test se régénèrent avec le script.
Le montage courant et ses sources se trouvent dans `episodes/03/cuisine_v22/`.

La référence visuelle est une illustration ; le rig est son interprétation
vectorielle. Le test vérifie des expressions et des raccords, sans mesurer
l'intérêt comique auprès d'un public.
