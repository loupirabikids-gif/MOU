# Jeu de la nouvelle réalisation — Le retardateur

Source de vérité : `../chronologie.json` (13 s, 24 i/s, flash image144 à6s).
Identité : `../../../mou_rig.py`, inchangé, et référence MOU vert citron àdeux
yeux. Aucune pose main-joue ni longue pose mains devant ventre de l’ancienne
réécriture. Il s’agit du gag initial : la prise surprend le relâchement.

## Intentions et temps

- 0–1s : personnage hors champ pendant activation du téléphone.
- 1–1,7s : moue de séduction puis beau sourire, menton et torse relevés,
  deux mains aux hanches. Regard vers l’objectif.
- 2,15–2,35s : seul clin d’œil volontaire de vanité ; le rendu place son éclat
  de satisfaction à2,20s. Retour àla pose fière jusqu’au1 à5s.
- 5–5,75s : son regard décroche de l’objectif vers le bas/droite, ses bras
  quittent les hanches et il souffle, persuadé que la prise est terminée.
- 5,75–6s : une seule chute accélérée, sans rebond. L’extrême n’arrive
  qu’àl’image144, exactement au flash : bouche déviée, langue molle unique,
  paupières dépareillées et corps aplati. La même affine porte visage et bras.
- 6–6,125s : pose capturée tenue sous le flash. Aucun autre clin d’œil de jeu.
- 6,125–6,5s : retour surpris, yeux grands ouverts et petite bouche en O
  (l’ancien U pouvait lire un sourire heureux, il a été corrigé avant intégration).
- 6,75–8,75s : le montage montre la photo immobile. La pose live reste surprise
  hors champ, mais le cliché conserve strictement `pose_at(6)`.
- 8,75–10s : les yeux visent le résultat sous l’objectif, expression déçue.
- 10–11s : bouche retenue et assurance qui tombe ; deux bras baissés courts.
- 11–13s : une seule réaction gênée, sans nouvelle tentative ni clasp ventral.

## Construction et APIs

APIs conservées : `pose_at`, `character_at`, `motion_at`, `deformation_at`,
`intention_at`. `motion_at` reste identité. Les paramètres affines sont
`warp_sx`, `warp_sy`, `warp_skew`, ancrés en(200,437). Le groupe `body-warp`
contient corps, bras et visage ; les pieds sont ses frères,
jamais ses descendants. Les pieds gardent strictement la géométrie du rig.

La pose fière monte à1,13 en hauteur. La capture descend à0,68 avec largeur1,12
et cisaillement−0,07. De138à144, les hauteurs diminuent sans rebond :
1,12 ;1,10778 ;1,07111 ;1,01 ;0,92444 ;0,81444 ;0,68.

Les bras sont exactement ceux renvoyés par `mou_rig.character_fragment` et
`mou_rig._arm`. Aucun adaptateur de forme ni masque de racine n’est appliqué.
Les paramètres de pose `arm_hips` et `arm_clasp` restent ceux du montage
précédent ; les transformations corporelles communes restent inchangées.
La demande de l’utilisatrice prévaut sur les adaptations proposées par
la critique interne. Les helpers `arm_controls` et `episode_arm` ont été supprimés.

## Contrôle avant intégration

Planches dans `work/reprise_animation/bras_sobres.png` et `jeu_prototype.png`.
La construction des bras a été examinée par coordinateur et critique avant
publication de ces sources. La bouche surprise en O corrige le sourire U
observé dans le premier prototype. La critique du montage complet reste distincte.

312 poses auditées : XML/IDs/masques valides, deux mains, pieds identiques,
aucun clasp, valeurs finies, extrême144 et chute monotone. Empreinte du rig :
`7f04a1424831db9a83956bf175579000269b9af6a2582fa5d0147e81e76a423e`.
Rapport préparatoire : `work/reprise_animation/audit_prototype.json`.

## Correction retenue après le premier montage — gêne finale

La critique du vrai MP4 a relevé que11–13s pouvait lire une fin apaisée :
petit U et regard revenu face àl’objectif. Seuls `ASHAMED`, `ADMITTED` et la
forme `shy` de bouche ont été corrigés : bouche presque plate àcoin tombant,
regard franchement bas/gauche qui évite l’objectif, sourcils plus retenus.
Aucun nouveau geste ni changement des bras, proportions ou durées.

La planche avant/après est `work/reprise_animation/gene_corrigee.png`.
237images plus9,85s comparées aux sources précédentes : poses et SVG sont
strictement identiques jusqu’à9,85s, ycompris la capture à6s. La correction
commence dans la transition de9,85s vers la gêne ; le montage doit la revérifier.
Rapport de cette restriction de portée : `work/reprise_animation/audit_gene.json`.


## Rétablissement demandé des bras d’origine

Révision2 : seul le dessin des bras est rétabli àpartir du rig original.
Les312poses, les bouches et l’affine corporelle sont identiques à302c870.
Après retrait des groupes de bras, tout le personnage reste identique.
Le cadrage de la photo est fixé aux valeurs précédentes pour éviter que
le retour des bras ne déplace ou ne redimensionne le reste du cliché.
Voir `../controle/audit_restauration_bras.json` et `restauration_bras.md`.
