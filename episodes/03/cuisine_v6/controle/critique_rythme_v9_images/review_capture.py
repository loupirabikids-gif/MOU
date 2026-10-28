"""Decode actual MP4 review samples; retain contact sheets and key native frames."""
from pathlib import Path
from fractions import Fraction
import hashlib
import io
import json
import math
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'mou_rig.py').is_file())
TIMES = (.417, .75, 1.7, 2.6, 3.25, 3.292, 3.333, 3.375, 3.417, 3.6, 5.6,
         6.5, 6.583, 6.625, 6.667, 6.95, 7.083, 7.25, 7.5, 7.667, 7.75,
         8.083, 13.5, 15., 20., 21.083, 21.75, 23., 27., 28.,
         31.5, 33.333, 34.583)
NATIVE_TIMES = (3.6, 6.583, 7.25, 31.5)


def main():
    video = Path(sys.argv[1]).resolve()
    tag = sys.argv[2]
    destination = HERE/tag
    destination.mkdir(parents=True, exist_ok=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
        '-show_streams', '-show_format', '-of', 'json', str(video)]))
    stream = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    fps = float(Fraction(stream['r_frame_rate']))
    duration = float(probe['format']['duration'])
    assert abs(duration-35.) < .05, duration
    indices = sorted({round(t*fps) for t in TIMES})
    native = {round(t*fps) for t in NATIVE_TIMES}
    font = ImageFont.truetype(str(ROOT/'fonts/DejaVuSans-Bold.ttf'), 16)
    decoded = []
    samples = []
    for index in indices:
        actual = index/fps
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss',
            f'{actual:.9f}', '-i', str(video), '-frames:v', '1',
            '-f', 'image2pipe', '-vcodec', 'png', '-'])
        frame = Image.open(io.BytesIO(raw)).convert('RGB')
        assert frame.size == (int(stream['width']), int(stream['height']))
        thumb = frame.copy()
        thumb.thumbnail((270, 480), Image.Resampling.LANCZOS)
        decoded.append((index, actual, thumb))
        record = {'frame': index, 'seconds': actual,
                  'decoded_png_sha256': hashlib.sha256(raw).hexdigest()}
        if index in native:
            name = f'{index:05d}.png'
            (destination/name).write_bytes(raw)
            record['native_png'] = name
        samples.append(record)
    pages = []
    for page_index in range(math.ceil(len(decoded)/12)):
        part = decoded[page_index*12:(page_index+1)*12]
        sheet = Image.new('RGB', (1080, math.ceil(len(part)/4)*505), '#FFF4E5')
        draw = ImageDraw.Draw(sheet)
        for j, (index, actual, thumb) in enumerate(part):
            x, y = j%4*270, j//4*505
            sheet.paste(thumb, (x, y))
            draw.text((x+4, y+482), f'{actual:.3f} s / {index}',
                      fill='#382035', font=font)
        name = f'planche_{page_index+1}.png'
        sheet.save(destination/name)
        pages.append(name)
    proof = {'video': video.name,
             'video_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
             'duration_seconds': duration, 'fps': fps,
             'dimensions': [int(stream['width']), int(stream['height'])],
             'method': 'Direct FFmpeg decoding of actual MP4; no SVG or PNG cache. All sampled images retained in contact sheets; selected full-resolution images retained separately.',
             'pages': pages, 'samples': samples,
             'limits': 'Images must still be opened and examined. No listening, continuous playback or public comprehension measurement claimed.'}
    (destination/'preuves.json').write_text(json.dumps(proof, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'sha256': proof['video_sha256'], 'frames': len(samples),
                      'pages': pages, 'native_frames': sorted(native)}))


if __name__ == '__main__':
    main()
