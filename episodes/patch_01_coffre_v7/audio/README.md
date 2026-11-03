# Mix V7 — voix aiguë, réactions distinctes

La banque originale V2 est réellement régénérée par Soundgen 3.0.0 sous
R 4.5.0, sans modèle neuronal ou voix clonée. Les WAV, paramètres, graines,
accents et licences des outils sont conservés sous `../assets/voix/`.

`sources/son_base.py` reconstruit les 18 effets antérieurs. `sources/son.py`
ajoute cinq prises V2 avec un gain fixe par prise. Les cibles RMS sont 1,5 dB
plus basses que dans V6 ; le gain est aussi soumis à un plafond de crête mono.
Pas de musique, compresseur ou ducking par scène.

Les accents des vrais WAV déterminent les placements et les petites ouvertures
de bouche. L'inspiration commence sur le visage après la coupe ; le bâillement
finit avant le changement de plan. Le rire et le « hm » possèdent deux accents.
Le début du fichier n'est pas traité comme son accent émotionnel.

Le mix est PCM16 stéréo à 48 kHz ; `base_mix.wav`, les quatre stems et les cues
sont inclus. `mix_report.json`, `controls.json` et le QA documentent les
mesures et les empreintes. Ils ne remplacent pas une écoute ; aucune qualité
perçue, confort ou reconnaissance émotionnelle n'est déclarée validée ici.
