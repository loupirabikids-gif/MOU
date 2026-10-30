# Reproduire et régler la V23

Le film conserve **48,25 s**, soit **1 158 images à 24 images/s**, en
1080 × 1920. L'animatique complète est en 540 × 960 à 12 images/s.
L'extrait final de huit secondes correspond à 40,25–48,25 s, soit 192 images.

Python, SVG, CairoSVG, Pillow, NumPy et FFmpeg fabriquent l'image. FluidSynth
rend la nouvelle partition originale avec une banque d'instruments libre
incluse : [FluidR3_MOU_trio.sf2](../assets/FluidR3_MOU_trio.sf2?raw=true),
sous-ensemble MIT de 4,05 Mo. La [notice et la procédure de sélection](../assets/FluidR3_README.md)
renvoient au paquet Debian vérifié et au script `subset_soundfont.py`.
La banque réduite incluse suffit à rejouer la partition ; reconstruire le
sous-ensemble n'est nécessaire que pour changer sa sélection de notes.
Le modèle, les deux bras/moufles, le costume validé et les contacts des
accessoires restent les références de la V22.

## Commandes depuis la racine du dépôt

Prérequis : Python, les dépendances de `requirements.txt`, Cairo, FFmpeg,
la bibliothèque FluidSynth et les polices/banques incluses. Si nécessaire :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

La première passe visuelle peut être produite pendant la préparation du son.
Après critique et corrections retenues, rendre le mix, l'animatique avec son
et le final :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v23/sources/render.py --preview --silent-only --workers 3
.venv/bin/python -B episodes/03/cuisine_v23/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v23/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v23/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v23/sources/test_scene.py
.venv/bin/python -B episodes/03/cuisine_v23/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v23/controle/verify_revision_v23.py --final
.venv/bin/python -B episodes/03/cuisine_v23/sources/package.py
```

`--silent-only` ignore volontairement le WAV présent : cela évite d'attacher
un ancien mix à une nouvelle passe visuelle. `test_scene.py --silent-only`
permet aussi un test muet isolé de la clôture.

Le cache est indexé par le SVG complet, sa version et son échelle. Les sources
sont figées pendant le rendu et une modification concurrente provoque un échec.
Les contrôles du final comparent aussi des images décodées du vrai MP4 à des
rendus frais hors cache ; un cache réutilisé ne suffit pas à vérifier le film.

## Où régler le jeu

- [animation.py](animation.py) conserve la chronologie et les états physiques
  de cuisine puis raccorde le contrôleur facial au personnage existant.
- [jeu_visage.py](jeu_visage.py) choisit les poses selon les cinq moments du
  récit, dirige le regard vers les objets réels et règle l'exposition des poses.
- [visage.py](visage.py) est la copie gelée de l'adaptateur de bibliothèque :
  neuf formes de bouche, sourcils, paupières et pupilles. Les transitions
  interpolent un seul contour et un seul masque de bouche.
- [expressions.json](expressions.json) est le catalogue de 36 poses gelé pour
  cet épisode. Une évolution ultérieure de la bibliothèque ne le remplace pas
  automatiquement.
- [acting.py](acting.py) et [poses.json](poses.json) conservent les actions,
  regards de référence et plans de la fin sur la grille de 192 images.
- [render.py](render.py) compose les cadres, dont le détail main/tablier sans
  visage ni îlot. [chronologie.json](../chronologie.json) garde les instants
  des gestes, des plans et des événements sonores.

Le contrôleur remplace **le groupe visage**, pas le SVG de personnage complet.
Les deux bras ne sont donc ni redessinés ni ajoutés une seconde fois.
Leurs raccords, la prise du papier, la cuillère, le couteau, le sel et la moufle
du lavabo demandent toujours des contrôles de contact dans les images réelles.

Pour la première inspection, le regard rejoint la main avant le doute ; il
rejoint ensuite le lavabo avant la coupe. Pour le petit papier, l'objet devient
visible avant la surprise. La clôture garde l'insert de tissu, celui des déchets
et le retour au public, avec une dernière pose tenue. La [direction détaillée](../developpement/direction_v23.md)
et la [critique](../controle/critique_montage_v23.md) complètent les paramètres.

## Refaire le son

[son.py](son.py) construit le mix depuis les événements et la partition
originale, puis écrit `audio/mix.wav`. [music.py](music.py) garde une seule
grille musicale pour le film entier ; les coupes de caméra ne découpent pas
les notes. Le tempo retenu est 108 BPM, en la majeur, avec un jeu en deux temps
et une coda. Il garde la grille du balancement et des notes sifflées existants. L'harmonie
A6/9 de l'ouverture accompagne les trois notes sifflées A5–C#6–B5, dont les
instants sont conservés. Le début utilise un accord lié et la basse avant
l'installation du motif rythmique. Le dosage des lavages utilise des transitions
progressives, sans reprise ni normalisation indépendante de chaque scène.

Seuls les fichiers listés dans `audio/provenance.json` participent au mix :
ne pas sommer tous les WAV du dossier. La [recette V23](../developpement/son_v23.md)
décrit les stems, la banque, les gains et les traitements effectivement retenus.
L'extrait de fin doit reprendre exactement les mêmes échantillons du mix,
sans normalisation supplémentaire. `audio/jazz_seul_15s.wav` et sa copie MP3
permettent d'écouter la nouvelle musique sans bruitages ; l'extrait utilise le
même gain que le fond musical du film. `jazz_seul_complet.wav` couvre la durée
entière. La partition est fournie en JSON et MIDI, avec les quatre stems
`jazz_basse_v23.wav`, `jazz_accords_v23.wav`, `jazz_melodie_v23.wav` et
`jazz_balais_v23.wav` : les accords et la mélodie emploient le même piano.

Les contrôles techniques du final et le contrôle indépendant sont passés.
Leur bilan est séparé dans
[CONTROLE.txt](../CONTROLE.txt), [audit final](../controle/audit_final.json)
et [audit indépendant](../controle/audit_revision_v23.json). Les chiffres de
niveau, la reproductibilité ou un export H264 valide ne certifient pas le
confort d'écoute ni la compréhension du gag. Aucune écoute du mix par le
modèle n'est revendiquée. Après l'emballage, le contrôle de l'archive extrait
les sources dans un nouveau dossier et reproduit des images et le mix sans
réseau ni cache :

```sh
.venv/bin/python -B episodes/03/cuisine_v23/controle/verify_archive_v23.py
```

`controle/audit_archive.json` reste à côté du ZIP et est exclu de son contenu
pour éviter une dépendance circulaire de son empreinte.
