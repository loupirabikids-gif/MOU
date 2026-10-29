# Critique indépendante — continuité musicale V17

Le diagnostic V16 est conservé dans
`episodes/03/developpement/diagnostic_musique_v17.md`. Cette revue vérifie
les causes matérielles qui y étaient identifiées : anciennes frontières de
partition, quasi-extinctions courtes et fond trop masqué par l’eau.

La V17 corrige ces points dans le code, le score et les WAV réellement produits.
Avis favorable sur cette correction ciblée, sous les limites d’écoute précisées
ci-dessous. Aucun défaut matériel bloquant retenu dans ce périmètre.

## Fichiers réellement examinés

- `sources/music.py` : composition et enveloppe de volume.
- `audio/musique_sans_baisse.wav` et `audio/musique_cuisine.wav` : PCM réel.
- Les cinq `audio/cN_eau.wav`, la chronologie et les rapports de production.
- MP4 final identifié par métadonnées et empreinte, 41 s, H.264 1080 × 1920
  à 24 images/s et piste AAC. SHA-256 :
  `993307805fb8ffb9c904e66f2af85342fd1f42c03e955960b5b425c971c0fb8b`.

Les mesures de cette revue utilisent les WAV ; le contrôle de correspondance
AAC/WAV et des images du MP4 relève des vérificateurs de livraison distincts.
Aucune écoute ou lecture sonore continue du MP4 n’est revendiquée ici.

## Une partition indépendante des plans

`compose()` lit désormais la durée et le tempo seulement. Les anciennes
fenêtres V15, leurs exclusions et leurs fins de phrase imposées par le montage
ont disparu. La forme harmonique évolue par mesures de quatre pulsations.
La basse, les accords réguliers et les balais poursuivent leur grille pendant
les pauses de la mélodie.

Vérification indépendante : le score reste strictement identique après
modification des champs `windows`, `original_cooking_windows`, `duck_intervals`
et `duck_db`. Il contient 594 événements. Les 74 attaques de basse suivent
les pulsations entières de la grille à 108 BPM, erreur numérique maximale
inférieure à 8,1 × 10⁻¹⁰ pulsation.

Les accords successifs sont écrits avec des portes MIDI de 0,98 pulsation
pour un intervalle d’une pulsation. Le code vérifie aussi l’absence de
chevauchement de portes du même pitch : le relâchement d’une ancienne note
ne doit pas annuler une note retriggerée plus récente. Les relâchements sonores
peuvent ainsi assurer la liaison sans utiliser ce chevauchement ambigu.

La banque et les quatre familles de timbres sont conservées : contrebasse,
piano électrique doux, piano et balais. La partition est reconstruite pour
obtenir cette régularité ; le maintien exact des 119 anciens événements
n’est plus un objectif qui contraint les raccords.

## Les vraies quasi-coupures sont corrigées

Même méthode indépendante pour V16 et V17 : PCM16 stéréo moyenné en mono,
gain master exact `2.124210976406158`, RMS non pondéré après master. Chaque
temps ci-dessous désigne le début d’une fenêtre de 200 ms.

| Fenêtre de la musique livrée | V16 | V17 |
| --- | ---: | ---: |
| 14,65–14,85 s | −99,522 dBFS | −33,024 dBFS |
| 15,85–16,05 s | −82,529 dBFS | −29,590 dBFS |
| 16,45–16,65 s | −86,100 dBFS | −33,722 dBFS |
| 29,00–29,20 s | −87,072 dBFS | −36,292 dBFS |

Les deux plus fortes anciennes remontées à la reprise sont aussi réduites.
Sur les 500 ms avant/après 13,5 s : +4,74 dB en V16, +0,05 dB en V17.
À 21,5 s : +5,79 dB en V16, −0,08 dB en V17. Le phrasé peut avoir ses
variations naturelles de niveau ; elles ne sont plus programmées par les
frontières de cuisine et de lavage.

Ces observations constituent une correction mesurée des vrais défauts
précédents. Elles vont au-delà du simple passage d’un seuil « non nul »
sur une fenêtre de 500 ms.

## Présence du fond et place laissée à l’eau

Sur le corps de 2 à 40,5 s, mesure indépendante :

| Mesure après master | V16 | V17 |
| --- | ---: | ---: |
| Musique brute sans baisse | −35,992 dBFS | −31,000 dBFS |
| Musique avec baisses | −36,681 dBFS | −31,777 dBFS |
| Musique avec baisses, bande 300–4500 Hz | −42,867 dBFS | −35,191 dBFS |

Le fond dans les médiums gagne donc environ 7,68 dB sur cette mesure. Le proxy
300–4500 Hz est un filtrage numérique idéal, pas un modèle de haut-parleur
ou une preuve d’audibilité sur téléphone.

Pendant les écoulements effectifs des cinq cycles, l’eau seule dépasse encore
la musique de 12,0 à 13,5 dB RMS en large bande, et de 14,9 à 15,9 dB dans
ce proxy de médiums. Elle reste dominante numériquement, tout en masquant
moins profondément le fond qu’en V16, où cet écart dans les médiums atteignait
25,6 à 29,4 dB.

La baisse de la musique est légère, à 3 dB, avec une entrée de 500 ms et un
retour de 700 ms. Cette enveloppe n’intervient pas dans l’écriture du morceau.
Les stems bruts et baissés permettent son contrôle séparé. Les niveaux et
les trois notes sifflées restent soumis aux audits de conservation des
bruitages, sans nouvelle normalisation de ces effets.

## Avis et limites

La correction traite les causes mises en évidence par le retour de
l’utilisatrice : accompagnement régulier indépendant des plans, disparition
des quasi-extinctions réelles, fond plus présent et baisse moins abrupte au
lavabo. Aucun raccord supplémentaire de notes ou de volume n’est demandé
sur les observables examinés.

Cette revue ne valide pas une qualité musicale à l’oreille, une préférence
artistique, l’intelligibilité sur un téléphone réel ou la réussite comique.
L’extrait et l’épisode corrigés permettent ce jugement d’écoute. Les anciens
tests « un synthé continu / signal non nul » ne doivent plus être présentés
comme une validation de continuité perçue.
