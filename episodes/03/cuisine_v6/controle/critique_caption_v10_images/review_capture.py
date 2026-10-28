"""Decode a compact, indexed sample from a real caption MP4 for review."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=Path)
    parser.add_argument('tag')
    args = parser.parse_args()
    root = next(p for p in Path(__file__).resolve().parents if (p/'mou_rig.py').is_file())
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                             '-show_format', '-of', 'json', str(args.video)]))
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    fps = Fraction(stream['avg_frame_rate'])
    end = round(3*fps)
    indices = sorted({0, round(float(fps)*5/12), round(float(fps)*1.5),
                      round(float(fps)*2.75), end-1, end, end+1})
    destination = Path(__file__).resolve().parent/args.tag
    destination.mkdir(exist_ok=True)
    sheet = Image.new('RGB', (1080, 1010), '#FFF4E5')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(root/'fonts/DejaVuSans-Bold.ttf'), 15)
    evidence = []
    keep = {round(float(fps)*5/12), end}
    with tempfile.TemporaryDirectory(prefix='mou-caption-review-', dir='/tmp') as tmp:
        for column, index in enumerate(indices):
            capture = Path(tmp)/f'{index:05d}.png'
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(args.video),
                            '-vf', f'select=eq(n\\,{index})', '-frames:v', '1',
                            '-update', '1', str(capture)], check=True)
            raw = capture.read_bytes()
            native = Image.open(capture).convert('RGB')
            if index in keep:
                (destination/capture.name).write_bytes(raw)
            native.thumbnail((270, 480), Image.Resampling.LANCZOS)
            x, y = column % 4*270, column // 4*505
            sheet.paste(native, (x, y))
            seconds = float(Fraction(index, 1)/fps)
            draw.text((x+6, y+483), f'{seconds:.3f} s / {index}', font=font, fill='#382035')
            evidence.append({'frame':index, 'time_seconds':seconds,
                             'png_sha256':hashlib.sha256(raw).hexdigest(),
                             'native_png_preserved':index in keep})
    sheet.save(destination/'planche.png')
    report = {'video':str(args.video), 'sha256':hashlib.sha256(args.video.read_bytes()).hexdigest(),
              'dimensions':[stream['width'], stream['height']], 'fps':str(fps),
              'duration_seconds':float(probe['format']['duration']), 'samples':evidence,
              'method':'Direct indexed ffmpeg decoding of the named MP4; no SVG or render cache.'}
    (destination/'preuves.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'destination':str(destination), 'sha256':report['sha256'],
                      'samples':len(indices)}))


if __name__ == '__main__':
    main()
