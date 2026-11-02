# Repérage animalier — état des preuves

2 novembre 2026, observations en fuseau Africa/Casablanca. Mission : repérer
des personnages animaliers d'animation courte pour une nouvelle identité,
en abandonnant MOU. Aucun nouveau dessin ni film fabriqué par ce mandat.

## Résultat de collecte

La veille récente **n'est pas complète**. Aucune date, durée ou audience d'un
Short publié dans les soixante derniers jours n'a pu être vérifiée. Les trois
pages YouTube ci-dessous échouent au tunnel HTTPS du proxy avec 403 Forbidden.
Les sites officiels testés échouent de la même façon. Aucun accès refusé n'a
été contourné, aucun cookie ou secret demandé.

| Référence recherchée | Cible | Preuve actuelle |
| --- | --- | --- |
| Chikn Nuggit | https://www.youtube.com/@chiknnuggit/shorts | Accès direct 403 ; recherches web hors sujet, non exploitées. |
| Simon's Cat | https://www.youtube.com/@SimonsCat/shorts | Accès direct 403 ; recherches web hors sujet, non exploitées. |
| Pusheen | https://www.youtube.com/@PusheenTheCat/shorts | Handle essayé, non confirmé par la page directe ; accès 403. |

Les recherches Bing sur Pusheen recoupent cependant deux identités officielles
indexées :

- https://pusheen.com/ et https://pusheen.com/pages/characters : le résultat
  décrit le site comme le foyer officiel de Pusheen et de ses produits.
- https://www.youtube.com/channel/UCFWi9aUuK7oFksfbWObwcIQ : le résultat
  « Pusheen the Cat - YouTube » dit « Welcome to Pusheen's official Youtube
  Channel » et renvoie à Pusheen.com.

Il s'agit de **résultats de moteur examinés**, pas de pages officielles
ouvertes ni d'un visionnage. Une vidéo Pusheen du 22 août 2020 remonte aussi
dans les résultats ; elle est hors fenêtre et n'est pas un succès récent.

Les recherches Chikn Nuggit/Simon's Cat retournent majoritairement des pages
Microsoft, StackOverflow ou autres résultats sans rapport. Leurs titres et
dates ne sont pas utilisés comme preuves sur ces séries. Google retourne
une page JavaScript sans résultats exploitables dans cette collecte.

## Ce qui demeure non accessible

Pour les trois séries : Shorts récents, dates exactes de publication,
durées, compteurs de vues/likes, comparaison chronologique avec des
publications voisines et rétention. Aucune métrique n'est remplacée par zéro.
Aucune nouvelle vidéo, image de personnage ou bande-son n'a été examinée.

Cette collecte permet de retrouver une identité officielle indexée, pas
d'affirmer qu'une espèce, une palette ou un dessin attire aujourd'hui plus
de vues. La présence d'une marque connue ne prouve pas la performance de
ses dernières publications.

## Hypothèses de conception proposées au coordinateur

Ces points sont des choix de design à tester, **pas des conclusions causales
d'audience issues de cette collecte** :

1. Un animal identifiable peut donner immédiatement une catégorie, une
   silhouette et des attentes de comportement au spectateur.
2. Une tête, un museau, des oreilles et une queue peuvent différencier un
   héros sans dépendre d'une couleur seule. Conserver peu de formes pour
   que sa production reste réaliste.
3. Le contraste du visage doit laisser lire regard, sourcils et bouche en
   miniature ; de grands yeux seuls ne garantissent pas une présence.
4. Une personnalité contradictoire et des situations quotidiennes doivent
   porter la promesse de série. Ne pas copier le design ni les gags de
   Pusheen, Chikn Nuggit ou Simon's Cat.

Avant de présenter ces choix comme fondés sur des succès récents, il reste
à obtenir les vidéos et compteurs vérifiables. Le coordinateur peut proposer
une direction provisoire en annonçant cette limite explicitement.

## Fichiers de preuve

`access_youtube.json`, `access_official.json`, `access_search.json` : URLs,
résultats et observations horodatées. `search_results.json`,
`specific_results.json`, `targeted_results.json` : extraits réellement reçus,
y compris les résultats non exploitables. HTML bruts dans `work/`, hors Git.
