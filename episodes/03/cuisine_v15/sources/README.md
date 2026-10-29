# Reproduire la révision musicale V15

Python et dépendances fixées dans `requirements.txt`, FFmpeg, Cairo et
**libfluidsynth** nécessaires. La banque libre TimGM6mb est incluse dans
`../assets/`, avec ses crédits et licences ; aucun téléchargement d’instrument
n’est nécessaire. FluidSynth 2.4.4 est installé dans l’environnement cloud.
Sous Debian/Ubuntu, la bibliothèque est fournie par `libfluidsynth3`.

Depuis la racine du dépôt complet, pour garder exactement les images V14 :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v15/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v15/sources/mux.py
.venv/bin/python -B episodes/03/cuisine_v15/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v15/controle/audit_audio_v15.py --final
.venv/bin/python -B episodes/03/cuisine_v15/sources/package.py
```

`mux.py` copie les flux H.264 V14 vérifiés et remplace seulement l’audio.
La version muette est identique à l’octet près. Les commandes comparatives
ont besoin de V14 dans le checkout complet.

Pour refaire le film depuis l’archive autonome, sans V14 ni anciens MP4 :

```sh
.venv/bin/python -B episodes/03/cuisine_v15/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v15/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v15/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v15/sources/verify.py
```

Le rendu des images est conservé : animation, accessoires, lavabo et moufle
au pouce arrondi restent ceux de V14. `render.py` conserve donc aussi son
identifiant de cache V14 ; le cache dépend toujours du SVG complet et de
l’échelle. Aucun changement d’image n’est nécessaire pour améliorer la musique.

- `music.py` : partition originale, quatre familles d’instruments et rendu
  local FluidSynth sans serveur sonore ; métadonnées des notes et instruments.
- `son.py` : bruitages/sifflement conservés, remplacement de la musique,
  mix et audit de provenance.
- `mux.py` : remplacement de la piste sonore avec copie des images.
- `verify.py` : décodage complet et comparaisons hors cache des images,
  concordance AAC/WAV et contrôle des dépendances gelées.
- `package.py` : archive des sources, sons, instruments libres, licences,
  contrôles et manifeste SHA-256. `audit_archive.json` est exclu de son propre ZIP.

Format final : 41 s, 1080 × 1920, 24 images/s, H.264/yuv420p et AAC stéréo
48 kHz. L’animatique conserve 540 × 960 à 12 images/s. Les vérifications de
niveaux et de silences ne sont pas une écoute perceptive du mix.
