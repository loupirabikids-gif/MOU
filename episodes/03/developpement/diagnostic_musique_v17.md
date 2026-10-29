# Diagnostic des coupures perçues — musique V16

Retour de l’utilisatrice : « la musique est comme ça se coupe et ça reprend ».
La V16 était présentée comme continue après des contrôles de signal non nul.
Ces contrôles étaient insuffisants pour conclure à une continuité musicale.

Analyse indépendante du code, de la partition et des fichiers PCM/AAC de V16.
Aucune écoute perceptive n’a été effectuée dans cette analyse. Les mesures
ci-dessous expliquent des causes matérielles et des risques de masquage ; elles
ne remplacent pas le jugement d’écoute de l’utilisatrice.

Fichiers examinés : `cuisine_v16/sources/music.py`, `sources/son.py`,
`audio/musique_sans_baisse.wav`, `audio/musique_cuisine.wav`, les cinq WAV
`cN_eau.wav` et le MP4 final. MP4 SHA-256 :
`579bc4ec2b6d60a96395fa1487527729290c360c9145307919cd4fe4b8c858f0`.

## 1. Le montage musical conserve ses anciennes frontières

Dans `music.py`, `compose()` appelle encore `_v15_score()` avec les anciennes
fenêtres de cuisine (ligne 159). La fonction qui ajoute les liaisons interdit
les nouvelles notes à l’intérieur de ces fenêtres (ligne 170), puis raccourcit
leurs durées avant chaque début de fenêtre (lignes 171–172). Le résultat
juxtapose donc les phrases locales V15 et des remplissages entre ces phrases.
Un rendu FluidSynth unique par instrument n’efface pas cette construction.

Les reprises V15 sont écrites relativement au début de chaque ancien plan.
À 108 BPM, une pulsation dure 0,555556 s. Les débuts de reprise n’ont pas
la même phase sur cette grille globale :

| Début de reprise | Position en pulsations | Phase dans la pulsation |
| --- | ---: | ---: |
| 13,50 s | 24,3 | 0,3, soit 166,7 ms |
| 21,50 s | 38,7 | 0,7, soit 388,9 ms |
| 27,00 s | 48,6 | 0,6, soit 333,3 ms |
| 33,00 s | 59,4 | 0,4, soit 222,2 ms |

Exemple réel de basse : 13,333333 s (liaison globale raccourcie à 0,131667 s),
puis 13,500000 s et 14,060000 s (phrase locale conservée). Les syncopes sont
possibles en jazz ; ici, le changement de figure est commandé par les anciennes
fenêtres de montage. Le champ `one_global_clock=True` ne vérifie pas la cohérence
de ce groove. La préservation obligatoire des 119 anciens événements empêche
de reconstruire librement un accompagnement régulier.

## 2. De vraies quasi-extinctions courtes restent dans le WAV

Méthode : WAV PCM16 stéréo moyenné en mono, division par 32768, puis gain
master exact `2.124210976406158`. RMS non pondéré sur des fenêtres de **200 ms**,
balayées tous les 50 ms. Le temps du tableau est le **début** de la fenêtre.
Les valeurs sont en dBFS après master, pour la musique seule.

| Fenêtre | Musique sans baisse lavabo | Musique livrée |
| --- | ---: | ---: |
| 14,65–14,85 s | −99,522 | −99,522 |
| 15,85–16,05 s | −82,53 | −82,53 |
| 16,45–16,65 s | −81,23 | −86,10 |
| 29,00–29,20 s | −81,24 | −87,07 |

Le premier trou existe donc avant l’enveloppe du lavabo. Les notes courtes,
les retraits autour des contacts et la construction par fenêtres conservent
des vides que le remplissage des anciennes zones silencieuses n’a pas résolus.

Sur la musique livrée, le RMS médian de ces fenêtres de 200 ms est −39,16 dBFS
et le dixième percentile −49,60 dBFS. Une fenêtre de 500 ms peut inclure une
attaque forte à côté d’une extinction de 200 ms et rester au-dessus d’un seuil
de −75 dBFS : c’est pourquoi le précédent audit pouvait réussir.

Des remontées de niveau accompagnent aussi les anciennes reprises. Comparaison
du RMS des 500 ms juste avant et juste après le début de la reprise :

| Reprise | Avant | Après | Remontée |
| --- | ---: | ---: | ---: |
| 13,50 s | −34,73 | −29,99 | +4,74 dB |
| 21,50 s | −36,48 | −30,69 | +5,79 dB |
| 27,00 s | −34,15 | −31,16 | +2,99 dB |
| 33,00 s | −37,46 | −33,67 | +3,79 dB |

