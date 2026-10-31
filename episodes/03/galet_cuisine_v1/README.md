# Just cooking. Mostly washing. — avec le galet

Épisode de cuisine demandé avec le nouveau personnage sélectionné : forme
compacte citron, deux grands yeux, deux moufles flottantes à pouce rond et
deux petits pieds. Nom de travail Galet ; le mot MOU sur la toque garde la
marque du projet. 38 secondes, 1080 × 1920, 24 images/s, sans dialogue.

- [Épisode avec son](Galet_Cuisine.mp4?raw=true)
- [Version muette](Galet_Cuisine_muette.mp4?raw=true)
- [Sources autonomes ZIP](Galet_Cuisine_sources.zip?raw=true)
- [Bilan des contrôles](CONTROLE.md)
- [Découpage](developpement/decoupage.md)

Le chef remue, coupe une carotte, ajoute la tomate puis le sel. Après chaque
contact, il lave les bouts de sa moufle et gaspille du papier. Le rouleau
diminue, le panier se remplit et la cuisson avance. Dernier morceau au sol,
repas brûlé ; il trouve tout de même un succès à présenter : ses mains propres.

Le personnage et ses gestes ont été reconstruits pour les moufles flottantes.
Le décor, les accessoires et le costume approuvés sont réutilisés. L'ancien
modèle MOU, ses épisodes et la V29 interrompue restent conservés.

Les prises, regards, phases de papier et inserts lavabo partagent la chronologie
locale. La petite main du lavabo emploie le même contour ; elle actionne le
robinet et ne rince que les bouts. La musique reste douce et les effets sont
calés sur les contacts ou les pics de mouvement. Les voix proposées dans la
bibliothèque ne sont pas ajoutées automatiquement à ce film.

## Reproduction

Python 3.11 minimum, FFmpeg et bibliothèques système Cairo ; dépendances Python
dans requirements.txt. Depuis le dépôt ou l'archive extraite :

```sh
python -m pip install -r requirements.txt
python episodes/03/galet_cuisine_v1/sources/son.py
python episodes/03/galet_cuisine_v1/sources/render.py --preview
python episodes/03/galet_cuisine_v1/sources/render.py
```

Dans l'environnement cloud existant, employer `.venv/bin/python -B`.
Le mix se reconstruit depuis les WAV d'entrée locaux et motion_sync.json,
sans importer une ancienne vidéo ou appeler un service. `son.py --sync-motion`
sert à remesurer les accents si les gestes sont modifiés. Les licences et les
limites de provenance des anciennes matières sonores sont conservées.

Le ZIP contient les producteurs visuels, la palette, le décor, les polices,
les entrées audio, la partition et les crédits. Les MP4 et grands caches PNG
sont livrés séparément. La QA complète protège aussi des archives MOU qui
restent dans le dépôt et ne sont pas recopiées dans ce ZIP.

Cette réalisation est un premier épisode avec le nouveau personnage. Les
contrôles et les critiques internes ne constituent pas une approbation
artistique de l'utilisatrice ni une preuve de réussite de chaîne. Le modèle
ne peut pas écouter dans cet environnement ; le confort du mix reste à juger.
