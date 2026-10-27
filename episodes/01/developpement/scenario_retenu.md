# La dernière retouche — scénario retenu pour la révision 4

## Statut et origine du choix

Réécriture du pilote 01, approuvée par l’utilisatrice : « Vas y avec la deuxième ».
Après la V3, elle a signalé que le gag restait peu clair. Le coordinateur et les
agents ont réexaminé le mécanisme : l’aperçu de MOU sur l’écran avant le clic,
le délai irrégulier après « 1 » et plusieurs réactions finales pouvaient brouiller
la cause du ratage. Ce diagnostic a été établi à partir du découpage et des
retours, sans nouveau visionnage de V3 lors de cette discussion.

La deuxième proposition retenue change la cause de l’accident : MOU ne se relâche
plus après avoir cru la photo prise ; il rate sa photo parce qu’il cherche à
embellir encore une pose qu’il trouve déjà magnifique. Le scénario V3 est conservé
dans `scenario_v3.md`, avec ses autres documents et critiques historiques.

La veille externe récente reste incomplète, avec son blocage consigné dans
`../../../editorial/veille_2026-10-27.md`. Cette correction du pilote s’appuie sur
le caractère de MOU, le retour de l’utilisatrice et la critique interne. Elle
n’est pas présentée comme validée par des Shorts observés ou par des statistiques.

## Petite histoire

**Désir.** MOU veut une photo à la hauteur de sa beauté, dont il est déjà certain.
Il lance le retardateur, relève le menton et offre un sourire fier à l’objectif.

**Tentative.** Pendant le compte à rebours, ses deux mitaines soulèvent doucement
ses joues : un petit sourire rendu encore meilleur. Il approuve cette retouche,
puis décide d’en ajouter davantage. Ses mains restent au contact du visage.

**Renversement.** Sa dernière traction devient trop forte et asymétrique. Il reste
satisfait et continue de tirer au moment du flash. La photo conserve exactement
ce visage déformé, mains aux joues. L’excès résulte visiblement de ses gestes.

**Réaction révélatrice.** Il découvre enfin ce résultat. Son sourire se fige,
les mains descendent lentement et son visage revient. Menton rentré, bouche
minuscule et regard bas : une seule gêne, sans nouvelle tentative ni deuxième gag.

Aucun dialogue ni texte explicatif nécessaire. Les chiffres, les signes de caméra,
le clic et la photo décrivent une prise de vue ordinaire. Un seul téléphone et
une seule capture. Aucun portrait sur l’écran avant le clic.

## Référence et choix de jeu

Conserver le MOU vert citron de `references/MOU_reference.png` et le rig articulé
`mou_rig.py` : petite double bosse, deux yeux, deux bras avec une mitaine chacun,
deux petits pieds sombres. Le corps, les joues et le sourire suivent la traction ;
aucune troisième main, nouveau doigt, tête détachée, nez ou costume. Les pieds
restent au sol. MOU reste de face : le choix de sa pose passe par le menton,
le regard et les sourcils, sans nouveau profil ni retournement.

La première retouche est petite et symétrique. Le dernier ajout devient exagéré
sans inquiétude de MOU avant qu’il voie la photo. Un éventuel infime hochement
signifie son approbation, pas un doute. Le public peut voir l’excès avant lui ;
MOU ne doit pas jouer une grimace volontaire pour amuser l’appareil.

## Durée et fabrication

13 secondes, 24 images/s, 1080 × 1920. Chronologie commune verrouillée dans
`../chronologie.json` : compte 5–4–3–2–1 aux images 34/58/82/106/130, clic à
l’image154 (6,416667 s). La traction est encore en cours lors de cette image.
Photo fixe de 7 à 8,8 s ; mains qui descendent de 9,7 à 11,1 s ; gêne jusqu’à 13 s.
Les chiffres sont espacés d’une seconde, sans attente supplémentaire après « 1 ».

Le découpage détaillé et les sons sont dans `decoupage_v4.md` et `storyboard_v4.json`.
La fabrication conserve Python, SVG, CairoSVG, Pillow, NumPy et FFmpeg, gratuits
et open source. Sept sons courts originaux, sans voix ni musique, avec un vrai
silence avant le clic et pendant la lecture de la photo.

## Forces, faiblesse et passage à l’essai

La vanité provoque directement le ratage : désir, geste et conséquence appartiennent
à la même action. La photo révèle à MOU ce que son assurance l’empêchait de juger.
La réaction unique laisse lire cette découverte sans ajouter de nouvelle intrigue.

La faiblesse principale est le nouveau contact des mains sur les joues : s’il
paraît détaché, masque les yeux ou ressemble à une grimace volontaire, la causalité
s’affaiblit. Tester les contacts mitaine–bouton et mitaines–joues avant intégration,
puis examiner une animatique complète muette. La photo doit partager le même état
de modèle que l’image154, puis rester immobile et lisible au format mobile.

La critique conceptuelle est favorable sous ces réserves (`critique_scenario_v4.md`).
Ce document ne vaut ni validation d’un rendu V4, ni écoute réelle, ni test de public.
