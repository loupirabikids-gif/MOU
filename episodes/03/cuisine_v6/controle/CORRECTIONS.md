# Corrections et contrôles de la révision cuisine V6

28 octobre 2026. Révision ciblée de la v5 à la demande de l’utilisatrice.

## Ajouts retenus

- Jet d’eau environ trois à quatre fois plus large, impact et éclaboussures
  dans le bassin ; bruitages d’eau renforcés de 4 dB par rapport à la v5.
- Tablier corail attaché au corps, sous les deux bras, visage dégagé.
- Petit balancement joyeux pendant la cuisine et quatre phrases sifflées
  originales, neuf notes à 108 BPM. Une seule bouche se transforme en O aux
  notes puis retrouve le sourire. Arrêt du jeu aux inspections et lavages ;
  les deux impacts du couteau conservent leurs contacts stables.

Les études puis l’animatique complète ont été examinées par le critique dans
ses propres rapports. Aucun défaut artistique matériel supplémentaire n’a été
retenu pour imposer une réécriture du gag. Les fonctions natives des bras,
les deux moufles, le décor et la main à 0,70 dans le lavabo sont conservés.

## Encodage corrigé après contrôle du premier export

Le premier export final en CRF 18 échouait au contrôle strict de deux zones
de main : erreur RGB moyenne 3,0315/255 à 1,458 s et 3,1100/255 à 9 s, pour
une limite de 3/255. Le rapport est conservé sous `audit_final_crf18.json`.
Les sources gelées et les fonctions du rig étaient conformes : aucun indice
de mauvaise géométrie ou de cache périmé n’a été trouvé.

Correction : augmenter la qualité H.264 en CRF 16, réencoder les mêmes images,
puis relancer le contrôleur sans changer son seuil. `audit_final.json` passe
les 33 comparaisons hors cache et toutes les zones visibles. Le critique
relit le véritable nouveau fichier ; l’ancienne preuve est identifiée comme
historique. Ni le jeu, ni les dessins, ni le son n’ont changé pour cette étape.

## Limites conservées

La critique repose sur des images décodées successives. Les rendez-vous et
niveaux sonores sont vérifiés numériquement ; aucune écoute perceptive ni
projection auprès d’un nouveau spectateur n’est revendiquée. La recherche
internet reste partielle, documentée dans `../editorial/veille_cuisine_v6.md`.
