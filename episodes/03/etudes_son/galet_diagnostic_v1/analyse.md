# Diagnostic après le retour sur la bande-son du film Galet

Mandat : examiner les éléments sonores que l'utilisatrice soupçonne de gêner
le résultat, avant un autre mix complet. Ce retour ne constitue pas un rejet
explicite du nouveau film.
**Aucun WAV, film livré ou producteur sonore n'a été modifié.** Les empreintes
des fichiers protégés sont identiques avant et après les lectures.

Le mix examiné est `galet_cuisine_v1/audio/mix.wav`, SHA
`06946073fb2c39f49d79acf8d1d5a073b1ac07aeb6dd49e127b0b8158abcb18b`.
Provenances, événements et stems ont été lus ; des fenêtres de niveau et de
superposition ont été calculées. **Aucune écoute n'est disponible.** Il n'est
donc pas possible d'affirmer qu'un timbre est mauvais, agressif, naturel ou
reconnaissable à partir de ces mesures.

## Ce que la provenance établit

Le nouveau galet a reçu une nouvelle animation, mais **sa palette sonore reste
principalement héritée du travail V27**. Les 58 cues ne sont pas 58 nouvelles
captations. Retirer les anciennes voix et baisser le jazz ne change pas la
nature des matières qui peuvent déplaire.

| Famille | Ce qui est établi | Ce qui reste à entendre |
| --- | --- | --- |
| Eau et robinets | La provenance décrit les cues comme des synthèses antérieures du projet, ensuite adoucies. Aucune captation de vrai lavabo n'est identifiée dans cette banque. | Le jet paraît-il être de l'eau, un souffle ou un bruit de machine ? Les clics identifient-ils le robinet ? Une origine synthétique ne suffit pas à répondre. |
| Cuisson et air de pièce | Cuisson synthétique antérieure ; crépitements et petits pops stylisés incorporés. Air/ventilateur de pièce synthétiques, à très bas niveau. La cuisson reste présente jusqu'à 31,95 s. | Ces deux fonds apportent-ils un espace ou un grain artificiel qui fatigue ? Leur retrait est un test possible, pas encore une correction démontrée. |
| Sifflement | Trois notes synthétiques au départ : 0,30–0,70 ; 0,85556–1,25556 ; 1,41110–1,73110 s. | Est-ce compris comme un sifflement du personnage, ou comme un signal musical électronique ? |
| Papier | Une partie provient de gestes AtomSFX documentés comme enregistrés ; la déchirure est du **carton adapté**, et la texture Ben Burnes est CC0 sans méthode de captation vérifiée. Les mêmes petites sources servent plusieurs fois. | Une vraie captation de carton ou de papier ordinaire peut rester mal adaptée à de l'essuie-tout. Le mot « enregistré » ne garantit pas le bon matériau ou un geste clair. |
| Jazz | Composition originale rendue par FluidSynth avec guitare nylon et contrebasse échantillonnées. Le code prévoit une dérive de hauteur légère et une accélération 108→112 BPM ; ce n'est pas une prestation humaine captée. | La bossa convient-elle au personnage ? La dérive voulue est-elle ressentie comme comique ou simplement étrange ? Aucun jugement d'écoute n'est établi. |

Sources consultées : `audio/events.json`, `input_bank.json`,
`source_provenance_v27.json`, `partition_reference.json`, `sources/son.py`,
`sources/music_reference.py` et les notices `assets/paper_recordings/`.
La banque des douze voix proposées n'est pas utilisée dans le film.

## Densité : une explication à borner

Le film possède **54 cues courts et quatre fichiers de fond** : musique, deux
segments d'air et une longue cuisson. **32 cues concernent le papier.** Cela
reflète quatre rituels détaillés ; ce chiffre ne prouve pas une surcharge.

Avec un repère purement numérique de RMS supérieur à −66 dBFS par fenêtres de
50 ms, on trouve au plus **cinq couches actives : trois fonds et deux effets
courts**. Deux effets courts se recouvrent pendant environ 1,35 s cumulée.
Les exemples les plus nets sont l'ouverture eau/clic à 3,90 s, la fermeture à
5,30–5,35 s et le double son d'arrivée du papier à 8,35–8,50 s. Les pops déjà
incorporés à la longue cuisson ne sont pas comptés comme fichiers distincts.

