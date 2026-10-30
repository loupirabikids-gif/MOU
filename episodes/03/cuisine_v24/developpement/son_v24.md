# Son V24 — jazz réduit et bruitages de papier

La commande est de baisser le jazz et d'ajouter les effets proposés. Le film
se termine à 43 secondes. La composition V23, ses instruments et ses variations
aux lavages sont conservés dans un PCM de référence gelé et autonome.

## Dosage

Le fond musical baisse de **4 dB** sur toute sa durée. Les 39 événements
non musicaux encore dans le montage gardent leurs PCM traités, leurs instants
et leur gain final V23 de **+3,50 dB**. Le seul ancien événement écarté est
l'essuyage du tablier à 43,75 s, séquence retirée du nouveau montage.

La musique garde une seule continuité. Elle se termine par un fondu cosinus
au carré de 42,4 à 43 s, aligné avec la pose finale tenue. Les regards de la
clôture ne déclenchent aucun bruitage supplémentaire. Aucune nouvelle
normalisation de sonie ne remonte le fond après sa réduction.

## Dix-huit effets originaux ajoutés

- Dix frottements secs : deux passages pour chacun des cinq essuyages.
- Cinq froissages : un par transformation du papier en boulette.
- Trois contacts feutrés manquants dans la poubelle : 21,27, 26,77 et 32,77 s.

Les premiers et derniers impacts déjà présents sont conservés ; les deux
contacts finaux restent distincts à 39,10 s sur le tas et 39,85 s au sol.
La petite dernière déchirure garde son niveau plus faible que les grandes.

Les frictions suivent des pics de vitesse relative des deux moufles. Le relevé
utilise 240 états par essuyage de l'animation V23, conservée avant 40,25 s :
différence main droite–main gauche, dérivée numérique, maxima après l'approche
et séparation minimale de 22 % de la durée d'essuyage. Les centres et vitesses
mesurés sont gelés dans `sources/foley.py` et consignés dans les événements
`sync` de `audio/provenance.json`. Le début sonore précède le centre du geste
de la moitié de la durée du court frottement.

Chaque bruitage est synthétisé localement avec NumPy : bruit coloré chaud,
grains irréguliers fenêtrés et enveloppes douces. Les frottements sont brefs ;
les froissages comportent quatre petites compressions ; les contacts ont une
attaque arrondie de 3,5 ms. Les graines et niveaux sont conservés dans le code.
Les petites feuilles ont des effets moins forts que les grandes bandes.
Aucun échantillon externe, voix, modèle payant ou requête réseau n'est utilisé.

## Recette et sources autonomes

`audio/reference_v23/provenance.json` conserve les événements d'origine.
`audio/reference_v23/musique_v23.wav` est le PCM musical V23 inclus, SHA-256
`31b1eb935a51e7a93b02812b9bde5d2e0809094dbc048010a9f4fa9dabf13e38`.
Les fichiers `processed_v22/` et `cuisson_v22.wav` fournissent les événements
existants. La partition MIDI/JSON, `music.py`, la banque FluidR3 et ses notices
MIT restent inclus pour une édition ultérieure de la composition.

`son.py` coupe la référence à 2 064 000 trames stéréo, multiplie par
`10**(-4/20)` et l'enveloppe de fin, puis arrondit en PCM. Il synthétise les
18 nouveaux événements et additionne les 58 événements listés à `start_sample`.
L'enveloppe globale de bord 8/35 ms est appliquée puis arrondie ; le gain fixe
`10**(3.5/20)` est appliqué puis arrondi en PCM 16 bits. Seuls les événements
listés participent au mix, pas les références ou les extraits.

Le contrôle mesuré avant le fondu donne **−3,999985 dB** de baisse musicale.
Le mix de 43 s est en stéréo, 48 kHz, avec **−27,95 LUFS**, **−13,71 dBTP**
et aucun échantillon écrêté. Ces mesures décrivent le signal et sa fabrication.
**Le modèle ne peut pas écouter l'audio dans cette session : le confort et
l'agrément sonore ne sont pas certifiés par ces chiffres.**

## Exports et reproduction

- `audio/mix.wav` : mix du film entier, 43 s.
- `audio/test_fin_v24.wav` : échantillons exacts de 40,25 à 43 s, soit 2,75 s.
- `audio/extrait_bruitages_v24.mp3` et `.wav` : passage 11,25–26,25 s du mix.
- `audio/jazz_seul_15s.mp3` et `.wav` : nouveau niveau musical seul au gain du film.
- `audio/jazz_seul_complet.wav` : musique seule sur la durée du film.
- `audio/foley_v24/` : dix-huit nouveaux effets séparés et modifiables.

```sh
.venv/bin/python -B episodes/03/cuisine_v24/sources/son.py
```

Empreintes et paramètres : `controle/audit_son.json`,
`controle/audit_audio_v24.json` et `audio/provenance.json`.
Les gros stems et l'ancien extrait de huit secondes copiés de V23 ont été
retirés du seul dossier V24 ; V23 et ses sources restent conservés.
