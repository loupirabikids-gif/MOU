# Reproduire Encore une feuille

Depuis la racine du dépôt ou de l’archive des sources, avec Python3.11minimum,
FFmpeg et les bibliothèques système Cairo installés :

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/film/sources/son.py
.venv/bin/python -B episodes/03/film/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/film/sources/render.py --workers 3
.venv/bin/python -B episodes/03/film/sources/verify.py
.venv/bin/python -B episodes/03/film/sources/package.py
```

L’animatique légère est540×960à12images/s. L’export complet est1080×1920à24images/s,
26s. Le rendu produit la version muette puis copie exactement son flux vidéo
pour y ajouter le mix original en AAC. Les sources sont gelées par empreinte
pendant chaque rendu et les images du cache sont copiées atomiquement.

`animation.py` fournit les poses du rig et les contacts ; `art.py` dessine les
accessoires ; `render.py` compose les calques du décor validé et les caméras ;
`son.py` synthétise les bruitages ; `verify.py` contrôle les exports réellement
décodés et13images reconstruites indépendamment du cache. `package.py` rassemble
les dépendances du projet dans une archive sans les images intermédiaires.

Le modèle original, les dessins validés et le test de remuage ne sont pas
réécrits. Les gestes utilisent les mêmes bras et moufles ; seule la petite
jonction extérieure du bras gauche avec le corps est raccordée en tangence,
avec sa frontière de remplissage et son encre. Dans les
plans d’évier, le même bras est réorienté par une isométrie pour laisser le
filet d’eau visible. Aucun étirement ni nouvelle main n’est dessiné.
La main/avant-bras sont uniformément réduits dans les seuls inserts lavabo,
avec une légère correction de contact avec le jet. Le modèle du plan large
et les contacts de commande restent conservés.

Les contrôles numériques et les images extraites ne remplacent pas une écoute
sur un appareil ou le jugement du public. Les revues précisent leur méthode.
