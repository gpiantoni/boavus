from os import environ
from boavus.main import boavus

from .paths import FREESURFER_PATH, BOAVUS_PATH, FEAT_PATH, BIDS_PATH, PARAMETERS_PATH
from .utils import update_parameters

PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_corrfmri.json'


def test_main_ieeg_corrfmri_parameters():
    assert not PARAMETERS_JSON.exists()

    boavus([
        'ieeg',
        'corrfmri',
        '--feat_dir',
        str(FEAT_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, kernel=[5, ])


def test_main_ieeg_corrfmri():
    if environ.get('FSLDIR') is not None:
        boavus([
            'ieeg',
            'corrfmri',
            '--feat_dir',
            str(FEAT_PATH),
            '--output_dir',
            str(BOAVUS_PATH),
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            '--bids_dir',
            str(BIDS_PATH),
            '--parameters',
            str(PARAMETERS_JSON),
            '--log',
            'debug',
            ])
