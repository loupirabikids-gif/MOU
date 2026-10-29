# Reproduire la révision du mix V18

Python et dépendances fixées dans `requirements.txt`, FFmpeg, Cairo et
**libfluidsynth** nécessaires. La banque libre TimGM6mb est incluse dans
`../assets/`, avec ses crédits et licences ; aucun téléchargement d’instrument
n’est nécessaire. FluidSynth 2.4.4 est installé dans l’environnement cloud.
Sous Debian/Ubuntu, la bibliothèque est fournie par `libfluidsynth3`.

Depuis la racine du dépôt complet, pour garder exactement les images V17 :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v18/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v18/sources/mux.py
.venv/bin/python -B episodes/03/cuisine_v18/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v18/controle/audit_mix_v18.py --final
.venv/bin/python -B episodes/03/cuisine_v18/sources/package.py
```

`mux.py` copie les flux H.264 V17 vérifiés et remplace seulement l’audio.
La version muette est identique à l’octet près. Les commandes comparatives
ont besoin de V17 dans le checkout complet.

Pour refaire le film depuis l’archive autonome, sans V17 ni anciens MP4 :

```sh
.venv/bin/python -B episodes/03/cuisine_v18/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v18/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v18/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v18/sources/verify.py
```

Le rendu des images est conservé : animation, accessoires, lavabo et moufle
au pouce arrondi restent ceux de V17. `render.py` conserve donc aussi son
identifiant de cache V14 ; le cache dépend toujours du SVG complet et de
l’échelle. Aucun changement d’image n’est nécessaire pour améliorer la musique.

- `music.py` : partition continue, quatre parties instrumentales, enveloppe de volume et rendu
  local FluidSynth sans serveur sonore ; métadonnées des notes et instruments.
- `son.py` : bruitages/sifflement conservés, remplacement de la musique,
  mix, baisse douce au lavabo et audit de provenance.
- `mux.py` : remplacement de la piste sonore avec copie des images.
- `verify.py` : décodage complet et comparaisons hors cache des images,
  concordance AAC/WAV et contrôle des dépendances gelées.
- `package.py` : archive des sources, sons, instruments libres, licences,
  contrôles et manifeste SHA-256. `audit_archive.json` est exclu de son propre ZIP.

Format final : 41 s, 1080 × 1920, 24 images/s, H.264/yuv420p et AAC stéréo
48 kHz. L’animatique conserve 540 × 960 à 12 images/s. Les vérifications de
niveaux et de silences ne sont pas une écoute perceptive du mix.

La V18 compose une partition à partir de la durée et du tempo uniquement.
Les anciennes fenêtres et les intervalles de lavabo ne modifient aucune note.
Le volume peut descendre de 1,5 dB au lavabo avec rampes de 500/700 ms ;
la référence `musique_sans_baisse.wav` permet de vérifier ce seul traitement.
Les régressions mesurent aussi les creux sur 100/200 ms et la grille musicale.

V18 conserve la partition et les banques de sons V17. `son.py` applique
MIX_GAIN_DB au mix seulement : eau −9 dB, frottement mouillé −7 dB, papier
à −2/−3/−5 dB selon le geste. La musique baisse de 1,5 dB au lavabo.
Chaque événement indique son mix_gain_db dans audio/provenance.json.
Les fichiers de banque ne comprennent pas ces gains, qui changent
volontairement le niveau des bruitages dans le mix final.
