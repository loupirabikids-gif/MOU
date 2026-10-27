# MOU 01 — Le retardateur

Épisode muet dans son écriture, avec ponctuations sonores originales : 14 secondes,
24 images/s, 1080 × 1920, H264 yuv420p et AAC stéréo 48 kHz. Deux versions vidéo :
avec son et sans piste audio. Le rig original reste inchangé.
Révision 3 : chute unique juste avant le clic et tentative finale de sauver
les apparences, puis gêne assumée. Vanité et déformation ample conservées.

Depuis la racine **MOU** du projet décompressé, Python 3.11+ et FFmpeg avec libx264,
Cairo et fontconfig doivent être disponibles. Les dépendances Python exactes sont
consignées dans `requirements-render.lock` ; la police et sa licence sont dans
`fonts/`. Linux vérifié ici, Python 3.12.14 et FFmpeg 7.1.5.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r episodes/01/sources/requirements-render.lock
.venv/bin/python episodes/01/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01/sources/render.py --preview
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01/sources/render.py
.venv/bin/python episodes/01/sources/verify.py
```

Les scripts déterminent leurs chemins depuis leur propre emplacement. Utiliser
le checkout existant : les tâches cloud sont déjà isolées, aucun worktree requis.
Aucun service, compte, clé, API de génération, ressource payante ou accès réseau
n'est nécessaire au rendu après installation.

`animation.py` contient les poses et interpolations ; `render.py` compose le décor,
le même téléphone et ses recadrages, crée la photo fixe à 6,50 s puis encode.
`son.py` synthétise huit effets actifs et le mix ; la détente élastique V2
reste en banque et est explicitement exclue du mix. `verify.py` audite les fichiers
réellement décodés. `../chronologie.json` est le découpage commun de l’équipe.
Les SVG/PNG `photo_capturee` sont calculés par le même modèle à l'instant du clic.

Le cache par contenu dans `episodes/01/cache/` conserve les images non modifiées :
relancer ne recalcule que les contenus ou résolutions différents. Les séquences
PNG et caches sont régénérables et exclus de l'archive de sources. Le script
`--stills --preview` permet d'examiner une planche avant le montage complet.

Le gros plan reste le même téléphone fixe, sans apparition d'un autre appareil.
Les mains ne prennent aucun objet ; aucune marche ni rotation n'est ajoutée.
L'adaptation des paupières dans l'épisode évite les anneaux verts pendant les
fermetures ; la surprise s'ouvre sous le flash, sans modifier le dessin du rig.

Les paramètres `warp_sx`, `warp_sy`, `warp_skew` déforment le torse, les bras
et le visage ensemble. Les deux pieds restent hors de ce groupe et fixes.
MOU se redresse à 1,13 en hauteur, atteint 1,15 en anticipation, puis tombe
une seule fois à 0,68 pour la photo, sans rebond. Le premier extrême se
produit à l’image155, juste avant le flash156. La fin tente une façade
séduisante puis la casse ; la bouche finale reste presque plate. La même déformation
est utilisée dans la scène, l’aperçu et la capture. Le cadrage photo ajuste
sa taille à la silhouette mesurée, sans couper les deux bosses ou les mains.

`package.py` régénère le ZIP des sources et LIVRAISON.json après les exports
et la mise à jour du GIF. Le ZIP exclut caches, séquences PNG, venv et Git.

Les contrôles et limites sont dans `../CONTROLE.txt` et `../controle/`.

Le scénario, le storyboard, l’avis avant fabrication et le journal des décisions
sont conservés dans `../developpement/`. La veille et les profils d’équipe
sont conservés à la racine du projet.
