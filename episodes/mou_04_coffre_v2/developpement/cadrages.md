# Cadrages fabriqués — Le coffre V2

Le module `sources/cadrage.py` définit treize plans sur trente secondes. Chaque
viewport s’applique globalement au décor, au personnage et aux accessoires,
après leur mise en place. Les cartouches temporels restent hors caméra. Aucun
bras ou objet n’est déplacé séparément pour simuler un nouvel angle. Les vues
de base sont les dessins 2D existants ; les rapprochements et le recul sont 2D.

## Découpage et intentions

Coordonnées du viewport dans l’image de base, sous la forme `(x, y, largeur,
hauteur)`. Le rapport reste 9:16 pendant les deux mouvements.

| Plan | Temps | Vue et viewport initial | Intention / regard | Pause et raccord | Accent éventuel |
| --- | --- | --- | --- | --- | --- |
| P01 | 0–2,1 | wide_high · (220, 620, 760, 1351,111) | Réunir visage, feuille, crayon, téléphone et coffre. Les yeux quittent la feuille pour le téléphone. | Le choix précède l’insert de l’objet. | Notification brève, après l’installation du travail. |
| P02 | 2,1–4,6 | lock_insert · (100, 200, 780, 1386,667) | Mains, dépôt, couvercle, bouton et 30:00. Visage volontairement hors champ. | Dépôt, retrait, fermeture et bouton se lisent comme des gestes successifs. | Matières distinctes pour dépôt, fermeture et verrou. |
| P03 | 4,6–6 | medium · (70, 500, 740, 1315,556) | Le regard et le crayon reviennent vers la feuille. La boîte subsiste au bord. | Courte certitude avant la contradiction de l’horloge. | Laisser le geste porter la satisfaction. |
| P04 | 6–7 | clock · (80, 160, 920, 1635,556) | L’horloge et 09:01 donnent une seule minute écoulée. | Insert unique, puis retour au même travail. | Aucun bip à chaque minute. |
| P05 | 7–10 | medium · (70, 500, 740, 1315,556) | Le regard glisse vers la boîte et revient ; la tentative se bloque. | Conserver la continuité de l’intention commencée en P03. | Espace sonore autour du regard. |
| P06 | 10–12,25 | work_close · (80, 420, 900, 1600) | Concentrer l’attention sur la main qui abandonne le crayon et le visage. | Couper après l’abandon, pas au milieu d’une prise. | Petit contact du crayon. |
| P07 | 12,25–15,2 | medium · (160, 610, 570, 1013,333) | Deux yeux et joue appuyée dominent ; le regard reste attiré vers la boîte. | Resserrement motivé par le renoncement. | Pas de vocalisation synthétique ajoutée. |
| P08 | 15,2–18,4 | medium · (0, 0, 1080, 1920) | Révéler la posture fermée, la feuille et l’horloge. | Changement d’échelle pour montrer la nouvelle posture et l’ellipse. | Fond discret, sans boucle de vérifications. |
| P09 | 18,4–21,7 | low · (240, 550, 825, 1466,667) | Les yeux ouverts visent le minuteur ; les mains restent au plateau. | Rapprochement de 3 % entre 18,55 et 19,25, puis arrêt. | Attente sans ticks répétés. |
| P10 | 21,7–23 | box_insert · (40, 450, 900, 1600) | Le verrou et le dernier chiffre deviennent l’unique centre. | Suspendre avant l’ouverture, ne pas anticiper la récupération. | Déverrouillage matériel. |
| P11 | 23–25,4 | face_box · (0, 70, 1080, 1920) | MOU, deux yeux, ouverture et reprise dans une seule image. | Maintenir les contacts et la causalité. | Charnière et réponse du mécanisme. |
| P12 | 25,4–27 | phone_final · (160, 500, 710, 1262,222) | Face et téléphone à deux moufles ; regard vers l’écran. | Satisfaction courte avant le coût révélé par le papier. | Pas de fanfare ni voix imposée. |
| P13 | 27–30 | phone_final · (90, 1490, 180, 320) | D’abord TO DO et trois cases vides ; ensuite MOU ravi, téléphone et 09:30. | Maintien papier jusqu’à 28 ; recul 28–29,2 vers (0, 60, 1080, 1920), puis maintien jusqu’à 30. | Fin calme. |

## Contrôles et corrections effectués

La planche `work/cadrage/board_candidates.png` et ses quinze images
individuelles sont calculées par `scene.svg_at`, avec les treize nouvelles
fenêtres de caméra, non dessinées à la main. Les suppléments P13b/P13c montrent
le recul et la dernière composition. Une première version de la planche avait
été calculée avant l’arrivée de `jeu_mou.py`. La planche a été recalculée après
son intégration : la version conservée emploie bien l’acting réel, sans fonction
de remplacement. Son examen reste une vérification de compositions et de poses
échantillonnées, pas une lecture continue du montage.

- L’insert initial du papier a été décalé à droite pour montrer TO DO entier,
  et descendu pour retirer le morceau de corps présent dans le premier essai.
  Les trois cases restent celles de la feuille frontale existante, vides et
  fixes pendant le recul. Aucune vue en plongée n’est substituée.
- Le plan bas a été recomposé pour retirer l’heure flottante au bord haut et
  la bande de mur apparaissant sous le panneau du bureau dans le premier essai.
  Les deux yeux et l’afficheur complet restent visibles après le push de 3 %.
- Dans P03/P05, le viewport finit à x810, avant le LCD qui commence à x829,8.
  P07 finit à x730. Le cadenas et le bouton peuvent se voir au bord, sans aucun
  chiffre partiel. L’interprétation initiale en planche d’un demi-LCD a été
  corrigée par l’ouverture de l’image individuelle.
- P12 finit à x870 ; le LCD final déplacé par la réalisation commence à x1106.
  P13 finit au plus à x1080. Aucun chiffre du coffre n’apparaît donc à moitié
  dans les plans de satisfaction et de chute.
- L’horloge finale est placée par la réalisation à (924, 350), rayon104, pour
  conserver l’horloge et 09:30 au plan d’ensemble. La demi-horloge du plan de
  reprise a été sortie du champ par la réalisation.
- Le ratio 9:16 et la couverture sans trou des 720 instants à 24 i/s ont été
  contrôlés par script. Les vues de réaction gardent les deux yeux dans les
  images de composition examinées.

Ces contrôles d’images ne remplacent ni la lecture du montage complet, ni un
test de compréhension, ni une audition de la bande-son. L’animatique et le MP4
doivent encore vérifier les gestes aux coupes, la tenue du téléphone, la
lisibilité de la feuille à petite taille et le rythme effectif du recul.
