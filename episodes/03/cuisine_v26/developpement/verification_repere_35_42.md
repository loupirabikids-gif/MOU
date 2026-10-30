# Vérification du repère 35–42 s sur V25

30 octobre 2026. Source examinée :
`episodes/03/cuisine_v25/MOU_Encore_une_feuille.mp4`, 43 s, 24 images/s.
Ce document distingue les événements de la version existante du nouveau
découpage en développement. Il ne valide pas ce dernier.

## Vérification effectuée

Lecture de `chronologie.json`, de `sources/jeu_visage.py`, de `sources/music.py`
et du stem `audio/musique_v25.wav`. Extraction et ouverture réelles de 16
images du MP4 entre 35 et 42,5 s. Preuves de travail dans
`work/repere_35_42/planche.png` et `music_39_41.json`.
Il s'agit d'images successives et d'une mesure numérique du son, sans lecture
continue ni écoute revendiquée.

## Instants utiles du film existant

| Temps V25 | Événement vérifié |
| --- | --- |
| 34–35,35 s | Dernier insert lavabo ; eau de 34,24 à 35,22 s. À 35 s, la moufle est donc encore au lavabo. |
| 35,35–36,05 s | Retour cuisine, prise et tirage du dernier papier ; déchirure à 36,05 s. |
| 36,05–36,8 s | Le petit morceau est exposé et la surprise se forme après sa découverte. |
| 36,8–38,1 s | Dernier essuyage ; froissage ensuite de 38,1 à 38,4 s. L'étiquette « essuyage nerveux accéléré » est une interprétation, pas une mesure du jeu. |
| 38,4–39,5 s | Jet ; lâcher à 38,65 s. Le petit papier rencontre le tas déjà débordant vers 39,1 s, avec contact programmé de 39,075 à 39,14 s. |
| 39,1–40 s | Rebond puis chute à côté ; atterrissage source à 39,85 s, stabilisation à 40 s. Boulette bien au sol sur l'image extraite à 39,875 s. Les quatre grandes boulettes restent dans la poubelle ; il n'y a pas d'avalanche générale. |
| 40,25–40,58 s | Retour sur MOU, encore soulagé au départ ; son regard quitte la main propre pour les déchets. |
| 40,58–40,83 s environ | Formation de la surprise et recul du haut du corps. Le visage ouvert est réellement visible à 40,83 s. |
| 41,333 s | Coupe au gros plan. Les yeux reviennent ensuite vers le public, cible frontale atteinte vers 41,708 s. |
| 42,375–43 s | Pose finale tenue ; la plage 35–42 s s'arrête avant cette tenue complète. |

Les nombres de la chronologie sont des instants de commande ; à 24 images/s,
les images réellement montrées sont espacées de 41,67 ms. La précision
« ±0,1 s » de l'analyse automatique n'est donc pas une précision mesurée
pour chacun de ses constats. Les anciens champs historiques `acting_polish`
ne remplacent pas le contrôleur de jeu V25 actuel.

## Pas de coupure musicale nette établie à 40 s

Le stem piano-contrebasse reste numériquement présent entre 39 et 41 s.
Mesures RMS sur fenêtres de 0,5 s :

| Fenêtre | RMS du stem musical |
| --- | --- |
| 39–39,5 s | −45,29 dBFS |
| 39,5–40 s | −51,91 dBFS |
| 40–40,5 s | −39,16 dBFS |
| 40,5–41 s | −38,94 dBFS |

Les très courts passages au zéro numérique relevés entre 39 et 41 s durent
au maximum 2,04 ms ; ils ne constituent pas un arrêt musical de montage.
Le code applique le fondu de fin de 42,4 à 43 s, pas une coupure à 40 s.
SHA-256 du stem mesuré :
`0d9f235c6f9644b0c36de85c4a33fe81d0dee98733451943d5ab749efc0696ac`.

Ces mesures ne prouvent ni la continuité perçue, ni l'agrément du mix. Elles
ne permettent simplement pas de reprendre comme fait « la musique s'arrête
net à 40 s » pour V25. Si l'analyse visait une autre version, son numéro
doit être identifié avant de transporter ses horodatages.

## Conséquence pour le nouveau découpage

Le repère 35–42 s désigne bien une chaîne de causes utile : dernier morceau,
essuyage, jet, contact du tas, chute et découverte de MOU. Conserver cette
construction lisible, sans copier ses secondes ni traiter la réaction seule
comme une chute désormais approuvée. Le repas raté et la présentation fière
des mains forment la nouvelle proposition ; son rythme et son jeu devront
être jugés sur leur propre animatique. Le jazz doux continu reste le choix
de travail ; une éventuelle rupture sonore serait une décision nouvelle.
