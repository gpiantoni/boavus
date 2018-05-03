from boavus import boavus

from .paths import BOAVUS_PATH, ANALYSIS_PATH, BIDS_PATH, PARAMETERS_PATH
from .utils import update_parameters


def test_ieeg_corrfmri():

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_corrfmri.json'
    boavus([
        'ieeg',
        'corrfmri',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON,
                      acquisition='ctprojectedregions',
                      regions=['ctx-lh-supramarginal', ])
    boavus([
        'ieeg',
        'corrfmri',
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])
