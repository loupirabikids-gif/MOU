"""Small, restrained mix studies from MOU's own bank; production stays untouched.

The output is a numerical proposal for listening, not an auditory approval.
All files are post-mix level tests: do not apply the historic master gain again.
"""
from pathlib import Path
import hashlib
import json
import wave

import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
EP=ROOT/'episodes/03/cuisine_v21'
OUT=Path(__file__).resolve().parent/'palette_tests'
SR=48000


def read(name):
    path=EP/'audio'/name
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        signal=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).mean(axis=1)/32768.
    return signal,{'source':str(path.relative_to(ROOT)),
                   'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def soften(signal,lowpass,attack=.008,release=.030):
    n=len(signal);freq=np.fft.rfftfreq(n,1/SR)
    shape=(1.-np.exp(-(freq/100.)**4))/np.sqrt(1.+(freq/lowpass)**8)
    out=np.fft.irfft(np.fft.rfft(signal)*shape,n)
    a=min(n,round(attack*SR));b=min(n,round(release*SR))
    if a:out[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    if b:out[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return out


def level(signal,rms=None,peak=-21.):
    result=signal.copy()
    if rms is not None:result*=10**(rms/20)/max(np.sqrt(np.mean(result*result)),1e-12)
    elif peak is not None:result*=10**(peak/20)/max(np.abs(result).max(),1e-12)
    if peak is not None:
        result*=min(1.,10**(peak/20)/max(np.abs(result).max(),1e-12))
    return result


def save(name,mono,inputs,parameters):
    path=OUT/name;stereo=np.column_stack((mono,mono));pcm=np.rint(stereo*32767).astype('<i2')
    assert np.abs(pcm.astype(np.int32)).max()<32767
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(pcm.tobytes())
    return {'file':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'duration_seconds':len(mono)/SR,'stage':'post-mix test level; no extra master gain',
            'sources':inputs,'parameters':parameters,
            'peak_dbfs':20*np.log10(max(float(np.abs(stereo).max()),1e-12))}


def main():
    OUT.mkdir(parents=True,exist_ok=True);items=[]
    # One stream, with no separate hand-water layer.
    water,source=read('c1_eau.wav');water=water[:round(1.5*SR)]
    water=level(soften(water,2400,.045,.070),rms=-32.,peak=-21.)
    take=np.zeros(round(2.*SR));take[round(.2*SR):round(.2*SR)+len(water)]=water
    items.append(save('eau_une_couche_test.wav',take,[source],
        {'lowpass_hz':2400,'attack_seconds':.045,'release_seconds':.070,
         'target_active_rms_dbfs':-32,'peak_cap_dbfs':-21,'separate_hand_layer':False}))
    pull,pull_src=read('c1_papier_deroule.wav');tear,tear_src=read('c1_papier_dechire.wav')
    pull=level(soften(pull,2600,.025,.045),rms=-35,peak=-23)
    tear=level(soften(tear,2800,.005,.025),peak=-22)
    take=np.zeros(round(2.*SR));a=round(.2*SR);take[a:a+len(pull)]+=pull
    a+=len(pull);take[a:a+len(tear)]+=tear
    items.append(save('papier_un_geste_test.wav',take,[pull_src,tear_src],
        {'one_pull_then_one_tear':True,'pull_lowpass_hz':2600,'tear_lowpass_hz':2800,
         'pull_target_rms_dbfs':-35,'tear_peak_dbfs':-22,
         'separate_wipe_crumple_flight_layers':False}))
    knife,source=read('carotte_coupe_1.wav')
    knife=level(soften(knife,2700,.0025,.020),peak=-21)
    take=np.zeros(round(1.7*SR))
    for when,gain in ((.3,1.),(1.,.87)):
        a=round(when*SR);take[a:a+len(knife)]+=knife*gain
    items.append(save('couteau_transitoires_retenus_test.wav',take,[source],
        {'lowpass_hz':2700,'attack_seconds':.0025,'peak_dbfs_first':-21,
         'two_contacts_seconds':[.3,1.],'production_retiming':False}))
    # Same three opening notes, quieter; no alteration of their pitch or timing.
    take=np.zeros(round(2.*SR));sources=[]
    for name,when in [('sifflement_p1_n1.wav',.3),('sifflement_p1_n2.wav',.855556),('sifflement_p1_n3.wav',1.411111)]:
        signal,source=read(name);sources.append(source)
        signal=level(soften(signal,2600,.020,.035),peak=-20.5)
        a=round(when*SR);take[a:a+len(signal)]+=signal
    items.append(save('sifflement_niveau_retenu_test.wav',take,sources,
        {'same_three_notes':True,'lowpass_hz':2600,'postmix_peak_dbfs':-20.5,
         'new_voice_or_melody':False}))
    manifest={'scope':'Listening studies only; no production file modified.',
              'tools':['Python','NumPy','wave'],
              'asset_origin':'Derived from original MOU synthetic banks, whose existing provenance is kept.',
              'claims':'No listening performed; fewer layers/lower high-frequency energy are measurable, pleasantness remains unverified.',
              'files':items}
    (OUT/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'output':str(OUT),'files':[e['file'] for e in items]},indent=2))


if __name__=='__main__':main()
