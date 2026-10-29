# Son ciblé de la chute V20

Le mix V19 est conservé comme entrée PCM dans `audio/mix_reference_v19.wav`.
Son empreinte SHA-256 est
`8ddc8746a5ec7ae7d5914a29245eb1033982029c2e1b3b4fd1b7cb415ac5874a`.
Ses 64 événements, dont 63 bruitages/sifflements et une piste musicale,
gardent leur fichier, leur instant, leur panoramique et leur dosage.
Les quatre stems instrumentaux et la référence musicale sans baisse restent
également identiques. Aucun nouveau rendu de musique ni normalisation.

L’impact existant à 39,1 s correspond au contact sur le tas débordant.
Un seul bruit original est ajouté au contact du sol de la chronologie :

- début : `overflow.floor_land`, 39,85 s ; durée : 120 ms ;
- nom : `c5_papier_sol.wav`, grain déterministe 3041672 ;
- bruit amorti à 160–1600 Hz, léger pli à 700–2700 Hz ;
- pic avant master : −37,5 dBFS ; panoramique : −0,35 ;
- master conservé : 2,124210976406158, sans modification du niveau global.

Le nouveau fichier individuel suit la convention des banques pré-master.
Sa contribution calculée en NumPy est multipliée par le master d’origine,
arrondie en entiers PCM16 puis ajoutée à la base PCM. L’addition ne touche
aucun échantillon hors de la fenêtre 39,85–39,97 s. Le script vérifie aussi
que tous les anciens WAV ont les empreintes de la provenance V19.
Le WAV de base et les JSON de provenance/audit d’origine sont inclus afin
que l’archive autonome puisse reproduire exactement cette opération sans
dépendre d’un ancien dossier ou de FluidSynth pendant ce correctif.
La synthèse originale reste lisible dans les fonctions de `son.py` ; son
ancien point d’entrée a été renommé `legacy_full_synthesis` et n’est pas
appelé par la commande V20.

Reproduction depuis la racine du dépôt :

```sh
.venv/bin/python -B episodes/03/cuisine_v20/sources/son.py
```

Le contrôle dans `controle/audit_son_chute_v20.json` compare la base et le
résultat, exige l’identité PCM avant/après l’ajout et l’absence de saturation.
Il ne constitue pas une écoute. Le modèle ne dispose pas d’entrée audio
dans cette session ; aucune appréciation auditive ou validation sur le
haut-parleur d’un téléphone n’est revendiquée.
