# Son de MOU : réduire la fatigue et clarifier les actions

Recherche et mesures du 29 octobre 2026. **Aucune écoute n’est possible par
le modèle dans cette session.** Ce rapport distingue les faits numériques,
les risques plausibles et les décisions de réalisation à éprouver. Aucun
fichier de production n’a été modifié.

## Ce qui est réellement mesuré dans V21

Le mix de 44,5 s mesure **−25,07 LUFS intégrés**, avec un true peak de
**−7,50 dBTP**, un RMS de **−27,89 dBFS** et un facteur de crête de **20,20 dB**.
Il n’est donc pas utile de conclure simplement « tout est trop fort » ou
de normaliser le film à −14 LUFS : cela remonterait également les défauts.

| Élément | Estimation après son gain de mix et master | Fait utile |
| --- | --- | --- |
| Déchirure de papier | RMS −25,19 ; pic −9,46 dBFS | **67,8 %** de l’énergie entre 2 et 6 kHz ; attaque programmée de 0,7 ms. |
| Premier coup de couteau | RMS −26,15 ; pic −8,46 dBFS | Attaque programmée de 0,25 ms ; surtout grave/médium, seulement 1,6 % dans 2–6 kHz. |
| Première note sifflée | RMS −17,86 ; pic −12,96 dBFS | Environ **13,6 dB RMS au-dessus** de la piste musicale moyenne. |
| Eau seule | RMS −29,76 ; pic −13,96 dBFS | Une seconde couche `hand_water` est simultanée pendant **65,5 %** du temps d’eau. |
| Musique | RMS −31,43 dBFS | Le niveau moyen est déjà discret ; la continuité V21 est conservée par les sources actuelles. |

La bande 2–6 kHz n’est pas une mesure universelle de gêne. Elle identifie
ici un candidat à examiner : la déchirure est très présente dans cette
zone, tandis que le couteau pose davantage une question de transitoire.
Un même égaliseur appliqué à tout le film serait une mauvaise réponse.

La provenance contient **64 événements de premier plan**, soit 1,44 par
seconde. Leur occupation programmée couvre 59,2 % du film ; deux couches de
premier plan se chevauchent pendant 14,1 %. La cuisson et la musique ne sont
pas incluses dans ces compteurs. Le bruit de cuisson est en réalité très
bas (RMS estimé −44,61 dBFS) : le désigner comme la cause dominante serait
sans fondement. Les résultats et limites sont dans [mesures_v21.json](mesures_v21.json).

## Direction de mix recommandée

1. **Une seule cause sonore par action importante.** Pour le lavabo, un
   courant d’eau cohérent ; le contact de la main fait évoluer ce courant
   plutôt qu’empiler un deuxième bruit complet. Garder un petit clic de
   robinet seulement si la commande est visible.
2. **Un groupe papier, pas six commentaires sonores.** Faire entendre le
   déroulage et une déchirure. Retirer les couches systématiques de frottage,
   froissage, souffle de vol et impact à chaque répétition. Réserver les
   impacts lisibles au premier jet et à la chute finale lorsque le récit
   en a besoin. Le mouvement seul peut raconter les étapes intermédiaires.
3. **Laisser les pensées respirer.** Pendant le regard, l’hésitation et la
   révélation, aucun petit « pop » ou jingle ajouté pour annoncer l’émotion.
   Une fenêtre de 8–12 images sans bruitage de premier plan est un choix
   raisonnable pour notre essai à 24 images/s, pas une mesure empruntée à Oggy.
   Le fond musical peut rester continu à un niveau stable.
4. **Calmer les accents au lieu de remonter le fond.** Atténuer le sifflement
   initial et les transitoires de coupe/déchirure ; adoucir leur enveloppe.
   Pour le papier, essayer un passe-bas vers 2,6–2,8 kHz. Pour le couteau,
   réduire d’abord le pic : son problème potentiel n’est pas une abondance
   d’aigus. Ces fréquences et niveaux sont des points de départ d’essai.
