"""Approved chef costume as an overlay in MOU's native coordinates.

The geometry, colours and embedded name match the chef_v1 validation still.
Render after the original torso and before the original arms. No body or limb
geometry is substituted. The bundled Nunito font keeps the name reproducible.
"""
from __future__ import annotations

import base64
from functools import lru_cache
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from art import _path

EP = Path(__file__).resolve().parents[1]
FONT = EP/'assets/Nunito-wght.ttf'
INK, CREAM, CORAL = '#382035', '#FFFDF7', '#D9947D'


@lru_cache(maxsize=1)
def hat_name():
    """Cache the approved 380×140 name raster once per rendering process."""
    im = Image.new('RGBA', (380, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT), 94)
    font.set_variation_by_name('ExtraBold')
    draw.text((190, 70), 'MOU', font=font, fill=INK, anchor='mm')
    data = io.BytesIO()
    im.save(data, format='PNG')
    return base64.b64encode(data.getvalue()).decode('ascii')


def costume_svg(state=None):
    """Return the exact approved short toque and waist apron overlay."""
    p = _path
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
        p('M131 348 Q205 342 284 349 L282 361 '
          'Q205 354 132 361 Z', CORAL, INK, 3.),
        p('M157 355 Q205 351 257 356 L269 403 '
          'Q265 415 252 418 Q204 428 158 416 '
          'Q144 412 143 402 Z', CORAL, INK, 3.6),
        p('M155 405 Q204 417 257 407', stroke='#FFF0DC', width=2.),
        p('M181 371 Q205 368 229 372 L228 391 '
          'Q206 402 183 392 Z', '#FFF0DC', INK, 2.3),
        p('M186 377 Q205 374 224 378', stroke='#B77E77', width=1.8),
        p('M142 354 Q132 343 126 350 Q124 358 140 358 '
          'Q130 364 134 369 Q144 370 146 358', CORAL, INK, 2.4),
        '</g></g>',
    ])


svg_at = costume_svg
