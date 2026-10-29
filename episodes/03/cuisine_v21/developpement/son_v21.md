# Continuité sonore de la nouvelle fin

Le mix V20 est conservé exactement en PCM jusqu’à 40,5 s. Il est reconstruit
depuis le mix V19 fourni et le même contact de papier au sol à 39,85 s :
aucun WAV de référence supplémentaire n’est nécessaire.

Les 70 WAV de référence restent inchangés : 64 événements V19, quatre stems,
une référence musicale sans baisse et le contact de sol V20. La musique
`music.py` reste également inchangée. La durée finale devient 44,5 s.

La continuation reprend la partition originale sur sa grille globale à
108 BPM. Les mêmes instruments FluidSynth/TimGM6mb et la calibration
fixe `1.2217762480997532` sont employés ; aucun nouveau calcul de niveau.
Le préfixe musical quantifié est comparé échantillon par échantillon à la
piste précédente avant le raccord. Les notes poursuivent la même forme ;
aucun bouclage audio ni redémarrage de phrase à l’image.

Le raccord se fait de 40,5 à 40,75 s, avant l’ancienne sortie musicale qui
commençait à 40,78 s. Les deux musiques sont en phase et utilisent un mélange
linéaire lissé, pour éviter la bosse de +3 dB d’un mélange à puissance égale.
Le bruit de cuisson, indépendant, utilise un raccord à puissance égale.
Son niveau reste celui de l’ancienne tenue finale, soit 0,55 du bruit initial.
La nouvelle texture de cuisson est synthétisée localement, sans boucle musicale.

Un seul bruitage nouveau accompagne le contact : un frottement doux de tissu
de 42,0 à 42,4 s, pic −35 dBFS avant le master fixe d’origine. L’approche
de 41,85 à 42,0 s et le retrait de 42,4 à 42,65 s restent sans friction. Aucun son
de goutte tant qu’elle pend à la moufle, aucune voix ni ponctuation de révélation.
La musique continue pendant la gêne finale, puis sort à la fin du fichier.

Nouveaux assets modifiables :

- `musique_extension_v21.wav` : même partition, pré-master, 40,5–44,5 s ;
- `cuisson_extension_v21.wav` : bruit de cuisson discret, même intervalle ;
- `tablier_essuie.wav` : friction de tissu, contact effectif 42,0–42,4 s.

Les anciens fichiers restent des banques de référence. Ils ne doivent pas
être sommés une seconde fois au mix figé : la recette complète figure dans
`audio/provenance.json` et dans le programme `sources/son.py`.

Reproduction depuis la racine du dépôt, avec Python/NumPy et la bibliothèque
libre FluidSynth installée :

```sh
.venv/bin/python -B episodes/03/cuisine_v21/sources/son.py
```

Contrôles : identité PCM du préfixe, musique quantifiée en phase, fenêtres
musicales de 100 ms par pas de 20 ms autour de la prolongation, sauts aux
bornes du raccord, absence de saturation et régénération déterministe.
Les résultats sont dans `controle/audit_audio_v21.json`.

Recalage après observation du vrai contact : l’ancien bruit de tissu couvrait
41,85–42,65 s. Il est limité à 42,0–42,4 s. La comparaison des deux mix PCM
confirme l’identité de tous les échantillons avant 41,85 s et après 42,65 s ;
la musique et son raccord restent donc strictement inchangés. Cette preuve
figure sous `cloth_retiming_check` dans le rapport audio.

Ces contrôles sont numériques. Aucune écoute humaine, appréciation du mix
sur téléphone ou validation par un public n’est revendiquée.
