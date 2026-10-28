# Préparation du contrôle indépendant du microtest « remuer »

Périmètre reçu du coordinateur : quatre secondes muettes, deux remuages courts, aucune transition vers l’essuyage ni fabrication du film. Les autorisations plus récentes de l’utilisatrice priment sur l’étape de placement décrite dans l’ancien AGENTS.md.

Références réellement consultées : `AGENTS.md`, `BRIEF_MOU_CODEX.txt`, `PLACEMENT.json`, le PNG d’aperçu validé, le SVG maître de placement via sa source et le rig original `mou_rig.py`. Aucun rendu animé n’est encore examiné ; ce texte formule des recommandations et ne valide pas une intention sur le code.

## Appuis utiles pour le geste

- Garder le placement `translate(80,380) scale(2.3)`, le décor et le corps immobiles. Le bras droit fixe en clasp 1 convient au test : une action d’un bras face à l’autre au repos reste lisible.
- La moufle gauche de `_arm` passe d’environ (255,1224) à (489,1275) en coordonnées image lorsque clasp passe de 0 à 1. Vers clasp 0,3–0,5, sa position (325–372,1239–1249) permet une cuillère courte inclinée vers l’intérieur de la poêle (293,1304).
- Viser pour le bol de cuillère une ellipse conservatrice, de rayons approximatifs 55–65 × 12–18 pixels, dans la cavité de rayons 114 × 34. La marge doit comprendre la largeur du bol et son contour.
- Le manche passe derrière la moufle et ressort vers le bol sans séparation visible. Au passage près du bord avant, l’extrémité doit paraître dans la poêle, pas posée au-dessus de son contour.
- Petite préparation, contact ralenti, accélération sur une partie du tour, freinage puis brève pause : la variation de vitesse compte davantage que multiplier les oscillations. Le second tour peut avoir une durée ou une amplitude légèrement différente.
- Orienter les pupilles vers le contact avant de démarrer. Un très petit suivi de la zone suffit ; éviter un regard adressé au public.

## Points à juger sur les vrais rendus

1. Continuité épaule–bras–moufle pendant clasp et rotation ; aucune nouvelle forme, racine masquée ou costume.
2. Prise fixe en coordonnées de la moufle ; manche sans glissement pendant les changements de direction.
3. Cuillère au contact d’une surface cohérente ; passage avant/arrière du bord de poêle.
4. Trajet lisible comme remuage, accélérations perceptibles et arrêt qui ne ressemble pas à un moteur coupé.
5. Deux bras et deux mains ; corps et décor préservés.

Le contrôle définitif donnera un instant, un fait visible, son effet probable et une correction concrète pour chaque défaut réel. Aucun gag ni ajout sonore ne sera évalué dans ce seul test de geste.
