from boavus import boavus

from .paths import BOAVUS_PATH, ANALYSIS_PATH, BIDS_PATH


def test_ieeg_corrfmri():

    boavus([
        'ieeg',
        'corrfmri',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--output_dir', str(BOAVUS_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--log', 'debug',
        '--acquisition', 'ctprojectedregions',
        '--plot',
        ])
