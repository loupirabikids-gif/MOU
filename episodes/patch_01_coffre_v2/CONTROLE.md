# Bilan — Trente minutes de concentration

Film de 30 s, 1080 × 1920, à 24 images/s. La version son et la version muette
partagent le même flux H264. La V1 reste intacte ; le rig et la palette de
PATCH sont conservés.

Le délai du récit passe de dix secondes à trente minutes. Une horloge,
les repères 30 MIN / MIN:SEC et les ellipses explicites expliquent le passage
du temps. Les deux premiers regards comportent de vrais retours vers la
liste ; le crayon est ensuite posé. Les 29 minutes sont représentées et les
trois dernières valeurs disposent de 16/17/17 images avant la dernière seconde.
Un insert de 30 images montre les trois cases restées vides.

La [critique](controle/critique_finale.md) examine les vraies images décodées,
en distinguant animatique et HD. Une lecture interne sans explication du
scénario comprend le téléphone enfermé pour travailler, les trente minutes
perdues et la liste intacte. Ce n'est pas un test public. La réserve sur les
premières tentatives de travail, assez discrètes, est conservée. La V1 avait
déjà passé une QA : cela n'en faisait pas un gag validé par l'utilisatrice.

La [QA indépendante](controle/qa.json) passe 16 contrôles ciblés. Les 720 états
SVG, 29 minutes, retours 1/2, contacts, masquages, liste et ressources sont
cohérents. Douze images décodées du vrai HD concordent avec des rendus frais
hors cache ; les 60 échantillons de raccords manche/patte ne montrent pas de
trou. Les six références protégées et les dix fichiers gelés sont intacts.
Un décalage de carton d'une image, lié à l'arrondi de la minute17, a été
corrigé avant les nouveaux rendus preview et HD.

Depuis le ZIP extrait dans un dossier séparé, douze PNG frais et le WAV
complet se reproduisent à l'identique, sans ancien dossier ni cache de rendu
ou réseau. Le [rapport de reproduction](controle/reproduction.json) précise
les images testées. Aucune identité binaire des MP4 n'est revendiquée.

Le mix contient 18 effets, en PCM16 stéréo 48 kHz, sans écrêtage. Les stems et
les cues correspondent à la chronologie. Aucun son d'écriture, musique ou
voix n'est ajouté. Les Foley CC0 sont des extraits documentés de bibliothèque ;
les signaux UI sont originaux. Les effets finissent vers 24,15 s pour laisser
lire le résultat.

**Limite d'écoute :** aucune audition réelle n'a été possible dans cet
environnement. Les niveaux et les instants sont contrôlés ; le confort
sonore n'est pas certifié par ces mesures. Ni succès d'audience ni cadence
hebdomadaire ne sont déduits de ces vérifications.

SHA-256 du film avec son :
`eed3bf80ee7ac21682e3dbf16ff061952c7df3381391c461ffa72794e26e00dd`.

SHA-256 de la version muette :
`ccce6a9323adbb6daea18ba987a257da1de8221a387cb1ff9ef5d5069c634601`.
