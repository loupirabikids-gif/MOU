# MOU

**Nouvelle proposition écrite : [Le torchon](episodes/02/developpement/scenario_retenu.md).**
« Le retardateur » est mis de côté à la demande de l’utilisatrice ; ses fichiers
restent conservés ci-dessous. Aucune nouvelle vidéo n’est produite à ce stade.

**Archive — Le retardateur, fin révisée** : 13 secondes, vertical **1080×1920**,
avec des sons originaux et une histoire compréhensible sans dialogue.
Dernier montage conservé dans `episodes/01_reprise/`.

## Voir l’épisode mis de côté

L’aperçu est animé et muet ; le MP4 contient les effets synchronisés.

[![MOU — Le retardateur](episodes/01_reprise/MOU_le_retardateur_apercu.gif)](episodes/01_reprise/MOU_le_retardateur_nouveau.mp4?raw=true)

- **[MP4 avec son — télécharger](episodes/01_reprise/MOU_le_retardateur_nouveau.mp4?raw=true)**
- [Version muette](episodes/01_reprise/MOU_le_retardateur_nouveau_muet.mp4?raw=true)
- [Sources, sons et références — ZIP](episodes/01_reprise/MOU_le_retardateur_sources.zip?raw=true)
- [Bilan des contrôles](episodes/01_reprise/CONTROLE.txt) · [Reproduction](episodes/01_reprise/sources/README.md)

MOU se croit magnifique. Il pose, se relâche pendant que le dernier chiffre
reste affiché, puis le flash capture son sourire crispé et son regard qui louche.
Il découvre sa photo, nous regarde et tente deux petits « hé… hé… » soufflés
pour sauver les apparences. La pose finale tient une demi-seconde en silence.
Le personnage vert à deux yeux, ses deux mains et son rig sont conservés.

Le compteur est régulier et aucun portrait n’apparaît avant la capture.
La photo exacte reste figée en gros plan pendant 1,25 seconde. Les bras gardent
exactement le dessin du modèle original, avec une seule mitaine chacun ;
les pieds restent au sol. Les anciens montages sont conservés
séparément dans [episodes/01/](episodes/01/), avec leur historique Git.

## Équipe et dossier de création

[Règles durables et rôles](AGENTS.md) · [Profils Codex](.codex/config.toml) ·
[Compatibilité](equipe/compatibilite_agents.md) · [Coordination](equipe/README.md).
Les rôles sont appliqués par mandats distincts dans la session ; la présence
des fichiers ne prouve pas leur activation native dans tous les clients.

- [Scénario et découpage](episodes/01_reprise/developpement/)
- [Critique de la fin avant fabrication](episodes/01_reprise/developpement/critique_scenario_fin_v3.md) et [critique du montage rendu](episodes/01_reprise/controle/critique_fin_v3.md)
- [Critiques initiales conservées](episodes/01_reprise/controle/critique.md)
- [Corrections retenues](episodes/01_reprise/developpement/corrections.md)
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
Le montage courant, ses livrables et ses sources se trouvent dans `episodes/01_reprise/`.

La référence visuelle est une illustration ; le rig est son interprétation
vectorielle. Le test vérifie des expressions et des raccords, sans mesurer
l'intérêt comique auprès d'un public.
