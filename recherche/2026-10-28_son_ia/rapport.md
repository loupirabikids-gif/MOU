# Son et IA gratuits pour MOU — recherche documentaire

Observation : **28 octobre 2026, Africa/Casablanca**. Les heures exactes, URL,
réponses HTTP et SHA256 sont dans `preuves_http.json` et `preuves/ia/fetches.json`.
Recherche GitHub publique réelle :
[foley sound generation](https://github.com/search?q=foley+sound+generation&type=repositories)
et [sound effects generator](https://github.com/search?q=sound+effects+generator&type=repositories),
puis lecture des README, licences et notices des dépôts sélectionnés.
Les résultats extraits sont dans `resultats_recherche.json` ; les pages HTML
complètes restent dans `work/` pour éviter de publier leur bruit et leurs jetons
de session anonymes. Aucun poids téléchargé, outil installé, son généré ni modèle
écouté au cours de cette recherche. Aucune mesure de vitesse personnelle.

## Recommandation pour cet épisode

**Priorité : une petite banque de bruitages originaux, montée dans Audacity et
calée sur les contacts visibles dans Kdenlive ou notre FFmpeg existant.**
Le couteau doit faire un son de coupe, le papier un son de papier et l’eau se
taire au moment où la main ferme le robinet. Un son reconnaissable et bien placé
aide davantage la compréhension qu’un accent synthétique générique à chaque geste.
Conserver Python/NumPy pour les petits accents originaux et le mix reproductible.

**IA optionnelle : Bark local**, pour quelques soupirs ou réactions non verbales
de MOU, après essai et écoute. Son dépôt annonce explicitement le code et les
checkpoints utilisables commercialement sous MIT. Il ne remplace pas une banque
de Foley contrôlable pour la carotte, l’eau et le papier. Aucune installation ou
migration de production n’est proposée à cette étape de recherche.

## Cinq candidats examinés

| Outil et sources officielles | Gratuité/licence vérifiée | Apport précis à MOU | Limite et intégration |
| --- | --- | --- | --- |
| **[Audacity](https://github.com/audacity/audacity)** — [README](https://github.com/audacity/audacity/blob/master/README.md), [LICENSE.txt](https://github.com/audacity/audacity/blob/master/LICENSE.txt) | Le README et la licence actuels annoncent **GPLv3** ; beaucoup de fichiers restent GPLv2-or-later. Éditeur libre et gratuit. La licence du logiciel ne donne pas de droits sur des échantillons tiers. | Enregistrer et nettoyer nos propres sons, sélectionner les bonnes attaques, monter plusieurs couches, faire varier les déchirures et impacts, exporter des WAV séparés. | Application de bureau Windows/macOS/Linux. Aucun modèle IA ni GPU spécialisé nécessaire au montage audio ordinaire ; pas de benchmark effectué ici. Le dépôt `master` est en transformation Audacity4 : privilégier une version stable, sans compiler la branche de développement pour ce petit besoin. |
| **[Kdenlive](https://github.com/KDE/kdenlive)** — [README](https://github.com/KDE/kdenlive/blob/master/README.md), [COPYING](https://github.com/KDE/kdenlive/blob/master/COPYING) | README : « free and open-source video editor ». Texte GPLv3 fourni dans COPYING. Le dépôt GitHub est un miroir officiel ; développement principal sur KDE Invent. | Regarder réellement la scène avec ses sons, déplacer un coup de couteau jusqu’à son contact sur la planche, comparer une pause, raccourcir un rituel et vérifier les raccords. Accepte nos exports d’images/vidéo sans recréer le personnage. | Interface graphique de montage. Nouveau poste de contrôle humain, pas moteur d’animation automatique. L’export FFmpeg actuel peut rester la sortie de production. Aucun calcul d’IA requis pour cette utilisation. |
| **[JSFXR](https://github.com/chr15m/jsfxr)** — [README](https://github.com/chr15m/jsfxr/blob/master/README.md), [UNLICENSE](https://github.com/chr15m/jsfxr/blob/master/UNLICENSE), [package.json](https://github.com/chr15m/jsfxr/blob/master/package.json) | Bibliothèque ouverte sous **Unlicense**, usage commercial explicitement permis. Le README distingue une offre **Pro** payante : elle n’est pas nécessaire pour utiliser la bibliothèque libre et exporter une onde via `toWave`. | Créer un petit « plop », clic, accent élastique ou sursaut original, enregistrer les paramètres et réutiliser une même signature sonore de MOU. Pas de poids ou de données d’entraînement à obtenir. | Générateur orienté effets de jeu/8bits ; ne pas lui confier tous les sons réalistes de cuisine. Bibliothèque JS utilisable dans le navigateur ou Node ; pas de GPU IA. Le site `sfxr.me` est indiqué par le README mais n’a pas été consulté ici. |
| **[Bark local](https://github.com/suno-ai/bark)** — [README](https://github.com/suno-ai/bark/blob/main/README.md), [MIT](https://github.com/suno-ai/bark/blob/main/LICENSE) | README explicite : checkpoints « available for commercial use » et licence MIT. Il s’agit du dépôt Bark local ; aucune gratuité du service commercial Suno Studio n’en est déduite. | Essayer des réactions `[laughs]`, `[sighs]`, `[gasps]` pour rendre un doute, un soulagement ou un emballement plus expressif, sans phrase ni dialogue nécessaire au gag. | Génératif : peut dévier du prompt ; clips à écouter, trier et couper. Docs : CPU et GPU supportés ; environ12GB VRAM pour le modèle complet,8GB pour la petite variante ; offload possible mais plus lent. Ces valeurs viennent des auteurs, pas d’un essai ici. Poids et calcul sont distincts : machine/hébergement à fournir. |
| **[Foley-Omni](https://github.com/SAIL-PRLab/Foley-Omni)** — [README](https://github.com/SAIL-PRLab/Foley-Omni/blob/main/README.md), [LICENSE](https://github.com/SAIL-PRLab/Foley-Omni/blob/main/LICENSE), [MODEL_LICENSE](https://github.com/SAIL-PRLab/Foley-Omni/blob/main/MODEL_LICENSE), [notices tierces](https://github.com/SAIL-PRLab/Foley-Omni/blob/main/THIRD_PARTY_NOTICES.md) | Code propre Apache2.0 et checkpoint Foley-Omni MIT, **mais** le README signale des utilitaires EDM2 CC-BY-NC-SA4.0 et des checkpoints MMAudio CC-BY-NC4.0 dans la chaîne. Le badge MIT ne couvre donc pas toute la production. | Piste de recherche intéressante : bruitages conditionnés par la vidéo et le texte ; le modèle annonce aussi parole/musique et permet un prompt de bruitages seulement. | **Non retenu comme chaîne commerciale gratuite prête à l’emploi.** Docs : clips jusqu’à10s ; environnement testé Python3.10,CUDA12.4,PyTorch2.6,FlashAttention2.7.4. Aucun minimum VRAM confirmé dans ces pages. Il faudrait découper l’épisode, recaler les sons et résoudre les droits des composants avant un essai de production. |

## Deux pièges supplémentaires vérifiés

- **[AudioCraft/AudioGen](https://github.com/facebookresearch/audiocraft)** :
  [code MIT](https://github.com/facebookresearch/audiocraft/blob/main/LICENSE),
  [poids CC-BY-NC4.0](https://github.com/facebookresearch/audiocraft/blob/main/LICENSE_weights).
  La [fiche AudioGen](https://github.com/facebookresearch/audiocraft/blob/main/model_cards/AUDIOGEN_MODEL_CARD.md)
  distingue expressément ces deux licences. La
  [documentation AudioGen](https://github.com/facebookresearch/audiocraft/blob/main/docs/AUDIOGEN.md)
  annonce au moins16GB GPU pour les modèles medium1.5B. Ne pas recommander ces
  poids comme solution gratuite de production commerciale.
- **[Stable Audio Tools](https://github.com/Stability-AI/stable-audio-tools)** :
  moteur [MIT](https://github.com/Stability-AI/stable-audio-tools/blob/main/LICENSE),
  mais le [README](https://github.com/Stability-AI/stable-audio-tools/blob/main/README.md)
  demande d’accepter les termes du checkpoint exact sur Hugging Face. La licence
  des poids d’Open1.0 ou d’Open Small n’est pas déduite de la licence du moteur.
  Pas de consultation externe autorisée de ces fiches dans cette recherche.

Les détails sur TangoFlux, Kokoro et Chatterbox sont conservés dans
`licences_ia.md`. Ils ne sont pas nécessaires à la recommandation immédiate.
LMMS a aussi été lu : logiciel libre de composition musicale, moins ciblé ici
que le montage de bruitages d’Audacity. Aucun choix n’est fondé sur un essai ou
une écoute que nous n’avons pas réalisés.

## Rendre la scène de carotte compréhensible avec le son

1. Trois coups de coupe bien distincts, chacun au contact du couteau et de la
   planche ; l’autre main stabilise la carotte et les rondelles restent visibles.
2. Regard vers la main, puis clic de commande **avant** l’eau ; arrêt du filet
   au moment de fermeture visible.
3. Long froissement de déroulage puis déchirure nette : la quantité excessive
   doit se voir et s’entendre. Bref frottement pour lire le séchage.
4. Lâcher, puis impact doux dans la poubelle ; garder chaque ancienne boulette.
   L’impact devient plus mat sur le papier accumulé.
5. À chaque répétition, réduire les pauses et les déplacements superflus, tout
   en conservant les attaques qui identifient les gestes. Garder une courte
   suspension avant le dernier réflexe. Ne pas accélérer uniformément tout le
   film et le son au point de changer les timbres ou de masquer la causalité.

Les durées et le rythme restent des choix de scénario à tester sur une animatique.
Ces recommandations ne constituent ni une écoute du prochain montage ni une
validation comique par un public.
