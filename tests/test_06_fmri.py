from os import environ
from boavus import boavus
from bidso.utils import read_tsv, replace_underscore, replace_extension

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    task_fmri,
                    )
from .utils import compute_md5


output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')
output_tsv = replace_extension(output_nii, '.tsv')


def test_fmri_percent():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    assert compute_md5(output_nii) == '1d64d5bf6f83ba5f9f29c2459e98c307'


def test_fmri_at_electrodes_gaussian():

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
        ])

    tsv = read_tsv(output_tsv)
    assert [x['7'] for x in tsv if x['channel'] == 'grid01'][0] == '59382.12053669494'


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

    tsv = read_tsv(output_tsv)
    assert [x['7'] for x in tsv if x['channel'] == 'grid01'][0] == '61441.38281250001'


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

    tsv = read_tsv(output_tsv)
    assert [x['7'] for x in tsv if x['channel'] == 'grid01'][0] == '60590.677291881606'


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

    tsv = read_tsv(output_tsv)
    assert [x['7'] for x in tsv if x['channel'] == 'grid01'][0] == '61441.387'
