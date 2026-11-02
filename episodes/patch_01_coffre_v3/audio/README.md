# Bande-son — reconstruction PATCH V3

Le coffre représente trente minutes dans une vidéo de trente secondes.
La reconstruction visuelle reprend les intentions d'attente et de joie de
la référence fournie, sans réutiliser son MP4 ou sa piste audio dans le film.
Aucune audition de cette référence ni du mix n'est revendiquée.

La banque incluse est identique à celle de la V2 : extraits CC0 documentés,
signaux UI originaux et court accent d'ellipse déjà construit. Les origines,
licences et empreintes sont conservées dans `../assets/son/`.

Le producteur `../sources/son.py` vérifie les originaux et chaque effet avant
le rendu. Il charge la banque fournie ; il ne réécrit pas les actifs. La
commande `--prepare` reste disponible pour reconstruire explicitement cette
banque à partir des sources incluses, mais n'est pas nécessaire au mix.

Depuis le dossier de l'épisode, après gel des contacts communs :

```sh
python sources/son.py --timeline chronologie.json --output audio/mix.wav
```

Le mix suit les cues explicites de `chronologie.json`. Les gains sont fixes ;
aucun compresseur ou équilibrage automatique ne change le niveau d'une scène
à l'autre. Les sons correspondent au téléphone, au coffre, au crayon posé et
à quelques repères d'ellipse. Aucun bruit d'écriture n'accompagne une liste
restée vide. Les nouveaux gestes d'attente et de joie n'ajoutent pas d'effet
artificiel systématique ; ils peuvent se lire dans le silence.

Aucune musique ni voix n'est ajoutée. Les pistes sont PCM16 stéréo à 48 kHz ;
le producteur fournit le mix, les stems (`foley`, `ui`, `tick`), la liste des
cues et leurs métadonnées. Les mesures et synchronisations techniques ne
certifient ni la reconnaissance de la matière sonore ni le confort d'écoute.
Les chiffres du rendu gelé sont consignés dans `mix_report.json` et
`controls.json` après fabrication.

## Rendu gelé V3

Le mix est reconstruit depuis la chronologie V3 : 30 s exactes, 18 événements,
stéréo PCM16 à 48 kHz. Il ne présente aucun échantillon écrêté ; le pic mesuré
est de −19,81 dBFS. Les sons finissent vers 24,15 s et les
5,85 dernières secondes restent silencieuses pour lire la joie et la liste.

Les cues, gains et instants étant inchangés, le WAV obtenu est identique à
celui de la V2 ; les métadonnées désignent bien la chronologie V3. Le changement
porte sur le jeu visuel, pas sur une nouvelle bande-son. Les trois stems
recomposent exactement le PCM du mix.
Aucun actif ou original de la banque n'a été modifié. Aucune écoute réelle
n'a été effectuée.
