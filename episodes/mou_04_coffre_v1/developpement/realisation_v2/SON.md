# Le coffre — direction sonore proposée pour MOU

Observation : 3 novembre 2026, Africa/Casablanca. Ce document est un travail
de conception, sans modification du film, du mix ou de la chronologie de
production. Les fichiers, paramètres et placements ont été inspectés ;
**aucune écoute n'est possible ici**. Les textures décrites ci-dessous sont
à rechercher et à écouter, pas des qualités déjà constatées dans les WAV.

## Ce qui existe réellement

Le WAV livré est `audio/mix.wav`, SHA256
`b09ec672aba907961c386be03e2df22c13f36d9ee5d39d94171ad5a3c364ad41` :
30 s, PCM16 stéréo48kHz, 18 cues, sans musique ou voix. Pic mesuré−19,81dBFS.
Les derniers échantillons non nuls finissent vers24,151s ; il reste environ
5,85s sans événement audio. Cela ne suffit pas à déclarer la fin mauvaise :
un silence peut être un choix comique, mais il doit servir une action visible.

Huit des18cues sont des repères d'ellipses ou de secondes. Les prises du
téléphone à1,7 et24,05s utilisent exactement le même fichier `tap.wav`.
`button.wav`, `tick.wav` et `tap.wav` dérivent du même original
`click_button_1`. Le dépôt et la fermeture dérivent de `spring_plastic_1` ;
le crayon posé est un extrait de caresse de papier. Les origines et les
licences CC0 des packs sont documentées dans `assets/son/`. Leur adéquation
à ces objets précis n'a pas été jugée à l'oreille.

## Audit du montage actuel

| Repère actuel | Constat vérifiable | Effet possible sur la lecture, à confirmer à l'écoute | Décision de réalisation |
| --- | --- | --- | --- |
| 0,65s, notification | Deux notes de synthèse additive,0,39s | Peut lire comme un jingle plutôt que le téléphone qui tente MOU | Comparer à une vibration courte d'objet posé ; ne garder qu'un signal clair et localisé sur le téléphone |
| 1,7 et24,05s, saisies | Même `tap.wav` aux deux changements de propriétaire | Un son d'impact n'est pas forcément motivé par une simple saisie | Retirer les taps systématiques ; ne sonoriser que le contact matériel réellement visible |
| 2,8 /3,55 /3,9 /4s | Dépôt, fermeture, bouton et verrou ont quatre cues rapprochés | Risque d'une rafale de petits clics dont les causes se confondent | Organiser une hiérarchie : dépôt doux, fermeture plus pleine, petit bouton puis réponse du verrou ; écouter cette séquence seule |
| 6 /8 /10 /15,917 /19,917 /20,583 /21,292 /22s | Huit ellipses/ticks sur le passage du temps | Peut commenter chaque saut de montage au lieu de laisser grandir l'obsession | Retirer cette ponctuation systématique ; l'horloge et les poses racontent les ellipses |
| 11,781s, crayon | Texture issue de `paper_caress.wav` | La friction de papier peut ne pas raconter l'abandon du crayon | Chercher un petit contact de crayon sur le bois et, seulement si animé, son bref roulement |
| 23s, fin | Deux notes `end_ping` ; le verrou visuel passe déverrouillé à23s | Une mélodie de récompense peut annoncer trop fortement la joie | Remplacer par le vrai petit déclic de libération du mécanisme |
| 23,7s, « couvercle ouvert » | Fichier nommé `unlock.wav` ; le panneau bouge approximativement23,2–23,75s | L'identité de déverrouillage et le mouvement de charnière peuvent être confondus | Séparer libération du verrou à23s et mouvement de charnière pendant le geste |
| Après24,155s | Aucun nouveau cue dans la fin actuelle | Le résultat dépend entièrement du jeu et du cadre ; un bruit ajouté ne réparera pas une chute trop faible | Construire le retour de l'attention au téléphone et la révélation des trois cases vides à l'image ; garder cette révélation sans accent artificiel |

Les hypothèses de cette colonne ne sont pas des jugements d'écoute. La
licence, le nom d'un fichier et un pic correctement dosé ne prouvent ni
reconnaissance de matière, ni naturel, ni effet comique.

## Proposition alignée sur CAMERA.md — 30 secondes

La priorité sonore est **le choix de MOU**, puis **l'attente**, puis **la
récompense minuscule**. Les sons appartiennent aux objets et actions.
La nouvelle caméra précise où diriger l'attention ; le son ne commente pas
chaque cut. Les horaires ci-dessous sont des repères de découpage proposés,
à figer ensemble lors de la nouvelle animatique.

