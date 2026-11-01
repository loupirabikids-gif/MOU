# Banque PCM conservée pour V30

Les 61 fichiers de `cues/` sont copiés octet pour octet depuis les cues du
mix V28. Leurs empreintes et leurs instants figurent dans
`../input_bank.json`. Il s'agit des signaux avant le gain global de livraison
de +3,5 dB, avec la ponctuation absolue déjà incorporée dans les cues.

Seuls `cuisson_progressive_v27` et `dernier_tsss_poele_v27` sont exclus de
la banque active. `provenance_v28.json` conserve le manifeste historique
complet pour documenter les origines ; ses deux références de cuisson ne
désignent pas des entrées actives de V30.

La piste musicale d'entrée est inchangée. `sources/son.py` lui applique le
seul nouveau gain de −6 dB lors du mélange, sans nouvelle modulation de
volume ni normalisation. La petite modulation de musique des anciens
lavages reste incorporée à la source historique.

Les partitions JSON/MIDI originales sont conservées ici. Les notices de la
banque instrumentale, du papier et des vocalisations se trouvent dans les
`assets/` de cet épisode, avec leurs sources et licences. L'eau, le sifflement
et plusieurs contacts restent des synthèses antérieures. Les voix sont les
cinq adaptations de bibliothèque CC0 déjà présentes ; ni leur auteur
original ni leur procédé de captation ne sont établis.

Aucune écoute du modèle ou validation perceptive n'est revendiquée.
