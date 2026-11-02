# Référence commune — PATCH, reconstruction du coffre

2 novembre 2026, Africa/Casablanca. L'utilisatrice demande de reconstruire
l'épisode en s'inspirant de la vidéo qu'elle a fournie. Cette autorisation
porte sur un nouvel épisode complet, pas seulement un test de poses.
Les versions précédentes restent conservées.

## Personnage et outils

PATCH reste le raton gris et crème au masque brun, au hoodie corail,
aux deux oreilles et à la queue annelée. Il possède deux bras continus,
deux pattes simples et deux yeux. Le jeu évolue ; son identité graphique
reste reconnaissable. Aucun ancien modèle MOU ou Galet n'entre en production.

Python, SVG, Pillow, CairoSVG et FFmpeg restent les outils de production,
gratuits et libres. La vidéo reçue sert de référence de jeu, pas de plan
à insérer dans le film. Sa source privée reste dans l'espace de travail.

## Histoire à rendre visible

PATCH veut travailler. Il choisit d'enfermer son téléphone pendant trente
minutes. Il tente de commencer, vérifie le coffre chaque minute, puis se
consacre entièrement à son attente. Il récupère joyeusement le téléphone ;
ses trois tâches sont restées au même point. Sa satisfaction finale est
sincère : le contraste avec la liste intacte donne la chute.

Film cible : 30 secondes à 24 images/s, 1080 × 1920. Le récit représente
trente minutes par des ellipses explicites, et non trente secondes réelles.

- Coffre : `30:00`, repères `30 MIN` et `MIN:SEC` au verrouillage à 4 s.
- Horloge : 09:00 au départ, 09:30 à l'ouverture à 23 s.
- Première ellipse à 6 s : `1 MIN LATER`. Les 29 vérifications sont conservées.
- Trois premières minutes longues ; montage des minutes 4 à 29 entre
  12,25 et 22 s. Les valeurs `03:00`, `02:00`, `01:00` sont davantage tenues.
- Dernière seconde réelle de film entre 22 et 23 s : `00:01`, coffre fermé.
- Reprise du téléphone à 24,05 s ; joie après la fin de la prise physique.
- Insert `TO DO` entre 26,65 et 27,9 s : trois cases imprimées, zéro coche.
- Retour à PATCH absorbé par son téléphone de 27,9 à 30 s.

## Apport précis de la référence

La vidéo reçue montre une progression du corps : joue dans la main,
bras croisés, tête descendue près du plateau, puis redressement et joie.
Cette progression guide les nouvelles poses. Le regard, les paupières,
les sourcils et les épaules portent une intention commune. Des poses tenues
séparent les gestes ; le personnage ne flotte pas entre deux attitudes.

La reconstruction garde une motivation de travail lisible au début.
Elle évite les défauts observés dans la référence : apparition d'un œil
dans l'horloge, compteur temporel incohérent, pseudo-texte et cases cochées
dans la liste finale. Le jeu expressif ne dispense pas de cette continuité.

## Frontières de fabrication et revue

Le coordinateur possède scène, chronologie, caméras, contacts, exports,
archives et bilan. Le dessinateur possède `sources/personnage.py` et
`sources/jeu.py`. Le scénariste possède ce fichier et
`developpement/decoupage.md`. La critique possède ses rapports et la QA
son contrôleur et ses rapports. Chaque rôle écrit seulement ses fichiers.

Les contacts de la prise initiale, du dépôt, de la fermeture et de la reprise
du téléphone restent conservés. Le crayon est déposé à 11,78125 s et reste
libre ensuite. Si la nouvelle joie bouge une patte qui tient le téléphone,
le téléphone doit suivre réellement cette patte.

La joue doit toucher la patte qui la soutient ; les bras croisés restent
lisibles au-dessus du bureau. La tête basse garde les deux yeux visibles.
Aucune manche ne se détache et aucune main supplémentaire ne remplace
une pose difficile. Le compteur et la liste restent lisibles dans les cadres.

Les sons ont des causes visibles et des instants communs à l'image.
Pas de bruit d'écriture sur le papier intact, pas de clic ajouté à chacune
des trente minutes. Les sons sobres existants peuvent être réutilisés.
Aucune musique ou vocalisation n'est ajoutée pour expliquer une action.

Examiner les vraies poses, l'animatique complète sans son, puis le véritable
export HD. Corriger les défauts observés avant livraison. Une QA passée
ne constitue ni une approbation comique du public ni une écoute du mix.
