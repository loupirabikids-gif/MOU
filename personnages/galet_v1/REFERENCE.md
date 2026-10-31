# Galet v1 — référence commune du prototype

L'utilisatrice a sélectionné le nouveau personnage proposé : petit galet souple,
deux grands yeux, deux moufles flottantes et deux petits pieds. Son assurance
est démesurée devant des contrariétés minuscules. Ce choix autorise le dessin
et l'essai court ; les épisodes MOU et la V29 interrompue restent conservés.

Nom de travail : **Galet**, pas un nom de série définitivement choisi.
Palette initiale vert citron, annoncée comme défaut dans la question ouverte.
Aucun dessin, sprite, personnage ou gag tiers repris. Outils de production :
Python, SVG, CairoSVG, Pillow et FFmpeg, tous gratuits et open source.

## Construction

- Corps ovale compact et souple, déformation ancrée au bas du corps.
- Deux yeux blancs, deux pupilles masquées, deux sourcils et une bouche.
- Deux petites moufles flottantes, avec un seul pouce distinct arrondi.
  Pas de bras, de doigts détaillés ou de raccord de poignet.
- Deux petits pieds sombres, stables au sol.
- Chaque moufle garde sa taille ; elle possède position, rotation et fermeture
  du pouce indépendantes du corps. Les ombres n'ajoutent aucun membre.

## Essai muet « La miette collante » — 5 s / 24 images/s

1. 0–0,70 : assurance, puis regard attiré par la miette sur la moufle gauche.
2. 0,70–1,20 : la droite approche avec une intention précise.
3. 1,20–1,80 : contact, fermeture du pouce et retrait. Transfert à 1,60 s.
4. 1,80–2,70 : les mains se séparent ; gauche propre, droite portant la miette.
5. 2,70–3,80 : regard vers la droite, constat de l'échec, hésitation.
6. 3,80–5,00 : retour vers le public et sourire pour sauver les apparences.
   Les 0,5 dernières secondes sont tenues exactement.

La miette est contrastée et reste assez grande pour être lue sur téléphone.
Le transfert suit les vrais contours : l'ancre de la moufle droite est amenée
sur celle de gauche avant le changement de parent. Le masque des mains ne doit
pas les fusionner au point de perdre l'action. La caméra reste fixe.

## Répartition et contrôle

Le coordinateur possède les producteurs `sources/rig.py`, `animation.py` et
`render.py`. Le critique possède les critiques et ses preuves privées ; la QA
possède `controle/verify.py` et ses rapports. Aucune édition concurrente.
Critiquer les vrais rendus puis l'export ; ne pas assimiler mesures, préférence
de l'utilisatrice et qualité professionnelle. Le test muet ne valide aucun son.
