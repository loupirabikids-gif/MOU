# Galet v1 — contrôle indépendant du HD

31 octobre 2026. **Contrôle technique passé** sur
`Galet_miette_muette.mp4` : cinq secondes, 1080 × 1920, 24 images/s,
120 images H.264, aucune piste audio. Décodage complet sans erreur.
SHA256 : `30bff6dcabcbe97ae6d6cc7346e0a7cacb80c257b6dcc16004641f420d57631e`.

## Structure et stabilité

Les 120 SVG émis ont été examinés : deux moufles flottantes, deux pieds,
deux yeux et deux pupilles identifiés ; références de masques présentes,
identifiants uniques et aucun bras ajouté. Les positions et transformations
des pieds restent constantes. L'échelle des deux moufles reste constante ;
le changement de forme du pouce n'est pas assimilé à un changement d'échelle.
Les douze images finales du personnage et de la miette sont tenues exactement
dans le SVG, de 4,50 à 5,00 s.

Les empreintes du gel des producteurs et de la police ont été vérifiées avant
et après le contrôle. Le rig MOU historique et le film V28 sont inchangés.

## Contact et transfert réellement mesurés

Les silhouettes de la miette et de chaque moufle ont été isolées depuis les
vrais SVG puis rasterisées à 1080 × 1920. Aucun booléen de réussite de
l'animation n'a servi de preuve du contact.

- Neuf repères contrôlés entre 0 et 4,50 s : la distance entre la miette et sa
  moufle porteuse est toujours de 0 pixel, leurs silhouettes étant en contact.
- À 1,25 / 1,50 / 1,583 s, les deux moufles touchent la miette. Après retrait,
  à 2,167 s, elle touche seulement la droite et se trouve à plus de 526 px
  de la silhouette gauche.
- Un seul changement de parent, à 1,60 s : la géométrie SVG de la miette n'a
  aucun saut de position ou d'orientation mesuré entre les instants situés
  une microseconde avant et après ce changement.
- La miette mesure environ 29–32 px dans ces repères HD. Cela respecte la
  cible de taille du découpage ; cette mesure ne garantit pas sa lisibilité
  pour tous les spectateurs.

## Comparaison du fichier encodé

Quatorze images réelles du MP4 ont été comparées à des rendus CairoSVG frais,
sans cache. Elles couvrent l'approche, le contact, les deux côtés du transfert,
le retrait, le constat et la dernière pose, notamment les anciens passages
gênants devant les yeux à 0,958 et 1,875 s.

Erreur RGB moyenne maximale : 1,506/255 sur l'image entière et 2,864/255 sur
les silhouettes mains/miette. Aucun échec de comparaison. À ces quatorze
repères, aucun pixel des pupilles ne sort de l'ouverture des yeux ; les mains
et la miette ne recouvrent aucun pixel de ces ouvertures.

Rapport détaillé : `QA.json`. Commande de reproduction depuis le dépôt :

```sh
.venv/bin/python -B personnages/galet_v1/controle/verify.py \
  --contract personnages/galet_v1/controle/contrat_QA.json
```

Ces résultats portent sur la géométrie, les pixels et l'encodage. Ils ne
constituent ni écoute, ni visionnage continu, ni reconnaissance émotionnelle
par un public, ni approbation artistique de l'utilisatrice. La critique des
images et du jeu est conservée séparément.
