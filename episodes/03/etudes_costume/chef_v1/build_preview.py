"""Native SVG costume study only; the V19 film and rig are read-only inputs."""
from pathlib import Path
import base64
import hashlib
import importlib.util
import io
import json
import sys

import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
OUT = Path(__file__).resolve().parent
REF = ROOT/'episodes/03/cuisine_v19'
INK, CREAM, CORAL = '#382035', '#FFFDF7', '#D9947D'
FONT = REF/'assets/Nunito-wght.ttf'
spec = importlib.util.spec_from_file_location('chef_reference_v19', REF/'sources/render.py')
ref = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ref
spec.loader.exec_module(ref)


def font(size):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_name('ExtraBold')
    return f


def hat_name():
    """Bundled font raster embedded in the SVG; no fontconfig dependence."""
    im = Image.new('RGBA', (380, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.text((190, 70), 'MOU', font=font(94), fill=INK, anchor='mm')
    b = io.BytesIO()
    im.save(b, format='PNG')
    return base64.b64encode(b.getvalue()).decode('ascii')


def costume_svg(state=None):
    """Only clothes, in native coordinates. No limb or body substitutions."""
    p = ref.art._path
    return ''.join([
        '<g id="costume-chef-etude">',
        '<g id="toque-chef" data-costume="chef-hat">',
        p('M196 112 C180 113 174 100 182 89 '
          'C177 74 191 62 205 67 C212 50 238 50 250 69 '
          'C272 57 296 73 290 90 C307 99 301 112 286 115 '
          'L286 127 L196 127 Z', CREAM, INK, 4.),
        p('M205 82 Q200 92 205 101 M228 75 Q225 88 228 100 '
          'M254 83 Q260 91 257 101 M279 92 Q280 98 276 103',
          stroke='#CDB4C7', width=2.2),
        p('M194 109 Q239 115 288 108 L287 134 '
          'Q242 143 195 134 Z', CREAM, INK, 3.5),
        '<image x="206" y="110" width="69" height="25.4" '
        f'href="data:image/png;base64,{hat_name()}"/>',
        '</g>',
        '<g id="tablier-taille" data-costume="apron">',
        # Entire garment begins at the waist, below the face and shoulders.
        p('M131 348 Q205 342 284 349 L282 361 '
          'Q205 354 132 361 Z', CORAL, INK, 3.),
        p('M157 355 Q205 351 257 356 L269 403 '
          'Q265 415 252 418 Q204 428 158 416 '
          'Q144 412 143 402 Z', CORAL, INK, 3.6),
        p('M155 405 Q204 417 257 407', stroke='#FFF0DC', width=2.),
        p('M181 371 Q205 368 229 372 L228 391 '
          'Q206 402 183 392 Z', '#FFF0DC', INK, 2.3),
        p('M186 377 Q205 374 224 378', stroke='#B77E77', width=1.8),
        # The side knot is cloth; its small loops remain inside the body.
        p('M142 354 Q132 343 126 350 Q124 358 140 358 '
          'Q130 364 134 369 Q144 370 146 358', CORAL, INK, 2.4),
        '</g></g>',
    ])


def floor_bin_svg():
    """Proposed final outcome: 4 large sheets in the bin, final small one outside."""
    return (ref.art.bin_svg(4) + '<g id="dernier-papier-au-sol">'
            + ref.art._ellipse(325, 1831, 32, 8, '#BDA6BD', opacity='.35')
            + ref.art._ball(325, 1805, 22, 12, 4) + '</g>')


def raster(svg, width, height):
    layer = Image.open(io.BytesIO(cairosvg.svg2png(
        bytestring=svg.encode(), output_width=width, output_height=height))).convert('RGBA')
    return Image.alpha_composite(Image.new('RGBA', layer.size, '#FFF8ED'), layer).convert('RGB')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = [ROOT/'mou_rig.py', REF/'MOU_Encore_une_feuille.mp4',
              REF/'sources/art.py', REF/'sources/animation.py',
              REF/'sources/render.py', REF/'chronologie.json', REF/'audio/mix.wav']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    # In-memory study substitution only; production source modules stay untouched.
    ref.art.apron_svg = costume_svg
    t = 4.
    state = ref.animation.scene_state(t)
    scene_svg = ref.svg_at(t)
    (OUT/'MOU_chef_cuisine.svg').write_text(scene_svg)
    scene = raster(scene_svg, 1080, 1920)
    scene.save(OUT/'MOU_chef_cuisine.png')
    scene.resize((360, 640), Image.Resampling.LANCZOS).save(OUT/'MOU_chef_cuisine_mobile.png')

    # Unoccluded detail shows the waist apron that the island partly hides.
    figure_svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="560" height="800" '
                  'viewBox="60 40 290 420">'
                  '<rect x="60" y="40" width="290" height="420" fill="#FFF8ED"/>'
                  + state['torso'] + costume_svg(state) + state['arms'] + '</svg>')
    (OUT/'MOU_costume_detail.svg').write_text(figure_svg)
    figure = raster(figure_svg, 560, 800)
    figure.save(OUT/'MOU_costume_detail.png')
    bin_svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="560" height="490" '
               'viewBox="5 1280 390 600">'
               '<rect x="5" y="1280" width="390" height="600" fill="#F2E3E3"/>'
               '<path d="M5 1810 H395" stroke="#DAC5D3" stroke-width="3"/>'
               + floor_bin_svg() + '</svg>')
    (OUT/'MOU_chute_papier.svg').write_text(bin_svg)
    bin_image = raster(bin_svg, 560, 490)
    bin_image.save(OUT/'MOU_chute_papier.png')

    board = Image.new('RGB', (1240, 1380), '#FFF8ED')
    d = ImageDraw.Draw(board)
    d.text((40, 25), 'MOU — proposition à valider', font=font(35), fill=INK)
    d.text((40, 74), 'Toque « MOU » + tablier noué à la taille', font=font(25), fill=INK)
    board.paste(scene.resize((648, 1152), Image.Resampling.LANCZOS), (28, 125))
    d.text((718, 127), 'Détail du costume', font=font(26), fill=INK)
    board.paste(figure.resize((500, 714), Image.Resampling.LANCZOS), (708, 168))
    d.text((718, 908), 'Dernier jet : poubelle pleine', font=font(24), fill=INK)
    board.paste(bin_image.resize((470, 411), Image.Resampling.LANCZOS), (723, 950))
    # Preserve each image's aspect ratio in the validation board.
    # The floor preview is a separate storyboard state, not the opening scene.
    board.save(OUT/'MOU_chef_validation.png')
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    assert before == after, 'A read-only production input changed'
    report = {'scope': 'Still study only, awaiting user approval; no MP4 rerendered.',
              'reference': 'cuisine_v19', 'reference_time': t,
              'tools': ['Python', 'SVG', 'CairoSVG', 'Pillow'],
              'production_inputs_unchanged': before,
              'costume': {'hat_text': 'MOU', 'apron': 'waist only; no bib or shoulder straps'},
              'proposed_ending': 'Final radius-22 crumpled sheet lands on floor beside full bin; first four remain in bin.'}
    (OUT/'controle.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
