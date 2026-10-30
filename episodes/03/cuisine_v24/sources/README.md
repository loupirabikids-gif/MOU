# Reproduire la V24

Durée43s, 1032images à24images/s, 1080 ×1920 ; animatique complète
540 ×960 à12images/s. Fin isolée40,25–43 s :66images, 2,75 s.

Outils gratuits et open source : Python, SVG, CairoSVG, Pillow, NumPy et
FFmpeg. La composition de jazz originale provient de la V23, réalisée avec
FluidSynth et une banque FluidR3 MIT dont la notice reste dans `assets/`.
Le mix V24 réutilise une référence musicale PCM incluse et des sons originaux,
pour se reproduire sans service externe. Voir [la recette sonore](../developpement/son_v24.md).

## Commandes depuis la racine

Prérequis : Python3.12, dépendances de `requirements.txt`, Cairo et FFmpeg.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v24/sources/render.py --preview --silent-only --workers 3
.venv/bin/python -B episodes/03/cuisine_v24/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v24/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v24/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v24/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v24/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v24/controle/verify_revision_v24.py --final
.venv/bin/python -B episodes/03/cuisine_v24/sources/planche_jeu.py
.venv/bin/python -B episodes/03/cuisine_v24/sources/package.py
.venv/bin/python -B episodes/03/cuisine_v24/controle/verify_archive_v24.py
```

Les comparaisons avec l'historique V23 demandent le dépôt complet ; dans
l'archive autonome leur absence doit être indiquée explicitement. Les sources
d'image et de son nécessaires au rendu sont incluses. Le contrôle d'archive
extrait dans un nouveau dossier, bloque les connexions réseau et reproduit
trois rendus frais ainsi que le mix. Son audit est stocké hors du ZIP pour
éviter une empreinte circulaire.

## Paramètres

- `acting.py`, `poses.json` : fin courte, deux plans, corps et bras stables.
- `jeu_visage.py` : regards déchets puis public, transition vers le regret,
  tenue finale ; jeu V23 conservé avant40,25 s.
- `animation.py` : modèle, gestes et chronologie ; fragment facial unique.
- `son.py` : fond musical baissé, bruitages existants et effets ajoutés,
  gain de livraison constant pour préserver la baisse demandée.
- `foley.py` : synthèse déterministe des frictions, froissages et impacts,
  avec leurs instants et les paramètres de matière.
- `render.py` : cache fondé sur le SVG complet, rendu et exports son/muet.
- `verify.py` : flux MP4 et audio, sources gelées, images décodées comparées
  aux rendus CairoSVG frais indépendants du cache.

Ne pas sommer tous les WAV du dossier : seuls les événements indiqués dans
`audio/provenance.json` participent au mix. Les fichiers de référence restent
distincts du résultat et des extraits.

[Bilan](../CONTROLE.txt) · [Revue visuelle](../controle/critique_montage_v24.md).
Aucune écoute par le modèle n'est revendiquée ; les contrôles techniques
ne certifient ni agrément sonore ni reconnaissance publique des émotions.
