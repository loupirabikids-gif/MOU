"""PATCH: the original raccoon concept made into a small analytic SVG puppet.

World-space palm controls keep both short sleeves connected to the shoulders.
The parent scene owns props, cameras, timing and occlusion by its desk.
"""
from __future__ import annotations
import html
import json
import math
from pathlib import Path

P=json.loads(Path(__file__).with_name('palette.json').read_text())
INK=P['ink']; FUR=P['fur']; LIGHT=P['light']; CREAM=P['cream']
MASK=P['mask']; CORAL=P['coral']; CORAL_DARK=P['coral_dark']; WHITE=P['white']
BASE_SCALE=1.25
SHOULDERS={'left':(266.,552.),'right':(427.,550.)}
REST_HANDS={'left':(211.,660.),'right':(480.,654.)}

BASE=dict(open_l=1.,open_r=1.,pupil=14.,brow_raise_l=0.,brow_raise_r=0.,
          brow_l0=0.,brow_lq=-20.,brow_l1=-2.,brow_r0=-6.,brow_rq=-24.,brow_r1=-12.,
          mouth_width=74.,mouth_smile=.8,mouth_open=0.,mouth_skew=.0,blush=0.,
          eye_scale=1.,sparkle=0.)


def pose(**change):return dict(BASE,**change)


POSES={
 'curieux':pose(),
 'idee':pose(pupil=15.,brow_raise_l=10.,brow_raise_r=14.,mouth_width=70.,mouth_open=.35,mouth_smile=.95),
 'satisfait':pose(open_l=.6,open_r=.69,pupil=15.,brow_raise_r=6.,mouth_width=78.,mouth_smile=1.1,mouth_skew=.25),
 'impatient':pose(open_l=.45,open_r=.45,pupil=13.,brow_l0=-2.,brow_lq=5.,brow_l1=18.,
                  brow_r0=18.,brow_rq=0.,brow_r1=-2.,mouth_width=60.,mouth_smile=-.2),
 'concentre':pose(open_l=.83,open_r=.83,pupil=13.,brow_l0=0.,brow_lq=2.,brow_l1=13.,
                  brow_r0=13.,brow_rq=2.,brow_r1=0.,mouth_width=44.,mouth_smile=.0),
 'surprise':pose(pupil=10.5,brow_raise_l=16.,brow_raise_r=18.,mouth_width=65.,mouth_open=.85,mouth_smile=.8),
 'gene':pose(open_l=.65,open_r=.95,pupil=13.,brow_raise_l=1.,brow_raise_r=12.,
             brow_l0=10.,brow_lq=-12.,brow_l1=-9.,mouth_width=72.,mouth_smile=.65,mouth_skew=.9,blush=.26),
 'ennui':pose(open_l=.43,open_r=.49,pupil=13.5,
              brow_l0=7.,brow_lq=-7.,brow_l1=-13.,brow_r0=-13.,brow_rq=-7.,brow_r1=7.,
              mouth_width=46.,mouth_smile=-.30,mouth_skew=.10),
 'suppliant':pose(open_l=1.,open_r=1.,pupil=17.,eye_scale=1.10,sparkle=.85,
                  brow_l0=12.,brow_lq=-13.,brow_l1=-26.,brow_r0=-26.,brow_rq=-13.,brow_r1=12.,
                  mouth_width=42.,mouth_smile=-.16),
 'joie':pose(open_l=1.,open_r=1.,pupil=16.,eye_scale=1.06,sparkle=1.,
             brow_raise_l=11.,brow_raise_r=12.,mouth_width=82.,mouth_open=.62,mouth_smile=1.),
}


def default_state():
    return dict(cx=540.,floor_y=1570.,scale=1.,pose='curieux',gaze=(.4,-.35),blink=1.,
                body_tilt=0.,head_tilt=0.,lean=(0.,0.),tail_angle=0.,seated=True,hands={})


def n(v):return f'{float(v):.5f}'


def path(d,fill='none',stroke=INK,w=6.,extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{n(w)}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def ellipse(x,y,rx,ry,fill,stroke='none',w=0.,extra=''):
    return f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(ry)}" fill="{fill}" stroke="{stroke}" stroke-width="{n(w)}" {extra}/>'


def clamp(v,a,b):return max(a,min(b,float(v)))


