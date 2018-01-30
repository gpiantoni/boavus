from boavus.main import boavus

from .paths import BIDS_PATH, BOAVUS_PATH, PARAMETERS_PATH
from .utils import update_parameters


PARAMETERS = {
    'markers': {
        'on': 'move',
        'off': 'rest',
        'minimalduration': 20
        },
    'regions': [
        'ctx-lh-supramarginal',
        'ctx-rh-superiorfrontal',
        ],
    }


def test_ieeg_preprocessing():

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_preprocessing.json'

    boavus([
        'ieeg',
        'preprocessing',
        '--bids_dir',
        str(BIDS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, **PARAMETERS)

    boavus([
        'ieeg',
        'preprocessing',
        '--bids_dir',
        str(BIDS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])


def test_ieeg_psd():

    boavus([
        'ieeg',
        'psd',
        '--output_dir',
        str(BOAVUS_PATH),
        ])
