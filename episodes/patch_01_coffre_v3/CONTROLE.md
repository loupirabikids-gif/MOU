# Bilan — reconstruction du jeu de PATCH

Livrables : 30 secondes, 720 images à 24 images/s, 1080 × 1920.
La version avec son et la version muette partagent le même flux H264.
Les anciens épisodes et la référence conceptuelle sont conservés.

La reconstruction emprunte à la référence fournie ses intentions de jeu :
joue soutenue par la patte, bras croisés, tête près du plateau, puis joie
corporelle. Les nouvelles poses sont dessinées et animées dans le rig du
projet. Aucune image ou bande-son de la vidéo privée n'est réutilisée.
Le téléphone volontairement enfermé, les trente minutes et la liste restée
intacte donnent les repères de récit qui manquaient à cette référence.

Les [critiques du vrai montage](controle/critique_finale.md) distinguent
poses, animatique et HD. Les premières images ont conduit à ouvrir la
bouche de joie, puis à élargir et remonter le plan du rebond pour garder les
oreilles dans le cadre. Le carton est retiré pendant ce geste. La revue des
images décodées du vrai MP4 final ne retient plus de défaut visuel bloquant
sur les passages inspectés. Il s'agit d'une revue interne, sans test public.

La [QA indépendante](controle/qa.json) passe 22 contrôles ciblés :
720 états SVG, 29 minutes, regards et retours au travail, prises, profondeur,
liste sans coche, ressources et cadrages. Soixante échantillons de raccords
manche/patte et cinq appuis joue/paume sont vérifiés sur des rendus réels.
Dix-huit silhouettes de tête restent cadrées, dont le sommet de la joie.
Douze images décodées du HD concordent avec des rendus frais hors cache.
Les six références protégées et les dix fichiers gelés sont intacts.

Depuis le [ZIP extrait](controle/reproduction.json), quatorze PNG frais et
le WAV complet se reconstruisent à l'identique, sans ancien dossier,
cache ou réseau. Aucune identité binaire des MP4 n'est revendiquée.

La banque et le mix sont identiques à ceux de la V2 : 18 effets courts,
PCM16 stéréo 48 kHz, aucun écrêtage, stems conformes. Les contacts restent
aux mêmes instants et les métadonnées correspondent à la chronologie V3.
Pas de bruit d'écriture, de nouvelle musique ou voix. Les derniers gestes
et le résultat peuvent se lire dans le silence.

**Limite d'écoute :** aucune audition réelle du mix n'est disponible ici.
Les contrôles de niveaux et de synchronisation ne certifient pas son confort
ou son effet comique. Les revues ne promettent ni réception publique ni
cadence hebdomadaire déjà validée.

SHA-256 du film avec son :
`ef4e807907f60182682d43bfb8e107ce8cc1fbdfa73487225981b38a4ce6b566`.

SHA-256 de la version muette :
`06ee0d3032f19870143b70b9cf0c49e56ad98fcf5877df8dd2ac1218b266bcf4`.
