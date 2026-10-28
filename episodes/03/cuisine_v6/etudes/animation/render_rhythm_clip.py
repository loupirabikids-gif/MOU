"""A short actual encoded study of cooking sway and the original whistle."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,tempfile
import cairosvg

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').exists())
OUT=Path(__file__).resolve().parent
EP=OUT.parents[1]
sp=importlib.util.spec_from_file_location('v6_rhythm_clip',EP/'sources/render.py')
r=importlib.util.module_from_spec(sp);sp.loader.exec_module(r)
fps,count=24,54
paths=[EP/'sources'/n for n in ('animation.py','art.py','render.py','son.py')]+[EP/'chronologie.json',EP/'audio/mix.wav']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):digest(p) for p in paths}
with tempfile.TemporaryDirectory(prefix='mou-v6-rythme-',dir='/tmp') as temporary:
    frames=Path(temporary)
    for index in range(count):
        cairosvg.svg2png(bytestring=r.svg_at(index/fps).encode(),output_width=540,output_height=960,
                        write_to=str(frames/f'{index:04d}.png'))
    dest=OUT/'MOU_jeu_siffle_v6.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(fps),'-i',str(frames/'%04d.png'),
                    '-i',str(EP/'audio/mix.wav'),'-map','0:v:0','-map','1:a:0',
                    '-frames:v',str(count),'-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','160k','-t',str(count/fps),'-movflags','+faststart',str(dest)],check=True)
silent=OUT/'MOU_jeu_siffle_v6_muette.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-i',str(dest),'-map','0:v:0','-c:v','copy','-an',
                '-movflags','+faststart',str(silent)],check=True)
assert before=={str(p):digest(p) for p in paths}
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dest)]))
video=next(x for x in probe['streams'] if x['codec_type']=='video')
assert int(video['nb_frames'])==54 and [video['width'],video['height']]==[540,960]
checks={'duration':count/fps,'fps':fps,'frames':count,'dimensions':[540,960],
        'scene_time':[0.,count/fps],'sound_file':dest.name,'silent_file':silent.name,
        'clips_sha256':{p.name:digest(p) for p in (dest,silent)},
        'sources_sha256':before,
        'limits':'A complete encoded short acting study; no claim of human listening or a public comprehension test.'}
(OUT/'clip_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,ensure_ascii=False))
