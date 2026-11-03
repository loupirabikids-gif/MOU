# MOU — Le coffre, V2

MOU enferme son téléphone pour travailler trente minutes. Son attention finit
entièrement dirigée vers le coffre. Il retrouve son écran avec bonheur ; la
liste de travail est toujours vide.

- [Film avec son — 30 secondes](MOU_Le_coffre_V2.mp4?raw=true)
- [Version muette](MOU_Le_coffre_V2_muet.mp4?raw=true)
- [Storyboard des treize plans et du recul final](MOU_Le_coffre_V2_storyboard.png?raw=true)
- [Sources ZIP](MOU_Le_coffre_V2_sources.zip?raw=true)
- [Contrôles et limites](CONTROLE.md)
- [Effets seuls](audio/demonstrations/banque_effets_v2.mp4?raw=true)

## Réalisation

L'entrée rapproche le travail et la tentation. Un insert montre les gestes
du verrouillage. L'attente passe de l'effort au renoncement, puis au désir
de récupérer le téléphone : visage rapproché, posture fermée et plan bas
avec une courte avancée de caméra 2D. La satisfaction remplace le saut
suspendu. Le dernier plan part des trois cases vides puis recule dans la
même vue frontale pour réunir MOU absorbé, sa feuille et l'heure09:30.

Le MOU original et ses bras/moufles sont conservés. Le rig natif copié sous
`sources/mou_rig_original.py` et son adaptateur `personnage.py` restent ceux
de la V1. Les changements de composition s'appliquent à toute l'image ;
un recadrage n'est pas présenté comme une rotation 3D.

Huit prises sonores distinctes remplacent les anciens accents répétitifs.
Téléphone, couvercle, bouton, mécanismes et crayon ont des événements
séparés. Le moteur d'un petit ventilateur sert de substitut Foley à la
vibration et un contact bois à celui du crayon. Les sources CC0, auteurs,
URL, notices et traitements sont conservés dans `assets/son_v2/`.
Sans musique ni voix synthétiques rejetées. Les anciens sons copiés dans
`assets/son/` sont des archives, non utilisés par ce mix.

Les contrôles visuels et numériques ne remplacent pas une audition.
Le naturel, le confort et l'efficacité comique du son restent à apprécier
en lecture. Aucun plan ou son de la référence privée Runway n'est inséré.
Les anciens films MOU et PATCH restent conservés.

## Documents d'équipe

- [Découpage approuvé](developpement/direction/CAMERA.md)
- [Cadrages fabriqués et corrections](developpement/cadrages.md)
- [Jeu et continuité des mains](developpement/jeu.md)
- [Son : sources, substitutions et mesures](developpement/son.md)
- [Critique avant fabrication](developpement/critique_avant.md)
- [Critique du vrai montage](controle/critique_finale.md)
- [Décisions de correction](developpement/corrections.md)

## Reproduction

Depuis la racine du dépôt ou du ZIP extrait, Python3.11 ou plus et FFmpeg :

```sh
python -m pip install -r episodes/mou_04_coffre_v2/requirements.txt
python episodes/mou_04_coffre_v2/sources/son.py --prepare
python episodes/mou_04_coffre_v2/sources/son.py --timeline episodes/mou_04_coffre_v2/chronologie.json --output episodes/mou_04_coffre_v2/audio/mix.wav
python episodes/mou_04_coffre_v2/sources/render.py --stills
python episodes/mou_04_coffre_v2/sources/render.py --preview
python episodes/mou_04_coffre_v2/sources/render.py --preview --mux
python episodes/mou_04_coffre_v2/sources/render.py
python episodes/mou_04_coffre_v2/sources/render.py --mux
python episodes/mou_04_coffre_v2/sources/package.py
```

Dans l'environnement du projet : `.venv/bin/python`. Les images de travail
sont des caches exclus de Git et du ZIP. Celui-ci contient dessins, sons,
polices, licences, chronologie et rapports. Les contrôles comparant les
anciennes versions et le rig à la racine demandent le dépôt complet.
