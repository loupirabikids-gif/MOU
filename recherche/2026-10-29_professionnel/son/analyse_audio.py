"""Read-only measurements of MOU V21; does not substitute for listening."""
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import wave

import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP=ROOT/'episodes/03/cuisine_v21'
OUT=Path(__file__).resolve().parent
SR=48000


def read(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).astype(float)/32768.


def db(value):
    return 20*math.log10(max(float(value),1e-12))


def metrics(x):
    mono=x.mean(axis=1)
    w=np.hanning(len(mono));spec=np.abs(np.fft.rfft(mono*w))**2
    freq=np.fft.rfftfreq(len(mono),1/SR);total=float(spec.sum())
    rms=float(np.sqrt(np.mean(x*x)));peak=float(np.abs(x).max())
    return {'duration_seconds':len(x)/SR,'rms_dbfs':db(rms),'peak_dbfs':db(peak),
            'crest_db':db(peak/max(rms,1e-12)),
            'energy_fraction_2_6khz':float(spec[(freq>=2000)&(freq<6000)].sum()/max(total,1e-30)),
            'energy_fraction_above_6khz':float(spec[freq>=6000].sum()/max(total,1e-30))}


def main():
    data=json.loads((EP/'audio/provenance.json').read_text())
    events=data['events'];master=10**(data['master_gain_db']/20)
    selected=['cuisson','remuage_debut','c1_eau','c1_main_sous_eau',
              'c1_papier_deroule','c1_papier_dechire','c1_essuie_main',
              'c1_papier_froisse','c1_poubelle_impact','carotte_coupe_1',
              'sifflement_p1_n1','musique_cuisine','tablier_essuie']
    bank=[]
    for name in selected:
        e=next((v for v in events if v['name']==name),None)
        if e is None:continue
        signal=read(EP/'audio'/e['file'])*master*10**(float(e.get('mix_gain_db',0.))/20)
        bank.append({'name':name,'kind':e['kind'],'start':e['start'],
                     'mix_gain_db':e.get('mix_gain_db',0.),
                     'post_master_estimate':metrics(signal),
                     'source_sha256':hashlib.sha256((EP/'audio'/e['file']).read_bytes()).hexdigest()})
    mix=read(EP/'audio/mix.wav');n=len(mix)
    foreground=np.zeros(n,dtype=np.uint8)
    excluded={'frying','background_music','background_music_continuation','frying_continuation'}
    for e in events:
        if e['kind'] in excluded:continue
        a=round(e['start']*SR);b=min(n,a+round(e['duration']*SR));foreground[a:b]+=1
    wet=[e for e in events if e['kind']=='water'];hand=[e for e in events if e['kind']=='hand_water']
    overlap=sum(max(0,min(w['start']+w['duration'],h['start']+h['duration'])-max(w['start'],h['start'])) for w in wet for h in hand)
    fft=metrics(mix)
    raw=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(EP/'audio/mix.wav'),
        '-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],
        check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode()
    loudness=json.loads(re.findall(r'\{[\s\S]*?\}',raw)[-1])
    report={'scope':'Measurements only, no listening or perceptual approval.',
            'mix_sha256':hashlib.sha256((EP/'audio/mix.wav').read_bytes()).hexdigest(),
            'mix_metrics':fft,'loudnorm_input':{k:v for k,v in loudness.items() if k.startswith('input_')},
            'bank_post_master_estimates':bank,
            'foreground_event_count':sum(e['kind'] not in excluded for e in events),
            'foreground_events_per_second':sum(e['kind'] not in excluded for e in events)/(n/SR),
            'foreground_scheduled_occupancy_fraction':float(np.mean(foreground>0)),
            'foreground_layers_2plus_fraction':float(np.mean(foreground>=2)),
            'foreground_layers_3plus_fraction':float(np.mean(foreground>=3)),
            'water_seconds':sum(e['duration'] for e in wet),
            'hand_water_overlap_seconds':overlap,
            'hand_water_overlap_fraction_of_water':overlap/sum(e['duration'] for e in wet),
            'limits':'Bank estimates apply fixed event mix gain/master only; the full mix contains overlaps and global envelope. Spectral share, LUFS and absence of clipping do not prove comfort.'}
    (OUT/'mesures_v21.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='bank_post_master_estimates'},indent=2))


if __name__=='__main__':main()
