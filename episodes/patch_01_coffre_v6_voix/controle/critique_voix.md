# Critique indépendante des vocalisations — PATCH V6

## État avant fabrication

La V5 réellement encodée a été examinée aux huit poses clés décrites dans
`developpement/voix_decoupage.md`. Les emplacements retenus sont la décision
après verrouillage, l'appui de joue, la somnolence en bras croisés, la surprise
au déverrouillage et la joie en l'air.

Deux risques concrets sont identifiés avant production : le soupir ne doit
pas devenir une bouche souriante avec des dents, et le bâillement doit se
refermer avant la coupe de 18,4 s puis l'éveil. Le rire ne doit pas entraîner
un mouvement de mains ou de corps qui rompe la prise bilatérale du téléphone.

Le début à 0,6 s a été écarté : notification et prise du téléphone occupent
déjà cette courte séquence. La décision vocale à 4,75 s accompagne plutôt
le retour de Patchy à sa feuille après avoir verrouillé le coffre.

À ce premier stade, les prises vocales, l'animatique et le mix V6 restaient
à examiner. La fabrication et la revue réalisées ensuite sont distinguées
ci-dessous ; aucune audition ou validation du public n'est revendiquée.

## Animatique réellement examinée

Fichier : `PATCH_Le_coffre_V6_voix_animatique.mp4`, SHA256
`c71be55f207f71ad88c093cde43c050b0edd913b90fff747905bbddaddf85ae3`.
104 images uniques ont été décodées du MP4 : fenêtres consécutives autour
des cinq vocalisations et treize repères de raccord. Les six planches
`decision`, `soupir`, `baillement`, `surprise`, `joie`, `raccords` ont été
ouvertes, avec preuve de l'empreinte dans le dossier privé
`work/critique/preview/`.

| Moment | Observation sur les images du MP4 | Effet sur la lecture |
| --- | --- | --- |
| 4,75–5,05 s | Bouche fermée pendant le petit « hm », très léger accent des sourcils ; regard qui revient ensuite vers la feuille | La vocalisation accompagne le choix de se concentrer plutôt que la notification déjà passée |
| 13,10–13,62 s | Petit ovale sombre sous le museau, sans dents, puis retour à la bouche d'ennui ; main toujours sous la joue | Le soupir est associé à une expiration, sans nouveau sourire ni rupture d'appui |
| 17,45–18,29 s | Ouverture ronde progressive, fermeture des yeux près de 18 s, bouche refermée avant la coupe de 18,4 s | Le bâillement appartient à l'assoupissement et ne continue pas pendant l'éveil suivant |
| 23,04–23,28 s | Surprise O dans le plan visage/coffre, déjà visible après la coupe de 23 s ; accent final choisi à 23,2083 s | L'inspiration ne commence pas sur un plan où le personnage est absent ; la prise du couvercle reste distincte |
| 25,05–25,48 s | Téléphone tenu à deux mains et pieds visibles ; deux petites variations de bouche autour des images 603 et 608 | Le rire reste bref et accompagne la joie existante sans ajouter des secousses qui désolidariseraient l'objet |
| 26,65–30 s | Trois cases de travail vides puis Patchy absorbé au téléphone, bouche de contentement fermée | La chute garde son espace sans commentaire vocal supplémentaire |

L'accent de surprise a été ajusté par le coordinateur : de 23,125 s
proposé à **23,2083 s**, pour laisser l'attaque réelle de la prise entièrement
après la coupe de 23 s. Les autres repères proposés sont conservés. Les
fichiers `audio/voice_cues.json` et `sources/voix_gestes.json` documentent les
positions réelles et l'enveloppe mesurée des WAV générés. Cette inspection
confirme la cohérence visuelle des actions aux accents ; elle ne constitue
pas une écoute du caractère ou du niveau perçu des sons.

Le soupir et le bâillement utilisent une bouche de souffle sans dents. Le
petit jeu de bouche n'a pas créé de nouveau chevauchement de mains avec le
coffre dans les repères examinés. Le téléphone reste tenu et son retournement
ainsi que les deux prises restent lisibles. L'horloge revient à 09:30, le
minuteur à 00:00, et la série de regards tardifs n'a pas été réintroduite.

**Décision intermédiaire :** aucune correction visuelle supplémentaire
retenue avant le HD. La revue du fichier HD reste à faire. Le naturel de la
voix, son agrément et l'équilibre perçu du mix restent non évalués ici.

## Fichier HD final réellement examiné

Fichier : `PATCH_Le_coffre_V6_voix.mp4`, SHA256
`f9069b502ca3fccbae72135d2d6b9d166d223a68e745ca9a227dac4b82800d89`.
La même sélection de **104 images uniques** a été décodée du MP4 HD,
puis les six planches ont été ouvertes dans `work/critique/hd/`. Ce nouvel
examen porte sur le film final lui-même, et non uniquement sur les PNG sources.

Les cinq intentions restent placées dans les poses correspondantes. Le
soupir et le bâillement gardent leur bouche de souffle sans dents ; le
bâillement se referme avant la coupe et l'éveil. La surprise reste en bouche O
après le retour du visage à 23 s. Les petits accents de rire restent à
l'intérieur du plan de joie et n'altèrent ni le téléphone entre les deux
moufles, ni les deux pieds en l'air. Les repères d'appui de joue, bras croisés,
plan bas, dépôt et reprise n'ont pas montré de nouvelle collision dans les
images examinées. Les trois cases de travail restent vides.

**Décision finale de critique visuelle :** aucune correction supplémentaire
retenue sur ce fichier HD. Les faits observés sont compatibles avec les
intentions du découpage ; ce constat ne certifie pas la qualité perçue des
vocalisations. Aucun son n'a été écouté par cette critique : le naturel,
la reconnaissance immédiate des émotions, le volume confortable et le
caractère comique à l'oreille restent à apprécier sur le mix et la planche
de voix livrés. Les mesures du mix et de synchronisation sont rapportées
séparément par le contrôleur technique.
