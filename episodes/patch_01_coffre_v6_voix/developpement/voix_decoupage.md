# PATCH — intentions vocales et synchronisation V6

Observation : 3 novembre 2026, Africa/Casablanca. Ce découpage est une
proposition de placement, pas une audition de prises. Les vocalisations
Soundgen ne sont pas encore disponibles lors de sa rédaction.

La V5 réellement décodée (`f86fd51e079578b65182cf154baaaf3993baff9af0372885b7825d58f1d797d5`)
a été examinée aux images zéro-basées 114, 314, 420, 432, 439, 553, 603 et
608. La planche privée est conservée dans `work/critique/base/planche.png`.
Les choix ci-dessous suivent ses poses et ses coupes, sans reprendre des
horodatages de la référence Runway.

## Cinq accents, avec de longues plages sans voix

| Intention | Fenêtre cible dans le film | Accent de jeu, image zéro-basée à 24 ips | Image et geste compatibles |
| --- | --- | --- | --- |
| Décision, petit « hm » bouche fermée | 4,75–5,05 s | 4,875 s, f117 | Patchy a verrouillé le coffre et revient à sa feuille. Un petit signe de détermination se comprend ici. Le choix évite la notification à 0,65 s et la prise à 1,7 s. La bouche reste fermée ; pas de faux dialogue articulé. |
| Ennui, expiration brève | 13,0833–13,6667 s | 13,25 s, f318 | La joue est appuyée dans la moufle depuis 12,86 s. Une très petite ouverture ou une bouche pincée accompagne l'expiration ; la moufle ne bouge pas et continue de porter la joue. Ne pas transformer ce soupir en sourire avec des dents. |
| Somnolence, bâillement unique | 17,5–18,2917 s | 18 s, f432 | Paupières déjà lourdes, bras croisés. Une bouche arrondie s'ouvre puis se ferme avant la coupe de 18,4 s. Le geste finit avant l'éveil à 19 s ; pas de ronflement qui continuerait après les grands yeux. |
| Surprise, petite inspiration | 23,0417–23,2917 s | 23,125 s, f555 | Après l'insert du compteur, le visage revient avec les yeux ouverts et sa bouche O déjà lisible. Ne pas changer la prise du couvercle ni les mains. Le ping de fin existe à 23 s : contrôler numériquement le chevauchement et garder l'inspiration courte. |
| Joie, deux petits souffles de rire | 25,125–25,5833 s | 25,125 s, f603 ; puis 25,3333 s, f608 | Les deux pieds sont en l'air, le téléphone est tenu à deux mains, la bouche est ouverte depuis 25,12 s. Deux pulsations de bouche suffisent. Ne pas secouer le corps ou déplacer les mains : cela pourrait casser les contacts du téléphone validés. |

Les accents proposés sont des repères de l'action. Une fois les WAV produits,
leur attaque utile et leur accent doivent être mesurés : le début du fichier
n'est pas forcément le sommet de l'intention. Calculer `audio_start =
action_accent - clip_accent`, puis arrondir au sample à 48 kHz. Les fenêtres
ci-dessus peuvent être légèrement adaptées à la vraie durée de la prise,
mais la fin du bâillement doit rester avant 18,4 s et le rire avant 26,65 s.

## Limites de mise en scène

La V5 a validé les bras, le coffre, l'horloge et les prises du téléphone.
La V6 ne doit ajouter que le petit jeu facial et respiratoire utile aux voix.
Une respiration éventuelle se fait par un décalage de tête ou des paramètres
du visage ; ne pas modifier la transformation du corps auquel les objets
sont attachés. Éviter la bouche O fixe qui apparaît en une image : interpoler
son ouverture si une nouvelle bouche de bâillement est introduite.

Aucune voix lors des cartons de temps, du gros plan des trois cases vides
ou de la pose finale absorbée par le téléphone. Le contraste « trente minutes
de concentration, aucun travail fait » doit rester visible sans être commenté.

## Ce que la revue finale doit prouver

- Le MP4 réellement encodé montre l'ouverture de bouche pendant la prise
  et la refermet à sa fin ; les accents audio mesurés rejoignent les repères
  de jeu à une image près.
- Le bâillement ne déborde pas sur l'éveil et le rire ne traverse pas la
  coupe vers la feuille.
- Les membres, le téléphone, les cadrages et la session de trente minutes
  restent cohérents avec la V5 ; aucune nouvelle collision.
- Absence de saturation, attaques et fins non coupées, volume stable entre
  les prises. Ces mesures ne démontrent ni naturel ni confort à l'oreille.

Une vraie écoute de la planche de voix et du mix restera nécessaire pour
juger si l'identité de Patchy est attachante et si les sons évoquent bien
les intentions. Il n'est pas possible de le conclure à partir des seuls
spectrogrammes et formes d'onde.