Les variations de note participent à ces valeurs. Elles ne démontrent pas
à elles seules une erreur de mix, mais elles sont cohérentes avec l’impression
de phrase qui s’efface puis repart signalée par l’utilisatrice.

## 3. Le fond est très faible face à l’eau

RMS de toute la musique livrée après master : −36,61 dBFS. Son RMS dans une
bande idéale 300–4500 Hz est −42,80 dBFS. Cette bande est un proxy numérique
de comparaison des médiums ; ce n’est pas une simulation d’un téléphone réel.

Pendant les écoulements effectifs, en comparant le WAV d’eau seul au passage
musical correspondant :

| Cycle | Musique après master | Eau après master | Eau au-dessus de la musique | Écart dans 300–4500 Hz |
| --- | ---: | ---: | ---: | ---: |
| 1 | −42,07 | −21,60 | 20,47 dB | 26,44 dB |
| 2 | −42,37 | −21,29 | 21,08 dB | 28,07 dB |
| 3 | −42,38 | −20,56 | 21,82 dB | 27,87 dB |
| 4 | −43,12 | −20,67 | 22,45 dB | 25,63 dB |
| 5 | −43,03 | −20,75 | 22,28 dB | 29,37 dB |

Le mélange est techniquement non nul, mais une part importante de la musique
se trouve encore très loin sous le bruit d’eau. Une disparition perceptive par
masquage est donc une hypothèse sérieuse, particulièrement sur petit haut-parleur.

## 4. Aucune coupure de transport AAC mise en évidence

Le MP4 contient 1 923 paquets audio, couvrant les 41 s. L’écart maximal entre
fin d’un paquet et début du suivant est d’environ 1 µs, compatible avec les
arrondis des horodatages affichés. Le décodage fournit 1 968 000 trames stéréo
à 48 kHz ; aucun bloc du mix de 100 ms n’est entièrement nul. Corrélation
AAC/WAV : 0,998490.

Cela ne garantit pas une qualité d’écoute, mais les trous et changements
d’arrangement existent déjà dans le WAV de musique. Aucune réparation de
paquets ou nouvelle découpe vidéo n’est justifiée par ces observations.

## Solution retenue pour V17

1. Écrire une seule partition globale à 108 BPM, déterminée par durée et tempo,
   avec une pulsation régulière, des accords liés et des variations par mesure.
   Supprimer les anciennes fenêtres de cuisine, les exclusions et les arrêts
   forcés aux frontières. Garder la famille sonore et le caractère jazz,
   sans imposer la conservation des 119 événements qui causent ces raccords.
2. Assurer la continuité par l’arrangement : accompagnement harmonique dans
   les médiums et pulsation présente, sans se contenter de quelques échantillons
   non nuls ou d’un accord ajouté sur chaque trou détecté.
3. Rendre le fond plus présent et plus régulier. La production V17 vise environ
   −31 dBFS RMS après master en régime normal ; baisse limitée à 3 dB et
   transitions de 500/700 ms au lavabo. Ce sont des réglages de réalisation,
   pas des valeurs demandées par l’utilisatrice ni une garantie perceptive.
4. Conserver le sifflement, les 63 bruitages, leur gain, le montage et les images.
   La baisse porte uniquement sur la musique ; l’eau conserve son niveau.

## Contrôles qui remplacent l’ancien « non nul »

- Invariance de la partition et du rendu brut quand seules les frontières de
  plans/lavages changent. L’enveloppe de volume peut changer, la musique brute
  doit continuer indépendamment des plans.
- Régressions aux instants réels ci-dessus sur des fenêtres glissantes de
  100 et 200 ms ; suivi des excursions locales de niveau, pas seulement un
  RMS de 500 ms dépassant un seuil proche du bruit de quantification.
- Contrôle de la pulsation et des jonctions d’accords sur le WAV rendu.
  Des notes écrites avec des durées qui se chevauchent ne prouvent pas seules
  que le moteur de synthèse les relie correctement.
- Contrôle du niveau dans les médiums et face à l’eau, du flux AAC et des
  bruitages/images conservés. Les mesures doivent être accompagnées des
  limites de méthode et d’un extrait permettant le vrai jugement d’écoute.

Le constat durable est le suivant : **un signal continu dans un fichier et un
synthé rendu une seule fois ne suffisent pas à produire une musique qui semble
continue.** Les anciens tests protégeaient le fichier et certains niveaux,
pas la continuité du phrasé ni sa présence dans le mix.
