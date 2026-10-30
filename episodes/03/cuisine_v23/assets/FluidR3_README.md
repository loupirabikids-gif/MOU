# FluidR3 : sous-ensemble du trio MOU

Banque d'instruments tiers, distincte de la partition originale MOU.
Le SoundFont fourni est un sous-ensemble de **FluidR3 GM** de Frank Wen et
Toby Smithe, licence **MIT**. La notice originale Debian est incluse dans
NOTICE_FluidR3_COPYRIGHT.txt. La clause GPL de cette notice concerne les
fichiers d'empaquetage Debian, non les échantillons SoundFont (section Files:* MIT).

## Provenance vérifiée

Paquet officiel Debian Trixie `fluid-soundfont-gm` version3.1-5.3 :
https://deb.debian.org/debian/pool/main/f/fluid-soundfont/fluid-soundfont-gm_3.1-5.3_all.deb

La signature du fichier InRelease de Debian Trixie a été vérifiée avec GPG
et le trousseau d'archives Debian déjà installé. Son SHA256 du Packages.xz
correspond au fichier récupéré ; le SHA256 du paquet correspond ensuite à
son entrée dans cet index. Aucune vérification de signature ou TLS désactivée.
Le détail est dans FluidR3_MOU_trio.json, `package_verification`.

- Paquet SHA256 : `6f531493ac4e4d9772fd96b2488ea1790af81c196135fbdd25997da0781fc60e`.
- SF2 original :148398306octets, SHA256 `74594e8f4250680adf590507a306655a299935343583256f3b722c48a1bc1cb0`.
- Sous-ensemble :4048186octets, SHA256 `c8c326b595c4cf49a5aa58c920ecb27b645deb025652938e7db8b6795eca5fe2`.

## Sélection

- banque0/programme0, Yamaha Grand Piano : notes48à76 ;
- banque0/programme32, Acoustic Bass : notes33à57 ;
- banque128/programme40, Brush : notes36,38,42,44,51.

Les échantillons PCM et points de boucle retenus sont copiés intégralement.
Les zones hors plages sont retirées, les tables SF2 et liens stéréo réindexés.
Le résultat contient32échantillons et6instruments internes pour3presets.
Les messages MIDI hors de ces plages ne font pas partie de la banque réduite.

Les59notes retenues ont été rendues à vélocité72 avec FluidSynth, sur la
banque originale puis sur le sous-ensemble, réverbération/chorus désactivés.
Chaque waveform est **identique échantillon par échantillon** et aucune note
n'est muette. Cela prouve la fidélité de l'extraction, pas la qualité perçue
d'un mix ni une écoute. Les résultats sont dans `render_checks` du JSON.

## Reproduire le sous-ensemble

Depuis la racine du projet, après téléchargement et vérification du paquet
ci-dessus puis extraction locale avec `dpkg-deb -x` :

```sh
.venv/bin/python -B episodes/03/cuisine_v23/sources/subset_soundfont.py \
  CHEMIN_EXTRACTION/usr/share/sounds/sf2/FluidR3_GM.sf2 \
  episodes/03/cuisine_v23/assets/FluidR3_MOU_trio.sf2
```

Le SF2 complet et le paquet restent dans work/, hors livraison. Le script
Python et la banque réduite rendent la partition reproductible sans service
payant. Le droit de modification et redistribution provient de la licence
MIT de la banque, dont la notice doit rester jointe.
