# Jeu MOU — coffre V2

Le jeu suit le découpage caméra en treize plans. MOU essaie de travailler,
renonce, attend le coffre et retrouve immédiatement son plaisir au téléphone.
Ce plaisir vient de l'objet : aucune honte ni adresse au public dans le final.

## Couche de production

`sources/jeu_mou.py` expose `apply_mou_acting(t, actor)` et renvoie une copie
indépendante. La scène l'applique après l'attente, les bras et les expressions,
avant la projection caméra et l'attache du téléphone. Le dessin original, ses
deux bras, ses deux mains et ses pieds ne changent pas. Les gestes de dépôt,
fermeture, bouton, crayon et récupération restent ceux du montage précédent.

| Temps | Intention et modification |
| --- | --- |
| 4,60–5,30 s | La certitude satisfaite est tenue, puis retourne doucement au travail jusqu'à 5,75 s. |
| 9,50–10,30 s | Le découragement continue malgré la frontière de pose à 10,00 s ; aucun retour de sourire. |
| 12,00–12,86 s | Le visage impatient devient lassé avec l'appui de joue, sans sourire parasite au changement de plan à 12,25 s. |
| 12,30–12,76 s | Le regard finit son trajet vers le coffre ; la joue reste appuyée. |
| 12,76–15,20 s | Regard tenu, sans repartir à chaque chiffre du montage temporel ; un clignement supplémentaire à 14,24–14,46 s. Les yeux se ferment aussi dans les événements déjà présents. |
| 24,35–24,70 s | Le visage de récupération devient un petit sourire ; suppression de la bouche ronde imposée par l'ancien gros plan. |
| 24,70–25,04 s | MOU reste assis. La main libre retrouve progressivement l'autre bord du téléphone ; mêmes contrôles de prise. Le téléphone et les deux paumes descendent sur une enveloppe continue, jusqu'à 85 px de décalage monde, pour séparer l'avant-bras du sourire. Les coudes accompagnent. Léger relâchement du corps de trois pixels maximum, sans saut. |
| 25,15–25,75 s | Les deux mains et le téléphone redescendent ensemble vers la position de lecture finale. Les coudes suivent. Le regard accompagne l'objet. |
| 25,75–30,00 s | Position stable, grands yeux dirigés vers le téléphone, sourire fermé. Le recul caméra révèle la feuille vide sans nouvelle gesticulation. |

Les anciennes translations verticales de plusieurs centaines de pixels, le
maintien en l'air et le changement brutal des mains à 26,65 s sont supprimés.
Le label interne `whole_body_joy` reste sur toute la fin uniquement pour conserver
la contrainte de tangente de moufle déjà validée dans le renderer natif. Aucun
saut n'est associé à ce label dans la nouvelle couche. L'intention explicite
`acting_intent=content_phone_series` décrit le jeu réellement produit. Garder
cette construction de contour continue évite un petit changement de tangente
à 25,15 s après l'abaissement du téléphone.

## Contrôles

`work/jeu/check_jeu.py` vérifie 720 poses : entrée non modifiée, actions hors
périmètre identiques, absence de saut, liaison bilatérale du téléphone,
continuité des contrôles et pose stable à partir de 25,75 s. Le rapport est
`work/jeu/verification_jeu.json`.

`work/jeu/poses_composition_v2.png` montre les vraies compositions avant et après
la seconde prise, le changement de plan et l'ancien point de rupture à 26,65 s.
Les contrôles de contact dans les coordonnées du monde ne suffisent pas seuls :
la scène projette également le même décalage du coffre sur les deux paumes
pendant le gros plan. Les images composées sont inspectées pour le raccord réel
des moufles, le regard et la lisibilité du sourire. Cette vérification de jeu ne
conclut rien sur la qualité sonore.

## Correction après l'animatique A

La revue du vrai MP4 a repéré une fusion de l'avant-bras gauche et du sourire
à 24,917–25,333 s, ainsi que les deux retours de sourire à 10,00 et 12,25 s.
`work/jeu/corrections_b.png` montre les compositions corrigées aux instants
24,70 / 24,92 / 25,00 / 25,17 / 25,33 / 25,40 s et 9,90 / 10,00 / 10,10 /
12,20 / 12,25 / 12,50 s. La seconde prise reste rigide ; la pose finale et la
récupération antérieure à 24,70 s restent identiques. La validation du raccord
en mouvement appartient à l'animatique B, après gel de cette couche.
