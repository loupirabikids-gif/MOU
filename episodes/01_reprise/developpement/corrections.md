# Décisions — nouvelle réalisation du Retardateur

Les sections ci-dessous conservent l’historique. Les décisions des révisions 1
et 2 ne décrivent pas la fin courante de la révision 3. Toute ancienne directive
interne demandant des bras raccourcis, sans long J ou des racines masquées est
retirée : les deux bras canoniques `_arm` doivent rester tels quels.


Commande : refaire l’épisode depuis le début après la confusion entre plusieurs
anciennes versions. Nouveau dossier01_reprise et nouveaux noms de MP4 ; aucun
ancien média de episodes/01 n’est modifié.

| Phase / fait observé | Décision et correction | Contrôle |
| --- | --- | --- |
| Proposition initiale : réglage3s mais clic5s après activation | Retenir la réserve commune scénariste/critique : réglage5s, chiffres5/4à1/2s puis3/2/1à3/4/5s et flash6 | Chronologie verrouillée avant fabrication, compteur régulier ; le1 reste affiché pendant l’abandon |
| Anciennes attaches du bras et long J ventral signalés par l’utilisatrice | Bras baissés courts, une seule mitaine, racines masquées dans le torse pour une émergence visuelle au flanc ; aucune pose clasp | Trois poses de construction examinées indépendamment ; chute et retour contrôlés dans l’encodé |
| Premier jeu : bouche enU après flash lisait joie | PetitO de surprise à6,5/8,75 avant lecture du cliché | Nouvelle planche examinée par critique avant montage |
| Premier montage complet : risque du faux départ et de grimace volontaire | Conserver le changement de regard, souffle, bras qui abandonnent puis chute unique138→144 ; aucun clic anticipé | Critique du vrai MP4 :29images119→147, le1 reste visible, extrême au flash et aucune grimace volontaire tenue |
| Résultat photographique | Montrer le même téléphone en gros plan fixe, image calculée à6s par le même personnage, PNG2× | Photo lisible à270px dans le vrai montage, bras courts intacts, aucune image avant capture |
| Fin11–13s : petitU et regard presque frontal pouvaient lire l’apaisement | Retenir la réserve : bouche presque plate ou coin défait et regard bas de côté ; bras, pose, temps et son conservés | Correction ciblée du visage, puis revue du nouveau MP4 avant final |

Les avis conceptuels, poses et montage sont distingués dans les critiques.
Aucun test public ou résultat d’audience n’est inventé. La veille externe
reste incomplète, sans empêcher cette reprise explicitement demandée.


## Revue de la fin corrigée et passage au final

Le critique revoit le MP4 réencodé aux instants9,25/9,85/10,25/10,5/11/11,75/
12,5/12,958s, dont réduction270×480. Le regard évite désormais l’objectif et
la bouche n’a plus le petit sourire apaisé ; la gêne prolonge la déception.
Les bras restent courts et attachés. Réserve levée, aucune autre correction
ni coupe imposée :13s conservées. Son avis porte sur le vrai montage léger ;
le coordinateur contrôle ensuite le final1080 par décodage et SVG frais.


## Révision2 — retour au dessin original des bras, àla demande de l’utilisatrice

Les bras raccourcis et leurs masques de racine sont retirés. Les groupes
`_arm` du rig original sont réutilisés sans remplacement. Les312poses, les
bouches, les déformations corporelles et le mix sont strictement conservés.
Le cadrage et l’ombre du cliché sont figés aux valeurs précédentes : hors
les deux groupes de bras, le SVG de la photo reste strictement identique.
La demande de conservation du dessin original prévaut sur les adaptations
esthétiques internes précédentes ; aucun autre geste, rythme ou scénario
n’est modifié. Contrôles : audit_restauration_bras.json et restauration_bras.md.

## Révision 3 — visage capturé et rire nerveux, à la demande de l’utilisatrice

La correction porte sur l’expression de la capture et la réaction finale.
Le début, le compte régulier, le flash à 6 s, le modèle, le rig et le dessin des
bras sont conservés. La nouvelle demande remplace volontairement l’ancienne
bouche pendante, le O de surprise et la fin au regard baissé.

| Demande / risque | Décision | Contrôle prévu sur le vrai rendu |
| --- | --- | --- |
| Visage de référence : un œil grand ouvert, l’autre légèrement fermé ; MOU louche et sourit nerveusement de travers | Paramètres indépendants pour la convergence des pupilles et sourire oblique crispé ; aucune nouvelle anatomie | Deux pupilles visibles dans leurs masques au flash et à la dernière pose |
| Le clic doit photographier cette expression exacte | Source unique `character_at(pose_at(6.0))` pour scène et photo ; arrêt de cinq images à la capture | Comparer capture et cliché, puis vérifier le maintien après le flash |
| Photo environ une seconde et immobile | Même téléphone, photo fixe de 6,75 à 8 s soit 1,25 s | Comparer les images du MP4 à l’intérieur de l’insert |
| MOU regarde le résultat puis le spectateur | Regard vertical commun ajouté aux décalages horizontaux convergents ; pas de retour au visage serein | Lire l’ordre des regards de 8 à 10,25 s |
| Sauver les apparences plutôt que rester simplement déçu | Sourire un peu plus crispé et sourcils gênés de 10,25 à 11,5 s | Réserve du critique : couper si cette intention devient un temps mort, sans mouvement gratuit |
| Deux petits hé soufflés avec deux minuscules secousses | Sons originaux synthétisés localement aux secondes 277/24 et 287/24, durée 0,25 s chacun ; mêmes repères pour le corps | Vérifier synchronisation et niveau du mix exporté ; ne pas confondre audit numérique et écoute humaine |
| Fin tenue dans le silence | Pose identique et silence de 12,5 à 13 s | Comparer les douze dernières images et l’audio décodé |

La [recommandation du critique avant fabrication](critique_scenario_fin_v3.md)
est consignée séparément. La [critique du vrai montage](../controle/critique_fin_v3.md)
sera le lieu des constats sur le rendu et des corrections réellement retenues.
Ce journal de décisions ne revendique aucune écoute humaine ni validation du
MP4 avant leur contrôle par la coordination.


### Revue et export de la fin révision 3

Le premier MP4 de cette fin montrait encore une bouche en U trop sereine.
Le coordinateur et le critique ont retenu une correction strictement locale :
sourire plus plat à gauche, coin droit pincé et petite commissure. Les 312 poses
et tous les SVG hors bouche restent identiques à ce premier montage.
La critique du nouveau MP4 540 × 960 confirme la photo fidèle, les regards et
les deux microcontractions ; elle accepte les 13 s, l’hésitation avant le rire
restant motivée par la crispation. Aucun changement des bras n’est retenu.

Le final 1080 × 1920 est décodé intégralement avec sa version muette. Douze
gestes correspondent aux SVG frais, photo et pose finale restent figées,
les deux vocalisations sont présentes et la demi-seconde finale est silencieuse.
Les chiffres et limites figurent dans `../controle/audit_final.json` et
`../CONTROLE.txt`. La critique et le contrôle audio numérique ne prétendent
à aucune écoute humaine ni à un test public.
