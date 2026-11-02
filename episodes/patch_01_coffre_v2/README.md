# PATCH — Trente minutes de concentration

**30 secondes de film représentent trente minutes dans l'histoire.**
PATCH enferme son téléphone pour travailler. À chaque minute, il regarde
le coffre. Ses tentatives de revenir à sa liste cèdent à la surveillance du
compteur. Trente minutes plus tard, il récupère son téléphone avec joie :
les trois cases de sa liste sont toujours vides.

- [Film avec son — 1080 × 1920](PATCH_Le_coffre_30min.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_30min_muet.mp4?raw=true)
- [Storyboard rendu](PATCH_Le_coffre_30min_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_30min_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

Cette révision répond au retour « dix secondes, le gag n'est pas lisible ».
La [première version](../patch_01_coffre/) reste conservée. Le dessin, la
palette et le rig de PATCH sont identiques ; les prises et la profondeur
du coffre réutilisent les mécanismes de cette version.

Le réglage porte `30 MIN`, `30:00` et `MIN:SEC`. L'horloge passe de 09:00
à 09:30. La première ellipse est annoncée par `1 MIN LATER`, puis un montage
montre les 29 vérifications. Les premiers retours vers le crayon sont plus longs ;
les minutes 4 à 26 accélèrent, puis les trois dernières minutes et la dernière
seconde reprennent de l'espace. Un insert final isole la liste intacte.

La bande-son comporte 18 effets courts, sans musique ni voix. Les sources CC0
et les signaux UI originaux sont documentés dans `assets/son/`. Les mesures
et la synchronisation ne constituent pas une écoute du mix.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, Python 3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v2/sources/son.py --timeline episodes/patch_01_coffre_v2/chronologie.json --output episodes/patch_01_coffre_v2/audio/mix.wav
python episodes/patch_01_coffre_v2/sources/render.py --stills
python episodes/patch_01_coffre_v2/sources/render.py --preview
python episodes/patch_01_coffre_v2/sources/render.py --preview --mux
python episodes/patch_01_coffre_v2/sources/render.py
python episodes/patch_01_coffre_v2/sources/render.py --mux
```

Dans l'environnement du projet, utiliser `.venv/bin/python`.
Les dessins paramétriques, sons, licences et police DejaVu sont inclus.
Aucun compte, service payant ou accès réseau n'est nécessaire au rendu.
Les images intermédiaires restent dans `work/`, hors Git.

`personnage.py` conserve le rig ; `reference_scene.py` contient une copie
autonome des mécanismes de la V1, pas un import vers son dossier. `scene.py`
dirige les ellipses, regards et plans. `chronologie.json` porte les instants
communs à l'image et au son. `render.py` produit les 720 images puis encode ;
le mux conserve le flux vidéo de la version muette.

Les scénarios, critiques et corrections restent dans `developpement/` et
`controle/`. La lecture des agents est une revue interne, pas un test public
ni une approbation de l'utilisatrice.
