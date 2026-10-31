# Gestes de cuisine adaptés au galet

31 octobre 2026. Producteur indépendant `sources/cooking_actions.py`, destiné
au nouveau galet. Aucun ancien rig MOU ni contour de bras employé. Les deux
moufles gardent leur dessin, leur taille1,2 et leur pouce arrondi ; leur position,
rotation et fermeture sont indépendantes.

Repos commun retenu après inspection du contexte : gauche(270,1170),
droite(925,1040), au-dessus du rouleau. La position initiale droite(800,1160)
touchait le flanc ; une position latérale à875,1160 aurait recouvert le rouleau.
La gauche à310,1170 touchait encore le ventre par son pouce ; le dernier
écart vers270,1170 restitue un espace négatif entre moufle et silhouette.
Tous les contacts de travail restent aux mêmes coordonnées.

## Interface

`state_at(t)` couvre0–38s et retourne `hands`, `spoon`, `spoon_held`, `carrot`,
`tomato`, `tomato_added`, `tomato_held`, `tomato_in_front`, `salt`, `gaze_target`,
`emotion_hint`, `cooking_phase` et `cooking_contacts`. Le coordinateur remplace
les mains dans les lavages, le papier et la fin. Les accessoires posés persistent.

Les manches passent par `character.point(main,'grip')` ; la prise de tomate et
la pincée de sel utilisent le vrai contour du pouce. Le soutien de carotte se
fait avec le vrai point `tip`. Les trajets de travail restent sous le visage.

## Remuage et pose de cuillère

0–2,35s : le bol de la cuillère suit une petite orbite dans la poêle, et la
paume tient son manche.2,35–2,70s : objet et moufle vont ensemble à la pose
existante, grip(468,1275), bol(337,1308). La main se retire après2,70s et
s'expose à l'inspection. La cuillère posée ne disparaît pas.

## Carotte

La droite pose les bouts sur le dessus de la moitié feuillue, à(747,1340),
loin des deux coupes. La gauche tient le manche. La lame est placée par le
vrai ventre de son dessin, `art.knife_edge_point`, et non par la pointe.

- Première coupe à9,40s, ventre de lame(655,1360), tenue jusqu'à9,46s.
- Seconde coupe à9,98s, ventre de lame(675,1360), tenue jusqu'à10,035s.
- Lame relevée, puis posée à10,40s. Les mains ne se retirent qu'après.

Les rondelles et le reste de la carotte persistent après les coupes ; les
paramètres de glissement des rondelles restent ceux du dessin existant.

## Tomate et sel

La tomate démarre à(530,1268), position de contenu de sa coupelle dans
`art.tomato_dish_svg`. La référence(530,1237) aurait laissé un vide au-dessus
du plat. Prise à15,12s, lâcher à15,38s, contact poêle à15,58s. À ce contact,
le morceau de cuisson reprend position et échelle exactes de la fin du vol.

Le sel est pincé sur la surface du bol, puis soulevé au-dessus de la poêle.
Les onze émissions20,10–20,60s mémorisent la position réelle du pouce à leur
naissance ; les grains déjà lâchés ne suivent plus la main. Un petit reste
blanc accompagne la main jusqu'au lavage. Entre21,65 et22,45s, l'approche de
la cuillère reste suspendue avant une vraie prise, puis la main renonce.

Ces choix sont des producteurs de poses et contacts. Ils ne remplacent pas
la critique des images encodées et ne constituent pas une validation artistique.

## Vérification de préparation

Six poses de travail puis six poses dans le décor existant ont été rendues et
ouvertes. Preuves privées : `work/galet_cooking_actions/actions_sheet.png` et
`contexte_actions_sheet.png`. Les mains actives restent sous le visage ; le
repos droit retenu reste au-dessus du rouleau. Ces planches ne remplacent pas
la future revue du vrai MP4 avec caméra et jeu corporel du coordinateur.

Sur912 états à24 images/s, écarts de prise calculés : cuillère0px, couteau0px,
soutien carotte0px et tomate inférieur à6e-14px. Les deux ventres de lame
coïncident avec les points de coupe aux instants définis. Dix-huit frontières
internes des gestes sont continues àmoins de0,01px ; les boîtes conservatrices
de moufles ne croisent pas les boîtes des yeux sur ces seules actions de travail.
Ce dernier contrôle est une borne spatiale en pose neutre, pas une preuve de
masquage exact du montage final ni de compréhension par le public.

Après le dernier écart du repos gauche à270,1170, les912 prises et les dix-huit
frontières ont été revérifiées : mêmes contacts et continuité conservée. Aucune
autre reprise. Source gelée :
`10a3ee3c45044e5803b5330d7a1d39918e34dca956bcb3484b39afbba225604c`.
