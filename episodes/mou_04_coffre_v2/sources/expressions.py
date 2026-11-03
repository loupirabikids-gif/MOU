"""Reuse the existing silent facial timing for the MOU recast.

The curves were authored for the earlier performance. No vocal asset is loaded
or mixed here; they simply time determination, boredom, yawn and joy.
"""
from copy import deepcopy
import json
from pathlib import Path
from personnage import face_parameters

DATA=json.loads(Path(__file__).with_name('expressions_gestes.json').read_text())


def interp(points, at):
    if at<=points[0][0]:return points[0][1]
    for (x0,y0),(x1,y1) in zip(points,points[1:]):
        if at<=x1:return y0+(y1-y0)*(at-x0)/max(x1-x0,1.e-9)
    return points[-1][1]


def apply_expressions(t, actor):
    a=deepcopy(actor)
    for cue in DATA['events']:
        if not cue['start']<=t<=cue['end']:continue
        env=max(0.,min(1.,interp(cue['envelope'],t)))
        if env<1.e-5:continue
        f=face_parameters(a);name=cue['sound']
        if name=='resolve_hm':
            f['mouth_open']=0.
            f['mouth_smile']+=.12*env
            f['brow_raise_l']+=2.*env;f['brow_raise_r']+=2.*env
        elif name=='bored_exhale':
            a['mouth_shape']='breath'
            f['mouth_width']=f['mouth_width']*(1.-env)+29.*env
            f['mouth_open']=.30*env
        elif name=='sleepy_yawn':
            a['mouth_shape']='breath'
            f['mouth_width']=f['mouth_width']*(1.-env)+36.*env
            f['mouth_open']=.92*env
            a['blink']=a.get('blink',1.)*(1.-.86*env)
            f['brow_raise_l']+=3.*env;f['brow_raise_r']+=3.*env
        elif name=='surprise_inhale':
            # The established discovery pose already has an O-shaped mouth.
            a['mouth_o_scale']=1.+.14*env
            f['brow_raise_l']+=3.*env;f['brow_raise_r']+=3.*env
        elif name=='relief_chuckle':
            f['mouth_open']=f['mouth_open']*(1.-env)+.86*env
            f['mouth_smile']=max(f['mouth_smile'],.90)
        a.pop('pose_weights',None);a['face']=f
        a['expression_event']=cue['id'];a['expression_amount']=env
    return a
