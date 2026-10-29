# Oggy comme référence : accès réel et mise en scène proposée pour MOU

Observation : 29 octobre 2026, 20 h 51–20 h 53 environ, Africa/Casablanca
(19 h 51–19 h 53 UTC dans les journaux). Recherche de réalisation pour le
pilote existant, pas veille statistique d’un nouvel épisode.

## Ce qui a pu être consulté

Deux sources officielles ont été tentées directement :

- [Fiche Oggy chez Xilam](https://xilam.com/en/media/oggy-and-the-cockroaches/).
- [Chaîne YouTube Oggy](https://www.youtube.com/@oggy/videos).

Les deux requêtes ont échoué au tunnel du proxy avec **403 Forbidden**.
La politique réseau est restreinte et appliquée ; aucun contournement,
miroir de vidéo ou téléchargement d’épisode tiers n’a été utilisé.
Preuves : [acces_sources.json](acces_sources.json).

**Aucun épisode Oggy n’a été vu ni écouté dans cette recherche.** Aucun
minutage de plan, bruitage, compteur, rétention ou technique propre à une
séquence Oggy n’est donc présenté comme une observation. « Oggy » reste la
référence artistique demandée par l’utilisatrice ; les recommandations
ci-dessous sont des propositions pour MOU, distinctes d’une analyse de cet
exemple inaccessible. Aucun personnage, gag précis ou son n’est repris.

Des documents officiels ouverts ont en revanche été réellement lus :

1. [OpenToonz — Creating Movements](https://github.com/opentoonz/opentoonz_docs/blob/master/source/creating_movements.rst) : caméras multiples et actives, hiérarchies de transformations, clés et réglage de vitesse.
2. [OpenToonz — Editing Curves and Numerical Columns](https://github.com/opentoonz/opentoonz_docs/blob/master/source/editing_curves_and_numerical_columns.rst) : interpolations Constant, Linear, Ease et réglage Step, courbes et valeurs image par image.
3. [OpenToonz — Cutout Animation](https://github.com/opentoonz/opentoonz_docs/blob/master/source/creating_cutout_animation.rst) : parentage, pivots, IK et limites des modèles à sections fixes.
4. [Friction — Animation Techniques](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/animation_techniques.md) : flipbook d’images, morphing de chemins, parentage et orientation vers une cible.
5. [Friction — Usage](https://github.com/friction2d/friction2d.github.io/blob/main/documentation/usage.md) : édition des clés et paramètres.

Les réponses HTTP, dates, tailles et SHA256 sont dans [documents.json](documents.json).
Les textes complets restent dans `work/recherche_oggy/`, hors livraison ; les
preuves versionnées contiennent des résumés et de courts extraits. La licence
du logiciel ne doit pas être déduite de celle de sa documentation. Une tentative
de `LICENSE` à la racine des docs OpenToonz a répondu 404 ; aucune licence de
redistribution de l’ensemble du manuel n’est affirmée ici.

## Cinq décisions concrètes pour le prochain essai

### 1. Dessiner d’abord les poses qui portent l’intention

La V21 faisait surtout varier des contrôles de visage. Pour le prochain
essai, définir seulement trois poses lisibles : **constat**, **solution**,
**pris sur le fait**. Vérifier leurs silhouettes et leurs regards avant
de créer les transitions. Les deux mains restent les moufles du rig natif.
La silhouette du corps, les raccords et l’identité de MOU restent conservés.

Le flipbook décrit par Friction est une possibilité pour tenir des poses
dessinées ; le morphing et les courbes sont des moyens de relier des poses,
pas une garantie de jeu. Un changement de logiciel ne fournit pas les poses.

### 2. Séparer lecture, anticipation, geste et réaction

Utiliser de vraies tenues Constant/Step pour l’instant où MOU comprend.
Puis relier les poses par des accélérations différentes, au lieu d’appliquer
le même lissage à tout le corps. Éviter les montées/descentes qui n’ont pas
de cause physique : le regard et le geste doivent porter la décision.

À 24 images/s, points de départ **proposés pour notre test** : regard tenu
6–10 images, anticipation 3–5 images, geste court 8–12 images, résultat/réaction
tenus 12–18 images. Ce ne sont ni des mesures d’Oggy ni des normes de qualité.
Déplacer ou supprimer une tenue après avoir vu le mouvement réel.

### 3. Faire porter une information à chaque cadre

La caméra doit résoudre les ambiguïtés identifiées dans MOU :

- **Plan moyen visage + moufle** : la goutte et son regard sont lisibles ensemble.
- **Insert du tube vide** : la cause de l’arrêt du geste devient évidente.
- **Retour visage** : bref déclic ; main encore immobile avant le geste.
- **Très gros plan main/tablier, sans visage** : montrer le glissement sur le tissu ; aucune lecture possible d’une main au menton.
- **Plan plus large du résultat** : mains retirées du visage, poubelle pleine et papier au sol ; MOU regarde le gaspillage puis nous.

Le tableau de caméras peut déjà exister en SVG/Python : il n’exige pas une
migration. Préférer une coupe motivée à un zoom permanent ou à une remontée
du personnage servant seulement à contourner le plan de travail.

### 4. Résoudre l’insert du tablier par son cadrage, pas par un corps flottant

Une possibilité native à essayer : préparer la zone **x160–230 / y334–423**
du rig comme détail de main/poche. Le cadre vertical doit ensuite être composé
autour de cette zone ; ce rectangle de travail n’est pas un viewBox 9:16
définitif. La marge horizontale doit contenir la calotte de la moufle pendant
toute la passe. Pour cet insert uniquement, rendre le détail corps habillé
et bras concernés, sans l’îlot ni les pieds hors sujet, afin que le premier
plan ne masque plus le contact. Ne pas déplacer le décor général ni allonger
les bras.

Ce repère est une proposition de préparation, **pas un rendu validé**. Selon
la pose effective, élargir le champ ou ajuster le point de contact pour garder
le contour complet de la moufle. Si cette géométrie ne montre pas un essuyage,
retravailler le blocage plutôt que conclure que le nom de phase dans le code
prouve l’action.

### 5. Hiérarchiser le son et ménager le temps de réaction

Pour le test, associer un bruitage à l’action utile : ouverture du robinet,
filet d’eau, déchirure, contact souple. Éviter une ponctuation à chaque regard
ou changement de visage. La réaction peut avoir seulement le fond sonore
discret, ce qui laisse lire le visage. Ne pas ajouter un effet sonore pour
compenser une action visuellement ambiguë.

Ce point est une direction éditoriale, pas une appréciation auditive d’Oggy
ou du mix MOU : aucune écoute n’a eu lieu ici. Les niveaux numériques et les
spectres peuvent détecter des défauts matériels, sans certifier le confort.

## Ce qui permettrait de juger l’essai

Un court montage muet doit permettre à un lecteur sans scénario d’indiquer
**l’objet regardé et l’action comprise**, avant de lui demander de nommer une
émotion fine comme la gêne. Le montage sonore doit ensuite renforcer ces mêmes
informations. Une série de sept poses fixes ne suffit pas à conclure sur une
passe de tissu ; examiner aussi les images successives du contact et le clip.

La production ne doit pas être qualifiée de « professionnelle » sur la seule
base d’un export H264, de variations de paramètres ou d’une liste d’outils.
Les critères matériels et la lecture artistique sont à consigner séparément.
