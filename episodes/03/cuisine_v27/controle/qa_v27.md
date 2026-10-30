# Contrôle indépendant V27 — son seul

**Contrôle final passé.** Deux MP4 entièrement décodés : 38 s, 912 images,
24 images/s, 1080 × 1920. La version muette est le fichier V26 exact ; le flux
H.264 et les 912 horodatages du film avec son lui sont identiques. Les sources
visuelles, la chronologie, le rig et les quatre références protégées sont
inchangés. Aucun rendu d'image supplémentaire n'a été nécessaire.

Le WAV contient 1 824 000 trames stéréo à 48 kHz/16 bits, sans saturation.
La corrélation entre l'AAC décodé et le WAV actuel, sans décalage, vaut
0,997439444. La pause de 32 à 32,5 s contient exactement 24 000 trames stéréo
nulles ; son noyau AAC de 32,06 à 32,44 s est également numériquement nul.
Le WAV reste nul de 37,25 à 38 s pendant la dernière pose.

Les 63 événements et leurs empreintes PCM sont vérifiés. Les 46 éléments
conservés de V26 sont comparés directement aux références : mêmes PCM,
instants, longueurs et types. Les cinq accents vocaux totalisent 0,98 s et
respectent les instants prévus. Les cinq stems (guitare, basse, effets, voix,
ambiance) sont vérifiés avec leurs deux silences. Le fond musical est nul
après 32 s en dehors de la note située entre 36,25 et 36,75 s.

Les originaux et conversions des sources vocales ainsi que leur notice CC0
ont les empreintes attendues. La méthode d'enregistrement et l'auteur
original restent non vérifiés, comme indiqué dans leur provenance.
Le gain de livraison fixe de +3,5 dB et le gel des producteurs sont contrôlés.

La première exécution complète avait passé les contrôles média et son.
L'ajout du contrôle direct des 46 références a révélé une différence de schéma
du contrôleur : leurs instants sont stockés en secondes, pas en start_sample.
Le contrôleur convertit maintenant ces secondes en échantillons ; la reprise
complète est passée, sans changement de producteur, PCM ou MP4.

**Limites :** aucune écoute ni transcription effectuée. Ces mesures ne
certifient ni douceur, naturel, absence perceptive de mots, reconnaissance
d'émotions ou réussite comique. Le rapport détaillé est audit_final.json.
