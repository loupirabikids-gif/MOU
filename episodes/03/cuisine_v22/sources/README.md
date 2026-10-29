# Reproduire et régler la V22

Le film dure **48,25 s**, soit **1 158 images à 24 images/s**, en 1080 × 1920.
L’animatique complète est en 540 × 960 à 12 images/s. Le test de fin utilise
les 192 dernières images du film, en 1080 × 1920, de 40,25 à 48,25 s.

La chaîne conserve Python, SVG, CairoSVG, Pillow, NumPy et FFmpeg. Le rig,
les deux bras/moufles et les inserts du lavabo restent ceux du projet. Le
costume validé est une toque « MOU » et un tablier de taille sans bretelles.
FluidSynth et la banque TimGM6mb servent la partition originale ; leurs
licences et crédits sont dans [assets](../assets/README.md).

## Commandes depuis la racine du dépôt

Prérequis : Python et les dépendances de `requirements.txt`, Cairo, FFmpeg,
la bibliothèque FluidSynth et les polices/banques incluses. Si nécessaire,
créer l’environnement avec `python3 -m venv .venv`, puis installer les
dépendances avec `.venv/bin/python -m pip install -r requirements.txt`.

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v22/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v22/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v22/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v22/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v22/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v22/controle/verify_revision_v22.py
.venv/bin/python -B episodes/03/cuisine_v22/sources/package.py
```

`test_scene.py --silent-only` permet de rendre la fin sans lire l’audio.
Les images de contrôle sont décodées du MP4 réellement exporté. Le cache
n’est réutilisé que si le SVG complet, sa version et son échelle correspondent.
Les empreintes des sources sont figées pendant le rendu ; une modification
en cours de fabrication provoque un échec plutôt qu’un film hybride.

## Modifier le jeu et les plans

- [poses.json](poses.json) contient les poses et repères du jeu final.
- [acting.py](acting.py) organise leurs transitions, regards, contacts et
  tenues sur la grille de 192 images. Le corps garde une transformation fixe.
- [animation.py](animation.py) conserve les actions de cuisine et raccorde
  ce jeu final au film. Les temps qui tombent sur la grille sont arrondis
  avec une tolérance de 1e−8 image pour éviter une coupe décalée d’une image.
- [render.py](render.py) fixe les cadrages et compose le détail main/tablier
  sans îlot ni visage. Le cadre change sans relever le personnage.
- [chronologie.json](../chronologie.json), section `professional_ending`,
  conserve les six plans et le contact tissu de 43,75 à 44,583333 s.

Les cinq temps narratifs sont : manque de papier, découverte d’une solution,
essuyage sur le tablier, constat du gaspillage, puis réaction au public. Le
constat se répartit entre un large orientant le regard et un plan de poubelle.
La pose finale reste fixe pendant les seize dernières images, soit environ
deux tiers de seconde. Les durées sont des choix pour cet essai, pas des
normes garantissant une émotion lisible.

## Refaire le son

[son.py](son.py) conserve les banques brutes puis fabrique les couches
traitées et leur somme. Seuls les événements de `audio/provenance.json`
entrent dans le mix : ne pas sommer tous les WAV du dossier, qui contient
aussi des originaux et des références historiques.

Le mix V22 utilise 41 événements actifs, dont 39 de premier plan et deux fonds,
avec 25 couches retirées.
Il garde une seule eau, adoucit papier/couteau et réduit le sifflement initial.
La musique à 108 BPM suit une grille globale continue, avec une baisse de
1,5 dB au lavage et des transitions progressives. Un gain final unique de
+5,13 dB s’applique au film entier ; aucun réglage de loudness par scène.
Le test sonore de huit secondes est extrait du même PCM final, sans gain
supplémentaire. Lire la [recette et les mesures](../developpement/son_v22.md).

La régénération sonore a reproduit le mix octet pour octet. Les contrôles
finaux du MP4 et la critique artistique sont documentés séparément dans
[controle](../controle/) et [CONTROLE.txt](../CONTROLE.txt). Les mesures
audio ne remplacent pas une écoute ; aucune écoute par le modèle ni
certification de confort n’est revendiquée.
