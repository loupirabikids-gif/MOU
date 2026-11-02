# PATCH — Le coffre à concentration

Épisode vertical de **20 secondes**, 1080 × 1920, 24 images/s.
PATCH enferme son téléphone pour se concentrer, puis surveille le compte à
rebours jusqu'à l'ouverture. Il retrouve son écran avec joie ; la feuille
est restée vierge. Le scénario a été choisi explicitement par l'utilisatrice.

- [Voir le film avec son](PATCH_Le_coffre.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_muet.mp4?raw=true)
- [Storyboard rendu](PATCH_Le_coffre_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_sources.zip?raw=true)
- [Bilan des contrôles](CONTROLE.md)

Le raton reprend le croquis PATCH : masque, museau crème, oreilles, hoodie
corail et queue annelée. Son rig est neuf, sans réemploi du dessin de MOU.
La scène utilise quatre plans et un compte à rebours réel : verrou à4s,
déverrou à14s, affichage00:10→00:00. Aucun saut temporel caché.

Les bruitages courts ont des causes visibles. Pas de musique ni voix dans
cet épisode ; la compréhension visuelle ne dépend pas du son. Les sources
CC0, extraits et deux petits signaux UI originaux sont documentés dans
`assets/son/`. Les mesures audio ne constituent pas une écoute du mix.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, Python3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre/sources/son.py --timeline episodes/patch_01_coffre/chronologie.json --output episodes/patch_01_coffre/audio/mix.wav
python episodes/patch_01_coffre/sources/render.py --stills
python episodes/patch_01_coffre/sources/render.py --preview
python episodes/patch_01_coffre/sources/render.py --preview --mux
python episodes/patch_01_coffre/sources/render.py
python episodes/patch_01_coffre/sources/render.py --mux
```

Dans l'environnement du projet utiliser `.venv/bin/python`.
Tous les inputs de production sont inclus : dessins paramétriques, son,
licences et police DejaVu pour la seule planche de légendes. Aucun compte,
service payant, ancien rig ou accès réseau nécessaire pour reconstruire.
Les PNG de travail restent dans `work/`, hors Git.

`personnage.py` porte les expressions et les pattes ; `scene.py` dirige les
regards, prises, profondeur et plans ; `chronologie.json` conserve le découpage
et les cues ; `son.py` produit le mix et ses stems ; `render.py` rend puis
encode. Le mux conserve le flux vidéo de la version muette.

Les scénarios et critiques du montage effectivement produit sont conservés
dans `developpement/` et `controle/`. La revue technique est distincte de la
lecture comique et de l'approbation du public. La cadence hebdomadaire et
le succès d'audience ne sont pas déduits de cet épisode.
