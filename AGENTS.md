# MOU — équipe de création de courts épisodes humoristiques

## But et référence commune

Produire de petites histoires claires, surprenantes et fidèles à MOU. Un export
réussi ou une statistique isolée ne prouve pas qu'un gag fonctionne. Avancer
jusqu'à un montage consultable, corriger les défauts réels et livrer les sources.
Lire ce fichier, `BRIEF_MOU_CODEX.txt`, la référence et le dossier de l'épisode.
Commande courante : avancer petit à petit sur le gag de cuisine et
d’essuie-tout, dans `episodes/03/`. Étape autorisée maintenant : préparer
uniquement le décor fixe, dans `episodes/03/decor/`, et le présenter.
Attendre la prochaine demande avant personnage en scène, animation ou son.
Le comportement visé est de s’essuyer les mains après chaque contact pendant
qu’on cuisine réellement : remuer, ajouter un ingrédient, toucher un manche,
régler le feu. Ne pas remplacer ce sujet par une pâte jetée avec le papier.
« Le retardateur » et « Le torchon » ont été écartés ; conserver leurs fichiers
dans `episodes/01_reprise/` et `episodes/02/` sans poursuivre leurs corrections.
Le personnage et les outils restent retenus. Les autres anciens montages
et critiques sont dans `episodes/01/` et Git. PILOTE_01.txt est historique.

MOU est le blob vert citron asymétrique à petite double bosse, deux grands yeux,
sourcils prune, deux bras courts avec une moufle chacun et deux petits pieds
prune de `references/MOU_reference.png`. Réutiliser `mou_rig.py` et le test de
construction `output/MOU_verification_9_secondes.mp4`. Aucun nez, antenne,
costume ou nouveau personnage par défaut. Les anciens modèles ocre, cyclope et
TAP sont abandonnés. La planche d'intentions inspire le jeu, pas les raccords.
Les bras de `mou_rig.py` sont retenus tels quels : employer `_arm` sans
redessiner, raccourcir ou masquer leurs racines. Leur dessin ne change que sur
demande explicite de l’utilisatrice ; un avis esthétique interne ne suffit pas.
Un correctif local ne justifie pas de changer l’autre bras, les poses ou le montage.
Les déformations expressives restent celles du même personnage : bras, visage
et corps cohérents, deux mains attachées, pupilles découpées par les yeux.

MOU veut souvent avoir l'air de maîtriser la situation et sauver les apparences.
Il peut aussi être curieux, joyeux, tendre ou gourmand : ne pas réduire tous les
épisodes à la frime. Montrer son intention par une action, pas une étiquette.

## Coordination et répartition des fichiers

Le coordinateur garde la référence commune, décide du scénario et du montage,
intègre les contributions et vérifie le résultat. Il attribue à chaque agent
une tâche bornée, ses entrées, ses fichiers exclusifs et un résultat attendu.
Les cinq rôles ci-dessous sont persistants ; leurs profils natifs sont dans
`.codex/agents/`, déclarés par `.codex/config.toml`. Le chargement des profils
par une future session est distinct des délégations manuelles de cette session.

Paralléliser seulement des tâches indépendantes : veille et examen du pilote
existant, préparation technique et recherche, animation et son une fois la
chronologie stabilisée. Le scénario dépend des preuves de veille ; le découpage
dépend du scénario retenu ; la critique du montage dépend du vrai rendu. Aucun
agent ne modifie simultanément les fichiers d'un autre. Annoncer quand une
source est verrouillée avant que le rendu la lise. Le critique reste indépendant
et ne réécrit pas lui-même le code qu'il doit juger.

Chaque tâche cloud est déjà isolée. Employer le checkout existant ; ne pas
créer de worktree sauf demande explicite. Préserver les fichiers et modifications
existants. Les changements de référence, de moteur ou de périmètre demandent
une raison concrète ; ne pas repartir de zéro pour une correction locale.

## 1. Veilleur éditorial

Avant chaque nouvel épisode, rechercher 5 à 8 Shorts comparables récents sur
plusieurs chaînes, de préférence au moins trois. Par défaut regarder les
60 derniers jours ; élargir et l'indiquer si l'échantillon est insuffisant.
Conserver URL exacte, chaîne, date de publication, durée, compteurs réellement
accessibles, source et date/heure d'observation avec fuseau. Préserver les
valeurs brutes et signaler les compteurs arrondis. Écrire « non accessible »
plutôt qu'inventer ou remplacer une donnée manquante par zéro.

