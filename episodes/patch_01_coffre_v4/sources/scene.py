"""Distinct drawn viewpoints, truthful prop contacts and PATCH's physical acting."""
from __future__ import annotations
from copy import deepcopy
import json
import math
from pathlib import Path
import scene_base as base
from personnage import character_svg
from jeu import phone_binding
from vues import scene_layers,clock_placement

EP=Path(__file__).resolve().parents[1]
TIMELINE=base.TIMELINE
FPS=base.FPS;DURATION=base.DURATION
LAYOUTS=json.loads(Path(__file__).with_name('cadres.json').read_text())


def view_at(t):
    for item in TIMELINE['views']:
        if item['at'][0]<=t<item['at'][1]:return item['view']
    return 'phone_final'


def mapped_actor(actor,layout):
    a=deepcopy(actor);s=layout['scale'];tx=layout['tx'];ty=layout['ty']
    a['cx']=actor['cx']*s+tx;a['floor_y']=actor['floor_y']*s+ty
    a['scale']=actor.get('scale',1.)*s
    a['lean']=tuple(v*s for v in actor.get('lean',(0.,0.)))
    for side,h in a['hands'].items():
        h['x']=actor['hands'][side]['x']*s+tx;h['y']=actor['hands'][side]['y']*s+ty
    if 'elbows' in a:a['elbows']={side:(x*s+tx,y*s+ty)for side,(x,y)in actor['elbows'].items()}
    if layout.get('box_shift_y'):
        a['hands']['right']['y']+=layout['box_shift_y']
    return a


def state_at(t):
    s=base.state_at(t);t=s['t'];a=s['actor'];view=view_at(t);layout=LAYOUTS[view]
    # The clock insert precedes the first visible look, rather than hiding it.
    if 7.<=t<8.:
        p=t-7.;look=base.ref.ease(p,.02,.17)*(1.-base.ref.ease(p,.48,.80))
        a.pop('pose',None);a.pop('face',None)
        a['pose_weights']={'concentre':1.-look,'curieux':look}
        a['gaze']=(base.ref.lerp(-.25,1.,look),1.)
        a['head_tilt']=3.*look
        a['hands']['left']['y']=base.ref.lerp(1312.,1332.,base.ref.ease(p,.72,.97))
        a['performance_state']='visible_first_return'
    if view=='face_box':a['mouth_shape']='o'
    s['view']=view;s['shot']='V4_'+view;s['camera']=(0.,0.,1080.,1920.)
    s['layout']=layout;s['actor_screen']=mapped_actor(a,layout)
    if t>=24.7 and s['phone']['owner']=='right':
        b=phone_binding(t,a);s['phone_binding']=b
        s['phone']['center']=tuple(b['center']);s['phone']['angle']=b['angle']
        s['phone']['face']=b['face'];s['phone']['bilateral']=b['bilateral']
    else:
        s['phone']['face']='screen';s['phone']['bilateral']=False
    return s


def transform(layout,box=False):
    s=layout['scale'];dy=layout['ty']+(layout.get('box_shift_y',0.)if box else 0.)
    dx=layout['tx']+(layout.get('box_shift_x',0.)if box else 0.)
    return f'translate({dx} {dy}) scale({s})'


def wrap(svg,layout,box=False):return '<g transform="'+transform(layout,box)+'">'+svg+'</g>'


def draw_clock(cx,cy,r,elapsed):
    hour=math.radians(180.+elapsed/120.);minute=math.radians(-90.+elapsed/10.)
    out=[f'<g id="wall-clock" data-elapsed-seconds="{elapsed:.6f}">',
         f'<ellipse cx="{cx+9}" cy="{cy+11}" rx="{r}" ry="{r}" fill="#78666B" opacity=".18"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FAF4E8" stroke="#51464D" stroke-width="{max(5.,r*.035)}"/>']
    for i in range(12):
        theta=math.radians(i*30.-90.)
        points=[(cx+math.cos(theta)*r*k,cy+math.sin(theta)*r*k)for k in(.81,.91)]
        out.append(f'<path d="M{points[0][0]} {points[0][1]} L{points[1][0]} {points[1][1]}" stroke="#71686E" stroke-width="{max(3.,r*.025)}"/>')
    for angle,length,width,color in [(hour,.51,.067,'#403C48'),(minute,.76,.042,'#D36A5B')]:
        out.append(f'<path d="M{cx} {cy} L{cx+r*length*math.cos(angle)} {cy+r*length*math.sin(angle)}" stroke="{color}" stroke-width="{max(4.,r*width)}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{max(6.,r*.055)}" fill="#403C48"/></g>')
    return ''.join(out)


