from os import environ
from boavus.main import boavus

from .paths import PARAMETERS_PATH, BIDS_PATH, ANALYSIS_PATH
from .utils import update_parameters


def test_fmri_percent():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        ])


def test_fmri_compare_zstat():

    if environ.get('FSLDIR') is None:
        return

    PARAMETERS_JSON = PARAMETERS_PATH / 'fmri_compare.json'

    boavus([
        'fmri',
        'compare',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, measure='zstat')

    boavus([
        'fmri',
        'compare',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])


def test_fmri_at_electrodes():

    if environ.get('FSLDIR') is None:
        return

    PARAMETERS_JSON = PARAMETERS_PATH / 'fmri_atelectrodes.json'

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, kernels=[5, ], parallel=False)
    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, distance='inverse')
    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, distance='sphere')
    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])
