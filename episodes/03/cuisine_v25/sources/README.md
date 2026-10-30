# Reproduire la V25

Film de 43 s, 1032 images à 24 images/s, en 1080 × 1920. Animatique 540 × 960,
12 images/s, 516 images. Aperçu de la fin :35–43 s, 192 images, 8 s.

Production gratuite et open source : Python, SVG, CairoSVG, Pillow, NumPy,
FFmpeg et FluidSynth. La banque FluidR3, les sources de papier, leurs
licences et les polices sont incluses ; aucun service de production payant.

## Commandes depuis la racine

Prérequis : Python 3.12, dépendances de `requirements.txt`, Cairo, FFmpeg
et bibliothèque FluidSynth.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v25/sources/render.py --preview --silent-only --workers 3
.venv/bin/python -B episodes/03/cuisine_v25/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v25/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v25/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v25/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v25/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v25/controle/verify_revision_v25.py --final
.venv/bin/python -B episodes/03/cuisine_v25/sources/package.py
.venv/bin/python -B episodes/03/cuisine_v25/controle/verify_archive_v25.py
```

La critique examine l'animatique réellement produite avant le rendu final.
`--silent-only` permet cette passe sans attacher un ancien mix copié.
Les sources de scène sont gelées pendant le rendu. Le cache est indexé par
le SVG complet ; les contacts du final sont aussi comparés à des rendus frais.

## Animation et contacts

- `performance.py` dirige le jeu corporel et les mains libres. Il prépare
  l'inclinaison cohérente du personnage et résout les prises dans le repère
  inverse de cette inclinaison.
- `jeu_visage.py` dirige les regards et les expressions, avec une pensée
  lisible avant l'action et une exposition des poses importantes.
- `render.py` applique la même transformation au corps, au costume et aux
  bras ; les fragments des pieds sont rendus au sol. Le dessin des membres
  reste celui du rig canonique.
- `animation.py`, `acting.py` et `poses.json` conservent les événements de
  cuisine et la conclusion de 43 s. Les mouvements autorisés peuvent changer
  par rapport à V24 ; la QA ne doit donc pas exiger l'identité des anciens états.

Les cibles des objets tenus, les attaches des bras, les pieds, les masques
des pupilles et les changements de caméra demandent des contrôles distincts.
Un paramètre d'angle différent ne suffit pas à prouver une intention lisible.

## Son et archive

La [recette sonore](../developpement/son_v25.md) décrit les gains fixes,
la partition, les sources utilisées et les textures adaptées. Seuls les
événements de `audio/provenance.json` participent au mix : ne pas sommer
tous les WAV du dossier. L'extrait final reprend les mêmes échantillons
du mix de 35 à 43 s, sans gain supplémentaire.

Les comparaisons historiques de la QA demandent le dépôt complet. Les
dépendances de fabrication sont incluses dans l'archive ; le contrôle froid
charge uniquement son extraction, sans réseau ni cache, et reproduit quatre
images ainsi que le mix. L'audit d'archive est conservé hors du ZIP afin
d'éviter une empreinte circulaire.

[Bilan](../CONTROLE.txt). Aucun jugement d'écoute par le modèle n'est revendiqué.
