# MOU original — sans son de cuisson

**[Voir la vidéo](MOU_Encore_une_feuille_sans_cuisson.mp4?raw=true)**

Reprise de la dernière version livrée avec le MOU original : V28, 38 secondes,
1080 × 1920, 24 images/s. Les images, le montage et les gestes sont conservés
par copie directe du flux H.264, sans nouveau rendu.

Seuls deux sons sont retirés : le fond de cuisson de 0 à 31,95 s, avec ses
crépitements et pops d'huile, et le dernier « tsss » de 32,60 à 32,95 s.
Les 61 autres événements restent aux mêmes gains et instants : musique,
sifflements, vocalisations, eau, papier, découpe et contacts des ustensiles.
Aucune normalisation ou remontée du volume ne compense ce retrait.

Les anciens films et le galet restent conservés. Cette correction ne reprend
pas la V29 interrompue et ne change pas le personnage.

## Sources et contrôle

Le [script](sources/retirer_cuisson.py) utilise les cues PCM et le manifeste
de [V28](../cuisine_v28/), déjà conservés dans le dépôt. Il vérifie d'abord
que leur somme reproduit exactement le WAV livré, puis retire uniquement les
deux cues, avec le fondu global et le gain fixe d'origine. La piste finale
est encodée en AAC 160 kbit/s ; l'encodage est avec pertes.

```bash
.venv/bin/python -B episodes/03/cuisine_v28_sans_cuisson/sources/retirer_cuisson.py
```

[Contrôles et empreintes](CONTROLE.json) : vidéo H.264 identique, 912 images,
durée audio/vidéo de 38 s, absence d'écrêtage PCM, silences préservés et
résultat PCM conforme à une reconstruction indépendante. Tous les fichiers
sources d'origine restent inchangés. Le modèle ne peut pas écouter ; ces
contrôles ne constituent pas une appréciation des timbres ou du confort.
