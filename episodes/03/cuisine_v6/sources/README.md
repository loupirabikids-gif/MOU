# Reproduire MOU en cuisine et en rythme

Depuis la racine du dépôt, avec Python et les dépendances de `requirements.txt`
ainsi que FFmpeg installés :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v6/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v6/sources/render.py --preview
.venv/bin/python -B episodes/03/cuisine_v6/sources/render.py
.venv/bin/python -B episodes/03/cuisine_v6/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v6/sources/package.py
```

Hors du cloud, remplacer `.venv/bin/python` par le Python où les dépendances
sont installées. Aucun service externe ni accès GPU requis. Les images et les
caches se régénèrent localement ; ils ne sont pas nécessaires dans l’archive.

- `animation.py` : actions, regards, expressions et articulation du modèle.
- `art.py` : tablier, jet renforcé, accessoires, papier et poubelle.
- `render.py` : plans larges, lavabo/main uniquement, zooms poubelle, encodage.
- `son.py` : eau et autres effets originaux, neuf notes sifflées, mix et provenance.
- `verify.py` : contrôles des vrais MP4 et comparaison à des SVG frais hors cache.
- `package.py` : archive vérifiée avec manifeste SHA-256.
- `../chronologie.json` : référence commune des événements et durées.
- `../editorial/` : références réellement accessibles et limites de la veille.

L’animatique est en 540×960 à 12 images/s ; l’export complet en 1080×1920 à
24 images/s. La version muette partage exactement les images de la version
avec son. La vérification technique ne constitue pas un test auprès d’un public.
