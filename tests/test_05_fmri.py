from os import environ
from boavus.main import boavus

from .paths import FEAT_PATH, BOAVUS_PATH, PARAMETERS_PATH
from .utils import update_parameters


def test_fmri_percent():
    if environ.get('FSLDIR') is not None:
        boavus([
            'fmri',
            'compare',
            '--feat_dir',
            str(FEAT_PATH),
            '--output_dir',
            str(BOAVUS_PATH),
            ])

def test_fmri_compare_zstat():

    PARAMETERS_JSON = PARAMETERS_PATH / 'fmri_compare.json'

    boavus([
        'fmri',
        'compare',
        '--output_dir',
        str(BOAVUS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, measure='zstat')

    boavus([
        'fmri',
        'compare',
        '--output_dir',
        str(BOAVUS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])
