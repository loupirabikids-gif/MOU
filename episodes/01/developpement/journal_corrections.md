# Journal des décisions — Le retardateur, révision 3

La V2 au commit `0392a27` est le point de départ. Les critiques historiques restent
conservées ; l'absence de veille externe complète est déclarée dans le scénario.

| Retour et passage | Décision du coordinateur | Modification retenue | Responsable exclusif | Vérification |
| --- | --- | --- | --- | --- |
| Critique V3, 5,25–6,50 : le résultat est annoncé par chute, rebond et pose trop tenue | Retenir | Relâchement à5,75 ; anticipation brève ; une chute de l'image149 à155 ; clic156 sur le premier extrême | Animation : animation.py ; coordinateur : chronologie.json | Vérifié dans le montage encodé V3 : chute149–155 et flash156 |
| Le déplacement rendrait le bruit élastique V2 précoce ou annonciateur | Retenir le conseil du découpage | Souffle5,78–5,98 ; chute silencieuse ; retirer détente du mix, conserver sa source en banque | Son : son.py et sons/ | Audit PCM et repères du MP4 contrôlés ; pas d'écoute subjective revendiquée |
| Critique V3, 11,5–14 : sourire U et mains ventre peuvent paraître sereins | Retenir | Une tentative de faire bonne figure face au spectateur ; regard photo ; sourire qui se casse ; gêne presque sans sourire | Animation | Vérifié sur montage muet : façade puis abandon, fin presque sans sourire |
| Temps de lecture de la photo7,25–8,85 | Préserver | Ne pas raccourcir arbitrairement un résultat qu'il faut reconnaître | Coordinateur/réalisation | Temps de lecture jugé utile dans le montage par la critique |
| Suggestion de raccourcir à13,5 si la dernière tenue est morte | Conditionnelle, pas un ordre de durée | Garder14 comme travail ; réduire seulement si le vrai montage le justifie | Coordinateur après critique | 14s conservées : aucun temps mort justifiant une coupe repéré |
| Min. hauteur V2×0,65 vs capture×0,68 | Accepter×0,68 sans rebond | Ne pas réintroduire un rebond pour retrouver un nombre ; la rupture ample reste le but | Animation | Amplitude et contours revérifiés dans le montage |
| Veille récente inaccessible, YouTube403 | Ne pas inventer ; poursuivre la révision interne du pilote demandé | Rapport de blocage, exigences réseau en brouillon ; cinq pistes provisoires distinctes pour la suite | Veilleur/coordinateur | Collecte externe toujours incomplète |

L'accord artistique du scénario et du découpage a été donné avant la fabrication,
par le critique indépendant ; voir `critique_scenario_v3.md`. Les corrections ont ensuite été vérifiées dans l’animatique, puis le final
1080×1920 a passé ses audits techniques. Voir ../controle/critique_v3.md.


## Réécriture V4 — La dernière retouche

Le retour de l’utilisatrice (« le gag n’est pas clair ») prévaut sur l’accord
artistique antérieur. Deux mécanismes ont été discutés ; la seconde proposition,
une retouche du sourire qui va trop loin, a été explicitement choisie.
Le scénario V3 est archivé dans `scenario_v3.md` ; les découpages et critiques
précédents restent conservés. La veille externe n’est pas devenue complète.