def box_parts(s):
    """One actual volume: a recessed opening, visible side and hinged lid."""
    lid=s['lid'];line=base.ref.path
    back=(line('M662 1205 L700 1295 V1465 L662 1375 Z','#70978F',width=4.)+
          line('M662 1205 H952 L990 1295 H700 Z','#8CB2A5',width=5.)+
          line('M676 1217 H943 L974 1282 H710 Z','#354D4E',width=3.))
    fx=700.-20.*lid;fy=1295.-295.*lid
    lid_svg=(f'<g id="lid" data-open="{lid:.6f}">'+
             line(f'M662 1205 H952 L{fx+290:.5f} {fy:.5f} H{fx:.5f} Z','#85A99C',width=5.)+
             f'<path d="M{fx+13} {fy+5} H{fx+276}" stroke="#D3E2CA" stroke-width="5"/>'+
             f'<path d="M{fx+121} {fy+7} H{fx+158}" stroke="#3A5150" stroke-width="7" stroke-linecap="round"/></g>')
    front=['<g id="box-front" data-volume="perspective-v4">',
           '<rect x="700" y="1295" width="290" height="170" rx="11" fill="#A2BFB0" stroke="#3C3441" stroke-width="5"/>',
           '<path d="M709 1304 V1451 H981" fill="none" stroke="#D0DBBF" stroke-width="3" opacity=".7"/>',
           '<rect x="754" y="1335" width="200" height="86" rx="12" fill="#344149" stroke="#3C3441" stroke-width="4"/>',
           f'<g id="timer" data-display="{s["display"]}" data-remaining="{s["remaining"]}">']
    for ch,x in zip(s['display'].replace(':',''),(770,805,867,902)):front.append(base.ref.digit_svg(ch,x,1352))
    front.append('<circle cx="851" cy="1368" r="3.2" fill="#F9F2DF"/><circle cx="851" cy="1389" r="3.2" fill="#F9F2DF"/></g>')
    shackle='M0 10 V1 Q12 -17 24 1 V10'if s['locked']else'M0 10 V1 Q12 -17 24 1'
    front.append(f'<g id="lock" data-locked="{int(s["locked"])}" transform="translate(720 1332)">'+line(shackle,'none',width=4.)+
                 '<rect x="-4" y="8" width="32" height="27" rx="4" fill="'+('#D5A656'if s['locked']else'#D9EEE1')+'" stroke="#3C3441" stroke-width="3"/></g>')
    front.append(f'<ellipse id="start-button" cx="731" cy="1417" rx="16" ry="{9 if 3.84<=s["t"]<4.02 else 12}" fill="#FFF0D6" stroke="#3C3441" stroke-width="3"/>')
    front.extend([base.text_svg('30 MIN',818,1303,18,'box-duration'),base.text_svg('MIN:SEC',817,1432,14,'box-units'),'</g>'])
    return back,''.join(front),lid_svg,lid>.306


