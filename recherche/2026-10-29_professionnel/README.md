# MOU — recherche et essais de réalisation

Recherche du **29 octobre 2026**, pour améliorer l’épisode de cuisine après
le rejet de la V21. Les rapports distinguent les sources consultées, les
essais réellement exécutés et les choix artistiques proposés.

La décision de production est de **garder le rig et le rendu CairoSVG**, qui
respectent les contours et les masques de MOU, puis de préparer le jeu par
poses, regards, pauses et coupes de caméra. Les logiciels testés donnent des
moyens de régler ces éléments ; ils ne choisissent pas une bonne réaction.

## Outils utiles et niveau de preuve

| Outil libre | Utilité pour MOU | Résultat de cette recherche |
| --- | --- | --- |
| [Blender](https://github.com/blender/blender), [GPL](https://github.com/blender/blender/blob/main/COPYING) | Caméra orthographique, clés, pauses et compositing. | Deux imports SVG et un plan d’image ont été réellement rendus. Les imports automatiques altèrent les masques ou les contours ; le plan d’image issu de CairoSVG conserve le dessin. Le `.blend` fourni est un essai de caméra, pas un épisode transféré. |
| [RaveAnima](https://github.com/vibecoderkz/raveanima), [MIT](https://github.com/vibecoderkz/raveanima/blob/main/LICENSE) | Animation pilotée par code, poses tenues, interpolation et export MP4. | Version 0.2.0 réellement exécutée : maintien, déplacement et export de 36 images. L’import a demandé la reconstruction explicite de trois masques. Aucun nouveau jeu expressif de MOU n’a été validé avec ce moteur. |
| [Friction](https://github.com/friction2d/friction), [GPL-3.0-only](https://github.com/friction2d/friction/blob/main/LICENSE.md) | Flipbook de poses, morphing vectoriel et courbes. | Documentation et licence lues ; pas de migration ni d’essai de production. La méthode de poses affichées et tenues est applicable dans notre chaîne actuelle. |
| [OpenToonz](https://github.com/opentoonz/opentoonz), [BSD-3-Clause](https://github.com/opentoonz/opentoonz/blob/master/LICENSE.txt) | Xsheet, durée d’exposition des poses et courbes Constant/Step. | Documentation et licence lues ; pas de nouveau rig créé. La feuille d’exposition sert à calculer les pauses avant de fabriquer les transitions. |
| [Audacity](https://github.com/audacity/audacity), [GPL-3.0](https://github.com/audacity/audacity/blob/master/LICENSE.txt), et [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Édition des sons, enveloppes, filtrage et mesures. | Sources et documentation consultées. Les filtres et mesures FFmpeg sont réellement employés dans les essais et le mix V22 ; aucune écoute humaine n’est remplacée par ces chiffres. |

Les [comparaisons Blender et les essais RaveAnima](outils/rapport.md)
comprennent images, scripts, versions et preuves d’accès.

## Application dans l’épisode

La [V22](../../episodes/03/cuisine_v22/README.md) reprend les dessins et les
deux bras/moufles existants. Sa fin de huit secondes sépare la cause, le regard,
la solution, le contact main/tissu, la découverte de la poubelle et la réaction
au public. Elle utilise six cadrages pour cinq temps narratifs. Le corps reste
stable ; la caméra de détail dégage le geste sur le tablier. La dernière pose
est tenue pendant seize images à 24 images/s.

Le mix retire 25 couches de premier plan, garde une seule eau et adoucit les
attaques du papier et du couteau. Le jazz suit une grille continue, avec une
baisse légère et progressive au lavage. Le gain de livraison est commun au
film entier. Le [rapport son](son/rapport.md) expose le diagnostic V21 ; la
[recette V22](../../episodes/03/cuisine_v22/developpement/son_v22.md) décrit
les traitements effectivement retenus et leur régénération.

Deux textures CC0 ont aussi été vérifiées dans
[CC0-Public-Domain-Sounds](https://github.com/lavenderdotpet/CC0-Public-Domain-Sounds)
avec leurs notices et empreintes. Elles restent des essais de recherche :
une page tournée ou un tap de couteau ne reproduisent pas automatiquement
une déchirure d’essuie-tout ou une coupe de carotte.

## Référence Oggy et limites

Les accès officiels à [Xilam](https://xilam.com/en/media/oggy-and-the-cockroaches/)
et à la [chaîne Oggy](https://www.youtube.com/@oggy/videos) ont répondu **403**.
Aucun épisode n’a donc été vu ni écouté dans cette recherche. Les durées de
pause et les cadrages proposés pour MOU ne sont pas présentés comme des mesures
relevées dans Oggy. Le [rapport de mise en scène](oggy/rapport.md) conserve
les tentatives d’accès et les documents techniques réellement consultés.

Le modèle ne peut pas écouter le mix dans cette session. Les mesures établissent
des niveaux et une continuité de fabrication ; elles ne certifient ni le confort
sur téléphone ni une animation professionnelle. Les critiques du montage restent
conservées dans le [dossier d’étude](../../episodes/03/developpement/etude_professionnelle/).
