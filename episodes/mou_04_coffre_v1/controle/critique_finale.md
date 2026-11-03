# Critique du montage MOU — Le coffre

**Avis final : favorable à la livraison du remplacement de Patchy par le
MOU original.** Le MP4 HD `84ead5b0…a26ecb0` a été contrôlé après les
corrections ci-dessous. Aucun défaut visuel bloquant n'est retenu dans les
plans examinés. Cet avis porte sur l'image, la lisibilité des actions et
la fidélité au modèle ; il ne vaut pas audition du mix ni garantie de
réception comique auprès du public.

## Première planche effectivement examinée

La planche privée `work/rig/planche_12.png` a été ouverte : 0 / 1,7 / 2,8 /
3,9 / 7,3 / 13,5 / 16,8 / 18 / 19,3 / 23,3 / 25,3 / 28,5 s. Les images
19,3 et 25,3 s ont aussi été ouvertes en grand. Cette première intégration
montre bien le MOU original : corps vert asymétrique, grands yeux blancs,
deux bras et pieds prune, sans oreilles, nez, queue ou vêtement du raton.
Le sourire et les deux petits pieds de la joie restent lisibles.

Trois points sont adressés avant la revue du montage :

- À 13,5 s, la fermeture des yeux donne des ovales verts vides et l'appui de
  joue est un crochet de bras éloigné du visage. Revoir l'arc de clignement
  et la courbe/contact de cette moufle avec la joue réelle de MOU.
- À 23,3 s, la largeur de l'œil MOU dépasse le bord gauche du gros plan.
  Desserrer ou déplacer le cadrage en gardant aussi le LCD lisible.
- Les petits replis internes des moufles à 19,3 et 25,3 s sont signalés au
  spécialiste pour vérifier qu'ils restent des contours simples, sans boucle
  de ruban replié ni seconde extrémité de main suggérée.

Les contacts voulus sur le couvercle et le téléphone ne sont pas assimilés
automatiquement à des collisions. Les points ci-dessus sont examinés dans
la version de travail et ne sont pas un avis sur le futur film corrigé.

## Contact du bouton adapté au bout natif de MOU

Les gros plans `work/placement/button_detail.png` puis
`button_corrected_detail.png` ont été ouverts. La cible héritée x690
laissait un espace réel entre le bout arrondi de MOU et le bouton, malgré
des coordonnées de prise conservées. La cible x715 fait toucher le bord
gauche du bouton par la moufle sans recouvrir le LCD. Ce contact doit encore
être contrôlé dans les images du MP4 autour de 3,875–4 s et au retrait.

## État de la revue

La planche `work/rig/planche_12_corrigee.png` a ensuite été ouverte, avec les
détails 19,3 et 25,3 s en grand. Les paupières fermées sont des arcs nets ;
la moufle d'appui et les contours des prises ne présentent plus les petits
crochets signalés. Le gros plan est desserré : les deux yeux et le LCD sont
lisibles. MOU conserve sa silhouette, sa bouche sans nez et les deux pieds
sombres dans la joie ; les deux moufles partagent le téléphone de façon
plausible. Aucun nouveau défaut n'est retenu sur ces poses.

**Avis intermédiaire : favorable au passage à l'animatique.** Ce constat ne
valide pas encore les transitions ou le MP4. La prerevue et ses points de
contrôle sont conservés dans `developpement/critique_avant.md`.

Aucune audition ni qualité perçue du son n'est revendiquée.

## Première animatique réellement décodée

Fichier `MOU_Le_coffre_animatique.mp4`, SHA256
`5fdd3dd5959e227007e84fb56e9973fb27f453a83052f0fa721485ce1c433440`,
30 s, 720 images à 24 ips, 540 × 960. Le film est décodé en 720 PNG ;
douze planches ont été ouvertes, couvrant toute la chronologie à 0,25 s
et les fenêtres de dépôt, bouton, reprise, appui, plan bas, joie et fin.
Quatre images du film sont ouvertes en grand : f94 (bouton), f324 (yeux
fermés/appui), f559 (coffre/visage) et f596 (anticipation de joie).

La silhouette de MOU, ses yeux, les ouvertures de bouche, les petits pieds
et les prises utiles sont présents dans le vrai film. Les arcs fermés ne
forment plus des lentilles vertes. Le bouton est réellement atteint et le
LCD reste dégagé dans les images examinées. Le cadre visage/coffre conserve
les deux yeux et l'affichage. Le petit récit se termine toujours par les
trois cases vides puis MOU absorbé par son téléphone.

Une dernière anomalie réelle apparaît dans la transition vers la joie,
vers 24,75–24,92 s : la moufle gauche libre porte un petit triangle/boucle
prune intérieur, clairement visible à f596 (24,833 s). La pose tenue à
25,3 s, propre, ne suffisait pas à contrôler ce passage. Le contrôle du
coude et la tangente terminale doivent être redressés avant la prise
bilatérale, en gardant le contact et une moufle continue ; cacher le petit
trait avec un masque ne corrigerait pas la courbe de bras.

Le coordinateur signale aussi un petit débordement de la main au-dessus
de la façade au début de l'ouverture (23–23,25 s) et élargit son masquage
par la façade. Cette retouche et le triangle doivent être revus sur un
nouveau MP4 avant l'avis de passage au HD. Aucun autre nouveau défaut n'est
retenu sur les portions examinées. Les preuves restent privées sous
`work/critique/preview/`.

