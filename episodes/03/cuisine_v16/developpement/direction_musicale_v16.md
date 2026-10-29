# Jazz continu et baisse au lavabo — V16

Nouvelle consigne : conserver la musique tout au long de l’épisode et baisser
seulement son volume pendant les lavages pour entendre l’eau. Elle remplace
les coupures et les anciens silences pendant papier, poubelle et fin.

Le même jazz cartoon discret est conservé : contrebasse, accords doux de
piano électrique, petites réponses de piano acoustique, batterie aux balais.
Les **119 notes/événements écrits V15 sont repris aux mêmes instants**, avec
les mêmes hauteurs, durées, instruments et vélocités. Les anciennes zones
vides reçoivent des liaisons sur le même tempo de 108 BPM. Trois petits
accords tenus assurent les raccords de phrase de l’ouverture, du sel et du
dernier manche propre ; aucun redémarrage de musique à l’entrée d’un plan.

## Continuité réelle

FluidSynth rend chaque instrument **une seule fois de 0 à 41 s**. Les voix,
leurs relâchements et l’horloge musicale continuent à travers les raccords
du film. Les notes sont exprimées en temps absolu ; le paramètre historique
`original_cooking_windows` sert seulement à conserver la partition V15,
pas à couper le signal. La spécification active est fournie par `son.py` :
`windows=[[0,41]]`, avec les cinq intervalles lavabo comme baisses de volume.
La chronologie visuelle est conservée à l’octet près.

L’enveloppe `music.gain_envelope(length, specification)` réduit le signal
de **6 dB**, soit un facteur 0,501187, pendant chaque insert lavabo :
7,75–10,30 /16,50–18,60 /23–24,50 /29–30,35 /34–35,35 s.
Descente douce sur 120 ms avant l’insert ; retour sur 180 ms après sa fin.
Le gain ne tombe jamais à zéro. Le niveau normal revient pour essuyage,
papier et poubelle ; la musique continue aussi sur la réaction finale.
Seule sa sortie terminale possède un fondu de 150 ms.

## Conservation et vérification

Gain commun de musique V15 conservé : 1,0202131333074838. Gain master exact
conservé : 2,124210976406158. Les 63 WAV de bruitages et sifflements gardent
leurs octets, leurs horaires et leurs niveaux ; aucune nouvelle normalisation
globale ne sert à forcer le pic à −4 dBFS. L’ajout d’une musique atténuée au
premier lavage peut donc changer légèrement le pic total, sans saturation.

Les quatre stems modifiables sont baissés comme le stem `musique_cuisine.wav`.
`musique_sans_baisse.wav` contient la même musique au même gain commun avant
l’enveloppe de lavabo : on peut mesurer directement la réduction de 6 dB
sans la confondre avec une variation du phrasé. La spécification exacte est
dans `audit_son.json` → `background_music.parameters.effective_specification`.

L’audit de production vérifie les 119 événements conservés, 63 WAV identiques,
le gain master, la baisse mesurée et la présence musicale sur chaque fenêtre
glissante de 0,5 s. Un ancien blanc au sel et une quasi-extinction après la
reprise du manche ont été comblés par les accords liés décrits ci-dessus.
Ces mesures et la partition ne sont pas une écoute perceptive du mix.

Partition originale ; rendu libre FluidSynth 2.4.4 et banque tierce TimGM6mb
GPL-2 déjà fournie et créditée dans `assets/`. Aucun morceau ou boucle importé.
