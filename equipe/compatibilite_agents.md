# Agents personnalisés — compatibilité vérifiée

Observation : 2026-10-27T19:41:04+01:00 (Africa/Casablanca).

Les cinq profils sont enregistrés dans `.codex/agents/` et référencés par
`.codex/config.toml` dans ce dépôt. Aucune configuration globale, aucun secret,
aucun choix de modèle et aucune permission de sandbox n'ont été modifiés.
Le coordinateur reste le rôle principal régi par `AGENTS.md`.

| Nom natif | Mission |
| --- | --- |
| `veilleur_editorial` | Veille récente et publications ordinaires comparables, preuves et limites. |
| `scenariste_comique` | Cinq idées différentes, évaluation et choix motivé. |
| `responsable_decoupage` | Storyboard chronométré, actions, regards et son. |
| `critique_independant` | Critique du scénario puis du montage réel, corrections vérifiées. |
| `realisateur_animation_son` | Animatique complète, animation, effets originaux, corrections et exports. |

## Preuves de compatibilité

- Binaire installé : `codex-cli 0.163.0` (`/opt/codex/bin/codex`).
- `codex -C /workspace/MOU features list` réussit (code0), avec
  `multi_agent stable true`, sans avertissement de rôle malformé.
- Les six fichiers TOML sont analysés et validés contre le schéma officiel du
  **tag correspondant exactement au binaire**, `rust-v0.163.0`. Le validateur
  Python a vérifié les noms, descriptions, instructions non vides et chemins.
- Le parseur officiel accepte `name`, `description`, `developer_instructions`
  dans les fichiers de rôle et retire les métadonnées avant de charger leur
  configuration. Le chargeur sait lire les tables `[agents.nom]` et découvrir
  `.codex/agents/*.toml` dans les couches de configuration actives.
- Les profils n'imposent aucun modèle, effort de raisonnement, service payant,
  nouvelle fonctionnalité expérimentale ou assouplissement des permissions.

Sources officielles consultées :

- [Schéma exact0.163.0](https://raw.githubusercontent.com/openai/codex/rust-v0.163.0/codex-rs/core/config.schema.json)
- [Parseur des fichiers de rôle](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/agent-roles/src/agent_role_config.rs)
- [Chargement et découverte des rôles](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/agent-roles/src/loader.rs)
- [Application des instructions de rôle](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/agent/role.rs)

## Enregistrement et activation sont distincts

Ces définitions sont prêtes pour une session Codex qui charge la configuration
projet de MOU, selon les règles de confiance du projet et du client. Ouvrir ou
recharger une telle session depuis la racine du dépôt permet au client natif de
les découvrir. L'enregistrement des fichiers ne prouve pas un rechargement de la
session cloud déjà active.

L'outil de délégation disponible dans ce chat ne propose pas de champ
`agent_type` permettant de sélectionner directement un de ces noms. Dans cette
session, le coordinateur peut lire les instructions des profils et les remettre
explicitement aux agents de travail, avec leur périmètre exclusif de fichiers.
C'est un usage opérationnel des rôles, pas la preuve de leur activation native.

Une tentative locale de lecture via `codex --strict-config app-server` n'a lancé
aucun agent ou appel de modèle : le serveur s'est arrêté avant initialisation,
car son état SQLite dans `/run/codex-environment/codex-home` n'était pas
initialisable dans ce contexte protégé. Aucun changement de ce répertoire ni de
`CODEX_HOME` n'a été tenté. `--strict-config` n'est par ailleurs pas accepté par
la sous-commande `features` de cette version ; la validation de schéma et le test
`features list` ci-dessus sont donc rapportés séparément.

Il n'est pas nécessaire de débloquer ce serveur local pour travailler avec
l'équipe déjà disponible. Ne pas annoncer « agents natifs activés dans le chat »
sans observation ultérieure du client qui les charge. Les profils restent
lisibles, versionnables et transférables avec le dépôt.
