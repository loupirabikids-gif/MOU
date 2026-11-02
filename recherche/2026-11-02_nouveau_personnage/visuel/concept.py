"""Original static raccoon proposal, drawn only with SVG and CairoSVG.

This is a design hypothesis, not a validated character or audience result.
"""
from pathlib import Path
import math
import cairosvg

HERE=Path(__file__).resolve().parent
INK='#302D35'; FUR='#A7A29A'; LIGHT='#C6C0B7'; CREAM='#FFF0D6'
MASK='#52413C'; CORAL='#ED7563'; CORAL_DARK='#D45D52'; WHITE='#FFFDF8'


def path(d,fill='none',stroke=INK,w=6,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def ellipse(x,y,rx,ry,fill,stroke='none',w=0,extra=''):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" {extra}/>'


def head(uid,expression='curieux'):
    p=[]
    # Round ears with a subtle fold on one side. They belong to this new animal.
    p.append(path('M-134 -85 C-172 -104 -177 -155 -148 -181 C-122 -205 -86 -179 -88 -134 Z',FUR))
    p.append(path('M-142 -115 C-155 -128 -153 -157 -139 -165 C-123 -172 -110 -151 -111 -135 Z',CREAM,w=0))
    p.append(path('M94 -129 C95 -174 126 -196 153 -180 C179 -164 174 -121 153 -98 Z',FUR))
    p.append(path('M117 -134 C119 -153 132 -166 144 -158 C157 -148 150 -129 141 -121 Z',CREAM,w=0))
    p.append(path('M146 -179 Q153 -156 174 -153',FUR,w=4))
    # Cheeks are a new pear-free shape with a small brow tuft and broad muzzle.
    p.append(path('M-162 -39 C-162 -107 -104 -153 -37 -155 L-22 -170 L-8 -157 '
                  'L8 -169 L20 -153 C93 -154 153 -120 170 -56 L181 -24 L168 -20 '
                  'L182 4 L164 8 C159 83 101 130 19 139 C-62 148 -131 117 -156 58 '
                  'L-173 43 L-164 29 L-180 14 L-164 1 Z',FUR))
    p.append(path('M-138 -56 C-111 -119 -45 -137 4 -133 C-12 -104 -15 -76 -8 -44 '
                  'C-55 -58 -100 -50 -138 -30 Z',LIGHT,w=0))
    # Separated eye masks preserve a cream bridge and clear eyebrows.
    p.append(path('M-139 -43 C-119 -74 -68 -73 -32 -40 C-15 -24 -13 18 -32 46 '
                  'C-57 79 -116 63 -139 31 C-154 10 -154 -17 -139 -43 Z',MASK,w=0))
    p.append(path('M40 -42 C69 -72 120 -66 144 -37 C161 -16 159 18 144 40 '
                  'C120 73 69 65 46 44 C27 26 21 -21 40 -42 Z',MASK,w=0))
    p.append(path('M-3 -90 C3 -66 9 -46 15 -28 C22 -46 27 -65 31 -86',CREAM,w=0))
    # Cheek and muzzle shapes keep the nose/mouth distinct from the eye masks.
    p.append(path('M-117 64 C-91 50 -54 53 -24 65 C1 45 35 42 57 59 '
                  'C88 45 123 57 139 76 C116 112 73 132 23 136 C-32 142 -81 119 -117 92 Z',CREAM,w=0))
    p.append(ellipse(-15,70,46,28,CREAM))
    p.append(ellipse(47,68,40,27,CREAM))
    if expression=='curieux':
        eyes=[(-82,-4,36,46),(91,-6,32,43)]; gaze=(8,-7); pupils=14
        brows=[('M-118 -89 Q-87 -109 -49 -91'),('M57 -98 Q88 -121 120 -105')]
        mouth='M-12 92 Q23 118 62 84'
    elif expression=='impatient':
        eyes=[(-82,3,36,39),(91,5,32,39)]; gaze=(12,6); pupils=13
        brows=[('M-119 -89 Q-83 -83 -48 -68'),('M56 -68 Q92 -85 124 -86')]
        mouth='M-10 105 Q17 95 53 101'
    else:
        eyes=[(-82,-6,38,50),(91,-9,35,49)]; gaze=(-5,-5); pupils=12
        brows=[('M-122 -100 Q-87 -129 -48 -115'),('M54 -115 Q91 -140 127 -115')]
        mouth=None
    for j,(x,y,rx,ry) in enumerate(eyes):
        p.append(ellipse(x,y,rx,ry,WHITE,INK,4.6))
        if expression=='impatient':
            lid=f'M{x-rx} {y-ry*.25} Q{x} {y-ry*.35} {x+rx} {y-ry*.05}'
            p.append(path(f'M{x-rx-3} {y-ry-3} H{x+rx+3} V{y-ry*.05} Q{x} {y-ry*.35} {x-rx-3} {y-ry*.25} Z',MASK,w=0))
            p.append(path(lid,MASK,w=4))
        px=x+gaze[0];py=y+gaze[1]
        p.append(ellipse(px,py,pupils,pupils*1.22,INK))
        p.append(ellipse(px-4,py-5,4,5,WHITE))
        if expression=='impatient':
            # The lid covers the top of the pupil as well.
            p.append(path(f'M{x-rx+2} {y-ry+2} H{x+rx-2} V{y-ry*.05} Q{x} {y-ry*.35} {x-rx+2} {y-ry*.25} Z',MASK,w=0))
            p.append(path(lid,MASK,w=4))
        p.append(path(brows[j],w=7.8))
    p.append(path('M3 59 Q22 49 42 58 Q46 62 37 73 Q25 87 13 76 Q0 65 3 59 Z',INK,w=3))
    p.append(path('M23 79 V91',w=4))
    if mouth:p.append(path(mouth,w=5.1))
    else:
        p.append(path('M-6 92 Q24 122 63 87 C63 128 13 145 -6 92 Z',INK,w=4))
        p.append(path('M5 98 Q27 110 50 98 L47 106 Q27 117 9 108 Z',WHITE,w=0))
        p.append(path('M19 123 Q34 115 46 118 Q33 133 19 123 Z','#E7A092',w=0))
    p.append(path('M-120 77 L-139 73 M134 73 L151 67',w=3.5))
    return '<g id="'+uid+'">'+''.join(p)+'</g>'


def hero():
    tail='M450 713 C550 763 664 711 658 596 C656 547 638 514 611 515 C576 517 577 553 591 582 C613 632 575 684 468 654 Z'
    p=['<defs><clipPath id="tail-clip">'+path(tail,w=0)+'</clipPath></defs>']
    p.append(ellipse(359,851,256,30,'#E9DACE'))
    p.append(path(tail,LIGHT,w=7))
    p.append('<g clip-path="url(#tail-clip)">')
    p.append(path('M503 651 L548 666 L550 752 L505 744 Z',MASK,w=0))
    p.append(path('M589 611 L661 600 L668 647 L595 661 Z',MASK,w=0))
    p.append(path('M576 535 L642 525 L661 569 L586 582 Z',MASK,w=0))
    p.append('</g>'+path(tail,w=7))
    # Two attached short legs and sturdy, soft paws.
    p.append(path('M265 735 L319 735 L316 816 Q291 833 264 816 Z',FUR,w=7))
    p.append(path('M373 738 L427 737 L438 811 Q416 836 384 820 Z',FUR,w=7))
    p.append(path('M265 799 C240 799 231 825 249 840 L304 840 Q326 834 317 812 Z',MASK,w=6))
    p.append(path('M386 803 C375 820 378 840 399 844 L452 842 C475 830 456 807 432 802 Z',MASK,w=6))
    # Hood, sleeves, cuffs and mitten paws are connected, not floating.
    p.append(path('M250 505 C280 475 395 476 430 513 L444 699 Q424 770 343 773 Q268 771 247 711 Z',CORAL_DARK,w=7))
    p.append(path('M258 536 C232 537 210 577 202 617 L238 633 L276 568 Z',CORAL,w=7))
    p.append(path('M424 534 C478 525 501 481 530 451 L567 468 C559 520 514 570 458 584 Z',CORAL,w=7))
    p.append(path('M202 612 L242 627 L237 649 L197 634 Z',CORAL_DARK,w=5))
    p.append(path('M526 456 L537 432 L572 445 L567 475 Z',CORAL_DARK,w=5))
    p.append(path('M199 632 C179 642 185 678 210 686 C233 692 253 673 240 648 L228 650 L222 641 Z',FUR,w=6))
    # A raised friendly open paw, rounded mass with one thumb.
    p.append('<g transform="translate(47 -3)">'+path('M493 442 C476 430 475 413 486 405 C495 398 501 408 508 417 C500 398 500 382 512 381 C523 382 523 400 526 410 C528 394 538 389 545 398 C550 406 542 424 534 437 L523 448 Z',FUR,w=5.5)+'</g>')
    p.append(path('M276 535 Q339 565 410 534 L421 719 Q340 750 265 716 Z',CORAL,w=0))
    p.append(path('M264 713 Q341 741 427 711 L424 745 Q344 770 266 743 Z',CORAL_DARK,w=5))
    p.append(path('M290 644 Q340 622 394 644 L393 698 Q342 715 290 698 Z',CORAL_DARK,w=4))
    p.append(path('M294 645 L306 659 M389 645 L376 659',w=3.4))
    p.append(path('M304 540 L298 582 M382 543 L388 581',CREAM,CREAM,5))
    p.append(ellipse(298,585,4,7,CREAM))
    p.append(ellipse(388,584,4,7,CREAM))
    p.append('<g transform="translate(337 372) rotate(-4) scale(1.08)">'+head('hero-head','curieux')+'</g>')
    return ''.join(p)


def main():
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="960" viewBox="0 0 1280 960">',
           '<rect width="1280" height="960" fill="#FFF8EE"/>',
           '<path d="M737 147 V859" stroke="#E3D6C9" stroke-width="2"/>',
           '<text x="61" y="74" font-family="DejaVu Sans" font-weight="bold" font-size="46" fill="'+INK+'">PATCH</text>',
           '<text x="62" y="105" font-family="DejaVu Sans" font-size="17" fill="#7D7068">RATON CITADIN · NOM PROVISOIRE</text>',
           '<text x="62" y="912" font-family="DejaVu Sans" font-size="23" font-weight="bold" fill="'+INK+'">Une idée. Tout de suite.</text>',
           '<text x="62" y="938" font-family="DejaVu Sans" font-size="15" fill="#7D7068">Croquis de proposition — design et jeu à juger.</text>',hero()]
    for idx,(expression,label,cy) in enumerate([('curieux','CURIOSITÉ JOYEUSE',277),('impatient','IMPATIENCE',524),('surpris','SURPRISE AMUSÉE',771)]):
        parts.append(f'<g transform="translate(1001 {cy}) scale(.56)">'+head('expression-'+str(idx),expression)+'</g>')
        parts.append(f'<text x="1001" y="{cy+107}" text-anchor="middle" font-family="DejaVu Sans" font-size="16" font-weight="bold" fill="#6A5A55">{label}</text>')
    parts.append('</svg>')
    svg=''.join(parts)
    (HERE/'Patch_concept.svg').write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(HERE/'Patch_concept.png'))
    print('PATCH_CONCEPT_READY')


if __name__=='__main__':main()
