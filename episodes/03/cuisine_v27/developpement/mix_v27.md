# Intégration sonore V27

Le mix de 38 secondes conserve les images et gestes V26. Les 46 bruitages
existants d'eau, de papier, d'ustensiles et de sifflement sont reconstruits
avec des PCM et instants strictement identiques, contrôlés par leurs SHA.
La cuisson et la musique sont remplacées ; aucun dossier V26 externe n'est
nécessaire à la génération.

## Direction et composants

La bossa originale associe guitare nylon et basse, avec une dérive composée
avant la coupure à 32 s. Onze compléments apportent une ambiance de pièce
très basse, une matière de papier qui se densifie aux contacts réels du tas,
une cuisson progressivement plus sèche et un dernier tsss à 32,60–32,95 s.
Ils n'ajoutent pas d'alarme ou d'appareil absent du décor.

Cinq accents vocaux brefs accompagnent hésitation, fumée, choc, déception et
fierté déplacée : 21,98 / 25,68 / 31,76 / 32,78 / 35,15 s. Le total vocal est
de 0,98 s. Les extraits CC0 adaptés viennent d'une bibliothèque de souffles et
de sons de créature ; auteur original et méthode d'enregistrement restent
non vérifiés. Ils ne sont présentés ni comme des captations humaines certifiées
ni comme une imitation de Lamput. Leur compréhension sans mots et leur naturel
ne sont pas validés par écoute dans cet environnement.

## Ponctuation et hiérarchie

Un même masque temporel s'applique à chaque cue avant quantification : fondu
de 6 ms immédiatement avant 32 s, puis zéro intégral de 32 à 32,5 s. Les sons
reprennent doucement après la pause. Un fondu terminal de 32 ms, de 37,218 à
37,25 s, termine l'ambiance ; les 0,75 dernières secondes restent silencieuses.
La note musicale finale est isolée entre 36,25 et 36,75 s et ne relance pas
l'accompagnement. Ces silences sont contrôlés sur chaque couche et sur le mix.

Le gain de livraison demeure fixe à +3,5 dB. Aucune normalisation LUFS, aucun
réglage de gain par scène ou détecteur de mix n'est ajouté. Les niveaux des
bruitages conservés ne changent pas. Le dosage reste une proposition : les
mesures ne prouvent pas le confort ou la personnalité à l'écoute.

## Résultats et fichiers

63 événements : 46 conservés, 11 compléments, cinq accents vocaux et une piste
musicale. WAV stéréo 48 kHz / 16 bits, 1 824 000 échantillons par canal, zéro
échantillon écrêté. Mesures : −31,64 LUFS intégrés, −19,00 dBTP. Le silence
32–32,5 s contient exactement 24 000 échantillons nuls par canal ; la fin
37,25–38 s contient 36 000 échantillons nuls par canal.

- audio/mix.wav : bande-son complète.
- audio/test_fin_v27.wav : extrait exact de 30 à 38 s.
- audio/musique_v27.wav : partition seule.
- audio/stems_v27/ : guitare, basse, effets, voix et ambiance avant gain final.
- audio/audition_voix_v27.wav : les cinq propositions dans des créneaux courts,
  5,5 s au total, au gain de livraison du film. Les repères sont dans le JSON.
- audio/provenance.json : sources, transformations, gains et positions.

54 anciennes copies devenues inutiles ont été retirées du seul dossier audio
V27, soit 32 156 822 octets. Les 22 PCM bruts, leurs références et les sources
nécessaires restent présents. V26 n'a pas été modifiée.

Une régénération complète après nettoyage a produit des WAV strictement
identiques : mix, musique, extrait final et audition vocale. Résultat détaillé
dans controle/audit_son_reproduction_v27.json. Les audits numériques sont
controle/audit_son.json et controle/audit_audio_v27.json.

```sh
.venv/bin/python -B episodes/03/cuisine_v27/sources/son.py
```

Aucune écoute, lecture continue, reconnaissance publique des émotions ou
approbation artistique n'est revendiquée par ce contrôle.
