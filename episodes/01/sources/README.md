# MOU 01 — La dernière retouche (V5)

13 secondes, 24 images/s, vertical 1080 × 1920. MP4 H264/yuv420p,
AAC stéréo 48 kHz et version sans piste audio. Les noms historiques
`MOU_01_le_retardateur*.mp4` sont conservés pour les liens déjà partagés.
Le scénario courant est dans `../developpement/scenario_retenu.md` ;
PILOTE_01.txt reste le point de départ historique, remplacé par la réécriture approuvée.

Depuis la racine MOU, Python 3.11+, Cairo/fontconfig et FFmpeg avec libx264 :

```bash
bash episodes/01/sources/install.sh
.venv/bin/python episodes/01/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01/sources/render.py --preview
# Examiner le montage complet et corriger avant le rendu final.
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01/sources/render.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01/sources/verify.py
.venv/bin/python episodes/01/sources/package.py
```

Versions Python fixées dans `requirements-render.lock`. Aucun service, clé,
ressource payante ou réseau n'est nécessaire au rendu après installation.
Les chemins dépendent de l'emplacement des sources, pas du dossier courant.
Les profils d'équipe sont appliqués par délégations bornées ; leur présence
ne prouve pas leur activation native dans un client Codex donné.

`animation.py` adapte le rig original inchangé : mêmes rubans continus et
mitaines, nouvelles cibles de joues, contour et sourire entraînés après contact.
`contact_geometry(p)` expose les repères locaux des deux bras et joues ;
`character_at()` est l'unique source du personnage animé et du cliché.
Les pieds restent fixes. La dernière traction continue jusqu'à l'image154 ;
le résultat est calculé exactement à154/24 s, puis figé. Les deux yeux restent
masqués comme dans le modèle. Lire `poses.md` pour les paramètres de jeu.

`render.py` compose l'insert d'activation (une mitaine recoupée par le cadre),
la vue depuis l'objectif, le flash puis le résultat dans le même téléphone.
Aucun portrait n'est affiché avant le clic. Le résultat7–8,8s est montré
en gros plan fixe×1,4 du même téléphone, après critique du premier montage. Le premier contact bouton utilise
le même échantillonnage de ruban que le rig, avec la racine hors cadre.
Les SVG/PNG `photo_capturee` partagent strictement la pose du clic.

`son.py` synthétise sept événements originaux et un mix13s à partir de graines
fixes : trois bips identiques, deux frottements, clic et descente des mains.
La pause avant clic et la lecture de la photo restent silencieuses. Les WAV
historiques ne sont pas utilisés ; le manifeste distingue banque et mix actif.
`verify.py` décode les deux fichiers livrés, vérifie format/audio/clic/photo fixe
et compare les moments décisifs à des SVG fraîchement rasterisés hors cache.

Le cache par contenu n'utilise pas de liens physiques : écritures et copies
atomiques, comparaison de chaque destination et de sa clé avant encodage.
`--stills --preview` rend une planche de contrôle ; `--preview` produit le montage
léger complet. Les PNG/cache/venv/Git sont exclus du ZIP généré par `package.py`.
Pour régénérer aussi l'aperçu GitHub après le final :

```bash
ffmpeg -y -i episodes/01/MOU_01_le_retardateur_muet.mp4 -filter_complex "fps=10,scale=270:480:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 episodes/01/MOU_01_apercu.gif
.venv/bin/python episodes/01/sources/package.py
```

Contrôles, critique réelle et limites : `../CONTROLE.txt`, `../controle/`.
Scénario, storyboard, critique avant fabrication et décisions : `../developpement/`.
La veille externe demeure incomplète ; aucune mesure d'audience n'est inventée.


Correction graphique V5 : dans la réaction finale, les attaches suivent les
flancs et les avant-bras sont plus courts. Les mains passent de389à366 en
hauteur locale ; le bras droit part de316/301 plutôt que297/291. Le même
constructeur de contour arrondi reste actif pendant la descente et la pose
ventrale, évitant un changement de dessin à10,7s. Le rig original reste intact.
Les cadrages sont conservés ; le cliché PNG et le mix WAV sont byte-identiques
àceux de la V4.
La revue dense et les preuves sont dans `../controle/critique_bras_v5.md`.
