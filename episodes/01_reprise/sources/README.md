# Reproduire Le retardateur — fin révisée

13 secondes, 24 images/s, vertical 1080 × 1920. Le modèle et le rig fournis
restent la référence ; le dessin des deux bras est conservé. La révision 3
modifie le visage capturé et la réaction finale, avec des sources locales
reproductibles et les mêmes outils libres.

Depuis la racine MOU, avec Python 3.11+, Cairo/fontconfig et FFmpeg/libx264 :

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
poses paramétriques, groupes `_arm` canoniques sans remplacement de leur dessin,
déformation commune au corps/visage/bras, deux pieds fixes. Les pupilles
convergent indépendamment ; le regard vertical commun indique le résultat
puis le spectateur. Le sourire nerveux est légèrement oblique. Les deux
minuscules secousses gardent les pieds au sol.
`character_at(pose_at(6.0))` fournit exactement la pose du cliché.
Lire `poses.md` pour les paramètres et essais.

`render.py` conserve l’activation du téléphone, la vue depuis l’objectif,
le compteur 5→1 régulier et le flash à 6 s. Aucun portrait avant le clic.
La capture tient cinq images ; la photo reste immobile dans le même écran
agrandi de 6,75 à 8 s (1,25 s). Elle est rasterisée 2× pour garder ses contours.
La dernière pose tient sans mouvement de 12,5 à 13 s.

`son.py` produit neuf événements originaux : appui à 0,90 s, éclat à 2,20 s,
bips à 3/4/5 s, souffle de 5,20 à 5,40 s, déclencheur à 6 s, puis deux petits
hé soufflés à 277/24 et 287/24 s, chacun de 0,25 s. Les hé sont synthétisés
localement par Python/NumPy, sans voix humaine enregistrée ni service vocal.
Silence avant le flash, pendant la photo et sur la dernière demi-seconde.
Aucune musique ; graines, paramètres et audits dans `../sons/`.
Le contrôle numérique ne vaut pas écoute sur appareil réel.

`verify.py` contrôle les MP4 exportés, leur format, durée et audio,
la synchronisation, la photo figée et la conformité des gestes à des SVG frais
hors cache. Les résultats effectifs et leur portée se trouvent dans
`../CONTROLE.txt` et `../controle/`. Le cache par contenu emploie des écritures
et copies atomiques, sans liens physiques partagés.
`render.py --preview --stills` produit les images et une planche de contrôle.

Après le final, régénérer l’aperçu et l’archive :

```bash
ffmpeg -y -v error -threads 2 -i episodes/01_reprise/MOU_le_retardateur_nouveau_muet.mp4 -filter_complex_threads 2 -filter_complex "fps=10,scale=270:480:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 episodes/01_reprise/MOU_le_retardateur_apercu.gif
.venv/bin/python episodes/01_reprise/sources/package.py
```

Le ZIP contient cette fabrication, les références et les règles communes ;
il exclut venv, cache, séquences PNG, Git et anciens montages de `episodes/01/`.
Les anciennes critiques et décisions restent consultables dans le dossier de
l’épisode ; les nouveaux avis sont reliés depuis son README.
