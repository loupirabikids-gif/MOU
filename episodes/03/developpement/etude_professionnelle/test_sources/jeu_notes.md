# Jeu du test de 8 secondes

Fichiers exclusifs : `acting.py`, `poses.json`, ce document. Aucun épisode
de production n’est modifié. Base attendue : copie de l’état V20 à40,5s et
module d’animation V20 fournissant les solveurs et le dessin natifs.

## API d’intégration

```python
state = acting.state_at(frame, animation_v20, base_state)
```

Le corps garde exactement `(80,380,2.3)` pendant les192images. Les deux bras
sont dessinés par les fonctions existantes, sans nouvel étirement ni contour.
`pro_shot` choisit l’un des cinq plans définis dans `poses.json` ;
`pro_test_frame` et `pro_test_time` donnent le temps local du test.

Le renderer applique `face_roll_deg` au groupe **face entier**, masques compris,
autour du pivot natif `(205,250)`. Les valeurs restent entre−2et+2,5degrés.
Le regard est calculé dans le repère inverse correspondant. Aucun mouvement
vertical ni translation du corps ne porte les émotions.

`drop` et `ending_drop` désignent le même ancrage sur la calotte réellement
dessinée de la moufle gauche, demi-trait compris. `amount` vaut1jusqu’à84,
puis descend à0à89. `apron_wetness` progresse pendant le contact ;
`contact_apron` contient le point fixe natif `(195,385)`, le point réel mobile,
et les bornes84–104. L’insert doit montrer l’absorption et la trace.

## Espacement et pauses

- Regard vers le tube images4–10 ; main droite après le regard, images10–24.
  Le geste s’arrête ensuite et le tube reste sous le regard.
- Regard vers le tablier images48–56, avec un seul bref clignement. Arrêt
  images56–63, puis pose de solution images68–75. La main attend l’image76.
- Une seule passe sur le tissu images84–103. Entrée et sortie sont séparées.
  Images108–115 : main gauche remontée hors de la poche, droite à l’écart,
  pour tenir la trace dégagée. Pas de deuxième frottement décoratif.
- Le plan large commence sur les positions de mains précédentes, puis les
  deux mains rejoignent la pose native de repos images116–124. Leur retour
  accompagne le regard au tas et évite un saut de position entre les plans.
- Le regard rejoint le public images160–166. La bouche reste retenue jusqu’à
 172 ; la tentative de sourire arrive ensuite. Les16dernières images tiennent
  exactement la même expression et la même pose.

Les poses sont volontairement peu nombreuses : contrariété, solution, puis
pris sur le fait. L’essuyage se lit par le contact du tissu ; il ne reçoit pas
une nouvelle succession de grimaces. Les intervalles de tenue produisent de
vraies expositions stables, pas une oscillation permanente des paramètres.

## Limites à contrôler au rendu

Une valeur de pose ou une ancre exacte ne certifie pas l’émotion. Vérifier
le vrai MP4 muet : tube et goutte identifiables à taille mobile, macro loin
du menton, tissu lisible autour de la moufle, trace dégagée, regard au tas
assez tenu et dernier sourire sans lecture de frime. Les rotations du visage
doivent conserver pupilles et langue dans leurs masques. Aucun avis d’écoute
ni garantie de rendu professionnel n’est revendiqué par ce module.
