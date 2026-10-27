# Projet MOU

## Décision de référence

MOU est retenu par l'utilisatrice. Reprendre le personnage vert citron à deux
yeux de `references/MOU_reference.png` et le modèle articulé `mou_rig.py`.
Le test de construction est dans `output/MOU_verification_9_secondes.mp4`.

Conserver le corps asymétrique, la petite double bosse arrondie au sommet,
les deux grands yeux, les sourcils prune, les deux bras courts avec une moufle
par bras et les deux petits pieds prune. Aucun nez, germe, antenne ou costume.
Garder des couleurs uniformes, des contours nets et des repères stables.
Le modèle de patate ocre, le cyclope au nez rose et TAP sont des pistes abandonnées.

## Mission

Lire `BRIEF_MOU_CODEX.txt` et `PILOTE_01.txt`, puis produire le premier épisode
terminé avec son et ses sources. Réutiliser la base vérifiée. Avancer jusqu'au
résultat consultable, en corrigeant les défauts observés.

## Fabrication

- Utiliser des outils de production gratuits et open source.
- Conserver Python, les formes SVG, CairoSVG, Pillow, NumPy et FFmpeg pour
  cette première réalisation. Les versions Python sont dans requirements.txt.
- Ne pas changer de moteur sans problème concret qui le justifie.
- Ne pas employer d'API payante, de crédits vidéo, de service propriétaire
  présenté comme gratuit, ni de ressource à licence commerciale incertaine.
- Produire les sons courts localement ou avec des enregistrements originaux.
  Conserver les sources des effets et leur provenance.
- Rendre les trajectoires, expressions et poses modifiables dans le code.
  Les mains et les pupilles restent attachées à leurs repères pendant les gestes.
- Le corps et le visage doivent rester lisibles sur un petit écran.

## Agents

Employer les agents lorsqu'il existe du travail indépendant, avec des fichiers
distincts. Le coordonnateur choisit les tâches et réalise l'intégration.

1. Animation : adapter les gestes nécessaires au seul épisode retenu.
2. Son : préparer les effets à partir de la même chronologie stabilisée.
3. Critique : examiner le rendu, repérer les défauts avec leurs instants précis.

Le scénario se stabilise avant la fabrication ; la critique dépend du rendu.
Les agents ne changent pas chacun la silhouette ou le caractère de MOU.

## Contrôles utiles

Les expressions, les regards et les transitions ont été testés. La marche,
les retournements et la prise d'objets n'ont pas encore été vérifiés.
Si l'épisode ajoute un geste, réaliser un petit test de contact correspondant.
Vérifier sa continuité et son intention, puis l'intégrer.

Contrôler les raccords des bras, le nombre de mains, les regards dirigés,
les pieds au sol, les contacts avec l'accessoire, le découpage des pupilles,
la synchronisation des sons et l'absence de saturation. Un export réussi
ne démontre pas que le gag est compréhensible.

Examiner d'abord un montage léger complet avec son. Corriger les problèmes
repérés, puis exporter le final 1080 × 1920. Conserver les images non concernées
par une correction et limiter le recalcul aux passages modifiés lorsque possible.

## Livraison

Fournir le MP4 avec son, une version muette, la chronologie, les sources et
une courte note de contrôle. Indiquer honnêtement les limites restantes.
Le projet local et les fichiers livrés constituent le périmètre actuel.
