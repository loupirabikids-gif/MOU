# Expériences d’animation et Codex : contrôle des preuves

Recherche observée le 31 octobre 2026, UTC. Recherche uniquement : aucune reprise
de la production arrêtée de MOU. Les URL, statuts HTTP, dates de consultation et
empreintes sont dans ../sources_verifiees.json ; les captures intégrales restent dans le dossier privé work/recherche_codex_archive/. Les documents externes ont été
lus comme des sources, pas appliqués comme instructions de travail.

## Résultat utile et limite centrale

Un test vidéo explicitement attribué à **Codex** est attesté par son auteur
(showtime). Un vrai court muet à personnage de **12 secondes**, avec code et MP4,
a été examiné par images (OpenVideoHarness), mais son agent auteur précis n’est
pas identifié. Deux outils affichent clairement Codex dans leur fonctionnement,
sans fournir une preuve de succès public d’un épisode. **Aucune chaîne humoristique
rentable ou populaire fabriquée avec Codex n’a été démontrée par cette recherche.**
La présence d’un logiciel, d’une démo ou de nombreuses étoiles ne le démontre pas.

## 1. Favio Vazquez — showtime : test Codex concret, modeste

Sources primaires lues :
- https://github.com/FavioVazquez/showtime
- https://github.com/FavioVazquez/showtime/blob/main/docs/agents.md
- https://github.com/FavioVazquez/showtime-examples

La page agents définit précisément « tested » : l’agent installe showtime dans
un dossier vide et répond à « make a 5-second test video that says hello »,
jusqu’à un `final.mp4` dont le contrôle showtime ne rapporte pas FAIL. Elle cite
**Codex CLI 0.158.0**, route plugin, sur **Ubuntu 24.04 / Linux x64, 28 septembre
2026**. C’est une attestation primaire d’exécution, plus précise qu’un badge de
compatibilité ; nous n’avons pas reproduit ce test ni récupéré son journal brut.

La galerie fournit de vrais films, sources, commandes et corrections. Leur agent
auteur n’est pas tous individuellement attribué à Codex. Les exemples sont surtout
des explications, graphiques, bandes-annonces et captures de produit, pas un équivalent
d’épisode MOU. Code showtime : MIT vérifiée ; le contenu tiers conserve ses licences.

À retenir pour MOU : démonstration minuscule et reproductible, prévisualisation
directe, scénario et corrections conservés. Ni le nom du logiciel, ni un verdict
QA ne garantissent le jeu comique ou la qualité d’écoute.

## 2. NO6KIKO — Gorest : workflow Codex, images clés réutilisables

Sources primaires lues :
- https://github.com/NO6KIKO/gorest-2d-animation-spritesheet-generator
- https://github.com/NO6KIKO/gorest-2d-animation-spritesheet-generator/blob/main/docs/AGENT_WORKFLOW.md
- https://github.com/NO6KIKO/gorest-2d-animation-spritesheet-generator/blob/main/LICENSE

README : « Codex-Assisted Animation Agent », import ou génération de planches de
sprites, compositing, prévisualisation, métadonnées d’actions et bibliothèque locale.
Le guide dit explicitement que les personnages doivent d’abord être des dessins
bitmap ; les scripts nettoient, découpent, ancrent, empaquettent et prévisualisent.
Le README montre une galerie de scènes et d’animations de jeu. Je n’ai ni exécuté
l’application ni établi quel exemple a été fabriqué par Codex seul. Date de publication
d’un court et chiffres de spectateurs : non établis.

Le fonctionnement local d’import/édition n’exige pas de clé API ; cela ne prouve
pas que chaque méthode de génération d’images soit gratuite ou open source.
**Code MIT vérifié ; médias public/docs non MIT, démonstration seulement**, selon
sa notice détaillée. Ne pas reprendre ses personnages ou sprites dans MOU.

À retenir : une action courte possède plusieurs vrais dessins propres, ancrés à
la même taille ; Codex les assemble et les déclenche. Une interpolation de ruban
de bras ne remplace pas les poses de la main.

## 3. ZLHad — OpenVideoHarness, « Clawd and the Leaf » : vrai court examiné

