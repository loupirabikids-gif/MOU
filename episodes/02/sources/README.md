# Reproduire Le torchon

Fabrication autorisée par le « Vas y » du 28 octobre 2026.
Cible : 12 secondes, 24 images/s, vertical 1080 × 1920, avec son et version muette.
Les contrôles réellement effectués et leurs limites figurent dans ../CONTROLE.txt.

Depuis la racine MOU, avec Python 3.11+, Cairo/fontconfig et FFmpeg/libx264 :

```bash
bash episodes/02/sources/install.sh
.venv/bin/python episodes/02/sources/son.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/02/sources/render.py --preview
# Examiner et corriger le vrai montage léger avant le final.
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/02/sources/render.py
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/02/sources/verify.py
```

Les versions Python sont fixées dans requirements-render.lock. Le script
d’installation vérifie FFmpeg/ffprobe et les imports ; Cairo et fontconfig
doivent être disponibles. Après installation, la fabrication utilise les
fichiers locaux sans service, compte ou API de production.

Les chemins sont résolus depuis les scripts. Le rendu retrouve la racine
contenant mou_rig.py ; les outils d’archive emploient la structure
MOU/episodes/02/sources/. Préserver cette structure avec rig, polices et
références lors de l’extraction du ZIP.

## Sources et vérifications

- animation.py décrit poses, contacts et torchon SVG original. Le rig partagé
  reste inchangé ; les tracés _arm canoniques sont conservés. Les rotations
  éventuelles sont des groupes autour des épaules, avec deux bras et deux
  moufles. Les raccords ont été examinés dans les études de contact et le vrai MP4,
  avec leur portée dans ../controle/.
- render.py compose la scène et réutilise CairoSVG/FFmpeg, avec cache par
  contenu et écritures/copies atomiques, sans PNG liés modifiés en place.
- son.py synthétise six sons de tissu originaux et un mix WAV stéréo 48 kHz.
  Graines, paramètres et provenance sont dans ../sons/. Aucune voix ni musique.
  Les événements et trois silences viennent de ../chronologie.json.
- verify.py décode les MP4 réellement encodés et contrôle format, durée, sons,
  silences, synchronisation et gestes comparés à des SVG frais. Ces mesures
  ne remplacent pas la critique ni une écoute.
- package.py prépare l’archive de cet épisode et ../LIVRAISON.json.

Tester prises, appui et trajet du tissu avant validation du montage complet.
Le scénario initial est conservé ; découpage de production, storyboard et
corrections sont dans ../developpement/, critiques réelles dans ../controle/.

## Aperçu et archive

Après correction, export et contrôle du final :

```bash
ffmpeg -y -v error -threads 2 -i episodes/02/MOU_02_le_torchon_muet.mp4 -filter_complex_threads 2 -filter_complex "fps=10,scale=270:480:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 episodes/02/MOU_02_le_torchon_apercu.gif
.venv/bin/python episodes/02/sources/package.py
```

Aperçu attendu : muet, 270 × 480, 10 images/s, durée de 12 secondes.
Le ZIP autonome conserve la racine MOU/ et inclut sources, sons, contrôles,
rig, polices, références et test de construction original. Il exclut Git,
venv, cache, séquences PNG et anciens épisodes. Les MP4 sont fournis séparément.

La reproduction du ZIP extrait doit être consignée selon sa portée réelle ;
ne pas revendiquer de machine vierge non testée. Les contrôles numériques
ne valent pas écoute humaine sur téléphone ni test public. La veille externe
reste incomplète, documentée dans le développement. Une livraison GitHub
n’est ni une publication de Short ni une mesure de son audience.
