"""Assemble the three actual HD Blender renders, retaining individual PNGs."""
from pathlib import Path
import shutil
from PIL import Image,ImageDraw,ImageFont

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
poses = [(12,'Assurance'),(54,'Résistance'),(99,'Il cède')]
out = Image.new('RGB',(1620,1032),'#fff9f0')
draw = ImageDraw.Draw(out)
font = ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),25)
(EP/'poses').mkdir(exist_ok=True)
for column,(frame,label) in enumerate(poses):
    source = EP/f'work/hd/{frame:04d}.png'
    im = Image.open(source).convert('RGB')
    assert im.size == (1080,1920)
    shutil.copyfile(source,EP/f'poses/{frame:03d}.png')
    out.paste(im.resize((540,960),Image.Resampling.LANCZOS),(column*540,0))
    draw.text((column*540+24,978),f'{frame:03d} — {label}',font=font,fill='#34202e')
out.save(EP/'MOU_Blender_trois_poses.png')
print('Exported 3 HD Blender poses and their contact sheet')
