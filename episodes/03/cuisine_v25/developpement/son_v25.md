# Son V25 — fond doux, matières papier et mix complet

La demande concerne une musique plus douce et une amélioration générale du
jeu et des mouvements. Le son est intégré au film de 43 s, avec les mêmes
contacts et gestes de cuisine. La palette papier reste une proposition :
l'essai court précédent n'est pas présenté comme accepté par l'utilisatrice.

## Un accompagnement plus discret

La nouvelle partition conserve la grille à **108 BPM** et les couleurs en
la majeur compatibles avec les trois notes sifflées initiales. Elle comporte
uniquement un **piano dans le registre médium et une contrebasse**. Un accord
de trois notes est tenu par mesure ; la basse joue en deux temps. La ligne
mélodique aiguë, la basse marchante, le kit et les balais sont retirés.

Les notes utilisent des vélocités de 28 à 36. Après rendu des échantillons
FluidR3, chaque attaque est enveloppée sur **45 ms au piano et 35 ms à la
contrebasse**. Les notes d'introduction et de conclusion sont tenues plus
longtemps pour éviter une interruption avant le prochain accord ou la sortie.
Aucune couche de bruit continu ne remplit les espaces de la partition.

Le seul fond musical reçoit une calibration constante à **−41,5 dBFS RMS**,
mesurée avant atténuation sur 2–42,3 s. La basse est équilibrée à −8 dB RMS
du piano. Le fond baisse au maximum de 1 dB aux lavages, avec transitions de
600/800 ms. La dernière tenue se fond de 42,4 à 43 s. Les coupes de caméra
ne redémarrent ni ne découpent la partition. Aucun compresseur de bus musical
ou gain automatique par scène n'est ajouté.

Sur les PCM réellement écrits, le niveau musical moyen de 2–42,3 s est de
**−41,779 dBFS RMS**, soit **−5,795 dB par rapport à V24** et **−9,795 dB
par rapport à V23**. L'orchestration est différente : ces écarts mesurent les
signaux et ne certifient pas leur douceur perçue. Le contrôle du PCM ne
trouve aucune plage de silence numérique musical supérieure à 100 ms.

## Trente et un événements papier adaptés

Les tirages, déchirures, frottements, froissages et contacts avec la poubelle
et le sol utilisent des extraits de matières existantes. Les coupes changent
selon les cycles. Aucune nouvelle synthèse de bruit ou boucle granulaire ne
remplace les textures. Les petits bouts gardent des niveaux adaptés à leur
taille ; chaque impact reste sur le contact visible.

Les dix frottements durent 240 ou 260 ms. Leurs centres suivent les maxima
de vitesse relative des moufles. Les positions monde des mains pendant les
essuyages sont conservées par l'animateur V25. Au dernier essuyage, les centres
37,377 et 37,820 s utilisent deux pics principaux plus tôt pour exposer les
extraits de 260 ms avant le froissage de 38,1 s.

Les sources ont des statuts distincts, consignés dans
`assets/paper_recordings/provenance.json` :

- **AtomSFX / MXAntian, MIT** : prises de paume lissant ou tapotant du papier,
  et déchirure de carton épais. Le procédé d'enregistrement et les techniques
  sont documentés au commit `b3e55737e0019905b8d85ef0d06def1bca6ab025`.
  Ces prises sont adaptées aux gestes de MOU ; elles ne sont pas décrites
  comme des captures d'essuie-tout ou de chutes dans une poubelle.
- **Ben Burnes / Abstraction, CC0** : extrait de la texture de bibliothèque
  « Paper Scraps », adapté aux cinq froissages. La méthode d'enregistrement
  et le geste exact ne sont pas établis par la notice consultée.

Les WAV originaux, notices et preuves sont inclus. Le traitement conserve
leur spectre : conversion en 48 kHz stéréo, retrait de composante continue,
fondus courts, compression 2:1 seulement au-dessus de quatre fois le RMS de
l'extrait, puis appariement RMS plafonné à +3 dB de l'ancienne crête du cue.
Il n'y a ni filtrage passe-bas à 2 kHz, ni transposition, ni étirement temporel.
Chaque coupe, source, adaptation et gain est consigné dans les événements.

## Éléments conservés et limites

Les **26 événements non papier** conservent exactement leurs PCM traités,
leurs instants et leur gain de livraison V24 : eau, commandes du robinet,
couteau, contacts d'ustensiles, cuisson, tomate, sel et sifflement. Leurs
sources synthétiques restent identifiées comme telles. Aucun remplacement
enregistré de l'eau ou du couteau n'a été ajouté. Il n'y a pas de ponctuation
sonore sur les sourcils, les regards ou la réaction finale.

Le modèle ne peut pas écouter l'audio dans cette session. Les niveaux,
attaques définies dans les sources et preuves de matière sont des contrôles
techniques. Le confort, le naturel, l'identité des gestes à l'écoute et la
réussite comique restent des appréciations distinctes.

## Recette et exports

Les **58 événements** de `audio/provenance.json` sont additionnés en PCM
entier à `start_sample`. L'enveloppe globale de bord de 8/35 ms est appliquée
puis arrondie ; le gain fixe de **+3,50 dB** est appliqué puis arrondi en
PCM 16 bits. Aucune normalisation du film vers une cible LUFS ne remonte
le fond musical après sa baisse.

Le mix complet mesure **−30,57 LUFS**, **−14,15 dBTP**, sans écrêtage. Il dure
43 s en stéréo, 48 kHz. Les 26 fichiers de référence conservés sont vérifiés
par SHA. La musique utilise la banque FluidR3 MIT réduite incluse, avec la
partition originale, les paramètres et les pistes séparées disponibles.

- `audio/mix.wav` : bande-son complète.
- `audio/test_fin_v25.wav` : échantillons exacts de **35 à 43 s**, huit secondes.
- `audio/extrait_mix_v25.mp3` et `.wav` : passage 10,25–17,25 s au gain du film.
- `audio/jazz_seul_15s.mp3` et `.wav`, `jazz_seul_complet.wav` : fond seul.
- `audio/partition_v25.mid` et `.json` : deux pistes, notes, vélocités, attaques.
- `audio/jazz_accords_v25.wav`, `jazz_basse_v25.wav` : pistes avant le gain
  final du film ; `jazz_sans_baisse_v25.wav` : référence avant atténuation.
- `audio/foley_v25/` : les 31 événements papier séparés.

Reproduction autonome depuis les sources et les ressources incluses :

```sh
.venv/bin/python -B episodes/03/cuisine_v25/sources/son.py
```

FluidSynth système est nécessaire au rendu de la partition. Le script n'a
besoin ni du dossier V24 extérieur, ni de réseau. Les niveaux historiques sont
conservés en métadonnées dans `audio/reference_levels_v23_v24.json` ; les
fichiers copiés devenus inutiles ont été retirés du seul dossier V25.
Empreintes et contrôles : `controle/audit_son.json`, `audit_audio_v25.json`.
