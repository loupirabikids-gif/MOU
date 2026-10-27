# MOU

Le premier épisode **« Le retardateur »** est terminé : 14 secondes, format
vertical **1080 × 1920**, avec des effets sonores originaux et sans dialogue.

## Voir le premier épisode

L'aperçu ci-dessous est animé et muet. Pour entendre les effets, télécharger
le MP4 puis l'ouvrir sur un téléphone ou un ordinateur.

[![Aperçu animé de MOU — Le retardateur](episodes/01/MOU_01_apercu.gif)](episodes/01/MOU_01_le_retardateur.mp4?raw=true)

- **[Télécharger le MP4 avec son](episodes/01/MOU_01_le_retardateur.mp4?raw=true)**
- [Télécharger la version muette](episodes/01/MOU_01_le_retardateur_muet.mp4?raw=true)
- [Télécharger les sources et les sons — ZIP](episodes/01/MOU_01_sources.zip?raw=true)
- [Lire le bilan des contrôles](episodes/01/CONTROLE.txt)
- [Chronologie](episodes/01/chronologie.json) · [Instructions de reproduction](episodes/01/sources/README.md)

Le rig MOU fourni est conservé. Fabrication locale avec Python, SVG, CairoSVG,
Pillow, NumPy et FFmpeg, tous gratuits et open source. Les raccords, les regards,
la photo figée, la synchronisation et les exports ont été contrôlés. Les deux
défauts repérés au premier montage (paupières et recadrage) sont corrigés.
Le contrôle audio est numérique, sans écoute sur téléphone réel ni test public.

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
