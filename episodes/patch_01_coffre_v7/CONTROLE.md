# Contrôles V7 et limites

Le défaut V6 a été recherché dans toutes les phases du film : les anciennes
mesures de quelques poses au repos ne couvraient pas la fermeture puis la
pression du bouton. La V7 corrige ce trajet et les paumes entrant dans le coffre.

## Image et raccords

- Les 720 états ont été considérés pour l'affichage du coffre. Sur les
  612 images où le LCD est réellement dessiné et visible, le dessin réellement composé ne comporte
  aucun pixel de manche ou de paume dans sa zone intérieure. Le bouton à
  gauche et les contacts voulus sur le couvercle sont traités séparément.
- Le bras contourne le flanc : fermeture vers le coin gauche, retrait,
  descente extérieure et pression latérale. Le poignet explicite et la manche
  courbe évitent un raccord caché à travers la boîte. La critique examine
  les images consécutives, la fermeture, le pli du bras et le retour au repos.
- Les positions de mains hors correction, le téléphone, le corps, les vues,
  le temps de session et les trois cases vides sont comparés à V6. La façade
  masque la paume qui entre avec le téléphone pendant le dépôt et la reprise.
- Les MP4 sont décodés et vérifiés : 30 s, 720 images, 24 ips, 1080 × 1920,
  son AAC dans la version son uniquement, même flux H264 son/muet. Des
  images du vrai HD sont confrontées à des rendus frais.

## Nouvelle voix

Soundgen 3.0.0 est réellement exécuté avec le runtime R 4.5.0 existant.
Six intentions et douze prises nouvelles, sans voix clonée ni poids
neuronaux. Résonances articulées M/O/A, conduit de 11 cm, nouveaux contours
et rythmes ; les quatre prises périodiques mesurables ont une fondamentale
environ 2,2 à 2,7 fois plus élevée que V1. Le souffle et le bâillement ne
servent pas à une fausse estimation fiable de fondamentale.

La banque possède paramètres, graines, licences tierces, preuves d'exécution
et de seconde synthèse. Les prises sont proposées selon leur recette et
graine ; aucune sélection à l'oreille n'est revendiquée. Les créations
originales ne reçoivent pas de dédicace publique CC0.

Les cinq cues vocaux suivent les accents des vrais WAV à une image près.
Le bâillement finit avant la coupe, l'inspiration commence sur le visage,
les deux accents du rire restent dans la pose de joie. Les 18 effets de
base sont conservés. Gains fixes, absence de musique et de pompage : le mix
et les stems sont comparés au sample, sans saturation. Les mesures détaillées
et empreintes figurent dans les rapports.

Voir [QA](controle/qa.json), [critique du vrai montage](controle/critique_finale.md),
[diagnostic des bras](developpement/diagnostic_bras.md),
[mix](audio/controls.json), [banque](assets/voix/README.md).

Le ZIP vérifie CRC et manifeste SHA256. `controle/reproduction.json`
documente une extraction isolée, des PNG frais et la reconstruction du WAV.
L'identité binaire d'un nouvel encodage MP4 n'est pas promise.

**Aucune audition réelle n'est possible ici.** Mesures de hauteur, niveaux,
licences et synchronisation ne certifient ni naturel, ni confort ou singularité
perçue. La planche d'écoute des douze prises est livrée séparément. La revue
visuelle ne prédit pas le succès public. Aucune vidéo privée de référence
ou piste sonore tierce non autorisée n'est incluse.