## Ajustements du plan visage/coffre

L'élargissement du cadre a aussi nécessité de reposer le coffre sur le
bureau : son ancien décalage vertical le laissait au-dessus du plateau.
Le décalage est ajusté pour que sa base rejoigne le plateau, et mains/
téléphone reçoivent le même placement de contact. Les gros plans source
23,167 et 24,6 s ont été ouverts après cette correction.

Le premier montage portant cette retouche, SHA256
`d5f72401932535766cb2dd5b0beb932b2d3cf7743d90aabec220a4138d4fb6ae`,
a été décodé sur les 53 images consécutives f552–604. Le contour de la
moufle libre est corrigé, mais à 23,167 s le début du bras droit apparaît
encore coupé au milieu du panneau : le déport latéral hérité place son
épaule derrière le coffre. Un test privé de quatre poses a vérifié qu'annuler
seulement ce déport latéral dans le plan rapproché relie réellement le bras
au corps, sans déplacer la cible de prise, le téléphone ou le coffre. Les
deux yeux restent entiers ; le blanc de l'œil gauche débute vers x42 sur
les quatre rendus 1080 examinés. Le coordinateur intègre ce réglage de pose.

## Animatique corrigée : avis de passage au HD

La nouvelle animatique réellement encodée, SHA256
`ecc8eab5ad766f58d9ab579a04e0daa44aa9a6682cde937b3278a78cfe6aa008`,
a été décodée sur les **53 images consécutives f552–604** (23–25,167 s).
Les trois planches ont été ouvertes, puis f556, f590 et f596 en grand,
depuis ce MP4 et non depuis un rendu SVG de contrôle. L'identifiant et la
liste des images sont conservés dans `work/critique/preview_join/evidence.json`.

À f556 (23,167 s), le bras droit part maintenant du flanc réel de MOU et
rejoint la paume posée sur le panneau : il ne commence plus comme une bande
coupée dans le couvercle. La façade masque la partie qui passe derrière
elle sans rogner les chiffres. La base du coffre repose sur le bureau.
Les deux yeux restent entiers dans ce plan. À f590 (24,583 s), la prise du
téléphone est lisible ; à f596 (24,833 s), la moufle libre a un contour
arrondi simple. Le passage aux deux mains puis au saut garde les petits
pieds distincts. Aucun autre problème réel n'est retenu dans ces fenêtres.

**Avis : favorable au rendu HD de cette source corrigée.** Les autres plans
de l'animatique n'ont pas été modifiés depuis la revue complète précédente.
Le MP4 HD devra encore être décodé et contrôlé ; aucune audition du son
n'est revendiquée.

## Contrôle du MP4 HD livré

Fichier réellement décodé : `MOU_Le_coffre.mp4`, SHA256
`84ead5b0f9fd99db277db6bdb9ed1f61ad51318ec6651ae124aa63390a26ecb0`.
Le conteneur confirme 30 s, H.264 1080 × 1920, 720 images à 24 ips et une
piste AAC stéréo 48 kHz de 30 s. Les **45 images choisies ont été décodées
à leur taille native**, puis ouvertes dans deux planches. Cinq images ont
également été ouvertes en grand : f94, f556, f596, f607 et f685.
L'identifiant, les indices exacts et les métadonnées restent conservés dans
`work/critique/hd/evidence.json`. Cette revue ciblée complète la lecture
chronologique de l'animatique antérieure ; les producteurs sont restés
gelés depuis l'approbation de la dernière animatique.

Constats sur le film, et non sur de simples coordonnées de prise :

- 1,667–3,917 s : dépôt, fermeture et pression du bouton restent lisibles.
  À f94, la moufle arrondie touche le bouton et dégage l'affichage.
- 13,5 et 19,333 s : l'attente utilise des paupières et des appuis de moufles
  reconnaissables. Les petits crochets de la première version sont corrigés.
- 23–23,792 s : les vingt images consécutives de l'ouverture confirment le
  bras relié au corps, la paume sur le panneau, le LCD non recouvert, les
  deux yeux entiers et le coffre posé sur le bureau.
- 24,583–25,167 s : reprise du téléphone puis passage de la main libre à la
  prise bilatérale. Les treize images consécutives f592–604 confirment la
  suppression du triangle interne. La joie à f607 laisse deux petits pieds
  distincts, deux moufles et un sourire lisible.
- 27,083 et 28,542 s : les trois cases non cochées sont montrées, puis MOU
  est absorbé par le téléphone. La chute conserve le contraste entre sa
  joie d'avoir récupéré l'appareil et le travail resté vide.

La silhouette vert citron asymétrique, les deux grands yeux blancs, les
bras à bouts arrondis et les petits pieds prune identifient bien le MOU
original. Aucun nez, oreille, queue ou vêtement de Patchy n'est présent.
Le remplacement reste dans le scénario et la mise en scène existants.

**Conclusion du contrôle visuel : remplacement validé pour livraison de
ce MP4 HD.** Les anomalies relevées pendant la fabrication ont une
correction observée dans le film livré. Aucun défaut supplémentaire n'est
inventé pour prolonger la liste. Aucune audition n'a été effectuée et aucun
jugement de qualité perçue des sons n'est revendiqué.
