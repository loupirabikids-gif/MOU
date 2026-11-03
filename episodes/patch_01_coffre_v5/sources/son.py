"""Quiet, sparse Foley/UI for PATCH's reconstructed camera/acting episode (V4).

Prepare the bank: python sources/son.py --prepare
Render after the picture timing is frozen:
  python sources/son.py --timeline chronologie.json --output audio/mix.wav

Timeline contract: duration in seconds, audio_cues list with
{id, sound, at, gain_db=0, pan=0}. No music, voice, ambience or compressor.
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

EP = Path(__file__).resolve().parents[1]
ASSETS = EP/'assets/son'
RATE = 48000

# Source clips are existing CC0 library sounds, not recordings made for the
# episode. Pack notices explicitly grant sound reuse. Exact recording methods
# and subjective material fit are not established by those filenames.
RECIPES = {
    'tap': dict(source='click_button_1', start=0., end=.105, low=100., high=4200., peak=.105, group='foley'),
    'button': dict(source='click_button_1', start=.160, end=.270, low=100., high=4000., peak=.105, group='foley'),
    'phone_place': dict(source='spring_plastic_1', start=0., end=.130, low=100., high=1900., peak=.115, group='foley'),
    'lid_close': dict(source='spring_plastic_1', start=0., end=.235, low=90., high=2900., peak=.190, group='foley'),
    'lock': dict(source='ratchet_muted_1', start=.018, end=.160, low=130., high=3300., peak=.135, group='foley'),
    'unlock': dict(source='spring_plastic_2', start=.400, end=.635, low=120., high=2800., peak=.145, group='foley'),
    'paper': dict(source='paper_caress', start=0., end=.240, low=130., high=4400., peak=.080, group='foley'),
    'tick': dict(source='click_button_1', start=.160, end=.230, low=200., high=3400., peak=.034, group='tick'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_wav(path, samples):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = np.asarray(samples, dtype=np.float64)
    channels = 1 if samples.ndim == 1 else samples.shape[1]
    if np.max(np.abs(samples), initial=0.) > 1.:
        raise ValueError('Clipping refused: '+str(path))
    pcm = np.rint(samples*32767.).astype('<i2')
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(channels)
        stream.setsampwidth(2)
        stream.setframerate(RATE)
        stream.writeframes(pcm.tobytes())


def read_wav(path):
    with wave.open(str(path), 'rb') as stream:
        assert stream.getframerate() == RATE and stream.getsampwidth() == 2
        channels = stream.getnchannels()
        data = np.frombuffer(stream.readframes(stream.getnframes()), dtype='<i2').astype(np.float64)/32767.
    return data.reshape(-1,channels).mean(axis=1)


def decode_source(path):
    result = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ac','1',
                             '-ar',str(RATE),'-f','f32le','-'],
                            check=True, stdout=subprocess.PIPE)
    return np.frombuffer(result.stdout, dtype='<f4').astype(np.float64)


def soften(samples, low, high):
    """Zero-phase gentle band limiting and a DC removal, not synthetic noise."""
    samples = np.asarray(samples, dtype=np.float64)
    samples = samples-np.mean(samples)
    freqs = np.fft.rfftfreq(len(samples), 1/RATE)
    response = (1.-np.exp(-(freqs/max(low,1.))**4))*np.exp(-(freqs/high)**6)
    return np.fft.irfft(np.fft.rfft(samples)*response, n=len(samples))


def fade(samples, attack=.0015, release=.018):
    samples = np.asarray(samples, dtype=np.float64).copy()
    n, m = min(len(samples)//2,round(attack*RATE)), min(len(samples)//2,round(release*RATE))
    if n:
        samples[:n] *= np.sin(np.linspace(0.,np.pi/2,n))**2
    if m:
        samples[-m:] *= np.cos(np.linspace(0.,np.pi/2,m))**2
    samples[0] = samples[-1] = 0.
    return samples


def level(samples, peak):
    actual = float(np.max(np.abs(samples), initial=0.))
    if actual < 1.e-9:
        raise ValueError('Silent source excerpt')
    return samples*(peak/actual)


def note(frequency, duration, peak):
    t = np.arange(round(duration*RATE), dtype=np.float64)/RATE
    env = (1.-np.exp(-t/.010))*np.exp(-t/.095)
    signal = np.sin(2*np.pi*frequency*t)+.10*np.sin(2*np.pi*frequency*2*t)
    return level(fade(signal*env, .012, .045), peak)


def ui_pair(first, second, peak):
    result = np.zeros(round(.390*RATE), dtype=np.float64)
    for at, frequency, gain in ((0.,first,1.),(.145,second,.78)):
        x = note(frequency,.245,peak*gain)
        start = round(at*RATE)
        result[start:start+len(x)] += x
    return fade(result,.003,.025)


def prepare_bank():
    provenance = json.loads((ASSETS/'provenance.json').read_text())
    sources = {entry['id']:entry for entry in provenance['sources']}
    decoded = {}
    for source_id, entry in sources.items():
        path = ASSETS/entry['file']
        if sha(path) != entry['sha256']:
            raise ValueError('Source changed: '+source_id)
        decoded[source_id] = decode_source(path)
    rows = {}
    for name, recipe in RECIPES.items():
        original = decoded[recipe['source']]
        part = original[round(recipe['start']*RATE):round(recipe['end']*RATE)]
        part = level(fade(soften(part,recipe['low'],recipe['high'])), recipe['peak'])
        path = ASSETS/'effets'/(name+'.wav')
        write_wav(path,part)
        rows[name] = dict(recipe, file='effets/'+name+'.wav', sha256=sha(path),
                          duration=len(part)/RATE, origin='CC0 library excerpt, filtered and faded')
    # A short two-click clock/page accent can mark selected explicit ellipses.
    # Reuse the existing CC0 tick; do not add a continuous fast ticking bed.
    tick = read_wav(ASSETS/'effets/tick.wav')
    ellipsis = np.zeros(round(.205*RATE),dtype=np.float64)
    for at,gain in ((0.,.85),(.095,.55)):
        start=round(at*RATE)
        ellipsis[start:start+len(tick)] += tick*gain
    ellipsis=level(fade(ellipsis,.0015,.018),.045)
    path=ASSETS/'effets/ellipsis.wav'
    write_wav(path,ellipsis)
    rows['ellipsis']=dict(file='effets/ellipsis.wav',sha256=sha(path),duration=len(ellipsis)/RATE,
                          peak=float(np.max(np.abs(ellipsis))),group='tick',derived_from='tick',
                          origin='Two low CC0 clock clicks arranged for selected visible time ellipses')
    for name, signal in {
        'notification':ui_pair(659.255,783.991,.110),
        'end_ping':ui_pair(783.991,659.255,.120),
    }.items():
        path = ASSETS/'effets'/(name+'.wav')
        write_wav(path,signal)
        rows[name] = dict(file='effets/'+name+'.wav', sha256=sha(path), duration=len(signal)/RATE,
                          peak=float(np.max(np.abs(signal))), group='ui',
                          origin='Original deterministic additive synthesis; sine plus quiet second partial')
    manifest = {'sample_rate':RATE,'channels':1,'bits':16,'sounds':rows,
                'listening_performed':False,
                'direction':'Sparse events, no music/voices/continuous ambience, fixed gains.',
                'limits':'Numeric levels and spectral limits do not certify subjective comfort or material recognition.'}
    (ASSETS/'bank.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    return manifest


def load_bank():
    """Use the included, verified assets without rewriting them on each mix."""
    bank = json.loads((ASSETS/'bank.json').read_text())
    if (bank['sample_rate'],bank['channels'],bank['bits']) != (RATE,1,16):
        raise ValueError('Unexpected sound-bank format')
    provenance = json.loads((ASSETS/'provenance.json').read_text())
    for entry in provenance['sources']:
        if sha(ASSETS/entry['file']) != entry['sha256']:
            raise ValueError('Original source changed: '+entry['id'])
    for name,entry in bank['sounds'].items():
        if sha(ASSETS/entry['file']) != entry['sha256']:
            raise ValueError('Sound-bank asset changed: '+name)
    return bank


def render_audio(timeline_path, output_path):
    """Render only explicitly supplied cues after the coordinator freezes them."""
    timeline_path, output_path = Path(timeline_path), Path(output_path)
    timeline = json.loads(timeline_path.read_text())
    duration = float(timeline['duration'])
    if not 0. < duration < 120.:
        raise ValueError('Expected a short-episode duration in seconds')
    if 'audio_cues' not in timeline:
        raise ValueError('Frozen timeline needs an explicit audio_cues list')
    cues = timeline['audio_cues']
    bank = load_bank()
    assets = {name:read_wav(ASSETS/info['file']) for name,info in bank['sounds'].items()}
    groups = {name:np.zeros((round(duration*RATE),2),dtype=np.float64) for name in ('foley','ui','tick')}
    rows, ids = [], set()
    for cue in cues:
        identifier, name = str(cue['id']), str(cue['sound'])
        if identifier in ids:
            raise ValueError('Duplicate cue id: '+identifier)
        ids.add(identifier)
        if name not in assets:
            raise ValueError('Unknown sound '+name)
        at = float(cue['at'])
        gain_db = float(cue.get('gain_db',0.))
        pan = float(cue.get('pan',0.))
        if not 0. <= at < duration or not -1. <= pan <= 1. or not -50. <= gain_db <= 12.:
            raise ValueError('Invalid cue: '+identifier)
        source = assets[name]*(10.**(gain_db/20.))
        if at+len(source)/RATE > duration+.001:
            raise ValueError('Cue tail extends beyond episode: '+identifier)
        # Equal-power pan; at centre both channels receive the same -3dB.
        angle = (pan+1.)*np.pi/4.
        stereo = source[:,None]*np.array([np.cos(angle),np.sin(angle)])[None,:]
        start = round(at*RATE)
        group = bank['sounds'][name]['group']
        groups[group][start:start+len(source)] += stereo
        rows.append({'id':identifier,'sound':name,'at':at,'start_sample':start,
                     'duration':len(source)/RATE,'gain_db':gain_db,'pan':pan,'group':group,
                     'sound_sha256':bank['sounds'][name]['sha256']})
    mix = sum(groups.values())
    peak = float(np.max(np.abs(mix),initial=0.))
    if peak > .85:
        raise ValueError('Mix peak too high; adjust the explicit cue gains, not a scene compressor')
    write_wav(output_path,mix)
    for group, samples in groups.items():
        write_wav(output_path.parent/'stems'/(group+'.wav'),samples)
    with (output_path.parent/'cues.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['id','sound','at'])
        writer.writeheader();writer.writerows(rows)
    (output_path.parent/'cues.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    report = {'file':output_path.name,'sha256':sha(output_path),'timeline_sha256':sha(timeline_path),
              'duration':duration,'sample_rate':RATE,'channels':2,'bits':16,'samples':len(mix),
              'cues':len(rows),'peak_linear':peak,'peak_dbfs':20*np.log10(max(peak,1.e-12)),
              'rms_dbfs':20*np.log10(max(float(np.sqrt(np.mean(mix*mix))),1.e-12)),
              'music':False,'voice':False,'compressor':False,'listening_performed':False,
              'limits':'Reproducible editing and numeric checks; human audition still needed for perceived material fit and comfort.'}
    (output_path.parent/'mix_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--timeline',type=Path)
    parser.add_argument('--output',type=Path,default=EP/'audio/mix.wav')
    args=parser.parse_args()
    if args.timeline:
        print(json.dumps(render_audio(args.timeline,args.output),ensure_ascii=False))
    elif args.prepare:
        bank=prepare_bank();print(json.dumps({'sounds':list(bank['sounds']),'sample_rate':RATE,'listening_performed':False}))
    else:
        parser.error('Use --prepare or --timeline after picture timings are frozen')


if __name__=='__main__':main()
