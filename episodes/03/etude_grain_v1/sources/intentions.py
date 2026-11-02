"""Three deliberately composed attitudes for the silent grain acting study.

The keys describe a thought and a whole-body contrast, rather than emotion
labels from a catalogue. Gaze, native mitten contacts and timing are supplied
by the study director. No pupil position, arm shape or permanent model changes.
"""
from __future__ import annotations

from copy import deepcopy

import visage


KEY_POSES = {
    'assurance': {
        'face': {
            'eye_open_l': .50, 'eye_open_r': .56,
            'brow_raise': .08, 'brow_l': .10, 'brow_r': -.10,
            'brow_raise_l': .04, 'brow_raise_r': .04, 'brow_curve': .30,
            'mouth_shape': 'smile', 'mouth_width': 26.,
            'mouth_open': 0., 'mouth_skew': .30, 'smile': .75,
            'laugh': 0.,
        },
        'body_profile': {'scale_y': 1.04, 'angle_deg': -3.},
        'intention': 'Je connais mon affaire : cuisiner mérite toute mon attention.',
        'read': 'Calme supérieur, paupières basses, sourire fermé et buste ouvert.',
    },
    'resistance': {
        'face': {
            'eye_open_l': 1., 'eye_open_r': 1.,
            'brow_raise': .40, 'brow_l': -.12, 'brow_r': .18,
            'brow_raise_l': .04, 'brow_raise_r': .10, 'brow_curve': .12,
            'mouth_shape': 'smile', 'mouth_width': 26.,
            'mouth_open': 0., 'mouth_skew': .06, 'smile': .35,
            'laugh': 0.,
        },
        'body_profile': {'scale_y': .98, 'angle_deg': 4.5},
        'intention': 'Continuer normalement ; surtout ne pas regarder ce grain.',
        'read': 'Yeux ouverts trop fixes et mince sourire fermé, buste retenu.',
    },
    'cede': {
        'face': {
            'eye_open_l': .84, 'eye_open_r': .84,
            'brow_raise': .04, 'brow_l': .06, 'brow_r': .06,
            'brow_raise_l': 0., 'brow_raise_r': 0., 'brow_curve': -1.,
            'mouth_shape': 'flat', 'mouth_width': 14.,
            'mouth_open': 0., 'mouth_skew': 0., 'smile': 0.,
            'laugh': 0.,
        },
        'body_profile': {'scale_y': .94, 'angle_deg': -6.},
        'intention': 'Ce grain exige une intervention immédiate et parfaitement sérieuse.',
        'read': 'Précision appliquée, sourcils presque horizontaux et bouche petite fermée.',
    },
}


def face_params(name):
    """Return an independent face dictionary; the director adds directed gaze."""
    return deepcopy(KEY_POSES[name]['face'])


def body_profile(name):
    """Return the modest body bias; feet and native contacts remain external."""
    return dict(KEY_POSES[name]['body_profile'])


def blend_params(first, last, amount):
    """One contour transition, only when the director explicitly calls for it."""
    a = face_params(first) if isinstance(first, str) else deepcopy(first)
    b = face_params(last) if isinstance(last, str) else deepcopy(last)
    return visage.blend_face_params(a, b, amount)
