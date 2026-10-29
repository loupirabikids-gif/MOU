# Son V22 : moins de couches, comparaison à volume global comparable

Le mix est reconstruit à partir des banques originales. Les timings des
événements conservés avant 40,25 s ne changent pas. La musique garde sa
partition globale à 108 BPM, les mêmes instruments et la calibration fixe
`1.2217762480997532`. Le fichier `music.py` reste identique à V21.

## Hiérarchie retenue

- Une seule eau ; les cinq couches `hand_water` sont retirées.
- Papier : déroulage puis déchirure, traités comme un groupe. Les bruits
  systématiques d’essuyage, froissage et déplacement d’air sont retirés.
- Les impacts de poubelle intermédiaires 2, 3 et 4 sont retirés ; le premier
  exemple, le contact du tas à 39,1 s et le sol à 39,85 s restent présents.
- Le remuage continu et la prise de sel ne sont plus surlignés. Les contacts
  utiles (couteau, tomate, commande du robinet et manche) restent sobres.
- Le sifflement conserve ses trois notes initiales, avec une atténuation de
  10 dB à son étage de mix, avant le gain de livraison commun.
- Les réflexions et changements d’expression n’ont aucun son ajouté.
  La seule ponctuation du test final est le tissu au contact réel.

Le résultat compte **41 événements actifs**, dont deux fonds et 39 sons de
premier plan ; **25 couches** de la banque de référence ne participent plus
au mix. Leur liste nominative figure dans `removed_events`. Les WAV historiques
restent conservés comme sources ; leur présence ne signifie pas qu’ils sont
sommés dans la nouvelle piste.

## Filtres et niveaux

La somme n’utilise plus le master historique de 2,124 appliqué aux banques
de l’ancien mix. Les nouveaux WAV de `audio/processed_v22/` ont déjà leur
dosage de famille. Un seul gain fixe de livraison est ensuite appliqué à
**l’ensemble du film**, afin de comparer le résultat à V21 au même niveau
intégré. Aucun réglage de loudness par scène, aucun limiteur agressif.

| Exemple | Pic du fichier traité avant gain commun | Pic estimé après gain commun | Traitement |
| --- | --- | --- | --- |
| Eau | −21,0 dBFS | −15,87 dBFS | Passe-bas 2,4 kHz ; entrée 35 ms, sortie 55 ms ; une couche. |
| Déchirure | −22,0 dBFS | −16,87 dBFS | Passe-bas 2,2 kHz ; attaque 6 ms. |
| Coupe de carotte | −21,5 dBFS | −16,37 dBFS | Passe-bas 2,4 kHz ; attaque 2,5 ms. |
| Première note sifflée | −23,11 dBFS | −17,98 dBFS | Même note, passe-bas 2,6 kHz, gain relatif −10 dB avant livraison. |
| Tissu | −29,5 dBFS | −24,37 dBFS | Friction originale 120–2000 Hz ; aucune attaque de déchirure. |

Ces valeurs décrivent la recette. Elles ne constituent pas un standard
universel de confort auditif. La part d’énergie 2–6 kHz de la première
déchirure passe de 67,8 % dans l’ancienne banque post-master à 24,6 % dans
la nouvelle ; la diminution d’aigus n’est pas une preuve d’écoute agréable.

## Gain unique et mesures du film

Le premier mix sobre mesurait **−30,13 LUFS**. Pour éviter une comparaison
qui gagnerait simplement en baissant tout le son, le coordinateur a retenu
un objectif de **−25 LUFS**, proche de V21 (−25,07 LUFS).

Un seul gain fixe de **+5,13 dB** (`delivery_gain_linear`) est donc calculé
sur le film entier et appliqué à tous les échantillons. Le test de 8 s est
extrait ensuite du même PCM final, sans normalisation séparée.

Mesures finales :

- intégré : **−25,01 LUFS** ; true peak : **−11,50 dBTP** ;
- RMS : **−27,29 dBFS** ; facteur de crête : **15,78 dB** ;
- différence P95–P05 des fenêtres RMS de 250 ms : **4,28 dB** sur le corps
  du film, de 2 s jusqu’à 0,5 s avant la fin ;
