# Décor de cuisine — proposition 1

**Décor validé par l’utilisatrice** ; voir [la référence](VALIDATION.md).
Image fixe verticale **1080 × 1920**, dessin original réalisé en SVG.
Couleurs crème, bois et lavande, contours prune ; centre laissé libre pour MOU.

[![Aperçu](MOU_cuisine_apercu.png)](MOU_cuisine_decor.png)

- [PNG complet](MOU_cuisine_decor.png?raw=true)
- [SVG modifiable](MOU_cuisine_decor.svg?raw=true)
- [Générateur Python](sources/decor.py)
- [Repères et palette](DECOR.json)
- [Revue du décor](controle/revue_decor.md)

Les éléments de premier plan sont séparés : poêle et plaque à gauche,
planche de préparation au centre, rouleau d’essuie-tout avec amorce de feuille
à droite. Évier, fenêtre, étagère et meuble mural composent le fond.

## Calques

Dans calques/, chaque groupe existe en SVG et en PNG :
fond_cuisine, ilot_cuisine, accessoires_cuisine.
Les deux derniers PNG ont un fond transparent. Le générateur assemble ces
mêmes dessins pour le décor complet, avec une seule définition des couleurs.

Depuis la racine du dépôt, dans l’environnement installé :

    XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python episodes/03/decor/sources/decor.py

Le script retrouve son dossier depuis son propre chemin ; aucun service,
compte ou réseau n’est nécessaire au dessin. Outils libres : Python, SVG,
CairoSVG, Pillow et NumPy. Aucun média de stock ni génération à crédits.
Le script n’importe ni ne modifie le rig du personnage.

La composition des trois calques est comparée au PNG complet ; dimensions,
opacité et empreintes figurent dans controle/audit_decor.json.
La revue porte sur cette image fixe. Contacts des mains, échelle finale de
MOU et animation des accessoires restent des étapes ultérieures.
