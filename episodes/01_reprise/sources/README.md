# Refaire Le retardateur

Nouvelle réalisation du gag initial, dans un dossier distinct des anciens
montages : 13 secondes, 24 images/s, vertical1080×1920. Le personnage et le
rig fournis restent la référence. La nouvelle scène, le jeu et le son sont
reproductibles avec les outils libres déjà retenus.

Depuis la racine MOU, avec Python3.11+, Cairo/fontconfig et FFmpeg/libx264 :

```bash
bash episodes/01_reprise/sources/install.sh
.venv/bin/python episodes/01_reprise/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01_reprise/sources/render.py --preview
# Examiner et corriger le vrai montage avant le final.
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01_reprise/sources/render.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/01_reprise/sources/verify.py
```

Les chemins sont calculés depuis chaque script, indépendamment du dossier
courant. Les versions Python sont fixées dans `requirements-render.lock`.
Après installation, le rendu ne nécessite aucun service, compte ni réseau.

`animation.py` adapte le modèle `../../../mou_rig.py` sans le modifier :
poses paramétriques, bras originaux sans remplacement de leur dessin, déformation commune au
corps/visage/bras, deux pieds fixes. `character_at(pose_at(6.0))` fournit
exactement la pose du cliché. Lire `poses.md` pour les paramètres et essais.

`render.py` reconstruit la mise en scène : activation du téléphone, vue depuis
l’objectif, compteur5→1 strictement régulier, affaissement pendantle1 et flash6s.
Aucun portrait n’apparaît avant le clic. Le résultat est montré en gros plan
fixe du même écran6,75–8,75s ; la photo est rasterisée2× pour garder ses contours.
La signature de l’épisode reste « Le retardateur ».

`son.py` produit7effets originaux : appui0,90, éclat2,20, bips3/4/5, souffle
5,20–5,40 et déclencheur6s. Silence5,5–6 et pendant la lecture de la photo.
Aucune voix ni musique ; graines, paramètres et audits dans `../sons/`.
Le contrôle numérique ne vaut pas écoute sur appareil réel.

`verify.py` décode les deux MP4, vérifie dimensions/durée/audio, synchronisation,
photo figée et gestes comparés à des SVG frais hors cache. Le cache par contenu
emploie des écritures et copies atomiques, sans liens physiques partagés.
`render.py --preview --stills` produit15images et une planche de contrôle.

Après le final, régénérer l’aperçu et l’archive :

```bash
ffmpeg -y -i episodes/01_reprise/MOU_le_retardateur_nouveau_muet.mp4 -filter_complex "fps=10,scale=270:480:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 episodes/01_reprise/MOU_le_retardateur_apercu.gif
.venv/bin/python episodes/01_reprise/sources/package.py
```

Le ZIP contient cette fabrication, les références et les règles communes ;
il exclut venv, cache, séquences PNG, Git et anciens montages de episodes/01.
Les sources et commandes sont testées avant livraison, avec leur portée dans
`../CONTROLE.txt` et `../controle/`. Les fichiers antérieurs restent dans le dépôt.

Révision2 : bras du rig original restaurés àla demande de l’utilisatrice.
Les poses, expressions, timings, son et cadrage photo sont conservés.
