# Accompagnement jazz sur une seule grille — V17

L’utilisatrice entend encore des coupures et reprises dans V16. L’absence de
silence numérique ne démontrait pas une continuité musicale. L’ancienne
partition gardait les phrases composées pour cinq fenêtres distinctes et
tronquait les liaisons devant ces fenêtres ; leur pulsation se décalait donc
aux anciennes reprises. Sous l’eau, le fond devenait aussi très faible.

## Construction de la solution

`music.compose()` utilise uniquement la durée et le tempo. Les anciennes
fenêtres, les plans et les gestes n’interviennent plus dans la partition.
La basse joue chaque pulsation entière à 108 BPM, les accords de piano
électrique répondent sur un contretemps régulier légèrement balancé, et les
balais assurent un accompagnement stable. De petites réponses de piano suivent
une forme musicale de huit mesures, indépendante des raccords de l’image.
Le centre tonal reste en la majeur, avec A6, D6, Bm7 et E9 ; les instruments
de jazz discret TimGM6mb restent les mêmes. Le piano mélodique attend la fin
des trois notes sifflées originales.

Chaque instrument est rendu une fois sur les 41 secondes. Les notes de même
hauteur n’ont pas de portes MIDI qui se chevauchent : un ancien `noteoff`
ne peut donc relâcher une voix plus récente. Les relâchements naturels des
instruments se superposent au reste de l’accompagnement. Aucun pad artificiel
n’est ajouté pour satisfaire un test de non-zéro.

## Présence et volume sous l’eau

Un seul gain musical constant calibre le corps du morceau à environ
−31 dBFS RMS après le master conservé. Cette calibration ne dépend d’aucun
plan ni intervalle de lavage. Les accords dans les médiums renforcent la
présence sur petits haut-parleurs ; la basse n’est pas la seule composante
continue du fond.

L’enveloppe est ensuite appliquée à cette musique complète : baisse légère
de 3 dB aux cinq inserts lavabo, descente de 500 ms et remontée de 700 ms.
Il n’y a pas de baisse supplémentaire aux coups de couteau, au sel ou aux
anciennes limites de phrases. Les seuls fondus de la piste sont son entrée
de 20 ms et sa sortie de 220 ms. La référence `musique_sans_baisse.wav`
permet de mesurer directement l’automation et de séparer son effet du phrasé.

## Contrôles réellement effectués

La partition est identique lorsque les fenêtres visuelles et les baisses
sont déplacées. Une seconde synthèse avec ces fenêtres modifiées produit
une référence PCM brute identique à l’octet près. Les 63 fichiers de bruitages
et notes sifflées restent identiques à V16 ; leur gain master précis
2,124210976406158 est conservé.

Le diagnostic se fait sur des fenêtres de 100, 200 et 500 ms, et sur un
proxy mono limité à 300–4500 Hz, plutôt que sur un simple seuil de non-zéro.
Le rapport `controle/audit_musique_v17.json` fournit les minima, percentiles,
mesures d’automation et empreintes. Ces mesures expliquent la correction
technique ; elles ne constituent pas une écoute perceptive du morceau.

Partition originale, rendu local FluidSynth 2.4.4, banque tierce TimGM6mb
GPL-2 fournie et créditée. Aucun morceau ou boucle téléchargé.
