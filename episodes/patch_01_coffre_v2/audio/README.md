# Bande-son de PATCH — contrat de montage

Version2 : le coffre représente trente minutes dans une vidéo de trente secondes avec
ellipses explicites. La banque de la première version est conservée et ses
sources/provenances restent identiques. Aucun ancien mix n'est réemployé.

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
`lid_close`, `lock`, `button`, `unlock`, `paper`, `tick`, `ellipsis` et `end_ping`.

`ellipsis` est un très court double clic, composé à partir du tick CC0 existant.
Il est prévu pour quelques passages du temps clairement montrés. Il ne faut
pas associer un clic supplémentaire à chacune des trente minutes affichées :
le montage et les regards doivent expliquer les ellipses. Les transitions
peuvent garder le silence, surtout pendant l'accélération du milieu.

Le rendu produit `mix.wav`, trois stems (`foley`, `ui`, `tick`), `cues.csv`,
`cues.json` et `mix_report.json`. Les pistes sont PCM16 stéréo48kHz.
Les gains restent fixes et explicites ; aucun compresseur ni réglage
automatique par scène ne change l'équilibre. La musique et les voix sont
absentes. La feuille vierge n'a pas de bruit d'écriture.

Les fondus, crêtes et synchronisations peuvent être contrôlés numériquement.
Ils ne remplacent pas une écoute réelle du confort et de la matière des
bruitages. Aucune écoute n'est revendiquée par ce producteur.

## Rendu de cette version

La chronologie gelée contient dix-huit événements : les contacts du téléphone
et du coffre, quatre accents d'ellipse, quatre ticks de repère et le signal
de fin. Les trente minutes ne sont pas accompagnées de trente clics.
Le compte à rebours de l'histoire est comprimé par les ellipses visibles ;
les instants du WAV suivent les trente secondes du montage.

Le mix est PCM16 stéréo48kHz, sans saturation. Les derniers effets finissent
vers24,15s ; la fin reste calme pour lire le travail inachevé. Les fichiers
`mix_report.json` et `controls.json` conservent les mesures et l'empreinte de
la chronologie. Aucun confort perceptif n'est déduit de ces chiffres.
