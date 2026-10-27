# Restauration des bras du modèle original

Demande utilisateur : laisser les bras comme avant. Le contrôle porte sur la
conformité au modèle fourni et sur la limitation de la modification aux bras,
par rapport au montage `302c87033374255fc7a9f8d5b1025a8eb2ebc6d7`.
Aucun nouveau dessin ni changement de jeu n’est proposé par cette revue.

## Source et portée de la correction

Les adaptations `arm_controls` et `episode_arm` sont supprimées. Les bras
émis directement par `mou_rig.character_fragment` restent dans le personnage.
Les deux fragments `_arm` du rig sont retrouvés strictement dans chacune des
312 poses, avec les mêmes paramètres `arm_hips` et `arm_clasp` qu’avant.
Le fichier `mou_rig.py` lui-même reste inchangé.

Comparaison indépendante des 312 instants à24i/s avec le commit de référence :

- dictionnaires de pose, mouvements et déformations strictement identiques ;
- chemins de bouche strictement identiques ;
- après retrait des seuls groupes `arm-left` et `arm-right`, tout le SVG du
  personnage est strictement identique ;
- actions et temps de la chronologie identiques, hors métadonnées de révision,
  note de restauration et fixation du cadrage photographique ;
- `sources/son.py`, le mix WAV et le rig original sont byte-identiques.

Le cadrage de la photo est fixé à celui du montage précédent pour que le
retour aux bras d’origine n’entraîne pas de recadrage automatique. Une seconde
comparaison avec la fonction photographique du commit302c870 confirme que
le SVG entier du cliché — fond, ombre, placement, corps et visage — reste
strictement identique après retrait des seuls deux groupes de bras.

Preuves de calcul dans `work/controle_restauration_bras/scope.json` et
`photo_scope.json`. Ces fichiers de travail n’ont modifié aucune source.

## Vérification du véritable encodage

Montage léger examiné : `premier_montage.mp4`,540×960,13s.
SHA256 : `af283c40ac6b744d9f37c8b02024462866bab11f1ebb59e65b908d15c321356a`.

Trois images réellement décodées ont été examinées à2,25s,6,125s et12,5s :
pose aux hanches, déformation capturée et réaction finale. Les bras du rig
sont visibles dans ces trois cas ; les poses et le déroulement restent ceux
du montage précédent.

Les pixels qui distinguent les bras restaurés de l’adaptation supprimée sont
comparés à deux rasterisations fraîches. L’erreur moyenne vers les bras du
rig est de4,55à5,79/255 sur ces pixels, contre137à138/255 vers l’adaptation
supprimée. Cela confirme que le fichier encodé contient la restauration,
et non une ancienne image de cache. Preuves : `encode.json`,
`encode_retabli.png` et `encode_retabli_*.png` dans le même dossier de travail.

**Accord de conformité pour l’export final.** Cette revue ne demande aucun
réajustement esthétique des bras. Elle concerne le montage léger ; les
contrôles de fidélité et de format du final1080×1920 sont effectués séparément
par le coordinateur. Aucune écoute humaine ni test public n’est revendiqué.
