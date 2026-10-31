# Galet — premier essai de personnage

Concept sélectionné par l'utilisatrice : un petit galet souple, deux grands yeux,
deux petites moufles flottantes et deux pieds sombres. Très sûr de lui, dépassé
par un minuscule problème. **Galet est un nom de travail.** Le dessin citron est
une première proposition à juger ; le choix du concept ne vaut pas approbation
de ce rendu.

- [Voir l'essai muet — 5 secondes](Galet_miette_muette.mp4?raw=true)
- [Dessin du personnage](Galet_reference.png)
- [Six poses du test](Galet_poses.png)
- [Sources autonomes ZIP](Galet_sources.zip?raw=true)
- [Bilan des contrôles](CONTROLE.md)

La miette collante : il repère la miette sur sa moufle gauche, la retire avec
la droite, admire la gauche propre, puis découvre la miette à droite. Retour
au public et sourire de façade, dernière demi-seconde tenue. Aucun dialogue,
texte explicatif ou son dans ce premier essai.

Le nouveau rig est indépendant : les moufles ont leurs propres position,
rotation et fermeture de pouce. Il n'y a pas de bras. Les petits pieds restent
stables pendant le jeu du corps. Les mains passent sous le visage à l'aller et
au retour pour laisser lire les expressions.

Les anciens personnages, épisodes cuisine et travaux V29 interrompus restent
conservés. Ce test ne relance pas l'ancien épisode ni une production de série.
Tous les dessins sont créés par code pour cette proposition ; aucun sprite ou
son de Bubu, Clawd ou d'une autre référence n'est réutilisé.

## Reproduction

Depuis le dépôt ou le ZIP extrait, avec Python 3.11 minimum et FFmpeg installé :

```sh
python -m pip install -r requirements.txt
python personnages/galet_v1/sources/render.py --stills
python personnages/galet_v1/sources/render.py --preview
python personnages/galet_v1/sources/render.py
```

Dans l'environnement du projet, remplacer `python` par `.venv/bin/python -B`.
La police DejaVu et sa licence sont incluses pour les légendes des planches.
Les images de la vidéo n'emploient aucune police et aucun fichier externe.
Le ZIP ne nécessite ni l'ancien rig MOU, ni un service, ni une connexion réseau.

`sources/rig.py` dessine corps, visage et moufles ; `sources/animation.py` dirige
l'action ; `sources/palette.json` fixe les couleurs ; `sources/render.py` produit
poses, animatique et MP4. La QA indépendante se trouve dans `controle/verify.py`.
Voir ses options `--help` pour relancer le contrôle dans le dépôt complet :
il vérifie aussi les archives MOU protégées, absentes du petit ZIP autonome.

Ce prototype vérifie un dessin et une seule manipulation. Il ne démontre pas
encore tous les gestes de cuisine, un épisode complet, une identité sonore ou
le succès d'une chaîne.
