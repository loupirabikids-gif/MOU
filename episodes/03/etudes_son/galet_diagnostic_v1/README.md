# Comparaison de la bande-son

Trois versions du début du film Galet : environ neuf secondes, depuis la
cuisine jusqu'au premier jet de papier. Ce sont les mêmes images avec des
couches sonores isolées. Aucun nouveau mix complet n'est livré ici.

- **[A — Mix actuel](A_mix_actuel.mp4?raw=true)** : musique, bruitages et ambiance.
- **[B — Jazz seul](B_jazz_seul.mp4?raw=true)** : même niveau que dans A.
- **[C — Bruitages seuls](C_bruitages_seuls.mp4?raw=true)** : effets et ambiance,
  aux mêmes niveaux que dans A. Le sifflement du personnage appartient à cette piste.

Comparer à volume d'appareil constant : sifflement vers 0,3–1,7 s, eau vers
3,9–5,35 s, puis papier à partir de 5,93 s. Le but est de repérer une matière
ou une combinaison gênante avant de remplacer des sons. Le retrait du jazz
dans C est une comparaison, pas une décision de supprimer la musique.

L'eau, la cuisson et le sifflement sont des synthèses réutilisées ; certains
sons de papier viennent de captations documentées. L'origine d'un son ne
prouve ni son naturel ni sa pertinence pour le geste. Voir l'[analyse de
provenance et de niveaux](analyse.md), qui distingue constats et hypothèses.

Le modèle ne peut pas écouter dans cet environnement. Ces fichiers permettent
une écoute humaine ; les mesures ne valident pas les timbres ou le confort.

## Sources et contrôles

Le [script Python](comparer.py) lit les WAV et la version muette de
`episodes/03/galet_cuisine_v1/`. Reproduction depuis la racine du dépôt,
avec NumPy et FFmpeg installés :

```bash
.venv/bin/python episodes/03/etudes_son/galet_diagnostic_v1/comparer.py
```

A utilise le PCM du mix livré ; B la musique ; C les bruitages et l'air.
Aucun gain, filtre ni normalisation n'est ajouté. Chaque extrait est encodé
en AAC 160 kbit/s. La vidéo H.264 est copiée sans réencodage : les trois flux
sont identiques et les 210 premières images décodées correspondent au film
livré. La fenêtre audio dure 8,75 s ; la copie vidéo donne un conteneur de
8,833 s. Les empreintes du film complet et des pistes d'origine restent
identiques après génération.

[Rapport des contrôles et empreintes](CONTROLE.json).
