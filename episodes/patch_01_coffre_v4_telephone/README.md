# PATCH V4 — correctif des prises du téléphone

Version locale de la [V4](../patch_01_coffre_v4/) : les défauts de poignet,
de relâchement et de retournement du téléphone sont corrigés. Durée : 30 s,
1080 × 1920, 24 images/s. Le personnage, ses poses générales, les vues, le récit,
la chronologie et la bande-son sont conservés.

- [Film corrigé avec son](PATCH_Le_coffre_V4_telephone.mp4?raw=true)
- [Version muette](PATCH_Le_coffre_V4_telephone_muet.mp4?raw=true)
- [Huit vues des contacts](PATCH_Le_coffre_V4_telephone_storyboard.png?raw=true)
- [Sources autonomes ZIP](PATCH_Le_coffre_V4_telephone_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)

La patte s'oriente avant de prendre l'objet et se ferme progressivement.
Au dépôt, le téléphone s'immobilise ; la patte s'ouvre puis se retire avant
la fermeture du couvercle. Les changements instantanés de poignet d'environ
85° sont supprimés. Le téléphone passe par la tranche pendant la levée,
puis montre son dos avant la coupe vers la joie.

Les centres et trajectoires du téléphone, ses instants de dépôt/reprise,
le seuil de dégagement du coffre et les prises à deux mains après 24,7 s
restent ceux de la V4. Le téléphone reste devant la manche et derrière la
façade tant qu'il est dans le coffre ; les paumes restent au-dessus pour
la prise. Le dépôt gagne une courte pause et la fermeture finit toujours
à 3,55 s, au même signal sonore.

`correction_telephone.json` décrit les fenêtres du correctif.
`sources/telephone.py` en dirige la gestuelle ; `scene.py` l'intègre au
dessin, à la profondeur et au retournement du téléphone. Les autres sources
du personnage et des vues sont copiées sans modification. Les contrôles
comparent les PNG hors fenêtres à ceux de la V4 pour éviter une modification
collatérale de l'épisode.

La chronologie, la banque, le WAV et ses stems sont copiés à l'identique.
Aucun effet, musique ou voix n'est ajouté. Les mesures ne constituent pas
une écoute réelle. Aucun plan ou son de la vidéo privée de référence
n'entre dans cette fabrication.

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, avec Python 3.11 minimum et FFmpeg :

```sh
python -m pip install -r requirements.txt
python episodes/patch_01_coffre_v4_telephone/sources/render.py --stills
python episodes/patch_01_coffre_v4_telephone/sources/render.py --preview
python episodes/patch_01_coffre_v4_telephone/sources/render.py --preview --mux
python episodes/patch_01_coffre_v4_telephone/sources/render.py
python episodes/patch_01_coffre_v4_telephone/sources/render.py --mux
```

Dans l'environnement du projet utiliser `.venv/bin/python`. Le mix déjà
fourni peut être reconstruit avec `sources/son.py --timeline chronologie.json
--output audio/mix.wav` depuis le dossier de cette version. Tous les dessins,
sons, licences et police nécessaires au rendu sont inclus. Le contrôle des
références historiques nécessite le dépôt complet.
