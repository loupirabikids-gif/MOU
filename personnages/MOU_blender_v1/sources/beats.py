"""A short, explicit action clock inspired by doodle-anim's beat compiler.

Only the idea of named actions and timed waits is reused. The character,
scene, poses and gag are MOU's; no doodle-anim character drawing is imported.
"""
from __future__ import annotations
import math

BEATS = [
    ('assaisonner', .72, 'assurance'),
    ('remarquer_le_grain', .18, 'assurance'),
    ('inspecter', .40, 'resistance'),
    ('faire_comme_si', .20, 'resistance'),
    ('reprendre_la_cuillere', .48, 'resistance'),
    ('remuer_malgre_le_grain', .57, 'resistance'),
    ('suspendre_le_geste', .15, 'resistance'),
    ('revoir_le_grain', .20, 'resistance'),
    ('tenir_la_pensee', .20, 'resistance'),
    ('ceder_et_reposer', .24, 'cede'),
    ('porter_la_main_au_lavabo', .96, 'cede'),
    ('ouvrir_le_robinet', .15, 'cede'),
    ('rejoindre_le_jet', .15, 'cede'),
    ('un_seul_grain', .05, 'cede'),
    ('grain_emporte', .19, 'cede'),
    ('fin_du_lavage', .16, 'cede'),
]


def compile_beats(fps=24):
    clock = 0.
    result = []
    for action, duration, pose in BEATS:
        end = round(clock+duration, 8)
        result.append({'action':action, 'pose':pose, 't0':clock, 't1':end,
                       'frame_start':math.ceil(clock*fps-1e-8)+1,
                       'frame_end_exclusive':math.ceil(end*fps-1e-8)+1})
        clock = end
    assert abs(clock-5.) < 1e-8
    return result
