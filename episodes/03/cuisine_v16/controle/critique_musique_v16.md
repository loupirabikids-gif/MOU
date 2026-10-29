# Critique ciblée — musique continue et baisse au lavabo

Nouvelle consigne explicite : conserver la musique tout au long de la vidéo,
en diminuant son volume pendant le lavage pour laisser entendre l’eau. Cette
consigne remplace les anciennes coupures pendant lavage, papier, poubelle
et fin. La couleur « Jazz cartoon discret », les images, les gestes, le
sifflement et les bruitages V15 restent la référence.

## Examen avant fabrication

Lecture du code de rendu musical V15 et de la chronologie : cinq inserts de lavabo,
7,75–10,30 /16,50–18,60 /23–24,50 /29–30,35 /34–35,35 secondes. La révision
concerne la continuité et le niveau, sans changement de direction musicale.

Points transmis au compositeur et au coordinateur :

- Garder le thème et les timbres jazz. Relier les passages par une pulsation
  et des voix continues ; pas de reset du synthétiseur ou de boucle au
  changement de plan. La musique doit aussi accompagner papier, jets,
  poubelle et dernière pose, avec seulement une courte sortie à la fin.
- Le coordinateur retient une baisse de 6 dB au lavabo, avec des transitions
  douces de 120 ms à la baisse et 180 ms au retour : le fond V15 étant déjà
  discret, la musique doit rester présente sous l’eau. Ces valeurs sont un
  choix de réalisation, pas une préférence chiffrée attribuée à l’utilisatrice.
  Le contrôle
  doit porter sur l’enveloppe réellement appliquée, plutôt que sur le RMS
  de deux mesures musicales différentes.
- Préserver les 63 WAV non musicaux et le gain master V15. Avec une musique
  continue, l’ancien calcul du master à partir des régions sans musique
  n’est plus applicable. Une très petite variation du pic global ne
  justifie pas de renormaliser tous les bruitages.
- Actualiser les audits et la provenance : aucune assertion historique
  « silence musical hors cuisine » ne doit être présentée comme une
  exigence actuelle. Les licences FluidSynth/TimGM6mb restent pertinentes.

## Examen du rendu

Sources gelées examinées : `music.py` SHA-256
`2a977a953932b0df0f2aef14b12c537760973aa3d40f322cff9e1c2a8e153b5f`,
mix WAV `4dd914c20c5913af0e7bcfabb887fecc83e5651e3b0b2edadaf9ed6bb372cbd1`.
Le MP4 complet réellement exporté dure 41 secondes et comporte une piste
AAC stéréo 48 kHz ; son empreinte est
`579bc4ec2b6d60a96395fa1487527729290c360c9145307919cd4fe4b8c858f0`.
Les extraits comparatifs avant/après existent. Les fichiers et leur structure
ont été examinés, sans prétendre avoir écouté leur contenu.

### Partition et continuité

Comparaison indépendante des événements composés V15/V16 : les **119
événements V15** sont tous repris avec les mêmes instruments, hauteurs,
instants, durées et vélocités. Les quatre définitions d’instruments sont
identiques. Le total passe à 316 événements par ajout de liaisons dans les
anciens vides et de trois accords doux de raccord ; le thème n’a donc pas
été remplacé par une nouvelle direction musicale.

Le code rend chaque instrument en une seule session FluidSynth de 0 à 41 s.
L’horloge à 108 BPM et les relâchements des voix traversent les changements
de plan. Le début garde la place réservée au sifflement initial. Un accord
porte la fin de la phrase d’ouverture ; deux autres comblent l’ancien creux
du sel et celui du dernier manche avant le lavage. Ces ajouts répondent à
la nouvelle continuité demandée, plutôt qu’aux anciennes coupures comiques.

La spécification musicale active est bien `windows=[[0,41]]`, publiée dans
`audit_son.json` sous `background_music.parameters.effective_specification`.
Les fenêtres V15 conservées comme données historiques servent à reprendre
les notes initiales ; elles ne masquent plus le signal produit.

### Baisse au lavabo et place de l’eau

L’enveloppe réellement utilisée a été lue et comparée aux WAV
`musique_sans_baisse.wav` et `musique_cuisine.wav`. Son gain varie de 1 à
0,501187, soit **−6 dB**, sans jamais s’annuler. La reconstruction du WAV
baissé à partir du WAV brut et de cette enveloppe diffère d’au plus une unité
PCM16, ce qui correspond aux arrondis de quantification.

Les cinq plateaux couvrent les inserts de lavabo prévus. La descente de
120 ms précède chaque insert ; la remontée de 180 ms suit sa fin. Les
interpolations douces ne créent pas un changement instantané de niveau.
L’enveloppe n’agit ni sur l’horloge ni sur les notes, et ne remet pas une
phrase à zéro. La musique revient au niveau normal sur papier et poubelle.

Mesures ciblées indépendantes sur les périodes d’écoulement : l’eau isolée
se situe environ **21,3 à 23,3 dB au-dessus de la musique en RMS**, avant le
même gain master. Cela confirme que la baisse protège la place de l’eau
dans le signal ; la perception réelle reste à juger à l’écoute.

### Papier, fin, conservation et provenance

Le PCM musical est présent dans les essuyages et jets de papier, les
inserts de poubelle et la dernière réaction. Vérifications ciblées : RMS
musical avant master −43,79 dBFS au premier essuyage, −39,13 dBFS au premier
insert poubelle, −43,01 dBFS au dernier essuyage et −41,99 dBFS sur la réaction
finale. La seule sortie globale de musique est le fondu terminal de 150 ms.
L’audit indépendant complète ces points par 163 fenêtres glissantes de
0,5 seconde sans réapparition des anciennes plages muettes.

Les 63 WAV non musicaux et le gain master V15 sont conservés. Le pic du mix
atteint environ −3,735 dBFS sans saturation ; il n’a pas été forcé à
−4 dBFS au prix d’un changement global des bruitages. La provenance décrit
la musique continue et la baisse actuelle, avec les mêmes crédits et
licences FluidSynth/TimGM6mb. Les anciennes déclarations de silence pendant
papier, poubelle et fin ne décrivent plus le mix produit.

## Avis

Révision cohérente avec la nouvelle consigne : même jazz, continuité du fond,
baisse douce au lavabo et eau dominante dans les mesures. Aucun défaut
matériel bloquant retenu dans la partition, les enveloppes et les fichiers
examinés ; aucune correction supplémentaire proposée sans défaut démontré.

Limites : examen de code, de partition, d’enveloppes, de PCM et de métadonnées
des exports. Aucun visionnage sonore continu, écoute perceptive, test sur
téléphone ou validation auprès d’un public n’est revendiqué.
