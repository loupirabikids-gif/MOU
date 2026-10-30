"""Check the V24 ZIP and reproduce images/audio from a fresh isolated extraction.

Run after sources/package.py. This audit is deliberately excluded from the ZIP;
its own checker is included. No viewing, listening or artistic approval follows
from a successful integrity/reproduction check.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import wave
import zipfile

import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p/'mou_rig.py').is_file())
REL_EP = EP.relative_to(ROOT)
TIMES = [4., 36.5, 42.75]
GITHUB_LIMIT_BYTES = 100_000_000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


NETWORK_GUARD = r'''
def forbid_network(event, arguments):
    if event in ('socket.connect', 'socket.getaddrinfo', 'socket.bind', 'socket.sendto'):
        raise RuntimeError('Network disabled during archive reproduction: '+event)
sys.addaudithook(forbid_network)
'''

PICTURE_WORKER = r'''
import hashlib, importlib.util, json, pathlib, sys
''' + NETWORK_GUARD + r'''
import cairosvg
from PIL import Image
root=pathlib.Path(sys.argv[1]).resolve()
relative=pathlib.Path(sys.argv[2])
out=pathlib.Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
path=root/relative/'sources/render.py'
spec=importlib.util.spec_from_file_location('archive_cold_renderer_v24',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
assert r.ROOT.resolve()==root, ('Unexpected renderer ROOT',r.ROOT,root)
assert (r.DURATION,r.FPS,r.W,r.H)==(43.,24,1080,1920)
results=[]
for i,t in enumerate(json.loads(sys.argv[4])):
    data=r.svg_at(t).encode()
    (out/f'frame_{i}.svg').write_bytes(data)
    output=out/f'frame_{i}.png'
    cairosvg.svg2png(bytestring=data,output_width=1080,output_height=1920,write_to=str(output))
    with Image.open(output) as image:
        rgba=image.convert('RGBA')
        assert rgba.size==(1080,1920)
        pixels=rgba.tobytes()
    results.append({'time_seconds':t,'svg_sha256':hashlib.sha256(data).hexdigest(),
                    'png_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                    'rgba_sha256':hashlib.sha256(pixels).hexdigest()})
modules=[r,r.animation,r.art,r.sink,r.costume,r.animation._stir,sys.modules['mou_rig']]
for loaded in list(sys.modules.values()):
    file=getattr(loaded,'__file__',None)
    if file and ('/episodes/03/' in str(file) or '/bibliotheque/' in str(file)):
        if loaded not in modules:
            modules.append(loaded)
for m in modules:
    assert pathlib.Path(m.__file__).resolve().is_relative_to(root),(m.__name__,m.__file__)
print(json.dumps({'modules':{m.__name__:str(pathlib.Path(m.__file__).resolve().relative_to(root))
                              for m in modules},'frames':results}))
'''

SOUND_WORKER = r'''
import pathlib, runpy, sys
''' + NETWORK_GUARD + r'''
path=pathlib.Path(sys.argv[1]).resolve()
sys.argv=[str(path)]
runpy.run_path(str(path),run_name='__main__')
'''


def isolated_env(cache):
    # Keep the managed proxy/CA/authentication environment untouched. Python -I
    # and removal of Python path overrides isolate project module loading.
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['XDG_CACHE_HOME'] = str(cache)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def isolated_run(code, arguments, root, env, log):
    result = subprocess.run([sys.executable, '-I', '-B', '-c', code, *map(str, arguments)],
                            cwd=root, env=env, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=600)
    log.with_suffix('.stdout.txt').write_text(result.stdout)
    log.with_suffix('.stderr.txt').write_text(result.stderr)
    if result.returncode:
        raise RuntimeError(f'Isolated process failed ({result.returncode}); see {log}.stderr.txt')
    return json.loads(result.stdout)


def pcm(path):
    with wave.open(str(path), 'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(48000,2,2)
        return np.frombuffer(source.readframes(source.getnframes()), '<i2').reshape(-1,2).copy()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=EP/'MOU_Encore_une_feuille_sources.zip')
    args=parser.parse_args()
    archive=args.archive.resolve()
    audit=EP/'controle/audit_archive.json'
    report={'status':'running','observed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'limits':'ZIP integrity and isolated reproducibility only; no listening, continuous viewing, artistic or audience approval.',
            'isolation':{'python_flags':['-I','-B'],'fresh_extraction':True,
                         'python_socket_operations_blocked':True,'proxy_environment_preserved':True,
                         'external_fetches_required':False,'packages_installed':False}}
    try:
        report.update(archive_sha256=sha(archive),archive_bytes=archive.stat().st_size)
        assert archive.stat().st_size<GITHUB_LIMIT_BYTES, 'Archive exceeds the 100 MB delivery limit'
        work=ROOT/'work/archive_v24';work.mkdir(parents=True,exist_ok=True)
        trial=Path(tempfile.mkdtemp(prefix='cold_',dir=work))
        extracted=trial/'extracted';extracted.mkdir()
        report['isolated_work_directory']=str(trial.relative_to(ROOT))
        with zipfile.ZipFile(archive) as source:
            names=source.namelist()
            assert len(names)==len(set(names)), 'Duplicate ZIP members'
            assert source.testzip() is None, 'ZIP CRC failure'
            for name in names:
                path=PurePosixPath(name)
                assert not path.is_absolute() and '..' not in path.parts and '\\' not in name, name
                assert not source.getinfo(name).is_dir(), ('Unexpected directory member',name)
                assert not (source.getinfo(name).external_attr>>16)&0o170000==0o120000, ('Symlink member',name)
                assert not any(p in ('__pycache__','cache','frames','work') for p in path.parts), name
                assert path.suffix!='.pyc', name
            assert str(REL_EP/'controle/audit_archive.json') not in names, 'Circular archive audit included'
            assert str(REL_EP/'controle/verify_archive_v24.py') in names, 'Reusable checker missing'
            manifest=json.loads(source.read('MANIFESTE_SHA256.json'))
            assert set(names)==set(manifest)|{'MANIFESTE_SHA256.json','LIRE_MOI.txt'}, 'Unmanifested payload'
            report['metadata_sha256']={name:hashlib.sha256(source.read(name)).hexdigest()
                                       for name in ('MANIFESTE_SHA256.json','LIRE_MOI.txt')}
            for name,digest in manifest.items():
                assert len(digest)==64 and all(c in '0123456789abcdef' for c in digest), ('Invalid SHA',name)
                assert hashlib.sha256(source.read(name)).hexdigest()==digest, ('Manifest mismatch',name)
            source.extractall(extracted)
        report['crc_passed']=True
        report['manifest_files_verified']=len(manifest)
        assert all(sha(extracted/name)==digest for name,digest in manifest.items()), 'Extraction differs'
        mismatches=[name for name,digest in manifest.items()
                    if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
        assert not mismatches, ('Archive differs from current repository',mismatches)
        report['current_repository_payload_identical']=True
        production={name:digest for name,digest in manifest.items()
                    if name.startswith((REL_EP/'sources').as_posix()+'/')
                    or name.endswith('.py') or name in ('mou_rig.py',(REL_EP/'chronologie.json').as_posix())
                    or name.startswith((REL_EP/'assets').as_posix()+'/')
                    or name.startswith((REL_EP/'audio/reference_v23').as_posix()+'/')}
        expected_mix=sha(EP/'audio/mix.wav')
        expected_end=sha(EP/'audio/test_fin_v24.wav')
        report['current_repository_mix_sha256']=expected_mix
        jazz_reference=REL_EP/'audio/reference_v23/musique_v23.wav'
        assert jazz_reference.as_posix() in manifest, 'Bundled V23 PCM jazz reference missing'
        report['bundled_jazz_pcm_reference']={'file':jazz_reference.as_posix(),
                                             'sha256':sha(extracted/jazz_reference),
                                             'mode':'Frozen included PCM, not a new FluidSynth rendering'}
        env=isolated_env(trial/'cache')
        cold=isolated_run(PICTURE_WORKER,[extracted,REL_EP,trial/'cold_pictures',json.dumps(TIMES)],
                          extracted,env,trial/'pictures_cold')
        reference=isolated_run(PICTURE_WORKER,[ROOT,REL_EP,trial/'reference_pictures',json.dumps(TIMES)],
                               ROOT,env,trial/'pictures_repository')
        assert len(cold['frames'])==len(reference['frames'])==len(TIMES)
        differences=[]
        for index,(actual,expected) in enumerate(zip(cold['frames'],reference['frames'])):
            assert actual['svg_sha256']==expected['svg_sha256'], ('SVG mismatch',TIMES[index])
            with Image.open(trial/'cold_pictures'/f'frame_{index}.png') as picture:
                a=np.array(picture.convert('RGBA'))
            with Image.open(trial/'reference_pictures'/f'frame_{index}.png') as picture:
                b=np.array(picture.convert('RGBA'))
            assert a.shape==b.shape==(1920,1080,4)
            error=np.abs(a.astype(np.int16)-b.astype(np.int16))
            assert not error.any(), ('Cold pixels differ',TIMES[index])
            differences.append({**actual,'max_pixel_error':int(error.max()),'pixels_identical':True})
        report['cold_loaded_modules']=cold['modules']
        report['fresh_cairo_frames']=differences
        report['no_render_cache_used']=True
        sound=isolated_run(SOUND_WORKER,[extracted/REL_EP/'sources/son.py'],extracted,env,trial/'sound_cold')
        actual_mix=sha(extracted/REL_EP/'audio/mix.wav')
        assert actual_mix==expected_mix==sha(EP/'audio/mix.wav'), 'Regenerated mix differs'
        assert sha(extracted/REL_EP/'audio/test_fin_v24.wav')==expected_end==sha(EP/'audio/test_fin_v24.wav'), 'Final excerpt differs'
        mix=pcm(extracted/REL_EP/'audio/mix.wav')
        end=pcm(extracted/REL_EP/'audio/test_fin_v24.wav')
        assert mix.shape==(2_064_000,2) and end.shape==(132_000,2)
        assert np.array_equal(end,mix[1_932_000:]), 'Final 2.75 seconds are not exact mix samples'
        assert all(sha(extracted/name)==digest for name,digest in production.items()), 'Extracted production sources changed'
        assert all(sha(ROOT/name)==digest for name,digest in production.items()), 'Repository production sources changed'
        assert sha(archive)==report['archive_sha256'], 'Archive changed during verification'
        report['production_sources_unchanged']=True
        report['regenerated_mix_sha256']=actual_mix
        report['regenerated_final_2_75s_sha256']=expected_end
        report['final_2_75s_exact_samples']={'start_seconds':40.25,'end_seconds':43.,'frames':132000,'identical':True}
        report['sound_regeneration']=sound
        report['status']='passed'
    except Exception as error:
        report['status']='failed';report['error']=f'{type(error).__name__}: {error}'
        raise
    finally:
        audit.parent.mkdir(parents=True,exist_ok=True)
        temporary=audit.with_name('.'+audit.name)
        temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        os.replace(temporary,audit)
    print(json.dumps({key:report[key] for key in ('status','archive_sha256','archive_bytes',
                     'manifest_files_verified','regenerated_mix_sha256','regenerated_final_2_75s_sha256')}))


if __name__=='__main__':
    main()
