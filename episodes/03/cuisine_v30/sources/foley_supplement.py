"""V27 material Foley and a quiet room bed, without voices or detector beeps.

The cooking cue replaces the former frying cue; paper cues are restrained
additional textures. No image, original audio input, or global mix gain changes.
No auditory-quality claim is made: this module exposes reproducible signals.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np

EP=Path(__file__).resolve().parents[1]
ASSETS=EP/'assets/paper_recordings'
SILENCE=(32.,32.5)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _fade(n,sr,attack=.008,release=.035):
    e=np.ones(n,dtype=np.float64)
    a=min(n,max(2,round(attack*sr)));b=min(n,max(2,round(release*sr)))
    e[:a]*=np.sin(np.linspace(0,np.pi/2,a))**2
    e[-b:]*=np.cos(np.linspace(0,np.pi/2,b))**2
    return e


def _metrics(signal):
    x=np.asarray(signal,dtype=np.float64)
    def db(v):return float(20*np.log10(max(float(v),1e-15)))
    return {'rms_dbfs':db(np.sqrt(np.mean(x*x))),
            'peak_dbfs':db(np.abs(x).max()),'samples':len(x)}


def _calibrate(signal,target,peak_cap=-28.):
    x=np.asarray(signal,dtype=np.float64).copy()
    x-=x.mean(axis=0,keepdims=True)
    rms=float(np.sqrt(np.mean(x*x)));peak=float(np.abs(x).max())
    assert rms>0 and np.isfinite(x).all()
    gain=min(10**(target/20)/rms,10**(peak_cap/20)/peak)
    return x*gain,{'target_rms_dbfs':target,'peak_cap_dbfs':peak_cap,
                   'fixed_offline_gain_db':float(20*np.log10(gain))}


def _pan(x,pan):
    return np.asarray(x)*np.array([np.sqrt(1.-pan),np.sqrt(1.+pan)])[None,:]


@lru_cache(maxsize=12)
def _load(path,sr):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),
        '-ar',str(sr),'-ac','2','-c:a','pcm_f32le','-f','f32le','-'],stderr=subprocess.PIPE)
    return np.frombuffer(raw,'<f4').reshape(-1,2).astype(np.float64)


def _library():
    manifest=ASSETS/'provenance.json'
    entries={x['id']:x for x in json.loads(manifest.read_text())['sources']}
    for item in entries.values():
        assert _sha(ASSETS/item['path'])==item['sha256']
        assert _sha(ASSETS/item['licence_file'])==item['licence_sha256']
    return entries


def _source(item):
    return {'file':'assets/paper_recordings/'+item['path'],
            'sha256':item['sha256'],'url':item['source_url'],
            'author':item['author'],'licence':item['licence'],
            'licence_file':'assets/paper_recordings/'+item['licence_file'],
            'recording_method_verified':item['recording_method_verified'],
            'recording_method_note':item['recording_method_note']}


def _excerpt(item,offset,duration,sr):
    data=_load(str(ASSETS/item['path']),sr)
    a=round(offset*sr);n=round(duration*sr)
    assert a>=0 and a+n<=len(data),(item['id'],offset,duration,len(data)/sr)
    out=data[a:a+n].copy();out-=out.mean(axis=0)
    out*=_fade(n,sr,.004,.030)[:,None]
    return out


def _color_noise(n,sr,seed,low,high,pink=.0):
    raw=np.random.default_rng(seed).normal(0.,1.,n)
    spectrum=np.fft.rfft(raw);freq=np.fft.rfftfreq(n,1./sr)
    highpass=(freq/np.maximum(freq+low,1.))**2
    lowpass=1./(1.+(freq/high)**4)
    shaping=highpass*lowpass/np.maximum(freq,low)**pink
    out=np.fft.irfft(spectrum*shaping,n=n)
    return out/max(float(np.sqrt(np.mean(out*out))),1e-15)


def cues(timeline,sr=48000):
    """Return (metadata, float stereo) cues; summed before one delivery gain.

    ``replaces_kind='frying'`` on the cooking cue requests removal of V26's
    old continuous cooking event. Every returned signal is exactly zero in
    the requested absolute 32.000–32.500s silence, including the room bed.
    """
    assert sr>=8000 and float(timeline['duration'])==38.
    library=_library();result=[]

    def add(name,kind,start,signal,target=None,peak_cap=-28.,pan=0.,**meta):
        x=np.asarray(signal,dtype=np.float64)
        if x.ndim==1:x=np.column_stack((x,x))
        assert x.ndim==2 and x.shape[1]==2 and np.isfinite(x).all()
        x=_pan(x,pan)
        gain={}
        if target is not None:x,gain=_calibrate(x,target,peak_cap)
        else:
            ceiling=10**(peak_cap/20.)
            trim=min(1.,ceiling/max(float(np.abs(x).max()),1e-15))
            x*=trim
            gain={'peak_cap_dbfs':peak_cap,
                  'fixed_offline_gain_db':float(20*np.log10(trim))}
        a=max(0,round((SILENCE[0]-start)*sr));b=min(len(x),round((SILENCE[1]-start)*sr))
        if b>a:x[a:b]=0.
        metadata={'name':name,'kind':kind,'start':float(start),
            'duration':len(x)/sr,'sample_rate':sr,'channels':2,'pan':pan,
            'normalization':'Single offline gain for this cue; no mix or scene normalization',
            'gain':gain,'actual_metrics':_metrics(x),
            'limits':'Numerical waveform/source checks only, no listening or perceived-realism claim',**meta}
        assert start>=0 and start+len(x)/sr<=38.+1e-8
        result.append((metadata,x))

    # The synthetic low air/hood colour is a room cue, never a music-filling bed.
    n=round(38.*sr);time=np.arange(n)/sr
    air=_color_noise(n,sr,2701,70.,2300.,.45)
    fan=.28*np.sin(2*np.pi*92.*time)+.08*np.sin(2*np.pi*184.*time+.4)
    room=.78*air+fan
    stereo=np.column_stack((room,.97*room+.03*np.roll(air,round(.008*sr))))
    stereo,_=_calibrate(stereo,-55.,-44.)
    for j,(a,b) in enumerate(((0.,32.),(32.5,38.))):
        segment=stereo[round(a*sr):round(b*sr)].copy()
        segment*=_fade(len(segment),sr,.15 if j==0 else .10,.008 if j==0 else .40)[:,None]
        add(f'room_air_{j+1}_v27','room_ambience',a,segment,
            source={'method':'Original NumPy synthesis, seeded pink air and low92/184Hz fan partials',
                    'seed':2701,'recording':False},
            intention='Very low room presence, not a recorded kitchen or street ambience')

    # Reused material, new four-stage cooking envelope. The oil pops and dry
    # crackles below are original stylised synthesis, not false recordings.
    raw_path=EP/'audio/raw_bank/cuisson_v22.wav'
    raw=_load(str(raw_path),sr)[:round(31.95*sr)].copy()
    raw-=raw.mean(axis=0);wet=raw.copy()
    for channel in range(2):
        spectrum=np.fft.rfft(wet[:,channel]);freq=np.fft.rfftfreq(len(wet),1./sr)
        wet[:,channel]=np.fft.irfft(spectrum/(1.+(freq/3600.)**4),n=len(wet))
    wet,_=_calibrate(wet,-47.,-31.)
    clock=np.arange(len(wet))/sr
    stage=np.interp(clock,[0.,7.,15.,20.,26.,31.95],[.80,.85,1.05,1.20,1.40,1.12])
    dry=raw.copy()
    for channel in range(2):
        spectrum=np.fft.rfft(dry[:,channel]);freq=np.fft.rfftfreq(len(dry),1./sr)
        shape=(freq/(freq+1200.))**2/(1.+(freq/6200.)**4)
        dry[:,channel]=np.fft.irfft(spectrum*shape,n=len(dry))
    dry,_=_calibrate(dry,-47.,-31.)
    dry_amount=np.interp(clock,[0.,12.,19.5,26.,31.95],[0.,0.,.25,.72,.78])
    cooking=(wet*(1.-dry_amount[:,None])+dry*dry_amount[:,None])*stage[:,None]
    rng=np.random.default_rng(2702)
    crackles=[]
    for when in (15.75,17.20,19.82,21.15,22.52,24.12,25.04,26.42,27.82,29.32,30.66):
        span=float(rng.uniform(.018,.045));length=round(span*sr)
        noise=_color_noise(length,sr,int(rng.integers(100000,999999)),800.,5700.)
        envelope=np.exp(-np.arange(length)/(span*.25*sr))*_fade(length,sr,.002,.008)
        burst=np.column_stack((noise*envelope,noise*envelope))
        burst,_=_calibrate(burst,-47. if when<21. else -44.5,-31.)
        start=round(when*sr);cooking[start:start+length]+=burst
        crackles.append({'time_s':when,'duration_s':length/sr,'method':'Seeded short shaped-noise crackle'})
    oil_pops=[]
    for when,pitch in ((15.58,470.),(20.35,390.)):
        length=round(.095*sr);local=np.arange(length)/sr
        noise=_color_noise(length,sr,round(when*1000),1200.,5100.)
        pop=(.35*np.sin(2*np.pi*(pitch*local-650.*local*local))+.65*noise)
        pop*=np.exp(-local/.020)*_fade(length,sr,.003,.012)
        burst,_=_calibrate(np.column_stack((pop,pop)),-45.5,-30.)
        at=round(when*sr);cooking[at:at+length]+=burst
        oil_pops.append({'time_s':when,'duration_s':.095,'trigger':'tomato contact' if when<16. else 'salt added',
                         'method':'Original short damped noise/partial, not an oil recording'})
    cooking*=_fade(len(cooking),sr,.12,.16)[:,None]
    # Fixed whole-cue soft peak rounding removes the isolated synthetic click
    # crest without a moving detector or scene-by-scene gain correction.
    rms=float(np.sqrt(np.mean(cooking*cooking)));soft_ceiling=5.*rms
    cooking=np.tanh(cooking/max(soft_ceiling,1e-15))*soft_ceiling
    cooking,cooking_gain=_calibrate(cooking,-44.7,-29.)
    add('cuisson_progressive_v27','frying',0.,cooking,pan=-.28,
        replaces_kind='frying',
        source={'file':'audio/raw_bank/cuisson_v22.wav','sha256':_sha(raw_path),
                'method':'Previously synthesised MOU cooking source, spectrally softened plus new original crackles',
                'recording':False,'seed':2702},
        crackles=crackles,oil_pops=oil_pops,
        cooking_gain=cooking_gain,
        soft_peak_rounding={'method':'tanh with one fixed threshold for the complete cue','threshold_relative_to_rms':5.},
        stage_windows_s=[[0.,7.],[7.,15.],[15.,21.],[21.,31.95]],
        intention='Wet gentle fry becomes drier through the accumulated delay; no loud alarm')

    # Extra paper body, never a low thud. The last small ball stays lighter.
    for c in timeline['cycles']:
        number=int(c['id']);duration=(.20,.29,.40,.16)[number-1]
        target=(-47.,-45.7,-44.3,-49.)[number-1]
        x=np.zeros((round(duration*sr),2));parts=[]
        specs=([('flatten02',.10,.20,0.,1.)] if number==1 else
               [('paperscraps',.96,.29,0.,1.),('flatten02',.08,.20,.025,.45)] if number==2 else
               [('paperscraps',1.62,.40,0.,1.),('paperscraps',2.72,.34,.035,.55),('flatten02',.035,.28,.06,.35)] if number==3 else
               [('flatten02',.22,.16,0.,1.)])
        for source_id,offset,span,delay,gain in specs:
            item=library[source_id];clip=_excerpt(item,offset,span,sr)*gain
            a=round(delay*sr);length=min(len(clip),len(x)-a)
            x[a:a+length]+=clip[:length]
            parts.append({'source':_source(item),'offset_s':offset,'used_s':length/sr,
                          'delay_s':delay,'relative_gain':gain})
        x*=_fade(len(x),sr,.003,.040)[:,None]
        add(f'papier_tas_matiere_c{number}_v27','paper_heap_body',float(c['land']),x,target,
            pan=-.32,cycle=number,source=parts,
            intention='Light contact' if number==1 else 'Increasing paper-texture density' if number<4 else 'Small final scrap on full heap; deliberately quieter',
            sync={'contact_seconds':float(c['land']),'visual_action':'paper meets persistent heap'},
            additive_to_existing_paper_land=True)
    item=library['flatten02'];x=_excerpt(item,.29,.12,sr)
    add('papier_sol_matiere_v27','paper_floor_texture',float(timeline['paper_overflow']['floor_land']),x,-51.,pan=-.24,
        source=[{'source':_source(item),'offset_s':.29,'used_s':.12}],
        sync={'visual_action':'small scrap lands on floor'},additive_to_existing_paper_floor=True)

    for number in (1,3):
        c=timeline['cycles'][number-1];item=library['flatten01']
        duration=.12 if number==1 else .16
        x=_excerpt(item,.24 if number==1 else .40,duration,sr)
        add(f'papier_lacher_c{number}_v27','paper_release_texture',float(c['release']),x,
            -49. if number==1 else -48.,pan=-.15,
            source=[{'source':_source(item),'offset_s':.24 if number==1 else .40,'used_s':duration}],
            sync={'visual_action':'paper leaves actual hand','release_seconds':float(c['release'])},
            intention='A faint paper flutter on the real release, not a whoosh at every cut')

    n=round(.35*sr);time=np.arange(n)/sr
    tsss=_color_noise(n,sr,2703,900.,5000.)
    tsss*=np.exp(-time/.11)*_fade(n,sr,.008,.07)
    add('dernier_tsss_poele_v27','last_pan_sizzle',32.60,np.column_stack((tsss,tsss)),-45.,pan=-.28,
        source={'method':'Original NumPy shaped-noise decay, seed2703','recording':False,'seed':2703},
        intention='One short remaining hot-pan release after the half-second silence')

    # Parent integrator may sum freely: no cue here contaminates the pause.
    for meta,x in result:
        a=max(0,round((32.-meta['start'])*sr));b=min(len(x),round((32.5-meta['start'])*sr))
        assert b<=a or not np.any(x[a:b]),meta['name']
        assert float(np.abs(x).max())<=10**(-27.5/20.)
    return sorted(result,key=lambda cue:(cue[0]['start'],cue[0]['name']))
