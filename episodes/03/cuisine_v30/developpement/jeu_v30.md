# Direction de jeu V30 — MOU original

Sources modifiées : `performance.py` et `jeu_visage.py` uniquement. Le dessin
canonique, les formes des bras/moufles, le solveur, les cibles de prise et de
présentation des mains, les gestes de recette, les plans et la durée restent
les références V28. L'affine du torse entraîne les membres libres avec lui ;
aucune trajectoire de main indépendante ou nouvelle cible n'est ajoutée.

| Passage | Intention et contraste ajouté |
| --- | --- |
| 0–2,75 s | Chef plus satisfait de lui : sourire large légèrement de travers et regard sur la cuillère. Souplesse limitée pendant le geste contraint. |
| 2,92–3,50 s | Une trace minuscule provoque un bref étonnement : visage et étirement culminent pendant deux images vers 3,04–3,13 s. Ensuite un œil se pince tandis que l'autre inspecte largement ; cette attitude reste lisible jusqu'au départ. Le regard atteint la trace avant la réaction. |
| 7,05–7,58 s | Première victoire ridicule : sourire trop heureux pour un simple essuyage, yeux apaisés et petit redressement tenu. |
| 10,5–19,5 s | Les retours au lavage deviennent contrariés : asymétrie des paupières et sourcils plus marquée au deuxième cycle, puis bouche serrée et œil pincé au troisième. La tête ne s'agite pas au hasard. |
| 21,95–22,45 s | Vraie décision suspendue. La matrice du corps et les mains restent identiques durant cette tenue. Le murmure nasal coïncide avec une petite bouche pincée ; aucune ouverture de parole. Il abandonne ensuite avec des paupières tombantes et une bouche baissée. |
| 25,63–25,92 s | Devant la fumée, inspiration visible et petit étirement. Puis le regard retourne à la main : il choisit encore le rituel. |
| 26,52–26,65 s et 28,25–28,38 s | Écrasements brefs de trois images suivis d'un dépassement et d'un retour au volume. Le papier et les bras suivent le mécanisme de contact existant. |
| 31,75–32 s | Surprise du repas raté : petite anticipation verticale, bouche en O et pupilles réduites, écrasement franc tenu trois images vers 31,83–31,96 s. |
| 32,75–33,17 s | L'expiration est distincte du choc : petite bouche soufflée, puis bouche baissée et corps légèrement affaissé. La matrice ne continue pas à rebondir pendant la déception. |
| 33,25–35,75 s | Les deux inspections successives des moufles restent avant le triomphe. Le sourire naît vers 34,70 s et devient trop fier pendant le petit murmure nasal à 35,15 s. |
| 35,75–38 s | Regard vers le public puis pose finale : sourire décentré, paupières satisfaites et mains natives devant le torse. Le corps et le visage restent tenus dès 37,25 s. |

## Synchronisation prévue des cinq voix existantes

Les ancres sont les pics RMS sur 8 ms communiqués par le responsable son ;
elles ne prouvent pas l'instant perçu d'un son ou l'émotion entendue.

| Voix | Pic numérique | Réponse visible prévue |
| --- | --- | --- |
| Hésitation | 22,03402 s | Bouche pincée fermée tenue de 22 à 22,125 s, corps immobile. |
| Inspiration | 25,76619 s | Bouche en O tenue ouverte de 25,667 à 25,875 s. |
| Choc | 31,85998 s | O franc tenu de 31,833 à 32 s ; écrasement pendant les trois premières images de cette tenue. |
| Expiration | 32,80821 s | Petite bouche soufflée au maximum entre 32,792 et 32,875 s, puis fermeture lente. |
| Satisfaction | 35,16219 s | Sourire fermé tenu de 35,125 à 35,333 s et léger redressement. |

## Contrôles effectués avant rendu

Les 912 états de scène s'évaluent avec des nombres finis et deux mains.
Le produit des échelles reste égal à 1 pour tous les états de torse concernés.
Les échelles verticales effectivement observées vont de 0,75 à environ 1,14.
Quatre états répartis dans la tenue de résistance donnent une seule matrice
et une seule paire de positions de mains. Les cinq actions vocales sont
exposées dans `expression.vocal_sync` pour contrôle du vrai montage.

Ces vérifications ne valident pas l'image finale : relire l'animatique et les
inserts réellement encodés, surtout le visage comprimé au choc, les contacts
papier pendant les accents et le volume du costume. Aucun rendu complet ou
écoute n'a été effectué par ce mandat d'animation. La critique du résultat
appartient au critique indépendant et au coordinateur.

## Correction retenue après examen du HD

La critique du vrai export a trouvé à 31,875 s une bouche de choc tronquée par
la ceinture du tablier. Le crop `work/cuisine_v30_critique/final/mouth_detail.png`
confirme cette superposition. Correction limitée à `jeu_visage.py` : le O garde
sa demi-largeur de 31 unités, son ouverture passe de 1 à 0,8 et son groupe
remonte progressivement de 8 unités natives au maximum. L'enveloppe monte de
31,667 à 31,833 s, reste maximale jusqu'à 32 s puis revient à zéro à 32,5 s.
Corps, bras, costume, durée et son restent inchangés par ce correctif.

Les six SVG aux instants 31,75 ; 31,833 ; 31,875 ; 31,917 ; 32,083 ; 32,25 s
ont été rendus en HD dans `work/cuisine_v30_animation_correction/`. La planche
et l'image HD du pic montrent la bouche entière au-dessus de la ceinture,
avec du vert entre bouche et yeux. Des masques natifs à résolution quadruple
ne trouvent aucun pixel de bouche superposé au costume ou aux contours des
yeux à ces six instants. `expression.mouth_offset_native` et
`expression.mouth_anchor_native` exposent la correction pour la QA.
Cette vérification de SVG frais reste à confirmer dans le nouvel export vidéo.
