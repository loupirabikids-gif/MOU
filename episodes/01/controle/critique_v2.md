# Critique indépendante — révision 2, « Le retardateur »

## Demande de révision prise en compte

Le retour de l'utilisatrice est que le relâchement manque d'exagération et
que MOU ne paraît pas assez convaincu d'être beau. La réussite technique de
la première version n'établissait donc pas la réussite de ces intentions.
Cette révision sera jugée d'abord sans son.

## Diagnostic de départ

Dans la première version, la poitrine et le corps ne changeaient pas entre
la pose et le relâchement. Le changement restait porté par les paupières,
les bras et la bouche. L'œil fermé accompagné d'une bouche souriante ouverte
pouvait même évoquer un clin d'œil voulu pour la photo plutôt qu'une grimace
accidentelle. La pose de départ était souriante, sans action suffisamment
claire d'auto-admiration.

## Critères ciblés de la révision

| Passage | Exigence de jeu et de continuité |
| --- | --- |
| 0–2 s | MOU se plaît à lui-même : préparation affectée, redressement, satisfaction devant son aperçu, et maintien assumé de la meilleure pose. Un simple sourire supplémentaire ne suffit pas. |
| 2–5,25 s | La vanité se maintient devant le compte à rebours ; le regard revient clairement vers le téléphone. La crispation doit rester une tentative de tenir cette beauté, pas une émotion isolée. |
| 5,25–6,5 s | Un affaissement visible de la masse du corps rompt la pose : appui bas, changement de largeur/hauteur, bras entraînés, visage mou ou tordu. Le départ du mouvement et sa pose finale doivent se lire en petit écran. |
| 6,5 s | La prise saisit réellement le pire moment du relâchement. La grimace ne doit pas pouvoir être confondue avec un clin d'œil coquet volontaire. |
| 7,25–8,85 s | Le cliché reste immobile, identique à la pose capturée, et contraste nettement avec l'image flatteuse voulue par MOU. |
| 9,5–14 s | MOU reconnaît le décalage entre ce qu'il croyait montrer et ce que la photo révèle. Regard vers photo, chute de l'assurance et sourire de façade final. |

Dans toutes les poses : même silhouette de référence malgré les déformations
animées ; aucune anatomie ajoutée, pas de nez ni d'appendice ; deux bras
continus terminés chacun par une seule main ; deux pieds ancrés au sol ;
pupilles découpées par les yeux ; aucune dissociation involontaire entre
corps, visage et bras lorsque l'ensemble se déforme.

## Méthode et état

Examiner les images clés comparées avant/après à 360 × 640, puis les
intermédiaires denses autour de 5,25–6,5 s et le montage encodé complet.
Signaler des instants et défauts précis, et distinguer l'amélioration
visible d'une preuve de compréhension par un public. En attente des images
clés de la révision 2 ; aucune validation de celle-ci n'est encore émise.

## Première planche de la révision 2

Planche `work/animation_v2/vanite_effondrement.png` et planche de prévisualisation
examinées. L'intention de vanité est plus claire : MOU se redresse, fait une
petite moue devant son aperçu vers 0,6 s, relève son sourire et se fait un
clin d'œil vers 1,6 s. Le passage du maintien fier à l'écrasement est désormais
ample et immédiatement distinct : étirement vers 5,4 s, chute vers 5,62 s,
rebond et affaissement tenu vers 6,15–6,5 s. Ce ne sont plus seulement les yeux
qui changent. Les bras sont entraînés avec le corps et les pieds restent
ancrés dans les poses clés.

Deux faiblesses restent visibles sur cette première planche, signalées
avant le montage :

- La bouche de capture en grand U, avec une langue encore contenue dans le
  sourire, peut se lire comme un rire plutôt qu'une détente maladroite. Le
  squash seul ne résout pas entièrement cette ambiguïté. Un bas de bouche
  mou, franchement oblique, avec la même langue pendante, est à examiner.
- La première incrustation photographique coupe la bosse et une partie des
  mains. L'adaptation du cadrage à l'encombrement réel du personnage déformé
  est nécessaire ; le recadrage doit être calculé une fois pour le cliché,
  pas changer la pose photographiée.

Observation secondaire : la réaction immédiate après le flash conserve une
petite bouche souriante. Un petit O donnerait une surprise plus nette, sans
anticiper la gêne qui survient lorsqu'il voit le résultat.

Ces images précèdent l'affinage de la bouche et l'autocadrage de la photo.
Aucun avis final n'est encore porté sur ces corrections en cours.

## Montage léger révisé : amélioration visible et défaut matériel bloquant

