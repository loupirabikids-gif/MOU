# Accessoires et cuisson V26

30 octobre 2026. Réalisation limitée à `sources/art.py` et
`sources/cooking_fx.py`. Le modèle de MOU, ses moufles, le lavabo, le costume,
la carotte et le couteau ne sont pas redessinés par cette contribution.

## Repas et vapeur

`cooking_fx.food_svg(t, state, base_art)` remplace la couche des aliments.
Le temps `t` est le temps de production V26. Les cinq morceaux de légumes,
les deux rondelles et la tomate ajoutée gardent leurs positions et contours
originaux. Les couleurs passent progressivement du vert au doré, puis au
brun et au charbon. Un dépôt de cuisson apparaît graduellement dans la
cavité de la poêle ; aucun bloc noir étranger ne remplace les ingrédients.

La coloration dorée se forme entre 10 et 20 s. Le noircissement évolue entre
19,5 et 30,25 s. L'indicateur public `cooking_state(t)` expose ces valeurs
continues pour le contrôle, sans changer l'histoire ou ses contacts.

`cooking_fx.steam_svg(t, state)` fournit une couche séparée, à placer après
les aliments et avant les bras. Deux volutes légères deviennent trois puis
quatre avec des entrées fondues, sans apparition brusque. Elles deviennent
grises entre 24,2 et 25,7 s, assez visibles pour le regard de MOU vers 25,55 s.
Leur enveloppe reste à gauche, dans x=200–382 et y>990. La fumée continue de
monter pendant la tenue finale du corps ; elle ne doit pas être figée avec
le personnage. Aucun écran de brouillard, flamme, alarme ou flou ajouté.

## Papier et poubelle

Le panier garde son dessin, sa maille et son ombre. Trois grosses boulettes
persistent aux positions et rayons de `chronologie.json` :

| Ordre | Centre | Rayon |
| --- | --- | --- |
| 1 | 140,1700 | 58 |
| 2 | 195,1590 | 70 |
| 3 | 135,1480 | 82 |

La quatrième boulette est distincte : rayon 22, graine visuelle 4, rebond sur
le tas puis position finale 325,1805. `bin_svg` attend toujours que l'animation
fournisse son rayon et sa graine pendant le vol ; elle ne la transforme pas
en une quatrième grosse boule. Son marquage au sol porte maintenant l'ordre 4.
Le dernier morceau souple reste 64 × 88 avant froissage, avec son contour et la
prise de moufle existants ; aucun petit rectangle rigide n'est créé.

## Contrôles réellement faits

Six rendus isolés de la poêle et quatre du panier ont été produits par
CairoSVG, assemblés puis réellement ouverts. Planches privées :
`work/v26_art/progression_cuisson.png` et
`work/v26_art/progression_poubelle.png`.

Ces images montrent les aliments encore reconnaissables à 30,3 et 37,5 s,
la vapeur devenue grise, trois états de remplissage persistants et le petit
papier au sol. Les coordonnées/contours des aliments sont identiques dans
les trois derniers états ; le changement est de couleur et de matière.
La couche vapeur diffère entre 37,25 et 37,5 s, donc la tenue du corps ne la fige
pas par sa propre API. Les paramètres de panier correspondent à la chronologie
et le dernier papier conserve ses dimensions 64 × 88.

Ces contrôles isolés ne valident pas encore la superposition avec le visage
ou les mains pendant les grandes déformations, ni la lisibilité au sein de
l'animatique complète. Le critique devra voir le fichier réellement monté.
