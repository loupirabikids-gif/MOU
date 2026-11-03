# Licences et provenance — voix PATCH V1

Les douze WAV maîtres, les recettes originales et les fichiers de paramètres
ont été fabriqués pour ce projet. Les vocalisations sont synthétiques :
aucun enregistrement tiers ni timbre d'une personne réelle n'est utilisé.

**Créations originales du projet : droits conservés.** Aucune licence de
réutilisation publique n'est accordée ici aux WAV, recettes, paramètres ou
scripts originaux du projet PATCH. Leur visibilité dans le dépôt ne constitue
pas une dédicace au domaine public ni une autorisation de réutilisation.
Le manifeste indique `NOASSERTION` pour ces prises :
« Original audio for PATCH; no public reuse licence assigned ».

Les licences des outils et composants tiers restent applicables à ces seuls
composants, selon leurs textes respectifs. La GPL du synthétiseur ne devient
pas automatiquement la licence d'un WAV original qui ne reprend pas de
matériau protégé du paquet. Les textes tiers ci-dessous sont conservés sans
modification ; aucun nouveau droit public n'est attribué aux créations PATCH.

| Outil effectivement exécuté | Version | Licence du code | Source fixée |
| --- | --- | --- | --- |
| Soundgen | 3.0.0 | GPL≥2 | https://github.com/cran/soundgen/tree/ea27b027896d4aab7bddf349e6687013c6c78d98 |
| tuneR | 1.4.7 | GPL-2 ou GPL-3 | https://github.com/cran/tuneR/tree/ee0ec05b00ad9c886d9cdf45bae8d586c4e82d08 |
| signal | 1.8-1 | GPL-2 | https://github.com/cran/signal/tree/5eff0e48052444c44e2f4776f28e8b0b8e036cc3 |
| phonTools | 0.2-2.2 | BSD2clauses | https://github.com/cran/phonTools/tree/760ad82606113512c48a864fb0e86fd14c121cf8 |
| R | 4.5.0 | GPL-2 ou GPL-3 selon les composants | Paquet officiel Debian, URL/SHA dans `controle/runtime_packages.json` |

Les DESCRIPTION des quatre paquets et le texte BSD de phonTools sont inclus
dans `licences/`. Les archives tierces, leurs binaires et leurs données de
démonstration restent dans le runtime privé, pas dans cette banque. Aucun
poids neuronal, preset vocal enregistré ou audio d'exemple n'a été copié.
La voix vient de l'exécution de nos paramètres numériques.

Référence scientifique demandée par Soundgen : Anikin,A.(2019).
*Soundgen: an open-source tool for synthesizing nonverbal vocalizations*.
Behavior Research Methods,51(2),778–792.
https://doi.org/10.3758/s13428-018-1095-7

Les URLs/commits, empreintes d'archives, graines, paramètres et empreintes de
WAV servent de preuves de fabrication. Les étiquettes émotionnelles restent
des intentions. Ni les licences ni les contrôles ne constituent une audition.