Le montage complet de révision 2 a été extrait à 12 i/s et réduit à
360 × 640. L'affaissement et la nouvelle bouche pendante sont visibles dans
le fichier encodé : vers 5,42 s le corps s'étire encore, puis il s'écrase
franchement vers 5,67 s, rebondit et se repose dans une pose molle tenue
avant le flash. Le cliché agrandi garde les deux mains, la bosse et les pieds
et ne ressemble plus à un rire coquet. Ce contraste répond au défaut de jeu
signalé par l'utilisatrice, sous réserve du raccord de montage à corriger.

**Défaut matériel trouvé avant l'export final :** le clin d'œil prévu vers
1,625 s n'apparaît pas dans le fichier encodé ni dans l'image de travail
`0039.png`, alors qu'un rendu direct du SVG actuel le montre correctement.
Les éclats de vanité sont également absents de plusieurs images attendues.

Le contrôle a isolé une réutilisation incorrecte d'images liées physiquement :
les fichiers `0030`, `0033`, `0037`, `0038`, `0039`, `0040`, `0041` et `0042`
partageaient le même inode avec 16 liens alors que leurs contenus SVG
attendus différaient. La copie en place d'une nouvelle image pouvait donc
écraser plusieurs anciennes images et leur entrée de cache commune. Plusieurs
comparaisons entre la clé SVG attendue, le cache et la destination étaient
incohérentes. Le problème a été communiqué au coordonnateur avec les exemples
et la correction nécessaire : remplacement atomique ou suppression du lien
avant copie, cache neuf pour cette révision, puis nouveau montage.

Aucun avis final positif n'est porté sur ce montage incomplet au niveau des
images de vanité. Les raccords de bras et l'ancrage des pieds ne présentent
pas de nouveau défaut visible sur les vues de chute ; le problème décrit
ci-dessus concerne la fidélité du montage aux images effectivement calculées.

## Nouveau montage après correction du cache — avis de révision

Le nouveau `premier_montage.mp4` a été contrôlé par des extractions directes
aux instants 1,3125 s, 1,625 s, 6,25 s, 7,5 s et 13,5 s. L'éclat de glamour
et le clin d'œil sont désormais réellement présents dans le fichier encodé ;
la pose de chute, son cliché et la réaction finale y correspondent également.
Le coordonnateur a remplacé l'écriture en place par un remplacement atomique,
isolé les anciennes images et recalculé les 336 images avec un cache neuf.
Le défaut de montage relevé ci-dessus est donc corrigé dans ce nouveau rendu.

**Jeu de vanité, 0–2 s :** le regard satisfait vers son aperçu, la petite
moue, le redressement du corps, le sourire relevé puis le clin d'œil donnent
une action d'auto-admiration. Les brefs éclats visuels appuient cette
prétention. Le personnage ne fait plus seulement un sourire générique.

**Relâchement, 5,25–6,5 s :** la rupture de hauteur et de largeur se lit à
360 × 640. La petite anticipation verticale rend la chute plus nette ; le
rebond se termine dans une posture tassée et de travers, assez tenue avant
le flash pour être reconnue. La bouche tombante avec la même langue pendante
ne se confond plus avec le rire volontaire de la première version.

**Contraste photographique, 7,5 s :** le cliché montre cette pose ratée en
entier, sans couper la bosse, les mains ou les pieds. Le visage reste lisible
en affichage mobile malgré les espaces lavande créés par le corps aplati.
Le contraste avec le MOU auparavant redressé et satisfait est franc.

**Continuité et chute :** les deux bras et leurs moufles suivent le torse
pendant l'affaissement ; les deux pieds conservent leur appui. Aucun ajout
anatomique n'est observé, la langue existait déjà dans le rig. Le retour à
la photo puis au regard du spectateur explique la gêne sans dialogue. La
réaction de fin reste brève et la durée de 14 s n'appelle pas de prolongation.

**Avis :** cette version corrige de façon visible les deux faiblesses de
jeu signalées par l'utilisatrice et peut passer à l'export final 1080. Aucun
autre défaut matériel n'est relevé dans les passages examinés du nouveau
montage. La petite bouche souriante juste après le flash reste une nuance
de jeu secondaire : la découverte du résultat et la gêne ultérieure sont
assez nettes pour que cela ne bloque pas le gag.

**Limites :** ce jugement repose sur les images extraites et l'enchaînement
du montage muet, pas sur un test auprès d'un public ni sur une mesure de
compréhension. Aucune écoute humaine du son ou du mix n'est revendiquée.
Le fichier final 1080 doit encore recevoir son contrôle technique distinct.
