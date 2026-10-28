# Le torchon — découpage de fabrication

Révision1 ·12s ·24images/s ·288images ·1080×1920.

Le « Vas y » du28octobre2026 autorise la fabrication de ce scénario. La source
commune est `../chronologie.json`, verrouillée par la coordination avant animation
et son. Le scénario écrit précédent reste historique ; il ne doit pas être pris
pour une interdiction de produire après cette nouvelle commande.

## Intention et information

MOU repère le coin libre et veut ramasser le torchon, sans regarder le bout
bloqué sous son pied. Le public voit le pied qui l’immobilise dès les
premières tractions, tandis que MOU fixe sa prise. Son obstination conduit à
la libération maladroite ; sa dernière réaction accuse son pied. Le geste et
sa cause doivent se comprendre sans les sons.

Un plan frontal continu suffit : éviter un recadrage qui cacherait le pied ou
séparerait la levée de l’appui et le trajet du tissu. Le tissu reste devant le
corps dans la traction ; il ne devient pas un ressort et ne saute pas de couche.

## Actions visibles

| Temps / images | Action, intention et anticipation | Regard / expression | Contacts et tenue | Son |
| --- | --- | --- | --- | --- |
| 0–2s / 0–47 | Ramasser le coin libre. Petite flexion pour approcher le coin sans saut de tissu. | Curiosité simple ; regard vers le coin puis ses mains. | Deux mains prennent la même lisière ; autre extrémité continue jusqu’au pied qui la bloque. | prise_tissu à1.5s (0.15s) |
| 2–4s / 48–95 | Surmonter une petite résistance. Courte préparation à2,25s, traction culminant2,5s, arrêt net puis réajustement. | Intrigue puis sourcils qui se resserrent ; regard sur sa prise. | Tissu lié aux deux moufles ; extrémité au sol bloquée. | traction_1 à2.25s (0.4s) |
| 4–6s / 96–143 | Gagner contre ce torchon obstiné. Anticipation4–4,25s, traction plus forte jusqu’au pic5s, effort maintenu. | Effort sincère, mâchoire retenue ; yeux sur les mains plutôt que sur le pied. | Mains vers le menton, corps en arrière ; tissu tendu devant le torse, sans allongement élastique. | traction_2 à4.25s (0.8s) |
| 6–7.25s / 144–173 | Comprendre ce qui bloque. Le déplacement des yeux précède la décision de lever le pied ; pas de pause décorative. | Le regard descend de la prise au tissu puis au pied ; compréhension brève. | La prise reste ferme et l’effort présent ; pied encore sur le tissu avant la libération. | Pas de nouveau son. |
| 7.25–7.5s / 174–179 | Libérer le torchon tout en continuant à tirer. La levée de l’appui précède le mouvement libre du bord, les mains l’entraînent vers le haut. | Attention au pied, puis yeux pris de court par l’arrivée du tissu. | Un pied se lève ; les deux mains restent liées au tissu ; l’autre pied garde l’appui au sol. | envol_tissu à7.25s (0.25s) |
| 7.5–8.5s / 180–203 | Subir un bref arrêt. Impact à7,5s, petit tassement éventuel puis arrêt, sans rebond répété. | Visage caché ; ne pas le remplacer par une nouvelle grimace gratuite. | Tissu devant le visage et tenu par les deux mains ; aucune téléportation de couche. | flap à7.5s (0.12s) |
| 8.5–9s / 204–215 | Chercher comment se dégager. Très petite préparation des mains, aucun nouveau tirage spectaculaire. | L’intention se lit par les mains, pas une parole. | Les deux prises restent cohérentes avec le bord qui va descendre. | Pas de nouveau son. |
| 9–10.5s / 216–251 | Retrouver la vue. Les mains abaissent progressivement le tissu, pas un effacement par fondu. | Yeux d’abord dégagés, puis attention au pied ; aucune pose sereine vers le spectateur. | Bord du tissu suit les mains et passe sous les yeux ; deux mitaines restent présentes. | revelation à9s (0.85s) |
| 10.5–11.5s / 252–275 | Reporter la faute sur son propre pied. Le regard désigne le pied avant la tenue finale. | Pupilles dirigées vers ce pied, sourcils contrariés ; mauvaise foi plutôt que honte. | Tissu retenu sous les yeux ; position stabilisée, aucun geste ajouté pour remplir. | Pas de nouveau son. |
| 11.5–12s / 276–287 | Soutenir son accusation absurde. Aucun mouvement nouveau pendant cette demi-seconde. | Même regard vers le pied et même expression. | Deux mains et deux pieds du modèle conservés, pose strictement identique. | Pas de nouveau son. |

## Repères exacts communs

- Prise :1,5s, image36. Première traction :2,25s, pic2,5s, images54/60.
- Deuxième traction :4,25s, pic5s, images102/120. Regard vers le pied àpartir de6s.
- Libération :7,25s, image174 ; contact du tissu au visage :7,5s, image180.
- Arrêt sous le torchon :7,5–8,5s, images180–203. Préparation8,5–9s.
- Révélation :9–10,5s, images216–251. Accusation du pied :10,5–11,5s, images252–275.
- Dernière tenue immobile et silencieuse :11,5–12s, images276–287.

Les repères audio sont recopiés exactement dans `storyboard.json` : prise1,5s
(0,15s, −26dBFS cible), traction1 à2,25s (0,4s, −23), traction2 à4,25s
(0,8s, −21), envol7,25s (0,25s, −18), FLAP7,5s (0,12s, −9), révélation9s
(0,85s, −26). Ces niveaux sont des cibles de fabrication, pas des mesures déjà
effectuées. Aucune voix, aucun rire ou musique ne porte la compréhension.

Silences prévus :6–7,25s pour comprendre le pied ;7,75–9s après le FLAP ;
11,5–12s pour le dernier regard. Ils seront contrôlés sur le son réellement exporté.

## Essais nécessaires et modèle retenu

Avant montage, éprouver quelques poses : coin au sol saisi sans lévitation,
deux prises qui restent attachées, pied bloquant visible, levée précédant la
libération, trajet continu jusqu’au visage, lisière abaissée qui révèle les yeux.
Une simple proximité de coordonnées ne suffit pas à valider visuellement un contact.

Le modèle vert et `mou_rig.py` restent la référence ; les fragments `_arm`
d’origine sont conservés sans redessin, raccourcissement ou masque des racines.
Le repositionnement articulé nécessaire doit garder les épaules jointes au torse
et exactement une moufle au bout de chaque bras. Si un geste ne passe pas,
adapter le geste ; ne pas changer le dessin pour faire tenir ce scénario.

Outils de production :Python, SVG, CairoSVG, Pillow, NumPy et FFmpeg. Sons
courts originaux et modifiables, synthétisés localement. La veille récente reste
incomplète (`veille_et_limites.md`) ; aucune tendance ou métrique externe n’est
invoquée pour justifier ce choix. « Le retardateur » reste de côté.

## Portée de ce document

Ceci verrouille les intentions et les repères du travail à produire. Ce n’est
ni une validation des contacts ou du vrai montage, ni une écoute, ni un test
public. La critique du rendu et les corrections effectivement retenues seront
consignées séparément après examen des médias réellement fabriqués.
