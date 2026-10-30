"""Crop eight facial moments from the actual encoded movie, for review."""
from pathlib import Path
import importlib.util,subprocess,sys,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if(p/'mou_rig.py').is_file())
spec=importlib.util.spec_from_file_location('poster_v23',EP/'sources/render.py')
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
items=[(3.5,'Cuisine'),(7.375,'Inspection'),(12.25,'Main essuyée'),(31.4,'Rituel répété'),(36.55,'Petite feuille'),(37.33,'Constat'),(43.2083,'Tablier'),(47.75,'Dernier regard')]
frames=[round(t*24) for t,_ in items]
flt='select='+'+'.join('eq(n\\,%d)'%i for i in frames)
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(EP/'MOU_Encore_une_feuille_muette.mp4'),'-vf',flt,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
ims=np.frombuffer(raw,np.uint8).reshape(len(frames),1920,1080,3)
board=Image.new('RGB',(1080,850),'#FFF8ED');d=ImageDraw.Draw(board)
bold=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),20);small=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans.ttf'),16)
d.text((20,16),'MOU — expressions intégrées dans le film V23',font=bold,fill='#2B0A24');manifest=[]
for j,(pixels,n,(_,label)) in enumerate(zip(ims,frames,items)):
 t=n/24;s=r.animation.scene_state(t);ax,ay,scale=s['actor_transform'];vx,vy,vw,vh=r.camera_at(t,s)
 x0,y0=ax+115*scale,ay+75*scale;x1,y1=ax+295*scale,ay+355*scale
 box=(max(0,math.floor((x0-vx)*1080/vw)),max(0,math.floor((y0-vy)*1920/vh)),min(1080,math.ceil((x1-vx)*1080/vw)),min(1920,math.ceil((y1-vy)*1920/vh)))
 assert box[2]-box[0]>100 and box[3]-box[1]>100,(t,'Face not sufficiently in view')
 im=Image.fromarray(pixels).crop(box);im.thumbnail((248,325),Image.Resampling.LANCZOS)
 x=j%4*270;y=58+j//4*390;board.paste(im,(x+(270-im.width)//2,y+(325-im.height)//2))
 d.text((x+12,y+331),label,font=bold,fill='#2B0A24');d.text((x+12,y+358),f'{t:.3f} s',font=small,fill='#73516B')
 manifest.append({'frame':n,'time':t,'label':label,'crop_from_encoded_frame':box,'expression':s.get('expression')})
board.save(EP/'controle/planche_jeu_final.png')
(EP/'controle/planche_jeu_provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Eight encoded facial moments exported')