| Passage / retour réel | Décision | Correction | Vérification et portée |
| --- | --- | --- | --- |
| V3 : aperçu avant le clic et délai après1 brouillaient préparation/résultat | Réécrire la causalité | Aucun portrait avant clic ;5→1 régulier ; retouche encore en mouvement au flash154 | Découpage V4 et avis conceptuel indépendant ; montage à vérifier séparément |
| Le personnage doit être sûr d’être beau | Conserver ce désir jusqu’au résultat | Pose satisfaite, premier embellissement modéré, approbation, dernier ajout excessif ; gêne seulement après regard vers photo | Consigne de jeu, pas une validation de réception publique |
| Prototype contact1 : sourire final encore harmonieux | Retenir la réserve commune réalisateur/critique | ±45px de traction et asymétrie verticale +26/−40px, bouche diagonale, une paupière comprimée ; pas de langue ni inquiétude volontaire | Nouvelle amplitude examinée par critique et coordinateur, favorable pour animatique |
| Prototype2/4 : boucle, petit crochet et croisement du ruban droit à6,15–6,417 | Corriger avant montage | Simplifier le contour continu de ce bras en gardant une seule mitaine arrondie, mêmes cibles de contact | Revue dense requise avant gel et montage |
| Nouveau contact mitaine/déclencheur | Tester avant intégration | Avant-bras continu recoupé hors cadre, bout au centre540/1450, appui et changement d’état du bouton | Trois images d’activation examinées par coordinateur et critique ; vitesse à vérifier dans montage |
| Son et contact joues | Synchroniser l’action réelle | Contact3,55s ; première frictionf86 ; secondef142–146 ; silence146–154 et photo7–8,8 | PCM/AAC audioseul vérifiés ; contrôle du MP4 final séparé |
| Réaction finale trop compliquée en V3 | Retenir une seule réaction | Regard bas vers écran, sourire figé, mains baissent9,7–11,1 puis honte ; pas de regain de frime | À vérifier sur montage muet complet |

Les mesures de fichiers et le verdict du vrai montage seront consignés dans
`../CONTROLE.txt`, `../controle/audit_final.json` et `../controle/critique_v4.md`.
Une inspection d’images et un contrôle numérique du son ne valent pas test de public.


### Critique du premier montage complet V4

Le montage réel540×960/312images est examiné en muet par extractions denses,
puis sa piste AAC est contrôlée numériquement. La montée des mains relie la
traction au flash ; l’excès est visible, le raccord tient et MOU ne découvre
l’échec qu’après la photo. Aucune écoute subjective ni test public n’est revendiqué.

Correction retenue7–8,8s : le téléphone entier réduisait fortement MOU au moment
de la révélation. Le critique demande un véritable gros plan du même écran.
Le coordinateur ajoute un recadrage fixe×1,4 sur cet insert : bezel conservé,
photo et mains entières, image toujours figée. La correction doit être revue
dans le MP4 léger réencodé avant le passage au final.


### Accord après correction du montage

Le critique réexamine la révélation réencodée à7/7,8/8,75s, puis en270×480.
La bouche diagonale, la paupière et les deux mains sont plus lisibles. Le même
téléphone se reconnaît au bezel ; bosses, mains et pieds restent entiers.
La largeur de MOU passe de256à359px dans la vidéo540px. La photo reste immobile
(écart moyen7→8,75s :0,00347/255). La réserve est levée : accord pour le final.

Le montage complet relie désormais pose fière, retouche symétrique, dernier
ajout excessif, flash, photo et réaction unique. Les raccords sont revérifiés
dans l’encodé. Il s’agit d’un avis interne par extractions chronométrées,
pas d’une preuve de réception auprès d’un public. Audio décodé analysé,
sans écoute subjective. Rapport final : `../controle/critique_v4.md`.


## Correction graphique V5 — placement des bras

Retour utilisatrice : « Bras droite et comme mal placée », avec capture d’une
ancienne version. Le même défaut est confirmé sur la fin de la V4 actuelle.
La racine droite(297,291) était àenviron20unités du contour du flanc, et le
long J vers la main389 créait trois traits parallèles et une attache flottante.
Le passage au ruban historique vers10,7s renforçait la mauvaise lecture.

Correction locale retenue après prototype : racines aux flancs, avant-bras
plus courts et mains finales remontées à366 ; droite(316,301), gauche(92,302).
Le constructeur arrondi reste actif dans la pose ventrale pour garder le même
dessin pendant la descente. Ajuster les deux côtés maintient la cohérence ;
aucun geste, dialogue, cadrage, temps ou son n’est ajouté. Cliché et mix
reproduits identiquement àlaV4.

Le critique indépendant examine36images consécutives9,75–11,208s et15poses,
ycompris10,708s et12,5s du vrai montage corrigé540×960. Il ne constate plus de
rupture au changement d’état ni de double trait flottant dans la pose finale.
Accord pour le final. Deux mains, yeux et pieds conservés ; pas de test public.
Preuves et portée : `../controle/critique_bras_v5.md`, `bras_v5_*.png/json`.
