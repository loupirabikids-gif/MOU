# Jeu de MOU — Le retardateur

Source commune : `../../../mou_rig.py` et `../../../references/MOU_reference.png`.
La silhouette, les attaches, les deux bras et moufles, les yeux et les pieds
ne sont pas redessinés. `animation.py` expose les poses et une variante de
la même bouche : `character_at()` doit servir au plan et à la photo figée.

- 0–1,25 s : le regard bas-gauche vise le téléphone ; les bras finissent de
  prendre appui aux hanches et le sourire se prépare.
- 1,25–5,25 s : tenir la frime ; après 4 s, sourire plus ouvert et yeux plus
  tendus. Pas de mouvement mécanique sur chaque bip.
- 5,25–6,15 s : détente des mains, yeux fermés pour le souffle, puis grimace
  asymétrique : un œil plissé, l'autre ouvert, bouche étirée de travers.
- 6,15–6,50 s : même grimace stable. La capture à 6,50 s partage exactement
  les paramètres et le rendu du personnage animé.
- 6,50–6,625 s : yeux et sourcils se lèvent sous le flash, puis regard vers la photo.
  Les ouvertures inférieures à 0,30 utilisent un trait de paupière franc, pour
  éviter les ovales verts vides de la transition morphologique du rig.
- 9,50–10,62 s : les mains se rapprochent devant le ventre ; sourcils relevés
  à l'intérieur, sans V de colère ; petit sourire pour sauver les apparences.
- 11,00–14,00 s : regard spectateur, sourire forcé, bref retour à la photo,
  puis réaction finale tenue. Deux clignements ponctuels, aucune voix.

`motion_at()` conserve un ancrage fixe : aucune marche, aucun pied levé,
aucune translation du personnage. Le recadrage est géré par le plan.

Contrôle propre au module : 336 poses à 24 i/s analysées ; XML lisible,
exactement deux formes de main, identifiants uniques dans chaque fragment,
valeurs finies et levées de pieds nulles. Planche de travail à
`work/animation/poses.png` : douze instants, de 0 à 13,5 s.
