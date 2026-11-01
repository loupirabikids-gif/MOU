"""Independent V30 checks on protected sources, native geometry and real exports.

No renderer cache is used for fresh-image checks. Audio checks compare PCM and
the decoded AAC, without claiming listening, perceived audibility or humour.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import wave
import xml.etree.ElementTree as ET

import cairosvg
import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[1]
ROOT = next(p for p in EP.parents if (p / 'mou_rig.py').is_file())
SOURCE = EP / 'sources'
SR, FPS, SECONDS = 48000, 24, 38.
SAMPLES = round(SR * SECONDS)
REMOVED = {'cuisson_progressive_v27', 'dernier_tsss_poele_v27'}
LIMITS = ('Source, numerical and decoded-image checks. No model listening, '
          'human artistic approval, emotion recognition or comic success is certified.')
SAMPLE_TIMES = (.65, 1.5, 2.9583333, 3.25, 4.5, 6.75, 7.125, 9.4, 10.75,
                11.7, 13.4, 15.58, 16.1, 16.85, 18.3, 20.35,
                21.875, 22.0416667, 22.4166667, 25.5, 25.6666667,
                25.75, 25.8333333, 26.6, 28.25, 29.5, 30.8,
                31.7916667, 31.875, 32.15, 32.5, 32.7916667,
                32.8333333, 33.0833333, 33.5, 34., 34.5,
                35.1666667, 35.5, 36.15, 37.25, 37.9583333)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


ref = module(SOURCE / 'verify_reference_v28.py', 'mou_qa_reference_v28')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path), 'rb') as stream:
        assert (stream.getframerate(), stream.getnchannels(), stream.getsampwidth()) == (SR, 2, 2)
        return np.frombuffer(stream.readframes(stream.getnframes()), '<i2').reshape(-1, 2).astype(np.int64)


def locate(path):
    """Resolve source-freeze paths both in the repository and a portable copy."""
    path = Path(path)
    if path.is_file():
        return path
    marker = 'episodes/03/cuisine_v30/'
    value = path.as_posix()
    return EP / value.split(marker, 1)[1] if marker in value else ROOT / path


def source_checks():
    baseline = json.loads((EP / 'controle/baseline_protegee.json').read_text())
    preserved, absent = [], []
    for name, expected in baseline.items():
        path = ROOT / name
        if path.is_file():
            assert sha(path) == expected, ('Protected original changed', name)
            preserved.append(name)
        else:
            absent.append(name)
    frozen = json.loads((EP / 'controle/sources_final.json').read_text())['sha256']
    assert frozen
    for name, expected in frozen.items():
        assert sha(locate(name)) == expected, ('Visual source changed after HD render', name)
    required = {'render.py', 'animation.py', 'performance.py', 'jeu_visage.py',
                'visage.py', 'sink.py', 'mitten.py', 'costume.py'}
    assert required.issubset({Path(x).name for x in frozen})
    assert sha(ROOT / 'mou_rig.py') == ref.RIG_SHA
    gel = json.loads((EP / 'audio/gel_son.json').read_text())
    assert sha(SOURCE / 'son.py') == gel['source_sha256']
    for name, expected in gel['inputs_sha256'].items():
        assert sha(EP / name) == expected, ('Frozen audio input changed', name)
    assert sha(EP / 'audio/mix.wav') == gel['mix_sha256']
    assert sha(EP / 'audio/provenance.json') == gel['provenance_sha256']
    return {'canonical_rig_sha256': ref.RIG_SHA, 'visual_frozen_file_count': len(frozen),
            'protected_originals_verified': preserved,
            'historical_files_absent_in_portable_copy': absent,
            'sound_producer_sha256': gel['source_sha256'], 'mix_sha256': gel['mix_sha256']}


def audio_checks():
    bank = json.loads((EP / 'audio/input_bank.json').read_text())
    original = json.loads((EP / 'audio' / bank['original_manifest_file']).read_text())
    old = {e['name']: e for e in original['events']}
    events = bank['events']
    assert len(old) == 63 and len(events) == 61
    assert {e['name'] for e in events} == set(old) - REMOVED
    music_before = np.zeros((SAMPLES, 2), dtype=np.int64)
    music_after = np.zeros_like(music_before)
    other = np.zeros_like(music_before)
    voice = np.zeros_like(music_before)
    gain = 10. ** (-6. / 20.)
    for e in events:
        former = old[e['name']]
        for key in ('kind', 'sha256', 'start_sample', 'samples'):
            assert e[key] == former[key], (e['name'], 'Retained cue changed', key)
        path = EP / 'audio' / e['file']
        assert sha(path) == e['sha256']
        data = pcm(path)
        assert data.shape == (e['samples'], 2)
        a, b = e['start_sample'], e['start_sample'] + len(data)
        if e['kind'] == 'background_music':
            music_before[a:b] += data
            music_after[a:b] += np.rint(data * gain).astype(np.int64)
        else:
            other[a:b] += data
            if e['kind'] == 'mou_nonverbal':
                voice[a:b] += data
    envelope = np.ones(SAMPLES)
    attack, release = round(.008 * SR), round(.035 * SR)
    envelope[:attack] *= np.sin(np.linspace(0., np.pi / 2., attack)) ** 2
    envelope[-release:] *= np.cos(np.linspace(0., np.pi / 2., release)) ** 2

    def master(signal):
        before = np.rint(signal * envelope[:, None]).astype(np.int32)
        return np.rint(before * 10. ** (3.5 / 20.)).astype(np.int32)

    revised = master(other + music_after)
    delivered = pcm(EP / 'audio/mix.wav')
    assert np.array_equal(revised, delivered), 'WAV does not equal retained cues plus fixed music gain'
    prior = master(other + music_before)
    prior_sha = hashlib.sha256(prior.astype('<i2').tobytes()).hexdigest()
    assert prior_sha == '8f06edd457bca66d39a7079107d80a56f6b738fd660d7488818d4b5708d9e809'
    zero_music = np.all(music_before == 0, axis=1)
    assert np.array_equal(revised[zero_music], prior[zero_music])
    for a, b in ((32., 32.5), (37.25, 38.)):
        assert not revised[round(a * SR):round(b * SR)].any()
    assert np.abs(revised).max() < 32767
    ratios = []
    for e in events:
        if e['kind'] != 'mou_nonverbal':
            continue
        a, b = e['start_sample'], e['start_sample'] + e['samples']
        rms = lambda x: float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2)))
        before, after = rms(music_before[a:b]), rms(music_after[a:b])
        item = {'name': e['name'], 'interval_s': [a / SR, b / SR],
                'voice_unchanged': True, 'music_is_zero': before == 0.}
        if before:
            improvement = 20. * math.log10(before / after)
            assert abs(improvement - 6.) < .02
            item['voice_to_music_improvement_db'] = improvement
        else:
            assert not after
            item['voice_to_music_improvement_db'] = None
        ratios.append(item)
    assert len(ratios) == 5
    return {'retained_cues': 61, 'removed_cues': sorted(REMOVED),
            'unchanged_nonmusic_cues': 60, 'music_constant_gain_db': -6.,
            'independent_reconstruction_bit_exact': True, 'prior_no_cooking_pcm_sha256': prior_sha,
            'pcm_identical_where_original_music_is_zero': True,
            'new_normalization': False, 'new_ducking': False,
            'clipped_pcm_samples': 0, 'exact_silences_s': [[32., 32.5], [37.25, 38.]],
            'voice_windows': ratios}


def sink_checks(renderer):
    times = []
    current = {}
    for i in range(round(FPS * SECONDS)):
        state = renderer.animation.scene_state(i / FPS)
        if state['shot'] == 'sink':
            times.append(i / FPS)
            current[str(i)] = hashlib.sha256(renderer.svg_at(i / FPS).encode()).hexdigest()
    old_path = EP.parent / 'cuisine_v28/sources/render.py'
    if not old_path.is_file():
        return {'sink_frames': len(times), 'historical_svg_comparison': 'V28 absent in portable copy'}
    script = '''import hashlib,importlib.util,json,sys
p=sys.argv[1];spec=importlib.util.spec_from_file_location('old_sink_renderer',p)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
indices=json.loads(sys.argv[2]);print(json.dumps({str(i):hashlib.sha256(r.svg_at(i/24).encode()).hexdigest() for i in indices}))
'''
    previous = json.loads(subprocess.check_output([
        sys.executable, '-B', '-c', script, str(old_path), json.dumps([round(t * FPS) for t in times])]))
    assert previous == current, 'Approved sink insert images changed'
    return {'sink_frames': len(times), 'four_insert_svg_frames_identical_to_v28': True,
            'comparison': 'SHA256 of emitted SVG, every sink frame, separate clean process'}


def isolate(svg, ids, dimensions=(270, 480)):
    root = ET.fromstring(svg)
    face = next(e for e in root.iter() if e.get('id') == 'face')
    clips = [e for e in face.iter() if e.tag.endswith('clipPath') and '-eye-' in e.get('id', '')]
    assert len(clips) == 2
    for index, clip in enumerate(clips):
        aperture = copy.deepcopy(list(clip)[0])
        aperture.set('id', 'qa-eye-' + str(index))
        aperture.set('fill', '#FFFFFF')
        face.append(aperture)
    selected = set(ids)

    def prune(node):
        if node.tag.rsplit('}', 1)[-1] in ('defs', 'style') or node.get('id') in selected:
            return copy.deepcopy(node)
        result = ET.Element(node.tag, node.attrib)
        for child in node:
            value = prune(child)
            if value is not None:
                result.append(value)
        return result if len(result) or node is root else None

    result = prune(root)
    result.set('viewBox', '0 0 1080 1920')
    png = cairosvg.svg2png(bytestring=ET.tostring(result),
                         output_width=dimensions[0], output_height=dimensions[1])
    return np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'))[:, :, 3] >= 64


def face_clearance_checks(renderer):
    # Critical poses and breath accents, including late presentation, at phone scale.
    times = (2.9583333, 3.0833333, 3.25, 3.4166667, 6.75, 7.125,
             13.1, 13.4, 18.04, 18.3, 21.9583333, 22.1666667,
             25.75, 26.6, 28.25, 31.8333333, 31.9583333,
             32.8333333, 33.5, 34., 34.5, 35.1666667, 35.5, 36.15, 37.5)
    results = []
    for t in times:
        i = min(911, round(t * FPS))
        svg = renderer.svg_at(i / FPS)
        hands = isolate(svg, ['arm-left', 'arm-right'])
        eyes = isolate(svg, ['qa-eye-0', 'qa-eye-1'])
        mouth = isolate(svg, ['mouth'])
        overlap_eyes = int(np.count_nonzero(hands & eyes))
        overlap_mouth = int(np.count_nonzero(hands & mouth))
        assert overlap_eyes <= 1 and overlap_mouth <= 1, (i, 'Native arm hides face', overlap_eyes, overlap_mouth)
        results.append({'frame': i, 'time_s': i / FPS,
                        'eye_overlap_pixels_270': overlap_eyes,
                        'mouth_overlap_pixels_270': overlap_mouth})
    return results


def shock_mouth_clearance_checks(renderer):
    """Measure actual emitted geometry after the mouth/apron collision correction."""
    results = []
    for index in range(math.ceil(31.66 * FPS), math.floor(32.5 * FPS) + 1):
        svg = renderer.svg_at(index / FPS)
        mouth = isolate(svg, ['mouth'], (1080, 1920))
        apron = isolate(svg, ['tablier-taille'], (1080, 1920))
        eyes = isolate(svg, ['qa-eye-0', 'qa-eye-1'], (1080, 1920))
        mouth_area = int(np.count_nonzero(mouth))
        apron_overlap = int(np.count_nonzero(mouth & apron))
        eye_overlap = int(np.count_nonzero(mouth & eyes))
        assert mouth_area > 0, (index, 'Shock mouth is absent from the frame')
        assert apron_overlap == 0, (index, 'Apron hides the shock mouth', apron_overlap)
        assert eye_overlap == 0, (index, 'Shock mouth reaches the eyes', eye_overlap)
        results.append({'frame': index, 'time_s': index / FPS,
                        'mouth_area_pixels': mouth_area,
                        'mouth_apron_overlap_pixels': apron_overlap,
                        'mouth_eye_overlap_pixels': eye_overlap})
    return {'window_s': [31.66, 32.5], 'raster_dimensions': [1080, 1920],
            'method': 'Independent alpha masks of actual mouth, apron and eye apertures; complete discrete frame window.',
            'frames_checked': len(results), 'samples': results}


def vocal_pose_checks(renderer):
    provenance = json.loads((EP / 'audio/provenance.json').read_text())
    results = []
    for event in provenance['voice_anchors']:
        peak = event['peak_rms_8ms_seconds']
        i = round(peak * FPS)
        state = renderer.animation.scene_state(i / FPS)
        sync = state['expression'].get('vocal_sync')
        assert sync and sync['amount'] > .5, (event['name'], 'No visual accent at voice peak')
        assert abs(sync['audio_rms_peak_s'] - peak) < .0001, (event['name'], 'Wrong anchor')
        assert abs(i / FPS - peak) <= .5 / FPS + 1e-8
        pose = state['pose']
        if event['name'] in ('mou_inspiration', 'mou_choc', 'mou_expiration'):
            assert pose['mouth_shape'] == 'o', (event['name'], 'Breath lacks opening')
            assert pose['mouth_open'] >= {'mou_inspiration': .35, 'mou_choc': .75, 'mou_expiration': .09}[event['name']]
        else:
            assert pose['mouth_open'] < .10, (event['name'], 'Nasal murmur became an open breath')
        results.append({'name': event['name'], 'audio_rms_peak_s': peak,
                        'nearest_video_frame': i, 'time_s': i / FPS,
                        'mouth_shape': pose['mouth_shape'], 'mouth_open': pose['mouth_open'],
                        'vocal_sync': sync, 'body_scale_y': state['performance']['scale_y']})
    assert len(results) == 5
    still = []
    for i in range(math.ceil(21.95 * FPS), math.ceil(22.45 * FPS)):
        state = renderer.animation.scene_state(i / FPS)
        still.append(json.dumps({k: state.get(k) for k in ('performance_affine_svg', 'hands', 'arms')}, sort_keys=True))
    assert len(set(still)) == 1, 'Resistance pause has bodily drift'
    return {'voice_accents': results, 'resistance_body_and_hands_hold_frames': len(still),
            'voice_synchronization_scope': 'Numeric peaks and visible state; not perceived phonation or emotion.'}


def caption_image_check(renderer, movie):
    """Check the entire enlarged title, including the newly extended right edge."""
    index = round(1.5 * FPS)
    actual = ref.decoded_samples(movie, [index])[0]
    svg = renderer.svg_at(index / FPS)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=1080, output_height=1920)
    fresh = np.asarray(Image.open(io.BytesIO(png)).convert('RGB'))
    left, top, right, bottom = map(int, renderer.CAPTION_BOUNDS)
    left, top, right, bottom = left - 8, top - 8, right + 8, bottom + 8
    difference = np.abs(actual[top:bottom, left:right].astype(np.int16)
                        - fresh[top:bottom, left:right].astype(np.int16))
    error = float(difference.mean())
    assert error < ref.MEAN_ERROR_LIMIT, ('Enlarged caption differs from fresh render', error)
    root = ET.fromstring(svg)
    caption = next(e for e in root.iter() if e.get('id') == 'caption-ouverture')
    assert caption.get('data-caption') == renderer.CAPTION_TEXT
    return {'frame': index, 'time_s': index / FPS,
            'enlarged_caption_pixel_roi': [left, top, right, bottom],
            'mean_abs_rgb_error_0_255': error, 'data_caption': caption.get('data-caption')}


def main():
    sources = source_checks()
    renderer = ref.load_renderer()
    movie = EP / 'MOU_Encore_une_feuille.mp4'
    mute = EP / 'MOU_Encore_une_feuille_muette.mp4'
    ref.SAMPLE_TIMES = SAMPLE_TIMES
    print('QA V30: protected files and source freezes checked', flush=True)
    sound = audio_checks()
    sound['encoded_correspondence'] = ref.audio_check(movie)
    print('QA V30: independent sound reconstruction and AAC correspondence checked', flush=True)
    structure = ref.structure_checks(renderer)
    print('QA V30: 912 structural states checked', flush=True)
    sink = sink_checks(renderer)
    clearance = face_clearance_checks(renderer)
    shock_clearance = shock_mouth_clearance_checks(renderer)
    print('QA V30: corrected shock mouth clear of apron and eyes throughout window', flush=True)
    accents = vocal_pose_checks(renderer)
    assert renderer.CAPTION_TEXT == 'Me cooking: touch, wash, wipe… repeat.'
    assert renderer.CAPTION_BOUNDS[1] >= 120. and renderer.CAPTION_BOUNDS[2] <= 900.
    video = {'sound': ref.check_video(movie, True), 'mute': ref.check_video(mute, False)}
    a, b = ref.bitstream_digest(movie), ref.bitstream_digest(mute)
    assert a == b, 'AAC mux changed the picture'
    fresh = ref.fresh_image_checks(renderer, movie)
    assert not fresh['failures'], fresh['failures']
    caption_image = caption_image_check(renderer, movie)
    # Recheck freezes after independent rasterization and full decodes.
    assert source_checks() == sources
    report = {'revision': 30, 'status': 'pass', 'sources': sources, 'audio': sound,
              'structure': structure, 'sink_unchanged': sink,
              'phone_scale_native_arms_face_clearance': clearance,
              'shock_mouth_clearance': shock_clearance,
              'vocal_pose_checks': accents, 'videos': video,
              'same_h264_in_sound_and_mute': a, 'fresh_image_checks': fresh,
              'caption': {'text': renderer.CAPTION_TEXT, 'bounds': renderer.CAPTION_BOUNDS,
                          'end_s': renderer.CAPTION_END, 'decoded_image_check': caption_image}, 'limits': LIMITS}
    ref.atomic_json(EP / 'controle/qa_v30.json', report)
    max_error = max(x['full_frame_mean_abs_rgb_error_0_255'] for x in fresh['samples'])
    text = f'''# Contrôle indépendant V30

Statut : passé. 38 s, 1080 × 1920, 24 images/s, 912 images.

- 912 états SVG : deux bras/moufles natifs, contacts recalculés, pieds ancrés,
  quatre lavages des extrémités et tenue finale de 18 images.
- {len(clearance)} poses sensibles : aucun recouvrement des yeux ou de la bouche
  par les bras aux masques de 270 × 480.
- Correctif après critique HD : bouche de choc dégagée du tablier et des yeux,
  contrôlée par masques 1080 × 1920 sur les {shock_clearance['frames_checked']} images
  de la fenêtre 31,66–32,50 s. Les contrôles portent sur la géométrie émise.
- Cinq accents vocaux : poses et bouche vérifiées aux pics RMS, avec une vraie
  pause corporelle de {accents['resistance_body_and_hands_hold_frames']} images lors de l’hésitation.
- 61 cues conservés ; les deux cues de cuisson sont absents. Jazz −6 dB
  constant, autres cues et voix inchangés. Le mix est reconstruit exactement
  par le contrôleur indépendant. Silences préservés, zéro écrêtage PCM.
- MP4 son et muet décodés entièrement, flux H.264 identiques ; AAC comparé au
  WAV courant sans décalage. {len(fresh['samples'])} images HD réelles comparées à des
  rendus CairoSVG frais hors cache ; erreur moyenne maximale {max_error:.3f}/255.
- Rig et anciens fichiers présents protégés, gels des sources visuelles et
  sonores vérifiés avant et après les contrôles.

Le détail de la comparaison des lavabos, les ancres, mesures et empreintes
sont dans qa_v30.json. Ces contrôles ne prouvent ni l’émotion reconnue par
un public, ni le confort d’écoute, ni le succès comique. Le modèle ne peut
pas écouter dans cet environnement.
'''
    (EP / 'controle/qa_v30.md').write_text(text)
    print(json.dumps({'status': 'pass', 'frames': 912, 'fresh_hd_samples': len(fresh['samples']),
                      'max_full_frame_mean_error': max_error, 'report': 'controle/qa_v30.json'}))


if __name__ == '__main__':
    main()
