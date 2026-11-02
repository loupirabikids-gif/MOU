# Bande-son de PATCH — contrat de montage

Le producteur est `../sources/son.py`. La banque et ses origines sont dans
`../assets/son/`, avec les notices CC0 et les empreintes des fichiers source.

Préparation indépendante :

```sh
python sources/son.py --prepare
```

Après gel des contacts et des instants communs, depuis le dossier de l'épisode :

```sh
python sources/son.py --timeline chronologie.json --output audio/mix.wav
```

Le JSON contient `duration` et une liste explicite `audio_cues`, chaque entrée
portant `id`, `sound`, `at` en secondes, et facultativement `gain_db` et `pan`
entre −1 et1. Sons disponibles : `notification`, `tap`, `phone_place`,
`lid_close`, `lock`, `button`, `unlock`, `paper`, `tick` et `end_ping`.

Le rendu produit `mix.wav`, trois stems (`foley`, `ui`, `tick`), `cues.csv`,
`cues.json` et `mix_report.json`. Les pistes sont PCM16 stéréo48kHz.
Les gains restent fixes et explicites ; aucun compresseur ni réglage
automatique par scène ne change l'équilibre. La musique et les voix sont
absentes. La feuille vierge n'a pas de bruit d'écriture.

Les fondus, crêtes et synchronisations peuvent être contrôlés numériquement.
Ils ne remplacent pas une écoute réelle du confort et de la matière des
bruitages. Aucune écoute n'est revendiquée par ce producteur.