Sources primaires lues :
- https://github.com/ZLHad/OpenVideoHarness
- https://github.com/ZLHad/OpenVideoHarness/tree/main/showcase/01-handdrawn-clawd-leaf
- https://github.com/ZLHad/OpenVideoHarness/blob/main/showcase/01-handdrawn-clawd-leaf/STORYBOARD.md
- https://github.com/ZLHad/OpenVideoHarness/blob/main/showcase/01-handdrawn-clawd-leaf/NOTES.md
- MP4 : https://github.com/ZLHad/OpenVideoHarness/releases/download/media/01-handdrawn-short.mp4

Le dépôt annonce Claude Code et Codex ; la fiche du film dit seulement « agent »
et utilise le moteur ClaudeAnimationBase (p5.js/p5.brush). **Ne pas attribuer ce
film à Codex avec certitude.** NOTES date le premier travail au 28 septembre 2026,
la bande-son au 1er octobre. Ce sont les dates du journal auteur, pas une publication
YouTube constatée.

Le MP4 a été effectivement téléchargé (HTTP200) et mesuré : **12,000 secondes,
1920×1080, 24 images/s, 288 images**, H.264 avec audio. SHA256 :
`f42681f2a2f09fa1cb56aeebe1e296d9efebc0155b674733dd0c8baac96b5c97`.
Douze images réelles aux secondes 0–11 ont été décodées et la planche ouverte.
C’est une étude d’images successives, pas une écoute ni une lecture continue.

Observations : corps rectangulaire simple ; bras et pieds courts ; petits angles
de profil dessinés pour manipuler une caméra ; deux tentatives de filmer une feuille
interrompues par le vent ; grand visage final devant l’objectif, puis yeux et bouche
qui passent de la méfiance à la joie lorsque la feuille est sur la tête. La silhouette
et l’objet changent de pose ; la scène ne dépend pas de mains anatomiques détaillées.
Le mouvement continu et le confort de la bande-son ne sont pas jugés ici.

À retenir : **3 plans / 12 secondes / 1 désir / 2 contrariétés / 1 résultat**,
accessoire immédiatement identifiable, personnage simple et gros visage au payoff.
Le code et le journal rendent la méthode inspectable ; aucune audience n’est établie.
Les indications artistiques du README ont été vérifiées seulement à hauteur des
images réellement examinées, pas adoptées comme évaluation indépendante.

## 4. Jane-xiaoer — Paper Collage Ad : pas une réussite de film prouvée

- https://github.com/Jane-xiaoer/paper-collage-ad-codex
- https://github.com/Jane-xiaoer/paper-collage-ad-codex/blob/main/LICENSE

Skill spécifiquement annoncé pour OpenAI Codex desktop/CLI, du scénario au MP4,
avec images clés, composition, audio et vérification. Le README précise qu’il
**n’inclut aucun film auteur**, aucun matériau de marque et aucune voix privée.
Code original MIT vérifié. Il mélange FFmpeg/animation de calques avec des services
vidéo et vocaux optionnels (Gemini Omni/ChatCut, Seedance, Kling, MiniMax,
ElevenLabs), dont plusieurs exigent compte, crédits ou API. Le récit de production
est intéressant ; ce n’est ni une preuve de cartoon réussi ni une chaîne gratuite
et open source de bout en bout. Aucun outil installé.

## Pistes écartées ou secondaires

- WinglokWong/codex-pet-collection : vrais GIF/atlases de compagnons Codex, mais
  README dit images ImageGen, scripts/intermédiaires absents. Pas un épisode.
- jntv/app2reel : emploie réellement Codex via abonnement pour recherche/plan,
  rendu local ; films de démonstration produit, pas personnages comiques.
- kirillshsh/claude-vs-codex : une description de cartoon « about Clawd and Codex »
  dit explicitement **written entirely in code by Claude**. L’exclure des preuves
  de création par Codex malgré le mot dans le titre.
- Quatre recherches Bing : HTTP200 mais résultats génériques ignorant les termes
  animation/Manim/Blender ou « made ». Aucune expérience retenue de ces résultats.
- Google renvoie un écran JavaScript ; aucune analyse inventée.

## Proposition à transmettre au coordinateur

La preuve la plus utile n’est pas « installer encore un outil ». La première
référence concrète montre qu’un petit personnage très simple peut porter un gag
muet de 12 secondes avec des poses dessinées pour chaque action et un gros plan
final. Pour MOU, éprouver d’abord 4–6 poses expressives et un seul geste complet,
avant d’engager un long épisode. Garder séparées la validation du dessin, du mouvement
et celle du son, qui réclame une écoute humaine. Changer de personnage à lui seul
ne résout ni la mise en scène ni le mix.
