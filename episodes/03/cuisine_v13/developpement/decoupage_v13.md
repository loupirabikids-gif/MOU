# Cuisine, bout des moufles et sel — V13

29 octobre 2026. Référence conservée : V12, commit
`bad439dafb1d2bd7fccb2683efc4d7c2258be8c7`, dans `../cuisine_v6/`.

L’utilisatrice approuve les trois retouches de jeu proposées et demande un
lavabo plus lisible, un rinçage limité au bout des mains et une nouvelle
pincée de sel suivie d’un lavage. Le montage passe de 35 à 41 secondes pour
ajouter une action complète, sans comprimer l’ouverture qu’elle a demandé
de laisser respirer. Aucun dialogue, nouveau doigt ou nouveau personnage.

## Découpage commun

| Temps | Intention et action visibles |
| --- | --- |
| 0–6,6 s | MOU cuisine avec plaisir, quatre tours de cuillère ; trois notes sifflées seulement au départ. |
| 6,6–7,75 s | Poser la cuillère, lever la moufle. Le sourire disparaît, les sourcils montent et le regard se fixe sur la main avant le lavabo. |
| 7,75–13,5 s | Premier rinçage, grande bande de papier, essuyage, jet et zoom sur la première boulette. |
| 13,5–16,5 s | Deux coupes de carotte à 14,55/15,25 s, couteau posé à 15,95 s ; inspection de la main. |
| 16,5–21,5 s | Deuxième rinçage, essuyage et deuxième jet ; le rouleau diminue. |
| 21,5–23 s | Prendre la tomate et la jeter dans la poêle à 22,3 s. Les rondelles de carotte et le couteau posé restent présents. |
| 23–27 s | Troisième rinçage et troisième gaspillage. |
| 27–29 s | Écarter la main de soutien pour montrer le bol, prendre une pincée à 27,35–27,65 s, transporter et saupoudrer à 28,05–28,55 s, puis inspecter le bout de la moufle. |
| 29–33 s | Quatrième rinçage, quatrième grande bande et quatrième grosse boulette. |
| 33–34 s | Reprendre le manche propre de la cuillère ; le réflexe de nettoyage repart malgré l’absence de nourriture sur la main. |
| 34–36,05 s | Cinquième rinçage, puis tirer le dernier morceau. |
| 36,05–36,8 s | Dans la pause existante, regarder le papier, le tube vide, puis le papier avec une détermination exagérée. |
| 36,8–39,5 s | Essuyer avec application, froisser, jeter la cinquième petite boulette sur la pile. |
| 39,5–41 s | Admirer la main propre avec un sourire plus fier, un minuscule hochement à 40–40,35 s, puis la tenue déjà prévue à 40,4–41 s. Le tube vide et le gaspillage restent visibles. |

La musique originale garde 108 BPM et joue uniquement pendant la cuisine :
0–7,75 /13,5–16,5 /21,5–23 /27–29 /33–34 s. Les cinq rituels et la fin
restent sans musique ; les sons d’eau et de papier conservent leur fonction.

## Référence géométrique commune

Les deux bras restent les deux `_arm` du modèle original. Les huit fonctions
natives de géométrie, résolution et raccord gardent exactement leur AST.
Le sel est pris avec le bout arrondi de la moufle existante ; aucun doigt ou
paume séparée n’est ajouté. Un bref décalage du corps, déjà utilisé pour la
carotte, permet d’atteindre le bol sans étirer le bras.

Bol de sel permanent : centre `(590,1284)`. La main droite se pose sur la
zone de soutien de carotte `(775,1342)` dès le début du geste ; elle dégage
le bol avant l’arrivée de la main gauche. La première étude cachait le bol
sous les mains. Le dégagement en 0,12 s, suivi de l’arrivée de la main gauche,
rend le tas de sel visible avant la pincée, sans déplacer le bol ou les sons.

La source des grains est le cap arrondi natif, calculé par `world_grip` avec
la profondeur 19. Huit origines historiques à leur vrai instant d’émission
sont fournies à l’artiste ; les grains tombent de ces points vers la poêle.
Les données `production_time`, `production_cycle` et `native_cycle` séparent
le montage réel des gestes natifs réutilisés et de leurs cadrages.

Le stock suit `[1,.82,.58,.32,.006,0]`. Les cinq rayons de boulette sont
`47,53,59,61,22` ; leurs identités graphiques sont `1,2,3,3,4`, ce qui garde
le petit papier et la dernière boulette de la V11. La cinquième boulette
atterrit à `(201,1400)`, effectivement appuyée sur la quatrième après examen
du rendu ; les deux positions initialement testées la laissaient flotter.

## Études et limites

`controle/etude_animation_v13/planche.png` réunit 21 poses. Les vues natives
de la pincée, du saupoudrage et les huit poses de
`bol_et_grains_visibles.png` ont été réellement examinées. Le tas de sel
devient visible avant la prise, la chute des grains part du cap de la moufle,
et les trois retouches de visage se lisent sans changer les mains.

Préparation sur 984 états : stock décroissant, poubelle croissante de zéro à
cinq, et erreur de prise native maximale inférieure à `0,000001` unité.
Le rapport `preparation.json` conserve les empreintes. Ces études et contrôles
ne remplacent ni la critique des véritables exports, ni une projection
continue, ni une écoute sur téléphone.
