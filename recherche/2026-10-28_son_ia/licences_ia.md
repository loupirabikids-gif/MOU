# IA audio : licences et utilité pour MOU

Recherche réelle sur sources officielles GitHub/raw, observée le28octobre2026
entre16h18et16h22, Africa/Casablanca (UTC+01:00). Les réponses HTTP, dates et
SHA256 des documents sont conservés dans `preuves/ia/fetches.json`.
Pas d’installation, de poids téléchargés, de génération ou d’écoute de modèle.
Le réseau autorise GitHub/raw ; les fiches de poids externes Hugging Face
n’ont pas été consultées et aucun refus d’accès n’a été contourné.

## Choix utile : Bark local pour quelques réactions non verbales

**[suno-ai/bark](https://github.com/suno-ai/bark)** peut être essayé pour de
petits soupirs, rires et sursauts de MOU, en complément du Foley. Il s’agit du
dépôt local Bark, pas d’une promesse de gratuité du service Suno Studio.

Sources consultées :

- [README officiel](https://github.com/suno-ai/bark/blob/main/README.md)
- [Licence MIT](https://github.com/suno-ai/bark/blob/main/LICENSE)

Preuves courtes du README :

> “pretrained model checkpoints, which are ready for inference and available for commercial use.”

> “Bark is now licensed under the MIT License, meaning it's now available for commercial use!”

Le fichier LICENSE contient bien la licence MIT. Le README distingue lui-même
le modèle de recherche génératif d’un TTS conventionnel. Les tags documentés
incluent `[laughter]`, `[laughs]`, `[sighs]`, `[gasps]`. Il mentionne des voix
aléatoires ou des presets et indique ne pas proposer de clonage vocal custom.
Cela donne une piste pour les réactions brèves sans dialogue, sans imiter une
personne réelle. La qualité d’un soupir seul et la stabilité d’un timbre MOU
restent à essayer et à écouter ; elles ne sont pas validées par la documentation.

Matériel **annoncé par le projet**, pas mesuré ici : CPU et GPU supportés ;
PyTorch2.0+ ; version complète autour de12GB de VRAM, petite version8GB ;
offload CPU possible pour des cartes plus petites, avec génération plus lente.
Ne pas reprendre les annonces de vitesse comme nos propres benchmarks.

Le logiciel et l’accès aux checkpoints sont annoncés gratuits/licenciés MIT,
mais le calcul, la RAM/VRAM et l’hébergement restent des ressources à fournir.
Il faudrait un environnement séparé de notre chaîne SVG/CairoSVG actuelle.
Les sons de couteau, d’eau, de déchirure et de poubelle restent plus faciles à
contrôler par enregistrement original puis montage précis.

## Autres IA examinées

| Projet | Code et poids : faits vérifiés | Ressources documentées | Décision pour MOU |
| --- | --- | --- | --- |
| [AudioCraft / AudioGen](https://github.com/facebookresearch/audiocraft) | Code MIT, poids CC-BY-NC4.0 explicitement distingués dans README et model card. | Docs AudioGen : GPU avec au moins16GB pour les modèles medium1.5B ; README Python3.9/PyTorch2.1.0. | Recherche possible ; ne pas retenir ces poids pour une production commerciale gratuite sans autre autorisation. Ne pas déduire une licence de tous les audios produits de la seule licence du code. |
| [stable-audio-tools](https://github.com/Stability-AI/stable-audio-tools) | Code MIT confirmé. Le README exige l’acceptation des termes du modèle Hugging Face avant l’utilisation de `stable-audio-open-1.0`. Licence exacte de ces poids non vérifiée ici. | README : PyTorch2.5+ ; développement Python3.10 ; options half precision. Aucun minimum de VRAM d’inférence confirmé dans les documents lus. | Piste optionnelle à tester après lecture de la licence du checkpoint exact ; ne pas annoncer toute la chaîne « MIT et commerciale » à partir du seul moteur. |
| [TangoFlux](https://github.com/declare-lab/TangoFlux) | README actuel : modèle “non-commercial, research-only”, licence Stability et restrictions WavCaps academic-only ; usage commercial exige enregistrement/licence séparée d’après ce même texte. | README annonce44.1kHz stéréo jusqu’à30s, avec benchmark surA40 ; pas notre mesure et pas une garantie CPU. | Non retenu comme solution de production commerciale gratuite. |

### Sources AudioCraft

- [README, rubrique License](https://github.com/facebookresearch/audiocraft/blob/main/README.md#license)
- [MIT du code](https://github.com/facebookresearch/audiocraft/blob/main/LICENSE)
- [Licence des poids](https://github.com/facebookresearch/audiocraft/blob/main/LICENSE_weights)
- [Fiche AudioGen](https://github.com/facebookresearch/audiocraft/blob/main/model_cards/AUDIOGEN_MODEL_CARD.md)
- [Prérequis AudioGen](https://github.com/facebookresearch/audiocraft/blob/main/docs/AUDIOGEN.md)

Citation de la fiche AudioGen :

> “Code is released under MIT, model weights are released under CC-BY-NC 4.0.”

### Sources Stable Audio Tools

- [README](https://github.com/Stability-AI/stable-audio-tools/blob/main/README.md)
- [MIT du moteur](https://github.com/Stability-AI/stable-audio-tools/blob/main/LICENSE)

Citation du README :

> “once you've accepted the terms for the model on Hugging Face”

Le modèle cité est `stable-audio-open-1.0`. La licence d’Open Small n’est pas
déduite de cette phrase ni de la licence MIT du dépôt. Les sorties et les
conditions d’un checkpoint précis doivent être traitées séparément du code.

### Sources TangoFlux

- [README, rubrique LICENSE](https://github.com/declare-lab/TangoFlux/blob/main/README.md#license)
- [Texte Stability fourni dans ce dépôt](https://github.com/declare-lab/TangoFlux/blob/main/STABILITY_AI_COMMUNITY_LICENSE.md)

Le README dit aussi :

> “Any commercial usage requires registering with Stability AI or obtaining a separate commercial license.”

Cette copie de licence ne prouve pas les conditions actuelles d’un autre
modèle de Stability AI. Ne pas transférer ses droits supposés à Open Small.

## Deux pistes vocales supplémentaires, secondaires

**[Kokoro](https://github.com/hexgrad/kokoro)** :
[README](https://github.com/hexgrad/kokoro/blob/main/README.md) et
[LICENSE Apache2.0](https://github.com/hexgrad/kokoro/blob/main/LICENSE) lus.
Le README annonce explicitement : “With Apache-licensed weights, Kokoro can
be deployed anywhere from production environments to personal projects.”
Modèle TTS82M ; annonce de poids Apache vérifiée dans ce texte. La qualité de
réactions non verbales n’y est pas démontrée : choix moins ciblé que Bark pour
MOU sans dialogue. Pas de benchmark effectué ni de licence de chaque pack de
voix externe consultée.

**[Chatterbox](https://github.com/resemble-ai/chatterbox)** :
[README](https://github.com/resemble-ai/chatterbox/blob/master/README.md) et
[LICENSE MIT du dépôt](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE)
lus. Le README documente les tags `[laugh]`, `[cough]`, `[chuckle]` de Turbo,
et un Nano110M compatible CPU selon le projet. Sa vitesse annoncée est une
affirmation des auteurs, non testée ici. Les exemples Turbo/Nano emploient
une référence audio. Les licences des checkpoints externes n’ont pas été
consultées : ne pas inférer leurs conditions complètes de la MIT du code.

## Recommandation éditoriale et technique

Pour cet épisode, enregistrer ou créer séparément cinq événements reconnaissables :
couteau sur carotte, ouverture d’eau, frottement/séchage, longue déchirure de
papier, impact mou dans la poubelle. Les raccourcir et les placer au contact
visible plutôt qu’accélérer uniformément tout le mix. Garder une vraie pause
avant le dernier geste pour que la chute se lise.

Bark est une **option d’essai** pour un soupir ou un rire bref original, sans
dialogue et sans clonage vocal. Aucun modèle examiné ne dispense d’écouter,
de trier et de synchroniser les clips. Un nom de logiciel gratuit ne constitue
pas une promesse de calcul gratuit ou de résultat immédiatement publiable.
