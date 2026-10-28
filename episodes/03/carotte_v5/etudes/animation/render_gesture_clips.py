from pathlib import Path
import importlib.util,tempfile,subprocess,math,json,hashlib
import cairosvg
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').exists())
OUT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v5_gesture_review',ROOT/'episodes/03/carotte_v5/sources/render.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
metadata=[]
for label,start,end in [('carotte_raccord',15.,17.8333333333),('petit_essuyage',25.8,27.4)]:
    fps=12;count=round((end-start)*fps)
    with tempfile.TemporaryDirectory(prefix='mou-v5-geste-',dir='/tmp') as temporary:
        folder=Path(temporary)
        for index in range(count):
            svg=m.svg_at(start+index/fps)
            cairosvg.svg2png(bytestring=svg.encode(),output_width=540,output_height=960,
                            write_to=str(folder/f'{index:04d}.png'))
        destination=OUT/f'MOU_{label}_v5.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(fps),'-i',str(folder/'%04d.png'),
                        '-frames:v',str(count),'-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p',
                        '-an','-movflags','+faststart',str(destination)],check=True)
    metadata.append({'file':destination.name,'start_scene_time':start,'end_scene_time_exclusive':start+count/fps,
                     'fps':fps,'frames':count,'dimensions':[540,960],'muted':True,
                     'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()})
checks={'clips':metadata,'sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [ROOT/'episodes/03/carotte_v5/sources'/name for name in ['animation.py','art.py','render.py']]},
        'limits':'Gesture studies rendered from current source, not decoded samples of the full final movie.'}
(OUT/'clip_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(metadata,ensure_ascii=False))
