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
24 images/s, H.264 CRF 12 après la retouche matière V11. La version muette partage exactement les images de la version
avec son. La vérification technique ne constitue pas un test auprès d’un public.

Le correctif papier V7 conserve les gestes et le mix. Le dernier morceau et
sa boulette sont agrandis ; le froissage garde un contour continu.
`../controle/audit_archive.json` vérifie le ZIP lui-même et reste disponible
dans le dépôt, hors de l’archive, pour éviter une empreinte circulaire.
Les captures complètes des revues restent dans le dépôt ; le ZIP conserve
leurs rapports et preuves JSON, les études de construction et, pour la V11,
les planches de lecture et trois images natives décisives du dernier papier.

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

Légende V10 : `CAPTION_TEXT` dans `render.py`, visible sur les trois premières
secondes du film, avec sortie douce à 2,85–3 s. Le texte est dessiné avec la
police TTF fournie par Pillow puis intégré sur un calque transparent dans le
SVG. Cela évite une dépendance à la police installée sur le système de rendu.
La police est incluse dans le gel des sources et dans le ZIP.

Retouche matière V11 : le dernier morceau garde l’encombrement de 64 × 88 et
la même prise. Son contour souple et déchiré remplace le rectangle à coin
replié ; les plis suivent la feuille jusque dans son froissage continu.
`../controle/audit_papier_v11.json` compare les scènes aux 840 états V10.
Les autres accessoires, le personnage, les gestes et tout le son restent
inchangés lors de cette retouche. Les rapports V11 conservent sa preuve.

Ordre V12 : découper la carotte avant d’ajouter la tomate. Les trois segments
`action_reorder.segments` associent le nouveau temps de production aux gestes
natifs déjà contrôlés. `animation_reference` et les repères de caméra restent
en temps source ; la poubelle, le rouleau et les ingrédients suivent l’ordre
de production. La chronologie principale règle tous les événements sonores.
Ouverture 0–13,5 s et plans 23–35 s conservés ; montage toujours de 35 s.
Les contrôles courants et l’archive correspondent à cette V12. Les captures
complètes restent dans Git ; le ZIP garde les planches et trois poses finales
de contrôle du nouvel ordre.
