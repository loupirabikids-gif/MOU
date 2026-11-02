# PATCH — Trente minutes de concentration, vues et jeu reconstruits

Épisode vertical de 30 secondes, 1080 × 1920, à 24 images/s.
PATCH enferme son téléphone pour travailler, vérifie le coffre pendant
trente minutes, puis retrouve son écran avec joie. Les trois cases de sa
liste sont restées vides.

- [Film avec son](PATCH_Le_coffre_V4.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V4_muet.mp4?raw=true)
- [Douze vues rendues](PATCH_Le_coffre_V4_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_V4_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

Cette version applique l'[analyse complète de la référence](../../recherche/2026-11-02_analyse_reference_patch/ANALYSE.md).
Le bureau reçoit des dessins distincts : vue haute de trois quarts avec
flanc et façade, frontal de jeu, vue basse avec dessus mince, gros plan
visage/coffre et vue élargie pour la joie. L'horloge et le crayon ont leurs
plans dédiés. L'image ne repose plus sur le seul recadrage d'un dessin frontal.

Le corps entier se détend et tient une pose en l'air avec deux pieds visibles,
le coffre décalé au bord pour les dégager. Le montage coupe vers la liste
avant une réception montrée. Le téléphone passe réellement dans les deux
mains ; son dos est visible au spectateur et son écran est tourné vers PATCH.
La surprise à l'ouverture a sa bouche ronde sans dents ; la joie puis la
satisfaction au téléphone ont leurs propres intentions et leur lumière.

L'histoire conserve la motivation de travail et les trente minutes explicites,
avec une première vérification visible après l'insert d'horloge, puis retour
au papier. La liste est toujours intacte. Le dessin, la palette et l'identité
de PATCH restent reconnaissables. Les [anciens films](../patch_01_coffre_v3/)
restent conservés. Aucune image ou bande-son de la vidéo privée de référence
n'entre dans la fabrication ou les sources livrées.

La bande-son reste sobre : 18 effets courts documentés, sans musique ni voix
ajoutée. Le WAV est identique à la V3 puisque les contacts et cues sont
conservés. Aucun bruit de réception n'accompagne la coupe avant l'atterrissage.
Les niveaux et la synchronisation sont mesurés ; aucune audition n'est revendiquée.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, Python 3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v4/sources/son.py --timeline episodes/patch_01_coffre_v4/chronologie.json --output episodes/patch_01_coffre_v4/audio/mix.wav
python episodes/patch_01_coffre_v4/sources/render.py --stills
python episodes/patch_01_coffre_v4/sources/render.py --preview
python episodes/patch_01_coffre_v4/sources/render.py --preview --mux
python episodes/patch_01_coffre_v4/sources/render.py
python episodes/patch_01_coffre_v4/sources/render.py --mux
```

Dans cet environnement utiliser `.venv/bin/python`.
`vues.py` porte les dessins du décor et du bureau ; `cadres.json` leurs
placements ; `personnage.py` le dessin et les contrôles ; `jeu.py` les poses,
les pieds et la prise bilatérale ; `scene.py` compose les plans et objets.
`scene_base.py` et `reference_scene.py` sont des copies autonomes des
mécanismes précédents, sans import vers un ancien dossier. Chronologie,
sons, licences et police sont fournis ; le rendu n'exige aucun accès réseau,
compte, ancien dossier ou service payant.
Le contrôle des références historiques exige le dépôt complet ; le rendu
et le mix sont autonomes avec les sources fournies.

Les poses, la vraie animatique et les images du vrai HD sont examinées avant
livraison. Ces revues internes et contrôles ne préjugent pas de la réception
du gag par l'utilisatrice ou le public.
