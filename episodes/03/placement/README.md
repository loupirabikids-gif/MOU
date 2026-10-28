# MOU dans la cuisine — proposition de placement

Image fixe **1080 × 1920**, destinée à juger la taille et la position de MOU.

[![Proposition de placement](MOU_cuisine_placement_apercu.png)](MOU_cuisine_placement.png)

- [PNG complet](MOU_cuisine_placement.png?raw=true)
- [Source SVG](MOU_cuisine_placement.svg?raw=true)
- [Générateur Python](sources/placement.py)
- [Paramètres de pose et de placement](PLACEMENT.json)
- [Contrôle](controle/audit_placement.json) · [Revue visuelle](controle/revue_placement.md)

Le décor validé au commit795563c reste utilisé tel quel. Le script lit ses
calques SVG et emploie directement mou_rig.character_fragment. MOU est placé
derrière l’îlot ; ses deux bras originaux sont réempilés devant le meuble pour
laisser les mains visibles. Chaque bras canonique _arm apparaît une seule fois :
aucun contour redessiné, aucune rotation, aucun raccourcissement ou masque
de racine. Le personnage subit seulement translation et échelle uniforme.

Les fichiers du décor sont vérifiés par empreintes et restent identiques.
Un rendu sans personnage reproduit exactement le décor validé pixel par pixel.
Les pixels hors du personnage restent identiques à1niveau/255 près, dû aux
arrondis de composition.

Reproduire depuis la racine :

    XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/03/placement/sources/placement.py

Outils locaux libres : Python, SVG, CairoSVG, Pillow et NumPy. Le script résout
ses fichiers depuis son propre chemin. Aucun modèle ou dessin du décor n’est
modifié. Cette image est une proposition, pas un placement approuvé par
l’utilisatrice. Aucun mouvement, son, ingrédient ou nouvelle prise d’objet
n’est fabriqué à cette étape.
