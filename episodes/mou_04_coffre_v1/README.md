# MOU — Le coffre à concentration

MOU remplace Patchy dans le même épisode : il enferme son téléphone pour
travailler trente minutes, passe son temps à attendre, puis retrouve son
écran avec joie. Les trois cases de sa liste restent vides.

- [Film avec son — 30 secondes](MOU_Le_coffre.mp4?raw=true)
- [Version muette](MOU_Le_coffre_muet.mp4?raw=true)
- [Huit poses](MOU_Le_coffre_storyboard.png?raw=true)
- [Sources ZIP](MOU_Le_coffre_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

À la suite du retour sur les cadrages et les effets sonores :
[proposition de réalisation caméra/son pour la prochaine version](developpement/realisation_v2/).
Cette préparation décrit les prises et leurs intentions ; le film et le ZIP
V1 ci-dessus restent ceux de la livraison avec MOU.

Le personnage réutilise le corps, le visage et les pieds du modèle original
`mou_rig.py`, copié sans modification sous `sources/mou_rig_original.py`.
Il garde sa silhouette asymétrique vert citron, deux grands yeux, deux bras
continus avec deux extrémités arrondies et deux petits pieds prune. Aucun
nez, oreille, queue ou vêtement de Patchy n'est dessiné. La référence du projet
est incluse dans `assets/mou/`.

Les contrôles des poses précédentes dirigent maintenant MOU. Le renderer
adapte ses proportions et ses bras aux accessoires. La main atteint réellement
le bouton par le côté ; la façade masque la paume entrant avec le téléphone.
Le gros plan de l'ouverture est élargi et le corps légèrement décalé pour
garder les deux yeux visibles. Le téléphone, le coffre, les trente minutes,
le décor et la succession des plans sont repris ; le cadrage et le placement du gros
plan sont adaptés aux proportions plus larges de MOU et au plateau.

La bande-son conserve les **18 bruitages** du coffre, du téléphone et des
gestes. Les vocalisations synthétiques rejetées ne sont pas utilisées dans
cette version. Aucun nouveau dialogue ou musique. Les expressions restent
animées ; elles doivent pouvoir se lire sans voix. L'audio est contrôlé
numériquement, sans audition réelle revendiquée.

Les anciennes versions MOU et PATCH restent conservées. Aucun plan ou son
de la vidéo privée de référence n'est inclus.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, avec Python ≥ 3.11 et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/mou_04_coffre_v1/sources/son.py --timeline episodes/mou_04_coffre_v1/chronologie.json --output episodes/mou_04_coffre_v1/audio/mix.wav
python episodes/mou_04_coffre_v1/sources/render.py --stills
python episodes/mou_04_coffre_v1/sources/render.py --preview
python episodes/mou_04_coffre_v1/sources/render.py --preview --mux
python episodes/mou_04_coffre_v1/sources/render.py
python episodes/mou_04_coffre_v1/sources/render.py --mux
```

Dans cet environnement utiliser `.venv/bin/python`. Tous les dessins, sons,
polices et licences nécessaires sont inclus. Les comparaisons avec les
anciens films et le rig canonique nécessitent le dépôt complet.
