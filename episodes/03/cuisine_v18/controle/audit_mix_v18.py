"""Compare the existing V17 music and effect banks with the V18 balance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import wave

import numpy as np

EP=Path(__file__).resolve().parents[1]
BASE=EP.parent/'cuisine_v17'
SR=48000

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        return np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).astype(float)/32768.

def db(signal):
    return float(20*np.log10(max(np.sqrt(np.mean(signal*signal)),1e-12)))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
    provenance=json.loads((EP/'audio/provenance.json').read_text())
    audit=json.loads((EP/'controle/audit_son.json').read_text())
    master=audit['master_gain_linear_exact']
    actual=read(EP/'audio/mix.wav');rebuilt=np.zeros_like(actual);retained=0
    for event in provenance['events']:
        path=EP/'audio'/event['file']
        if event['kind']!='background_music':
            assert sha(path)==sha(BASE/'audio'/event['file']),event['name'];retained+=1
        signal=read(path)*10.**(event['mix_gain_db']/20.)
        start=event['start_sample'];rebuilt[start:start+len(signal)]+=signal
    rebuilt*=master
    for length,tail in ((round(.008*SR),False),(round(.035*SR),True)):
        curve=np.sin(np.linspace(0.,np.pi/2.,length))**2
        if tail:rebuilt[-length:]*=curve[::-1,None]
        else:rebuilt[:length]*=curve[:,None]
    error=np.abs(actual-rebuilt)*32768.
    assert retained==63 and error.max()<8.,float(error.max())
    assert sha(EP/'sources/music.py')==sha(BASE/'sources/music.py')
    assert sha(EP/'audio/musique_sans_baisse.wav')==sha(BASE/'audio/musique_sans_baisse.wav')
    timeline=json.loads((EP/'chronologie.json').read_text())
    segments=[('cuisine',2.,6.5),('carotte',13.5,16.5),('tomate',21.5,23.),('sel',27.,29.),('fin',39.5,40.8)]
    for c in timeline['cycles']:
        segments += [(f'eau{c["id"]}',*c['water']),(f'essuyage{c["id"]}',*c['wipe'])]
    rows=[]
    previous=read(BASE/'audio/mix.wav')
    for name,start,end in segments:
        region=slice(round(start*SR),round(end*SR))
        rows.append({'segment':name,'seconds':[start,end],'v17_rms_dbfs':db(previous[region]),'v18_rms_dbfs':db(actual[region])})
    old_range=max(r['v17_rms_dbfs'] for r in rows)-min(r['v17_rms_dbfs'] for r in rows)
    new_range=max(r['v18_rms_dbfs'] for r in rows)-min(r['v18_rms_dbfs'] for r in rows)
    assert new_range<5. and new_range<old_range-6.,(old_range,new_range)
    assert np.abs(actual).max()<.99
    report={'status':'passed','music_partition_and_unducked_pcm_identical':True,'original_effect_wavs_identical':retained,
        'mix_reconstruction_max_lsb':float(error.max()),'peak_dbfs':float(20*np.log10(np.abs(actual).max())),
        'segments':rows,'scene_rms_range_v17':old_range,'scene_rms_range_v18':new_range,
        'range_scope':'Comparable body scenes; initial foreground whistle phrase excluded. This is not a perceptual listening test.',
        'mix_gain_db_by_kind':audit['mix_stage_gain_db_by_kind'],'music_duck_db':audit['background_music']['sink_duck_db']}
    if args.final:
        hashes=[]
        for f in (BASE/'MOU_Encore_une_feuille.mp4',EP/'MOU_Encore_une_feuille.mp4'):
            data=subprocess.check_output(['ffmpeg','-v','error','-i',str(f),'-map','0:v:0','-c:v','copy','-bsf:v','h264_mp4toannexb','-f','h264','-'])
            hashes.append(hashlib.sha256(data).hexdigest())
        assert hashes[0]==hashes[1]
        report['h264_identical_to_v17']=hashes[0]
    (EP/'controle/audit_mix_v18.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='segments'},indent=2))

if __name__=='__main__':
    main()