def face_parameters(state):
    weights=state.get('pose_weights')
    if weights:
        total=sum(max(0.,float(v))for v in weights.values())
        if total<=0:raise ValueError('Positive pose weight required')
        f={k:sum(POSES[name][k]*max(0.,float(v))for name,v in weights.items())/total for k in BASE}
    else:f=dict(POSES[state.get('pose','curieux')])
    for k,v in state.get('face',{}).items():
        if k not in BASE:raise ValueError('Unknown facial parameter '+k)
        f[k]=float(v)
    return f


def matrix(state):
    scale=BASE_SCALE*float(state.get('scale',1.))
    angle=math.radians(float(state.get('body_tilt',0.)));c,s=math.cos(angle),math.sin(angle)
    lx,ly=state.get('lean',(0.,0.))
    px=float(state.get('cx',540.))+lx
    py=float(state.get('floor_y',1570.))-109.*scale+ly
    return c*scale,s*scale,-s*scale,c*scale,px-scale*(337*c-735*s),py-scale*(337*s+735*c)


def to_world(point,state):
    a,b,c,d,tx,ty=matrix(state);x,y=point
    return a*x+c*y+tx,b*x+d*y+ty


def to_local(point,state):
    a,b,c,d,tx,ty=matrix(state);x,y=point[0]-tx,point[1]-ty;det=a*d-b*c
    return (d*x-c*y)/det,(-b*x+a*y)/det


def _hand(side,state):
    value=state.get('hands',{}).get(side,{})
    if isinstance(value,(list,tuple)):value={'x':value[0],'y':value[1]}
    default=to_world(REST_HANDS[side],state)
    return dict(x=float(value.get('x',default[0])),y=float(value.get('y',default[1])),
                rotation=float(value.get('rotation',0.)),grip=clamp(value.get('grip',0.),0.,1.))


def anchors(state):
    hands={side:(_hand(side,state)['x'],_hand(side,state)['y'])for side in SHOULDERS}
    wrists={}
    for side in SHOULDERS:
        palm=to_local(hands[side],state);sx,sy=SHOULDERS[side]
        dx,dy=palm[0]-sx,palm[1]-sy;length=max(1.,math.hypot(dx,dy))
        wrists[side]=tuple(state.get('wrists',{}).get(side,
            to_world((palm[0]-dx/length*26.,palm[1]-dy/length*26.),state)))
    hsx,hsy=state.get('head_shift',(0.,0.))
    return {'head':to_world((337.+hsx,372.+hsy),state),
            'shoulders':{side:to_world(point,state)for side,point in SHOULDERS.items()},
            'hands':hands,'wrists':wrists,
            'feet':{side:to_world(foot,state)for side,foot in feet_local(state).items()}}


def feet_local(state):
    """The two real foot controls follow the body, including its jump offset."""
    spread=clamp(state.get('jump_spread',0.),0.,1.)
    return {'left':(281.-76.*spread,825.-18.*spread),
            'right':(421.+56.*spread,826.-19.*spread)}


def _legs(state,uid):
    spread=clamp(state.get('jump_spread',0.),0.,1.)
    if spread<=.001:
        return (path('M265 735 L319 735 L316 816 Q291 833 264 816 Z',FUR,w=7)+
                path('M373 738 L427 737 L438 811 Q416 836 384 820 Z',FUR,w=7)+
                path('M265 799 C240 799 231 825 249 840 L304 840 Q326 834 317 812 Z',MASK,w=6,
                     extra=f'id="{uid}-foot-left"')+
                path('M386 803 C375 820 378 840 399 844 L452 842 C475 830 456 807 432 802 Z',MASK,w=6,
                     extra=f'id="{uid}-foot-right"'))
    feet=feet_local(state);parts=[]
    for side,hip,sign in [('left',(289.,746.),-1.),('right',(399.,746.),1.)]:
        fx,fy=feet[side];hx,hy=hip
        # Short broad legs fan out below the same hoodie, rather than stretching.
        d=(f'M{hx-25.} {hy-12.} L{hx+25.} {hy-10.} '
           f'Q{(hx+fx)/2.+20.} {hy+34.} {fx+22.} {fy+1.} '
           f'Q{fx} {fy+18.} {fx-23.} {fy+1.} '
           f'Q{(hx+fx)/2.-18.} {hy+28.} {hx-25.} {hy-12.} Z')
        parts.append(path(d,FUR,w=7,extra=f'id="{uid}-leg-{side}"'))
        parts.append(f'<g transform="translate({n(fx)} {n(fy)}) rotate({n(sign*30.*spread)})">'+
                     path('M-28 -19 C-44 -17 -45 7 -30 20 Q-1 27 30 18 C43 7 34 -15 19 -20 Z',
                          MASK,w=6,extra=f'id="{uid}-foot-{side}"')+'</g>')
    return ''.join(parts)


