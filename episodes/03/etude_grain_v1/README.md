# MOU — Le grain, essai muet

**[Voir l'essai de cinq secondes](MOU_Le_grain_5s_muet.mp4?raw=true)**

[Trois poses](MOU_trois_poses.png) ·
[Assurance](01_assurance.png) · [Résister](02_resistance.png) · [Céder](03_cede.png) ·
[Sources ZIP](MOU_Le_grain_sources.zip?raw=true).

MOU veut cuisiner malgré un grain de sel sur sa moufle. Il reprend sa cuillère,
s'arrête, puis donne toute son attention à ce minuscule problème. C'est un
essai de jeu du MOU original, sans texte explicatif, musique ou vocalisation.
Les labels sous la planche de poses ne figurent pas dans la vidéo.

1080 × 1920, 24 images/s, cinq secondes. Le dessin du personnage, les bras
natifs et le lavabo existant sont réutilisés. Les anciens films restent
conservés. Aucune approbation artistique ou réussite comique n'est déduite
des seuls contrôles techniques.

[Découpage et corrections](developpement/decoupage.md) ·
[Critique des poses](developpement/critique_poses.md) ·
[Critique du montage](controle/critique_montage.md) ·
[Contrôles](controle/QA.md).

La revue a fait corriger deux expressions trompeuses, puis la première
tentative de reprise trop discrète. Le HD final a été revu sur des images
décodées et comparé à des rendus frais : bras natifs, contacts, grain fixé à
la moufle puis emporté dans l'eau, 120 images et aucune piste audio. Cela
ne constitue pas une validation de l'effet comique par des spectateurs.

## Reproduction

Python, NumPy, Pillow, CairoSVG et FFmpeg, avec les dépendances du dépôt :

```bash
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/etude_grain_v1/sources/etude.py --poses
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/etude_grain_v1/sources/etude.py --preview
XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/etude_grain_v1/sources/etude.py
```

`etude.py` est le producteur de cet essai. Les modules et chronologies copiés
de V30 conservent les dépendances du rig et des accessoires ; leur durée
historique de 38 s ne correspond pas à l'horloge de cette étude. Le producteur
utilise uniquement cinq secondes et n'importe aucun ancien film ou piste son.
