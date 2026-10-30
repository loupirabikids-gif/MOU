# Accès YouTube après activation — 30 octobre 2026

**Les autorisations ont été appliquées.** Le statut courant du runtime est
`restricted/enforced`, observations actuelles, avec les huit destinations du
brouillon dans l'autorisation active. Le fichier de politique local reflète
aussi ces règles. Il ne faut plus présenter leur activation comme manquante.

## Ce qui fonctionne et ce qui reste bloqué

- Bing répond et fournit certains résultats textuels pertinents.
- Les trois accès directs testés, Oggy, Mr Bean et Explosm, échouent encore
  avec `CONNECT tunnel failed, response403`. Le diagnostic curl confirme
  HTTP403 au tunnel et aucun code HTTP du site d'origine, serveur `envoy`.
- Cela situe le refus avant le chargement de YouTube ; la cause précise n'a
  pas été établie. Le catalogue des diagnostics réseau ne contient aucun
  enregistrement disponible. Ne pas attribuer sans preuve le refus à un
  compte utilisateur, aux cookies, à YouTube lui-même ou à une règle précise.
- Google répond200 mais présente une page JavaScript sans résultats lisibles.
  Bing renvoie aussi des résultats hors sujet à plusieurs requêtes Oggy :
  ceux-ci sont explicitement écartés.

[Diagnostic et réponses observées](diagnostic.json). Les réponses HTML
restent dans work/, hors livraison ; les données conservées sont sans secret.
Les horaires des requêtes sont UTC ; le diagnostic local est daté en
Africa/Casablanca.

## Lecture documentaire possible

Une recherche Bing RSS `MrBean animated` identifie le canal officiel
[Mr Bean](https://www.youtube.com/MrBean/featured) et le lien
[Business Bean | Funny | Mr Bean Official](https://www.youtube.com/watch?v=xTBDsVl9fQQ).
Ces titres sont **des données de l'index**, pas des vidéos consultées.
Aucune durée, date de mise en ligne ou audience actuelle n'est déduite de ce
repérage. Les copies Dailymotion ou autres lecteurs tiers apparus dans les
résultats n'ont pas été ouverts pour contourner le refus réseau.

Le [repérage de l'animation adulte](veille_adulte/rapport.md) exploite les
résultats textuels pertinents et sépare signes de distribution, métadonnées
indexées, compteurs non vérifiés et articles non consultés.

## Limites pour MOU

Aucun épisode d'Oggy, Mr Bean ou des chaînes adultes n'a été visionné ni
écouté dans cette reprise. Les regards, déformations, durées de pauses,
raccords de caméra et accents sonores ne peuvent donc pas être qualifiés
comme observations de leurs scènes. Aucun film MOU n'est recalculé ici.

L'étape de publication demandée à l'utilisatrice est accomplie. Vérifier
l'état réel avant toute nouvelle demande de configuration et ne pas faire
répéter la même manipulation sans diagnostic nouveau. Pour une étude visuelle,
un extrait fourni directement dans la conversation peut être examiné ; le
son exige toujours une capacité d'écoute réelle, absente dans cette session.
