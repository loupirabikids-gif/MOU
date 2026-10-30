# Matière sonore complémentaire — V27

Révision des sons seule : les images V26 et leurs 38 secondes sont conservées.
Le module `sources/foley_supplement.py` expose
`cues(timeline, sr=48000) -> [(metadata, signal_float_stereo)]`.
Les signaux sont déjà calibrés avant le gain de livraison commun. Ne pas les
normaliser une seconde fois individuellement ou par scène.

## Contrat d'intégration

Le cue `cuisson_progressive_v27`, de type `frying`, porte
`replaces_kind='frying'` : il REMPLACE le précédent `cuisson_v26`, il ne s'y
additionne pas. Les autres cues sont des couches discrètes qui complètent les
impacts de papier et deux lâchers déjà visibles. Aucun détecteur ni voix n'est
produit ici.

Onze cues sont émis : cuisson, deux segments d'ambiance, quatre matières de
contact avec le tas, un contact de papier au sol, deux accents de lâcher et
un dernier « tsss ». Les deux segments d'ambiance préservent le silence exact
32–32,5 s. Tous les autres signaux respectent également cette plage au zéro.

## Sources et évolution

Les trois gros impacts utilisent des extraits différents de paume/papier
AtomSFX et de « Paper Scraps » de Ben Burnes. La densité augmente par le nombre
de fragments superposés et leur durée, avec un écart modéré de niveau. La
quatrième petite boule et sa chute au sol restent moins présentes.

Les prises AtomSFX/MXAntian ont une méthode d'enregistrement documentée sous
MIT. « Paper Scraps » est une texture de bibliothèque CC0 ; sa méthode précise
n'est pas établie. Ces sons sont adaptés à des contacts avec un tas, pas
présentés comme des enregistrements d'essuie-tout dans une poubelle.
Les fichiers, URL épinglées, SHA, auteurs et licences proviennent du manifeste
inclus `assets/paper_recordings/provenance.json` et restent dans chaque cue.

La cuisson réemploie le PCM synthétique `audio/raw_bank/cuisson_v22.wav`.
Un mélange spectral continu passe du grésillement doux à une texture plus
sèche dès le milieu. Des crépitements déterministes et deux petits pops
accompagnent le contact de tomate et le sel. Les nouveaux crépitements sont
synthétisés localement avec NumPy, pas enregistrés. Une seule courbe de gain
et un arrondi doux des crêtes du cue complet évitent les clics isolés ; il
n'y a ni correction de niveau par scène ni normalisation du film.

L'ambiance à très bas niveau est une synthèse originale de souffle et de deux
partiels de ventilateur. Elle n'est pas une captation de cuisine, de hotte
ou de rue. Un seul « tsss » de 0,35 s à 32,6 s ponctue la poêle encore chaude.
Les accents de papier à 7,82 et 18,86 s suivent les lâchers, pas chaque coupe.

## Vérifications effectuées

L'API entière a été exécutée deux fois : métadonnées et signaux flottants
strictement identiques. Le cumul est fini, sans saturation, et exactement nul
entre 32 et 32,5 s. Audit et WAV de travail : `work/foley_v27/audit.json` et
`couche_seule.wav`, hors livrables.

RMS mesurés de la seule cuisson, avant master :

| Plage | RMS dBFS |
| --- | --- |
| 0–7 s | −44,89 |
| 7–15 s | −45,48 |
| 15–21 s | −44,27 |
| 21–31,95 s | −43,51 |

Les matières supplémentaires des trois grosses boulettes mesurent environ
−47,09 / −45,70 / −44,79 dBFS ; la petite dernière est à −51,91 dBFS.
Chaque cue reste sous −28 dBFS crête. Le cumul de cette seule couche mesure
−44,76 dBFS RMS et −25,28 dBFS crête ; le mix final doit encore tenir compte
de vos autres pistes et du gain commun. Aucune écoute, naturalité perçue ou
lisibilité émotionnelle n'est certifiée par ces mesures.
