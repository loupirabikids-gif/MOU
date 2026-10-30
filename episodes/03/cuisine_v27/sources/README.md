# Reproduire V27 — bande-son et images conservées

Python 3.11 minimum, requirements.txt, FFmpeg et FluidSynth. Ressources et
licences incluses ; aucun service payant ni téléchargement au rendu.
Depuis la racine du dépôt ou du ZIP extrait, après installation :

```sh
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/cuisine_v27/sources/son.py
.venv/bin/python -B episodes/03/cuisine_v27/sources/mux.py
.venv/bin/python -B episodes/03/cuisine_v27/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v27/sources/package.py
```

Le ZIP contient la vidéo muette de référence : mux.py copie son flux vidéo
sans réencoder le film complet, puis attache le nouveau mix AAC. L'aperçu
30–38 s est exporté séparément. Les sources SVG/Python V26 sont aussi incluses
pour une future animation ; leur chronologie est conservée à l'identique.
Le rendu graphique complet facultatif reste disponible via render.py.

son.py reconstruit les cues de base depuis raw_bank et les références V26
locales, puis ajoute music.py, foley_supplement.py et vocal.py. Le générateur
produit les stems séparés, la partition MIDI, la provenance, le mix de 38 s et
l'extrait exact30–38 s. Les deux silences sont appliqués aux cues avant sommation.
Le gain de livraison est fixe, sans normalisation LUFS ni gain par scène.

FluidR3_MOU_bossa.sf2 inclut les échantillons libres de guitare nylon et de
contrebasse. Les sources vocales OGG/WAV et leur notice CC0 sont conservées.
Leur procédé de création et leur auteur original ne sont pas vérifiés ;
les sons proposés ne sont pas présentés comme une voix humaine enregistrée
ou une imitation de Lamput validée à l'écoute.

L'archive contient un manifeste SHA256. Son contrôle à froid est enregistré
séparément dans controle/audit_archive.json pour éviter une empreinte circulaire.
Les contrôles numériques ne prouvent pas la douceur perçue ou l'humour.
