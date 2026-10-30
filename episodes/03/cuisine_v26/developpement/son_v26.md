# Son V26 — continuité musicale et gestes lisibles

Réalisation autorisée du découpage de 38 s. La V25 rejetée reste conservée ;
elle ne sert pas de validation de qualité sonore. Le modèle ne peut pas
écouter dans cette session. Les contrôles ci-dessous sont numériques.

## Fond musical

Partition originale à 108 BPM pour piano médium et contrebasse, sans ligne
aiguë, batterie, voix ou jingle. Les 135 notes ont des vélocités de 25 à 33.
Les harmonies sont liées sur une grille globale, indépendante des coupes :
un accord doux tous les deux temps, ses trois voix espacées de 170 ms.
Les attaques supplémentaires durent 110 ms au piano et 60 ms à la basse.

Le premier essai a montré qu'allonger les touches ne supprimait pas la
décroissance naturelle des échantillons : le niveau musical variait encore
de 22,85 dB sur des fenêtres de 0,5 s. La répartition harmonique plus régulière
ramène cette plage à 6,59 dB ; l'écart entre percentiles 5 et 95 est de 5,38 dB.
Aucun bruit de remplissage, détecteur de niveau ou normalisation par scène
n'a été ajouté. La composition porte cette continuité, pas une augmentation
générale du volume.

La calibration unique du fond reste à −41,5 dBFS RMS avant une atténuation
maximale de 0,6 dB aux lavages, avec transitions de 600/800 ms. Le PCM musical
mesuré sur 2–37,3 s est à −41,66 dBFS RMS avant le gain de livraison. Le plus
long passage au zéro numérique dans cette plage dure un seul échantillon.
Le fondu final va de 37,4 à 38 s. Ces résultats ne prouvent pas la douceur
ou la continuité perçues à l'écoute.

## Gestes et matières

Le mix additionne 48 événements : 25 événements papier, 22 éléments de cuisine
et de sifflement, un fond musical. Les trois notes sifflées restent seulement
au départ, aux instants 0,3 ; 0,855556 et 1,411111 s, avec un gain de −6 dB
par rapport aux anciens PCM. Aucun effet ne souligne les sourcils ou le sourire.

Les quatre jets occupent exactement les intervalles 3,9–5,35 ; 11,3–12,4 ;
16,5–17,45 et 23,25–24,2 s. Leur calibration fixe par type produit des RMS
entre −39 et −39,14 dBFS avant le gain de livraison, sans montée avec le débit
visuellement exagéré. Couteau, tomate et sel suivent la nouvelle chronologie.
La cuisson s'efface entre 31,5 et 33,25 s ; ensuite seul le jazz reste présent.

Les huit frottements papier sont centrés sur les maxima de vitesse relative
des deux moufles réellement évaluées dans le contrôleur V26 :

| Cycle | Centres mesurés en secondes |
| --- | --- |
| 1 | 6,66542 ; 6,90375 |
| 2 | 13,33417 ; 13,51542 |
| 3 | 18,23925 ; 18,38063 |
| 4 | 26,98583 ; 27,29063 |

Le producteur échantillonne 240 états par essuyage, exclut son approche initiale,
puis sélectionne deux maxima espacés. Les durées des extraits restent dans
leurs phases de contact. La déchirure finale se situe à 25,2 s, le contact du
tas à 29 s et celui du sol à 29,85 s. La mesure des mouvements n'est pas une
preuve d'identification perceptive des sons.

Les extraits de papier AtomSFX/MXAntian sont des captations documentées sous
MIT : lissage de papier et déchirure de carton épais adaptée discrètement.
Le carton n'est pas présenté comme de l'essuie-tout enregistré. La texture
« Paper Scraps » de Ben Burnes est CC0 ; son procédé d'enregistrement et le
geste exact ne sont pas documentés. Les WAV, notices et preuves restent dans
`assets/paper_recordings/`. Eau, commandes, ustensiles, cuisson, sel et
sifflement proviennent de la synthèse antérieure de MOU, pas de nouveaux
enregistrements naturels. Leur matière reste une limite de cette proposition.

## Livraison et reproduction

Le gain global reste fixe à +3,5 dB, appliqué une seule fois après l'addition
des PCM et un fondu de bord de 8/35 ms. Aucune cible LUFS ne remonte le film.
Le WAV final est stéréo 48 kHz/16 bits, 1 824 000 échantillons par canal :
−33,68 LUFS intégrés, −18,98 dBTP, zéro échantillon écrêté. Le niveau calme ne
certifie pas le confort sur un téléphone.

Les 22 PCM sources nécessaires sont conservés dans `audio/raw_bank/`, avec
empreintes et paramètres dans `source_bank_v26.json`. Les 97 fichiers copiés
de V25 devenus inutiles ont été retirés du seul dossier audio V26, libérant
68 302 585 octets. La V25 n'a pas été modifiée.

```sh
.venv/bin/python -B episodes/03/cuisine_v26/sources/son.py
```

Cette commande utilise les ressources incluses et FluidSynth local, sans
réseau ni dossier V25 extérieur. Elle recalcule aussi la synchronisation sur
les sources visuelles V26 : le paquet doit donc contenir les modules de
référence et `chronologie_reference_v25.json`, ainsi que le rig commun.

Une régénération complète après nettoyage a donné des PCM identiques :

- `audio/mix.wav` : `a785f8bd9cd5bbeeb3baae830b6e61f5b3d8154d6bed59887035f3c2d2051bbb`.
- `audio/musique_v26.wav` : `48a350334c30c7688bf43dbb17094a5c550ecdcd2cb9279c3ff04ecb794a670f`.
- `audio/test_fin_v26.wav`, extrait exact de 30 à 38 s : `768184867fc6c7edab065ef643c0f0e170e84c3e81b7b42a96998c98c2258e1f`.

Les audits sont `controle/audit_son.json`, `audit_audio_v26.json` et
`audit_son_reproduction_v26.json`. `audio/provenance.json` décrit chaque
événement, source, adaptation, niveau et position dans le mix. Ces contrôles
et la reproductibilité ne constituent ni une écoute ni une approbation du public.
