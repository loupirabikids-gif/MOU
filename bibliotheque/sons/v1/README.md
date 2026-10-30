# MOU — bibliothèque de sons v1

**12 propositions, six intentions et deux variantes chacune.** Ce premier
catalogue sert à choisir une identité sonore par écoute. Aucun son n'est
encore approuvé comme voix définitive de MOU.

- [Audition vidéo — 18 secondes](MOU_Bibliotheque_Sons_v1.mp4?raw=true)
- [Audition WAV sans musique](audition_complete.wav?raw=true)
- [Bibliothèque autonome ZIP](MOU_Bibliotheque_Sons_v1.zip?raw=true)
- [Catalogue HTML](index.html) · [Métadonnées](CATALOGUE.json)

Le HTML s'utilise après téléchargement et extraction du ZIP : ouvrir index.html
localement. Les boutons audio utilisent seulement des fichiers relatifs et
une interaction explicite ; aucun fetch, compte ou service externe. GitHub
peut afficher le code HTML au lieu du lecteur ; le MP4 reste la lecture mobile.

| Intention recherchée | Variante 1 | Variante 2 | Bouche / geste à privilégier |
| --- | --- | --- | --- |
| Hésitation | retenue | prolongée | bouche étroite, main suspendue |
| Effort | petit | plus marqué | contraction ou poussée brève |
| Surprise | légère | franche | inspiration, yeux vers la cause et bouche qui s'ouvre |
| Déception | courte | relâchée | expiration après constat de la perte |
| Satisfaction | retenue | fière | résultat examiné, puis petit sourire |
| Gêne | discrète | plus lisible | deux petits accents, sourire crispé |

Les variantes ont des durées, contours de hauteur, enveloppes et proportions
de souffle différents. Elles partagent une petite palette de sources et un
registre cohérent. La voix tonale dérive de l'asset « ooh » autour de trois
demi-tons plus haut ; les inspirations/expirations utilisent les assets de
souffle crédités. Ce ne sont pas douze noms donnés au même fichier.

## Repère pour la synchronisation

Chaque WAV contient anchor_sample et peak_sample dans CATALOGUE.json. L'ancre
est calculée sur le PCM réellement écrit : première séquence de 2 ms dépassant
25 % du maximum RMS mesuré sur 4 ms. C'est un repère numérique reproductible,
pas un seuil d'audibilité ni une preuve de bonne émotion.

Pour placer un son :

```text
départ du son = instant du geste choisi − anchor_sample / 48000
```

Choisir le bon geste : regard qui découvre une cause, début d'inspiration,
contraction ou relâchement. Une voix nasale peut accompagner une bouche fermée ;
une voyelle de surprise demande une ouverture compatible. Vérifier ensuite le
couplage par une vraie écoute avec l'image, sans déplacer toute la bande-son.
Les champs preferred_when, avoid_when et mouth_type aident à ce choix.

## Sources et statut

Trois couples OGG/WAV CC0 et leur notice sont dans sources/. URLs et empreintes
sont figées au commit f2b6264f9ab89fabc266914c3654685d68c5a39b du dépôt
lavenderdotpet/CC0-Public-Domain-Sounds. L'auteur original, la date de dédicace
et la méthode de création ne sont pas établis par les preuves accessibles.
Ne pas appeler ces assets des captations humaines vérifiées ou une imitation
de Lamput. Aucun son de référence Cartoon Network n'est réutilisé.

Tous les sons portent le statut **proposition_non_validee**. Les noms sont des
intentions éditoriales ; naturel, absence de mots perçus, personnalité et
confort ne sont pas validés par le modèle, qui ne peut pas écouter ici.

## Reproduction

Python 3.11 minimum, NumPy, Pillow et FFmpeg ; production gratuite et open source.
La police DejaVu et sa licence sont incluses. Depuis le dossier extrait :

```sh
python build.py
```

Depuis le dépôt, avec son environnement existant :

```sh
.venv/bin/python -B bibliotheque/sons/v1/build.py
```

L'API sound_bank.render(id) retourne le signal float stéréo 48 kHz et ses
métadonnées. Les WAV sont en PCM16. build.py recrée catalogue, galerie,
audition et archive avec manifeste SHA256, sans accès réseau ni épisode externe.
CONTROLE.json décrit les vérifications techniques ; elles ne remplacent pas
une écoute et une sélection par l'utilisatrice.
