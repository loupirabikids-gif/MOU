# Contrôle indépendant V26 — terminé

30 octobre 2026. **Résultat : passé** sur les exports finaux, après gel des
sources de fabrication. Cette vérification technique ne constitue pas une
écoute, une reconnaissance publique des émotions ou une approbation artistique.

## Médias réellement vérifiés

- MP4 avec son et version muette : décodage complet sans erreur, H.264,
  1080 × 1920, 24 images/s, 912 images, 38 secondes.
- Les deux fichiers contiennent exactement le même flux vidéo H.264 compressé.
- Son : AAC stéréo 48 kHz. Corrélation sans décalage avec le WAV courant :
  **0.998070582** ; aucun échantillon PCM saturé.
  Crête WAV -18.98 dBFS ; AAC décodé -18.79 dBFS.
- **50 images du vrai MP4** comparées à des rendus directs CairoSVG actuels,
  hors cache PNG. Erreur moyenne absolue RGB maximale par image :
  1.607743/255 ; maximum dans les régions visibles contrôlées :
  2.461632/255, sous le seuil de 3/255. Aucun échec.

## Géométrie et continuité

- Les 912 états SVG ont des identifiants uniques et des références de masques
  présentes ; deux marqueurs de moufle dans les plans du personnage et un
  seul dans chaque insert lavabo.
- **1488 contours natifs** de bras/moufle comparés à ceux du rig canonique,
  hors disque de 24 px du raccord local déjà approuvé.
- **1488 prises recalculées** à partir des contrôles natifs et de la matrice
  émise : écart maximal 7.66e-08 px avec les mains rendues.
  Erreur maximale vers les cibles contraintes : 0.02672784 px.
- Déformations réellement émises mesurées sur les matrices, compression
  maximale : **5.96 % au début,
  12.99 % au milieu,
  20.00 % dans le dernier tiers**.
  L'aire 2D est conservée à la précision numérique des coefficients SVG.
- Pieds natifs exclus de l'affine du haut du corps. Matrices du SVG parcourues
  jusqu'aux pieds : dérive maximale des ancres monde
  5.92e-07 px ; formes natives inchangées.
- Quatre rinçages observés numériquement : bouts dans le jet, poignets en dehors.
  Le repère de la moufle d'étude est adapté aux nouveaux horaires de lavage.
- Poubelle : trois grosses boulettes persistantes ; quatrième papier au sol.
  Stock du rouleau monotone de 1 à 0.
- Derniers **18 états du corps, des bras et du visage strictement tenus** ;
  la fumée fournit 18 fragments distincts pendant cette tenue.

## Sources et reproduction

Rig, décor approuvé et fichiers V25 protégés présents dans le checkout
inchangés. Les sources visuelles sont celles du manifeste du rendu final ;
les trois sources sonores correspondent à leurs empreintes d'audit et de
provenance. Aucune source contrôlée n'a changé pendant la vérification.

Le premier appel s'est arrêté avant décodage sur l'ancien nom d'un champ de
l'audit sonore. Seul le contrôleur a été adapté au nouveau tableau
`source_hashes` ; le contrôle complet ci-dessus a ensuite été exécuté. Aucun
film, mix ou paramètre de jeu n'a été corrigé par ce vérificateur.

```sh
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v26/sources/verify.py
```

`audit_final.json` et `audit_revision_v26.json` contiennent le même résultat
complet. `verify_revision_v26.py` est l'autre point d'entrée du même contrôleur ;
il n'est pas nécessaire de le relancer pour dupliquer ces mêmes contrôles.

Empreintes SHA-256 :

- Film son : `57e3cbb8b45595901aa18738643b135998fd97933460240f029d93855b516cc0`
- Film muet : `8190747fb4931221ba7f1e1968c1d795f813179f822eb8f33f81c1d3db9d4eeb`
- Mix WAV : `a785f8bd9cd5bbeeb3baae830b6e61f5b3d8154d6bed59887035f3c2d2051bbb`
- Audit final : `70b3a1555a53084056e59588434a4119d65c95a1e1f61a9ebe9c1c5ff71b056c`
- Vérificateur : `199db02c79dbe8ebdcf8cf4eef0da76a2fe123bb27a8df1f72e33fa5b0f2e2a7`