def _head(state,uid):
    p=[];f=face_parameters(state)
    # Native concept contours, kept separate from all facial controls.
    p.append(path('M-134 -85 C-172 -104 -177 -155 -148 -181 C-122 -205 -86 -179 -88 -134 Z',FUR))
    p.append(path('M-142 -115 C-155 -128 -153 -157 -139 -165 C-123 -172 -110 -151 -111 -135 Z',CREAM,w=0))
    p.append(path('M94 -129 C95 -174 126 -196 153 -180 C179 -164 174 -121 153 -98 Z',FUR))
    p.append(path('M117 -134 C119 -153 132 -166 144 -158 C157 -148 150 -129 141 -121 Z',CREAM,w=0))
    p.append(path('M146 -179 Q153 -156 174 -153',FUR,w=4))
    p.append(path('M-162 -39 C-162 -107 -104 -153 -37 -155 L-22 -170 L-8 -157 L8 -169 L20 -153 C93 -154 153 -120 170 -56 L181 -24 L168 -20 L182 4 L164 8 C159 83 101 130 19 139 C-62 148 -131 117 -156 58 L-173 43 L-164 29 L-180 14 L-164 1 Z',FUR))
    p.append(path('M-138 -56 C-111 -119 -45 -137 4 -133 C-12 -104 -15 -76 -8 -44 C-55 -58 -100 -50 -138 -30 Z',LIGHT,w=0))
    p.append(path('M-139 -43 C-119 -74 -68 -73 -32 -40 C-15 -24 -13 18 -32 46 C-57 79 -116 63 -139 31 C-154 10 -154 -17 -139 -43 Z',MASK,w=0))
    p.append(path('M40 -42 C69 -72 120 -66 144 -37 C161 -16 159 18 144 40 C120 73 69 65 46 44 C27 26 21 -21 40 -42 Z',MASK,w=0))
    p.append(path('M-3 -90 C3 -66 9 -46 15 -28 C22 -46 27 -65 31 -86',CREAM,w=0))
    p.append(path('M-117 64 C-91 50 -54 53 -24 65 C1 45 35 42 57 59 C88 45 123 57 139 76 C116 112 73 132 23 136 C-32 142 -81 119 -117 92 Z',CREAM,w=0))
    p.extend([ellipse(-15,70,46,28,CREAM),ellipse(47,68,40,27,CREAM)])
    gx,gy=state.get('gaze',(.4,-.35));blink=clamp(state.get('blink',1.),0.,1.)
    for side,x,y,rx,ry in [('l',-82.,-4.,36.,46.),('r',91.,-6.,32.,43.)]:
        rx*=clamp(f['eye_scale'],.9,1.15);ry*=clamp(f['eye_scale'],.9,1.15)
        ry=max(.55,ry*blink)
        clip=f'{uid}-eye-clip-{side}'
        shape=f'<ellipse cx="{n(x)}" cy="{n(y)}" rx="{n(rx)}" ry="{n(ry)}"/>'
        p.append(f'<defs><clipPath id="{clip}">{shape}</clipPath></defs>')
        shut=blink<.15
        p.append(ellipse(x,y,rx,ry,'none' if shut else WHITE,extra=f'id="{uid}-eye-white-{side}"'))
        p.append(f'<g clip-path="url(#{clip})" opacity="{0 if shut else 1}">')
        pr=clamp(f['pupil'],8.,18.)
        px=x+clamp(gx,-1.,1.)*16.;py=y+clamp(gy,-1.,1.)*18.
        p.extend([ellipse(px,py,pr,pr*1.22,INK,extra=f'id="{uid}-pupil-{side}"'),ellipse(px-4.,py-5.,4.,5.,WHITE)])
        if f['sparkle']>.01:
            p.append(ellipse(px+5.,py+7.,2.8,3.3,WHITE,extra=f'opacity="{n(clamp(f["sparkle"],0.,1.))}"'))
        opening=clamp(f['open_'+side],0.,1.)
        if opening<.999:
            ly=y-ry+2.*ry*(1.-opening)
            p.append(path(f'M{x-rx-4} {y-ry-4} H{x+rx+4} V{ly+3} Q{x} {ly-4} {x-rx-4} {ly-2} Z',MASK,w=0))
            p.append(path(f'M{x-rx-3} {ly-2} Q{x} {ly-5} {x+rx+3} {ly+3}',w=4.5))
        p.append('</g>')
        p.append(ellipse(x,y,rx,ry,'none','none' if shut else INK,4.6,extra=f'id="{uid}-eye-outline-{side}"'))
        if shut:
            p.append(path(f'M{x-rx+2.} {y+3.} Q{x} {y-13.} {x+rx-2.} {y+3.}',w=4.6,
                          extra=f'id="{uid}-eye-shut-{side}"'))
        by=-90.-f['brow_raise_'+side]
        p.append(path(f'M{x-36} {by+f["brow_"+side+"0"]} Q{x} {by+f["brow_"+side+"q"]} {x+35} {by+f["brow_"+side+"1"]}',w=7.8,extra=f'id="{uid}-brow-{side}"'))
    p.append(path('M3 59 Q22 49 42 58 Q46 62 37 73 Q25 87 13 76 Q0 65 3 59 Z',INK,w=3))
    p.append(path('M23 79 V91',w=4))
    width=f['mouth_width'];skew=f['mouth_skew'];op=f['mouth_open']
    left,right=23.-width/2.,23.+width/2.
    if state.get('mouth_shape')=='breath':
        # Smooth small exhale/yawn: an unvoiced rounded opening, without teeth.
        p.append(ellipse(23.,99.+op*16.,width/2.,max(.8,op*28.),INK,INK,4.,extra=f'id="{uid}-mouth"'))
    elif state.get('mouth_shape')=='o':
        # Discovery precedes possession: an O has no smiling teeth or tongue.
        vocal_scale=float(state.get('mouth_o_scale',1.))
        p.append(ellipse(23.,111.,17.*vocal_scale,22.*vocal_scale,INK,INK,4.,extra=f'id="{uid}-mouth"'))
    elif op>.06:
        h=op*46.
        mouth=(f'M{left} {94.-skew*3.} Q23 {99.+f["mouth_smile"]*4.} {right} {92.+skew*3.} '
               f'C{right-2.} {106.+h} {left+6.} {117.+h} {left} {94.-skew*3.} Z')
        p.append(path(mouth,INK,w=4,extra=f'id="{uid}-mouth"'))
        if op>.2:
            clip=f'{uid}-mouth-clip'
            p.append(f'<defs><clipPath id="{clip}"><path d="{mouth}"/></clipPath></defs>')
            p.append(f'<g clip-path="url(#{clip})">')
            p.append(path(f'M{left+9.} 97 Q23 105 {right-9.} 97 L{right-12.} 107 Q23 114 {left+12.} 107 Z',WHITE,w=0))
            if op>.45:
                p.append(path(f'M{left+15.} 128 Q23 115 {right-12.} 126 L{right-10.} 149 H{left+15.} Z','#E58F86',w=0))
            p.append('</g>')
    else:
        p.append(path(f'M{left} {96.-skew*5.} Q23 {96.+f["mouth_smile"]*30.} {right} {94.+skew*5.}',w=5.1,extra=f'id="{uid}-mouth"'))
    if f['blush']>.01:
        p.extend([ellipse(-100.,71.,21.,9.,'#E89C8C',extra=f'opacity="{n(f["blush"])}"'),ellipse(112.,69.,21.,9.,'#E89C8C',extra=f'opacity="{n(f["blush"])}"')])
    glow=clamp(state.get('screen_glow',0.),0.,1.)
    if glow>.001:
        # The light belongs to the screen facing PATCH. It stays on his muzzle.
        gid=f'{uid}-screen-muzzle-light'
        p.append(f'<defs><radialGradient id="{gid}" cx="50%" cy="90%" r="65%">'
                 '<stop offset="0" stop-color="#FFF9DD" stop-opacity=".66"/>'
                 '<stop offset="1" stop-color="#FFF9DD" stop-opacity="0"/></radialGradient></defs>')
        p.append(ellipse(19.,86.,106.,39.,f'url(#{gid})',extra=f'opacity="{n(glow)}"'))
    p.append(path('M-120 77 L-139 73 M134 73 L151 67',w=3.5))
    angle=-4.+float(state.get('head_tilt',0.))
    hx,hy=state.get('head_shift',(0.,0.));head_scale=1.08*float(state.get('head_scale',1.))
    return f'<g id="{uid}-head" transform="translate({n(337.+hx)} {n(372.+hy)}) rotate({n(angle)}) scale({n(head_scale)})">'+''.join(p)+'</g>'


