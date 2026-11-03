# PATCH — Le coffre, V7

Deux corrections demandées : une voix aiguë et couinante, aux réactions
plus différenciées, et un vrai trajet du bras autour du coffre pour presser
le bouton. 30 s, 1080 × 1920, 24 images/s. Les versions précédentes sont conservées.

- [Film avec son](PATCH_Le_coffre_V7.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V7_muet.mp4?raw=true)
- [Trajet et expressions](PATCH_Le_coffre_V7_storyboard.png?raw=true)
- [Sources ZIP](PATCH_Le_coffre_V7_sources.zip?raw=true)
- [Nouvelle bibliothèque et planche d'écoute](../../personnages/PATCH_voix_v2_squeaky/)
- [Contrôles et limites](CONTROLE.md)

Le défaut observé dans le vrai V6 était surtout entre 3,5 et 4,3 s : la main
passait devant le premier chiffre du minuteur et sa manche disparaissait
derrière le flanc. Elle ferme maintenant vers le coin gauche, se retire par
l'extérieur puis atteint le bouton par le côté. Un contrôle de poignet et
une manche courbée maintiennent le raccord. Le LCD reste dégagé. Au dépôt et
à la reprise, la façade masque le bas de la paume entrant avec le téléphone.
Les contacts légitimes sur le panneau du couvercle restent visibles.

Les douze prises vocales ont été régénérées avec Soundgen 3.0.0. La nouvelle
identité combine hauteur plus aiguë, petit conduit vocal et mêmes formants
neutres ; M, O et A modifient réellement les résonances. Chaque intention
a son propre rythme : deux petits « mm », expiration descendante, bâillement
lent, effort bref, surprise très courte, deux accents de rire. Cinq intentions
sont utilisées ; l'effort reste disponible dans la bibliothèque.

Le mix conserve les 18 effets de V5/V6 et cinq prises vocales, à gains fixes.
Les cibles RMS de voix sont réduites de 1,5 dB par rapport à V6 pour accompagner
le timbre aigu. Aucun mot, musique, compresseur ou variation de volume par scène.
Les mains hors correction, le téléphone, les vues, les trente minutes et
l'attente continue sont conservés.

Les données et la revue visuelle ne sont pas une audition. **Le naturel,
le confort et la singularité perçue de cette voix ne sont pas validés à
l'oreille ici.** La planche d'écoute séparée donne accès aux deux variantes
de chacune des six intentions. Les créations du projet ne reçoivent pas
de nouvelle licence publique ; les licences des outils sont conservées.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, avec Python ≥ 3.11 et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v7/sources/son.py
python episodes/patch_01_coffre_v7/sources/render.py --stills
python episodes/patch_01_coffre_v7/sources/render.py --preview
python episodes/patch_01_coffre_v7/sources/render.py --preview --mux
python episodes/patch_01_coffre_v7/sources/render.py
python episodes/patch_01_coffre_v7/sources/render.py --mux
```

Les WAV sont inclus : R n'est pas nécessaire pour reconstruire le mix ou le
film. Dans cet environnement utiliser `.venv/bin/python`. Les recettes,
paramètres, licences et preuves Soundgen sont sous `assets/voix/` ; voir le
README de la banque pour sa régénération avec le runtime local existant.
Les comparaisons avec les anciens films nécessitent le dépôt complet.

Depuis le ZIP extrait, sous Debian 13 x86_64 avec les prérequis documentés,
les scripts inclus peuvent installer le runtime local puis régénérer les voix :

```sh
python episodes/patch_01_coffre_v7/assets/voix/sources/install_runtime.py --runtime work/voix_soundgen_runtime
python episodes/patch_01_coffre_v7/assets/voix/sources/run_generation.py --runtime work/voix_soundgen_runtime
```
