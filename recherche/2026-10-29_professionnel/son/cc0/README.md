# Deux textures Foley à licence CC0 explicite

Recherche observée le 29 octobre 2026, UTC (horodatages exacts dans les JSON).
Les fichiers ont été téléchargés et sondés avec FFprobe. Aucune écoute n’a
été réalisée ; ils ne sont pas validés pour leur qualité perceptive.

## Fichiers disponibles

Auteur indiqué par les notices des deux packs : **Benjamin / Ben Burnes,
Abstraction**. Le dépôt `lavenderdotpet/CC0-Public-Domain-Sounds` constitue
le miroir consulté. Les liens de téléchargement sont épinglés au commit
`f2b6264f9ab89fabc266914c3654685d68c5a39b`.

| Fichier local | Fichier d’origine | Durée et format | Utilisation à tester, limite |
| --- | --- | --- | --- |
| `assets/ben_burnes_page_turn_1.wav` | `bb - Books, Paper, Writing (Jan 2021)/Page Turn 1.wav` | 3,436 s ; 44,1 kHz, stéréo, PCM16 | Texture de papier à découper. Une page tournée n’est pas un essuie-tout déroulé ou une déchirure. |
| `assets/ben_burnes_knife_tap_1.wav` | `Micro Pack - Kitchen Knives/Big Knife - Tap 1.wav` | 2,564 s ; 44,1 kHz, stéréo, PCM16 | Contact de couteau à examiner. Un tap ne démontre pas le bruit d’un couteau traversant une carotte. |

Chaque pack possède un `_README.txt` qui dit explicitement :

> These sounds are public domain (Creative Commons 0). You are free to
> enhance, reuse, remix, or do whatever with these files.

Les notices sont conservées dans `preuves/notice_paper.txt` et
`preuves/notice_knife.txt`. Le texte CC0 général du dépôt est également
conservé. Les droits ne sont donc pas déduits d’une licence de logiciel.
Les informations consultées n’explicitent pas le procédé d’enregistrement
de chaque WAV ; aucune méthode ou qualité « naturelle » n’est affirmée sur
la seule base du nom de fichier.

**[Provenance complète, URL immuables et SHA256](assets_provenance.json)**.
L’attribution est fournie par souci de traçabilité, même si les notices la
présentent comme facultative. Aucun son n’a été intégré à la production.

## Trois dépôts effectivement examinés

1. [lavenderdotpet/CC0-Public-Domain-Sounds](https://github.com/lavenderdotpet/CC0-Public-Domain-Sounds) :
   collection consultée, licence CC0 à la racine et notices explicites des
   packs ci-dessus. Le sous-dossier `40-cc0-water-splash-slime-sfx` propose
   des bulles, éclaboussures et boucles d’eau, mais aucun nom ne confirme un
   robinet de cuisine. Il n’a pas été importé à l’aveugle. Le dossier
   `MissLavs Sounds` n’a pas non plus fourni de robinet identifié.
2. [wyzowl/sfx-kit](https://github.com/wyzowl/sfx-kit) : README et licence
   déclarent explicitement les **sons et les données sous CC0**. Les
   métadonnées de placement, d’attaque et de niveau sont utiles. Le README
   indique toutefois que **tous les sons sont synthétisés par code, sans
   enregistrement ni bibliothèque tierce** : ce n’est pas une source de
   captations réelles. Aucun de ses WAV n’a été téléchargé dans cette étude.
3. [Bodila51/opus-sound-layer](https://github.com/Bodila51/opus-sound-layer) :
   code MIT, bibliothèque construite par téléchargement de packs Kenney et
   de sons Freesound déclarés CC0 ; les sons ne sont pas stockés dans ce
   dépôt. Ce code fournit des méthodes utiles de découpe, fondus et examen
   spectral. Ses affirmations de droits doivent être vérifiées sur chaque
   source effectivement téléchargée. Le code n’a pas été exécuté et aucune
   bibliothèque externe complète n’a été importée.

## Résultat et limites

Deux WAV dont le pack déclare explicitement CC0 sont disponibles, avec leurs
notices et empreintes. **Aucun échantillon de robinet naturel vérifié n’a été
trouvé dans cette recherche bornée.** Il vaut mieux le signaler que rebaptiser
une pluie, une éclaboussure ou une synthèse comme une captation de lavabo.

La recherche GitHub publique et les lectures HTTP sont conservées dans
`search_results.json`, `http_*.json`, `notices.json` et `preuves/`.
Le JSON de recherche GitHub place actuellement les résultats dans
`payload.blackbirdSearchRoute.results` ; une première extraction au mauvais
niveau a été corrigée. Les résultats conservés n’incluent pas les champs de
session/CSRF des pages HTML.

Ces deux textures sont des **candidats de montage**, pas une garantie de
confort sonore. Une écoute humaine reste nécessaire pour décider leur emploi.