def _arm(side,state,uid):
    hand=_hand(side,state);hx,hy=to_local((hand['x'],hand['y']),state);sx,sy=SHOULDERS[side]
    dx,dy=hx-sx,hy-sy;length=max(1.,math.hypot(dx,dy));ux,uy=dx/length,dy/length
    nx,ny=-uy,ux;wx,wy=hx-ux*26.,hy-uy*26.
    if side in state.get('wrists',{}):
        # A lateral button reach wraps around the box. Its wrist tangent
        # follows the palm's approach, rather than the shoulder-to-palm chord.
        wx,wy=to_local(tuple(state['wrists'][side]),state)
        dx,dy=hx-wx,hy-wy;length=max(1.,math.hypot(dx,dy))
        ux,uy=dx/length,dy/length;nx,ny=-uy,ux
    bend=-20. if side=='left' else 20.
    ex,ey=(sx+wx)/2.+bend,(sy+wy)/2.+12.
    if side in state.get('elbows',{}):
        ex,ey=to_local(state['elbows'][side],state)
    pair=lambda x,y:f'{n(x)} {n(y)}'
    if side in state.get('wrists',{}):
        # Follow the whole curved sleeve with local normals. Reusing the
        # wrist normal at the shoulder collapses a sideways reach into a spike.
        reach=math.hypot(wx-sx,wy-sy)
        tangent_len=min(50.,max(10.,reach*.33))
        c2x,c2y=wx-ux*tangent_len,wy-uy*tangent_len
        edge_a=[];edge_b=[]
        for j in range(25):
            q=j/24.;r=1.-q
            x=r*r*r*sx+3*r*r*q*ex+3*r*q*q*c2x+q*q*q*wx
            y=r*r*r*sy+3*r*r*q*ey+3*r*q*q*c2y+q*q*q*wy
            dx=3*r*r*(ex-sx)+6*r*q*(c2x-ex)+3*q*q*(wx-c2x)
            dy=3*r*r*(ey-sy)+6*r*q*(c2y-ey)+3*q*q*(wy-c2y)
            mag=max(1.e-8,math.hypot(dx,dy));nxq,nyq=-dy/mag,dx/mag
            width=23.-4.*q
            edge_a.append((x+nxq*width,y+nyq*width))
            edge_b.append((x-nxq*width,y-nyq*width))
        points=edge_a+list(reversed(edge_b))
        d='M'+pair(*points[0])+''.join(' L'+pair(*p) for p in points[1:])+' Z'
    else:
        d=(f'M{pair(sx+nx*23.,sy+ny*23.)} Q{pair(ex+nx*22.,ey+ny*22.)} {pair(wx+nx*19.,wy+ny*19.)} '
           f'L{pair(wx-nx*19.,wy-ny*19.)} Q{pair(ex-nx*22.,ey-ny*22.)} {pair(sx-nx*23.,sy-ny*23.)} Z')
    angle=math.degrees(math.atan2(uy,ux))
    cuff=f'<g transform="translate({n(wx)} {n(wy)}) rotate({n(angle)})">'+path('M-12 -21 H12 V21 H-12 Z',CORAL_DARK,w=4.7)+'</g>'
    return f'<g id="{uid}-arm-{side}" data-part="attached-sleeve">'+path(d,CORAL,w=6.)+cuff+'</g>'


