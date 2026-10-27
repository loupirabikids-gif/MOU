# Jeu de MOU — Le retardateur, révision du jeu

Source commune : `../../../mou_rig.py` et `../../../references/MOU_reference.png`.
Le rig original reste intact : même corps asymétrique, double bosse, deux yeux,
deux bras continus avec deux moufles et deux pieds sombres. `character_at()`
porte les déformations de jeu et la bouche ; le plan, le viseur et la photo
emploient tous cette fonction.

- 0–0,82 s : MOU est déjà certain de sa beauté, mains fièrement aux hanches,
  buste redressé, menton haut, regard vers son aperçu et petite moue narcissique.
- 0,82–1,78 s : grand sourire en coin, sourcil droit conquérant ; clin d'œil
  unilatéral de 1,58 à 1,66 s. Il se contemple, sans attendre un compliment.
- 1,78–5,25 s : maintien de la pose très assurée. Après 4 s, le sourire se
  crispe et les yeux s'ouvrent davantage ; le buste reste gonflé.
- 5,25–5,40 s : rupture visible, les bras tombent ; étirement bref du corps
  jusqu'à 118 % de hauteur avant l'affaissement.
- 5,40–6,15 s : squash à 65 %, petit rebond à 84 %, puis affaissement stable
  à 68 % avec élargissement à 112 % et inclinaison asymétrique. Les bras
  ballottent sans se détacher. Bouche grande, molle et pendante de travers,
  langue basse et un seul œil ouvert : l'accident doit contraster avec la frime.
- 6,15–6,50 s : grimace et déformation stables. `pose_at(155/24)` est exactement
  identique à `pose_at(6.5)` ; la photo utilise cette même source de rendu.
- 6,50–6,625 s : redressement surpris sous le flash. Après 6,625 s, les
  fragments du personnage sont strictement identiques à la première version.
- 9,50–10,62 s : regard photo, mains devant le ventre et sourcils de gêne,
  relevés vers l'intérieur, sans V de colère.
- 11,00–14,00 s : regard spectateur, sourire forcé, bref retour à la photo,
  puis réaction finale tenue. Cette dernière réaction n'est pas modifiée.

## Déformation et contacts

`pose_at(t)` fournit `warp_sx`, `warp_sy` et `warp_skew`. `deformation_at(p)`
renvoie ces valeurs sous les clés `sx`, `sy`, `skew`, avec `anchor_x=200`
et `anchor_y=437`. Limites : sx 0,94–1,12 ; sy 0,65–1,18 ; skew −0,07–0,005.

`character_at()` laisse `foot-l` et `foot-r` hors du groupe `body-warp`.
Ce groupe contient ensemble le corps, les deux bras, les deux mains et le
visage. Transformation :

    x' = 200 + sx * (x - 200) + skew * (y - 437)
    y' = 437 + sy * (y - 437)

Les pieds restent fixes, les raccords suivent le corps. Aucun groupe affine
n'est émis à l'identité, ce qui préserve les fragments de la réaction finale.
`motion_at()` reste à l'identité : la photo ne perd donc aucune déformation.

À l'ouverture d'œil inférieure à 0,30, une fermeture franche en arc remplace
l'intermédiaire creux du rig. Aucun ovale vert vide ne doit apparaître.

## Contrôles propres au module

336 poses : XML lisible, valeurs finies, exactement deux formes de main,
identifiants uniques ; pieds frères du groupe affine, bras et visage inclus.
Photo stable avant le clic, et fragments après 6,625 s strictement identiques
à la version précédente. À la position x=670 et échelle 2,35, les contours
des bras avec réserve de 7 pixels restent entre environ x=298 et x=1067,
ce qui évite le téléphone (bord x=290) et la coupe au bord droit.

Planches de travail : `work/animation_v2/vanite_effondrement.png` et
`work/animation_v2/scenes.png` ; fichiers SVG des poses conservés au même endroit.
