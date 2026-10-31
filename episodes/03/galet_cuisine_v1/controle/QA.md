# QA indépendante finale — passée

31 octobre 2026. Contrôle du film HD et de sa version muette, après gel visuel et
sonore annoncé par le coordinateur. **38 s, 1080 × 1920, 24 images/s, 912 images.**

Film son SHA256 :
`91fd95643cbec9f94a2dcbdd6630d9463b9c8f6c4538f1576f07983f2a045296`.
Version muette :
`a77ab0878fb6f0cf83a0f4395fb4e1ac4e3c151d1e5c2025254238620ff2ae8f`.

## Dessin, gestes et matière

- 912 SVG analysés : identifiants et masques valides ; deux moufles flottantes
  hors lavabo, une seule au lavabo, aucun bras, deux pieds et costume présents
  dans les scènes du personnage. La copie du dessin sélectionné et sa palette
  sont identiques aux sources du prototype Galet.
- 744 états hors lavabo contrôlés par masques à 270 px de large : aucun
  recouvrement des ouvertures d'yeux ou du trait de bouche par les moufles.
  Un composant situé hors cadre n'est pas traité comme un visage visible.
- Douze contrôles de prises : cuillère, manche de couteau, soutien de carotte,
  tomate et sel. Les ventres de lame réels atteignent les lignes de coupe à
  9,40 et 9,98 s. Les émissions de sel partent des vrais points de pouce.
- Quatre inserts lavabo : vrais contacts au levier pendant ouverture et fermeture,
  bouts dans le jet au rinçage et paume hors du jet. Aux quatre repères de rinçage,
  11,97 à 12,80 % de la silhouette de moufle intersecte le jet ; échelle constante.
- Quinze contacts papier mesurés sur les silhouettes émises. La petite feuille
  touche bien les deux moufles au repère d'essuyage 27,0175 s : écart raster 0 px.
  Ce contrôle confirme le correctif du contact, pas chaque instant d'une prise
  devant un public.
- La largeur effectivement dessinée du rouleau suit sa réserve décroissante,
  jusqu'au carton nu. Les géométries des boules déjà déposées persistent dans
  le panier ; le dernier papier reste au sol après sa chute.
- Pieds fixes, échelle des moufles constante. Les 18 dernières poses du corps,
  du visage et des mains sont identiques ; la vapeur conserve 18 états distincts.

## Images réellement encodées

46 images du MP4 son comparées à des rendus CairoSVG frais, sans cache : erreur
RGB moyenne maximale **1,6271/255** pour l'image entière et **2,8305/255** pour
les moufles. Aucun échec d'ouverture de pupille ni bord de caméra transparent
dans ces images. Les deux exports possèdent le même flux vidéo H.264.

## Son : contrôle du signal

WAV 48 kHz stéréo PCM16, 1 824 000 échantillons par canal. Aucun écrêtage.
Les 58 cues livrés et les trois stems reconstituent chacun exactement le mix.
Les sources actives, le générateur et la chronologie correspondent aux empreintes.
Les huit repères d'essuyage proviennent des trajectoires finales ; les 29 cibles
d'énergie annoncées correspondent aux pics RMS mesurés sur les cues écrits.

Corrélation AAC/WAV : **0,996963219**. Six fenêtres ne révèlent aucun glissement
global de la piste. Silences PCM exacts de 32 à 32,5 s et de 37,25 à 38 s.
Sifflements seulement au début, avant 1,732 s ; aucune voix de la banque d'essais
non validée n'est injectée.

## Gel et limites

Producteurs et ressources inchangés pendant le contrôle. Les empreintes du gel,
de l'ancien rig MOU, du premier test Galet et du film cuisine V28 sont conservées.
Le détail reproductible est dans `QA.json` ; le vérificateur est `verify.py`.

Ce sont des contrôles de géométrie, de pixels et de signal. Ils ne certifient
ni une écoute, ni le confort ou le naturel des sons, ni la compréhension des
émotions par un public, ni une qualité professionnelle ou une approbation de
l'utilisatrice. La critique du montage réel reste un rapport distinct.
