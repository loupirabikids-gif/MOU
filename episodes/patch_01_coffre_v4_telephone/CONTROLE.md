# Bilan — correctif local des prises du téléphone

Film de 30 s, 1080 × 1920, à 24 images/s. La version sonore et la version
muette partagent le même flux H264. La V4 initiale est conservée.

Les trois défauts observés sur ses vraies images sont corrigés : poignet
retourné instantanément au lâcher, bascule inverse à la reprise, puis face
écran devenue dos à la coupe sans retournement montré. Le dépôt marque une
courte pause, la patte se desserre puis se retire ; le poignet est orienté
avant la reprise. La tranche est visible à 24,500 s et le dos est établi
à 24,667 s, avant le changement de plan.

La [critique indépendante](controle/critique_finale.md) examine d'abord les
images consécutives de l'animatique, puis 38 images du véritable MP4 HD,
dont huit vues générales. Les défauts ciblés sont levés sur ces passages ;
aucun nouveau défaut bloquant n'y est observé. Ce n'est pas un test public.

La [QA finale](controle/qa.json) passe 16 contrôles ciblés. Les rotations
maximales par image aux gestes corrigés passent d'environ 85° à 16–18°,
avec fermeture/ouverture progressives et contacts continus. La pause, le
retrait, la fermeture et le retournement sont vérifiés sur les images rendues.
Douze images décodées du HD concordent avec des rendus frais hors cache.

**Les 632 PNG HD hors des fenêtres du correctif sont identiques à ceux de
la V4.** Le personnage, le rig, les vues, placements et chronologie restent
inchangés. Cette invariance porte sur les images sources du rendu ; les
octets de la compression MP4 sont contrôlés séparément.

Le WAV, le flux AAC encodé, les stems et les 18 cues sont identiques à la V4.
Aucun nouveau son, musique ou voix. Aucune écoute réelle n'est revendiquée.
Les huit références protégées et les quatorze fichiers gelés sont intacts.

Depuis le [ZIP extrait](controle/reproduction.json), seize PNG frais et
le WAV complet se reconstruisent à l'identique, sans V4, cache de rendu
ou réseau. Aucune identité binaire des MP4 n'est revendiquée. La QA de
préservation des anciennes références exige le dépôt complet.

SHA-256 du film avec son :
`e555c0589e92f48aabe3df8186fe6a3be6de1fef0d6aacd0cf15526b22966680`.

SHA-256 de la version muette :
`3bc36cb07979bebce909bae47e7020bcbb1e9eb2691778a06442249ad78158c0`.
