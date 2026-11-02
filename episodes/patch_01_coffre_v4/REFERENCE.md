# Référence commune — PATCH, vues et jeu V4

2 novembre 2026, Africa/Casablanca. Commande : corriger le film pour qu'il
soit similaire à la référence vidéo dans ses points de vue, ses positions
et son jeu. Les anciennes versions restent conservées. La vidéo fournie
est une référence privée ; aucun de ses plans ou sons n'entre dans le film.

## Personnage et fabrication

PATCH reste le raton gris et crème au masque brun, au hoodie corail,
aux deux oreilles et à la queue annelée. Deux yeux, deux bras continus,
deux pattes et deux pieds. Le dessin et la palette demeurent identifiables.
Les nouvelles positions doivent rester raccordées, même lorsque les bras
se croisent, qu'une patte porte la joue ou que les deux mains gardent l'objet.

Python, SVG, Pillow, CairoSVG et FFmpeg restent les outils de production,
gratuits et libres. Les vues du bureau et du coffre sont dessinées pour
leurs perspectives respectives ; un zoom du plan frontal ne suffit pas.

## Récit, durée et états à préserver

Film de 30 secondes à 24 images/s, 1080 × 1920. Le récit représente trente
minutes par des ellipses explicites. PATCH veut travailler, choisit de
s'éloigner du téléphone, tente deux retours vers sa feuille puis consacre
sa séance au coffre. Il retrouve l'écran avec joie. Les trois cases de la
liste restent vides ; sa satisfaction sincère fait contraste avec l'échec.

- Prise initiale du téléphone à 1,70 s ; dépôt réel dans le coffre à 2,80 s.
- Fermeture à 3,55 s ; appui au bouton à 3,90 s et verrouillage à 4 s.
- Départ `30:00`, repères `30 MIN` et `MIN:SEC`, horloge à 09:00.
- Première ellipse à 6 s, puis vingt-neuf vérifications représentées.
- Crayon définitivement posé à 11,78125 s ; aucune trace d'écriture ajoutée.
- Dernière seconde entre 22 et 23 s : `00:01`, coffre encore fermé.
- Déverrouillage à 23 s, horloge à 09:30 ; reprise à 24,05 s après ouverture.
- Joie après la prise ; deux pieds visibles dans une vue adaptée si la
  pose suspendue est retenue, sans inventer une réception qui n'est pas montrée.
- Insert `TO DO` de 26,65 à 27,9 s : trois cases identiques, zéro coche.
- Fin de 27,9 à 30 s : deux mains portantes, écran vers PATCH, regard bas,
  petit sourire fermé et lumière douce sur le museau.

## Vues à construire et fonctions

| Temps | Vue | Intention visible |
|---|---|---|
| 0–2,1 s | `wide_high`, plongée de trois quarts | Situer bureau, chaise, tâche et téléphone dans un espace profond, puis faire choisir le coffre. |
| 2,1–4,6 s | `lock_insert` | Voir le dépôt, la fermeture, l'appui et le délai de trente minutes. |
| 4,6–6 s | `medium` | Revenir volontairement à la feuille avec le crayon prêt. |
| 6–7 s | `clock` | Rendre la première minute et l'ellipse explicites. |
| 7–10 s | `medium` | Regard vers le coffre puis retour réel vers le papier ; seconde vérification plus longue. |
| 10–12,25 s | `work_close` | Isoler le renoncement : regard bas, crayon posé, patte libre. |
| 12,25–18,4 s | `medium` | Joue portée, puis fermeture des yeux et bras croisés rapides, suivis de pauses. |
| 18,4–21,7 s | `low`, ras du plateau | Baisser le corps et le museau vers le coffre qui domine au premier plan. |
| 21,7–23 s | `box_insert` | Concentrer l'attention sur la dernière minute puis la dernière seconde exacte. |
| 23–24,7 s | `face_box` | Relier ouverture, surprise et prise réelle, avant la joie de possession. |
| 24,7–26,65 s | `joy` | Libérer le corps entier dans le cadre, téléphone gardé à deux mains. |
| 26,65–27,9 s | `paper` | Faire lire l'absence de résultat sans explication verbale. |
| 27,9–30 s | `phone_final` | Calmer la joie en absorption satisfaite ; garder la liste comme conséquence. |

Les positions sont précisées dans `sources/cadres.json`. Le décor, le
plateau, la chaise et les occlusions doivent changer avec la vue. En vue
basse, le plateau est mince et la façade remplit le bas ; le coffre peut
passer devant une partie de joue en gardant les deux yeux lisibles.

## Contrat de prises et d'orientation

Les contacts protégés du début et de la reprise ne doivent pas être cassés
par le changement d'angle. Le coordinateur remappe ensemble le personnage,
les paumes et les accessoires. Après 24,7 s, `jeu.phone_binding(t, actor)`
définit centre, angle, face et caractère bilatéral de la prise. Le téléphone
suit les paumes finales ; la main opposée doit réellement toucher son bord.
Le contrat prévoit une transition continue depuis la prise précédente vers
la prise bilatérale, puis l'objet centré devant le buste à la fin.

Lorsque PATCH consulte l'écran, le dos et ses objectifs sont présentés
au spectateur. Une face écran tournée vers la caméra ne doit pas remplacer
cette orientation. La lueur doit venir du côté de l'écran vers le museau.

## Son et frontières de travail

La banque documentée de la V3 et ses dix-huit cues sont conservées, sans
nouvelle musique, voix, bruit d'écriture ou accent systématique sur les poses.
Aucun impact de réception n'est ajouté à une suspension coupée avant la
réception. Les gains restent fixes. Aucun confort d'écoute n'est revendiqué.

Le coordinateur possède scène, contacts, chronologie, cadres, rendu, exports,
sources et bilan. Le décor possède `vues.py`. Le jeu possède `personnage.py`
et `jeu.py`. Le scénario et le son possèdent le présent fichier, le découpage,
`son.py` et `audio/`. La critique possède ses rapports ; la QA son contrôleur
et son rapport. Aucun agent ne modifie les fichiers d'un autre rôle.

Revoir les vues et poses réellement rendues face à la référence, puis
l'animatique complète sans son, avant le HD. Vérifier le fichier final
effectivement exporté. Une validation numérique ne garantit ni fidélité
artistique, ni confort sonore, ni réception du public.