def _paw(side,state,uid):
    hand=_hand(side,state);hx,hy=to_local((hand['x'],hand['y']),state)
    angle=hand['rotation']-float(state.get('body_tilt',0.))
    flip=-1. if side=='right' else 1.
    # One rounded thumb and one simple finger mass, without changing topology.
    grip=hand['grip'];thumb_y=-5.-12.*grip
    d=(f'M-23 22 C-37 9 -33 -13 -20 -20 C-12 -25 -1 -23 5 -17 '
       f'C8 {n(thumb_y-12.)} 24 {n(thumb_y-11.)} 29 {n(thumb_y)} '
       'C35 8 22 31 7 35 C-8 40 -19 32 -23 22 Z')
    return (f'<g id="{uid}-hand-{side}" data-part="mitten-paw" transform="translate({n(hx)} {n(hy)}) '
            f'rotate({n(angle)}) scale({n(flip)} 1)">'+path(d,FUR,w=5.6)+'</g>')


def character_svg(state,uid='patch',layer='all'):
    """Draw all/body, or separate torso/arms/hands for desk/prop occlusion."""
    if layer not in ('all','body','hands','torso','arms'):raise ValueError('Unknown character layer')
    uid=html.escape(str(uid),quote=True);p=[]
    if layer=='hands':
        transform=' '.join(n(v)for v in matrix(state))
        return (f'<g id="{uid}-character-hands" transform="matrix({transform})">'
                +_paw('left',state,uid)+_paw('right',state,uid)+'</g>')
    if layer=='arms':
        transform=' '.join(n(v)for v in matrix(state))
        return (f'<g id="{uid}-character-arms" transform="matrix({transform})">'
                +_arm('left',state,uid)+_arm('right',state,uid)+'</g>')
    # The root continues behind the hoodie instead of leaving a floating gap.
    tail='M425 713 C550 763 664 711 658 596 C656 547 638 514 611 515 C576 517 577 553 591 582 C613 632 575 684 438 654 Z'
    p.append(f'<defs><clipPath id="{uid}-tail-clip">'+path(tail,w=0)+'</clipPath></defs>')
    p.append(f'<g id="{uid}-tail" transform="rotate({n(state.get("tail_angle",0.))} 459 689)">')
    p.append(path(tail,LIGHT,w=7))
    p.append(f'<g clip-path="url(#{uid}-tail-clip)">')
    for d in ('M503 651 L548 666 L550 752 L505 744 Z','M589 611 L661 600 L668 647 L595 661 Z','M576 535 L642 525 L661 569 L586 582 Z'):
        p.append(path(d,MASK,w=0))
    p.append('</g>'+path(tail,w=7)+'</g>')
    if not state.get('seated',True):
        p.append(_legs(state,uid))
    p.append(path('M250 505 C280 475 395 476 430 513 L444 699 Q424 770 343 773 Q268 771 247 711 Z',CORAL_DARK,w=7))
    p.append(path('M276 535 Q339 565 410 534 L421 719 Q340 750 265 716 Z',CORAL,w=0))
    p.append(path('M264 713 Q341 741 427 711 L424 745 Q344 770 266 743 Z',CORAL_DARK,w=5))
    p.append(path('M290 644 Q340 622 394 644 L393 698 Q342 715 290 698 Z',CORAL_DARK,w=4))
    p.append(path('M294 645 L306 659 M389 645 L376 659',w=3.4))
    p.append(path('M304 540 L298 582 M382 543 L388 581',CREAM,CREAM,5))
    p.append(ellipse(298,585,4,7,CREAM));p.append(ellipse(388,584,4,7,CREAM))
    if state.get('screen_glow',0.)>.001:
        gid=f'{uid}-screen-cloth-light'
        p.append(f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="#FFEAC9" stop-opacity=".3"/>'
                 '<stop offset="1" stop-color="#FFEAC9" stop-opacity="0"/></radialGradient></defs>')
        p.append(ellipse(341.,569.,70.,67.,f'url(#{gid})',extra=f'opacity="{n(clamp(state["screen_glow"],0.,1.))}"'))
    # The sleeves also stay visible over the hoodie when the palms cross it.
    if layer!='torso':p.append(_arm('left',state,uid));p.append(_arm('right',state,uid))
    p.append(_head(state,uid))
    if layer=='all':p.append(_paw('left',state,uid));p.append(_paw('right',state,uid))
    transform=' '.join(n(v)for v in matrix(state))
    group_id=uid+'-character'+('-'+layer if layer in ('body','torso') else '')
    return f'<g id="{group_id}" data-character="patch" transform="matrix({transform})">'+''.join(p)+'</g>'
