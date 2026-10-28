# Carotte avant tomate — ordre V12

Retour de l’utilisatrice : placer la découpe de carotte avant le geste où MOU
jette la tomate dans la poêle. La durée reste de 35 secondes ; les gestes du
modèle, les deux moufles, le tablier, la légende et le dernier papier souple
sont conservés.

## Découpage courant

| Temps du film | Action |
| --- | --- |
| 0–13,5 s | Ouverture, premier lavage et premier gaspillage conservés. |
| 13,5–16,5 s | Carotte : deux coupes à 14,55 et 15,25 s ; couteau posé à 15,95 s, inspection de main à 16,3 s. |
| 16,5–21,5 s | Deuxième lavage, essuyage, jet et zoom poubelle. |
| 21,5–23 s | Tomate ajoutée à la poêle à 22,3 s ; nouveau regard sur la main. |
| 23–35 s | Troisième rituel, reprise du manche, dernier petit papier et fin conservés. |

Les rituels gardent leur rang : le deuxième consomme la bande de quantité 1,4
et donne la deuxième boulette de rayon 53 ; le troisième garde la quantité
1,9 et le rayon 59. Le rouleau continue de diminuer et la poubelle de se
remplir. Intervertir simplement les clips complets aurait inversé ces états.

## Référence commune et continuité

La chronologie principale contient les nouveaux repères de production. Les
fenêtres musicales deviennent 0–7,75 /13,5–16,5 /21,5–23 /27–28 s. Les sons
de coupe et de tomate se déplacent avec leur action ; les fenêtres de lavage
restent muettes musicalement.

`animation_reference` reste la référence native antérieure de 30 s. Le champ
`action_reorder` décrit trois translations sans changement de vitesse :
13,5–16,5 du film emploie 15–18 natif ; 16,5–21,5 emploie 10–15 natif ;
21,5–23 emploie 8,5–10 natif. `state['t']` conserve cette horloge pour la caméra
et les gestes existants. Le renderer n’a pas besoin d’être modifié.

Le rang de cycle, le stock et le contenu de la poubelle suivent le temps réel
du film. La tomate reste sur sa coupelle jusqu’au geste désormais à 21,5 s ;
elle n’apparaît pas prématurément dans la poêle. Après la découpe, les deux
rondelles et le couteau posé persistent pendant le deuxième rituel et la tomate.
Les états hors de la fenêtre 13,5–23 s restent identiques à la V11.

## Études examinées

`controle/etude_ordre_v12/planche.png` : 18 poses du nouveau déroulement,
avec détails natifs de découpe et de prise de tomate. La planche et deux détails
ont été réellement vus : le nombre de boulettes et le stock progressent dans
le bon sens ; les rondelles restent visibles avant la prise de tomate ; la
tomate attend sur sa coupelle pendant la découpe. Les prises et bras sont
ceux des actions précédemment fabriquées.

Vérification de préparation sur 840 états : hors fenêtre de montage, état
complet identique à la référence V11 ; quantité de papier décroissante,
contenu de poubelle, coupes et arrivée de tomate monotones. Les huit fonctions
natives de bras/raccord sont identiques. L’audit indépendant et la critique
des véritables exports complètent ces études ; elles ne valent pas projection
continue ou écoute perceptive.
