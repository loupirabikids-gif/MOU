"""The rounded mitten/thumb approved in the isolated b4b0f78 study.

Coordinates and local deformation are copied from that study. Only the study
clock is fitted to the existing washing interval; no production rig is imported.
"""
from __future__ import annotations

import math

INK, SKIN, STROKE = '#2B0A24', '#D8F449', 8.372
OPEN = (
    (174.,1087.60),
    (161.,1084.),(151.,1082.),(143.,1080.),
    (135.,1078.),(133.,1067.),(122.,1067.),
    (111.,1067.),(106.,1077.),(112.,1085.),
    (115.,1089.),(119.,1091.),(123.,1095.),
    (110.,1093.),(97.,1099.),(94.,1110.),
    (89.,1126.),(104.,1137.),(122.,1138.),
    (142.,1140.),(156.,1132.),(174.,1126.8),
)
CONTACT = (
    (174.,1087.60),
    (161.,1084.),(147.,1081.),(135.,1081.),
    (123.,1081.),(114.,1082.),(108.,1087.),
    (102.,1092.),(103.,1097.),(109.,1100.),
    (115.,1103.),(120.,1103.),(127.,1106.),
    (115.,1101.),(101.,1104.),(96.,1114.),
    (91.,1128.),(105.,1137.),(122.,1138.),
    (142.,1140.),(156.,1132.),(174.,1126.8),
)


def smooth(v):
    v=max(0.,min(1.,v))
    return v*v*(3.-2.*v)


def pose_at(progress=None, rub_cycles=3):
    """Fit the approved contact/rub/release to one wash, without long holds."""
    t=.30 if progress is None else .65+2.70*max(0.,min(1.,progress))
    if t<.65:
        amount=0.; phase='pose_moufle'
    elif t<1.10:
        amount=smooth((t-.65)/.45); phase='contact_pouce'
    elif t<2.90:
        amount=1.; phase='frottement'
    elif t<3.35:
        amount=1.-smooth((t-2.90)/.45); phase='relachement'
    else:
        amount=0.; phase='pose_moufle'
    points=[[a[0]+amount*(b[0]-a[0]),a[1]+amount*(b[1]-a[1])]
            for a,b in zip(OPEN,CONTACT)]
    if phase=='frottement':
        u=(t-1.10)/1.80
        wave=math.sin(2.*rub_cycles*math.pi*u)
        for i,weight in ((5,1.),(6,1.),(7,1.),(8,1.),(9,1.),(10,1.),(11,.3)):
            points[i][0]+=2.1*wave*weight
            points[i][1]+=.75*math.sin(4.*rub_cycles*math.pi*u)*weight
        for i,weight in ((13,.3),(14,.7),(15,1.),(16,.5)):
            points[i][1]-=.6*wave*weight
    return {'progress':progress,'study_clock':t,'phase':phase,
            'amount':amount,'rub_cycles':rub_cycles,'points':points}


def outline(points):
    d=f'M{points[0][0]:.6f} {points[0][1]:.6f} '
    for i in range(1,len(points),3):
        d+='C'+' '.join(f'{x:.6f} {y:.6f}' for x,y in points[i:i+3])+' '
    return d.strip()


def cubic(p, u):
    return tuple(sum(p[j][axis]*weight for j,weight in enumerate(
        ((1.-u)**3,3.*(1.-u)**2*u,3.*(1.-u)*u*u,u**3))) for axis in (0,1))


def sample_outline(points, samples_per_segment=40):
    return tuple(cubic(points[i:i+4],j/samples_per_segment)
                 for i in range(0,len(points)-1,3)
                 for j in range(samples_per_segment+1))


def fingertip(points):
    """True leftmost point on the grouped fingers' distal cubic, not the rig."""
    p=points[15:19]
    a,b,c,d=(point[0] for point in p)
    qa=-a+3.*b-3.*c+d; qb=2.*(a-2.*b+c); qc=b-a
    candidates=[0.,1.]
    if abs(qa)<1e-12:
        if abs(qb)>1e-12:
            candidates.append(-qc/qb)
    else:
        discriminant=qb*qb-4.*qa*qc
        if discriminant>=0.:
            root=math.sqrt(discriminant)
            candidates.extend(((-qb-root)/(2.*qa),(-qb+root)/(2.*qa)))
    return min((cubic(p,u) for u in candidates if 0.<=u<=1.),key=lambda v:v[0])
