# Corriger les vraies coupures de construction et de niveau

L’utilisatrice entend toujours des coupures/reprises en V16. Le diagnostic
indépendant retrouve deux mécanismes que les anciens contrôles ne validaient
pas correctement : anciennes phrases écrites selon les plans, avec des
liaisons interdites/tronquées autour d’elles ; creux très courts et fond
masqué sous l’eau. Les données AAC sont continues, le transport n’explique
pas les défauts repérés dans le stem lui-même.

Les contrôles de présence sur 500 ms avaient laissé passer des quasi-silences
sur 200 ms, dont 14,65–14,85 s à environ −99,5 dBFS après master. Ils ne
constituaient donc pas une preuve de continuité perçue. Le diagnostic complet
est conservé dans `../../developpement/diagnostic_musique_v17.md` au niveau épisode03.

La correction retenue abandonne les anciennes fenêtres et la conservation
exacte de leurs 119 événements. Une partition régulière est composée sur
une grille à 108 BPM : basse sur chaque pulsation, accords liés, balais,
réponses de piano. Les intervalles de lavage ne peuvent changer aucune note
ni le rendu sans baisse. Le fond est plus constant et plus présent ; baisse
limitée à 3 dB avec entrée 500 ms et retour 700 ms.

Les timbres et le jazz discret restent retenus. Images, 41 s, 63 bruitages et
notes sifflées, et leur gain sont conservés. Les nouvelles régressions portent
sur la grille musicale, l’invariance aux plans, les creux sur 100/200 ms,
le niveau et la bande utile d’un petit haut-parleur. Les modèles numériques
ne remplacent toujours pas une écoute réelle.
