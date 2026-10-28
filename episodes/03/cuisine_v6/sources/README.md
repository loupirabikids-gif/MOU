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
- `son.py` : eau et autres effets originaux, trois notes sifflées initiales et musique de fond originale, mix et provenance.
- `verify.py` : contrôles des vrais MP4 et comparaison à des SVG frais hors cache.
- `package.py` : archive vérifiée avec manifeste SHA-256.
- `../chronologie.json` : référence commune des événements et durées.
- `../editorial/` : références réellement accessibles et limites de la veille.

L’animatique est en 540×960 à 12 images/s ; l’export complet en 1080×1920 à
24 images/s, H.264 CRF 14 après le correctif papier V7. La version muette partage exactement les images de la version
avec son. La vérification technique ne constitue pas un test auprès d’un public.

Le correctif papier V7 conserve les gestes et le mix. Le dernier morceau et
sa boulette sont agrandis ; le froissage garde un contour continu.
`../controle/audit_archive.json` vérifie le ZIP lui-même et reste disponible
dans le dépôt, hors de l’archive, pour éviter une empreinte circulaire.
Les captures des revues antérieures du papier restent dans le dépôt ; le ZIP
conserve leurs rapports et preuves JSON, ainsi que les images de la dernière
révision sonore et les études de construction.

Correctif sonore V8 : la première phrase sifflée reste, les suivantes sont
retirées. La piste musicale originale est rigoureusement muette hors des
fenêtres `background_music.windows` de la chronologie. Les sons d’eau et de
papier restent audibles pendant ces coupures musicales.

Révision de rythme V9 : 35 s /840 images au lieu de 30 s /720. Les champs
principaux de la chronologie sont les repères de production et pilotent le son.
`animation_reference` conserve les actions V8 en temps source ; `scene_time`
évalue l’ouverture prolongée et décale les autres plans de 120 images. Le
remuage natif et le balancement utilisent leur rythme propre, sans ralentir
la musique ni rejouer le sifflement. Les fonctions natives des bras restent
identiques. Les anciens repères chiffrés des documents V8 sont historiques.
