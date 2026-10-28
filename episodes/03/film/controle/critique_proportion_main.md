# Contre-contrôle indépendant : taille de la main et raccord du bras

Le retour utilisateur porte sur deux points précis : la correction effective
du raccord du bras, et la main trop grande dans les inserts du lavabo. Cette
revue ne demande aucun changement du récit, du son ou des autres gestes.

## Ce que le contrôle précédent avait manqué

La précédente validation du gros plan ne prouvait pas que le raccord du bras
était entièrement corrigé : ce raccord était alors hors champ. Elle n’avait
pas non plus relevé que la main dominait trop la cuve dans ce cadrage.

Une reprise des vrais pixels de la version précédente, commit `aada993`,
SHA256 vidéo `fca85b1fc1f268e717603e1dc328a4f89fb6ddbddec57589156782b661523061`,
montre encore une petite bosse sombre au raccord extérieur dans plusieurs
plans larges : 0,50 s, 7,25 s, 17,625 s et 24,75 s. Les poses à 2,75 s et
10,25 s gardent une cassure de pente. La correction précédente était donc
partielle, et son annonce trop générale. Le bras restait attaché ; il ne
fallait pas pour autant qualifier sa jonction de totalement lisse.

Preuves de travail : `work/main_lavabo_critique/raccords_plans_larges_avant.png`
et `raccord_placement_original.png`. Les recadrages sont agrandis pour examiner
le défaut, pas présentés comme des images de diffusion.

## Corrections examinées avant le final

- La réduction à 0,70 du bras et de la main dans les seuls inserts améliore
  leur proportion par rapport à la cuve, en conservant le dessin de la moufle.
  La première étude réduite faisait cependant apparaître la racine du bras
  dans le cadre et éloignait la main du filet. Ces deux défauts ont été signalés,
  puis repris par le cadrage et le placement au contact de l’eau. Cette première
  étude n’a pas été validée pour livraison.
- Le nouveau raccord extérieur rejoint la silhouette du corps par une courbe
  locale arrondie. Les six poses d’étude montrent la disparition de la bosse,
  sans changement visible du trait intérieur ou de la moufle. La retouche
  concerne le contour et son remplissage au raccord, pas toute la forme du bras.
- Une contrelecture supplémentaire du véritable aperçu à 10,333 s et 10,50 s
  a retrouvé une cassure sur un petit passage initialement non repris. Ces huit
  images du transport de tomate ont reçu le même traitement local avant le final.

## Contrelecture du véritable MP4 corrigé

Fichier : `MOU_Encore_une_feuille.mp4`, 1080 × 1920, 24 images/s, 26 s.
SHA256 vérifié sur le fichier effectivement décodé :
`ea75c9377982ba32982448234d259bb9eff5f7727e920cebaf2f71e4662c91b2`.

Dix-neuf images ont été décodées et examinées : indices 12, 66, 89, 112, 147,
174, 246 à 254, 307, 423, 470 et 594, comptés depuis zéro. Cela inclut les six
poses larges, les huit images consécutives du passage de tomate repris, les
trois états ouverture/lavage/fermeture du premier insert et les deux lavages
suivants. Études et liste dans `work/main_lavabo_critique/final/`.

- **Plans larges :** la petite bosse extérieure observée auparavant disparaît
  sur les six poses contrôlées. La jonction suit une courbe continue.
- **10,292 à 10,583 s :** les huit images consécutives montrent également une
  jonction extérieure arrondie ; la cassure signalée dans l’aperçu est corrigée.
- **Lavabo à 4,667 s, 12,792 s et 19,583 s :** la main est moins dominante par
  rapport à la cuve. Le filet rejoint son bord supérieur sans vide visible.
  La portion de bras continue hors du bord droit, sans racine terminée dans
  l’image. Aucun visage ni corps n’apparaît dans ces inserts.
- **Commande à 3,708 s et 6,125 s :** le contact de la main reste lisible ; les
  gouttes après fermeture sont proches de la main. Le dessin arrondi de la
  moufle est conservé.

## Avis et limites

Avis favorable à la livraison de ces deux corrections locales. Aucun nouveau
défaut matériel n’est retenu dans ce périmètre sur les images du MP4 examinées.
La préférence finale de proportion reste soumise au jugement de l’utilisatrice.

Il s’agit d’une lecture d’images réellement décodées, et non d’une projection
continue ou d’une écoute audio. L’identité des autres actions, du son et des
zones hors du raccord relève des audits de périmètre du coordinateur et du
diagnostic d’animation ; elle n’est pas revendiquée ici comme une comparaison
indépendante de tous les pixels et de toutes les images.
