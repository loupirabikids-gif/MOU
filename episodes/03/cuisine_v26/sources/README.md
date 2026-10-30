# Reproduire la cuisine V26

Python 3.11 minimum, dépendances de requirements.txt, Cairo, FFmpeg et
FluidSynth système. Les ressources et leurs notices sont incluses sous assets/.
Aucun service payant ni téléchargement n'est requis au rendu après installation.

Depuis la racine du dépôt ou de l'archive extraite :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/render.py --preview
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/render.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/verify.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v26/sources/package.py
```

Animatique : 540 × 960 à 24 images/s, afin de conserver les poses de 2–4 images.
Final : 1080 × 1920 à 24 images/s, 38 secondes. --silent-only permet d'encoder
le montage visuel pendant la préparation du son. Les caches sont écrits
atomiquement, puis des images du MP4 sont comparées à des SVG frais hors cache.

chronologie.json dirige la V26. Les fichiers locaux reference_*.py et
chronologie_reference_v25.json conservent les gestes précédents réutilisés
comme matière ; le wrapper dirige les quatre cycles, le jeu et la fin.
cooking_fx.py fait évoluer les mêmes aliments et la fumée dans le temps.
Le dossier developpement/ conserve le découpage, les décisions et les critiques.

Le ZIP inclut l'arborescence requise, les sons et licences, et un manifeste
SHA256. Aucun ancien film, cache ou image intermédiaire. L'audit de l'archive
elle-même reste à l'extérieur afin d'éviter une empreinte circulaire.

Une commande réussie prouve la fabrication, pas la lisibilité d'une émotion,
le confort sonore ou la réussite comique. Voir le bilan et la critique réelle.
