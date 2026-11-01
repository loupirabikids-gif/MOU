# Bilan V30 — MOU original

38 secondes, vertical 1080 × 1920, 24 images/s. Version avec son, version
muette et sources disponibles depuis le [dossier de l'épisode](README.md).

## Changements

- Jazz abaissé de 6 dB constant. Les cinq vocalisations et les autres effets
  conservent leurs sources PCM, niveaux et instants. Aucun nouveau son.
- Les deux cues de cuisson restent exclus, y compris crépitements, pops
  d'huile et dernier « tsss ». Les 61 événements restants sont conservés.
- Même rig, bras et moufles natifs. Jeu du visage et du corps plus contrasté :
  inspection outrée, contrariété progressive, décision suspendue, choc puis
  déception, fausse fierté devant les mains propres.
- Phrase d'origine remise en haut : « Me cooking: touch, wash, wipe… repeat. ».

## Revue et correction

La critique a examiné l'animatique complète puis les vrais exports HD.
La première version HD montrait une bouche de choc partiellement masquée
par le tablier. Après une légère réduction et remontée locale de cette
bouche, l'animatique et le HD ont été réexportés. La seconde revue a levé
cette réserve sur le vrai MP4, transition comprise. Les corps et bras n'ont
pas changé dans ce correctif. Voir le [journal](developpement/corrections.md)
et la [critique finale](controle/critique_finale.md).

## Preuves conservées

QA finale passée sur l'export corrigé : 912 états, 42 images HD fraîches,
21 images de la transition du choc sans recouvrement bouche/tablier/yeux.
Les versions son et muette ont un flux H.264 identique. Les anciens fichiers
protégés restent inchangés.

- [QA finale](controle/qa_v30.md) et [détails/empreintes](controle/qa_v30.json) :
  états, contacts, silhouettes natives, lavabos, poses vocales, pauses,
  flux vidéo et comparaison du vrai HD avec des rendus frais hors cache.
- [Reconstruction sonore autonome](audio/audit_autonomie.json) et
  [gel des entrées/sorties](audio/gel_son.json). Les mesures de rapport
  voix/jazz sont détaillées dans la [note de mix](developpement/mix_v30.md).
- [Reproduction visuelle à froid](controle/audit_reproduction.json) : cinq
  SVG et PNG540 identiques à partir d'une copie minimale sans V28/Galet.
- [Intégrité de l'archive](controle/audit_archive.json) : CRC et empreintes
  des fichiers inclus. L'archive exclut les caches et anciens films ; les
  fichiers nécessaires à la reconstruction de V30 sont inclus.

Les contrôles numériques et la critique par images ne remplacent pas une
écoute ou une réaction de spectateurs. Le modèle ne peut pas écouter dans
cet environnement. Aucune approbation artistique de l'utilisatrice ni
qualité professionnelle ou réussite publique n'est déduite de ces contrôles.
