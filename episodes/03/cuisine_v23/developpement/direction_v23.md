# Jeu du visage réellement intégré — V23

Intégration du 30 octobre 2026, Africa/Casablanca, sur la chronologie V22
conservée : **48,25 s à 24 images/s**. Le rendu léger reste à examiner par la
critique indépendante avant de qualifier l'effet des expressions en montage.

## Construction

`animation.py` conserve la fonction de scène V22 sous `_scene_state_v22`.
`jeu_visage.py` choisit les expressions et remplace seulement son dernier
groupe `face`. `visage.py` et `expressions.json` sont les copies gelées de la
bibliothèque v1 : aucun second personnage SVG n'est ajouté à la scène.
Le corps, les pieds, les deux bras/moufles, les contacts et les objets restent
ceux des états V22. Le groupe facial complet et ses masques suivent l'angle
facial existant. La cible réelle du regard est inversement compensée avant
`look_at`, pour que cette inclinaison ne détourne pas les pupilles.

## Les temps de jeu choisis

| Temps | Expression intégrée et cible | Temps de lecture |
| --- | --- | --- |
| 0–7 s | `joie_leger`, puis `joie_franc` après les notes sifflées. Cibles de la préparation existante : poêle, cuillère puis moufle. | Le sourire s'ouvre progressivement entre1,85 et 2,25 s, se simplifie avant l'inspection. Un seul clignement hors sifflement vers 4,40 s. |
| 7–7,75 s | `joie_leger` → `doute_franc`. Les yeux gagnent la moufle avant la nouvelle bouche et les sourcils ; ils gagnent ensuite le lavabo. | 4 images de regard, 4 de formation, 7 de pose, 3 vers le lavabo. Ce sont des choix pour cet espace de18 images, pas une norme d'animation. |
| Fin du premier essuyage | `doute_leger` → `soulagement_leger`, entre11,94 et 12,25 s. | Le résultat propre précède l'apaisement ; pas de bouche O de bâillement. |
| Carotte et sel | Attention `curiosite_leger` pour la carotte ; `joie_leger` pour le sel. | Les regards et prises existants restent les mêmes ; pas d'expression neuve à chaque coupe. |
| Papier des rituels 3 et 4 | `contrariete_leger`, puis `contrariete_franc`. | Une différence entre les retours ; pas de soulagement identique ajouté aux cinq rituels. Le visage reste hors des inserts lavabo. |
| 35,35–36,05 s | Attente assurée `fierte_leger` préparée pendant la prise et le tirage. | Les yeux anticipent la cible du papier avant que la main ne l'atteigne. |
| 36,05–36,8 s | Petite feuille réellement visible et regardée, puis `surprise_franc`. | 4 images d'observation avant la formation de la surprise sur4 images ; surprise exposée jusqu'au début de l'essuyage. |
| 36,8–38,4 s | `surprise_franc` → `contrariete_franc`, puis constat conservé pendant essuyage/froissage. | Le passage vers la contrariété utilise les premières0,33 s de l'essuyage. On ne fait pas défiler3mimiques dans les18 images de révélation. |
| 40,25–43,417 s | `doute_franc` → `contrariete_franc` devant le tube vide, puis `curiosite_franc` vers le tissu. | Les cibles et le départ des mains restent ceux du découpage V22. La découverte se forme sur les images 64–68 de la fin puis est exposée jusqu'au macro. |
| Macro tissu | `curiosite_franc`, bouche fermée. | La bouche reste au-dessus du cadre natif y334 : aucun bout de visage n'entre dans l'insert main/tablier. |
| Après essuyage, déchets, public | `tristesse_leger` après le regard aux déchets, puis `gene_franc` après le retour au public. | La pose finale reste strictement identique pendant16 images. Aucun sourire satisfait ne vient annuler le constat. |

Les trois notes sifflées conservent leurs fenêtres et leur bouche dédiée.
La partition sonore est traitée séparément : cette intégration ne qualifie
ni timbre musical ni confort auditif. Aucune écoute n'est revendiquée.

## Métadonnées pour les contrôles

Chaque état porte `expression` : identifiants d'arrivée/départ, coefficient,
phase de jeu, phase du regard, cible monde effective, cible compensée et
rotation du visage, facteur du clignement, empreintes des deux copies de la
bibliothèque. `look_target` contient la cible monde effectivement utilisée.
Le partage est ainsi explicite entre émotion choisie et objet regardé.

## Vérifications déjà effectuées

- Comparaison de 1158 états à V22 : 19 champs physiques identiques, notamment
  transformation du corps, tracés de bras, positions et prises des mains,
  cuillère, carotte/couteau, sel, papier, stock, poubelle, eau et sifflement.
- Fonctions natives d'articulation conservées par comparaison AST.
- Un seul groupe visage et une seule bouche dans les 1158 torses.
- Les 16 torses finaux sont strictement identiques.
- Deux planches de 20 échantillons ont réellement été ouvertes dans
  `work/anim_v23/planche_1.png` et `planche_2.png`. Elles montrent le contraste
  plaisir/doute, la surprise après le petit papier et le constat final.

Ces contrôles n'établissent pas le succès comique. Le prochain contrôle porte
sur l'animatique réellement encodée, les raccords et la lecture en succession.
Le corps est conservé plutôt que remonté artificiellement pour rendre visible
un contact ; une déformation future de corps demanderait un autre essai avec
attaches et prises contrôlées.

## Empreintes du gel de travail

- `animation.py` : `29d91856c227b7a9eec6a7248d894c66714a0fa0fae5f2f12df23f4efc8df895`.
- `jeu_visage.py` : `6213b819ebaa6d1ba1785d3e1ce8ddbc1d4f94ab08affd805fd3680ec8ee0cef`.
- `visage.py` : `f45f6c16ae021f211f3956ebfd3d3ea31c9fbeefd1fb9d4430d59f0a25bc6412`.
- `expressions.json` : `20cb51b6819bb6191bb19f847fc1e1db6a125b27958bf1fdb44d99155232157a`.
