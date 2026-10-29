# Critique indépendante de la musique V15

Commande : perfectionner la musique de l’épisode de cuisine. L’image, le
montage de 41 secondes, la moufle arrondie, les trois notes sifflées initiales
et les bruitages sont conservés. L’utilisatrice a choisi **« Jazz cartoon
discret »**. Le tempo reste à 108 BPM pour accompagner le jeu existant ;
la musique doit soutenir la cuisine sans expliquer le gag à sa place.

## Examen préalable réel

Lecture de `cuisine_v14/sources/son.py`, de sa chronologie et de son audit
sonore. Mesures indépendantes des WAV V14 `musique_cuisine.wav` et `mix.wav`.
Aucune écoute perceptive n’a été effectuée par ce critique ; les jugements
ci-dessous distinguent la partition observable des hypothèses d’effet.

### Observations

- L’ancienne partition utilise les mêmes sept notes de mélodie et deux notes
  de basse par cellule de quatre pulsations. Cette cellule recommence à
  chaque mesure et à chaque retour en cuisine. C’est une répétition dans
  le code ; cela ne prouve pas à elle seule qu’un auditeur la juge monotone.
- Les notes sifflées de 0,30 à 1,731111 s sont A5, C#6, B5. Le centre tonal
  initial doit leur laisser une place ; une tierce C naturelle insistante
  en accompagnement introduirait une friction avec le C# déjà sifflé.
- Les fenêtres musicales durent 7,75 /3 /1,5 /2 /1 seconde. Les quatre
  retours sont trop courts pour traiter chacun comme un développement de
  plusieurs mesures. Les silences des rituels restent essentiels au gag.
- Le stem V14 mesure environ −41 à −42 dBFS RMS selon la fenêtre, pour un
  pic proche de −27 dBFS avant le gain master de +6,544 dB. Le mix pendant
  la cuisine, hors sifflement, mesure environ −32 à −34,5 dBFS RMS. Une
  orchestration plus dense peut gagner beaucoup de présence à pic égal ;
  augmenter seulement le volume ne constitue pas une direction musicale.

### Trois améliorations proposées

1. **Laisser MOU mener l’ouverture.** Accompagnement léger jusqu’à 1,75 s,
   puis réponse instrumentale courte. Garder une harmonie compatible avec
   les notes sifflées et éviter une seconde mélodie forte en concurrence.
2. **Donner une pulsation jazz sobre.** Contrebasse ronde, piano ou Rhodes
   doux, accords courts et percussion brossée discrète avec respirations et
   réponse du motif. Hypothèse : ce contraste apportera plus de détente que
   les seules notes pincées. Le niveau et la densité devront préserver les
   gestes et petits bruitages ; éviter les ponctuations cartoon insistantes.
3. **Composer les reprises pour leur durée réelle.** Cellules variées et
   conclusions courtes avant chaque coupure, avec de la place autour des
   coupes de carotte, du couteau posé, de la tomate et de la pincée de sel.
   Silence musical absolu pendant lavage, essuyage, jet, poubelle et fin.

Le compositeur a reçu ces remarques avant fabrication et la préférence jazz
retenue par l’utilisatrice. L’intention reste compatible avec A majeur/A6,
sans lead avant 1,75 s ; elle doit encore être comparée à la partition et
aux mesures du rendu réellement livré.

## Examen de la version produite

Sources gelées examinées : `music.py` SHA-256 `6b314d8f…c48944ae1`,
`son.py` `de8aa94f…9b2e44a1`, mix WAV `068b6dae…6854b815` et stem musique
`07aad820…d397a04b`. Le MP4 complet réellement exporté mesure 41 secondes,
avec une piste AAC stéréo 48 kHz : SHA-256
`cace00f7d4c22f846e613de2a1affae263d90fb98ae5c5122aadc902268d98de`.
Les deux extraits comparatifs avant/après existent également. Ces fichiers
et leurs métadonnées ont été examinés ; ils n’ont pas été écoutés par ce critique.

