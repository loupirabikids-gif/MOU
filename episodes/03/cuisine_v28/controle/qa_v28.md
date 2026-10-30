# Contrôle indépendant V28 — passé

Exécution complète du vérificateur après gel des sources et des exports.
Deux MP4 de 38 s, 1080 × 1920, 24 images/s, 912 images, décodés sans erreur.
La vidéo H.264 est identique entre version son et version muette.

## Raccords et périmètre

- 912 SVG : deux moufles dans les plans du personnage, une dans les inserts
  lavabo ; masques, identifiants, costumes, stocks et quatre rinçages vérifiés.
- 1488 contours émis de bras/moufles comparés au rig natif, hors raccord local
  gauche autorisé de 24 px ; les prises sont recalculées depuis les contrôles.
- Erreur maximale de prise recalculée : 7.06e-08 px.
  Dérive maximale des ancres de pieds : 5.92e-07 px.
- V27 chargée dans un processus séparé : 798 états physiques précédant 33,25 s
  strictement identiques. 781 SVG hors des deux fenêtres de respiration et de la
  présentation finale sont identiques ; 120 SVG diffèrent dans les seules zones temporelles permises.
- Les deux moufles finales restent distinctes, devant le torse, sous la bouche.
  Les 18 dernières images corporelles sont tenues ; la fumée reste animée.

## Respiration et son

L'inspiration existante culmine à 25.766771 s ; ouverture visuelle retenue à
25.750000 s, écart 0.402 image. L'expiration culmine à
32.809271 s ; ouverture visuelle à 32.833333 s, écart
0.577 image. L'ouverture d'inspiration est tenue pendant le souffle,
puis le petit mouvement d'expiration revient à la déception.

Le WAV reste strictement identique à V27 : aucune translation globale de la
piste. Corrélation AAC/WAV sans décalage :
0.997439444. Aucun écrêtage PCM ; silences exacts de 32 à 32,5 s
et de 37,25 à 38 s. Les 63 événements, cinq accents vocaux, cinq stems et
46 cues conservés sont vérifiés directement, avec licences et empreintes.

## Images réellement encodées

38 images du MP4 comparées à des rendus CairoSVG frais, sans cache PNG.
Erreur globale maximale : 1.59735/255 ; erreur maximale des régions
visage/mains/accessoires : 2.25113/255, sous le seuil 3/255. Aucun échec.
Les producteurs et ressources n'ont pas changé pendant la vérification.

Rapports détaillés : `audit_final.json` et `audit_revision_v28.json`.
Ces résultats sont techniques et portent sur la géométrie émise, les images
encodées et le signal audio. Ils ne certifient aucune écoute, reconnaissance
émotionnelle par un public, qualité artistique ou approbation de l'utilisatrice.
