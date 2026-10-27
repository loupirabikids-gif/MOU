# Jeu de MOU — Le retardateur, révision 3

Source commune : `../../../mou_rig.py` et `../../../references/MOU_reference.png`.
Révision locale du pilote après critique du découpage ; les profils d'équipe
ont été lus comme consignes de rôle, sans prétendre à leur activation native.
Le rig original reste intact. `character_at()` porte les déformations et la
bouche ; le plan, le viseur et la photo emploient tous cette fonction.

## Intention et chronologie verrouillée

- 0–4,20 s : auto-admiration V2 conservée : regard aperçu, moue, menton haut,
  sourire en coin et seul clin d'œil à 1,58–1,66 s ; hanches fières.
- 4,20–5,75 s : le sourire se crispe progressivement, les yeux s'ouvrent
  davantage ; il lutte pour garder son beau visage. Aucun mouvement ajouté
  sur les signaux, pas de grotesque complet à ce stade.
- 5,75–6,00 s : souffle et détente initiale des mains, visage encore modéré.
- 6,00–149/24 s (6,208333 s) : courte anticipation verticale. Les bras
  descendent, sans grande bouche tordue ni aplatissement déjà offert au public.
- Images 149–155 : UNE chute accélérée quadratique, sans rebond. Le premier
  extrême est atteint exactement à l'image155 (6,458333 s) : corps à 68 %
  de hauteur et 112 % de largeur, bouche molle oblique, langue pendante,
  paupières dépareillées. L'ancien dépassement à 65 % est supprimé, car un
  retour à 68 % avant le clic créerait le rebond expressément rejeté.
- Image156 (6,50 s) : même pose et même déformation que155, sans différence
  numérique ; photo figée via cette même source.
- 6,50–6,625 s : redressement surpris sous le flash, puis découverte du clic.
- 9,50–10,40 s : MOU regarde la photo, déçu. Regard bas-gauche et bouche
  descendante, plutôt qu'une réaction immédiatement souriante.
- 10,40–11,40 s : il croise notre regard et tente de sauver les apparences :
  menton relevé, sourcil conquérant et vrai sourire de frime qui revient.
- 11,40–11,90 s : brève façade ; les mains commencent à rejoindre le ventre.
- 11,90–12,25 s : regard irrépressible vers la photo, qui défait sa prétention.
- 12,25–12,75 s : le menton retombe et le sourire se casse.
- 12,75–14,00 s : vraie gêne, mains devant le ventre ; bouche presque plate,
  coin minuscule, regard bas, aucun sourire en U ni nouveau clin d'œil.
  Pas d'éclat final, pas de mouvement destiné à remplir la dernière tenue.

## Déformation, pieds et raccords

`pose_at(t)` fournit `warp_sx`, `warp_sy`, `warp_skew`, ainsi que les paramètres
continus de visage et de bras. `deformation_at(p)` renvoie `sx`, `sy`, `skew`,
`anchor_x=200` et `anchor_y=437`. Limites V3 : sx 0,97–1,12 ; sy 0,68–1,15 ;
skew −0,07–0,008. `motion_at()` reste à l'identité.

`character_at()` laisse `foot-l` et `foot-r` hors du groupe `body-warp`.
Ce groupe transforme ensemble corps, deux bras/mains et visage :

    x' = 200 + sx * (x - 200) + skew * (y - 437)
    y' = 437 + sy * (y - 437)

Aucun glissement de pieds, aucune marche ni prise d'objet. Les ouvertures
inférieures à 0,30 terminent l'œil en arc franc pour éviter l'ovale vert creux.
La langue reste découpée par la bouche jusqu'au dernier stade de déformation ;
elle ne se dévoile pendante qu'à la chute aboutie, sans ellipse transparente
flottant sur la peau pendant l'anticipation.

## Contrôles exécutés

336 poses : XML lisible, valeurs finies, exactement deux formes de main,
identifiants uniques ; pieds frères du groupe affine, bras et visage inclus.
`pose_at(155/24) == pose_at(6.5)` strictement. Hauteur monotone pendant les
six intervalles de chute : 1,15 ; 1,13694 ; 1,09778 ; 1,0325 ; 0,94111 ;
0,82361 ; 0,68. Aucun état complet de capture avant l'image155.

Planche examinée : `work/animation_v3/poses_v3.png` (16 instants).
Elle vérifie les intentions et la forme ; elle ne remplace pas la critique
du montage complet, ni une écoute ou un test auprès d'un public.
