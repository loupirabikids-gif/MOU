"""V6: keep the quiet V5 Foley and add sparse original Soundgen vocalisations.

No music, scene ducking or compressor. Voice accents use the picture timeline.
Numeric checks are not an audition of naturalness or comfort.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import son_base as base

EP=Path(__file__).resolve().parents[1]
RATE=base.RATE


def render_audio(timeline_path, output_path):
    timeline_path=Path(timeline_path);output_path=Path(output_path)
    timeline=json.loads(timeline_path.read_text())
    base_report=base.render_audio(timeline_path,output_path.parent/'base_mix.wav')
    bank_root=EP/'assets/voix'
    bank=json.loads((bank_root/'bank.json').read_text())
    with base.wave.open(str(output_path.parent/'base_mix.wav'),'rb') as w:
        mix=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64).reshape(-1,2)/32767.
    voice=np.zeros_like(mix);rows=[];ids=set()
    for cue in timeline['voice_cues']:
        name=cue['sound'];identifier=cue['id']
        if identifier in ids:raise ValueError('Duplicate vocal cue '+identifier)
        ids.add(identifier);entry=bank['sounds'][name];path=bank_root/entry['file']
        if base.sha(path)!=entry['sha256']:raise ValueError('Voice asset changed '+name)
        source=base.read_wav(path)
        rms=float(np.sqrt(np.mean(source*source)))
        if rms<1.e-7:raise ValueError('Silent voice '+name)
        # Fixed per-take gains. Never modulate the existing soundtrack by scene.
        gain=10.**(cue['target_rms_dbfs']/20.)/rms
        gain=min(gain,.19/max(float(np.max(np.abs(source))),1.e-9))
        source=source*gain
        pan=float(cue.get('pan',0.));angle=(pan+1.)*np.pi/4.
        stereo=source[:,None]*np.array([np.cos(angle),np.sin(angle)])[None,:]
        at=float(cue['at']);start=round(at*RATE);end=start+len(source)
        if start<0 or end>len(voice):raise ValueError('Voice beyond episode '+name)
        voice[start:end]+=stereo
        accent=at+entry['accent_seconds']
        if abs(accent-float(cue['visual_accent']))>1./24.+1.e-7:
            raise ValueError('Voice accent missed visible action '+identifier)
        rows.append(dict(id=identifier,sound=name,at=at,start_sample=start,
                         duration=len(source)/RATE,gain_db=20.*np.log10(gain),
                         pan=pan,group='voice',sound_sha256=entry['sha256'],
                         accent_seconds=accent,visual_accent=cue['visual_accent'],
                         accent_error_frames=(accent-cue['visual_accent'])*24.))
    mix+=voice
    if np.max(np.abs(mix))>.70:raise ValueError('Combined peak too high')
    base.write_wav(output_path, mix)
    base.write_wav(output_path.parent/'stems/voice.wav',voice)
    old_rows=json.loads((output_path.parent/'cues.json').read_text())
    all_rows=sorted(old_rows+rows,key=lambda x:x['at'])
    (output_path.parent/'cues.json').write_text(json.dumps(all_rows,indent=2)+'\n')
    keys=list(dict.fromkeys(k for row in all_rows for k in row))
    with (output_path.parent/'cues.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(all_rows)
    report=dict(base_report,file=output_path.name,sha256=base.sha(output_path),
                base_mix_sha256=base.sha(output_path.parent/'base_mix.wav'),
                cues=len(all_rows),foley_ui_cues=len(old_rows),voice_cues=len(rows),
                voice=True,voice_engine=bank['engine'],
                peak_linear=float(np.max(np.abs(mix))),
                peak_dbfs=float(20.*np.log10(max(float(np.max(np.abs(mix))),1.e-12))),
                rms_dbfs=float(20.*np.log10(max(float(np.sqrt(np.mean(mix*mix))),1.e-12))),
                listening_performed=False,
                limits='Generated and aligned numerically; naturalness and comfort have not been heard here.')
    (output_path.parent/'mix_report.json').write_text(json.dumps(report,indent=2)+'\n')
    (output_path.parent/'voice_cues.json').write_text(json.dumps(rows,indent=2)+'\n')
    controls=dict(report,clipped_samples=int(np.count_nonzero(np.abs(mix)>=1.)),
                  fixed_gains=True,voice_asset_peak_ceiling=.19,
                  accent_max_error_frames=max(abs(x['accent_error_frames']) for x in rows),
                  perceptual_quality_validated=False)
    (output_path.parent/'controls.json').write_text(json.dumps(controls,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--timeline',type=Path,default=EP/'chronologie.json')
    p.add_argument('--output',type=Path,default=EP/'audio/mix.wav')
    args=p.parse_args();print(json.dumps(render_audio(args.timeline,args.output)))


if __name__=='__main__':main()
