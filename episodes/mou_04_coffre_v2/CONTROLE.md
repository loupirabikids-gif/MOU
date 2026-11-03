# Contrôles du coffre V2

Livraison : 30 s, 720 images, 24 images/s, MP4 vertical1080 ×1920. Une
version avec huit effets sonores et une version muette partagent exactement
le même flux vidéo H.264. Les empreintes sont dans
[`controle/livrables.json`](controle/livrables.json).

## Image et réalisation

L'animatique complète a précédé le HD. La critique indépendante a demandé
de séparer le sourire du bras pendant la reprise et de supprimer deux
retours souriants au milieu du découragement. Ces passages ont été
corrigés puis revus dans l'animatique B. La critique et ses limites sont
conservées dans [`controle/critique_finale.md`](controle/critique_finale.md) ;
les décisions dans [`developpement/corrections.md`](developpement/corrections.md).
La revue ciblée du vrai HD confirme les corrections, avec accord visuel.
[Douze images décodées du HD](controle/apercu_HD.png) et
[poses corrigées du jeu](controle/corrections_jeu.png) sont incluses.

Le [QA final](controle/qa.json) passe **24 contrôles techniques** : treize
plans jointifs, 720 états finis, caméra globale, cadrages de chiffres,
contacts composés aux gestes clés, prises bilatérales, pupilles visibles
aux poses ouvertes testées, fond opaque et temps commun au compteur et à
l'horloge. La dernière composition réunit la feuille vide, MOU au téléphone
et09:30. Le recul reste dans la même perspective frontale.

Douze images réellement décodées du MP4 HD ont été comparées à des rendus
Cairo neufs : erreur RGB moyenne de1,35 à1,77 due à la compression ; les
douze PNG du cache sont identiques aux rendus neufs. Les79 entrées gelées
et sept anciennes références sont intactes. Le rig original et l'adaptateur
MOU de V1 sont conservés. Ce contrôle technique ne mesure pas le rire ou
la compréhension d'un public.

## Son

Le MP4 contient le nouvel AAC issu du WAV courant, et non un ancien mix.
Huit sources distinctes sont documentées : attribution, licence CC0,
URL, original, découpe et traitement. Les deux substitutions Foley sont
signalées : moteur de ventilateur pour la vibration, contact bois pour
le crayon. Les voix synthétiques rejetées et les accents d'ellipse sont
absents. Aucun morceau musical ajouté.

WAV : 30 s, stéréo48kHz PCM16, pic−12,13dBFS, aucun échantillon saturé.
La somme des huit stems égale le mix. Les attaques d'énergie des effets
suivent leurs repères de0 à12,1ms ; cela vérifie le placement technique,
pas leur reconnaissance à l'oreille.

**Aucune audition réelle n'a été possible ici.** Le naturel des matières,
le confort du mix et l'efficacité comique sonore restent à apprécier en
lecture. Voir [fabrication sonore](developpement/son.md) et
[démo des effets](audio/demonstrations/banque_effets_v2.mp4?raw=true).

## Sources et reproduction

Le ZIP possède un manifeste SHA256 et un contrôle CRC. Depuis une extraction
isolée,16 PNG HD ont été reproduits à l'identique ; la préparation de la
banque sonore et le WAV ont aussi été régénérés à l'identique. Le rapport
[`reproduction_zip.json`](controle/reproduction_zip.json) porte sur ces
sources et assets. Le dernier réemballage ajoute les rapports sans changer
les producteurs gelés. Voir [`archive.json`](controle/archive.json) pour
l'archive finale et le [README](README.md) pour les commandes.

Les anciens films et la référence privée ne sont ni écrasés ni incorporés.
Une livraison GitHub ne constitue pas une publication sur un réseau social
ou une validation de performance publique.
