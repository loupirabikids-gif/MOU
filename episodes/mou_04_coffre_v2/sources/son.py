"""MOU coffre V2: eight motivated Foley cues from documented CC0 recordings.

No oscillators, procedural voice, music, tick track, scene ducking or ambience.
Prepare recorded source excerpts: python sources/son.py --prepare
Render frozen edit: python sources/son.py --timeline chronologie.json --output audio/mix.wav

Timeline: duration seconds, audio_cues: {id,sound,at,gain_db=0,pan=0}.
Each at is the visible action; the included short attack follows within the
measured delay in bank.json. No unreported automatic time offset is applied.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfiltfilt

EP = Path(__file__).resolve().parents[1]
ASSETS = EP / 'assets/son_v2'
RATE = 48000
RECIPES = {
    'phone_vibration': dict(source='small_fan',start=6.0,end=6.42,low=65,high=700,peak=.25,attack=.018,release=.045,
        function='Single short motor burst; recorded small-fan motor used as Foley substitute, not a phone recording.'),
    'phone_place': dict(source='plastic_thump_1',start=.010,end=.225,low=75,high=2200,peak=.26,attack=.0015,release=.028,
        function='Muted object contact; plastic thump is Foley substitution for the phone contacting the case.'),
    'lid_close': dict(source='plastic_case_1',start=2.233,end=2.415,low=70,high=5400,peak=.46,attack=.0015,release=.022,
        function='Short case closure with stronger contact than the phone deposit.'),
    'button': dict(source='button_3',start=0.,end=.090,low=140,high=5000,peak=.19,attack=.001,release=.018,
        function='First press only; release click from the same recording is excluded.'),
    'lock_engage': dict(source='ratchet_muted_3',start=.145,end=.235,low=150,high=4400,peak=.28,attack=.001,release=.014,
        function='Short recorded ratchet tooth contact for mechanical engagement.'),
    'pencil_place': dict(source='wood_rattle_1',start=.065,end=.240,low=180,high=6500,peak=.21,attack=.0015,release=.024,
        function='Short wooden contact used as pencil-placement Foley substitute; no invented rolling or writing.'),
    'lock_release': dict(source='spring_blade_2',start=.007,end=.155,low=140,high=5600,peak=.31,attack=.001,release=.025,
        function='Spring mechanism release; distinct source from the engagement ratchet, no musical reward.'),
    'lid_hinge': dict(source='hinge_1',start=1.850,end=2.400,low=170,high=3600,peak=.20,attack=.018,release=.045,
        function='Real metal-hinge movement excerpt following the 0.55-second visible opening.'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_wav(path, samples):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    samples = np.asarray(samples,dtype=np.float64)
    if not np.isfinite(samples).all() or np.max(np.abs(samples),initial=0.) > 1.:
        raise ValueError('Nonfinite or clipping audio: '+str(path))
    channels = 1 if samples.ndim == 1 else samples.shape[1]
    pcm = np.rint(samples*32767.).astype('<i2')
    with wave.open(str(path),'wb') as f:
        f.setnchannels(channels);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm.tobytes())


def read_wav(path):
    with wave.open(str(path),'rb') as f:
        if f.getframerate()!=RATE or f.getsampwidth()!=2:raise ValueError('Unexpected WAV format')
        ch=f.getnchannels();x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float64)/32767.
    return x.reshape(-1,ch).mean(axis=1)


def decode_source(path):
    x=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar',str(RATE),'-f','f32le','-'],
        check=True,stdout=subprocess.PIPE).stdout
    return np.frombuffer(x,dtype='<f4').astype(np.float64)


def fade(x,attack,release):
    x=x.copy();a=min(len(x)//2,round(attack*RATE));r=min(len(x)//2,round(release*RATE))
    if a:x[:a]*=np.sin(np.linspace(0.,np.pi/2,a))**2
    if r:x[-r:]*=np.cos(np.linspace(0.,np.pi/2,r))**2
    x[0]=x[-1]=0.
    return x


def prepare_bank():
    provenance=json.loads((ASSETS/'provenance.json').read_text())
    originals={e['id']:e for e in provenance['sources']};decoded={};sounds={}
    for name,recipe in RECIPES.items():
        source=originals[recipe['source']];path=ASSETS/source['file']
        if sha(path)!=source['sha256']:raise ValueError('Source changed: '+recipe['source'])
        if recipe['source'] not in decoded:decoded[recipe['source']]=decode_source(path)
        x=decoded[recipe['source']][round(recipe['start']*RATE):round(recipe['end']*RATE)].copy()
        x-=np.mean(x)
        # Fixed second-order bandpass, zero-phase, no varying gain or resynthesis.
        sos=butter(2,[recipe['low'],recipe['high']],btype='bandpass',fs=RATE,output='sos')
        x=sosfiltfilt(sos,x);x=fade(x,recipe['attack'],recipe['release'])
        peak=float(np.max(np.abs(x),initial=0.))
        if peak<1e-8:raise ValueError('Silent excerpt '+name)
        x*=recipe['peak']/peak
        file=ASSETS/'effets'/(name+'.wav');write_wav(file,x);q=read_wav(file)
        energy=np.convolve(q*q,np.ones(240)/240,mode='same')
        active=np.flatnonzero(energy>=float(energy.max())*.01)
        sounds[name]=dict(recipe,file='effets/'+name+'.wav',sha256=sha(file),duration=len(q)/RATE,group='foley',
            peak_dbfs=float(20*np.log10(max(abs(q).max(),1e-12))),rms_dbfs=float(20*np.log10(max(np.sqrt(np.mean(q*q)),1e-12))),
            first_significant_energy_seconds=float(active[0]/RATE),peak_sample_seconds=float(np.argmax(abs(q))/RATE),
            accent_contract='at = visible action. File begins with only stated short attack. No offset added.',
            listening_performed=False)
    bank=dict(sample_rate=RATE,channels=1,bits=16,sounds=sounds,listening_performed=False,
        direction='Eight sparse recorded-material events. Fixed gains, no music, voice, tones, ticks or synthetic ambience.',
        limits='Source names document origin; auditory object recognition, comfort and artistic fit have not been verified by listening.')
    (ASSETS/'bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n')
    return bank


def load_bank():
    bank=json.loads((ASSETS/'bank.json').read_text())
    if (bank['sample_rate'],bank['channels'],bank['bits'])!=(RATE,1,16):raise ValueError('Unexpected bank format')
    for e in json.loads((ASSETS/'provenance.json').read_text())['sources']:
        if sha(ASSETS/e['file'])!=e['sha256']:raise ValueError('Original source changed: '+e['id'])
    for name,e in bank['sounds'].items():
        if sha(ASSETS/e['file'])!=e['sha256']:raise ValueError('Bank file changed: '+name)
    return bank


def render_audio(timeline_path,output_path):
    timeline_path,output_path=Path(timeline_path),Path(output_path)
    timeline=json.loads(timeline_path.read_text());duration=float(timeline['duration'])
    if not 0.<duration<120.:raise ValueError('Invalid episode duration')
    cues=timeline['audio_cues'];bank=load_bank();mix=np.zeros((round(duration*RATE),2),dtype=np.float64)
    rows=[];ids=set();stems={}
    for cue in cues:
        ident,name=str(cue['id']),str(cue['sound'])
        if ident in ids:raise ValueError('Duplicate cue id '+ident)
        ids.add(ident)
        if name not in bank['sounds']:raise ValueError('Unknown sound '+name)
        info=bank['sounds'][name];at=float(cue['at']);gain=float(cue.get('gain_db',0));pan=float(cue.get('pan',0))
        if not 0.<=at<duration or not -1.<=pan<=1. or not -50.<=gain<=12.:raise ValueError('Invalid cue '+ident)
        mono=read_wav(ASSETS/info['file'])*10**(gain/20.)
        angle=(pan+1.)*np.pi/4.;signal=mono[:,None]*np.array([np.cos(angle),np.sin(angle)])[None,:]
        start=round(at*RATE)
        if start+len(signal)>len(mix):raise ValueError('Cue exceeds duration '+ident)
        mix[start:start+len(signal)]+=signal
        stem=np.zeros_like(mix);stem[start:start+len(signal)]=signal;stems[ident]=stem
        rows.append(dict(id=ident,sound=name,at=at,start_sample=start,duration=len(mono)/RATE,gain_db=gain,pan=pan,
            group='foley',sound_sha256=info['sha256'],source=info['source'],
            first_significant_energy_at=at+info['first_significant_energy_seconds'],peak_at=at+info['peak_sample_seconds']))
    peak=float(np.max(np.abs(mix),initial=0.))
    if peak>.85:raise ValueError('Mix too loud: adjust explicit cue gains; no auto-compression allowed')
    write_wav(output_path,mix);write_wav(output_path.parent/'stems/foley.wav',mix)
    for ident,stem in stems.items():write_wav(output_path.parent/'stems'/('cue_'+ident+'.wav'),stem)
    with (output_path.parent/'cues.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['id','sound','at']);w.writeheader();w.writerows(rows)
    (output_path.parent/'cues.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    report=dict(file=output_path.name,sha256=sha(output_path),timeline_sha256=sha(timeline_path),bank_sha256=sha(ASSETS/'bank.json'),
        duration=duration,sample_rate=RATE,channels=2,bits=16,samples=len(mix),cues=len(rows),peak_linear=peak,
        peak_dbfs=float(20*np.log10(max(peak,1e-12))),rms_dbfs=float(20*np.log10(max(float(np.sqrt(np.mean(mix*mix))),1e-12))),
        music=False,voice=False,ambience=False,compressor=False,ducking=False,listening_performed=False,
        limitation='Numerical checks do not replace audition for material recognition, comfortable balance or comic effect.')
    (output_path.parent/'mix_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepare',action='store_true')
    p.add_argument('--timeline',type=Path);p.add_argument('--output',type=Path,default=EP/'audio/mix.wav');args=p.parse_args()
    if args.timeline:print(json.dumps(render_audio(args.timeline,args.output),ensure_ascii=False))
    elif args.prepare:print(json.dumps({'sounds':list(prepare_bank()['sounds']),'listening_performed':False}))
    else:p.error('Use --prepare or --timeline')

if __name__=='__main__':main()