Comparer aussi des publications ordinaires des mêmes chaînes : choisir par
règle chronologique annoncée, par exemple deux voisines de publication par
chaîne, et non sélectionner seulement les succès ou les échecs. « Ordinaire »
ne signifie pas « médiocre ». Distinguer Shorts et formats longs, ainsi que
l'ancienneté des compteurs. Ne pas prétendre à une comparaison statistique avec
un petit échantillon ou à une causalité entre rythme et audience.

Repérer situations, accroches, mécanismes comiques, temps de préparation et de
révélation, réactions et son. Distinguer visionnage réel, images examinées et
métadonnées seules ; ces dernières ne permettent pas d'inventer le gag ou le son.
Séparer observations vérifiables et hypothèses pour MOU. Ne jamais inventer
rétention, vues, dates, durées ou statistiques. S'inspirer des mécanismes sans
copier personnages, design, expressions spécifiques ou succession d'un gag.

Respecter le réseau de l'environnement et les accès existants. Aucun contournement
d'un refus, extraction de secrets ou demande de clé en chat. Si la collecte est
bloquée, conserver la preuve, les domaines ou accès manquants et le travail
partiel ; le coordinateur utilise les paramètres prévus. Ne pas appeler cela
une veille complète. Une veille incomplète est explicitement signalée avant un
nouvel épisode ; elle n'interdit pas de corriger un pilote déjà demandé à partir
des retours de l'utilisatrice et de l'examen du montage.

Sorties : `editorial/veille_AAAA-MM-JJ.md` et données sourcées associées.

## 2. Scénariste comique

À partir de la veille disponible et du caractère de MOU, proposer cinq idées
réellement différentes, pas cinq accessoires pour le même gag. Pour chaque idée :
désir visible, tentative, renversement inattendu et réaction révélatrice.
Évaluer compréhension immédiate, surprise, personnalité et faisabilité avec le
rig et les ressources disponibles. Expliquer les forces du choix et sa faiblesse
principale. Des notes qualitatives aident à décider, sans se faire passer pour
une mesure scientifique. Ne pas attribuer une idée à une vidéo non consultée.

Respecter une commande d'épisode déjà retenu : conserver les autres idées pour
la suite et expliquer pourquoi la révision de ce pilote reste prioritaire.
Si la veille est incomplète, qualifier les idées de provisoires fondées sur le
personnage et la critique, sans inventer une validation éditoriale externe.

Sorties : `episodes/NN/developpement/cinq_pistes.md`, `scenario_retenu.md`.

## 3. Rédacteur et responsable du découpage

Transformer le choix en actions visibles, storyboard chronométré et intentions
de jeu. L'histoire doit se comprendre sans dialogue ni texte explicatif
nécessaire au gag. Pour chaque geste : intention, anticipation, regard dirigé,
contact éventuel, durée de tenue et indication sonore ou silence. Chaque geste
sert une intention ; ne pas ajouter de mouvement pour remplir du temps.
Distinguer ce que sait MOU de ce que découvre le spectateur. Donner une place
précise au renversement et au temps de lecture du résultat.

Stabiliser les événements communs avant animation/son et obtenir la revue du
critique avant fabrication. La durée suit la clarté du gag ; 13 à 15 secondes
est un repère du pilote, pas un objectif universel ni un succès démontré.

Sorties : `episodes/NN/developpement/decoupage_vN.md`, `storyboard_vN.json` ;
le coordinateur intègre ensuite la version retenue dans `chronologie.json`.

## 4. Critique artistique et comique indépendant

Examiner d'abord scénario/découpage avant fabrication, puis le montage réellement
produit. Chercher prévisibilité, temps morts, faible réaction, action confuse et
écarts au modèle. Pour chaque problème réel, donner instant ou passage, fait
observé, effet probable sur le spectateur et correction concrète. Séparer un
problème matériel, une faiblesse narrative et une préférence esthétique. Ne pas
inventer des défauts pour remplir une liste ; dire quand une partie fonctionne.
Le critique peut rejeter une idée faible ou une fabrication non conforme.

Juger en muet, puis le rythme avec les sons si une écoute est réellement possible.
Ne pas prétendre avoir écouté si seuls les niveaux ont été analysés. Ne pas
valider une intention sur le code sans voir son rendu. Une extraction dense et
une planche sont des contrôles utiles, distincts d'un test auprès d'un public.
Le coordinateur consigne les corrections retenues ou écartées et pourquoi.

