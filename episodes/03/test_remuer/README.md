# Test du geste : MOU remue la poêle

**4 secondes · 1080 × 1920 · 24 images/s · muet.**
Étape demandée après validation du décor et du placement.

[![Aperçu du geste](MOU_test_remuer_apercu.gif)](MOU_test_remuer.mp4?raw=true)

- **[Voir le MP4](MOU_test_remuer.mp4?raw=true)**
- [Bilan des contrôles](CONTROLE.txt)
- [Critique du premier rythme](controle/critique_rendu_v1.md)
- [Sources](sources/) · [Paramètres](TEST.json)

MOU tient une cuillère et effectue deux tours dans la poêle. Le bras du côté
papier conserve exactement la pose validée ; le bras qui remue utilise son
tracé original articulé autour de l’épaule. Corps, décor et placement
(80,380,2,30) sont conservés. La cuillère garde sa longueur et sa prise dans
la moufle. Le regard suit le geste et un bref clignement conserve le jeu du rig.

Le premier rythme avait des passages presque immobiles trop longs. Seule sa
progression temporelle est corrigée pour démarrer plus vite et terminer par
une courte tenue. Le geste reste à apprécier par l’utilisatrice sur ce test.

## Reproduction

Dans l’environnement du dépôt, avec Python, CairoSVG, Pillow, NumPy et FFmpeg :

    XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/test_remuer/sources/render.py --preview
    XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/test_remuer/sources/render.py
    XDG_CACHE_HOME="$PWD/work/font-cache" .venv/bin/python -B episodes/03/test_remuer/sources/verify.py

Le moteur lit le décor validé et le rig, sans les réécrire. Il conserve
source complète dans la signature du cache, copies atomiques et PNG distincts.
frames/ et cache/ sont des fichiers de travail exclus de Git.

Ce test porte seulement sur prise et remuage : aucun essuyage, son, nouvel
ingrédient ni montage de l’épisode n’est ajouté. Les images décor/placement
approuvées restent dans leurs dossiers séparés.
