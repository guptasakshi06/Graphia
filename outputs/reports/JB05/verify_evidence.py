"""JB05 development evidence only; never imported by the production app.

From the checkout: .venv/bin/python outputs/reports/JB05/verify_evidence.py --prepare
Then follow docs/validation/jigisha.md browser steps and run without --prepare.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def prepare():
    from PIL import Image, ImageDraw, ImageFont
    inputs = HERE / 'inputs'
    inputs.mkdir(exist_ok=True)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
    pages = {
        'JB05_FICTIONAL_identity_missing_name.png': [
            'SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT', 'Identity Proof',
            'Student Name:', 'Application ID: APP-2026-0104', 'Issue Date: 2026-01-18',
            'Fictional classroom data. No official validity.'],
        'JB05_FICTIONAL_unknown.png': [
            'SYNTHETIC SAMPLE - NOT AN OFFICIAL DOCUMENT', 'Classroom Library Note',
            'Return the borrowed books before Friday.', 'Fictional classroom data. No official validity.'],
    }
    for name, lines in pages.items():
        image = Image.new('RGB', (1400, 1000), 'white')
        draw = ImageDraw.Draw(image)
        for index, line in enumerate(lines):
            draw.text((65, 70 + index * 105), line, font=font, fill='black')
        image.save(inputs / name)
    # Intentionally blank negative control: no visual label, since OCR must see no text.
    Image.new('RGB', (1400, 1000), 'white').save(inputs / 'JB05_FICTIONAL_blank.png')
    (inputs / 'JB05_FICTIONAL_corrupt.png').write_bytes(b'JB05 fictional corrupt encoded image control\n')
    for folder in ('income_copy_a', 'income_copy_b'):
        destination = inputs / folder
        destination.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / 'dataset/income_certificate/income_certificate_clear.png',
                        destination / 'JB05_FICTIONAL_duplicate.png')
    print('Prepared labeled fictional image controls; blank explicitly identified by filename/manifest.')


def verify():
    import sys
    sys.path.insert(0, str(ROOT))
    from modules.readiness import render_report
    expected = {
        'single': (1, 1, 1, 4, 25, 25, 'Incomplete'),
        'complete': (4, 4, 4, 4, 100, 100, 'Ready'),
        'missing': (3, 3, 3, 4, 75, 75, 'Incomplete'),
        'unusable': (4, 4, 3, 4, 100, 75, 'Needs Attention'),
        'edge_batch': (9, 4, 3, 4, 100, 75, 'Needs Attention'),
        'checklist_subset': (9, 3, 3, 3, 100, 100, 'Ready'),
        'original_source': (9, 3, 3, 3, 100, 100, 'Ready'),
        'changed_settings': (9, 3, 3, 3, 100, 100, 'Ready'),
    }
    keys = ('submitted_file_count', 'detected_required_type_count', 'usable_required_type_count',
            'required_type_count', 'coverage_percent', 'readiness_percent', 'overall_status')
    for scenario, values in expected.items():
        report = json.loads((HERE / (scenario + '.json')).read_text())
        actual = tuple(report[key] for key in keys)
        assert actual == values, (scenario, actual, values)
        docs = report['documents']
        assert len({doc['id'] for doc in docs}) == len(docs)
        for doc in docs:
            assert doc['ocr'] == doc['ocr_' + doc['ocr_source']]
        dom = (HERE / (scenario + '_dom.txt')).read_text()
        for stage in ('Original', 'Grayscale', 'Denoised', 'Enhanced', 'Thresholded', 'Morphology'):
            expected_stages = sum(d['filename'] != 'JB05_FICTIONAL_corrupt.png' for d in docs)
            assert dom.count('button "Fullscreen: ' + stage + '"') == expected_stages, (scenario, stage)
        if scenario in ('complete', 'missing', 'single'):
            assert all(doc['ocr_original']['status'] == doc['ocr_processed']['status'] == 'ok' for doc in docs)
            manifest = json.loads((ROOT / 'dataset/manifest.json').read_text())
            samples = {Path(s['image_path']).name: s for s in manifest['samples']}
            for doc in docs:
                assert doc['doc_type'] == samples[doc['filename']]['doc_type']
                assert doc['fields'] == samples[doc['filename']]['expected_fields']
        if scenario in ('unusable', 'edge_batch'):
            assert report['missing_types'] == []
            assert report['unusable_types'] == ['identity_proof']
            candidate = next(d for d in docs if d['doc_type'] == 'identity_proof')
            assert candidate['readable'] and not candidate['usable']
            assert candidate['fields']['student_name'] is None
            assert candidate['missing_required_fields'] == ['student_name']
        if scenario == 'edge_batch':
            by_name = {doc['filename']: doc for doc in docs}
            assert by_name['JB05_FICTIONAL_blank.png']['ocr']['status'] == 'no_text'
            assert by_name['JB05_FICTIONAL_corrupt.png']['ocr']['status'] == 'error'
            assert by_name['JB05_FICTIONAL_unknown.png']['doc_type'] == 'unknown'
            assert by_name['JB05_FICTIONAL_unknown.png']['ocr']['status'] == 'ok'
            duplicates = [d for d in docs if d['filename'] == 'JB05_FICTIONAL_duplicate.png']
            assert len(duplicates) == 2 and all(d['doc_type'] == 'income_certificate' for d in duplicates)
            assert duplicates[0]['id'] != duplicates[1]['id']
        if scenario in ('original_source', 'changed_settings'):
            assert all(d['ocr_source'] == 'original' for d in docs)
        if scenario == 'changed_settings':
            assert all(d['processing_parameters']['requested_options']['threshold'] == 'adaptive' for d in docs)
            assert all(d['processing_parameters']['resolved_pipeline']['threshold'] == 'adaptive'
                       for d in docs if d['ocr_original']['status'] != 'error')
        md = HERE / (scenario + '.md')
        if md.exists():
            assert md.read_text() == render_report(report), scenario + ' actual Markdown download differs'
        print('PASS', scenario, actual)
    for kind in ('checklist', 'source', 'settings'):
        dom = (HERE / (kind + '_invalidated_dom.txt')).read_text()
        assert 'Inputs changed. Previous results and downloads were cleared' in dom
        assert 'heading "Readiness analysis"' not in dom
        assert 'Download JSON report' not in dom and 'Download Markdown report' not in dom
        print('PASS', kind, 'settled DOM has no stale report or downloads')
    print('PASS: browser JSON counts, types, expected fields, six stages, source/settings, negative cases and Markdown payloads.')


def inventory():
    paths = [p for p in HERE.rglob('*')
             if p.is_file() and p.name != 'artifact_manifest.json' and '__pycache__' not in p.parts]
    paths += sorted((ROOT / 'outputs/screenshots/JB05').glob('*.jpg'))
    manifest = json.loads((ROOT / 'dataset/manifest.json').read_text())
    paths += [ROOT / 'dataset' / sample['image_path'] for sample in manifest['samples']
              if sample['condition'] == 'clear']
    paths = sorted(set(paths))
    result = [{'path': str(p.relative_to(ROOT)), 'sha256': sha256(p.read_bytes()).hexdigest(),
               'bytes': p.stat().st_size} for p in paths if p.is_file()]
    (HERE / 'artifact_manifest.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    else:
        verify()
    import sys
    sys.stdout.flush()
    inventory()