5. **Conserver les timbres pendant l’accélération comique.** Raccourcir les
   pauses et choisir moins d’actions audibles ; ne pas monter le volume ou
   accélérer tout l’audio à chaque nouveau lavage. En format téléphone,
   garder les bruitages principaux près du centre évite aussi les grands
   déplacements stéréo sans nécessité narrative.

Cette hiérarchie est plus importante qu’un changement de moteur IA. Les
filtres et un chiffre de loudness ne peuvent pas certifier un rendu agréable.

## Quatre petites études concrètes

[palette_tests/](palette_tests/) contient quatre WAV stéréo 48 kHz, de
1,7 à 2 s, dérivés des banques originales MOU :

- `eau_une_couche_test.wav` : une seule couche, attaques/sorties plus douces ;
- `papier_un_geste_test.wav` : déroulage puis déchirure, sans autres couches ;
- `couteau_transitoires_retenus_test.wav` : deux contacts modérés et espacés ;
- `sifflement_niveau_retenu_test.wav` : les trois notes initiales à niveau réduit.

Ce sont des **études de niveau et de densité à écouter**, sans musique ni
image ; elles ne sont pas qualifiées de sons finaux. Elles sont fournies à
un niveau **post-mix** : ne pas appliquer à nouveau le master historique de
2,124. Les sources, filtres et empreintes sont dans
[palette_tests/provenance.json](palette_tests/provenance.json). Le script
[build_palette.py](build_palette.py) les reproduit. La friction du tablier
existante est déjà faible ; aucun accent supplémentaire ne lui est ajouté.

## Ressources libres effectivement vérifiées

Deux textures de **Ben Burnes / Abstraction** ont été récupérées dans le
miroir [lavenderdotpet/CC0-Public-Domain-Sounds](https://github.com/lavenderdotpet/CC0-Public-Domain-Sounds),
au commit épinglé `f2b6264f9ab89fabc266914c3654685d68c5a39b` : une page tournée
et un tap de couteau. Les notices des deux packs déclarent explicitement
les **sons** sous CC0. Les auteurs, URL, dates et SHA256 sont conservés dans
[cc0/assets_provenance.json](cc0/assets_provenance.json).

Une page tournée ne constitue pas automatiquement une déchirure d’essuie-tout,
et un tap ne démontre pas un couteau traversant une carotte. Leur procédé
d’enregistrement n’est pas explicité dans les notices ; ils sont présentés
comme candidats de texture, sans étiquette de captation « naturelle » garantie.
**Aucun vrai robinet identifié et vérifié n’a été trouvé dans cette recherche
bornée.** Aucun bruit de pluie n’a été rebaptisé lavabo.

Le [rapport CC0](cc0/README.md) documente aussi `wyzowl/sfx-kit` (sons CC0,
explicitement synthétisés) et `Bodila51/opus-sound-layer` (code MIT mais
téléchargements de sons externes à vérifier individuellement). Il est utile
de reprendre leurs principes de curation, pas de leur attribuer une banque
de sons directement validée pour MOU.

[FFmpeg](https://github.com/FFmpeg/FFmpeg/blob/master/doc/filters.texi) fournit
déjà les outils nécessaires : `afade`, `lowpass`, `acompressor`, `ebur128`
et `loudnorm`. Les sections officielles ont été lues et conservées dans
`preuves/ffmpeg_filters.txt`. **Audacity**, dont le README et la licence
GPLv3 ont été revérifiés, sert surtout à une véritable sélection et écoute
humaine, au montage des attaques et au contrôle avec l’image. Sa branche
`master` annonce actuellement la transition vers Audacity 4 ; une version
stable convient mieux qu’une compilation de cette branche pour cet essai.

Sources HTTP horodatées : [preuves/http_sources.json](preuves/http_sources.json).
Aucun modèle IA, plugin payant ou service vidéo à crédits n’a été installé.

## Condition de conclusion

Le prochain passage-test peut employer trois ou quatre événements sobres,
avec des moments de réaction sans bruitage. Il doit être jugé avec l’image
et par une personne qui peut l’écouter. La présente analyse n’a ni écouté
Oggy ni certifié le confort auditif du futur montage.