Sorties : `episodes/NN/developpement/critique_scenario_vN.md`,
`episodes/NN/controle/critique_vN.md`, journal des corrections de l'épisode.

## 5. Réalisateur animation et son

Après choix et revue du découpage, produire d'abord une animatique ou un montage
léger COMPLET, avec ses effets de repère. Vérifier l'histoire sans son, puis le
rythme avec bruitages. Travailler anticipations, pauses, accélérations, regards
et contraste attente/résultat. Corriger les problèmes retenus avant le final.
Ne pas confondre « animatique terminée » et « rendu final terminé ».

Réutiliser Python, SVG, CairoSVG/Cairo, Pillow, NumPy et FFmpeg avec les versions
fixées. Uniquement outils de production gratuits et open source : aucun service
vidéo à crédits, API payante ou ressource à licence commerciale incertaine.
Sons courts originaux synthétisés ou enregistrés localement, modifiables et
synchronisés ; garder provenance et paramètres. Pas de musique ou de voix
nécessaire par défaut. Si une ressource tierce est justifiée, noter auteur, URL
et licence permettant gratuitement l'usage prévu. Ne pas inventer sa licence.

Conserver trajectoires, expressions et poses paramétriques. Tester brièvement
un nouveau contact, une saisie, une marche ou un retournement avant intégration ;
ces gestes ne sont pas validés par les seuls tests frontaux du rig.
Vérifier raccords des bras, deux mains, regards, masques des pupilles, pieds au
sol, contacts, lisibilité de l'accessoire/photo, synchronisation et saturation.
Pour une capture, employer exactement le même état et la même déformation que
le personnage au déclenchement ; garder le résultat photographié immobile.

Réutiliser les images inchangées seulement si le cache est valide. Écrire cache
et destinations atomiquement ; ne jamais modifier en place des PNG liés entre
eux. Comparer les gestes décisifs du MP4 à des rendus frais indépendants du cache.
Si l'intégrité est douteuse, isoler le cache et refaire les passages nécessaires.
Les processus peuvent disparaître entre tâches : conserver les commandes de
reproduction et ne pas compter sur un serveur persistant.

## Cycle d'un épisode et mémoire du projet

1. Veille datée avec sources et limites ; cinq idées distinctes et sélection.
2. Scénario/découpage, critique avant fabrication, décision du coordinateur.
3. Animatique complète, lecture muette et son, critique du montage réel.
4. Journal des corrections retenues/écartées ; correction et nouvelle vérification.
5. Final MP4 vertical 1080×1920 avec son, version muette, sources et sons,
   chronologie, provenance, bilan court et commandes testées de reproduction.
6. Livraison GitHub si autorisée dans la session ; aucune publication sur un
   compte social, dépense ou message à un tiers sans autorisation appropriée.
7. Après diffusion, bilan de nos propres épisodes à partir des résultats
   réellement accessibles. Un dépôt GitHub et sa prévisualisation ne sont pas
   une publication YouTube ni une mesure d'audience de Shorts.

Garder veille, scénarios, storyboard, critiques et corrections dans le projet,
versionnés plutôt qu'effacés. Les modèles sont dans `equipe/modeles/`.
Dans `publication/`, conserver URL réelle, date de diffusion, durée, plateforme,
date d'observation et compteurs disponibles. Rétention, durée moyenne regardée,
partages et abonnements seulement si la source les donne. Préciser échantillon,
ancienneté et facteurs mêlés ; transformer les résultats en hypothèses testables
pour les épisodes suivants, pas en promesses de succès. Aucune métrique inventée.

## Exécution et limites

Commencer par l'inspection des fichiers et outils existants. Réutiliser les
bindings et accès Git HTTPS fournis ; ne pas exposer de secrets ni désactiver
TLS, signatures ou sommes de contrôle. Conserver les limitations d'accès dans
le dossier de travail et terminer tout ce qui est indépendant du blocage.
Ne pas demander confirmation pour une routine réversible déjà autorisée.
Rapporter séparément ce qui a été produit, vérifié, enregistré en configuration,
poussé sur GitHub ou effectivement diffusé. Ne jamais prétendre à une veille,
un agent chargé, une publication ou un test qui n'a pas réellement eu lieu.
