from boavus.main import boavus

from .paths import BIDS_PATH, PARAMETERS_PATH, ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH
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
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, **PARAMETERS)

    boavus([
        'ieeg',
        'preprocessing',
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

def test_ieeg_psd():
    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_psd.json'

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, parallel=False)

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])


def test_ieeg_compare_percent():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        ])


def test_ieeg_plotelectrodes_measure(qtbot):
    # follows up on test_04_electrodes.py/test_ieeg_plotelectrodes

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_plotelectrodes.json'
    update_parameters(
        PARAMETERS_JSON,
        acquisition='ctprojectedregions',
        measure=dict(
            modality='compare',
            column='measure',
            ))

    boavus([
        'ieeg',
        'plot_electrodes',
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
        ])