- occupation programmée du premier plan : **27,9 %** ; chevauchement de
  deux sons de premier plan : **0,78 %** ;
- aucun échantillon saturé, aucune coupure musicale liée à un changement
  de plan ou à un mouvement de MOU.

À niveau intégré comparable, V21 avait un true peak de −7,50 dBTP et un
facteur de crête de 20,20 dB. La nouvelle proposition réduit donc bien les
accents et la densité, au lieu de compter uniquement sur un volume moindre.
La comparaison ne vaut pas évaluation perceptive de la piste.

## Continuité et fin de huit secondes

La musique est rendue une fois par instrument sur sa grille globale, jusqu’à
48,25 s. Avant le nouveau dosage, son préfixe quantifié est identique à la
banque musicale précédente jusqu’à 40,5 s. La baisse au lavabo reste de
1,5 dB, avec transitions 500/700 ms. Le fond garde un gain de famille constant
de −2 dB avant le gain de livraison commun ; aucun pompage par plan.

La cuisson, très discrète, sort progressivement avant 40,25 s. Le test final
ne contient donc que le même fond musical et la friction de tissu de
**43,75 à 44,583333 s**. L’approche, les regards et la réaction finale restent
sans bruitage de premier plan. Il n’y a ni voix, ni jingle, ni « pop » de pensée.

`audio/test_fin_8s.wav` correspond exactement aux échantillons du mix final
de 40,25 à 48,25 s : 384 000 images PCM stéréo à 48 kHz.

## Reproduction et provenance

```sh
.venv/bin/python -B episodes/03/cuisine_v22/sources/son.py
```

Recette entière : lire uniquement les événements de `audio/provenance.json`,
sommer leurs fichiers PCM aux `start_sample`, appliquer l’enveloppe globale
d’entrée/sortie 8/35 ms puis arrondir en PCM16 ; appliquer ensuite le seul
`delivery_gain_linear` et arrondir. **Ne pas appliquer le master historique
aux nouveaux fichiers traités, ni sommer tous les WAV du dossier.**

Les originaux et leurs empreintes sont conservés ; l’ancien générateur reste
lisible dans `audio/historique/synthese_source_pre_v22.py.txt`. Les échantillons
d’instruments TimGM6mb sont tiers sous GPL-2, crédités avec FluidSynth dans
assets/. Les textures CC0 de recherche ne sont pas forcées dans ce montage :
une page tournée et un tap ne garantissent pas une déchirure ou une carotte.

Audits : `controle/audit_son.json`, `controle/audit_audio_v22.json`.
Les mesures, la provenance et la régénération sont vérifiées. **Aucune écoute
réelle ni certification du confort sur téléphone n’est revendiquée.**

## Gel et régénération du 29 octobre 2026

La régénération complète avec la chronologie à six cadrages a reproduit le
mix octet pour octet. Le changement de métadonnées caméra n’affecte ni la
partition ni les contacts. Les deux audits et `audio/provenance.json` portent
l’empreinte de la chronologie actuelle. Une somme indépendante des 41 fichiers
listés, avec les deux arrondis PCM et l’unique gain commun, reproduit aussi
exactement chaque échantillon du mix. L’extrait de huit secondes est identique
aux échantillons correspondants du film entier. Les 41 empreintes des fichiers
actifs ont été contrôlées.

- Mix : `d5e95dc32911c9087c797193ca750d66c82a546ad3355ebe210d6433bc68fc7b`.
- Extrait : `fb5b9b76dbc76bb3200222c94d713f15d7159d01f64541c7b7497b04da965b1a`.
- Source son : `f7ec60f0ab3781b0cf76895547f446f3ff99e8a7a107e1abbd0257a636566d0a`.

Ce gel établit la reproductibilité, la continuité de fabrication et les
limites de niveau. Il ne remplace pas une écoute humaine sur le support de
diffusion.
