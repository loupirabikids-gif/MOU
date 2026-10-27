# Jeu V5 — La dernière retouche

Référence : `../../../mou_rig.py` et `../../../references/MOU_reference.png`.
Le rig de base reste intact. Révision du pilote selon `chronologie.json` V5,
13 secondes à 24 i/s. Flash à l'image154 : 154/24 = 6,4166666667 s.

## Intention et chronologie

MOU est sûr de sa beauté. Il choisit sa pose, soulève ses joues puis pousse sa
retouche trop loin. Il reste satisfait jusqu'après l'affichage de la photo.
La gêne n'arrive qu'en découvrant le résultat, pas avant le clic.

- 0–34/24 s : le tap de mitaine est mis en scène dans `render.py`
  (`tap_geometry`, appui vers1,20s). `shutter_press` reste un paramètre réservé
  de la bibliothèque de poses ; ce module ne dessine aucun appareil.
- 34/24–82/24 s : moue puis sourire de vanité, menton relevé, regard objectif.
- 82/24–3,55 s : les deux mitaines gagnent leurs cibles de joue.
- 3,55 s : contact atteint. Le premier frottement à 3,583333 s est synchronisé.
- 3,583333–4,15 s : petit lift symétrique de 8 unités locales.
- 4,15–4,80 s : MOU approuve, avec ses deux mains toujours au contact.
- 4,80–6,15 s : il tire davantage ; la déformation devient asymétrique.
- 6,15–154/24 s : dernière traction linéaire encore en mouvement au clic.
  Les images153 et154 diffèrent ; le résultat n'est pas une pose ratée tenue
  en avance. Aucun air inquiet, langue, stupeur ou grimace volontaire.
- 154/24–8,80 s : satisfaction conservée ; même pose que la photo capturée.
- 8,80–9,70 s : les yeux descendent vers l'écran sous l'objectif, le sourire
  se fige puis l'intention change. Aucune découverte prématurée.
- 9,70–11,10 s : les mains descendent, la peau revient et le menton rentre.
- 11,10–13 s : une seule réaction gênée, bouche minuscule et regard bas.

## API et contact

`pose_at(t)`, `character_at(p, uid)`, `motion_at(t)`, `intention_at(t)` et
`deformation_at(p)` sont conservés. Le rendu du personnage et de sa photo
doivent tous deux employer `character_at(pose_at(154/24))` au déclenchement.
`motion_at` et `deformation_at` renvoient une affine identité : aucun aplatissement
magique du corps. Les pieds sont ceux du rig, sans levée ni translation.

Les paramètres nouveaux sont `arm_raise`, `cheek_contact`, `cheek_lift`,
`cheek_stretch`, `cheek_asym`, `chin_up`, `chin_tuck` et `shutter_press`.
Les positions sont exprimées dans le repère local400×500 du rig.

`contact_geometry(p)` renvoie :

- `left` / `right` : `shoulder`, `controls` (quatre points cubiques),
  `hand_center`, `hand_tip`, `cheek_target`, `contact_gap`, `in_contact`,
  `mitten_radius` (19).
- `skin_displacement` : vecteurs `left` et `right` communs aux mitaines,
  au contour de joue et aux coins de bouche.

Les cibles de base sont gauche(134,315), droite(272,315). Déplacements :

    dx gauche = -45 × stretch × contact
    dx droite = +45 × stretch × contact
    dy gauche = (-8 × lift + 34 × asym) × contact
    dy droite = (-8 × lift - 32 × asym) × contact

Au clic, les cibles sont donc gauche(89,341), droite(317,275). Le premier
lift reste symétrique ; seule la dernière retouche devient très excessive.
La paupière droite se comprime légèrement à l'extrême, avec les deux yeux et
leur découpe conservés. Les sourcils assurés évitent une lecture de peur.

## Raccords et contrôle avant intégration

Le nouveau contact a d'abord été fabriqué et examiné dans
`work/retouche_animation/`, avant de remplacer la source de production.
La première amplitude était trop jolie : la traction a été renforcée après
revue du coordinateur et du critique. Le ruban à offsets auto-croisés faisait
apparaître triangles/crochets à droite ; cette géométrie a été corrigée.

La version retenue utilise les mêmes arcs cubiques et largeurs que le rig,
construits par union visuelle de capsules SVG arrondies : toutes les encres,
puis toutes les peaux. Les recouvrements n'ajoutent plus de trait de poignet.
La base est masquée uniquement à l'intérieur du contour du torse, comme une
attache ouverte, sans bulle de rotule. Un seul groupe porte `data-part=hand`
par côté. Aucun doigt ni membre supplémentaire.

Planches examinées : `test_contact_ensemble.png`, `test_contact_proche.png`,
puis `test_contact_raccord_final.png` dans `work/retouche_animation/`.
Le coordinateur et le critique ont levé la réserve de raccord pour l'animatique.
La preuve retenue et l’audit312poses sont archivés dans
`../controle/contact_joues_v4.png` et `../controle/audit_contacts_v4.json`.
La critique du montage complet est distincte : `../controle/critique_v4.md`.


## Correction graphique V5 — réaction finale

Le retour utilisateur sur le bras à droite de l’image a révélé un défaut
également présent dans la V4 : racine trop à l’intérieur du torse et long J
parallèle au ventre. La pose ventrale est corrigée des deux côtés pour rester
cohérente, sans ajouter de geste ni modifier le scénario.

Contrôles cubiques à `arm_clasp=1` :

- Gauche : `(92,302), (73,333), (125,356), (174,366)`.
- Droite : `(316,301), (335,336), (285,360), (230,366)`.

Les deux mains sont plus hautes dans la pose finale. Le constructeur arrondi
reste actif quand `arm_raise>0` OU `arm_clasp>0`, ycompris après10,7s ; aucun
retour soudain au long ruban original. Les yeux, les pieds, la pose capturée
et le mix restent ceux de la V4. Le critique a revu la descente et le
rapprochement dans le vrai montage encodé : `../controle/critique_bras_v5.md`.
