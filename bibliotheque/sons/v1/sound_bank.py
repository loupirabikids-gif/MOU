"""MOU sound proposals: one small reusable source palette, twelve directed shapes.

No model listening was performed. Intention names are editorial suggestions,
not recognition results. Sources are CC0 assets of unverified production method.
"""
from __future__ import annotations
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import wave
import numpy as np

HERE=Path(__file__).resolve().parent
SR=48000
STATUS='proposition_non_validee'
FAMILIES=[
    ('hesitation','Hésitation','nasal','Geste suspendu, bouche étroite ou fermée.','Une bouche grande ouverte qui crie.'),
    ('effort','Effort','nasal_presse','Effort bref ou contraction avant un geste.','Une attente calme sans effort visible.'),
    ('surprise','Surprise','inspiration','Regard vers une cause, bouche qui s’ouvre.','Une grimace déjà terminée ou une bouche fermée.'),
    ('deception','Déception','expiration','Relâchement du corps après la perte constatée.','Un sourire déjà fier ou une action vive.'),
    ('satisfaction','Satisfaction','nasal','Examen d’un résultat, puis petit sourire retenu.','Une réaction de panique ou de dégoût.'),
    ('gene','Gêne','nasal_double','Deux petits accents d’embarras, sourire crispé.','Une découverte nouvelle demandant une grande surprise.'),
]
# Duration, source offset, pitch contours and envelopes differ intentionally.
# The character register stays near the same ooh +3 semitones reference.
SPECS=[
 dict(id='hesitation_01',family='hesitation',variant='retenue',duration=.24,source='ooh',offset=.11,pitch=[2.7,3.15,3.05],shape='hesitate',rms=-36.,cutoff=1450.),
 dict(id='hesitation_02',family='hesitation',variant='prolongée',duration=.36,source='ooh',offset=.08,pitch=[2.55,3.35,3.05],shape='question',rms=-35.2,cutoff=1500.),
 dict(id='effort_01',family='effort',variant='petit',duration=.18,source='ooh',offset=.17,pitch=[2.9,3.4,3.0],shape='press',rms=-36.,cutoff=1700.),
 dict(id='effort_02',family='effort',variant='plus marqué',duration=.26,source='ooh',offset=.12,pitch=[2.6,3.65,3.1],shape='press_long',rms=-34.7,cutoff=1850.),
 dict(id='surprise_01',family='surprise',variant='légère',duration=.14,source='breath_02',offset=.025,pitch=[2.2,2.8,2.5],shape='inhale',rms=-36.,cutoff=3600.),
 dict(id='surprise_02',family='surprise',variant='franche',duration=.25,source='ooh',offset=.075,pitch=[2.8,3.7,3.35],shape='gasp',rms=-34.5,cutoff=3100.),
 dict(id='deception_01',family='deception',variant='courte',duration=.34,source='breath',offset=.055,pitch=[1.2,.9,.5],shape='exhale',rms=-36.,cutoff=2900.),
 dict(id='deception_02',family='deception',variant='relâchée',duration=.50,source='breath',offset=.04,pitch=[1.5,.8,.2],shape='long_exhale',rms=-35.2,cutoff=2600.),
 dict(id='satisfaction_01',family='satisfaction',variant='retenue',duration=.18,source='ooh',offset=.115,pitch=[3.25,3.1,2.7],shape='round',rms=-36.,cutoff=1550.),
 dict(id='satisfaction_02',family='satisfaction',variant='fière',duration=.25,source='ooh',offset=.105,pitch=[3.0,3.55,2.85],shape='proud',rms=-35.2,cutoff=1650.),
 dict(id='gene_01',family='gene',variant='discrète',duration=.32,source='ooh',offset=.12,pitch=[3.0,3.3,2.85],shape='double',rms=-36.,cutoff=1450.),
 dict(id='gene_02',family='gene',variant='plus lisible',duration=.46,source='ooh',offset=.07,pitch=[2.8,3.45,2.9],shape='double_long',rms=-35.1,cutoff=1550.),
]


def _sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=4)
def _source(name):
    manifest=json.loads((HERE/'sources/provenance.json').read_text())
    entry=next(e for e in manifest['sources'] if e['id']==name)
    path=HERE/'sources'/entry['local_wav']
    assert _sha(path)==entry['wav_sha256']
    with wave.open(str(path),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        data=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).mean(axis=1)/32768.
    return data,entry


def _smooth(values):
    values=np.clip(values,0.,1.)
    return values*values*(3.-2.*values)


def _pulse(u,a,b,attack=.18,release=.24):
    local=(u-a)/max(b-a,1e-9)
    return _smooth(local/attack)*_smooth((1.-local)/release)*((local>=0.)&(local<=1.))


