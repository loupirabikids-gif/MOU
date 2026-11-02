# Corrections — retour « le gag n'est pas lisible »

LaV1 n'est pas une référence comique validée. Le retour de l'utilisatrice
prime sur sa QA et les lectures internes précédentes.

- **Enjeu trop faible :** remplacer le délai réel de dix secondes par trente
  minutes dans l'histoire, représentées dans un film de trente secondes.
- **Temps ambigu :** afficher30MIN, MIN:SEC, une horloge et une première
  ellipse explicite ; montrer chaque minute et réserver davantage de temps
  aux derniers03:00,02:00,01:00, puis00:01.
- **Tentative de travail trop abstraite :** garder le crayon, montrer les yeux
  et la pointe revenir vers le papier après les deux premiers regards, puis
  le dépôt définitif du crayon.
- **Résultat difficile à lire :** remplacer la feuille vierge par une liste
  TO DO à trois cases vides et réserver un insert final à cette même liste.
- **Continuité à conserver :** reprendre sans modification le rig, la prise
  du téléphone, le coffre opaque, la profondeur du couvercle et les contacts.
- **Son indépendant du récit :** déplacer les contacts aux nouveaux instants,
  ajouter seulement quelques accents d'ellipse ; aucun bruit d'écriture sur
  une feuille sans trace, aucune musique ou voix pour expliquer le gag.

Les corrections ci-dessus sont présentes dans la première animatiqueV2.
La critique du vrai fichier et la QA conservent leurs constats séparément.

La QA a ensuite identifié un défaut de calcul à l'image399 (16,5833s) :
l'arrondi flottant affichait «16 MIN ELAPSED» une image trop tard, tandis que
le coffre et l'horloge indiquaient déjà la minute17. Le calcul de minute
reçoit une tolérance de1e-7s ; l'animatique et le HD sont rendus de nouveau
depuis cette source corrigée. Aucun dessin, contact ou son n'est changé.
