# PATCH — Trente minutes de concentration, jeu reconstruit

Épisode de 30 secondes, 1080 × 1920, à 24 images/s. PATCH enferme son
téléphone pendant trente minutes pour travailler, puis consacre sa séance
à surveiller le coffre. Il retrouve son téléphone avec joie ; les trois
cases de sa liste sont restées vides.

- [Film avec son](PATCH_Le_coffre_V3.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V3_muet.mp4?raw=true)
- [Huit poses rendues](PATCH_Le_coffre_V3_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_V3_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

La vidéo fournie par l'utilisatrice sert de référence de jeu : appui de la
joue dans une patte, bras croisés, tête au niveau du plateau, puis détente
joyeuse après la reprise du téléphone. Le film est rendu depuis les dessins
et les nouvelles poses du projet. Aucune image ou bande-son de cette vidéo
privée n'entre dans le rendu ou les sources livrées.

PATCH conserve son dessin, sa palette et son identité. Son rig est étendu
pour diriger les coudes, déplacer légèrement la tête et animer les yeux et
la bouche. Les contacts de la prise, du dépôt et de la reprise du téléphone
sont préservés ; le téléphone suit la patte finale pendant la joie.
Les [versions précédentes](../patch_01_coffre_v2/) restent intactes.

Le récit représente trente minutes par des ellipses explicites, une horloge
et les repères `30 MIN`, `MIN:SEC`, `1 MIN LATER` et `30 MIN LATER`.
Les 29 vérifications sont conservées. La liste finale contient trois cases
vides : elle ne reproduit pas les coches erronées de la référence.

La bande-son reste celle, sobre, de la V2 : dix-huit effets courts,
sans musique ni voix ajoutée. Les nouveaux gestes se lisent aussi dans
le silence. Les origines CC0, les signaux UI originaux et les mesures sont
documentés dans `assets/son/` et `audio/`. Aucune audition n'est revendiquée.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, Python 3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v3/sources/son.py --timeline episodes/patch_01_coffre_v3/chronologie.json --output episodes/patch_01_coffre_v3/audio/mix.wav
python episodes/patch_01_coffre_v3/sources/render.py --stills
python episodes/patch_01_coffre_v3/sources/render.py --preview
python episodes/patch_01_coffre_v3/sources/render.py --preview --mux
python episodes/patch_01_coffre_v3/sources/render.py
python episodes/patch_01_coffre_v3/sources/render.py --mux
```

Dans l'environnement du projet, utiliser `.venv/bin/python`.
Les sources incluent dessins paramétriques, poses, chronologie, sons,
licences et police DejaVu. Aucun ancien dossier, cache, compte ou accès
réseau n'est nécessaire pour reconstruire le film.

`personnage.py` porte le dessin et les contrôles ; `jeu.py` compose les
attitudes et transitions ; `scene.py` dirige les caméras, temps, prises et
masquages. `reference_scene.py` contient une copie autonome des mécanismes
de scène initiaux. Les fichiers intermédiaires restent dans `work/`, hors Git.

Le scénario, la critique des rendus et les corrections sont conservés.
Les contrôles techniques et les lectures internes ne préjugent ni de la
réception du gag ni d'une cadence hebdomadaire validée.
