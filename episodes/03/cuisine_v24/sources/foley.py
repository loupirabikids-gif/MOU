"""Original deterministic dry-paper Foley, synthesized locally for MOU V24.

No recording, speech model, external sample or network request is used.
Peak levels below precede the unchanged +3.50 dB delivery gain.
"""
import math
import numpy as np

SR=48000
# Frozen measurement:240 samples per actual V23 relative-mitten trajectory,
# local speed maxima after approach, separated by at least .22 wipe duration.
MOTION_SYNC={1:[(11.74576,279.7),(12.05567,192.1)],
             2:[(19.87547,297.2),(20.17028,204.1)],
             3:[(25.56459,365.8),(25.80354,251.3)],
             4:[(31.44576,279.7),(31.75567,192.1)],
             5:[(37.59862,140.3),(38.01477,47.5)]}


def noise(rng,n,low=240.,high=1900.):
    freq=np.fft.rfftfreq(n,1./SR)
    response=(1.-np.exp(-(freq/low)**4))/np.sqrt(1.+(freq/high)**8)
    return np.fft.irfft(np.fft.rfft(rng.standard_normal(n))*response,n)


def stereo_peak(mono,peak_dbfs,pan=-.03):
    angle=(pan+1.)*np.pi/4.
    signal=mono[:,None]*np.array([math.cos(angle),math.sin(angle)])[None,:]
    signal*=10.**(peak_dbfs/20.)/max(float(np.abs(signal).max()),1e-12)
    return np.rint(signal*32767.).astype(np.int32)


def rub(duration,seed,peak):
    rng=np.random.default_rng(seed);n=round(duration*SR);u=np.arange(n)/(n-1)
    mono=noise(rng,n,300.,1800.);grains=np.zeros(n)
    for centre in rng.uniform(.16,.84,11):
        size=round(rng.uniform(.0025,.006)*SR)
        start=max(0,min(n-size,round(centre*n)-size//2))
        grain=noise(rng,size,380.,2100.)
        grains[start:start+size]+=grain*np.sin(np.linspace(0,np.pi,size))**2*rng.uniform(.3,.7)
    mono=(.65*mono+.35*grains)*np.sin(np.pi*u)**1.65
    return stereo_peak(mono,peak)


def crumple(duration,seed,peak):
    rng=np.random.default_rng(seed);n=round(duration*SR);mono=np.zeros(n)
    for centre in (.17,.33,.55,.77):
        size=round(rng.uniform(.035,.065)*SR)
        start=max(0,min(n-size,round((centre+rng.uniform(-.025,.025))*n)-size//2))
        grain=noise(rng,size,190.,1750.)
        mono[start:start+size]+=grain*np.sin(np.linspace(0,np.pi,size))**1.4*rng.uniform(.55,1.)
    mono*=np.sin(np.linspace(0,np.pi,n))**.6
    return stereo_peak(mono,peak,-.05)


def land(duration,seed,peak):
    rng=np.random.default_rng(seed);n=round(duration*SR);t=np.arange(n)/SR
    mono=(noise(rng,n,100.,1300.)*np.exp(-t/.026)+
          .16*np.sin(2*np.pi*155.*t)*np.exp(-t/.028))*(1.-np.exp(-t/.0035))
    tail=min(n,round(.025*SR));mono[-tail:]*=np.cos(np.linspace(0,np.pi/2,tail))**2
    return stereo_peak(mono,peak,-.08)


def cues(timeline):
    result=[]
    for cycle in timeline['cycles']:
        number=int(cycle['id']);tiny=bool(cycle.get('tiny'));a,b=cycle['wipe']
        for index,(centre,speed) in enumerate(MOTION_SYNC[number],1):
            duration=.11 if tiny and index==2 else .12 if number==3 else .14
            start=centre-duration/2.;assert a<=start and start+duration<=b
            seed=3241000+number*100+index;peak=(-29. if tiny else -25.5)+(0. if index==1 else -.7)
            meta={'name':f'c{number}_essuyage_{index}_v24',
                  'kind':'tiny_paper_wipe' if tiny else 'paper_wipe','cycle':number,
                  'start':start,'duration':duration,'seed':seed,'peak_dbfs_requested':peak,
                  'sync':{'target':'relative_mitten_motion_speed_peak','centre_seconds':centre,
                          'relative_speed_pixels_per_second':speed,'action_interval':cycle['wipe'],
                          'method':'V23 state.hands[right]-state.hands[left],240 samples; numpy.gradient; maxima after32%approach, before94%, separation>=22%duration'},
                  'synthesis':'short warm dry friction with softly windowed irregular grains'}
            result.append((meta,rub(duration,seed,peak)))
        a,b=cycle['crumple'];seed=3242000+number*100;peak=-30. if tiny else -27.
        meta={'name':f'c{number}_froissage_v24',
              'kind':'tiny_paper_crumple' if tiny else 'paper_crumple','cycle':number,
              'start':a,'duration':b-a,'seed':seed,'peak_dbfs_requested':peak,
              'sync':{'target':'visible_paper_compression','action_interval':cycle['crumple']},
              'synthesis':'four irregular soft grain compressions, warm paper spectrum'}
        result.append((meta,crumple(b-a,seed,peak)))
        if number in (2,3,4):
            duration=.14;seed=3243000+number*100;peak=-27.+.3*(number-2)
            meta={'name':f'c{number}_poubelle_impact_v24','kind':'paper_land','cycle':number,
                  'start':cycle['land'],'duration':duration,'seed':seed,'peak_dbfs_requested':peak,
                  'sync':{'target':'paper_reaches_bin','contact_seconds':cycle['land']},
                  'synthesis':'soft low paper thump with rounded3.5ms attack'}
            result.append((meta,land(duration,seed,peak)))
    assert len(result)==18
    return result
