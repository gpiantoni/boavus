from os import environ
from boavus.main import boavus

from .paths import FREESURFER_PATH, BOAVUS_PATH, ANALYSIS_PATH, BIDS_PATH, PARAMETERS_PATH
from .utils import update_parameters

PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_corrfmri.json'


def test_ieeg_corrfmri_parameters():

    boavus([
        'ieeg',
        'corrfmri',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])