def phone_svg(s):
    p=s['phone']
    if not p['visible']:return ''
    x,y=p['center'];face=p['face'];angle=p['angle'];layout=s['layout']
    # During the close recovery the box and reaching paw occupy a nearer plane.
    shift=layout.get('box_shift_y',0.)if p['owner']in('box','right')else 0.
    attrs=f'data-owner="{p["owner"]}" data-face="{face}" data-bilateral="{int(p["bilateral"])}"'
    shape=['<rect x="-39" y="-70" width="78" height="140" rx="12" fill="#494854" stroke="#302D35" stroke-width="5"/>']
    if face=='back':
        shape.extend(['<rect x="-31" y="-61" width="44" height="46" rx="10" fill="#666772" stroke="#302D35" stroke-width="2.5"/>',
                      '<circle cx="-18" cy="-48" r="10" fill="#212632" stroke="#B3B3B5" stroke-width="2.5"/>',
                      '<circle cx="-1" cy="-30" r="9" fill="#212632" stroke="#B3B3B5" stroke-width="2.5"/>',
                      '<circle cx="1" cy="-49" r="3.3" fill="#F9E7BD"/>',
                      '<path d="M-28 -4 V53 Q-28 60 -20 60 H23" fill="none" stroke="#737682" stroke-width="2"/>'])
    else:
        color='#F7BA9B'if s['t']>=.65 else'#ADB9CA'
        shape.append(f'<rect x="-31" y="-58" width="62" height="114" rx="7" fill="{color}"/>')
        shape.append('<path d="M-20 -29 H20 M-20 -7 H12 M-20 15 H19" stroke="#FFF5EA" stroke-width="9" stroke-linecap="round"/>')
        if s['t']>=.65:shape.append('<circle cx="23" cy="-47" r="10" fill="#E85F61" stroke="#FFF4E3" stroke-width="2"/>')
    local=f'<g id="phone" {attrs} transform="translate({x:.5f} {y:.5f}) rotate({angle:.5f})">'+''.join(shape)+'</g>'
    # Prop and right palm receive the same offset in this view.
    if shift:local='<g transform="translate(0 '+str(shift/layout['scale'])+')">'+local+'</g>'
    return wrap(local,layout)


def paper_svg(s):
    paper=base.paper_svg()
    if s['view']=='wide_high':
        # Tilt the paper in the actual diagonal tabletop, keeping the pencil's
        # contact near(458,1390) fixed rather than slipping it off the sheet.
        paper='<g transform="translate(458 1390) matrix(1 -.22 .20 1 0 0) translate(-458 -1390)">'+paper+'</g>'
    return wrap(paper,s['layout'])


def svg_at(t):
    s=state_at(t);a=s['actor_screen'];view=s['view'];layout=s['layout']
    layers=scene_layers(view,s['story_elapsed_seconds'],s['t'])
    if view=='paper':
        body=layers['background']+base.paper_svg(True)
        body+='<path d="M915 660 L933 659 L961 1320 L951 1360 L939 1320 Z" fill="#D7AD55" stroke="#4C3A38" stroke-width="4"/>'
    elif view=='clock':
        body=layers['background']+draw_clock(*clock_placement(view),s['story_elapsed_seconds'])
        total=9*3600+s['story_elapsed_seconds'];label=f'{int(total//3600):02d}:{int(total%3600//60):02d}'
        body+=base.text_svg(label,410,1190,76,'clock-readable-time')
    else:
        clock=''if view=='work_close'else draw_clock(*clock_placement(view),s['story_elapsed_seconds'])
        body=layers['background']+clock+layers['chair']
        show_actor=view!='box_insert'
        back,front,lid,lid_behind=box_parts(s)
        # In the close reveal PATCH leans ahead of the raised lid. The open
        # panel belongs behind his face, so it cannot erase the second eye.
        lid_before_actor=view=='face_box' and lid_behind
        if lid_before_actor:body+=wrap(lid,layout,True)
        if show_actor:body+=character_svg(a,'patch',layer='torso')
        body+=layers['tabletop']+layers['front']+paper_svg(s)
        body+=wrap(back,layout,True)
        if lid_behind and not lid_before_actor:body+=wrap(lid,layout,True)
        if s['phone_deep']:body+=phone_svg(s)
        # Sleeves can cross the hoodie and rest over the surface, behind the box.
        if show_actor:body+=character_svg(a,'patch',layer='arms')
        body+=wrap(front,layout,True)
        if not lid_behind:body+=wrap(lid,layout,True)
        if not s['phone_deep']:body+=phone_svg(s)
        body+=wrap(base.ref.pencil_svg(s),layout)
        if show_actor:body+=character_svg(a,'patch',layer='hands')
    body+=base.caption_svg(s)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920" '
            f'data-view="{view}" data-shot="{s["shot"]}" data-story-seconds="{s["story_elapsed_seconds"]:.6f}">'+body+'</svg>')