### Réponse aux remarques préalables

- **Ouverture :** la première réponse mélodique de piano commence à 1,84 s,
  après les trois notes sifflées. Les accords utilisent notamment C#–F#–B
  et C#–E–A, compatibles avec la couleur A majeur/A6 retenue. L’ouverture
  laisse donc bien le rôle mélodique à MOU dans la partition.
- **Direction choisie :** la version retenue compte 119 événements de notes,
  répartis en 23 notes de contrebasse acoustique, 42 notes d’accords de
  piano électrique, 21 ponctuations de piano acoustique et 33 notes de kit
  aux balais. Les contretemps concernés sont légèrement balancés à 58,5 %.
  Aucune guitare du premier prototype funk n’apparaît dans ces quatre stems.
  Ce choix d’ensemble et de jeu est cohérent avec « Jazz cartoon discret » ;
  cela ne constitue pas une validation auditive de la couleur effectivement perçue.
- **Reprises courtes :** les cinq fenêtres ont des réponses différentes.
  Leurs dernières fins de notes écrites précèdent la coupure de 0,23 à
  0,74 seconde environ, plutôt que de relancer une longue boucle tronquée.
  Les notes conservent leurs queues naturelles à l’intérieur de la fenêtre,
  avec une sortie de 12 ms et aucun débordement musical après le cut.
- **Place des gestes :** les nouvelles attaques de percussion évitent les
  impacts du couteau et de la tomate ; les attaques piano/percussion sont
  écartées de la pincée de sel. Une courte note de piano débute à 15,23 s,
  près de la seconde coupe à 15,25 s, mais le stem musical sur la durée de
  ce bruitage mesure −57,36 dBFS RMS contre −34,63 dBFS pour le bruitage
  isolé, avant le même master. Ce voisinage n’est donc pas un défaut de
  niveau démontré qui justifierait d’ajouter une correction arbitraire.

### Niveaux, silences et provenance

Mesures PCM indépendantes ciblées, complétées par les rapports du compositeur
et `controle/audit_audio_v15.json` :

- Le RMS de musique après master varie de −34,15 à −36,69 dBFS selon la
  fenêtre. L’arrangement reste un fond discret ; l’amélioration proposée
  repose sur la partition, les instruments et les respirations, pas sur
  une hausse générale du niveau.
- Pendant les trois notes sifflées, l’audit indépendant mesure la musique
  environ 19 à 22 dB sous le sifflement en RMS avant le gain commun.
- Les 63 WAV non musicaux et le PCM du mix hors des fenêtres musicales
  restent identiques à V14. Le gain master exact est conservé ; aucune
  saturation ni musique pendant les rituels et la fin n’est relevée par
  les contrôles numériques.
- Les quatre stems modifiables reconstruisent le stem musique à deux
  unités PCM16 près, dues aux arrondis de quantification.
- La provenance distingue correctement les bruitages et la partition
  originaux de la banque instrumentale tierce TimGM6mb sous GPL-2. La
  licence et les crédits sont fournis dans `assets/` ; le flag historique
  « aucun échantillon externe » a été corrigé. Aucun morceau ni boucle
  musicale préexistante n’est repris.

## Avis

Proposition cohérente avec la direction jazz choisie et les trois améliorations
de construction demandées. Aucun défaut matériel bloquant retenu dans la
partition et les mesures du rendu livré ; pas de correction supplémentaire
inventée pour remplir une liste. Les extraits comparatifs et le film complet
permettent à l’utilisatrice de juger les timbres, le naturel, le plaisir musical
et l’équilibre réellement entendus.

Limite explicite : cette critique porte sur la partition, les fichiers produits,
leur provenance et les mesures. Elle ne prétend pas à une écoute perceptive,
un visionnage sonore continu, un test sur téléphone ou une validation du public.
