# Galet en cuisine — référence commune

Commande : réaliser l'épisode de cuisine avec le nouveau galet sélectionné et
son premier essai déjà présenté. Conserver la forme compacte citron, deux yeux,
deux moufles flottantes avec un seul pouce rond et deux petits pieds. Aucun bras.
Anciennes vidéos et V29 interrompue conservées ; nouvelle production isolée ici.

## Histoire et horloge

38 secondes, 24 images/s, 1080 × 1920, sans dialogue. La chronologie locale
reprend les événements de cuisine, quatre lavages complets et les jets existants
afin de garder des repères partagés entre son et animation. Ce n'est pas un
simple changement de silhouette dans l'ancien film : les gestes et contacts
des moufles sont construits pour le nouveau personnage.

Assurance en remuant ; trace → lavage. Deux coupes de carotte, lavage plus pressé.
Tomate puis lavage presque automatique. Sel, tentative de résister au détour,
puis dernier lavage. Le rouleau diminue, le panier se remplit et le repas noircit.
Le dernier papier rebondit sur le panier plein et reste au sol. Repas brûlé,
déception, puis fausse victoire en présentant ses moufles impeccables au public.
Tenue corporelle finale 37,25–38 s ; fumée encore animée.

Toque et tablier de taille réutilisent les dessins approuvés, ajustés au galet.
Le nom MOU sur la toque reste celui du projet ; Galet demeure un nom de travail.
Le titre anglais reste en haut au début uniquement. Le gag ne dépend pas du texte.

## Interfaces et espaces

Monde cuisine : 1080 × 1920, décor et accessoires existants. Pan au voisinage
(301,1300), rouleau (876,1175), carotte/planche vers (635,1360).
`sources/character.py` expose `hand(side,target,rotation,pinch,scale,anchor)`,
`point(hand,anchor)`, `hand_svg(side,hand)` et `actor_svg(state)`. Ancres : `grip`
à l'intérieur de la paume pour un manche occlus par la moufle ; `tip` sur le vrai
point de contour du bloc arrondi. Échelle par défaut 1,2 ; dessin identique au test.

`cooking_actions.state_at(t)` produit mains et accessoires pour remuer, couper,
ajouter la tomate et le sel ; le coordinateur prend la main sur lavage/papier/fin.
`sink_galet.geometry_at(t,cycle)` expose main, vrai bout, levier et eau.
`sink_galet.svg_at(t,cycle,defs,background,art)` produit le SVG complet de l'insert.
Un seul gant y est visible ; le jet touche les bouts, pas la paume entière.

Chaque main se déplace et tourne indépendamment. Aucun trajet devant les yeux
ou la bouche pour une simple manipulation. Cible du regard avant la réaction.
Prises par contact, objets posés avant de retirer la main, deux mains seulement.

## Propriété des fichiers

- Coordinateur : `character.py`, `reference_character.py`, `animation.py`, `render.py`,
  chronologie, intégration, documentation et livraisons.
- Animation cuisine : `cooking_actions.py` et son bilan uniquement.
- Animation lavabo : `sink_galet.py` et son bilan uniquement.
- Son : `son.py`, ses modules dédiés, `audio/` et ressources sonores dédiées.
- Critique : critiques avant et après vrais rendus, aucune édition des producteurs.
- QA : vérificateur et rapports, aucune édition de l'animation ou du son.

Le scénario retenu ne demande pas une nouvelle recherche de cinq idées. Les
références déjà examinées et les retours utilisateur guident cette révision.
Outils libres existants seulement. Jazz doux, bruitages utiles à l'action ; pas
d'injection automatique des douze voix proposées. Une écoute du modèle n'est
pas disponible : ne pas certifier confort sonore ou qualité professionnelle.
