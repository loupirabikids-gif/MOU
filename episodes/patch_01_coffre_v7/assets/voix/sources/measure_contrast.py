"""Measure acoustic changes against V1; this is not an auditory judgement."""
from pathlib import Path
import json,wave,hashlib
import numpy as np
from scipy.signal import correlate,find_peaks,butter,sosfiltfilt
BANK=Path(__file__).resolve().parents[1]
ROOT=BANK.parents[1]
RATE=48000

def read(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(RATE,1,2)
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768.

def metrics(x):
 frame=1920;hop=480;f0=[];harmonic=[]
 # Broad lowpass makes the periodicity estimate less dependent on high formants.
 xx=sosfiltfilt(butter(3,[160,1800],btype='bandpass',fs=RATE,output='sos'),x)
 maxr=max(np.sqrt(np.mean(xx[i:i+frame]**2)) for i in range(0,max(1,len(xx)-frame),hop))
 for i in range(0,max(1,len(xx)-frame),hop):
  a=xx[i:i+frame]
  if len(a)<frame or np.sqrt(np.mean(a*a))<maxr*.16:continue
  a=(a-a.mean())*np.hanning(len(a));r=correlate(a,a,mode='full',method='fft')[len(a)-1:];r/=max(r[0],1.e-12)
  lo=round(RATE/1100);hi=round(RATE/180)
  peaks,_=find_peaks(r[lo:hi]);peaks=peaks+lo
  if not len(peaks):continue
  best=max(float(r[j]) for j in peaks)
  if best<.42:continue
  good=[j for j in peaks if r[j]>=max(.42,best*.91)]
  lag=min(good);f0.append(RATE/lag);harmonic.append(float(r[lag]))
 spectrum=abs(np.fft.rfft(x))**2;freq=np.fft.rfftfreq(len(x),1/RATE);total=max(float(sum(spectrum)),1.e-12)
 centroid=float(sum(freq*spectrum)/total)
 quartiles=np.quantile(f0,[.10,.50,.90]).tolist() if f0 else None
 return {'autocorrelation_candidate_hz_p10_median_p90':quartiles,'voiced_windows':len(f0),'autocorrelation_quality_median':float(np.median(harmonic)) if harmonic else None,'spectral_centroid_hz':centroid,'fraction_energy_above_6khz':float(sum(spectrum[freq>6000])/total),'whole_rms_dbfs':float(20*np.log10(max(float(np.sqrt(np.mean(x*x))),1.e-12))),'peak_dbfs':float(20*np.log10(max(float(max(abs(x))),1.e-12)))}

def main():
 oldroot=ROOT/'personnages/PATCH_voix_v1';old=json.loads((oldroot/'bank.json').read_text());new=json.loads((BANK/'bank.json').read_text());rows={}
 for k,v in new['sounds'].items():
  a=metrics(read(oldroot/old['sounds'][k]['file']));b=metrics(read(BANK/v['file']));p=a['autocorrelation_candidate_hz_p10_median_p90'];q=b['autocorrelation_candidate_hz_p10_median_p90']
  reliable=k not in ('sleepy_yawn','surprise_inhale')
  rows[k]={'v1':a,'v2':b,'f0_estimate_reliable':reliable,'median_f0_ratio':q[1]/p[1] if p and q and reliable else None,'v2_accent_points_seconds':v['accent_points_seconds'],'v1_duration':old['sounds'][k]['duration'],'v2_duration':v['duration']}
 report={'method':'40ms Hann-window autocorrelation, 10ms hop,160–1800Hz analysis band; ambiguous/nonperiodic windows excluded. These are estimates, not pitch ground truth or human emotion recognition. Breath-dominated yawn and mixed inhalation are marked unreliable for F0: formant/noise peaks must not be mistaken for a fundamental.','neutral_formants_ratio_vs_v1':1.3,'v1_vocal_tract_cm':None,'v2_vocal_tract_cm':11,'mouth_articulation_difference':'V1 NA length disabled resonance movement for mouth. V2 finite length physically shifts all formants with mouth opening; nasal threshold retained.','sounds':rows,'listening_performed':False,'naturalness_or_emotion_recognition_claimed':False}
 (BANK/'controle/contraste_v1_v2.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:round(v['median_f0_ratio'],2) if v['median_f0_ratio'] else None for k,v in rows.items()}))
if __name__=='__main__':main()