Il serait donc excessif de conclure « trop de sons empilés partout ». En revanche,
**chaque rituel cumule le fond de cuisson, le jazz et l'air, puis ses actions**.
Cette présence quasi permanente et la répétition des matières sont des hypothèses
plus précises à vérifier à l'écoute.

## Équilibre : ce qui peut guider le test

Rapports calculés sur les mêmes fenêtres des stems livrés, sans modification :

| Passage | Rapport RMS Foley / musique | Lecture limitée |
| --- | --- | --- |
| Départ sifflé, 0,30–1,73 s | +8,3 dB | Le sifflement et le fond Foley dominent énergétiquement le jazz. Le début doit être inclus dans le comparatif. |
| Premier lavabo, 3,90–5,35 s | +5,2 dB | L'eau et les autres effets sont énergétiquement devant la musique. Les autres lavages sont entre environ +4,1 et +5,4 dB. |
| Papier du premier rituel, 6,30–7,58 s | +0,3 dB | Foley et musique sont proches en RMS moyen sur cette fenêtre. Cela ne prouve ni lisibilité du frottement ni masquage. |

Ces rapports ne sont pas des rapports de volume perçu : spectre, durée, crête et
masquage comptent. Une moyenne comprenant la décroissance et le silence d'un
impact n'est pas comparable à celle d'un jet continu. Un chiffre LUFS global ou
l'absence d'écrêtage ne permet pas de déclarer le mix agréable.

Le gain du mix ne change pas automatiquement à chaque coupe ; le score comporte
une modulation écrite de seulement 0,6 dB sous les lavages. Cela n'exclut pas que
les matières et le passage musique→eau donnent une impression d'équilibre instable.
La fin reste également très dépouillée : coupure musicale à 32 s, petit tsss à
32,6 s, puis principalement l'air jusqu'à la note de 36,25 s. Ce choix pourrait
être questionné si le retour vise la fin ; ce n'est pas le premier test proposé.

## Un seul passage comparatif recommandé

**0,00–8,75 s, soit 210 images à 24 images/s.** Ce premier rituel contient
l'ouverture sifflée, la cuisson, le robinet et l'eau, le papier et sa première
arrivée dans le panier. Il s'arrête sur la coupe précédant la carotte, sans
introduire une nouvelle action incomplète. Les trois fichiers seraient des
variantes du **même extrait**, pas trois scènes différentes :

1. Mix livré, inchangé : référence.
2. Jazz seul, au gain exact du stem livré.
3. Bruitages + air seuls, aux gains exacts des stems livrés.

**Ne pas normaliser séparément les trois variantes et ne pas remonter le jazz
seul.** Modifier leurs niveaux pendant ce test fausserait la comparaison. Garder
les mêmes images et les mêmes instants, sans nouveau montage ou effet.

La réponse attendue est un instant ou une famille : sifflement, eau, papier,
fond continu ou musique. Si le défaut est déjà présent dans le troisième clip,
le jazz n'est pas nécessaire pour le produire. Si les deux couches isolées sont
acceptables mais leur combinaison gêne, l'équilibre et la coexistence deviennent
la priorité. Ce sont des observations à recueillir, pas des conclusions déjà faites.

## Direction après cette écoute, pas avant

Si les bruitages sont rejetés, remplacer d'abord la ou les familles identifiées
par des matières cohérentes avec le geste réel, puis éprouver le même extrait.
Une déchirure d'essuie-tout, un jet de lavabo et un impact de papier légers seraient
plus spécifiques que de nouvelles couches génériques. Une piste allégée pourrait
retirer les fonds de cuisson/air et les doublons de tassement avant de toucher au
volume global, mais elle n'est pas fabriquée ici et son intérêt reste à entendre.

Si le jazz seul est rejeté, travailler le motif, le timbre ou la dérive voulue au
lieu d'une nouvelle baisse de gain automatique. Aucune autre version complète
ne doit être présentée comme améliorée sur la seule base de ses mesures.

Preuves privées : `work/galet_diagnostic_v1/audio_audit.py` et
`audio_audit.json` (méthode, fenêtres, noms des cues et empreintes avant/après).
Les sources et les fichiers livrés n'ont pas changé.
