# Petite équipe MOU

La règle commune est [AGENTS.md](../AGENTS.md). Les cinq profils Codex natifs
sont dans [.codex/agents](../.codex/agents) et déclarés par
[.codex/config.toml](../.codex/config.toml). Le coordinateur reste responsable
du choix artistique, de la répartition des fichiers et de l'intégration.

| Rôle | Livrable principal | Dépendance avant validation |
| --- | --- | --- |
| Veilleur éditorial | Veille datée et sources vérifiables | Accès réel aux publications |
| Scénariste comique | Cinq idées distinctes, choix et faiblesse | Veille disponible et caractère de MOU |
| Responsable du découpage | Actions, intentions, regards, storyboard et son | Scénario choisi |
| Critique indépendant | Problèmes réels, instants et corrections | Scénario, puis montage effectivement produit |
| Réalisateur animation et son | Animatique, corrections et exports | Découpage revu et chronologie commune |

Le coordinateur lance les tâches indépendantes en parallèle, attribue un seul
propriétaire par fichier et fait les raccords entre étapes. Il clôt une version
avant le calcul qui la lit. Animation et son peuvent être délégués séparément
une fois les instants communs stabilisés.

## Utilisation et compatibilité

Voir [compatibilite_agents.md](compatibilite_agents.md) pour les preuves du
support local, les conditions de chargement et les limites de la session.
Enregistrer des profils ne prouve pas que le client courant les a chargés.
Si le client ne sait pas sélectionner un type d'agent, le coordinateur peut
lire les instructions du profil et les transmettre comme mandat borné à un
sous-agent normal. Les mêmes règles et livrables s'appliquent.
Aucun modèle, accès secret, serveur ou droit supplémentaire n'est imposé.

## Dossiers conservés

- `editorial/` : veille externe datée, sources et éventuels blocages.
- `episodes/NN/developpement/` : cinq pistes, scénario choisi, découpage,
  critique avant fabrication et journal des corrections.
- `episodes/NN/controle/` : critique du vrai montage, planches et audits.
- `episodes/NN/sources/` et `sons/` : fabrication reproductible.
- `publication/` : résultats accessibles de nos propres diffusions et hypothèses.

Les [modèles](modeles/) sont des aides à une collecte honnête, pas des cases
à remplir artificiellement. Le pilote existant peut être amélioré pendant qu'un
accès externe nécessaire à la veille est débloqué ; cela reste explicitement
une révision interne, pas une création appuyée sur une veille récente complète.
