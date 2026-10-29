# Reproduire la V20 — costume de chef et papier au sol

Le costume SVG de `costume.py` reprend exactement l’étude chef_v1 validée :
toque crème marquée « MOU », tablier corail de taille sans bretelles.
Le calque suit le corps, sous les deux bras d’origine. Le nom est une petite
image transparente issue de la police Nunito fournie, intégrée dans le SVG.

La chronologie conserve 41 secondes et ajoute la trajectoire de débordement :
impact sur le tas à 39,1 s, chute au sol vers 39,85 s, stabilisation à 40 s,
gros plan tenu jusqu’à 40,25 s puis plan large final. Les quatre grandes
boulettes restent dans la poubelle ; la cinquième reste au sol.

Depuis la racine du dépôt avec Python/dépendances du projet et FFmpeg :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v20/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v20/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v20/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v20/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v20/controle/verify_revision_v20.py
.venv/bin/python -B episodes/03/cuisine_v20/sources/package.py
```

Le rendu sonore V20 conserve un mix V19 figé fourni dans audio/, auquel est
ajouté uniquement le bref contact au sol. Aucune recomposition, variation
de niveau musical ou normalisation supplémentaire. Les sources originales
de synthèse, les stems, les banques et leurs licences restent inclus.
Le montage encode ce WAV en AAC et partage le même flux H264 avec le muet.

Cache : seuls les PNG dont la clé contient exactement le SVG complet, la
version et l’échelle peuvent être réutilisés. Le costume modifie les images
larges ; les inserts du lavabo restent identiques. Les gestes et la chute
du MP4 sont comparés à des rendus frais hors cache après export.

Format final : 1080 × 1920 à 24 images/s ; animatique complète : 540 × 960
à 12 images/s. Police Nunito sous SIL OFL 1.1, FluidSynth/TimGM6mb crédités
dans assets/. Aucun service payant ni outil de génération à crédits.
