# PATCH — bibliothèque vocale V1

Douze vocalisations originales synthétisées avec **Soundgen3.0.0, réellement
exécuté sous R4.5.0**. Aucun modèle neuronal, voix clonée, enregistrement humain,
service payant ou dialogue n'intervient dans ces prises.

- [Écouter les douze prises avec leurs étiquettes](PATCH_Voix_V1_ecoute.mp4?raw=true)
- [Même planche en WAV](PATCH_Voix_V1_ecoute.wav?raw=true)
- [Manifeste et repères de synchronisation](bank.json)
- [Licence des sorties et des outils](LICENCES.md)

## Intentions

| Identifiant | Intention | Première prise |
| --- | --- | --- |
| `resolve_hm` | Décision, petit son bouche fermée | 0,305s |
| `bored_exhale` | Ennui, expiration descendante | 0,519s |
| `sleepy_yawn` | Somnolence, petit bâillement | 0,833s |
| `effort_small` | Effort bref, utile à d'autres scènes | 0,265s |
| `surprise_inhale` | Surprise, inspiration sans voisement | 0,247s |
| `relief_chuckle` | Joie, deux petites expirations rieuses | 0,427s |

Chaque intention possède deux variantes reproductibles. Le premier essai
semé de chaque recette est proposé pour l'intégration ; ce choix n'est pas
un classement à l'oreille. Les mots « ennui », « joie » et « somnolence »
décrivent les intentions de fabrication, pas une reconnaissance perceptive
certifiée. **Aucune audition n'est revendiquée dans cet environnement.**

La direction est une voix douce, légère, sans mots, avec des hauteurs conçues
entre205 et310Hz environ et le même jeu de formants pour les six intentions.
Le soupir et le bâillement deviennent plus soufflés, tandis que l'inspiration
est non voisée. Le rire contient deux accents distants d'environ0,210s.

## Niveaux et synchronisation

Les maîtres sont des WAV mono PCM16 à48kHz. Le traitement retire l'offset,
adoucit les extrémités, règle le RMS des portions actives puis limite le pic
à−14dBFS. Aucun compresseur, gate ou normalisation variant par scène.
Un silence de fin de12ms est ajouté ; aucun maître ne contient d'échantillon
écrêté. Le gain du film reste distinct des maîtres et figure dans sa timeline.

`accent_seconds` repère le centre du maximum d'une enveloppe RMS de20ms.
Pour le rire, `accent_points_seconds` contient les deux pics séparés, et
`accent_seconds` reste le premier. Pour caler un son :
`début = accent_visuel − accent_seconds`. Garder le souffle d'anticipation
et vérifier la bouche autour de l'accent ; commencer le fichier sur l'accent
visuel désynchroniserait le jeu. Le niveau numérique ne garantit ni naturel,
ni confort, ni compréhension émotionnelle.

## Reproduction locale

Sur cet environnement Debian13 x86_64, Python, GCC14, FFmpeg et les
bibliothèques système sont déjà disponibles. Le script suivant télécharge
R4.5.0 et les dépendances dans `work/`, compile les paquets ouverts depuis
leurs commits et vérifie les empreintes. Il n'écrit pas dans les répertoires
système, ne change pas les permissions et conserve le proxy/TLS hérités.

```sh
.venv/bin/python personnages/PATCH_voix_v1/sources/install_runtime.py
.venv/bin/python personnages/PATCH_voix_v1/sources/run_generation.py
.venv/bin/python personnages/PATCH_voix_v1/sources/build_preview.py
```

Python doit disposer de NumPy, SciPy et CairoSVG. Sur un autre système,
installer R≥4.1 et les paquets Soundgen/tuneR/signal/phonTools selon sa
procédure normale, puis exécuter `sources/generate.R` et
`sources/finish_bank.py`. L'installateur Debian n'est pas annoncé portable
sur toutes les distributions. Il télécharge du code exécutable seulement
aux URLs et empreintes consignées dans les reçus.

Les paramètres exacts, graines et formants sont sous `parametres/` ; les
recettes partagées sont dans `sources/generate.R`. Les sources des quatre
paquets ont été comparées aux archives des commits enregistrés. Une seconde
installation isolée et une nouvelle synthèse sont contrôlées dans
`controle/reproduction.json`. Cela vérifie la reproductibilité numérique,
pas la qualité artistique. Aucun binaire R ou paquet tiers n'est redistribué
avec la banque ; les enregistrements et nos scripts suffisent pour le mix.
