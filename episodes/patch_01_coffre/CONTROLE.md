# Bilan — PATCH / Le coffre à concentration

Livrables : vingt secondes, 1080 × 1920, 24 images/s, film avec son et version
muette partageant exactement le même flux vidéo. Quatre plans, un compte à
rebours réel de dix secondes et une feuille qui reste vierge.

Le scénario choisi a été critiqué avant fabrication. Le rig et ses poses ont
été examinés, puis l'animatique complète a conduit aux corrections suivantes :
masquer le bas du hoodie par le bureau, séparer la patte initiale du téléphone,
mettre le couvercle ouvert derrière l'insertion, retirer la patte du crayon
après dépôt et dégager le minuteur après appui. Le gag et sa durée restent
conservés. Le [journal](developpement/corrections.md) et la
[critique du vrai montage](controle/critique_finale.md) gardent ces étapes.

La [QA indépendante](controle/QA.md) passe seize contrôles ciblés : 480 états
SVG, compteur et prises, continuité des relâchements, pattes/manches réellement
jointes, téléphone caché sous le couvercle fermé, papier sans marques. Douze
images décodées correspondent à de nouveaux rendus indépendants du cache.
Les six références protégées gardent leurs empreintes.

L'archive extraite dans un dossier séparé permet de reconstruire les480PNG
et leWAV à l'identique, sans ancien rig ni cache ni réseau. L'identité binaire
des fichiersMP4 n'est pas garantie par l'encodage ; ce point est distingué
des images et duPCM dans `controle/reproduction.json`.

Le WAV contient vingt secondes en stéréo48kHz. Les quatorze cues concordent
avec la banque et les stems, sans saturation. Le mix est fixe et sans musique
ou voix. Les Foley sont des extraits de bibliothèque CC0 documentés, pas des
captations réalisées pour cet épisode ; les deux signaux UI sont originaux.
Les dernières secondes gardent un espace calme pour la feuille vide.

**Limite d'écoute :** aucune audition réelle n'a été possible dans cet
environnement. La synchronisation et les niveaux sont contrôlés ; le confort
du mix et son adéquation perceptive nécessitent une écoute humaine. Ces
contrôles ne préjugent ni du succès du gag ni d'une cadence hebdomadaire.

SHA-256 du film avec son :
`bf3c7c558067c97f005db2c01fc6b44a234411581184caf07626ccdb147c9dae`.

SHA-256 de la version muette :
`ef7ff3d1c5d677b6fc92867e2b2a0ee3b10865451a2756032c57b6577969ef00`.
