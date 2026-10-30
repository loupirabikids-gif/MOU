# Musique V27 — guitare bossa et dérive discrète

30 octobre 2026. Révision sonore sur les images V26 inchangées. La partition
est originale ; les échantillons d'instruments sont une ressource tierce libre.
Aucune écoute ni appréciation de confort n'est revendiquée.

## Arrangement réellement construit

248 notes : guitare nylon GM24 et contrebasse GM32, sans piano ni percussion.
La guitare alterne accords de doigts syncopés sur croches droites et pouce
sur les premier et troisième temps. La basse soutient fondamentale et quinte.
Quatre patrons de syncope alternent ; les voicings de sixte/neuvième, mineure 7
et dominante évoluent dans un centre en la majeur compatible avec le sifflement.

La grille est globale et ne redémarre à aucun changement de plan. De 0 à 7 s,
le jeu reste régulier. Ensuite apparaissent de petites variations de placement
et d'accord. À partir de 20,75 s, le tempo passe progressivement de 108 à 112 BPM,
jusqu'à 31,65 s. Les attaques de guitare reçoivent une dérive limitée : plage
réellement utilisée −9,979 à +3,504 cents, sans transposition spectaculaire.
Un accord du dixième bar est retardé de 48 ms ; il s'agit d'une hésitation écrite
au score, pas d'une interruption du fichier musical.

Le seul creux isolé de 19,5–20 s a reçu une anticipation écrite de basse :
fa#2 (MIDI 42) au beat 35, soit 19,444 s, vélocité 29 et durée d'un temps.
La note précédente est raccourcie avant cette relève. Les autres silences
rythmiques de la bossa sont conservés, sans couche de bruit ni gain variable.

Les attaques ajoutées durent 16 ms pour la guitare et 40 ms pour la basse. La
calibration musicale unique vise −41,5 dBFS RMS sur 0,5–31,5 s avant l'atténuation
légère aux lavages. La basse est équilibrée à −9 dB RMS de la guitare. Aucun
détecteur de volume, compresseur de bus ou normaliseur de scène n'est ajouté.

## Rupture et conclusion

Le fond musical se termine exactement à 32,000 s, avec un bord de 6 ms pour
éviter une discontinuité d'échantillon. Aucun fragment de réverbération ou de
basse ne persiste après cette coupure.

Une seule note courte de guitare revient de 36,25 à 36,75 s : mi 4, vélocité 31,
avec une retombée de hauteur de +6 à −18 cents pendant son attaque/décroissance.
Elle se termine avant la pose finale 37,25–38 s. Les plages 32–36,25 et 36,75–38 s
sont exactement nulles dans le stem musical ; les voix/effets relèvent du mix.

## Banque et reproduction

`assets/FluidR3_MOU_bossa.sf2` contient seulement les deux presets utilisés :
guitare nylon notes 48–77, basse notes 33–57. Les 13 échantillons PCM et leurs
boucles sont conservés. La banque pèse 1 720 132 octets, SHA256 :
`fa64be8254db1fbe0ffde1121beb14aae96d4fe0f7f485a82ebee1768276936f`.

La source complète FluidR3 GM a été vérifiée au SHA256
`74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`.
La notice MIT de Frank Wen/Toby Smithe est incluse. Le JSON de la banque
conserve la provenance du paquet Debian et distingue ses preuves historiques
de la vérification locale actuelle. Sept notes frontières et représentatives
ont été rendues avec FluidSynth sans réverbération/chorus, sur source et
sous-ensemble : sorties identiques échantillon par échantillon, aucune muette.

`subset_soundfont.py` reproduit cette extraction depuis le SF2 complet. Le
rendu de l'épisode n'a besoin que de la petite banque incluse et de FluidSynth.
`music.render_background(38, specification)` renvoie le signal stéréo 48 kHz,
les paramètres et la partition, les stems guitare/basse, et la référence sans
atténuation de lavage. `write_midi` écrit aussi tempo et bends par corde ;
le PCM issu de Python reste la référence du mix, pas un lecteur MIDI externe.

## Contrôles numériques réellement faits

Deux rendus complets successifs ont donné des tableaux float identiques.
Leur somme de stems est exactement égale au signal livré par la fonction.
Les zéros après 32 s et après 36,75 s sont vérifiés sur tous les échantillons.

Le rendu final privé mesure −41,692 dBFS RMS sur 0,5–31 s et un pic de
−25,231 dBFS. La note finale culmine à −36,309 dBFS avant gain du mix. La plage
RMS sur fenêtres de 0,5 s passe de 17,766 à 11,580 dB après l'unique anticipation
de basse ; percentiles 5/95 : −46,998 / −40,119 dBFS. La fenêtre 19,5–20 s passe
de −57,394 à −51,217 dBFS, sans remonter l'ensemble de la musique. Elle reste
un repos plus doux de la phrase, et non un fichier coupé ou relancé.
Ces écarts décrivent les attaques et décroissances des instruments ; ils ne
prouvent pas une continuité perçue ou un confort d'écoute. La rupture à 32 s
est intentionnelle.

Preuves privées : `work/music_v27/check.json`, `parameters.json`, les stems
WAV et `partition.mid`. Aucun de ces rendus privés ne remplace le mix final.
