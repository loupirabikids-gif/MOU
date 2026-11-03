# Bande-son — PATCH V5, correctif des bras et de l’attente

Le film représente trente minutes dans trente secondes. Les points
de vue, la pose de corps entier et les prises à deux mains restent lisibles
sans ajouter de musique, de voix ou d'effets systématiques aux gestes.
La vidéo de référence et sa piste sonore ne sont pas réutilisées.

La banque incluse est identique à la V3 : extraits CC0 documentés, petits
signaux UI originaux et accent d'ellipse déjà construit. Le producteur
`../sources/son.py` charge et vérifie cette banque sans la réécrire. Les
origines, notices et empreintes sont conservées dans `../assets/son/`.

Le contrat reste une chronologie explicite : `duration` et `audio_cues`,
chaque cue ayant `id`, `sound`, `at`, `gain_db` et `pan`. Les dix-huit cues
existants suivent les contacts préservés : notification, téléphone, coffre,
crayon posé et quelques repères temporels. Les gains restent fixes ; aucun
compresseur ne modifie l'équilibre d'une scène à l'autre.

Aucun bruit d'écriture n'accompagne les cases restées vides. Aucun impact
de réception n'accompagne une pose en l'air coupée avant la réception.
Les derniers gestes et le résultat peuvent se lire dans le calme.

Après gel de la chronologie par le coordinateur, depuis le dossier épisode :

```sh
python sources/son.py --timeline chronologie.json --output audio/mix.wav
```

Le rendu produit `mix.wav`, les trois stems `foley`, `ui`, `tick`, les cues
CSV/JSON et `mix_report.json`, en PCM16 stéréo à 48 kHz. `--prepare` permet
de reconstruire explicitement la banque depuis les origines incluses ; il
n'est pas nécessaire au rendu du mix et n'est pas lancé pour cette révision.

## Rendu gelé V5

Le rendu utilise la chronologie V5 gelée : 30 s exactes, 18 événements,
PCM16 stéréo 48 kHz, sans échantillon écrêté. Les trois stems recomposent
exactement le PCM du mix. Le pic mesuré est de −19,81 dBFS ; les derniers
échantillons non nuls sont vers 24,1505 s, puis la fin garde environ5,85 s
calmes pour lire la joie, la feuille et l'absorption finale.

Les cues, gains et instants étant inchangés, le WAV est identique à celui
de la V4 corrigée. Les métadonnées pointent vers la nouvelle chronologie, dont
l'empreinte est conservée dans `mix_report.json` et `controls.json`.
Les22fichiers de banque et de provenance restent identiques. Aucun effet
de réception, nouvelle musique ou vocalisation n'a été ajouté.

Aucune audition de la référence ou du mix n'est revendiquée. Les contrôles
de niveaux, stems et synchronisation ne certifient ni reconnaissance de
matière sonore, ni confort d'écoute, ni effet comique.
