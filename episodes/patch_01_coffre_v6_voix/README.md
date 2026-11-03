# PATCH — Le coffre, V6 avec vocalisations

30 secondes, vertical 1080 × 1920, 24 images/s. Cette version ajoute cinq
interventions non verbales originales produites avec Soundgen 3.0.0 :
détermination, ennui, somnolence, surprise et joie. Aucun mot prononcé ni
musique. Les variantes et l'effort, non utilisé dans cet épisode, restent
disponibles pour les prochains films.

- [Film avec vocalisations](PATCH_Le_coffre_V6_voix.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V6_voix_muet.mp4?raw=true)
- [Expressions et accents](PATCH_Le_coffre_V6_voix_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_V6_voix_sources.zip?raw=true)
- [Bibliothèque vocale et planche d'écoute](../../personnages/PATCH_voix_v1/)
- [Contrôles et limites](CONTROLE.md)

Le moteur Soundgen a réellement été installé et exécuté dans un runtime R
local. Les prises sont générées à partir de paramètres conservés, sans poids
neuronaux, enregistrement tiers ou voix clonée. Bark n'a pas été exécuté.
La banque contient six intentions, deux prises par intention. Les licences
du logiciel, les paramètres, graines et preuves d'exécution sont inclus.

Le début de chaque prise tient compte de son accent sonore mesuré. La bouche
reste fermée pour le « hm ». Le soupir et le bâillement utilisent une ouverture
arrondie sans dents ; le bâillement se ferme avant le changement de plan.
L'inspiration commence après le retour du visage à l'écran. Les deux petits
souffles du rire modulent la bouche dans la pose de joie sans déplacer les
mains qui tiennent le téléphone.

Les bras, les contacts, le téléphone, les vues, le compte à rebours et la durée
sont ceux de V5. Les 18 effets existants et leurs niveaux sont préservés.
Les voix ont des gains fixes et mesurés, avec de longues plages sans voix ;
pas de musique, de pompage du volume ou de compression par scène.

Les vérifications portent sur les fichiers effectivement générés, le mouvement
visible, la synchronisation et les niveaux. **Aucune écoute réelle n'est
possible dans cet environnement : naturel, confort et effet comique des voix
ne sont pas déclarés validés à l'oreille.** La planche d'écoute est fournie
séparément pour apprécier les prises sans les bruitages du film.

## Reproduction

Les WAV inclus permettent de reconstruire le film sans installer R. Depuis
la racine du dépôt ou du ZIP extrait, avec Python ≥ 3.11 et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v6_voix/sources/son.py
python episodes/patch_01_coffre_v6_voix/sources/render.py --stills
python episodes/patch_01_coffre_v6_voix/sources/render.py --preview
python episodes/patch_01_coffre_v6_voix/sources/render.py --preview --mux
python episodes/patch_01_coffre_v6_voix/sources/render.py
python episodes/patch_01_coffre_v6_voix/sources/render.py --mux
```

Dans l'environnement du projet utiliser `.venv/bin/python`. Pour régénérer
la banque incluse avec Soundgen, sous Debian 13 x86_64 et avec les prérequis
décrits dans son README :

```sh
python episodes/patch_01_coffre_v6_voix/assets/voix/sources/install_runtime.py --runtime work/voix_soundgen_runtime
python episodes/patch_01_coffre_v6_voix/assets/voix/sources/run_generation.py --runtime work/voix_soundgen_runtime
```

Les paramètres R et versions des dépendances sont conservés dans
`assets/voix/`. `preparer_voix.py` prépare les cues et enveloppes depuis
la banque maître du dépôt ; il n'est pas nécessaire pour rendre les sources
déjà préparées. Les contrôles comparant les anciens films exigent le dépôt.
