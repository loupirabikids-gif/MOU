# Audit ciblé de synchronisation — V27 avant correction

30 octobre 2026. Référence : MP4 final V27, 38 s, 24 images/s.
SHA256 : `6c3a47f1f145b0b650ef22177276f05919f8e3f48e664ff42948988d9ea41ee6`.

Examen de la chronologie, du contrôleur facial et des cinq cues vocaux. Vingt
images du vrai MP4 ont été décodées et réellement ouvertes en planche, à quatre
repères par accent. Les paramètres de bouche ont été évalués aux mêmes images.
Les signaux des cues et du mix/AAC ont été mesurés. Ce n'est ni une écoute ni
une lecture continue ; aucune appréciation de naturel vocal n'est certifiée.
Preuves privées : `work/synchro_v28/vocal_frames.png` et `analysis.json`.

## Aucun décalage global du fichier audio établi

Six corrélations locales AAC/WAV autour du lavabo et des cinq accents donnent
un maximum à **0 échantillon de retard**, dans une recherche de ±20 ms. Les
corrélations à décalage nul vont de 0,996525 à 0,999904. L'export ne présente
donc pas ici un retard global à corriger en déplaçant toute la piste.

Les pics d'énergie des cues d'impact suivent les contacts programmés de moins
d'une image : premier panier 8,387 s (+0,65 image), deuxième 14,653 (+0,80),
troisième 19,220 (+0,97), petit papier 29,013 (+0,32), sol 29,880 (+0,73).
Les couteaux culminent 9,407 et9,987 s, soit +0,17/+0,18 image après leurs
contacts programmés 9,40/9,98. Ces écarts décrivent l'attaque des WAV, pas une
preuve que chaque contact visible est parfait ; aucun motif n'impose de
recaler ces familles en bloc.

## Deux réserves de couplage réellement observables

### 1. Inspiration à 25,68–25,84 s pendant une fermeture de bouche

Le cue commence 25,680 s, devient actif vers 25,694 s et son maximum d'énergie
sur fenêtre 10 ms arrive 25,767 s. Dans les images réellement ouvertes, la
bouche O est déjà grande à 25,542 s pour le petit papier, puis **se referme**
pendant la découverte de fumée : ouverture 0,333 à 25,667 puis 0,201 à 25,792.
Le regard va bien vers la fumée, mais aucune nouvelle prise d'air visible
ne distingue le souffle de la première surprise.

Effet plausible : l'inspiration peut paraître ajoutée après la réaction,
même si son horodatage appartient à la bonne séquence. Cette lecture est
une hypothèse de réception, pas un retard d'export mesuré.

Correction locale proposée : donner à la découverte de fumée une petite
inspiration distincte : maintien ou petite impulsion d'ouverture à 25,667 s, sommet vers 25,750 s,
maintien jusqu'à 25,875 s puis relâchement avant 25,917 s et retour au choix de la main avant 26,15 s. Le pic
actuel 25,767 s reste alors à 0,40 image du sommet ; déplacer le WAV entier
n'est pas nécessaire. Préserver le regard qui atteint d'abord la fumée.

### 2. Expiration à 32,78–33,06 s sur un acteur entièrement figé

Le maximum d'énergie est 32,809 s. Aux images 32,625 /32,792 /32,917 /33,125,
la bouche reste une courbe fermée et le corps demeure posé. Une comparaison
directe des fragments corporels, des bras, des pieds et de l'affine confirme
qu'ils sont strictement identiques sur les neuf images 32,750–33,083.
Le son est prévu nasal : **une bouche fermée n'est donc pas, à elle seule,
un défaut de synchronisation**. La faiblesse est l'absence de tout indice
corporel qui fasse sentir l'expiration de déception.

Effet plausible : le souffle peut sembler désolidarisé du personnage au
moment où toute l'attitude paraît gelée. Le silence précédent 32–32,5 s
n'est pas en cause et doit rester intact.

Correction locale proposée : amorcer un souffle visible à 32,750 s, poser
un minuscule relâchement du haut du corps ou de la bouche vers 32,833 s,
puis se stabiliser avant 33,083 s. Le maximum audio actuel est à 0,58 image
de ce repère. Garder les moufles attachées et l'attitude de déception ;
ne pas lancer encore la présentation fière des mains.

## Accents qui ne justifient pas de déplacement arbitraire

| Cue | Début / pic d'énergie | Observation et conclusion |
| --- | --- | --- |
| Hésitation |21,980 /22,033 s | Le bras est suspendu et les yeux vers la cuillère ; le murmure nasal prévu peut accompagner cet arrêt, même sans bouche ouverte. Aucun retard matériel prouvé. |
| Choc |31,760 /31,865 s | La bouche s'ouvre 31,667–31,833 et l'extrême corporel s'expose 31,833–31,958. Le pic vocal tombe dans cet extrême. Conserver cet ancrage. |
| Satisfaction |35,150 /35,163 s | Sourire en formation 34,70–35,25, redressement corporel et mains déjà présentées. Le cue ponctue la satisfaction, pas encore le regard public 36,15. Garder cette intention ou l'ancrer sur le futur geste corrigé, sans le confondre avec un haussement résigné. |

## Règle utile pour la bibliothèque sonore

Pour chaque proposition conserver l'intention, le mode oral/nasal/soufflé,
la durée, le début d'énergie réellement mesuré et son pic. Définir un repère
visuel précis — ouverture, arrêt, effort, relâchement — puis calculer
`début du cue = repère visuel − temps du pic dans le WAV`. Les pics actuels
surviennent de 13 à 105 ms après le début des fichiers : aligner seulement
les noms ou les débuts ne produit pas automatiquement le même couplage.

Les variantes doivent être auditionnées séparément puis avec leur geste.
Aucune étiquette « surprise » ou « satisfaction » n'est une preuve d'émotion
reconnue ; les trois usages du même asset « ooh » transformé ne suffisent pas
à valider l'identité vocale ou la variété d'une bibliothèque. Les niveaux,
la musique V27 et les bruitages physiques n'ont pas à être changés pour
corriger les deux couplages ci-dessus.
