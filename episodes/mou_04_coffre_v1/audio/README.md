# MOU — bruitages du coffre

Le mix reprend les 18 cues Foley/UI existants, à gains fixes : téléphone,
bouton, couvercle, verrou et quelques accents temporels. Les extraits et
signaux sont fournis avec leurs notices dans `../assets/son/`.

Aucune piste de voix synthétique de PATCH n'est incluse dans ce mix, à la
suite du rejet de ces vocalisations. Les expressions silencieuses restent
animées. Aucun dialogue, musique ou compresseur ; trois stems Foley/UI/ticks.

Le WAV est PCM16 stéréo à 48 kHz, 30 s. Les fichiers `mix_report.json`,
`controls.json`, `cues.json` et `cues.csv` conservent niveaux, placements,
provenance et empreintes. Une analyse numérique ne démontre pas le confort
ou l'effet comique à l'écoute ; aucune audition réelle n'est revendiquée.

Depuis la racine du projet :

```sh
python episodes/mou_04_coffre_v1/sources/son.py --timeline episodes/mou_04_coffre_v1/chronologie.json --output episodes/mou_04_coffre_v1/audio/mix.wav
```
