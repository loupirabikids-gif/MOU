# Contrôles V5

La critique porte sur des images décodées de l'animatique puis du MP4 HD.
Le contrôleur technique et les mesures audio sont conservés avec les sources.
Ils ne constituent ni une écoute réelle ni une validation du comique par le public.

- Bras : déplacement de la main droite et du coude, séparation visible du
  flanc et masquage par les faces solides. Vérification des vues composées
  et du film à 13,5 s et entre 19,3 et 21 s.
- Temps : contrôle des 720 états, somme écoulé/restant = 1 800 s, horloge
  dérivée du même temps entier ; endpoints à 16,25 / 22 / 23 s et arrêt de
  session à 09:30. Nouvel affichage HH:MM sous les horloges entières.
- Jeu : plus de relances minute par minute après 16,25 s ; une fatigue,
  une descente et un éveil, puis regard maintenu jusqu'à l'insert du coffre.
- Téléphone : états de contact protégés comparés à la V4 corrigée ; rig,
  vues, jeu de base et gestes de prise préservés.
- Exports : format, durée, décodage, concordance avec les dessins sources
  et identité du flux vidéo son/muet contrôlés dans `controle/qa.json`.
- Son : 18 cues conservés, WAV identique au précédent, aucune saturation
  PCM, chronologie V5 dans les rapports. Pas de nouvelle voix ou musique.

Voir [la critique des vrais montages](controle/critique_finale.md),
[le rapport technique](controle/qa.json), [les mesures son](audio/controls.json)
et [les corrections](developpement/corrections.md).

Les anciens films sont vérifiés par leurs empreintes. Les sources productrices
et les entrées sont gelées ; le renderer compare leur empreinte avant et
après le rendu. Le ZIP dispose d'un manifeste SHA256 et d'un contrôle CRC.
La reproduction depuis une extraction isolée est consignée séparément dans
`controle/reproduction.json` : elle compare des PNG et le WAV, sans promettre
l'identité binaire d'un nouvel encodage MP4.

La recherche vocale vérifie les documentations et les licences accessibles,
sans modèle exécuté ni échantillon jugé à l'oreille. Le rôle enregistré ne
fournit pas de moteur à lui seul. La qualité perçue des voix reste à valider
avant toute intégration. Aucun fichier privé de la référence n'est livré.
