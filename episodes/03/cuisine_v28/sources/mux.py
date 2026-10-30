"""Attach the preserved soundtrack to the corrected V28 silent export."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import wave

EP=Path(__file__).resolve().parents[1]
AUDIO_SHA='16294d1642cd220b6eb0cf3c7c8ffa32db70db5105f692e766a4fe62601aff0b'


def main():
    silent=EP/'MOU_Encore_une_feuille_muette.mp4'
    audio=EP/'audio/mix.wav'
    assert hashlib.sha256(audio.read_bytes()).hexdigest()==AUDIO_SHA,'Preserved soundtrack changed'
    silent_sha=hashlib.sha256(silent.read_bytes()).hexdigest()
    with wave.open(str(audio),'rb') as src:
        assert (src.getframerate(),src.getnchannels(),src.getsampwidth(),src.getnframes())==(48000,2,2,1824000)
    final=EP/'MOU_Encore_une_feuille.mp4';temporary=final.with_name('.'+final.name)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(silent),'-i',str(audio),
        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
        '-t','38','-movflags','+faststart',str(temporary)],check=True)
    os.replace(temporary,final)
    preview_mute=EP/'MOU_test_mise_en_scene_muette.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-ss','30','-i',str(silent),'-t','8',
        '-frames:v','192','-c:v','libx264','-threads','3','-preset','medium','-crf','8',
        '-pix_fmt','yuv420p','-an','-movflags','+faststart',str(preview_mute)],check=True)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(preview_mute),
        '-i',str(EP/'audio/test_fin_v27.wav'),'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','160k','-t','8','-movflags','+faststart',
        str(EP/'MOU_test_mise_en_scene.mp4')],check=True)
    print(json.dumps({'film':str(final),'duration_s':38,'video_mode':'stream copy',
        'silent_reference_sha256':silent_sha,'preview_interval_s':[30,38]}))


if __name__=='__main__':main()
