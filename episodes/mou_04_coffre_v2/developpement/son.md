# Le coffre V2 — fabrication sonore

État : 3 novembre 2026. Premier montage sonore fabriqué ; **aucune écoute n'a pu être effectuée dans cette interface**. La reconnaissance des matières, leur confort et leur efficacité comique restent à vérifier en lecture réelle. Les mesures qui suivent ne constituent pas cette validation artistique.

## Décisions appliquées

La chronologie à huit événements est figée au SHA256 `7747922f07c05dccc098804d8a6a31d8c91a4af545a979296eceec7e2c455c1d`. Chaque son correspond à un contact ou mécanisme visible. Les huit sons utilisent huit originaux distincts, issus de quatre packs CC0 de Benjamin Burnes / Abstraction. Les cinq anciens originaux de la V1 ne sont pas utilisés dans la nouvelle banque.

Les ellipses et sauts de temps restent silencieux. La prise du téléphone ne reçoit pas de tap sans contact. La chaise n'étant pas animée, son grincement est omis. Aucune nouvelle voix, musique, note de récompense, synthèse de bip ou ambiance artificielle n'a été ajoutée. Les gains sont fixes ; aucun compresseur, ducking ou variation de volume de plan en plan.

| Action | Temps | Original du pack | Découpe de l'original | Durée livrée |
| --- | --- | --- | --- | --- |
| Appel / vibration | 0,650 s | Fans and Drones / Small Fan | 6,000–6,420 s | 0,420 s |
| Téléphone déposé | 2,800 s | Retail Therapy / Plastic Thump 1 | 0,010–0,225 s | 0,215 s |
| Couvercle fermé | 3,550 s | Retail Therapy / Plastic Case 1 | 2,233–2,415 s | 0,182 s |
| Bouton pressé | 3,900 s | Smol Mechanisms / Click Button 3 | 0,000–0,090 s | 0,090 s |
| Verrou engagé | 4,000 s | Smol Mechanisms / Ratchet Muted 3 | 0,145–0,235 s | 0,090 s |
| Crayon abandonné | 11,78125 s | Retail Therapy / Rattling Cheap Wood 1 | 0,065–0,240 s | 0,175 s |
| Verrou libéré | 23,000 s | Smol Mechanisms / Spring Loaded Blade 2 | 0,007–0,155 s | 0,148 s |
| Charnière en mouvement | 23,200 s | Toolbox Rummaging / Metal Hinge 1 | 1,850–2,400 s | 0,550 s |

Deux substitutions sont explicites : la vibration vient d'un moteur de petit ventilateur enregistré, et non d'une capture de téléphone ; le contact du crayon vient d'une courte prise de bois, et non d'un crayon enregistré. Elles restent à juger à l'écoute. Les noms des fichiers de bibliothèque ne prouvent pas leur mode de capture. Les notices et empreintes garantissent la traçabilité des fichiers, sans revendiquer une inspection à l'oreille.

## Traitement et placement

Les originaux sont conservés sans modification dans `assets/son_v2/originaux/`. Traitement reproductible par Python/SciPy/FFmpeg : décodage mono48kHz, retrait de DC, filtrage fixe passe-bande de deuxième ordre en phase nulle, courtes fondus d'entrée/sortie, réglage fixe du pic par effet. Aucun oscillateur, étirement, boucle, resynthèse ou son vocal.

`audio_cues.at` place le début du fichier sur l'action. Les courtes attaques utiles sont documentées, sans décalage caché : énergie significative dans les 0–12,1 ms pour les contacts, et pics utiles environ 3–32 ms après les contacts. Le pic d'une vibration continue n'est pas un repère d'impact. La charnière s'arrête à 23,75 s, comme le mouvement prévu.

Les gains et panoramiques explicites de la chronologie sont respectés. Le couvercle reçoit le niveau le plus fort de la préparation ; le bouton reste plus discret ; le verrou possède une source différente du bouton et de sa libération. Le calme après l'ouverture est intentionnel : aucune ponctuation ne commente la révélation de la feuille vide.

## Livraison et contrôles exécutés

- `audio/mix.wav` : 30,000 s, 1 440 000 échantillons, stéréo48kHz PCM16.
- SHA256 du mix : `b477ff3138a4a2abaec529633ea233fa0dc36c74d7ddc631a7708ad5177ceffe`.
- SHA256 de `assets/son_v2/bank.json` : `dc7e64388ba753f9c7640e05695defe7a684b9e020d4519db3285105af24830c`.
- Huit cues aux huit horaires attendus ; huit sources distinctes ; aucune source d'ellipse/tick/UI musicale utilisée.
- Pic d'échantillon : −12,13 dBFS ; zéro échantillon saturé. Le RMS global de −47,06 dBFS inclut de longues pauses et ne permet pas d'évaluer le confort sonore.
- Somme PCM des huit stems égale exactement au mix ; débuts et fins des huit effets à zéro ; dernières données non nulles à 23,74890 s.
- Contrôles détaillés : `audio/controls.json`, `mix_report.json`, `cues.csv` et `cues.json`.

`audio/demonstrations/banque_effets_v2.mp4` permet d'entendre séparément les huit matières aux gains du mix, avec leur intitulé et leur source. Deux WAV isolent la préparation et la libération : `preparation_2p1_4p6.wav` et `liberation_21p7_30.wav`. La démo n'est pas une validation à l'écoute déjà faite.

## Provenance et reproduction

`assets/son_v2/LICENCES.md` et `provenance.json` répertorient URL raw exactes, commit, SHA256 des originaux et notices signées CC0. L'inventaire de recherche conserve aussi les candidats non retenus ; les trois fichiers candidats inutilisés sont identifiés dans la provenance. La licence des sons tiers ne s'étend pas aux créations originales MOU.

```sh
.venv/bin/python episodes/mou_04_coffre_v2/sources/son.py --prepare
.venv/bin/python episodes/mou_04_coffre_v2/sources/son.py --timeline episodes/mou_04_coffre_v2/chronologie.json --output episodes/mou_04_coffre_v2/audio/mix.wav
```

La validation encore nécessaire consiste à écouter le montage réellement encodé, particulièrement 2,1–4,6 s (hiérarchie des quatre contacts) et 21,7–30 s (pause, déclic, charnière, chute). Ne pas déclarer les sons « naturels », « professionnels » ou « acceptés » à partir des seuls niveaux et SHA.
