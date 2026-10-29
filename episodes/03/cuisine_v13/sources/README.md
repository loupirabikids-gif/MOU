# Reproduire la révision V13

Python et dépendances de `requirements.txt`, FFmpeg et Cairo nécessaires.
Depuis la racine du dépôt :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v13/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v13/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v13/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v13/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v13/sources/package.py
```

Hors du cloud, utiliser le Python où les dépendances fixées sont installées.
Aucun service externe, modèle génératif ou GPU n’est nécessaire.

- `animation.py` : gestes natifs, cinq rituels, sel et jeu des expressions.
- `art.py` : accessoires, bol/grains de sel, papier et cinq boulettes.
- `sink.py` : nouveau lavabo et pose du bout de la moufle sous l’eau.
- `render.py` : plans, calques, légende fournie et encodage.
- `son.py` : synthèse originale et mix des 64 événements.
- `verify.py` : décodage des vrais exports et rendus SVG frais hors cache.
- `package.py` : ZIP avec manifeste SHA-256 vérifié.

Les repères principaux de `../chronologie.json` sont ceux du film de 41 s.
Les gestes natifs antérieurs restent sous `animation_reference` ; la liaison
avec le montage et les cinq cycles est explicite. Garder les fichiers gelés
jusqu’à la fin du rendu. Le cache inclut le SVG complet et son échelle.

L’animatique complète est en 540 × 960 à 12 images/s ; le final en
1080 × 1920 à 24 images/s, H.264/yuv420p CRF 12 et AAC stéréo 48 kHz.
Les versions avec son et muette partagent le même flux d’images compressées.
La police DejaVu est fournie et intégrée sans dépendre des polices système.

Le ZIP contient code, dessins, sons, police, chronologie, critiques et preuves
choisies. Caches et séquences de PNG se régénèrent ; les captures complètes
restent dans Git. `controle/audit_archive.json` est hors du ZIP qu’il vérifie.
Les audits historiques comparant à une révision Git demandent l’historique du
dépôt ; la production et son contrôleur courant se reproduisent depuis le ZIP.
Les contrôles audio sont numériques, sans écoute perceptive revendiquée.
