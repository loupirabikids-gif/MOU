# Moufle à pouce arrondi dans les cinq lavages

L’accord « Oui go pour la video » autorise l’intégration de l’étude corrigée
au commit `b4b0f78d0c66bb9edc8446945a9d1c8600b6f736` dans le montage existant.
La V13 et le rig canonique restent conservés. Cette révision ne change ni les
plans de cuisine, ni les prises d’objets, ni la chronologie de 41 s, ni les sons.

## Construction

`mitten.py` reprend exactement les constantes `OPEN` et `CONTACT` validées.
Une seule moufle : un pouce extérieur distinct, les quatre autres doigts en
un volume rond unique. Le sommet du pouce et son extrémité conservent leurs
tangentes colinéaires durant le repli et les frottements ; les contrôles du
petit bout bougent ensemble, ce qui évite le sommet triangulaire rejeté.

Le script n’importe ni le rendu de l’étude ni des sources V13. Il est autonome
dans le dossier V14 pour que l’archive de sources puisse reproduire les images.
Le bras natif est conservé à droite de la jonction, comme dans l’étude ; seul
son bout est remplacé par la moufle approuvée. Aucun trait transversal de poignet.
La couleur `#D8F449`, le contour `#2B0A24` et le trait 8,372 du gros plan sont
ceux de l’étude. Le bassin, le robinet, le fort débit et le cadrage V13 restent
inchangés (`viewBox 0 925 270 480`).

## Geste et contacts

Chaque intervalle `wash` existant reçoit le rapprochement, le frottement puis
le relâchement de l’étude, sans ses longues poses d’attente. Trois frottements
pour les cycles de 1,30 et 1,07 s ; deux pour ceux de 0,64, 0,59 et 0,59 s.
Le pouce bouge relativement au bloc des doigts ; le poignet reste à droite,
hors du jet. L’ouverture et la fermeture gardent leurs repères d’origine.

La vraie extrémité gauche du contour des doigts est calculée sur sa cubique.
Pendant la manipulation du robinet, cette limite rejoint réellement le bout
du levier mobile. L’écart de quelques unités entre l’ancien bout natif et le
nouveau contour est compensé par une translation commune moufle/avant-bras,
puis cette correction s’efface à l’approche du jet. La pose sous l’eau reste
calée sur l’étude validée. Le jet et sa teinte humide sont découpés par le
contour effectivement dessiné ; la teinte n’atteint pas le poignet.

## Études et données vérifiables

`controle/etude_pouce_v14/planche.png` réunit 25 poses, cinq par lavage :
ouverture, moufle au début du rinçage, frottement, relâchement et fermeture.
Les PNG d’ouverture et frottement du premier cycle et la planche complète ont
été examinés visuellement. Le pouce extérieur reste lisible, la fermeture
des autres doigts reste ronde et la cuve est dégagée. Cette vérification de
poses ne vaut ni visionnage continu du montage exporté ni écoute du son.

`geometrie.json` contient les coordonnées réellement émises pour chaque étude.
`geometry_at` expose : `mitten_local_points`, `mitten_world_points`,
`mitten_outline_d`, `mitten_translation`, `mitten_phase`, `mitten_progress`,
`rub_cycles`, `thumb_bounds`, `forearm_clip_x`, `forearm_join_points`,
`tap_target`, le vrai `tip`, le `wrist`, ainsi que la matrice du bras conservé.
`hand_polygon` échantillonne la nouvelle moufle et `distal_cap_polygon` le bord
réel des doigts. L’ancien cap est seulement conservé sous le nom explicite
`reference_native_distal_cap_polygon`.

La structure des 984 SVG a été vérifiée : une seule main marquée dans les
inserts et deux dans les plans de cuisine, identifiants uniques. Les vrais
exports et les contacts font l’objet des contrôles indépendants de la V14.
