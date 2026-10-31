# Contrôles — Galet en cuisine

Épisode de **38 s, 1080 × 1920, 24 images/s**, avec son et version muette.
Le nouveau personnage sélectionné conserve sa forme, sa palette et ses deux
moufles flottantes. Les anciens épisodes et le prototype de cinq secondes
restent protégés.

## Corrections retenues après les revues

- Repos des moufles détaché du corps, sans les poser sur le rouleau.
- Même contour de moufle au lavabo, plus petit dans cet insert : ouvrir,
  frotter les bouts sous le jet et fermer manuellement.
- Dernier petit papier rapproché de la gauche : véritable contact pendant
  l'essuyage et froissage qui repart de cette pose sans saut.
- Fin : deux moufles abaissées derrière le comptoir, puis levées une après
  l'autre après les regards. Le repas noir reste dégagé. Sourire de fierté
  après les inspections, deux éclats brefs, puis tenue silencieuse.

L'animatique complète a été revue sur 127 images distinctes, puis la nouvelle
fin sur 29 autres. Une dernière revue de 14 images réellement décodées du HD
n'a identifié aucune nouvelle réserve dans les passages examinés. Les rapports
de scénario, d'animatique et de final sont conservés séparément.

## QA indépendante passée

- 912 SVG contrôlés : identifiants, masques, deux moufles sans bras, une seule
  au lavabo ; contours du nouveau galet et costume conservés.
- Aucun recouvrement des yeux ou de la bouche par les moufles dans le contrôle
  des masques à 270 px ; 46 images HD comparées à CairoSVG frais sans cache.
  Erreurs RGB moyennes maximales : 1,627/255 globale et 2,830/255 sur les moufles.
- Douze prises d'outils et quinze contacts papier vérifiés sur silhouettes.
  Les deux coupes ont de vrais contacts de lame. La petite feuille touche
  les deux mains à l'essuyage final.
- Quatre inserts lavabo : contacts bout/levier, paume hors du jet ; environ
  12 à 13 % de la surface de la moufle intersecte le jet au rinçage.
- Rouleau réellement aminci, anciennes boules persistantes, dernier papier
  au sol ; dix-huit dernières poses identiques, vapeur encore animée.
- Flux H.264 des versions son et muette identiques. Sources, nouveau modèle,
  prototype et archives MOU contrôlés avant/après sans modification.

Détails et empreintes : `controle/QA.json` et `controle/QA.md`.

## Son et limites de contrôle

58 cues, trois stems, WAV stéréo 48 kHz de 1 824 000 échantillons. La somme
reconstruite reproduit le mix exactement. Aucun écrêtage ; corrélation AAC/WAV
sans décalage : 0,996963219. Vingt-neuf repères énergétiques vérifiés. Les huit
accents d'essuyage suivent les maxima mesurés sur les vraies trajectoires.

Jazz abaissé de 1,5 dB par gain fixe, aucune normalisation par scène ; sifflement
seulement au départ, aucun nouveau vocal. Silences exacts 32–32,5 s et 37,25–38 s.
Les anciennes matières, leurs procédés et leurs licences sont documentés.

Le modèle ne peut pas écouter dans cet environnement. Ces mesures ne valident
ni naturel des bruitages, ni équilibre perçu sur téléphone, ni jeu reconnu par
un public. Les revues par images successives ne sont pas une lecture continue.
L'avis interne et la QA ne constituent pas l'approbation artistique de
l'utilisatrice, une qualité professionnelle certifiée ou un succès de chaîne.

## Sources portables

Le ZIP contient le décor, les dessins et gestes Python/SVG, les polices,
les entrées audio, la partition et les crédits. Les MP4 et les caches restent
séparés. Le contrôle à froid du ZIP est consigné dans
`controle/audit_archive.json`, en dehors du ZIP pour éviter une empreinte circulaire.
La protection des anciennes archives se contrôle dans le dépôt complet ; elles
ne sont pas nécessaires pour refaire les images et le mix du nouvel épisode.
