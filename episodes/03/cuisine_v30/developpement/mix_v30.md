# V30 — MOU plus présent, musique abaissée

Demande du 1 novembre 2026 : diminuer la musique pour entendre MOU, conserver
le retrait de la cuisson et accompagner le nouveau jeu sans changer sa voix.
Ce travail porte seulement sur `sources/son.py`, `audio/` et ce document.

## Changement effectué

Le mix conserve 61 des 63 événements de V28. Le fond de cuisson de 0–31,95 s
et le dernier « tsss » de 32,60–32,95 s restent supprimés. Le premier contient
aussi les crépitements et les pops d'huile ; aucun de ces sons n'est réintroduit.

La musique seule reçoit un gain constant de **−6 dB**, avec un arrondi PCM
avant mélange. Les 60 autres événements, dont les cinq vocalisations,
gardent exactement leurs sources PCM, instants et gains. Pas de nouvelle voix,
de nouvelle matière, de compression, de normalisation ou de modulation
supplémentaire. La petite modulation de 0,6 dB des lavages est déjà incorporée
dans la piste musicale historique et reste inchangée.

Le fondu global 8/35 ms et le gain fixe de livraison +3,5 dB restent ceux de
V28. Les silences exacts de 32–32,5 s et de 37,25–38 s sont conservés.

## Repères de synchronisation transmis à l'animation

Mesures sur les cinq WAV inchangés. Le pic est celui d'une fenêtre RMS
glissante de 8 ms ; le seuil indique 10 % de ce maximum. Ces chiffres sont
des repères numériques, pas une écoute ou une certification d'émotion.

| Son | Intervalle | Seuil 10 % | Pic RMS 8 ms | Centre d'énergie |
| --- | --- | --- | --- | --- |
| Hésitation | 21,98–22,16 s | 21,98456 s | 22,03402 s | 22,03778 s |
| Inspiration | 25,68–25,84 s | 25,68848 s | 25,76619 s | 25,76738 s |
| Choc | 31,76–31,96 s | 31,78944 s | 31,85998 s | 31,86594 s |
| Expiration | 32,78–33,06 s | 32,78400 s | 32,80821 s | 32,83668 s |
| Satisfaction | 35,15–35,31 s | 35,15400 s | 35,16219 s | 35,16385 s |

## Équilibre mesuré et limites

Sur les fenêtres des trois premières voix, le rapport RMS voix/jazz augmente
respectivement de 5,994, 5,995 et 6,000 dB. La différence minuscule avec le
gain mathématique de 6 dB vient de l'arrondi de la musique en PCM16.

Aux fenêtres d'expiration et de satisfaction, la musique était déjà muette.
Aucun rapport à un silence n'est annoncé : le mix demeure bit pour bit
identique à la variante sans cuisson pendant ces deux passages. Plus
généralement, tout échantillon où la musique originale est nulle reste
identique à cette variante.

Ces mesures ne prouvent pas que les vocalisations seront reconnues, agréables
ou suffisamment audibles sur un téléphone. Le modèle ne peut pas écouter
dans cet environnement. Aucun nouveau timbre n'est donc déclaré validé.

## Reproduction et contrôles

La matérialisation initiale a vérifié que la somme des 63 anciens cues,
suivie du fondu et du gain de livraison, reproduisait exactement le WAV V28.
La somme des 61 cues avant baisse musicale reproduit exactement le PCM de
la variante sans cuisson :
`8f06edd457bca66d39a7079107d80a56f6b738fd660d7488818d4b5708d9e809`.

Après cette étape, le producteur n'accède plus à V28. Il lit sa banque locale
et les notices copiées dans cet épisode :

```bash
.venv/bin/python -B episodes/03/cuisine_v30/sources/son.py
```

Une reconstruction dans un dossier temporaire sans accès de code à V28 a
produit les mêmes WAV, stems et manifeste, octet pour octet. Le contrôle est
dans `audio/audit_autonomie.json`. Le gel des sources, entrées et sorties est
dans `audio/gel_son.json` ; les niveaux, événements et ancres sont dans
`audio/provenance.json`. Zéro échantillon PCM écrêté.

Le WAV final a pour SHA256
`18448452c527eff7a4ae9ecfbb3c6fc5300697344a9e8b17be8a5140b4733c8e`.
Trois stems sont fournis aux niveaux de livraison : musique, voix,
bruitages/air. Leur somme peut différer du mix de quelques unités PCM,
car chaque stem reçoit son propre arrondi de livraison ; le producteur
arrondit une seule fois le mélange total.
