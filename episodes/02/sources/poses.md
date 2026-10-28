# Jeu de MOU — Le torchon

Source : animation.py, chronologie commune ../chronologie.json. Durée 12s,
24images/s, libération7,25s et contact du visage7,50s. Le rig partagé est inchangé.

## Construction conservée

Chaque bras provient exactement de mou_rig._arm(side,arm_hips,arm_clasp).
Les paramètres arm_hips et arm_clasp sont communs aux deux côtés. Un groupe
d’articulation fait seulement pivoter chaque fragment natif autour de sa racine
(105,291) ou (297,291). Aucun chemin, rayon de moufle, raccord ou masque de
racine n’est redessiné. Les deux moufles restent distantes d’au moins51unités.

Le corps, le visage et les racines des bras partagent la même affine de jeu.
Les pieds gardent la géométrie du rig ; seul lift_l utilise sa levée native
(20unités) pour libérer le tissu. Le pied droit demeure au sol.

## Jeu et contacts

- 0–1,5s : regard vers le coin libre, petit accroupissement. Le coin est déjà
  plissé et relevé ; il reste immobile avant la prise, sans voler vers la main.
- 1,5–2s : les deux moufles saisissent la lisière ; MOU se redresse et déplie
  le tissu. Les prises sont calculées dans les moufles natives, puis transformées
  par les mêmes rotations et affine que leurs bras.
- 2,25–3s : première traction, arrêt et réajustement ; sourcils intrigués.
- 4,25–6s : seconde traction plus forte vers le menton, silhouette tendue.
  Les plis du torchon convergent sous le pied gauche. Le droit est hors tissu.
- 6–7s : regard qui descend vers le pied gauche, compréhension de son erreur.
- 7,208–7,25s : levée du pied gauche. Le bord libre reste fixe à l’image7,25s.
- 7,25–7,5s : les mains montent d’environ24unités (71pixels à l’échelle finale).
  Le bord libéré se déplie en éventail et remonte sur le visage. Ce geste
  remplace le premier essai où les mains ne montaient que de8unités.
- 7,5–8,5s : visage couvert, bref arrêt et silence.
- 8,5–9s : le pied redescend ; préparation de la baisse du tissu.
- 9–10,5s : les mains descendent et le tissu se replie, laissant apparaître
  les deux yeux. Le tissu conserve sa largeur matérielle, avec projections
  plissées variables ; il ne s’agit pas d’une simulation physique.
- 10,5–11,5s : les pupilles se dirigent vers le même pied gauche, sourcils
  contrariés ; MOU rejette la faute sur son pied.
- 11,5–12s : pose et tissu strictement identiques pendant12images.

## APIs

pose_at(t) renvoie tous les paramètres numériques, avec les clés standard
du rig et arm_rot_l/r, body_sx/sy/skew/dx/dy. Le temps de jeu _t est bloqué à11,5s
pour garantir la dernière tenue. motion_at(t) est l’identité : pas de dérive
globale des appuis. character_at(p,uid) contient le personnage ET le torchon,
dans leur ordre de dessin final.

cloth_geometry_at(t) renvoie prises, lisière tenue, bord libre, polygone,
phase, état pinned/released et fraction de dévoilement. contact_at(t) ajoute
erreurs de contact après prise, séparation des mains et état du pied bloquant.
Avant1,5s, cloth_grips désigne la cible de prise fixe, pas des mains déjà liées.
Le champ face_covered indique une phase approximative ; les pixels du
dévoilement sont à juger dans le rendu, pas à déduire de ce booléen.

## Occlusion du pied et correction éprouvée

Le torchon passe devant le torse mais derrière les soles existantes grâce à
un clip vectoriel avec contours de trous de sens opposé. Le premier masque
de luminance était mal pris en charge par CairoSVG et cachait les pieds :
il a été retiré. Seul l’accessoire est découpé, jamais les bras ou leurs racines.
Les ellipses des pieds ne sont pas dessinées une seconde fois.

Un second défaut du premier tissu large a été corrigé : il passait sous les
DEUX pieds, rendant la libération impossible. Le pli au sol est désormais
rassemblé vers la gauche ;72points du périmètre de la sole droite sont hors
du panneau à chacun des174photogrammes précédant la libération. Le pied gauche
recouvre bien un point intérieur du tissu.

Preuves livrées : ../controle/contacts_animation_v3.png et audit_animation.json.
La première étude et sa critique sont conservées dans
../controle/critique_contacts_v1.md ; la V3 est examinée dans
../controle/critique_contacts_v3.md. L’audit de288poses vérifie deux mains,
chemins natifs exacts, IDs uniques, appui, contact et tenue finale.
La revue du véritable MP4 figure séparément dans ../controle/critique_montage.md.
