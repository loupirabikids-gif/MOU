# Critique indépendante — costume et chute V20

Critique : agent `critique_chef_v20`. Périmètre limité à la nouvelle toque,
au tablier de taille et à la fin où le papier tombe au sol. Aucun fichier
de fabrication modifié par le critique.

## Avant fabrication

Référence visuelle réellement examinée :
`episodes/03/etudes_costume/chef_v1/MOU_chef_validation.png`, image approuvée
par l’utilisatrice. Toque crème portant « MOU », tablier corail à la taille,
sans bavette ni bretelles. Le rig et ses deux bras/moufles restent la référence.

Le nouveau contraste comique fonctionne sur le principe : mains impeccables,
sol sali par le dernier papier. La fierté finale de MOU peut rester inchangée,
puisqu’il ne remarque pas ce qu’il vient de faire tomber.

La proposition conserve 41 s : dernier lâcher à 38,65 s, contact avec le tas
à 39,1 s, arrivée au sol vers 39,85 s, stabilisation vers 40 s, gros plan
jusqu’à 40,25 s puis retour à MOU. Le temps de chute et la pause au sol
semblent suffisants à ce stade ; il faut le vérifier sur le montage produit.

Point à garantir au rendu : le petit papier doit toucher le sommet du tas,
puis changer clairement de direction sur au moins deux images du final.
Une trajectoire qui passe seulement près de la poubelle ferait lire un tir
raté plutôt qu’une conséquence de son remplissage. Les quatre grosses
boulettes doivent rester dans la poubelle et la petite rester au sol.

## Revue de l’animatique produite

Éléments réellement vus : `controle/planche_animatique.png`, couvrant les
41 s du montage, `controle/animatique_chute_planche.png`, succession de douze
images extraites du vrai MP4 entre 38,75 et 40,75 s, et les extractions
`animatique_chef.png`, `animatique_lavabo.png`, `animatique_final.png`.
Le fichier examiné est `MOU_Encore_une_feuille_animatique.mp4`, 540 × 960,
12 images/s. Examen visuel par images extraites, pas lecture sonore.

- **Costume, ouverture et plans de cuisine : favorable.** La toque garde
  son inscription lisible et sa place sur la tête. Le tablier est bien limité
  à la taille ; le nouveau costume correspond à la maquette validée. Les deux
  bras et moufles restent visibles, le visage est dégagé, le décor reste
  lisible. Aucun défaut nouveau de raccord observé dans les images examinées.
- **Lavabo : favorable.** Le gros plan conserve le robinet et une seule
  moufle à pouce arrondi, sans visage ou vêtement ajouté dans l’insert.
- **39,083 s, contact du tas : favorable.** La petite boulette rejoint le
  sommet visible du tas qui dépasse de la poubelle. Son changement de
  direction dans les images suivantes donne une cause visible à sa chute.
  Elle ne disparaît pas dans la poubelle.
- **39,167–40,167 s : favorable.** La petite boulette repart vers la droite,
  descend, rejoint le sol et reste séparée de la poubelle dans le gros plan.
  Les quatre grosses boulettes demeurent à leur place. Le cadrage contient
  le tas, la trajectoire et le résultat au sol ; la tenue permet de le lire.
- **40,25–41 s : favorable.** Le retour au large conserve le papier au sol.
  MOU admire sa main propre sans remarquer le déchet : la fierté devient
  ironique par rapport au résultat que le spectateur vient de voir.

## Défaut retenu au recontrôle

La QA indépendante a signalé un défaut de cadrage que la première lecture
de la planche n’avait pas relevé. Examen supplémentaire de la vraie image
`animatique_chute_0467.png`, à **38,917 s** : le petit papier passe presque
entièrement hors cadre en haut pendant l’approche. Il ne reste qu’une petite
partie au bord supérieur. Le spectateur peut perdre le suivi du dernier papier
avant son contact avec le tas.

Correction concrète retenue par le coordinateur : élargir seulement le dernier
zoom, maximum **2,5** au lieu de 2,8, avec centre final **(220, 1536)** au lieu
de (200, 1575). Ce centre garde le viewBox à l’intérieur du décor. La
trajectoire, les bras, le costume et le son restent inchangés. Les autres
zooms gardent leurs paramètres précédents.

## Revue de l’animatique recadrée

Les preuves ont été extraites à nouveau du MP4 corrigé. La nouvelle
`animatique_chute_planche.png` et les images
`animatique_contact_0467.png` (38,917 s), `animatique_contact_0469.png`
(39,083 s), `animatique_contact_0481.png` (40,083 s) ont été réellement vues.
Les anciennes extractions de la première version ont été retirées par le
coordinateur pour éviter toute confusion.

- À **38,917 s**, la petite boulette est maintenant entièrement visible,
  avec une marge nette au-dessus. La perte de suivi identifiée est corrigée.
- Le contact avec le tas, le rebond puis la descente restent contenus dans
  le même cadre. Aucune marge transparente ou bande noire visible.
- À **40,083 s**, le papier reste distinct au sol ; la poubelle pleine est
  encore visible en entier. La pause et le retour au large conservent la
  compréhension du résultat.

**Verdict actualisé : favorable au rendu final.** Restent à contrôler les
images du MP4 final, notamment l’approche et les deux images de contact à
24 images/s. Aucun avis perceptif sur le son : l’équilibre musical n’a pas
été écouté par le critique.

## Revue de l’export final et gel du rapport

Preuves réellement examinées après export en 1080 × 1920, 24 images/s :
`final_chute_planche.png`, `final_contact_0934.png` (38,9167 s),
`final_contact_0938.png` (39,0833 s), `final_contact_0939.png` (39,125 s),
`final_chef.png`, `final_lavabo.png` et `final_final.png`, toutes extraites
du MP4 final `MOU_Encore_une_feuille.mp4`.

L’approche est entière dans le cadre corrigé. Les deux images consécutives
938 et 939 montrent le petit papier en contact avec le sommet du tas, sans
interruption de sa présence. La succession finale montre ensuite le rebond,
la descente et le papier posé au sol. Le retour au large maintient ce papier
à la même place et la fierté de MOU envers sa main propre. La toque et le
tablier correspondent à l’étude approuvée ; l’insert du lavabo conserve sa
main seule. Aucun autre défaut réel observé sur ces preuves finales.

**Verdict final : favorable à la livraison. Rapport gelé après cette revue.**
La correction de cadrage identifiée a été vérifiée sur les images du vrai MP4,
et pas seulement sur un rendu SVG ou le code. La revue demeure un examen visuel
par images extraites ; elle ne constitue pas une écoute ni un test de
compréhension auprès d’un public.

Dernier recontrôle après réencodage technique de l’**export définitif CRF8**,
sans changement des 984 PNG ni du WAV : les images réelles
`final_contact_0934.png`, `final_contact_0938.png`,
`final_contact_0939.png` et `final_chef.png` ont été vues à nouveau.
L’approche reste entièrement cadrée, les deux contacts restent lisibles et le
costume reste conforme. Avis favorable confirmé, aucun changement créatif
supplémentaire demandé. MP4 examiné identifié par `final_proofs.json` :
SHA256 `b4a05afccbeb4441f0f819b82b5efe29cacce9854173773c23abeee216db3342`.
Rapport gelé pour archivage après ce recontrôle.