def _shape(name,u):
    if name=='hesitate':return _pulse(u,.03,.98,.25,.27)*(.72+.28*u)
    if name=='question':return _pulse(u,.02,.99,.36,.20)*(.48+.52*u)
    if name=='press':return _pulse(u,.01,.99,.10,.25)*(.74+.26*np.sin(np.pi*u))
    if name=='press_long':return _pulse(u,.01,.99,.18,.18)*(.55+.45*u)
    if name=='inhale':return _pulse(u,.01,.99,.27,.14)*(.40+.60*u)
    if name=='gasp':return _pulse(u,.01,.99,.14,.31)*(.90-.32*u)
    if name=='exhale':return _pulse(u,.01,.99,.10,.30)*(1.-.75*u)
    if name=='long_exhale':return _pulse(u,.01,.99,.16,.34)*np.exp(-1.7*u)
    if name=='round':return _pulse(u,.02,.99,.25,.30)*(.8+.2*np.sin(np.pi*u))
    if name=='proud':return _pulse(u,.01,.99,.18,.38)*(1.-.2*u)
    if name=='double':return .74*_pulse(u,.02,.38,.17,.23)+_pulse(u,.57,.98,.21,.26)
    if name=='double_long':return .65*_pulse(u,.02,.39,.23,.28)+_pulse(u,.62,.99,.16,.23)
    raise ValueError(name)


def energy_markers(data):
    """A reproducible numeric anchor, distinct from claiming perceived onset."""
    mono=np.asarray(data,dtype=np.float64).mean(axis=1)
    window=round(.004*SR)
    energy=np.sqrt(np.convolve(mono*mono,np.ones(window)/window,mode='same'))
    maximum=float(energy.max());above=energy>=.25*maximum
    run=round(.002*SR)
    valid=np.flatnonzero(np.convolve(above.astype(int),np.ones(run,dtype=int),mode='valid')>=run)
    anchor=int(valid[0]) if len(valid) else int(np.argmax(energy))
    return {'anchor_sample':anchor,'anchor_seconds':anchor/SR,
            'peak_sample':int(np.argmax(energy)),'peak_seconds':int(np.argmax(energy))/SR,
            'absolute_peak_sample':int(np.argmax(np.abs(mono))),
            'anchor_method':'First 2ms run at >=25% of maximum centered 4ms RMS; numeric, not a listening result.'}


def render(sample_id):
    """Return (float64 stereo waveform, metadata) without global episode paths."""
    spec=next(e for e in SPECS if e['id']==sample_id)
    source,provenance=_source(spec['source']);count=round(spec['duration']*SR)
    u=np.linspace(0.,1.,count)
    semitones=np.interp(u,[0.,.55,1.],spec['pitch'])
    ratio=2.**(semitones/12.)
    positions=spec['offset']*SR+np.cumsum(np.r_[0.,ratio[:-1]])
    if spec['shape'] in ('double','double_long'):
        spans=((.02,.38),(.57,.98)) if spec['shape']=='double' else ((.02,.39),(.62,.99))
        for a,b in spans:
            indices=np.flatnonzero((u>=a)&(u<=b))
            local=ratio[indices]
            # Each accent uses a fresh voiced grain, so the second does not
            # disappear into the source asset's naturally quiet ending.
            positions[indices]=spec['offset']*SR+np.cumsum(np.r_[0.,local[:-1]])
    assert positions[-1]<len(source),(sample_id,'source excerpt exceeds input')
    clip=np.interp(positions,np.arange(len(source)),source);clip-=clip.mean()
    frequencies=np.fft.rfftfreq(count,1./SR)
    highpass=frequencies**2/(frequencies**2+100.**2)
    lowpass=1./np.sqrt(1.+(frequencies/spec['cutoff'])**6)
    clip=np.fft.irfft(np.fft.rfft(clip)*highpass*lowpass,n=count)
    clip*=_shape(spec['shape'],u)
    if spec['shape']=='gasp':
        breath,_=_source('breath_02')
        air=np.interp(.015*SR+np.arange(count)*1.03,np.arange(len(breath)),breath)
        air*=.15*_pulse(u,.01,.52,.22,.35)
        clip+=air
    rms=float(np.sqrt(np.mean(clip**2)));peak=float(np.abs(clip).max())
    gain=min(10.**(spec['rms']/20.)/max(rms,1e-12),10.**(-22./20.)/max(peak,1e-12))
    clip*=gain;clip[0]=clip[-1]=0.
    stereo=np.rint(np.column_stack((clip,clip))*32768.)/32768.
    family=next(e for e in FAMILIES if e[0]==spec['family'])
    metadata={**spec,'title':family[1]+' — '+spec['variant'],'status':STATUS,
              'family_label':family[1],'mouth_type':family[2],
              'preferred_when':family[3],'avoid_when':family[4],
              'sample_rate':SR,'channels':2,'samples':count,'duration_seconds':count/SR,
              'source_file':'sources/'+provenance['local_wav'],'source_sha256':provenance['wav_sha256'],
              'source_url':provenance['url'],'licence':'CC0 1.0; bundled repository-wide notice',
              'source_method':'Original author and creation method unverified; no listening performed.',
              'processing':{'pitch_curve_semitones':spec['pitch'],'envelope':spec['shape'],
                  'highpass_hz':100.,'lowpass_hz':spec['cutoff'],'mono_centered':True,
                  'rms_target_dbfs':spec['rms'],'peak_cap_dbfs':-22.},
              'actual_rms_dbfs':float(20*np.log10(max(np.sqrt(np.mean(stereo**2)),1e-12))),
              'actual_peak_dbfs':float(20*np.log10(max(np.abs(stereo).max(),1e-12))),
              'usage':'Align the measured energy anchor with the intended visible event, not the file start.',
              'limits':'Editorial intentions are unvalidated proposals. No claim of human recording, wordlessness, emotion recognition or comfort at listening.'}
    metadata.update(energy_markers(stereo))
    return stereo,metadata


# Compatibility alias useful for editors expecting render(sample_id).
render_sound=render
