# Faisabilité : garder MOU ou simplifier le personnage

31 octobre 2026. Analyse des sources locales, sans fabrication, rendu ni reprise de la V29 arrêtée. Les témoignages publics sur Codex font l'objet d'une recherche séparée ; cette note n'en déduit aucun succès artistique ou commercial.

## Ce qui bloque réellement dans notre construction actuelle

Dans `mou_rig.py`, `_arm` mélange trois courbes — bras baissés, hanches, repli — puis élargit leur extrémité en demi-cercle. Le poignet et la paume n'ont pas de rotation autonome. Pour relever ou orienter une main, la chaîne actuelle change donc la courbe du bras entier. Cela peut donner des boucles latérales, des palettes ou des bouts de tubes, même lorsque le raccord est techniquement fermé. La critique V29 décrit précisément cette mauvaise lecture à 33,5–38 s ; un test de géométrie favorable ne l'annule pas.

Il existe aussi deux constructions de main : le bout arrondi du bras dans les plans larges et la moufle à pouce articulé de `mitten.py` / `sink.py` dans les inserts lavabo. Le gros plan a un petit vocabulaire de formes explicites que le plan large ne partage pas. Le corps élastique global de `performance.py` ne remplace pas cette articulation manquante. Le visage possède déjà yeux, sourcils et bouches contrôlables ; sa lisibilité dépend encore de la cible du regard, de la pose du corps et de la durée d'exposition, pas du seul nombre d'expressions.

## Deux voies possibles

| Voie | Construction proposée | Actions et limites |
| --- | --- | --- |
| **1. Conserver MOU, reprendre son articulation interne** — recommandation | Garder silhouette citron, deux yeux, costume et deux petits pieds. Créer une paire cohérente de moufles au petit pouce rond, avec orientation de poignet indépendante et raccord masqué proprement au bras. Préparer quelques dessins choisis : repos, moufle ouverte, pince, prise d'ustensile ; profils gauche/droite. Employer ces mêmes formes dans les plans larges et les inserts. Corps et bras peuvent garder une apparence continue. | Plus adapté à la cuisine : tenir un manche, montrer une trace et rincer les bouts de la moufle. Réduit le besoin de déformer tout le bras pour orienter la main. Les contacts, changements de profil et croisements restent à dessiner et vérifier. Cette voie modifie la construction interne et localement le dessin des mains ; elle est une proposition, pas une autorisation de les remplacer maintenant. |
| **2. Nouveau personnage : un petit galet expressif aux deux moufles flottantes** | Une seule forme ovale simple, deux grands yeux, deux sourcils, une bouche, deux petites moufles séparées du corps et deux pieds courts. Aucun bras ni raccord de poignet visible. Les moufles ont quatre dessins limités, sans doigts détaillés. Palette et nom à choisir ; aucun remplacement de MOU effectué. | Plus simple à piloter par SVG : déplacer et orienter chaque moufle indépendamment, tenir un objet sur une ancre fixe, lire le visage dans une silhouette stable. Son jeu vient du regard, de la compression du corps et de poses tenues. Les rotations 3D, prises complexes et torsions restent difficiles. Les mains flottantes sont un parti graphique à accepter ; elles ne conviennent pas à toutes les sensibilités. |

Les deux voies restent compatibles avec Python, SVG, CairoSVG, Pillow et FFmpeg. Changer de moteur ou ajouter un plugin ne choisira pas les bonnes poses à notre place. Je ne recommande pas de jeter MOU : son identité peut être conservée, mais répéter le même système de main sans revoir sa construction conserve sa limite.

## Le prochain résultat à demander : une seule petite action de 4,5 s

**La miette collante** : MOU repère une miette sur sa moufle gauche (0–0,8 s), la pince de l'autre main (0,8–2 s), constate qu'elle est maintenant collée à droite (2–2,6 s), regarde une main puis l'autre (2,6–3,5 s), puis le spectateur avec une expression retenue (3,5–4,5 s). Pas de décor complexe, musique ou texte explicatif.

Ce test doit montrer une pince vraiment en contact, deux mains reconnaissables avant/pendant/après, un déplacement de miette lisible, un regard vers la cause avant la réaction et une pose finale assez tenue. Le juger d'abord sans son et à la taille d'un téléphone. S'il ne convainc pas l'utilisatrice, ne pas décliner ce système sur un nouvel épisode complet. Il n'est pas fabriqué dans cette recherche.

Codex peut construire les commandes de pose, les dessins paramétriques, les trajectoires, les contacts et les exports reproductibles. Cela ne garantit ni jeu comique professionnel ni succès d'une chaîne. Les mesures ne prouvent pas qu'une émotion est reconnue ; l'écoute subjective de la bande-son reste indisponible au modèle dans cet environnement.
