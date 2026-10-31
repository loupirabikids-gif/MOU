"""Expose the delivered mix's existing layers on the same short video.

Diagnostic only: no new effects, gains, filters, normalization or animation.
The original movie and audio inputs are read without modification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import wave

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'episodes/03/galet_cuisine_v1').is_dir())
EP=ROOT/'episodes/03/galet_cuisine_v1'
SECONDS=8.75
FPS=24
SR=48000


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path),'rb')as f:
        assert(f.getframerate(),f.getnchannels(),f.getsampwidth())==(SR,2,2)
        return np.frombuffer(f.readframes(round(SECONDS*SR)),'<i2').reshape(-1,2).astype(np.int64)


def write(path,data):
    assert np.abs(data).max()<32767
    with wave.open(str(path),'wb')as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes(data.astype('<i2').tobytes())


def command(*args):return subprocess.check_output(list(args))


def frame_hashes(path):
    raw=command('ffmpeg','-v','error','-threads','2','-i',str(path),
                '-frames:v',str(round(SECONDS*FPS)),'-map','0:v:0','-f','framemd5','-').decode()
    return [line.rsplit(',',1)[1].strip()for line in raw.splitlines()if line and not line.startswith('#')]


def main():
    HERE.mkdir(parents=True,exist_ok=True);private=ROOT/'work/galet_diagnostic_v1';private.mkdir(parents=True,exist_ok=True)
    source=EP/'Galet_Cuisine_muette.mp4'
    paths=[source,EP/'Galet_Cuisine.mp4',EP/'audio/mix.wav']+list((EP/'audio/stems').glob('*.wav'))
    frozen={str(p.relative_to(ROOT)):digest(p)for p in paths}
    common=private/'images_communes.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-t',str(SECONDS),
                    '-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(common)],check=True)
    reference_hashes=frame_hashes(source);assert frame_hashes(common)==reference_hashes,'Trim changed decoded picture'
    mix=pcm(EP/'audio/mix.wav');music=pcm(EP/'audio/stems/music.wav')
    foley=pcm(EP/'audio/stems/foley.wav')+pcm(EP/'audio/stems/ambience.wav')
    assert np.array_equal(mix,music+foley)
    report={'purpose':'Listening diagnosis, no revised full mix or new visual performance.',
            'source_episode':'12f3a14613a798623be182d7c2f47d7a7e6e3596',
            'start_episode_seconds':0.,'duration_requested_seconds':SECONDS,
            'unchanged_source_sha256':frozen,'normalization':False,'gain_changes':False,
            'first210_decoded_frames_identical_to_delivered_movie':True,'variants':[]}
    for name,label,data in (('A_mix_actuel','Mix livré',mix),('B_jazz_seul','Jazz seul, au même niveau',music),
                            ('C_bruitages_seuls','Bruitages et ambiance seuls, aux mêmes niveaux',foley)):
        wav=private/(name+'.wav');write(wav,data);output=HERE/(name+'.mp4')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(common),'-i',str(wav),
                        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
                        '-t',str(SECONDS),'-movflags','+faststart',str(output)],check=True)
        assert frame_hashes(output)==reference_hashes,'Comparison changes the picture'
        elementary=command('ffmpeg','-v','error','-i',str(output),'-map','0:v:0','-c:v','copy','-f','h264','-')
        probe=json.loads(command('ffprobe','-v','error','-show_format','-show_streams','-of','json',str(output)))
        report['variants'].append({'file':output.name,'label':label,'sha256':digest(output),
                                   'bytes':output.stat().st_size,'h264_sha256':hashlib.sha256(elementary).hexdigest(),
                                   'duration_container_seconds':float(probe['format']['duration']),
                                   'decoded_first210_images_identical':True})
    assert len({x['h264_sha256']for x in report['variants']})==1
    assert frozen=={str(p.relative_to(ROOT)):digest(p)for p in paths}
    report['limits']='No listening or timbre assessment by the model; these are isolated layers, not artistic fixes.'
    (HERE/'CONTROLE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'variants':report['variants'],'delivered_sources_preserved':True},ensure_ascii=False))


if __name__=='__main__':main()
