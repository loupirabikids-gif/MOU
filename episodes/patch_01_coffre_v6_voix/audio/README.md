# Mix V6 — voix espacées, effets V5 conservés

`sources/son_base.py` reconstruit les 18 effets historiques à gains fixes.
`sources/son.py` garde leur PCM intact dans `base_mix.wav`, ajoute les cinq
prises vocales Soundgen prévues dans `chronologie.json`, puis écrit le mix
PCM16 stéréo 48 kHz et quatre stems : Foley, UI, ticks et voix.

Les WAV de voix sont contrôlés par leur empreinte. Chaque cue comporte un
accent de jeu et une cible RMS ; le gain fixe calculé pour la prise respecte
un plafond de crête mono de 0,19. Aucune modulation du fond d'une scène à
l'autre, aucun compresseur, aucune musique. Le rire contient deux souffles
dans un même fichier ; le manifeste conserve les deux accents.

Le découpage des enveloppes mesurées sert au petit jeu du visage. Il ne
transforme pas les mesures en écoute : la pertinence émotionnelle, le
naturel et le confort doivent se juger en écoutant les fichiers livrés.

`mix_report.json`, `controls.json`, `cues.json` et `voice_cues.json`
documentent les niveaux, les fichiers et l'accord temporel. Les fichiers
CSV conservent les placements au sample. Les masters, les paramètres R et
les licences sont dans `assets/voix/`.

Depuis la racine du projet :

```sh
python episodes/patch_01_coffre_v6_voix/sources/son.py
```
