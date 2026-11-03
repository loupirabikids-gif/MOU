# Mix du coffre — V2

`mix.wav` est le nouveau premier montage à huit bruitages matériels, 30 s, stéréo48kHz PCM16. Il utilise la chronologie V2 figée, sans voix, musique, bips synthétiques, ticks d'ellipses, compresseur ou ducking.

`stems/foley.wav` reproduit le mix ; les huit `stems/cue_*.wav` isolent chaque événement dans sa position temporelle. Leur somme PCM égale exactement le mix. `cues.csv/json` indiquent les horaires, gains, sources et attaques. `controls.json` et `mix_report.json` contiennent les vérifications numériques.

La démo `demonstrations/banque_effets_v2.mp4` présente séparément les huit matières aux gains du mix. Deux courts WAV permettent d'écouter la préparation et la libération.

Aucune écoute n'est possible dans cette interface : le naturel, la compréhension des matières, leur équilibre perçu et la justesse comique ne sont pas validés à l'oreille. La vibration est une substitution Foley par moteur de petit ventilateur ; le contact crayon est une substitution bois. Les sources et notices CC0 signées sont dans `../assets/son_v2/`. Aucun droit nouveau n'est attribué aux créations MOU.

Détails de fabrication : `../developpement/son.md`. Sources reproductibles : `../sources/son.py`. Les V1 et anciens films n'ont pas été modifiés.
