# PATCH — voix V2, aiguë et couinante

Douze nouvelles prises réellement synthétisées avec **Soundgen 3.0.0 sous
R 4.5.0**. Cette direction répond au rejet de la V1 : une identité plus aiguë,
avec six articulations et rythmes différents. Aucune voix réelle clonée,
aucun mot, modèle neuronal ou service payant. La V1 reste intacte.

- [Écouter les douze nouvelles prises](PATCH_Voix_V2_squeaky_ecoute.mp4?raw=true)
- [Même planche en WAV](PATCH_Voix_V2_squeaky_ecoute.wav?raw=true)
- [Manifeste, paramètres et accents](bank.json)
- [Mesures comparatives V1 / V2](controle/contraste_v1_v2.json)
- [Licences des outils et droits du projet](LICENCES.md)

## Une identité commune, six intentions différentes

Le conduit vocal de 11 cm et les formants neutres communs, rehaussés de 30 %
par rapport à V1, définissent la même petite voix. Les hauteurs sont conçues
vers 390–880 Hz, avec de faibles variations entre les deux prises. Le résultat
est filtré doucement au-delà de 5 kHz, avec attaques et fins adoucies.

| Intention | Articulation et rythme conçus | Durée, prise 1 |
| --- | --- | --- |
| Décision | Deux petits « mm » nasaux, second plus affirmé ; lèvres fermées | 0,325 s |
| Ennui | Expiration en O, hauteur descendante et souffle qui prend la suite | 0,522 s |
| Somnolence | A long qui s'ouvre progressivement, voix puis souffle | 0,834 s |
| Effort | Bref grunt plus rugueux et resserré | 0,246 s |
| Surprise | Inspiration suivie d'un tout petit couinement montant | 0,238 s |
| Joie | Deux petites syllabes rieuses plus hautes, seconde infléchie | 0,412 s |

Dans V1, `mouth` avec `vocalTract=NA` ne déplaçait pas les résonances :
l'ouverture agissait surtout sur le basculement lèvres/nez. La V2 conserve
les mêmes formants neutres pour toutes les intentions mais fixe le conduit
à 11 cm. Les changements M/O/A déplacent donc réellement les résonances,
au lieu de reproduire seulement la même bosse de hauteur et de volume.

Les quatre prises les plus voisées ont une estimation de hauteur médiane
2,16 à 2,68 fois celle de V1. L'estimation de fondamentale du bâillement et
de l'inspiration est déclarée non fiable, car souffle et formants peuvent
produire de faux pics d'autocorrélation. Les paramètres conçus, les spectres
et les enveloppes sont conservés ; ils ne prouvent pas la reconnaissance
d'une émotion ou le naturel de la voix.

**Aucune audition n'a été possible ici.** La première graine de chaque recette
est retenue pour le montage, sans prétendre à un classement à l'oreille.
Les deux variantes sont proposées pour comparer les interprétations.

## Niveaux et accents

Les maîtres sont mono PCM16 à 48 kHz, sans écrêtage. La conversion applique
un coupe-bas à 100 Hz, un passe-bas doux à 5 kHz, un fondu de bord et un gain
fixe par prise. Le pic reste au plus à −14 dBFS ; le gain du film est distinct.
Aucun compresseur ou ducking par scène. Les noms d'émotion sont des intentions.

`accent_seconds` est le premier pic d'énergie utile. Les deux accents du
« hm » et du rire sont dans `accent_points_seconds`. Les centres RMS sont
mesurés sur 20 ms. Le placement d'un son se calcule par
`début_audio = accent_visuel − accent_seconds` ; ne pas confondre le début
silencieux du fichier et son accent. Garder le bâillement avant la coupe et
l'inspiration sur le visage revenu à l'écran.

## Reproduction avec le runtime déjà installé

Depuis la racine du dépôt, avec Python, NumPy, SciPy, CairoSVG et FFmpeg :

```sh
.venv/bin/python personnages/PATCH_voix_v2_squeaky/sources/run_generation.py
.venv/bin/python personnages/PATCH_voix_v2_squeaky/sources/measure_contrast.py
.venv/bin/python personnages/PATCH_voix_v2_squeaky/sources/build_preview.py
```

L'exécution réutilise `work/voix_soundgen_runtime/` et écrit les nouveaux
bruts uniquement sous `work/voix_squeaky/`. Aucune réinstallation de R et
aucune écriture dans la banque V1. `run_generation.py --runtime CHEMIN`
permet de sélectionner le runtime R local. L'installateur Debian 13 x86_64
inclus peut le préparer si nécessaire ; les archives de dépendances sont
fixées aux URLs et empreintes des reçus. Il ne prétend pas être portable
sur tout système d'exploitation.

Les recettes et graines sont dans `sources/generate.R` et `parametres/`.
Une seconde exécution a comparé les douze bruts et douze fichiers de
paramètres : voir `controle/reproduction.json`. Ce contrôle ne remplace
pas l'écoute. Aucun binaire R ni archive tierce n'est livré avec la banque.
