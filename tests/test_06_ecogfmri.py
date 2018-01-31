from os import environ
from boavus.main import boavus

from .paths import FREESURFER_PATH, BOAVUS_PATH, FEAT_PATH, BIDS_PATH, PARAMETERS_PATH
from .utils import update_parameters

PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_corrfmri.json'


def test_ieeg_corrfmri_parameters():

    boavus([
        'ieeg',
        'corrfmri',
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])


def test_ieeg_corrfmri_gaussian():
    if environ.get('FSLDIR') is None:
        return

    update_parameters(PARAMETERS_JSON, kernels=[5, ], parallel=False)

    boavus([
        'ieeg',
        'corrfmri',
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


def test_ieeg_corrfmri_sphere():
    if environ.get('FSLDIR') is None:
        return

    update_parameters(PARAMETERS_JSON, distance='sphere')

    boavus([
        'ieeg',
        'corrfmri',
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


def test_ieeg_corrfmri_inverse():
    if environ.get('FSLDIR') is None:
        return

    update_parameters(PARAMETERS_JSON, distance='inverse')

    boavus([
        'ieeg',
        'corrfmri',
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