| Événement | Plan / repère proposé | Texture et accent à préparer | Fonction narrative et place dans le mix |
| --- | --- | --- | --- |
| S1 — tentation du téléphone | Plan1, vers0,65s ; écran et regard réagissent | Une vibration courte et feutrée d'un objet posé, avec une petite résonance du support | Attirer l'attention vers le téléphone. Un seul appel ; pas une alarme ni une mélodie de victoire |
| S2 — téléphone déposé | Plan2, contact vers2,8s | Petit « toc » mat dans une boîte creuse ; amortissement bref | Faire sentir que MOU se prive volontairement du téléphone. Plus doux que la fermeture |
| S3 — boîte fermée | Plan2, bord du panneau touchant vers3,55s | Fermeture pleine et courte, matériau cohérent avec le petit coffre ; pas de gros choc métallique | Confirmer que le téléphone est enfermé. C'est le contact le plus net de la préparation |
| S4 — décision irréversible | Plan2, pression3,9s puis engagement4s | Minuscule clic de commande, suivi d'un cliquet mécanique distinct ; un seul événement avec une cause et sa réponse | Le doigt commande puis le verrou répond. Ne pas additionner deux impacts de même poids |
| S5 — travail abandonné | Plan6, vers11,78s | Petit contact de crayon contre le plateau ; très court roulement seulement s'il est montré | Rendre sensible le renoncement au travail sans simuler de l'écriture sur une feuille restée vierge |
| S6 — poids de l'attente, facultatif | Plan8, vers15,2s si l'assise bouge réellement | Un unique grincement discret de chaise, lié au déplacement du corps | Donner une présence physique à MOU. À retirer si aucun mouvement de chaise n'est visible ; MOU ne porte pas de vêtement à faire froisser |
| S7 — libération | Plan10→11, vers23s, exactement au changement du verrou | Bref déclic mécanique ; garder l'attaque utile, pas le début arbitraire du fichier | Faire entendre l'événement attendu après une pause. Pas de « tada », accord musical ou bip qui annonce déjà la réaction |
| S8 — récupérer l'objet | Plan11, charnière bougeant vers23,2–23,75s | Frottement ou petit mouvement de charnière qui suit la levée ; fin propre lorsque le panneau s'arrête | Donner une matière à l'ouverture. La main qui saisit ensuite le téléphone peut rester silencieuse |

Ces huit événements comprennent les deux micro-actions de S4. S6 n'est pas
une obligation de remplir la piste : si la chaise n'est pas animée, sept
événements suffisent. Aucun impact de réception n'est prévu pour un saut
coupé avant son atterrissage. Aucun bruitage d'interface ne doit apparaître
sans action correspondante sur le téléphone.

## Ambiance, pauses et fin

Une ambiance de pièce très faible peut relier les plans : fond réel stable,
sans conversation identifiable, musique ou changement de volume à chaque
coupe. Cette ambiance n'est pas encore choisie ni enregistrée. Elle doit
être vérifiée par écoute et accompagnée de sa provenance/licence exacte.

- **Plan4,6–7s :** premier regard à l'horloge sans ponctuation sonore. Le
  passage du temps doit se lire à l'image.
- **Plans7–9,12,25–21,7s :** plages calmes ; une seule présence matérielle
  éventuelle de chaise. Pas de soupirs procéduraux, ronflement en boucle,
  tick à chaque minute ou souffle ajouté pour expliquer le visage.
- **Plan10,21,7–23s :** retenir la respiration du montage avant le déclic.
  L'ambiance reste stable ou presque imperceptible ; éviter de créer un
  trou numérique qui redémarre brutalement.
- **Plans12–13,25,4–30s :** la joie revient au téléphone, puis la caméra
  révèle la feuille toujours vide. Ne pas surligner cette révélation avec
  un « boing », un trombone triste ou une sting. La contradiction visuelle
  doit parvenir au spectateur avant la fin.

## Voix et méthode de validation

La V2 proposée ici n'exige aucune nouvelle voix. Les banques Soundgen V1 et
V2 ont été rejetées par l'utilisatrice. Refaire la même synthèse en modifiant
la fréquence ne constitue pas une nouvelle interprétation de l'ennui ou de
la joie. Une voix future peut être facultative : prises non verbales
réellement jouées, cohérentes entre elles, écoutées seules puis sur la scène.
Aucun clonage ni promesse de naturel par les seuls paramètres.

Avant le prochain rendu final :

1. Écrire la cause visible et le repère d'accent de chaque S1–S8 dans la
   même timeline que les plans. L'image fonctionne d'abord sans son.
2. Choisir des prises concrètes. Conserver origine/licence exacte, version,
   découpe et transformations ; les candidats inclus ne sont pas automatiquement
   des choix artistiques acceptés.
3. Monter la préparation2,1–4,6s isolément pour distinguer dépôt, couvercle,
   bouton et verrou. Monter aussi la fin21,7–30s pour éprouver la pause et
   la libération, sans sons qui remplissent les cuts.
4. Effectuer une vraie écoute de la matière et du confort. Ici, cette étape
   n'a pas été exécutée ; une analyse RMS ou spectrale ne la remplace pas.
5. Faire les contrôles numériques utiles après le choix artistique : pas
   de saturation/clic de coupe, niveaux stables, accents sur leurs actions,
   absence de pompage, concordance du vrai MP4 avec les stems.

Python, FFmpeg et Audacity permettent ce montage avec les outils ouverts
retenus. Ce document ne déclare aucun nouvel enregistrement réalisé,
échantillon jugé à l'oreille, mix accepté ou film publié.
