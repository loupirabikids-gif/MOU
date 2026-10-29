"""Check source ZIP integrity and reproduce selected pictures/audio in isolation.

This checks reproducibility, not acting, comedy or listening comfort. Run after
package.py; audit_archive.json stays outside the ZIP to avoid a circular hash.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
REL_EP = EP.relative_to(ROOT)
EXPECTED_MIX = 'd5e95dc32911c9087c797193ca750d66c82a546ad3355ebe210d6433bc68fc7b'
TIMES = [4., 44.25, 47.916666666666664]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


WORKER = r'''
import hashlib, importlib.util, json, pathlib, sys
import cairosvg
root=pathlib.Path(sys.argv[1]).resolve()
out=pathlib.Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
path=root/'episodes/03/cuisine_v22/sources/render.py'
spec=importlib.util.spec_from_file_location('archive_cold_renderer',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
assert r.ROOT.resolve()==root
modules=[r,r.animation,r.art,r.sink,r.costume,r.animation._stir,sys.modules['mou_rig']]
for m in modules:
 assert pathlib.Path(m.__file__).resolve().is_relative_to(root),(m.__name__,m.__file__)
results=[]
for i,t in enumerate(json.loads(sys.argv[3])):
 data=r.svg_at(t).encode()
 output=out/f'frame_{i}.png'
 cairosvg.svg2png(bytestring=data,output_width=1080,output_height=1920,write_to=str(output))
 results.append({'time_seconds':t,'svg_sha256':hashlib.sha256(data).hexdigest(),
                 'png_sha256':hashlib.sha256(output.read_bytes()).hexdigest()})
print(json.dumps({'modules':{m.__name__:str(pathlib.Path(m.__file__).resolve().relative_to(root)) for m in modules},'frames':results}))
'''


def isolated_env(cache):
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['XDG_CACHE_HOME'] = str(cache)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def pictures(root, output, env):
    done = subprocess.run([sys.executable, '-I', '-B', '-c', WORKER,
                           str(root), str(output), json.dumps(TIMES)],
                          cwd=root, env=env, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return json.loads(done.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path,
                        default=EP/'MOU_Encore_une_feuille_sources.zip')
    args = parser.parse_args()
    archive = args.archive.resolve()
    report = {'status': 'running',
              'observed_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size,
              'limits': 'Archive integrity and isolated reproduction only; no continuous viewing, listening, artistic or audience approval.'}
    audit = EP/'controle/audit_archive.json'
    try:
        work = ROOT/'work/verif_archive_v22';work.mkdir(parents=True, exist_ok=True)
        trial = Path(tempfile.mkdtemp(prefix='cold_', dir=work))
        extracted = trial/'extracted';extracted.mkdir()
        with zipfile.ZipFile(archive) as source:
            names = source.namelist()
            assert len(names) == len(set(names)), 'Duplicate ZIP members'
            assert source.testzip() is None, 'ZIP CRC failure'
            for name in names:
                path = Path(name)
                assert not path.is_absolute() and '..' not in path.parts, name
                assert '__pycache__' not in path.parts and 'cache' not in path.parts and 'frames' not in path.parts, name
            manifest = json.loads(source.read('MANIFESTE_SHA256.json'))
            assert set(names) == set(manifest) | {'MANIFESTE_SHA256.json','LIRE_MOI.txt'}
            assert all(hashlib.sha256(source.read(name)).hexdigest() == digest
                       for name,digest in manifest.items()), 'Manifest mismatch'
            source.extractall(extracted)
        report['crc_passed'] = True
        report['manifest_files_verified'] = len(manifest)
        assert all(sha(extracted/name) == digest for name,digest in manifest.items())
        production = {name:digest for name,digest in manifest.items()
                      if name.startswith(str(REL_EP/'sources')+'/')
                      or name in ('mou_rig.py', str(REL_EP/'chronologie.json'))}
        env = isolated_env(trial/'cache')
        cold = pictures(extracted, trial/'cold_pictures', env)
        reference = pictures(ROOT, trial/'reference_pictures', env)
        differences = []
        for index,(a,b) in enumerate(zip(cold['frames'],reference['frames'])):
            assert a['svg_sha256'] == b['svg_sha256'], ('SVG mismatch', a['time_seconds'])
            with Image.open(trial/'cold_pictures'/f'frame_{index}.png') as image:
                actual = np.array(image.convert('RGBA'))
            with Image.open(trial/'reference_pictures'/f'frame_{index}.png') as image:
                expected = np.array(image.convert('RGBA'))
            assert actual.shape == (1920,1080,4)
            error = np.abs(actual.astype(np.int16)-expected.astype(np.int16))
            assert not error.any(), ('Cold picture differs', a['time_seconds'])
            differences.append({**a,'max_pixel_error':int(error.max()),'pixels_identical':True})
        report['cold_loaded_modules'] = cold['modules']
        report['fresh_cairo_frames'] = differences
        son = extracted/REL_EP/'sources/son.py'
        done = subprocess.run([sys.executable, '-I', '-B', str(son)],
                              cwd=extracted, env=env, check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        sound_result = json.loads(done.stdout)
        actual_mix = sha(extracted/REL_EP/'audio/mix.wav')
        assert actual_mix == EXPECTED_MIX == sha(EP/'audio/mix.wav')
        assert sha(extracted/REL_EP/'audio/test_fin_8s.wav') == sha(EP/'audio/test_fin_8s.wav')
        assert all(sha(extracted/name) == digest for name,digest in production.items()), 'Cold sources modified while reproducing'
        report['regenerated_mix_sha256'] = actual_mix
        report['sound_regeneration'] = sound_result
        report['isolated_work_directory'] = str(trial.relative_to(ROOT))
        report['no_render_cache_used'] = True
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        temporary = audit.with_name('.'+audit.name)
        temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        os.replace(temporary,audit)
    print(json.dumps({'status':report['status'], 'archive_sha256':report['archive_sha256'],
                      'manifest_files_verified':report['manifest_files_verified'],
                      'fresh_frames':len(report['fresh_cairo_frames']),
                      'regenerated_mix_sha256':report['regenerated_mix_sha256']}))


if __name__ == '__main__':
    main()
