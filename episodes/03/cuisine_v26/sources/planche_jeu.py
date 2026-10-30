"""Decode acting samples from the actual final MP4, never from a frame cache."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

EP=Path(__file__).resolve().parents[1]
ROOT=next(p for p in EP.parents if (p/'mou_rig.py').is_file())
SAMPLES=[(1.10,'Cuisine'),(3.17,'Inspection'),(7.20,'Soulagement'),(13.30,'Impatience'),
         (22.20,'Résister'),(25.80,'Fumée vue'),(26.55,'Finir le rituel'),(31.875,'Choc'),
         (32.70,'Repas perdu'),(34.20,'Examiner les mains'),(35.50,'Fausse victoire'),(37.50,'Public')]


def main():
    movie=EP/'MOU_Encore_une_feuille.mp4'
    sheet=Image.new('RGB',(1080,1530),'#FFF8ED');draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'),15)
    records=[]
    for n,(t,label) in enumerate(SAMPLES):
        frame=round(t*24);t=frame/24.
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),
             '-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-'])
        im=Image.open(io.BytesIO(raw)).convert('RGB')
        x,y=(n%4)*270,(n//4)*510
        sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+7,y+483),f'{label} — {t:.2f}s',font=font,fill='#382035')
        records.append({'frame':frame,'time_s':t,'label':label,'decoded_png_sha256':hashlib.sha256(raw).hexdigest()})
        if label=='Fausse victoire':im.save(EP/'controle/affiche_v26.png')
    sheet.save(EP/'controle/planche_jeu_final.png')
    (EP/'controle/planche_jeu_final_provenance.json').write_text(json.dumps({
        'source_video_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'samples':records,
        'method':'FFmpeg frame decoding of final MP4; no cached SVG/PNG source used.'},ensure_ascii=False,indent=2)+'\n')
    print('Final poster and acting sheet decoded from MP4.')


if __name__=='__main__':main()
