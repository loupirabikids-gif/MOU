# Jazz cartoon discret — musique V15

Choix explicite de l’utilisatrice : « Jazz cartoon discret ». Le prototype
de groove funk suggéré par défaut a été écarté avant livraison ; aucun stem
de guitare de ce prototype ne fait partie de la version retenue.

## Intention et partition

Petit ensemble original en la majeur, à 108 BPM : contrebasse acoustique,
accords de piano électrique doux, petites réponses de piano acoustique et
batterie aux balais. Un léger swing des contretemps (58,5/41,5) donne du
rebond, sans déplacer les gestes de MOU ni les bruitages.

Les trois notes sifflées A5–C#6–B5 gardent la mélodie de départ. Le piano ne
leur répond qu’après 1,75 s ; les voicings A6/9 et D6 restent compatibles.
Les retours de cuisine ont leurs propres petites réponses, raccourcies selon
la fenêtre, au lieu de relancer chaque fois la même boucle de sept notes.

Les coups de batterie évitent les impacts du couteau et de la tomate. Pendant
la pincée et les grains de sel, aucune nouvelle attaque de piano ou percussion
entre 27,65 et 28,55 s ; un creux doux protège ces petits bruitages. Les cinq
fenêtres restent exactement 0–7,75 /13,5–16,5 /21,5–23 /27–29 /33–34 s.
Attaques/sorties de 12 ms à l’intérieur des fenêtres ; aucune queue de
réverbération ou note pendant les lavages, essuyages, jets et la fin.

## Réalisation et provenance

Partition écrite dans `sources/music.py`, rendue hors ligne par FluidSynth
2.4.4 via Python/ctypes. Banque d’instruments tierce TimGM6mb fournie dans
`assets/`, avec sa licence GPL-2 et les crédits ; FluidSynth est un outil
libre. Il ne s’agit pas d’une musique ou boucle préexistante téléchargée.
Les timbres instrumentaux sont échantillonnés : la déclaration d’anciens
rapports « aucun échantillon externe » ne s’applique pas à cette musique.
Les 63 bruitages et notes sifflées restent les originaux de V14.

Quatre stems modifiables de 41 s : `musique_basse.wav`,
`musique_accords.wav`, `musique_ponctuations.wav`, `musique_percussions.wav`.
Ils partagent le même gain avant master et reconstruisent le stem musique
à deux unités PCM16 près, dues à l’arrondi de quantification des fichiers.
La partition inclut les notes, durées, instruments, vélocités et fenêtres.

## Mix et contrôles

Le pic global V14 se situe dans le premier lavage, à 9,171208 s, donc hors
musique. Le gain master est fixé sur ce même pic inchangé, avec sa valeur
précise 2,124210976406158 (environ +6,544 dB). Les 63 WAV non musicaux et
les échantillons du mix final hors fenêtres de musique sont identiques à
V14, pas seulement similaires. Pic du mix : −4 dBFS, aucune saturation.

Le stem musique est réglé à un pic avant master de −23,5 dBFS. Son RMS après
master varie selon la fenêtre entre environ −34,15 et −36,69 dBFS. Ce choix
conserve un fond discret ; les attaques et les creux sont aussi adaptés
aux petits sons de cuisine. Les valeurs exactes sont dans
`controle/audit_musique_v15.json` et le contrôle indépendant.

Ces mesures et l’examen de la partition ne sont pas une écoute perceptive,
un test de haut-parleur de téléphone ou une validation artistique auprès du
public. L’extrait comparatif et le film permettent à l’utilisatrice de juger
la couleur musicale et l’équilibre réellement perçus.
