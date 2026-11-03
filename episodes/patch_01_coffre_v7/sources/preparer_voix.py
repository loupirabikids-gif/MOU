"""Copy the generated original bank and bind vocal accents to the fixed film.

Run only when the Soundgen bank is frozen. This never calls a neural API.
The visual envelope comes from the generated audio, not an imagined duration.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import wave
import numpy as np

EP=Path(__file__).resolve().parents[1]
ROOT=EP.parents[1]

PLAN=[
    ('resolve_hm',4.875,-27.5,'closed_lip_decision'),
    ('bored_exhale',13.25,-28.5,'small_pursed_exhale'),
    ('sleepy_yawn',18.0,-28.5,'one_yawn_before_camera_cut'),
    ('surprise_inhale',23.208333333333332,-28.5,'discovery_inhale'),
    ('relief_chuckle',25.125,-27.5,'two_breathy_joy_pulses'),
]


def read_audio(path):
    with wave.open(str(path),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,1,2)
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768.


def envelope(samples):
    # 10 ms sampling, 30 ms centred energy window, then a 30 ms smoothing.
    step=480;half=720
    times=np.arange(0,len(samples)+step,step)/48000.
    values=[]
    for sec in times:
        at=round(sec*48000.)
        a=samples[max(0,at-half):min(len(samples),at+half)]
        values.append(float(np.sqrt(np.mean(a*a))) if len(a) else 0.)
    values=np.convolve(values,[.25,.5,.25],mode='same')
    peak=float(max(values))
    if peak<1.e-6:raise ValueError('Empty vocal envelope')
    values=np.clip(values/peak,0.,1.)
    # Silence on either side keeps the analytic rig unchanged outside the take.
    pairs=[[-.04,0.]]+[[float(t),float(v)] for t,v in zip(times,values)]+[[len(samples)/48000.+.04,0.]]
    return pairs


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bank',type=Path,default=ROOT/'personnages/PATCH_voix_v2_squeaky')
    args=p.parse_args()
    source=args.bank;dest=EP/'assets/voix'
    bank=json.loads((source/'bank.json').read_text())
    # Keep the master recipes and licence notices with the included bank.
    for path in source.rglob('*'):
        if not path.is_file() or 'work' in path.relative_to(source).parts:continue
        if path.suffix.lower() not in ('.wav','.json','.r','.py','.sh','.md','.txt'):continue
        target=dest/path.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,target)
    timeline=json.loads((EP/'chronologie.json').read_text())
    timeline['title']='PATCH — Le coffre V7 : voix squeaky et trajet des bras'
    timeline['status']='squeaky_voice_and_box_arm_revision'
    events=[];cues=[]
    for number,(name,accent,target_rms,intention) in enumerate(PLAN,1):
        entry=bank['sounds'][name];path=dest/entry['file'];samples=read_audio(path)
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        at=accent-float(entry['accent_seconds']);duration=len(samples)/48000.
        if name=='sleepy_yawn' and not (17.3<=at and at+duration<=18.4):
            raise ValueError('Yawn must finish before the low-angle camera cut')
        cue=dict(id=f'voice_{number:02d}_{name}',sound=name,at=at,
                 visual_accent=accent,target_rms_dbfs=target_rms,pan=0.,intention=intention)
        cues.append(cue)
        points=[[at+x,y]for x,y in envelope(samples)]
        events.append(dict(id=cue['id'],sound=name,start=points[0][0],end=points[-1][0],
                           visual_accent=accent,envelope=points))
    timeline['voice_cues']=cues
    timeline['voice_direction']={'engine':bank['engine'],'dialogue':False,'music':False,
         'listening_performed':False,'source_bank':'assets/voix/bank.json',
         'hands_camera_time_preserved':True,'takes':len(cues)}
    (EP/'chronologie.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n')
    (EP/'sources/voix_gestes.json').write_text(json.dumps({'events':events},indent=2)+'\n')
    print(json.dumps({'copied_bank':str(dest),'cues':cues},indent=2))


if __name__=='__main__':main()
