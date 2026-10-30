"""Five brief MOU vocal proposals, adapted from explicitly licensed CC0 assets.

The source pack labels breaths and creature vocal sounds. Its original author
and recording method are unverified. These are not claimed as verified human
recordings or as an imitation of Lamput. No model listening is available.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import wave
import numpy as np

ASSETS=Path(__file__).resolve().parents[1]/'assets/vocal_sources'
SPECIFICATIONS=(
    ('mou_hesitation',21.98,.18,'ooh',.120,3.,-39.,1400.,'murmure nasal hésitant'),
    ('mou_inspiration',25.68,.16,'breath_02',.025,2.,-40.,3500.,'inspiration brève devant la fumée'),
    ('mou_choc',31.76,.20,'ooh',.065,2.,-38.5,3000.,'prise de souffle devant le repas raté'),
    ('mou_expiration',32.78,.28,'breath',.055,1.,-40.,2900.,'expiration de déception'),
    ('mou_satisfaction',35.15,.16,'ooh',.350,3.,-40.,1500.,'murmure nasal de satisfaction déplacée'),
)


def _read(name):
    path=ASSETS/f'{name}.wav'
    manifest=json.loads((ASSETS/'provenance.json').read_text())
    source=next(e for e in manifest['sources'] if e['id']==name)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==source['wav_sha256']
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(48000,2,2)
        data=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2)/32768.
    return data,source


def cues(timeline,sr=48000):
    assert sr==48000 and float(timeline['duration'])==38.
    result=[]
    for name,start,duration,source_id,offset,semitones,target_db,cutoff,intention in SPECIFICATIONS:
        source,provenance=_read(source_id)
        mono=source.mean(axis=1);count=round(duration*sr)
        ratio=2.**(semitones/12.)
        positions=offset*sr+np.arange(count)*ratio
        assert positions[-1]<len(mono),(name,'source excerpt too short')
        clip=np.interp(positions,np.arange(len(mono)),mono)
        clip-=clip.mean()
        frequencies=np.fft.rfftfreq(count,1./sr)
        highpass=frequencies**2/(frequencies**2+100.**2)
        lowpass=1./np.sqrt(1.+(frequencies/cutoff)**6)
        clip=np.fft.irfft(np.fft.rfft(clip)*highpass*lowpass,n=count)
        attack=min(count//3,round(.018*sr));release=min(count//3,round(.035*sr))
        clip[:attack]*=np.sin(np.linspace(0,np.pi/2,attack))**2
        clip[-release:]*=np.cos(np.linspace(0,np.pi/2,release))**2
        rms=float(np.sqrt(np.mean(clip**2)));peak=float(np.abs(clip).max())
        gain=min(10.**(target_db/20.)/max(rms,1e-12),10.**(-27./20.)/max(peak,1e-12))
        clip*=gain;clip[0]=clip[-1]=0.
        signal=np.column_stack((clip,clip))
        result.append(({'name':name,'kind':'mou_nonverbal','start':start,'duration':count/sr,
            'source_id':source_id,'source_file':f'assets/vocal_sources/{source_id}.wav',
            'source_sha256':provenance['wav_sha256'],'source_url':provenance['url'],
            'licence':'CC0 1.0, repository-wide notice bundled',
            'source_method':'Library creature/breath asset; original production and author unverified',
            'intended_expression':intention,'intended_wordless':True,
            'processing':{'source_offset_s':offset,'varispeed_semitones':semitones,
                'mono_centered':True,'highpass_hz':100.,'lowpass_hz':cutoff,
                'attack_s':.018,'release_s':.035,'rms_target_dbfs':target_db,'peak_cap_dbfs':-27.},
            'limits':'Not listened to. Labels and treatments do not establish wordlessness, emotion or comfort perceived by an audience.'},signal))
    return result
