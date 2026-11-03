# Sources sonores V2 — licences et limites

Les huit effets utilisent des extraits de fichiers tiers du dépôt suivant, figé au commit `f2b6264f9ab89fabc266914c3654685d68c5a39b` :
https://github.com/lavenderdotpet/CC0-Public-Domain-Sounds

Auteur indiqué par les notices de pack : Benjamin Burnes / Abstraction. Chaque notice dit : « These sounds are public domain (Creative Commons 0). You are free to enhance, reuse, remix, or do whatever with these files. » Les notices originales sont conservées dans `evidence/`. Le texte juridique CC0 est également conservé (`repository_CC0.txt`).

La licence CC0 de ces fichiers tiers ne constitue aucune nouvelle licence du personnage, des images, du scénario ou des autres créations MOU.

| Fichier original | Utilisé | Notice locale | SHA256 de l’original |
| --- | --- | --- | --- |
| BB_Retail Therapy Sample Pack/Plastic Thump 1.wav | oui | evidence/retail_README.txt | `933474a0790754e98fba9f3f56f7b99f386a1b8c21819d422ba0bd31effc2932` |
| BB_Retail Therapy Sample Pack/Plastic Lid 1.wav | candidat conservé | evidence/retail_README.txt | `61ade84ae85a6d25f8ebb3db840e77a3ab9b6199f07552c823e23098bcb1db5f` |
| BB_Retail Therapy Sample Pack/Plastic Case 1.wav | oui | evidence/retail_README.txt | `bb679231c498a81033be026dcf1ae0d6052fca0815e6eaa594e393a00e1b389f` |
| BB_Retail Therapy Sample Pack/Rattling Cheap Wood 1.wav | oui | evidence/retail_README.txt | `03ce219b50741c390d6a5aac0b88058d6f7799274bca81b09410878d0ae50443` |
| bb - Smol Mechanisms (May 2021)/Click Button 3.wav | oui | evidence/smol_README.txt | `9a46e03777d033d333c39bcf03abdd68795848e5200d2526ce552786114e2736` |
| bb - Smol Mechanisms (May 2021)/Ratchet Muted 3.wav | oui | evidence/smol_README.txt | `9bfc93178e23261eaacea8c32061997218ea4ad0f97ce13d5cec6dd9696c5697` |
| bb - Smol Mechanisms (May 2021)/Spring Loaded Blade 2.wav | oui | evidence/smol_README.txt | `2ac0aab9e02fe84f91c6cb7757139c7bbe3a3cc5827f611dca6241135a71f700` |
| bb - Smol Mechanisms (May 2021)/Cable Coiler 2.wav | candidat conservé | evidence/smol_README.txt | `1bb7a8ca458b4eb4362b54407ae9fca501efa036cbc3b6b1e798c8a4784e07e0` |
| bb - Toolbox Rummaging (Sept 2021)/Metal Hinge 1.wav | oui | evidence/toolbox_README.txt | `c1fcb7d7234a74435e71650e529d5c5b1c5d54a297105ca418f7b68a26f9b522` |
| bb - Toolbox Rummaging (Sept 2021)/Metal Hinge 2.wav | candidat conservé | evidence/toolbox_README.txt | `1ce36197df1d9d8825d0570a4af0bee2fce0a90146faf8643e217525b5cea78f` |
| bb - Fans and Drones (Jul 2021)/Small Fan.wav | oui | evidence/fans_README.txt | `e20bff88c8948ca13784af53e6128af51e906eb06485fce5c8bae22b58fe3cc9` |

Les URL exactes de chaque original et de chaque notice, ainsi que leurs empreintes, figurent dans `provenance.json`. Les découpes, gains fixes, filtres et attaques mesurées figurent dans `bank.json` ; la recette reproductible est `sources/son.py --prepare`.

## Substitutions Foley explicites

- `phone_vibration` : extrait d’un petit ventilateur (`Small Fan.wav`), utilisé comme matière de moteur, et non présenté comme une prise de téléphone. Une seule impulsion, sans bip ni oscillateur.
- `pencil_place` : bref contact de bois (`Rattling Cheap Wood 1.wav`), substitut du contact du crayon sur le bureau. Aucun roulement ni son d’écriture inventé.

Les intitulés de packs et fichiers documentent ce que le distributeur a nommé. Ils ne prouvent pas seuls la méthode de capture ni la reconnaissance de l’objet à l’oreille. Aucune écoute n’a pu être effectuée ici : les sons restent des choix de réalisation à confirmer sur lecture réelle, malgré les contrôles de format, niveau et synchronisation.
