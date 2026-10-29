# Reproduire la phrase V19

Texte choisi : « Just cooking. Mostly washing. », deux lignes anglaises
Nunito ExtraBold 48 px dans un cartouche x60–480 / y128–274. Visible 0–3 s.
Le titre remplace l’ancien calque ; la scène, le personnage et le mix V18
restent conservés. Police Nunito et licence SIL OFL fournies dans assets/.

Depuis la racine du dépôt avec Python/dépendances du projet et FFmpeg :

```sh
export XDG_CACHE_HOME="$PWD/work/font-cache"
.venv/bin/python -B episodes/03/cuisine_v19/sources/render.py --preview --workers 3
.venv/bin/python -B episodes/03/cuisine_v19/sources/render.py --workers 3
.venv/bin/python -B episodes/03/cuisine_v19/sources/verify.py
.venv/bin/python -B episodes/03/cuisine_v19/sources/package.py
```

Le cache de rasters vérifié V14 peut être réutilisé si la clé du SVG complet,
de l’échelle et de la version est identique. Le nouveau texte change les
clés d’ouverture et impose de nouveaux rasters. Sans ancien cache, le rendu
se fait normalement depuis les sources. Les images décisives sont comparées
à des SVG frais hors cache après export.

Quand le MP4 V18 est présent, le rendu copie sa piste AAC sans réencodage.
L’archive autonome peut encoder le même mix WAV fourni si V18 est absent.
La musique n’est pas recomposée et le mix n’est pas recalculé pour ce titre.

Les sources son.py/music.py et les banques restent incluses pour reproduire
aussi le mix V18 : elles utilisent FluidSynth et la banque libre TimGM6mb,
avec crédits et licences dans assets/. Aucun service payant.

Format final : 41 s, 1080 × 1920, 24 images/s ; animatique : 540 × 960, 12 images/s.
La version muette partage le même flux vidéo que la version sonore.
