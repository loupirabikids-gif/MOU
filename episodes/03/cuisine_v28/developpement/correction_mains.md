# Correction locale de la présentation des mains — V28

30 octobre 2026. Le correctif porte uniquement sur les deux petits gestes de
présentation après 33,25 s. Le dessin canonique des deux bras et des deux
moufles, le costume, les cadrages et la durée sont conservés. Aucun contour
de paume, doigt ou articulation supplémentaire n'a été créé.

## Trois essais réellement rendus

La planche privée `work/pose_mains_v28/trois_candidats.png` a été produite par
le renderer SVG/CairoSVG du projet puis ouverte. Chaque candidat utilise les
mêmes contrôles natifs, avec des cibles calculées à partir de leurs prises :

| Candidat | Contrôles de départ | Lecture de la pose rendue |
| --- | --- | --- |
| A — proche | hips 0,7 ; clasp 0,45 ; pivots −15° / +10° | Les extrémités restent rondes et sous la bouche ; présentation plus resserrée et asymétrique. |
| **B — retenu** | **hips 0,7 ; clasp 0,25 ; pivots −8° / +8°** | **Les deux moufles sont bien séparées, sous la bouche et devant le torse. La relation courte entre bras et extrémité reste lisible.** |
| C — bas | hips 0,4 ; clasp 0,6 ; pivots −8° / +8° | Attitude très proche du repos, plus basse et plus serrée ; moins de contraste pour présenter les mains. |

Le choix B corrige la cause relevée par la critique : les grandes cibles
latérales à hauteur des yeux ne sont plus utilisées. Il ne cherche pas à
faire lire une main humaine par ajout de doigts. La lecture de « mains propres »
reste liée au séchage précédent et au regard de MOU, puis au repas raté.

## Mise en place

`FINAL_HAND_TARGETS` calcule les deux cibles à partir de `world_grip`, avec
les paramètres natifs ci-dessus et le transform de référence `(80,380,2.3)` :

- gauche : environ `(424,66 ; 1218,88)` ;
- droite : environ `(658,82 ; 1218,93)`.

Les instants restent ceux du découpage : première main de 33,50 à 34 s,
puis seconde de 34,25 à 34,70 s. Les petits arcs autour des épaules remplacent
les grandes montées latérales. Les regards existants utilisent `state.hands`
et suivent donc les nouvelles positions sans modification de leur contrôleur.
Le sourire et le retour au public restent ceux de la fin choisie.

Seul `sources/animation.py` a été modifié pour ce correctif. Ni
`performance.py` ni `jeu_visage.py` n'ont été édités par cet agent. Le
coordinateur traite séparément les ajustements locaux du visage liés au son.

## Contrôles préparatoires effectués

Le script privé `work/pose_mains_v28/verify_and_render.py` a évalué les
912 états et comparé les **798 états physiques avant 33,25 s** à la source
V27 : transform de l'acteur, mains, métadonnées et SVG des bras, accessoires,
matrice, pieds, stock, vols et contenu du panier sont strictement identiques.
Cette comparaison physique n'affirme pas l'identité des visages que le
coordinateur corrige séparément dans deux fenêtres autorisées.

Erreur maximale de prise sur les 912 états : **0,02673 px**. Les rotations
natives des bras dans la fin ne dépassent plus **8°**. Les prises restent
entre 1212 et 1278 px en hauteur monde, sous la bouche. Les deux moufles
restent des fragments natifs continus ; aucune main n'est ajoutée.
Les dix-huit derniers états du corps, des bras, des pieds, du visage et des
mains sont identiques. La vapeur peut continuer indépendamment.

La séquence de six poses fraîches `work/pose_mains_v28/sequence_corrigee.png`
a été ouverte. L'avant/après `avant_apres_pose.png` distingue explicitement
l'image décodée du MP4 V27 de la nouvelle pose rendue par CairoSVG.
Ces contrôles ne remplacent pas la critique des images du prochain MP4,
la lecture continue, une écoute ou l'appréciation de l'utilisatrice.

Source gelée, SHA256 de `animation.py` :
`f7761df3488324b38d52cea09d7ce9bd6510cc827595f728b2f98b544050c9d2`.
