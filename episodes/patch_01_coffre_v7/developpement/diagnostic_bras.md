# Bras et coffre — diagnostic V7

Le signalement porte sur le MP4 V6 réellement livré, pas seulement sur le
modèle ou les quatre poses d'attente précédemment contrôlées. Fichier examiné :
`PATCH_Le_coffre_V6_voix.mp4`, SHA256
`f9069b502ca3fccbae72135d2d6b9d166d223a68e745ca9a227dac4b82800d89`.

## Images examinées

120 images décodées à quatre images par seconde sur les trente secondes.
Trois planches ont été ouvertes : début et dépôt/fermeture (0–4,75 s),
ouverture/reprise/joie (22–26,75 s), puis poses d'attente réparties entre
5,25 et 21,25 s. Ces preuves restent dans `work/bras/v6/`.

Le contrôle du seul emplacement de la paume au repos à 13,5 ou 19–21 s ne
couvrait pas la fermeture et la pression sur le bouton. Le succès de ces
contrôles antérieurs n'invalidait donc pas le défaut signalé.

## Défaut réel retenu

Entre environ 3,5 et 4,25 s, la main droite quitte le couvercle et descend
sur la façade : elle recouvre le début du LCD, particulièrement à 3,75 et
4 s. La manche disparaît derrière le flanc alors que la paume est peinte
devant les chiffres. Le spectateur peut lire un bras traversant le volume,
et les trente minutes sont momentanément masquées.

La paume qui presse est centrée vers x755, y1395 alors que le LCD commence
à x754 et que le bouton est à x731, y1417. Le geste vise donc trop à droite
et trop haut pour une pression latérale claire. Changer uniquement le
masque cacherait la main et ne rendrait pas la trajectoire crédible.

## Contacts conservés

La manche devant le panneau ouvert vers 23,54–23,79 s peut correspondre
au geste de levée du couvercle. La main sur son bord à 23,04 s et la prise
du téléphone à 24,04 s sont des contacts voulus. La critique indépendante
les juge plausibles ; aucun masque global du panneau n'est demandé.

Une vérification du point flottant exact 24,05 s avait montré une valeur
isolée de rotation différente. Les vraies images 577 et 578 du film à 24 ips
passent en revanche de −89,79° à −89,39°, sans saut visible. Ce point
numérique n'est pas retenu comme défaut artistique du MP4.

## Correction proposée

`sources/bras.py` conserve toutes les poses hors 3,20–4,65 s. À la fin de
la fermeture, la paume est relevée de 21 unités et glisse de 200 unités
vers le coin gauche du panneau, au lieu de finir au milieu de sa largeur.
Elle se retire vers la gauche, descend à l'extérieur du coffre et approche
le bouton latéralement. La pression se fait vers x690, y1417 : le bord de
la moufle atteint le bouton sans cacher le LCD. L'accent sonore à 3,9 s
et le verrouillage à 4 s restent en place.

Un poignet explicite à gauche de la paume et un coude extérieur empêchent
la manche de suivre la ligne directe épaule→paume à travers le flanc.
Le coordinateur adapte le tracé du bras pour ces contrôles : une normale
unique à toute la manche créait un triangle trop fin dans le premier
prototype et n'a pas été retenue. Les coordonnées du poignet doivent être
transformées avec les mêmes scale/tx/ty que celles des mains.

Le téléphone, les vues, le temps, les deux moufles et les gestes de reprise
restent ceux de V6. Les nouvelles poses, puis les vraies images encodées,
doivent être revues après l'intégration du tracé courbe.

## Première intégration revue

Seize poses du véritable `scene.py` V7 avec le bras cubique du coordinateur
ont été rendues et ouvertes entre 3,20 et 4,65 s. La manche reste large et
courbée ; le bord de la moufle atteint le bouton sans couvrir les chiffres.
Le trajet court par le coin remplace un premier détour trop long.

Le helper a été contrôlé sur 720 états : l'entrée n'est jamais modifiée,
685 sorties sont strictement identiques et les 35 autres ne touchent que
le bras droit et ses repères de contact. La patte droite rasterisée sur ces
35 images ne dépose aucun pixel dans la zone du LCD. Ces vérifications
concernent la scène intégrée ; la critique du MP4 V7 encodé reste distincte.

`bras.py` gelé :
`b9047294f0ab0362518da8fe9ae3b09916b2fdea6b6dbed43bcb3da880179892`.
Aucune audition du son n'est revendiquée par ce diagnostic visuel.
