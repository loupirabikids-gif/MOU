# Son V23 — partition originale et recette reproductible

La V23 remplace la musique précédente par une partition continue de trio : piano acoustique, contrebasse et balais. Le rendu utilise FluidSynth 2.4.4 et un sous-ensemble de la banque FluidR3 sous licence MIT. Les 40 événements non musicaux de la V22 conservent leurs fichiers PCM traités, leurs instants et leurs longueurs. Aucun nouveau bruitage de regard ou d'émotion n'a été ajouté.

## Composition

- La majeur, 108 BPM, mesure à quatre temps ; grille à 0,30 s pour correspondre au balancement culinaire existant. Ce tempo remplace la première proposition à 80 BPM, abandonnée avant livraison après vérification du mouvement réel.
- Introduction A6/9 tenue sous les trois notes sifflées d'origine A5, C#6 et B5. Leurs instants restent 0,30 s, 0,855556 s et 1,411111 s. Le motif régulier de balais commence vers 2,522 s.
- Vingt et une mesures complètes, puis une courte coda à 46,966667 s ; durée totale inchangée de 48,25 s.
- Contrebasse principalement en deux temps, avec six mesures de transition marchées ; accompagnement de piano espacé et quelques courtes phrases séparées. Les accords ne redémarrent pas aux changements de plan.
- Variations déterministes de vélocité, accords légèrement déroulés, décalages d'attaque de ±8 ms et swing à 0,58. Graines aléatoires conservées dans le code et la partition JSON.
- Les balais incluent une texture continue fabriquée à partir de l'échantillon FluidR3 brush38, avec grains fenêtrés recouvrants. Ce traitement prolonge un geste de balai à partir d'un échantillon naturellement bref ; ce n'est pas une nouvelle couche de bruit d'eau.

## Banque et outils libres

`assets/FluidR3_MOU_trio.sf2` pèse 4 048 186 octets. Il contient uniquement les programmes Yamaha Grand Piano, Acoustic Bass et Brush et leurs échantillons nécessaires. SHA-256 : `c8c326b595c4cf49a5aa58c920ecb27b645deb025652938e7db8b6795eca5fe2`.

La source est le paquet Debian officiel `fluid-soundfont-gm` 3.1-5.3. Les signatures Debian et les empreintes des index et du paquet ont été contrôlées. La licence MIT des sons est distincte des mentions GPL propres à l'empaquetage Debian. Provenance, commande d'extraction et notice : `assets/FluidR3_README.md`, `assets/FluidR3_MOU_trio.json`, `assets/NOTICE_FluidR3_COPYRIGHT.txt` et `sources/subset_soundfont.py`. Les 59 notes sélectionnées, puis 18 essais prolongés, donnent les mêmes échantillons avec le sous-ensemble et la banque source. Le gros fichier d'origine n'est pas nécessaire au rendu et n'est pas embarqué.

Production : Python, NumPy, wave, FluidSynth et FFmpeg ; aucun service de synthèse payant ni enregistrement musical tiers. Le MIDI et la partition JSON sont fournis. L'ancienne banque TimGM et les anciens WAV musicaux copiés ont été retirés uniquement du dossier V23 ; l'historique V22 est conservé dans son propre dossier.

## Mixage

La musique possède une calibration globale à −31,5 dBFS RMS sur son corps non atténué. Un compresseur fixe sur son seul bus utilise un ratio 2:1, seuil −36 dBFS, genou 6 dB, détection RMS 25 ms, attaque 15 ms et relâchement 240 ms. La réduction maximale mesurée est de 5,667 dB. Le gain compensateur constant est 1,4924274723. Ces paramètres ne dépendent pas des plans.

La partition continue pendant les lavages. Son atténuation maximale y est de 1,5 dB, avec une entrée de 600 ms et une sortie de 800 ms. Les bruitages d'eau et de papier restent les fichiers traités V22. Les couches répétitives déjà retirées en V22 restent absentes.

Recette exacte du film : addition entière de chaque fichier `provenance.events[].file` à `start_sample` ; enveloppe de bord globale de 8 ms / 35 ms ; premier arrondi PCM ; gain fixe de livraison de **+3,50 dB** sur le film entier ; second arrondi PCM 16 bits. Aucun ancien gain maître n'est réappliqué. Le gain V22 était +5,13 dB : le gain final des mêmes bruitages est donc uniformément inférieur de 1,63 dB, sans réglage indépendant par scène.

## Contrôles factuels

| Mesure | V23 |
| --- | ---: |
| Durée / fréquence / canaux | 48,25 s / 48 kHz / stéréo |
| Événements actifs | 41, dont une musique |
| Événements non musicaux identiques à V22 avant gain final | 40 |
| Sonie intégrée FFmpeg | −25,00 LUFS |
| Crête vraie mesurée | −9,94 dBTP |
| Échantillons écrêtés | 0 |
| Écart P95–P05 des fenêtres RMS de 250 ms | 8,50 dB |
| Écart P95–P05 des fenêtres RMS de 2 s | 1,94 dB |
| Écart P95–P05 des fenêtres RMS de 3 s | 1,44 dB |

Le comparatif `controle/comparaison_audio_v22_v23.json` conserve aussi les mesures V22 : respectivement 4,28 dB, 1,37 dB et 1,13 dB. La V23 a donc davantage de variation sur les petites fenêtres, liée notamment aux attaques acoustiques. On ne peut pas présenter ces résultats comme une preuve de meilleure stabilité perceptive. Le minimum RMS de musique sur 100 ms dans le corps est −43,51 dBFS avant gain final ; aucun trou comparable aux versions de travail initiales proches de −90 dBFS ne subsiste dans ce contrôle.

**Limite : aucun jugement d'écoute n'a pu être effectué dans cette session.** Le retour d'outil audio était « audio content omitted because you do not support audio input ». Ces vérifications établissent une recette, une continuité de partition, des niveaux et une reproductibilité ; elles ne certifient ni agrément musical, ni équilibre ressenti, ni confort à l'écoute.

## Fichiers à écouter ou modifier

- `audio/jazz_seul_15s.mp3` et `.wav` : extrait initial de 15 s au même gain que la musique du film, sans normalisation supplémentaire.
- `audio/jazz_seul_complet.wav` : musique seule complète au gain de livraison.
- `audio/test_fin_8s.wav` : extrait exact 40,25–48,25 s du mix final.
- `audio/mix.wav` : mix stéréo complet destiné à l'export vidéo.
- `audio/partition_v23.mid` et `.json` : notes, instruments, horloge, vélocités et paramètres de rendu.
- `audio/jazz_basse_v23.wav`, `jazz_accords_v23.wav`, `jazz_melodie_v23.wav`, `jazz_balais_v23.wav` : pistes séparées avant l'unique gain de livraison du film, avec les traitements communs de musique déjà inscrits.
- `audio/musique_v23.wav` et `jazz_sans_baisse_v23.wav` : événement musical final et référence sans atténuation de lavage.

Reproduction depuis la racine du dépôt :

```sh
XDG_CACHE_HOME=/workspace/MOU/work/font-cache .venv/bin/python -B episodes/03/cuisine_v23/sources/son.py
```

Le contrôle indépendant doit reconstruire le mix depuis les fichiers d'événements, sans sommer les pistes séparées ni ajouter le gain historique. Empreintes du rendu gelé : `controle/audit_son.json` et `audio/provenance.json`.
