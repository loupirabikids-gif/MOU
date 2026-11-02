# Correctif local — mains et téléphone

Retour utilisateur : défauts lorsque PATCH pose et prend le téléphone.
Les contrôles antérieurs des centres et prises n'avaient pas détecté les
changements instantanés de rotation/grip. Le diagnostic porte cette fois
sur les images consécutives du véritable MP4V4.

Défauts observés :

- 2,7917→2,8333 s : poignet proche de−90° puis−5° au lâcher, ouverture du pouce
en une image. Le téléphone lui-même reste continu.
- 24,0417→24,0833 s : bascule inverse de la patte lors de la reprise et fermeture
instantanée de la prise.
- 24,6667→24,7083 s : face écran orange puis dos graphite à la coupe, sans
retournement montré.

Corrections : serrage progressif à la première prise sur le bureau ; pose
tenue de2,8à2,92s ; ouverture de la patte et retrait progressifs ; orientation
de la paume avant la reprise24,05s. Le couvercle se ferme après retrait de
la main, de3,20à3,55s, avec son signal final inchangé. Le retournement a lieu
de24,35à24,65s, avec une image sur tranche à24,5s, puis le dos avant la coupe.

Le booléen de dégagement du téléphone n'est pas modifié : il basculait déjà
après franchissement du bord du coffre. L'ordre de dessin reste désormais
manche→téléphone dans l'ouverture→façade→téléphone dégagé→paumes, ce qui
conserve son rapport de profondeur avec la manche.

Le rig, les vues, les cadrages, le saut, le final et le son sont conservés.
La variante est distincte de laV4, dont les fichiers ne sont pas écrasés.
Une comparaison de tous lesPNG vérifie l'invariance hors fenêtres locales.
