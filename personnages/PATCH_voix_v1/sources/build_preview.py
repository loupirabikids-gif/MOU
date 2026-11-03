"""Build a labelled listening reel of the12 generated takes, without audition claims."""
from pathlib import Path
import json,wave,subprocess,html
import numpy as np
import cairosvg
BANK=Path(__file__).resolve().parents[1]
ROOT=BANK.parents[1]
RATE=48000
CARD=1.8
LABELS={'resolve_hm':'Décision · petit « hm »','bored_exhale':'Ennui · soupir','sleepy_yawn':'Somnolence · bâillement','effort_small':'Effort bref','surprise_inhale':'Surprise · inspiration','relief_chuckle':'Joie · deux petits souffles'}
def main():
 bank=json.loads((BANK/'bank.json').read_text());work=ROOT/'work/voix_soundgen_runtime/preview';work.mkdir(parents=True,exist_ok=True)
 mix=np.zeros(round(len(bank['variants'])*CARD*RATE));cues=[]
 for i,(key,meta) in enumerate(bank['variants'].items()):
  id=key.rsplit('_',1)[0]
  with wave.open(str(BANK/meta['file'])) as w:audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
  at=i*CARD+.4;n=round(at*RATE);mix[n:n+len(audio)]+=audio
  cues.append({'id':key,'at':at,'duration':len(audio)/RATE,'accent_seconds':at+meta['accent_seconds']})
  title=html.escape(LABELS[id]);sub=f"Prise {meta['variant']} / 2 · {meta['duration']:.2f} s"
  points=' '.join(f'{140+1000*j/299:.2f},{550-85*abs(float(v)):.2f}' for j,v in enumerate(audio[np.linspace(0,len(audio)-1,300).astype(int)]/.2))
  svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720"><rect width="1280" height="720" fill="#fff8ee"/><rect x="80" y="72" width="1120" height="560" rx="32" fill="#f3dfd0" stroke="#5f5654" stroke-width="4"/><text x="140" y="145" font-family="DejaVu Sans" font-size="28" fill="#6b5d60">PATCH · Bibliothèque vocale V1</text><text x="140" y="285" font-family="DejaVu Sans" font-weight="bold" font-size="48" fill="#37323b">{title}</text><text x="140" y="355" font-family="DejaVu Sans" font-size="32" fill="#6b5d60">{sub}</text><text x="140" y="415" font-family="DejaVu Sans" font-size="24" fill="#6b5d60">Soundgen · sans mots · synthèse originale</text><polyline points="{points}" fill="none" stroke="#c86650" stroke-width="3"/><text x="140" y="602" font-family="DejaVu Sans" font-size="22" fill="#6b5d60">Prises à écouter et comparer · naturel non évalué à l’oreille ici</text></svg>'''
  png=work/f'{i+1:02d}.png';cairosvg.svg2png(bytestring=svg.encode(),write_to=str(png))
 pcm=np.rint(mix*32767).astype('<i2');wav=BANK/'PATCH_Voix_V1_ecoute.wav'
 with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
 # One card repeated for its1.8s segment; lossless source images stay private.
 concat=work/'cards.txt';lines=[]
 for i in range(len(cues)):lines.extend(["file '"+str(work/f'{i+1:02d}.png')+"'",'duration '+str(CARD)])
 lines.append("file '"+str(work/f'{len(cues):02d}.png')+"'");concat.write_text('\n'.join(lines)+'\n')
 target=BANK/'PATCH_Voix_V1_ecoute.mp4'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-r','24','-c:v','libx264','-preset','medium','-crf','20','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',str(len(cues)*CARD),'-movflags','+faststart',str(target)],check=True)
 (BANK/'controle/planche_ecoute.json').write_text(json.dumps({'duration':len(cues)*CARD,'cues':cues,'listening_performed':False},indent=2,ensure_ascii=False)+'\n')
 print(target)
if __name__=='__main__':main()
