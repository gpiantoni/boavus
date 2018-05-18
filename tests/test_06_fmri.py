from boavus import boavus
from bidso.utils import read_tsv, replace_underscore, replace_extension
from numpy.testing import assert_allclose
from os import environ
from pytest import raises

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    task_fmri,
                    )
from .utils import compute_md5


output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')
output_tsv = replace_extension(output_nii, '.tsv')


def test_fmri_compare_error():

    with raises(ValueError):
        boavus([
            'fmri',
            'compare',
            '--analysis_dir', str(ANALYSIS_PATH),
            '--measure', 'xxx',
            ])


def test_fmri_compare_zstat():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--measure', 'zstat',
        ])

    assert compute_md5(output_nii) == '82dccb2547855d0e883be67e3bf19d86'


def test_fmri_compare_normalize():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--normalize_to_mean',
        ])

    assert compute_md5(output_nii) == '6876c3692c5e1bb1596b1f07c7d2455f'


def test_fmri_compare():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    assert compute_md5(output_nii) == '1d64d5bf6f83ba5f9f29c2459e98c307'


def test_fmri_at_electrodes_sphere():

    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--distance', 'sphere',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 61441.38281250001)


def test_fmri_at_electrodes_inverse():

    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--distance', 'inverse',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 60590.677291881606)


def test_fmri_at_electrodes_approach():

    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--approach',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 61441.387, atol=.5)  # additional tolerance


def test_fmri_at_electrodes_gaussian():
    # run default as the last one, so that it's used by other functions

    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 59382.12053669494)
