"""Check the V28 ZIP and reproduce images/audio from a fresh isolated extraction.

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
TIMES = [2.9, 25.75, 32.8333, 35.5, 37.5]
GITHUB_LIMIT_BYTES = 100_000_000
PRESERVED_V27_MIX_SHA = '16294d1642cd220b6eb0cf3c7c8ffa32db70db5105f692e766a4fe62601aff0b'
REL_LIBRARY = Path('bibliotheque/sons/v1')


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
spec=importlib.util.spec_from_file_location('archive_cold_renderer_v28',path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
assert r.ROOT.resolve()==root, ('Unexpected renderer ROOT',r.ROOT,root)
assert (r.DURATION,r.FPS,r.W,r.H)==(38.,24,1080,1920)
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
modules=[r,r.animation,r.art,r.sink,r.costume,r.cooking_fx,
         r.animation._performance,sys.modules['mou_rig']]
assert pathlib.Path(r.animation._performance.__file__).resolve()==root/relative/'sources/performance.py'
# The wrapper's delegated native modules are in sys.modules or are module
# attributes; retain their real paths rather than assuming the old topology.
for candidate in (getattr(r.animation,'_reference',None),getattr(r.animation,'_stir',None)):
    if candidate is not None and candidate not in modules:modules.append(candidate)
for loaded in list(sys.modules.values()):
    file=getattr(loaded,'__file__',None)
    if file and ('/episodes/03/' in str(file) or '/bibliotheque/' in str(file)
                 or pathlib.Path(file).name=='mou_rig.py'):
        if loaded not in modules:modules.append(loaded)
for m in modules:
    assert pathlib.Path(m.__file__).resolve().is_relative_to(root),(m.__name__,m.__file__)
print(json.dumps({'modules':{m.__name__:str(pathlib.Path(m.__file__).resolve().relative_to(root))
                              for m in modules},'frames':results}))
'''

SOUND_WORKER = r'''
import json, pathlib, runpy, sys
''' + NETWORK_GUARD + r'''
path=pathlib.Path(sys.argv[1]).resolve()
root=next(p for p in path.parents if (p/'mou_rig.py').is_file())
sys.argv=[str(path)]
runpy.run_path(str(path),run_name='__main__')
modules={}
for loaded in list(sys.modules.values()):
    file=getattr(loaded,'__file__',None)
    if file and ('/episodes/03/' in str(file) or '/bibliotheque/' in str(file)
                 or pathlib.Path(file).name=='mou_rig.py'):
        location=pathlib.Path(file).resolve()
        assert location.is_relative_to(root),(loaded.__name__,str(location),str(root))
        modules[loaded.__name__]=str(location.relative_to(root))
actual=set(modules.values())
for name in ('music.py','foley.py','foley_supplement.py','vocal.py'):
    expected=str(path.parent.relative_to(root)/name)
    assert expected in actual,('Production module not loaded from isolated project',expected)
print(json.dumps({'archive_worker':{'executed_sound_source':str(path.relative_to(root)),
                                  'cold_project_modules':modules}}))
'''


LIBRARY_WORKER = r'''
import collections, hashlib, importlib.util, json, pathlib, sys, wave
''' + NETWORK_GUARD + r'''
import numpy as np
root=pathlib.Path(sys.argv[1]).resolve()
relative=pathlib.Path(sys.argv[2]);here=root/relative
out=pathlib.Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
path=here/'sound_bank.py'
spec=importlib.util.spec_from_file_location('archive_cold_voice_library_v1',path)
bank=importlib.util.module_from_spec(spec);sys.modules[spec.name]=bank;spec.loader.exec_module(bank)
assert pathlib.Path(bank.__file__).resolve().is_relative_to(root)
catalogue=json.loads((here/'CATALOGUE.json').read_text())
assert catalogue['sample_rate']==48000 and catalogue['channels']==2
assert catalogue['families']==6 and catalogue['variants_per_family']==2
assert len(catalogue['sounds'])==12
families=collections.Counter(e['family'] for e in catalogue['sounds'])
assert len(families)==6 and set(families.values())=={2}
results=[]
for entry in catalogue['sounds']:
    signal,metadata=bank.render(entry['id'])
    values=np.rint(np.asarray(signal)*32768.).astype(np.int32)
    assert values.shape==(entry['samples'],2) and np.abs(values).max()<32767
    assert metadata['anchor_sample']==entry['anchor_sample']
    assert metadata['peak_sample']==entry['peak_sample']
    target=out/(entry['id']+'.wav')
    with wave.open(str(target),'wb') as output:
        output.setnchannels(2);output.setsampwidth(2);output.setframerate(48000)
        output.writeframes(values.astype('<i2').tobytes())
    actual=hashlib.sha256(target.read_bytes()).hexdigest()
    assert actual==entry['sha256'],('Library WAV not reproducible',entry['id'])
    assert actual==hashlib.sha256((here/entry['file']).read_bytes()).hexdigest()
    results.append({'id':entry['id'],'sha256':actual,'anchor_sample':metadata['anchor_sample'],
                    'peak_sample':metadata['peak_sample'],'samples':entry['samples']})
assert len({e['sha256'] for e in results})==12
print(json.dumps({'source':str(path.relative_to(root)),'families':dict(families),
                  'regenerated_sounds':results,'injected_into_movie':False,
                  'limits':catalogue['limits']}))
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
    # The renderer emits one JSON object; the sound generator emits its mix
    # and music reports as successive JSON documents. Preserve every report
    # while rejecting unrelated, non-JSON stdout rather than hiding it.
    decoder=json.JSONDecoder()
    documents=[]
    position=0
    while position<len(result.stdout):
        if result.stdout[position].isspace():
            position+=1
            continue
        document,position=decoder.raw_decode(result.stdout,position)
        documents.append(document)
    if not documents:
        raise ValueError(f'Isolated process produced no JSON report; see {log}.stdout.txt')
    if len(documents)==1:
        return documents[0]
    return {'stdout_framing':'successive valid JSON documents','documents':documents}


def pcm(path):
    with wave.open(str(path), 'rb') as source:
        assert (source.getframerate(),source.getnchannels(),source.getsampwidth())==(48000,2,2)
        return np.frombuffer(source.readframes(source.getnframes()), '<i2').reshape(-1,2).copy()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=EP/'MOU_Encore_une_feuille_sources.zip')
    parser.add_argument('--precheck', action='store_true',
                        help='List missing local cold-reproduction inputs without opening a ZIP or writing a final audit')
    args=parser.parse_args()
    if args.precheck:
        required=[EP/'chronologie.json',EP/'chronologie_reference_v25.json',
                  EP/'README.md',EP/'CONTROLE.txt',EP/'audio/source_bank_v26.json',
                  EP/'audio/mix.wav',EP/'audio/test_fin_v27.wav',
                  EP/'assets/FluidR3_MOU_bossa.sf2',EP/'audio/reference_events_v26.json',
                  EP/'audio/musique_v27.wav',EP/'assets/vocal_sources/provenance.json',
                  EP/'assets/vocal_sources/CC0_LICENSE.txt',
                  ROOT/REL_LIBRARY/'CATALOGUE.json',ROOT/REL_LIBRARY/'index.html',
                  ROOT/REL_LIBRARY/'sound_bank.py',ROOT/REL_LIBRARY/'build.py',
                  ROOT/REL_LIBRARY/'sources/provenance.json']
        required.extend(EP/'sources'/n for n in ('render.py','son.py','music.py','foley.py',
             'foley_supplement.py','vocal.py','animation.py','performance.py','jeu_visage.py','reference_animation.py',
             'reference_performance.py','reference_jeu_visage.py','reference_acting.py',
             'art.py','cooking_fx.py','sink.py','mitten.py','costume.py','visage.py','expressions.json'))
        missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
        print(json.dumps({'mode':'precheck_only','missing_current_inputs':missing,
                         'all_inputs_present':not missing,'archive_opened':False,
                         'final_audit_written':False},ensure_ascii=False))
        return
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
        work=ROOT/'work/archive_v28';work.mkdir(parents=True,exist_ok=True)
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
            assert str(REL_EP/'controle/verify_archive_v28.py') in names, 'Reusable checker missing'
            manifest=json.loads(source.read('MANIFESTE_SHA256.json'))
            assert (REL_EP/'MOU_Encore_une_feuille_muette.mp4').as_posix() not in manifest, 'V28 source archive must rebuild its changed images rather than bundle the silent movie'
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
                    or any('reference' in part for part in PurePosixPath(name).parts)
                    or '/audio/recordings/' in name}
        expected_mix=sha(EP/'audio/mix.wav')
        assert expected_mix==PRESERVED_V27_MIX_SHA, 'V28 changed the deliberately preserved V27 mix'
        expected_end=sha(EP/'audio/test_fin_v27.wav')
        report['current_repository_mix_sha256']=expected_mix
        report['deliberately_preserved_v27_mix_sha256']=PRESERVED_V27_MIX_SHA
        soundfont=REL_EP/'assets/FluidR3_MOU_bossa.sf2'
        assert soundfont.as_posix() in manifest, 'Bundled FluidR3 bank missing'
        report['bundled_soundfont_sha256']=sha(extracted/soundfont)
        report['included_audio_reference_files']={name:digest for name,digest in manifest.items()
            if name.startswith((REL_EP/'audio').as_posix()+'/')
            and any('reference' in part for part in PurePosixPath(name).parts)}
        reference_contract=REL_EP/'audio/source_bank_v26.json'
        assert reference_contract.as_posix() in manifest, 'Local raw cue bank provenance missing'
        source_bank=json.loads((extracted/reference_contract).read_text())
        retained_pcm={}
        for event in source_bank['raw_events'].values():
            name=(REL_EP/'audio'/event['file']).as_posix()
            assert manifest.get(name)==event['sha256'], ('Raw input PCM missing or changed',name)
            retained_pcm[name]=manifest[name]
        production.update(retained_pcm)
        production[reference_contract.as_posix()]=manifest[reference_contract.as_posix()]
        assert (REL_EP/'chronologie_reference_v25.json').as_posix() in manifest, 'Reference gesture clock missing'
        assert (REL_EP/'sources/reference_animation.py').as_posix() in manifest, 'Reference gesture code missing'
        report['immutable_raw_bank_pcm_files']=retained_pcm
        vocal_dir=REL_EP/'assets/vocal_sources'
        vocal_manifest=vocal_dir/'provenance.json'
        assert vocal_manifest.as_posix() in manifest, 'Vocal provenance missing'
        vocal=json.loads((extracted/vocal_manifest).read_text())
        licence=[name for name,digest in manifest.items()
                 if name.startswith(vocal_dir.as_posix()+'/') and digest==vocal['licence_sha256']]
        assert licence, 'Bundled vocal CC0 notice missing or changed'
        vocal_inputs={}
        for entry in vocal['sources']:
            for key,digest_key in (('local_original','source_sha256'),('local_wav','wav_sha256')):
                payload=(vocal_dir/entry[key]).as_posix()
                assert manifest.get(payload)==entry[digest_key],('Vocal input missing or changed',payload)
                vocal_inputs[payload]=manifest[payload]
        report['bundled_vocal_sources_sha256']=vocal_inputs
        report['bundled_vocal_cc0_notice_files']=licence
        report['vocal_quality_limit']=vocal.get('limits','Recording method and perceived quality unverified.')
        event_reference=REL_EP/'audio/reference_events_v26.json'
        assert event_reference.as_posix() in manifest, 'Local V26 event metadata snapshot missing'
        production[event_reference.as_posix()]=manifest[event_reference.as_posix()]
        library_catalogue=(REL_LIBRARY/'CATALOGUE.json').as_posix()
        assert library_catalogue in manifest, 'Separate voice library catalogue missing'
        library=json.loads((extracted/library_catalogue).read_text())
        assert len(library['sounds'])==12 and library['families']==6 and library['variants_per_family']==2
        for entry in library['sounds']:
            payload=(REL_LIBRARY/entry['file']).as_posix()
            assert manifest.get(payload)==entry['sha256'],('Library proposal missing or changed',entry['id'])
        for filename in ('sound_bank.py','build.py','index.html','README.md','sources/provenance.json'):
            assert (REL_LIBRARY/filename).as_posix() in manifest,('Portable library input missing',filename)
        library_provenance=json.loads((extracted/REL_LIBRARY/'sources/provenance.json').read_text())
        library_licence=[name for name,digest in manifest.items()
                         if name.startswith((REL_LIBRARY/'sources').as_posix()+'/')
                         and digest==library_provenance['licence_sha256']]
        assert library_licence, 'Separate library CC0 notice missing'
        for entry in library_provenance['sources']:
            for field,checksum in (('local_original','source_sha256'),('local_wav','wav_sha256')):
                payload=(REL_LIBRARY/'sources'/entry[field]).as_posix()
                assert manifest.get(payload)==entry[checksum],('Separate library input missing',payload)
        production.update({name:digest for name,digest in manifest.items()
                           if name.startswith(REL_LIBRARY.as_posix()+'/')})
        report['separate_voice_library']={'sounds':12,'families':6,'variants_per_family':2,
            'catalogue_status':library['status'],'cc0_notice_files':library_licence,
            'not_injected_into_movie':True,'limits':library['limits']}
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
        report['separate_voice_library_cold_regeneration']=isolated_run(
            LIBRARY_WORKER,[extracted,REL_LIBRARY,trial/'library_wavs'],extracted,env,trial/'library_cold')
        actual_mix=sha(extracted/REL_EP/'audio/mix.wav')
        assert actual_mix==expected_mix==sha(EP/'audio/mix.wav'), 'Regenerated mix differs'
        assert sha(extracted/REL_EP/'audio/test_fin_v27.wav')==expected_end==sha(EP/'audio/test_fin_v27.wav'), 'Final excerpt differs'
        mix=pcm(extracted/REL_EP/'audio/mix.wav')
        end=pcm(extracted/REL_EP/'audio/test_fin_v27.wav')
        assert mix.shape==(1_824_000,2) and end.shape==(384_000,2)
        assert np.array_equal(end,mix[1_440_000:]), 'Final eight seconds are not exact mix samples'
        assert not mix[32*48000:round(32.5*48000)].any(), 'The required half-second silence changed'
        assert not mix[round(37.25*48000):].any(), 'Final body hold is no longer silent'
        music=pcm(extracted/REL_EP/'audio/musique_v27.wav')
        assert music.shape==mix.shape
        outside=np.ones(len(music),bool);outside[:32*48000]=False
        outside[round(36.25*48000):round(36.75*48000)]=False
        assert not music[outside].any(), 'Music outside pre32 score and isolated final note'
        assert music[round(36.25*48000):round(36.75*48000)].any(), 'Isolated final guitar note missing'
        report['audio_punctuation']={'mix_exact_zero_s':[32.,32.5],
            'terminal_mix_exact_zero_s':[37.25,38.],
            'music_silent_after32_except_s':[36.25,36.75]}
        assert all(sha(extracted/name)==digest for name,digest in production.items()), 'Extracted production sources changed'
        assert all(sha(ROOT/name)==digest for name,digest in production.items()), 'Repository production sources changed'
        assert sha(archive)==report['archive_sha256'], 'Archive changed during verification'
        report['production_sources_unchanged']=True
        report['regenerated_mix_sha256']=actual_mix
        report['regenerated_final_8s_sha256']=expected_end
        report['final_8s_exact_samples']={'start_seconds':30.,'end_seconds':38.,'frames':384000,'identical':True}
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
                     'manifest_files_verified','regenerated_mix_sha256','regenerated_final_8s_sha256')}))


if __name__=='__main__':
    main()
