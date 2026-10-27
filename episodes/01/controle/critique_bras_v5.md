# Correction du placement des bras — revue V5

## Demande et portée

Le 27 octobre2026, l’utilisatrice signale le bras à droite de l’image comme
mal placé et joint une capture du montage précédent (téléphone à gauche,
ancien titre « Le retardateur »). La vérification porte aussi sur la V4
actuelle « La dernière retouche », commit311bd18 : son dernier geste reprend
les bras repliés du rig original, donc le placement signalé peut y subsister.

Examen effectué sur des extractions du vrai MP4 V4 aux instants10,2/10,5/11,1/
12,5s, en plan complet et en recadrage du bras droit, puis comparaison avec
`references/MOU_reference.png`. Aucun fichier de production modifié par le critique.

## Défaut confirmé sur le rendu V4

| Passage | Observation | Effet probable et correction concrète |
| --- | --- | --- |
| 11,1–13s | Le bras droit forme un long J qui suit le contour du ventre. Deux traits de bras commencent à l’intérieur du torse, à côté du contour extérieur du corps. | L’attache semble flotter dans la peau et l’avant-bras ressemble à une bande du ventre. Ramener la racine vers le flanc, raccourcir le retour du coude et remonter légèrement la main. |
| 10,2–11,1s | La main passe près de l’attache pendant la descente ; la silhouette se transforme ensuite en la longue courbe du geste final. | Examiner cette transition densément après correction, afin d’éviter un saut de construction entre capsules et ruban. Ce contrôle reste nécessaire même si la pose finale est correcte. |

La cause géométrique concorde avec l’observation : la racine du bras droit
replié est(297,291), alors que le contour du corps à cette hauteur vaut
environ(316,74,291), soit19,74unités d’écart. À gauche, l’écart correspondant
n’est que8,38unités. Les deux racines ont la même hauteur291 ; le problème
principal est le retrait horizontal et la longue courbe vers la main ày389,
plutôt qu’une épaule simplement située plus bas que l’autre.

Deux mains présentes et un XML valide ne valident donc pas ce placement.
Preuves préparatoires : `work/diagnostic_bras/ensemble_v4_avant.png` et
`bras_droit_v4_avant.png` (extractions encodées, hors archive tant que non promues).

## Avis sur le prototype proposé par le coordinateur

Planche examinée : `work/bras_v5/comparaison_essai.png`, quatre instants, V4 en
haut et essai en bas. La version de production reste V4 au moment de cet avis.

Les nouveaux contrôles des bras repliés sont :

- gauche : (92,302), (73,333), (125,356), (174,366) ;
- droite : (316,301), (335,336), (285,360), (230,366).

**Avis favorable pour intégrer cet essai au montage léger.** À11,1/12,5s, les
attaches se lisent sur les flancs, les avant-bras sont plus courts et les mains
remontées. Le long J et les deux traits intérieurs flottants à droite ne sont
plus visibles. Deux mitaines restent distinctes ; visage et pieds demeurent
libres. Corriger les deux côtés est cohérent pour le geste final, sans changer
l’intention de gêne ni le mécanisme du gag.

Condition avant validation finale : revoir10,2→11,1s dans un encodé corrigé,
avec une extraction dense, afin de vérifier la continuité de la descente et
l’absence de saut lors du changement de construction du bras. Le maintien du
constructeur arrondi quand `arm_clasp>0` doit être jugé sur ces images, pas
validé seulement à la lecture du code. Aucun changement du scénario ou du son
n’est demandé par cet examen.

## Vérification du montage V5 corrigé — réserve levée

Le coordinateur intègre le prototype, verrouille les sources et fournit le
montage léger réellement encodé540×960,13s. La revue porte sur ce MP4, pas sur
la planche d’essai :

- 36images consécutives234→269, soit9,75→11,2083s, examinées en recadrage du bras droit ;
- 15poses complètes incluant l’image257(10,7083s), autour de l’ancienne commutation,
  puis la tenue finale à12,5s ;
- comparaison V4/V5 aux quatre passages initialement examinés.

**Réserve levée ; accord pour le rendu final de cette correction.** Les mains
descendent puis se rapprochent devant le ventre sans rupture observée autour
de10,7s. Le bras droit reste continu, avec une seule mitaine. Le long J et les
traits qui partaient à l’intérieur du torse ont disparu de la pose tenue.
Les mains finales sont plus hautes que dans la V4 ; aucun nouveau geste de
remontée n’est ajouté. Les deux yeux, la bouche et les pieds restent dégagés.
Aucune autre correction du scénario, du son ou du jeu n’est demandée.

Preuves archivées dans ce dossier : `bras_v5_transition.png`,
`bras_v5_droite_dense.png`, `bras_v5_comparaison.png` et `bras_v5_revue.json`.
Ce dernier relève l’empreinte du MP4 léger examiné et les numéros des images.
La portée est une inspection d’extractions chronométrées et consécutives,
sans écoute audio ni test public. La fidélité de l’export1080×1920 est à vérifier
séparément par le coordinateur lors des contrôles finaux.
