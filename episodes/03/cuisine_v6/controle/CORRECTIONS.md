# Corrections et contrôles de la révision cuisine V6

28 octobre 2026. Révision ciblée de la v5 à la demande de l’utilisatrice.

## Papier souple V11 — retouche autorisée avant diffusion

À 30,25–32,083 s, le dernier morceau ressemblait à une icône de document :
arêtes droites et coin rabattu. La retouche conserve l’encombrement 64 × 88,
la prise et les mains ; elle remplace ces arêtes par un contour légèrement
incurvé, un bas irrégulier et deux plis courbes. Le coin de document disparaît.
La boulette de rayon 22 reste identique en main, en vol et dans la poubelle.

Le départ du froissage reprend exactement le même contour souple ; l’ordre
des sommets conserve le sens de la boulette miroir. Dans la première étude,
le critique a repéré un pli qui dépassait du papier pendant sa contraction,
vers 32,167–32,333 s. Les plis sont maintenant masqués par le contour courant,
sans changement des gestes ou de la silhouette. Huit détails successifs sont
réexaminés après cette correction.

Seul `art.py` change le dessin. Personnage, bras/raccords, deux moufles, contacts,
regards, expressions, légende V10, montage de 35 s et tous les sons sont
conservés. Voir `audit_papier_v11.json`, `developpement/papier_v11.md` et les
critiques `*papier_v11*`. La V10 reste accessible au commit `b7328c6`.
Le premier export V11 en CRF 14 dépasse légèrement le seuil RGB 3/255 dans
deux régions de main à l’image 777 (32,375 s) : 3,027337 et 3,020194.
Le rapport est conservé sous `audit_final_papier_v11_crf14.json`. La qualité
d’encodage passe en CRF 12, sans changer le seuil ou les SVG, avant de refaire
les contrôles et la relecture du véritable fichier livré.
Les sections suivantes sont l’historique des versions précédentes.

## Légende V10 — phrase validée au départ

Ajout de « Me cooking: touch, wash, wipe… repeat. » pendant les trois premières
secondes, sur deux lignes, sans masquer le visage. Sortie douce à 2,85–3 s.
La police fournie est utilisée directement par Pillow et gelée avec le rendu.
Le calque transparent s’intègre au SVG ; le reste de la scène est conservé.

La première étude plaçait le texte devant le luminaire : son cordon traversait
visuellement certains mots. Les deux lignes sont déplacées sous l’étagère,
au-dessus de la tête, avec contour crème. L’étude native et la réduction au
format téléphone sont relues : texte entier lisible, visage dégagé.

Le montage, le mix et tous les gestes restent ceux de la V9. Les 43 SVG
échantillonnés après la disparition sont identiques aux empreintes précédentes.
Le retour sur la forme du dernier papier reste une proposition distincte ;
aucune correction de papier ou de main n’est incluse dans cette sélection.

Voir `audit_caption_v10.json` et les critiques de la légende. Les sections
suivantes restent l’historique des révisions précédentes.

## Rythme V9 — ouverture prolongée

Retour : la cuisine initiale se lit trop vite. Le montage passe de 30 à
35 s : remuage actif jusqu’à 6,6 s, cuillère posée à 7 s, puis inspection
de main jusqu’à 7,75 s. La main monte en un quart de seconde et son regard
reste dessus jusqu’à 7,5 s, puis s’oriente vers le lavabo.

Le geste natif effectue quatre tours, sans ralenti global. Les 654 états
à partir du premier lavabo sont identiques à la V8, décalés de 120 images ;
32 empreintes de SVG indépendantes sont également identiques. Le contact
cuillère/main et la position de son bout dans la poêle sont contrôlés sur
les 159 images de remuage, avec les coutures à 3,3 et 6,6 s.

La musique conserve son tempo ; les événements suivants sont décalés de
cinq secondes. Seuls le lit de cuisson, le premier remuage et la piste
musicale sont régénérés plus longs. Les 46 autres bruitages et les trois
notes initiales gardent leurs WAV. Le gain commun varie de +0,007 dB après
recalcul du lit prolongé. Aucun sifflement supplémentaire.

