# Contrôle indépendant — prototype Blender MOU

Scène ouverte dans un nouveau processus Blender 4.3.2.
Résultat technique : **passed** ; 19 contrôles ciblés.
Périmètre : scène native et MP4 final.

Le personnage est constitué de 96 courbes 2D éditables, avec 4992 clés de forme. Les 4 images emballées sont trois plaques de décor et le lettrage de la toque. Aucun film ou image entière de MOU ne pilote le personnage.

À timeline fixe, passer le poids de pose 54 à 99 déplace ensemble le bras, son ancre et la prise de cuillère. Déplacer le contrôle global translate le personnage et sa cuillère une seule fois. Modifier un point de la clé 54 change réellement le contour évalué. Ces essais restent en mémoire et ne sont pas sauvegardés.

Les 120 états ont été évalués sans erreur de driver ; la coupe de caméra et la visibilité passent au lavabo à l’image 105. Les 22 fichiers de référence, dont les anciens MP4 et le rig original, gardent leurs empreintes.

SHA-256 du `.blend` : `24f2cf8f0c18ab8df817704a3a403272f8b83e00efa65ea8b0e04922385f6378`.

MP4 : `personnages/MOU_blender_v1/MOU_Blender_5s_muet.mp4`.
SHA-256 : `2e29234ec7852c7fadf7e942c41da732357dc4ab1fb38f318bdfe437d22ecf48`.
Le MP4 est décodé à 120 images, 1080 × 1920, 24 ips, 5 s, sans flux audio. Huit images décodées, dont les anciens défauts aux images 77/94/114, sont comparées aux vrais PNG Blender HD correspondants ; les écarts de compression sont détaillés dans le JSON.

Les 17 contrôles initiaux avaient laissé passer des artefacts visibles entre les poses. Ils ne suffisaient donc pas à déclarer le film livrable. Contrôle ajouté : les contours et remplissages de la bouche (76–79), du bras gauche (91–99) et du centre de la paume (111–117) sont comparés localement à vingt rendus du rig SVG natif préservé. Le seuil accepte une enveloppe d’un pixel pour l’anticrénelage ; il rejette effectivement les pointes, replis et trous du premier export, dont les mesures sont conservées dans le JSON. La critique examine aussi le nouvel encodage.

La zone uniforme d’humidité de l’image 114 est également contrôlée pour éviter le grain de pixels de la transparence DITHERED. Ce contrôle porte sur la variance locale, pas sur une égalité gamma exacte entre les mélanges transparents SVG et Blender.

## Limites

La comparaison visuelle des poses et du montage est conservée dans les rapports de critique. Ce contrôle technique ne mesure ni la compréhension du gag ni la qualité comique. Le personnage reste un rig de poses 2D, sans IK. Le film est muet ; aucune écoute n’est revendiquée.

Détails reproductibles : `qa_blender.py` et `QA.json`.
