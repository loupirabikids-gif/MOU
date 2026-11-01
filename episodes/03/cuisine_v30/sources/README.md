# Reproduire V30

Python 3.11 minimum, NumPy, CairoSVG, Pillow et FFmpeg. Installer les dépendances
de `requirements.txt`. Les ressources et leurs licences sont conservées.

Depuis la racine du dépôt ou de l’archive extraite :

```bash
.venv/bin/python -B episodes/03/cuisine_v30/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v30/sources/render.py --preview
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v30/sources/render.py
```

`son.py` lit la banque locale `audio/inputs/`, vérifiée par empreintes. Il ne
resynthétise pas les voix ou les matières. La cuisson reste exclue ; le jazz
reçoit un gain constant de −6 dB. Les autres sons gardent leur niveau et leurs
instants. Les contrôles de niveau ne constituent pas une écoute.

`performance.py` et `jeu_visage.py` dirigent le jeu plus marqué du même MOU.
`animation.py` conserve le montage, les cibles et actions V28 ; le lavabo,
les bras et les moufles restent leurs dessins natifs. `render.py` remet le
cartouche anglais d’origine. L’animatique et le HD utilisent le même SVG.

Après les exports, dans le dépôt complet :

```bash
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v30/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v30/sources/package.py
```

La QA vérifie aussi les fichiers protégés des versions précédentes ; ces
anciens films ne sont pas dupliqués dans le ZIP. Les sources, sons et ressources
nécessaires à la reproduction de V30 sont inclus dans l’archive. Les producteurs
conservés avec le suffixe `reference` documentent la filiation du rig ; ils ne
doivent pas être exécutés comme nouvelle commande de production.
