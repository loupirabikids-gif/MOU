# MOU

Le pilote réécrit **« La dernière retouche »**, révision4 : **13 secondes**, vertical
**1080 × 1920**, avec des sons originaux et sans dialogue.

## Voir l’épisode

L’aperçu est animé et muet. Pour entendre les effets, télécharger le MP4.

[![MOU — La dernière retouche](episodes/01/MOU_01_apercu.gif)](episodes/01/MOU_01_le_retardateur.mp4?raw=true)

- **[MP4 avec son — télécharger](episodes/01/MOU_01_le_retardateur.mp4?raw=true)**
- [Version muette](episodes/01/MOU_01_le_retardateur_muet.mp4?raw=true)
- [Sources, sons et références — ZIP](episodes/01/MOU_01_sources.zip?raw=true)
- [Bilan des contrôles](episodes/01/CONTROLE.txt)
- [Chronologie](episodes/01/chronologie.json) · [Reproduction](episodes/01/sources/README.md)

MOU se trouve déjà magnifique. Il soulève ses joues pour embellir son sourire,
puis tire une fois de trop : le flash le capture en pleine retouche. La photo
lui révèle le résultat. Il baisse les mains, gêné. Son désir provoque l’accident.

Le personnage et le rig fournis sont conservés ; seuls le jeu, les gestes et
la mise en scène du pilote sont réécrits. Python, SVG, CairoSVG, Pillow, NumPy
et FFmpeg restent les seuls outils de production, tous gratuits et open source.

## Équipe et dossier de création

Règles durables : [AGENTS.md](AGENTS.md). [Profils Codex](.codex/config.toml),
[compatibilité](equipe/compatibilite_agents.md) et [coordination](equipe/README.md).
Les délégations de la session appliquent ces rôles ; la présence des fichiers
ne prouve pas leur chargement natif dans tous les clients.

- [Scénario courant](episodes/01/developpement/scenario_retenu.md) · [Découpage V4](episodes/01/developpement/decoupage_v4.md)
- [Critique avant fabrication](episodes/01/developpement/critique_scenario_v4.md) · [Critique du montage réel](episodes/01/controle/critique_v4.md)
- [Corrections et décisions](episodes/01/developpement/journal_corrections.md)
- [Cinq pistes pour la suite](episodes/01/developpement/cinq_pistes.md)
- [Veille datée et limites d’accès](editorial/veille_2026-10-27.md) · [Suivi après diffusion](publication/README.md)

La V3 avait été jugée confuse par l’utilisatrice. La V4 remplace le faux départ
par une retouche excessive, un compte régulier et une seule réaction finale.
Les critiques et découpages précédents restent conservés dans le dossier.

La veille externe reste incomplète : YouTube n’est pas autorisé par le réseau
courant. Aucun compteur ni visionnage n’est inventé. Cette correction du pilote
se fonde sur les retours et la critique interne. L’audio est contrôlé numériquement,
sans écoute sur téléphone réel ni test public. Aucun résultat d’audience n’est fourni.

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
Le premier épisode, ses livrables et ses sources se trouvent dans `episodes/01/`.

La référence visuelle est une illustration ; le rig est son interprétation
vectorielle. Le test vérifie des expressions et des raccords, sans mesurer
l'intérêt comique auprès d'un public.
