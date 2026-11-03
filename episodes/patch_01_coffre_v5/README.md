# PATCH — Le coffre, V5

Correctif des bras et du passage du temps, avec une attente moins répétitive.
30 secondes, vertical 1080 × 1920, 24 images/s. Le raton laveur, ses vues
et les prises du téléphone corrigées dans la V4 sont conservés.

- [Film avec son](PATCH_Le_coffre_V5.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V5_muet.mp4?raw=true)
- [Huit vues](PATCH_Le_coffre_V5_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_V5_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)
- [Recherche de voix gratuites](../../recherche/2026-11-03_sons_patch/RECHERCHE.md)

La main droite au repos est reculée : la paume et sa manche n'empiètent
plus sur le flanc plein du coffre. Pendant l'attente, les faces solides du
coffre masquent correctement les bras qui passent derrière. La profondeur
des prises du téléphone reste celle du correctif précédent.

Le minuteur, les aiguilles et la nouvelle heure numérique proviennent
d'un même temps de session, en secondes entières. Après le déverrouillage,
le compteur reste à zéro et l'horloge de la session à 09:30. Les trente
minutes sont représentées par des ellipses puis un passage accéléré du temps.

Dès la seizième minute du récit (16,25 s du film), les regards à chaque
minute cessent : bras croisés, paupières lourdes, une seule descente vers
le plateau, puis un éveil et un regard maintenu sur le coffre. Un bref
« LATER... » remplace les annonces répétées des minutes dans cette partie.
La dernière seconde est isolée avant l'ouverture. Les anciennes bornes de
minutes sont conservées dans la chronologie pour le moteur de base ;
`calm_waiting` et `sources/temps.py` dirigent le montage final après 16,25 s.

Les 18 effets précédents sont conservés ; aucune nouvelle voix ou musique
n'est ajoutée. Le mix est reconstruit avec la chronologie V5 et reste identique
au WAV précédent. Les mesures audio ne constituent pas une écoute réelle.
La vidéo privée de référence et ses sons ne sont pas inclus dans les sources.

## Reproduction

Depuis la racine du dépôt, ou du ZIP extrait, avec Python ≥ 3.11 et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v5/sources/render.py --stills
python episodes/patch_01_coffre_v5/sources/son.py --timeline episodes/patch_01_coffre_v5/chronologie.json --output episodes/patch_01_coffre_v5/audio/mix.wav
python episodes/patch_01_coffre_v5/sources/render.py --preview
python episodes/patch_01_coffre_v5/sources/render.py --preview --mux
python episodes/patch_01_coffre_v5/sources/render.py
python episodes/patch_01_coffre_v5/sources/render.py --mux
```

Dans l'environnement du projet, utiliser `.venv/bin/python`. Les dessins,
sons, licences et police nécessaires au rendu sont inclus. Les contrôles
de préservation des versions historiques nécessitent le dépôt complet.
