# Reproduire V28

Python 3.11 minimum, requirements.txt, Cairo, FFmpeg et FluidSynth.
Les sources, ressources et licences sont incluses ; aucun service payant.
Depuis la racine du dépôt ou de l'archive extraite, après installation :

```sh
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v28/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v28/sources/render.py --preview
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v28/sources/render.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v28/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v28/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v28/sources/package.py
```

La V28 reprend uniquement les cibles des mains après 33,25 s et deux actions
de bouche vers 25,77 et 32,81 s. Les fichiers audio conservent leurs noms V27 :
le WAV, la partition, les cues et leurs positions restent exactement ceux de
V27. son.py les régénère avec les nouveaux états physiques, dont les gestes
d'essuyage sont inchangés. Le cache complet SVG/échelle n'est jamais modifié
en place. Les MP4 sont comparés à des images fraîches hors cache.

L'archive V28 inclut les sources graphiques et les sons, sans MP4 muet de
référence ; render.py reconstruit le film. La banque bibliotheque/sons/v1 est
incluse séparément dans l'arborescence. Son build.py produit douze propositions,
les WAV, le catalogue HTML, l'audition et un ZIP autonome. Aucun nouveau son
de cette banque ne remplace automatiquement la voix de l'épisode.

Les métadonnées d'énergie aident à placer les sons sur des gestes ; elles
ne certifient pas l'audibilité, l'émotion reconnue ou le naturel. Les droits
CC0 sont documentés, avec limites sur l'auteur et la méthode de création.
Les audits des exports et de l'archive restent dans controle/ ; l'audit de
l'archive elle-même est exclu du ZIP pour éviter une empreinte circulaire.
