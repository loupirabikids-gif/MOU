# MOU

**Étape actuelle : un court test où MOU remue la poêle.**
Le décor et le placement sont validés. Ce test muet de4secondes permet
maintenant d’apprécier le geste avant de poursuivre avec l’essuyage.

[![Test du remuage](episodes/03/test_remuer/MOU_test_remuer_apercu.gif)](episodes/03/test_remuer/MOU_test_remuer.mp4?raw=true)

- **[Voir le test MP4](episodes/03/test_remuer/MOU_test_remuer.mp4?raw=true)**
- [Sources et contrôles](episodes/03/test_remuer/) · [Bilan](episodes/03/test_remuer/CONTROLE.txt)
- [Placement validé](episodes/03/placement/) · [Décor validé](episodes/03/decor/)

Le gag en développement porte sur le réflexe de s’essuyer les mains après
chaque contact pendant que MOU cuisine réellement. Cette étape ne présente
que le test de remuage, sans essuyage ni épisode complet.

Les anciens épisodes sont conservés, mis de côté :
[Le retardateur](episodes/01_reprise/), [Le torchon](episodes/02/).

## Équipe et dossier de création

[Règles durables et rôles](AGENTS.md) · [Profils Codex](.codex/config.toml) ·
[Compatibilité](equipe/compatibilite_agents.md) · [Coordination](equipe/README.md).
Les rôles sont appliqués par mandats distincts dans la session ; la présence
des fichiers ne prouve pas leur activation native dans tous les clients.

- [Archives : scénario et découpage du Torchon](episodes/02/developpement/)
- [Critique de la fin avant fabrication](episodes/02/developpement/critique_scenario_fin_v3.md) et [critique du montage rendu](episodes/02/controle/critique_montage.md)
- [Critiques initiales conservées](episodes/01_reprise/controle/critique.md)
- [Archives : corrections retenues](episodes/02/developpement/corrections.md)
- [Veille datée et limites](editorial/veille_2026-10-27.md) · [Suivi après diffusion](publication/README.md)

Outils de production gratuits/open source : Python, SVG, CairoSVG, Pillow,
NumPy et FFmpeg. Neuf événements sonores procéduraux originaux, dont deux
vocalisations brèves, sans voix humaine enregistrée ni musique externe.
La veille externe reste incomplète car YouTube n’est pas autorisé par le réseau
courant. Aucune statistique ni visionnage n’est inventé. La critique par images
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
L’étape en cours et ses sources se trouvent dans `episodes/03/test_remuer/`.

La référence visuelle est une illustration ; le rig est son interprétation
vectorielle. Le test vérifie des expressions et des raccords, sans mesurer
l'intérêt comique auprès d'un public.
