# Instruments libres utilisés pour la nouvelle musique

La partition est originale. Ses timbres d’instruments proviennent de la banque
**TimGM6mb**, distincte des bruitages originaux du projet. Aucune chanson ni
boucle musicale téléchargée n’est employée.

- Fichier : `TimGM6mb.sf2`, repris du paquet installé `timgm6mb-soundfont`.
- Auteurs : Tim Brechbill (2004), David Bolton (2010).
- Licence : **GPL version 2**, texte et notice Debian fournis ici.
- Source amont indiquée par cette notice :
  https://github.com/musescore/musescore-old/commit/90c33ef9d87b3f5ff92efd3b07d89eb455fb1fef
- SHA-256 : `c5378b62028c920cb11e4803327983fee2f2cdff5dc89c708e39da417e51c854`.

Le rendu hors ligne passe par **FluidSynth**, logiciel libre (LGPL-2.1+),
appelé depuis Python ; ni service distant, ni crédit de génération.
Notice de droits et texte LGPL fournis. Projet : https://www.fluidsynth.org/.

Le SoundFont est inclus dans l’archive de sources pour reproduire les timbres.
La bibliothèque système `libfluidsynth` doit être installée pour refaire la
musique, par exemple `libfluidsynth3` sur Debian/Ubuntu. Aucun serveur audio
ou périphérique sonore n’est nécessaire pour ce rendu.