Voir `audit_rythme_v9.json`, `audit_rythme_son_v9.json` et les critiques V9.
Les sections suivantes restent l’historique des versions précédentes.

## Correctif sonore V8, après précision de l’utilisatrice

Conserver seulement la phrase sifflée initiale, de 0,3 à 1,731111 s. Les trois
phrases suivantes et leurs bouches O sont retirées. Le dernier message précise
que l’arrêt est lié au lavage, et remplace la mention précédente de cuisine.
Aucun ajout de pause ni changement de geste n’est nécessaire.

Une musique de fond originale à 108 BPM accompagne les plages de cuisine :
0–2,75 ; 8,5–10 ; 15–18 ; 22–23 s. Elle se coupe sur chaque entrée au lavabo,
reste coupée pendant essuyage, jet et zoom, puis revient au retour cuisine.
Le dernier petit papier et la tenue finale conservent leurs seuls bruitages.
Les gestes, le personnage et le correctif papier V7 sont conservés.

Les contrôles du son et la critique actuelle sont dans `*musique_v8*`.
Les sections suivantes documentent les révisions antérieures et leurs
empreintes ; le contrôle courant des MP4 reste `audit_final.json`.

## Correctif papier V7, après retour sur la V6

Problème observé à 25,4–27,1 s : le dernier morceau de 26 × 40 unités ne
reste qu’une petite tache entre les moufles sur un écran de téléphone.
L’utilisatrice demande de l’agrandir. La critique indépendante confirme ce
problème sur une image décodée du montage livré.

Correction ciblée : morceau de 64 × 88, même prise et mêmes gestes. La
boulette passe de rayon 11 à 22 en main, en vol et dans la poubelle. Elle
reste plus petite que les trois grosses boulettes précédentes. Le départ du
froissage reprend le même contour et le même ancrage que la feuille tenue,
afin de conserver la continuité après son agrandissement.

Les 720 états sont comparés à la version du commit `0e188a3` : 27 champs
restent identiques, notamment corps, bras, mains, regards, expressions,
tablier, cuisine, eau, caméra et rythme. Aucun son ni événement de chronologie
n’est modifié. Les SVG échantillonnés avant le dernier tirage sont identiques.
Voir `audit_papier_v7.json`, les études et les critiques `*papier_v7*`.

Contrôle du froissage vers 27,30 s : l’interpolation vers une boulette
miroir inversait le sens de parcours du contour et le croisait brièvement.
Le sens des sommets a été rétabli sans changer la forme finale. Sur 101
progressions, le contour reste simple, sa surface positive et décroissante.
La critique reprend cette transition sur les nouvelles images réellement
décodées ; l’ancienne attribution à une occultation par les mains est retirée.

L’encodage du papier agrandi en CRF 16 dépassait légèrement la limite RGB
dans trois zones de mains à 27,33 et 27,58 s : maximum 3,0491/255 pour un seuil
de 3/255. Rapport conservé : `audit_final_papier_v7_crf16.json`. Le rendu final
est réencodé en CRF 14 avec le seuil inchangé ; les comparaisons hors cache
incluent maintenant quatre instants supplémentaires autour du froissage/jet.

Les deux exemples fournis sont consignés dans
`../editorial/references_utilisatrice_v7.md`. Leur accès renvoie un refus du
proxy ; aucune adaptation du montage ne leur est attribuée sans visionnage.

Les sections suivantes décrivent la V6 initiale, conservée dans Git avec son
empreinte. Le contrôle courant après correctif est `audit_final.json`.

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
puis relancer le contrôleur sans changer son seuil. `audit_final_v6_avant_papier_v7.json` conserve
les 33 comparaisons réussies hors cache et toutes les zones visibles. Le critique
relit le véritable nouveau fichier ; l’ancienne preuve est identifiée comme
historique. Ni le jeu, ni les dessins, ni le son n’ont changé pour cette étape.

## Limites conservées

La critique repose sur des images décodées successives. Les rendez-vous et
niveaux sonores sont vérifiés numériquement ; aucune écoute perceptive ni
projection auprès d’un nouveau spectateur n’est revendiquée. La recherche
internet reste partielle, documentée dans `../editorial/veille_cuisine_v6.md`.
