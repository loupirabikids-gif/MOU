# MOU — Poids plume

Essai **muet de dix secondes**, 1080 × 1920, 24 images/s. MOU offre sa tête
avec assurance à une plume qui descend. Elle l'écrase. Après un redressement
raté, il tente de garder sa dignité devant le spectateur.

- [Voir l'essai](MOU_Poids_plume_10s_muet.mp4?raw=true)
- [Trois intentions](MOU_Poids_plume_trois_poses.png?raw=true)
- [Sources autonomes](MOU_Poids_plume_sources.zip?raw=true)
- [Bilan des contrôles](CONTROLE.md)

Le dessin compact citron reprend la silhouette du galet déjà proposé dans
le projet. Ce test de base n'utilise ni bras ni mains. Les yeux, sourcils,
bouche, inclinaison, volume et pauses portent le jeu. Les anciennes versions
de MOU et les fichiers Blender sont conservés.

Ce premier essai suit la remise à zéro du plan de production. La critique
avant fabrication est conservée avec les cinq idées, le scénario, la
chronologie et la critique du vrai montage. La nouvelle cadence hebdomadaire
reste à mesurer après deux pilotes ; ce test ne vaut pas approbation artistique
de l'utilisatrice ni validation d'une série.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, avec Python 3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python essais/reprise_10s_v1/sources/render.py --stills
python essais/reprise_10s_v1/sources/render.py --preview
python essais/reprise_10s_v1/sources/render.py
```

Dans l'environnement du projet, utiliser `.venv/bin/python`.
Le personnage et la plume sont dessinés en SVG par les sources incluses.
Le rendu ne nécessite aucun ancien rig, service, modèle téléchargé ou compte.
La police DejaVu ne sert qu'aux légendes de la planche ; elle est incluse avec
sa licence. Le film n'emploie ni texte explicatif ni ressource tierce.

`sources/personnage.py` conserve la bibliothèque paramétrique de six attitudes.
`sources/scene.py` dirige les actions, regards, contacts et cadres ;
`sources/render.py` rend toute la séquence et encode le MP4.
`chronologie.json` décrit le découpage et les événements communs.
Les images de travail sont dans `work/`, hors Git.

La QA complète se relance dans le dépôt avec `controle/verify.py` (voir `--help`).
La partie qui vérifie les empreintes des anciens films nécessite le dépôt
complet : ces films ne sont pas recopiés dans l'archive des sources.

## Origine et périmètre

Dessins et mouvements créés dans le projet avec Python/SVG/CairoSVG/FFmpeg.
L'organisation en actions nommées et pauses s'inspire de la référence technique
doodle-anim déjà étudiée ; aucun code ou dessin de ce dépôt n'est importé.
Le mécanisme d'un très petit poids qui écrase un personnage est familier du
cartoon. Ce gag sert ici à tester trois intentions, sans revendication
d'invention du mécanisme ni données d'audience.
