# Son du galet en cuisine

Production locale uniquement : Python/NumPy pour le mix, FFmpeg pour la mesure
et l'encodage. Aucun service payant, aucune nouvelle voix ou imitation vocale.
Le modèle ne peut pas écouter ici ; aucune naturalité, émotion entendue ou
qualité d'écoute n'est donc déclarée validée.

## Palette conservée

Le mix reprend 58 cues du travail sonore V27 conservé en V28 : guitare nylon et
contrebasse originales, eau et robinets, ustensiles, papier, cuisson et présence
de pièce très basse. Les cinq accents vocaux précédents sont exclus. Les douze
propositions de la bibliothèque ne sont pas injectées dans ce film.

Les trois petits sifflements restent au tout début, avant tout lavage.
La bossa garde son score continu, sa dérive modérée de 108 à 112 BPM et la note
finale écrite. Aucun nouveau bruit filtré n'est fabriqué pour remplacer une
matière de papier. La méthode de création de chaque ancien cue reste documentée :
eau/ustensiles/cuisson et ambiance sont des synthèses antérieures du projet,
pas des captations naturelles nouvellement réalisées.

Le papier est adapté de sources libres déjà créditées : certains gestes AtomSFX
sont décrits comme enregistrés ; la déchirure emploie du carton adapté ; la texture
Ben Burnes est CC0 mais sa méthode d'enregistrement n'est pas vérifiée. Les droits,
notices et métadonnées de ces sources sont conservés dans assets/paper_recordings.

## Dosage

Le jazz reçoit **−1,5 dB fixes** par rapport au cue source V27. Tous les autres
cues gardent leur niveau relatif. Le gain de livraison de **+3,5 dB** est celui
de la version de référence, identique partout ; ce n'est pas une hausse nouvelle
pour compenser la baisse musicale. Aucun détecteur, AGC, sidechain ou
normalisation par scène dans ce nouveau mix ; le traitement antérieur des cues
source reste documenté dans leur provenance. La modulation douce de 0,6 dB écrite dans l'ancien
score sous les lavages reste celle du fichier musical source.

La coupure 32–32,5 s et la tenue 37,25–38 s sont exactement muettes, pour tous
les cues et toutes les pistes. La note finale reste entre 36,25 et 36,75 s.
Un très court contour de gain aux bords évite les clics numériques.

## Synchronisation

Les transitoires de contact — couteau, tomate, robinets, déchirure et impacts —
sont placés pour que leur pic RMS de 8 ms coïncide avec l'événement de la
chronologie. Il s'agit d'un repère énergétique mesurable, pas d'un seuil d'audibilité.
Les durées de l'eau et les phases de froissage restent liées aux gestes entiers.

Pour les huit accents d'essuyage, sources/son.py --sync-motion échantillonne
240 états frais de la nouvelle animation par lavage et mesure deux maxima de
vitesse relative entre les vrais bouts des moufles. Les cues sont alors placés sur
ces repères. Avant cette mesure finale, events.json indique explicitement
pending_new_character_motion : les anciens repères ne sont pas présentés comme
mesurés sur le nouveau galet.

## Reproduction et fichiers

Depuis le dépôt :

```sh
.venv/bin/python -B episodes/03/galet_cuisine_v1/sources/son.py
```

Après gel de l'animation, ajouter --sync-motion une fois pour mesurer puis
reconstruire. Les reconstructions suivantes reprennent audio/motion_sync.json
et n'importent plus l'animation. Tous les WAV de la banque d'entrée sont locaux
et vérifiés par SHA256 ; aucune ancienne version du film n'est requise.

audio/input_bank.json est la liste exhaustive des entrées actives. Le fichier
source_provenance_v27.json est une preuve historique : ses anciens chemins et
cinq voix ne sont pas des dépendances de cette production. La partition MIDI,
les paramètres et le module music_reference.py conservent le score original ;
la petite banque FluidR3 et ses notices sont jointes. Le mix courant utilise le
cue musical inclus, sans imposer FluidSynth pour une reconstruction identique.

Sorties : mix.wav (38 s, 48 kHz stéréo PCM16), test_fin.wav (30–38 s), trois
stems music/foley/ambience, tous les cues de sortie, events.json et provenance.
La somme des stems reproduit le PCM du mix exactement. Le bilan technique est
dans controle/audit_son.json ; il ne remplace pas une écoute sur téléphone.

## Recalage effectué sur le nouveau personnage

La première mesure du nouveau rig est terminée : les pics retenus sont
6,725 / 6,86854 s ; 13,380 / 13,49042 s ; 18,275 / 18,36113 s ;
26,875 / 27,08479 s, respectivement pour les quatre essuyages. Les WAV ont été
reconstruits sur ces repères ; events.json porte measured_new_character.
Les trois dernières décimales de certains temps viennent de l'échantillonnage
continu à 240 états par intervalle, pas d'une précision visuelle du film 24 fps.
La QA du MP4 doit encore confronter ces repères aux images encodées.

La critique peut conduire à corriger un geste ; dans ce cas, remesurer sur les
sources finales avant le gel de livraison. La première banque est entièrement
locale, sans resynthèse nouvelle de bruit et sans déplacement de toute la piste.

## Gel final

Après la seconde revue visuelle, les quatre essuyages ont été remesurés sur
l'animation finale SHA `7de33162f08a2e26f18a7ddf01a4fd675b61a12894b1ca080f43995ee666d3e7`.
La correction de la main gauche au dernier essuyage ne modifie pas les deux
pics retenus après l'approche ; les huit repères ci-dessus restent identiques.

Mix gelé : `06946073fb2c39f49d79acf8d1d5a073b1ac07aeb6dd49e127b0b8158abcb18b`.
La reconstruction isolée, sans ancien épisode ni import de l'animation, a
reproduit bit pour bit les 58 cues, les trois stems, le mix, l'extrait final et
events.json. Rapports : audio/gel_son.json et controle/audit_son_portable.json.
Le son est prêt au mux ; les vérifications d'écoute restent hors de cet audit.
