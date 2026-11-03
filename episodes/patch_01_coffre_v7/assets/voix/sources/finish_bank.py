"""Package actual Soundgen output as soft mono PCM16 masters and metadata."""
from pathlib import Path
import argparse,hashlib,json,wave,shutil
import numpy as np
from scipy.signal import find_peaks, butter, sosfiltfilt, correlate
BANK=Path(__file__).resolve().parents[1]
RATE=48000
RMS_DB={'resolve_hm':-27.,'bored_exhale':-29.,'sleepy_yawn':-28.,'effort_small':-27.5,'surprise_inhale':-29.,'relief_chuckle':-27.}
INTENT={'resolve_hm':'decision, bouche fermee','bored_exhale':'ennui, expiration descendante','sleepy_yawn':'somnolence, petit baillement','effort_small':'effort bref','surprise_inhale':'surprise, aspiration suivie de petit couinement','relief_chuckle':'joie, deux souffles rieurs'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finish(raw_path):
 raw_path=Path(raw_path);sound={};variants={};rows=[]
 for i,(id,rms_db) in enumerate(RMS_DB.items(),1):
  for v in (1,2):
   stem=f'{id}_{v:02d}';raw=np.fromfile(raw_path/(stem+'.f64'),dtype='<f8')
   assert raw.size and np.all(np.isfinite(raw))
   # Remove DC and taper the waveform itself, without a gate/compressor.
   x=raw-np.mean(raw)
   x=sosfiltfilt(butter(3,100,fs=RATE,btype='highpass',output='sos'),x)
   x=sosfiltfilt(butter(5,5000,fs=RATE,btype='lowpass',output='sos'),x)
   n=min(round(.008*RATE),len(x)//4)
   x[:n]*=np.sin(np.linspace(0,np.pi/2,n))**2
   x[-n:]*=np.sin(np.linspace(np.pi/2,0,n))**2
   # RMS of active waveform; a peak ceiling only limits pathological crests.
   active=np.abs(x)>max(abs(x))*.01
   rms=np.sqrt(np.mean(x[active]**2));gain=10**(rms_db/20)/rms
   gain=min(gain,10**(-14/20)/max(abs(x)));x*=gain
   x=np.r_[x,np.zeros(round(.012*RATE))]
   pcm=np.rint(np.clip(x,-1,1)*32767).astype('<i2')
   p=BANK/'maitres'/(stem+'.wav')
   with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
   env=np.sqrt(np.convolve(x*x,np.ones(960)/960,mode='same'))
   if id in ('resolve_hm','relief_chuckle'):
    half=int((.145 if id=='resolve_hm' else .205)*RATE)
    p1=int(np.argmax(env[:half]));p2=half+int(np.argmax(env[half:]))
    accents=[p1/RATE,p2/RATE]
   else:accents=[int(np.argmax(env))/RATE]
   nz=np.flatnonzero(np.abs(pcm)>32)
   meta={'file':str(p.relative_to(BANK)),'sha256':sha(p),'duration':len(x)/RATE,
     'accent_seconds':accents[0],'accent_points_seconds':accents,
     'onset_seconds':int(nz[0])/RATE if len(nz) else 0,
     'audible_end_seconds':(int(nz[-1])+1)/RATE if len(nz) else 0,
     'seed':8200+i*10+v,'intent':INTENT[id],
     'variant':v,'channels':1,'sample_rate':RATE,'bits':16,
     'active_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x[abs(x)>max(abs(x))*.01]**2)))),
     'whole_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x*x)))),
     'peak_dbfs':float(20*np.log10(max(abs(x)))),
     'clipped_samples':int(np.count_nonzero((pcm==32767)|(pcm==-32768))),
     'raw_soundgen_sha256':sha(raw_path/(stem+'.f64')),
     'parameter_file':'parametres/'+stem+'.R','license':'NOASSERTION',
     'rights_notice':'Original audio for PATCH; no public reuse licence assigned',
     'listening_performed':False}
   shutil.copy2(raw_path/(stem+'.R'),BANK/meta['parameter_file'])
   variants[stem]=meta
   if v==1:sound[id]=meta
   rows.append(meta)
 manifest={'engine':{'name':'Soundgen','version':'3.0.0','runtime':'R4.5.0','executed':True,
     'code_license':'GPL-2.0-or-later','models_or_voice_recordings_used':False},
   'sample_rate':RATE,'voice_identity':{'id':'PATCH-squeaky-source-filter-v2',
     'formants_hz':[715,1820,3510,5070,6240],'formant_width':1.35,'vocal_tract_cm':11.,'mouth_moves_formants':True,
     'direction':'small squeaky cartoon; varied M/O/A articulation, breath and cadence; no words or cloned person',
     'pitch_hz_design_range':[390,880], 'v1_pitch_hz_design_range':[205,310.5], 'neutral_formants_ratio_vs_v1':1.30},
   'sounds':sound,'variants':variants,'listening_performed':False,
   'selection_method':'First seeded take per recipe, not auditory ranking; variants offered for comparison.',
   'accent_method':'Centre of maximum20msRMS; first/second pulse searched separately for chuckle.',
   'levels':'100Hz highpass + gentle 5kHz lowpass, active RMS scaling, -14dBFS ceiling; no scene pumping.',
   'source_recipe':'sources/generate.R','postprocess':'sources/finish_bank.py'}
 (BANK/'bank.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
 shutil.copy2(raw_path/'engine.txt',BANK/'controle/engine.txt')
 print(json.dumps({k:{q:v[q] for q in ['duration','accent_seconds','accent_points_seconds','peak_dbfs']} for k,v in sound.items()},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('raw_directory');finish(p.parse_args().raw_directory)
