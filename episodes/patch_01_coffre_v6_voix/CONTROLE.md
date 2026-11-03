# Contrôles — V6 avec voix

Le MP4 final avec son et sa version muette ont été décodés et contrôlés.
La critique indépendante a examiné 104 images du vrai montage dans six
planches. Le rapport technique regroupe 18 contrôles ciblés.

- 720 états conservent les mains, les coudes, le corps, le téléphone, le
  couvercle, les vues et le temps de V5. Les 654 PNG hors fenêtres des
  vocalisations sont strictement identiques à ceux de V5.
- Le soupir et le bâillement ouvrent une petite bouche arrondie sans dents.
  Le bâillement se referme avant la coupe et l'éveil. Le « hm » garde les
  lèvres fermées. L'inspiration commence après le retour du visage.
- Les cinq accents et les deux pulsations du rire sont mesurés sur les WAV
  réellement générés, à moins d'une image des repères du visage.
- 18 effets et leurs niveaux sont préservés. La somme base + stem voix
  reconstitue le PCM du mix ; les échantillons hors voix restent identiques.
  Pic du mix : environ −17,06 dBFS, aucun écrêtage ; gains fixes, sans musique
  ou compresseur. Environ 2,33 s de voix actives sur 30 s.
- Soundgen 3.0.0 a réellement été exécuté sous R 4.5.0. Six intentions,
  douze WAV maîtres, paramètres/graines et notices des logiciels sont inclus.
  L'installation isolée et la synthèse des douze prises ont été reproduites
  par le spécialiste ; les bruts et paramètres correspondent à sa première
  exécution. La planche d'écoute est décodée et documentée séparément.
- Son/muet : 1080 × 1920, 24 ips, 720 images, 30 s, même flux H264 ; AAC
  présent uniquement dans la version son. Douze images du HD décodé
  concordent avec des rendus frais. Anciennes références intactes.

Sources des vérifications : [QA](controle/qa.json),
[critique du vrai montage](controle/critique_voix.md),
[mesures audio](audio/controls.json), [cues vocaux](audio/voice_cues.json),
[recettes et licences](assets/voix/README.md).

Le ZIP vérifie CRC et manifeste SHA256. `controle/reproduction.json`
documente la reconstruction de PNG sélectionnés et du WAV depuis une
extraction isolée, sans promettre l'identité binaire d'un nouvel encodage MP4.

**Limite : aucune audition réelle du mix ou de la banque n'est effectuée
ici.** Les noms d'émotions indiquent les intentions de synthèse. La revue
visuelle et les mesures ne prouvent ni naturel, ni confort, ni compréhension
émotionnelle à l'écoute. Aucune vidéo ou piste privée de référence n'est livrée.
