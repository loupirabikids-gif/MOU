# Reproduire la V21 — jeu des émotions et découverte du tablier

Le costume SVG de `costume.py` reprend exactement l’étude chef_v1 validée :
toque crème marquée « MOU », tablier corail de taille sans bretelles.
Le calque suit le corps, sous les deux bras d’origine. Le nom est une petite
image transparente issue de la police Nunito fournie, intégrée dans le SVG.

La chronologie dure 44,5 secondes. La trajectoire de débordement V20 reste
identique : impact sur le tas à 39,1 s, chute au sol vers 39,85 s, gros plan
jusqu’à 40,25 s. Puis : goutte sur la moufle, tube vide, regard de découverte
vers le tablier, essuyage, regard au gaspillage et sourire gêné face au public.
Les quatre grandes boulettes restent dans la poubelle ; la cinquième au sol.

Depuis la racine du dépôt avec Python/dépendances du projet et FFmpeg :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v21/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v21/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v21/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v21/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v21/controle/verify_revision_v21.py
.venv/bin/python -B episodes/03/cuisine_v21/controle/build_proofs.py
.venv/bin/python -B episodes/03/cuisine_v21/sources/package.py
```

Le rendu sonore garde les entrées PCM et la partition précédentes, prolonge
la même musique sur son horloge globale, et ajoute une friction de tissu
au geste d’essuyage. Les paramètres et les preuves d’identité de l’ancien
passage sont dans developpement/son_v21.md et controle/audit_audio_v21.json.
Le montage encode le WAV courant en AAC et partage le même flux H264 avec
le muet. Le modèle ne revendique aucune écoute auditive.

Cache : seuls les PNG dont la clé contient exactement le SVG complet, la
version et l’échelle peuvent être réutilisés. Les nouvelles expressions et
la clôture changent les clés ; les inserts du lavabo restent identiques.
Les gestes et la chute
du MP4 sont comparés à des rendus frais hors cache après export.

Format final : 1080 × 1920 à 24 images/s ; animatique complète : 540 × 960
à 12 images/s. Police Nunito sous SIL OFL 1.1, FluidSynth/TimGM6mb crédités
dans assets/. Aucun service payant ni outil de génération à crédits.
