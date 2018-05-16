from boavus import boavus

from .paths import BIDS_PATH, PARAMETERS_PATH, ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH
from .utils import update_parameters


def test_ieeg_preprocessing():

    boavus([
        'ieeg',
        'preprocessing',
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--markers_on', 'move',
        '--markers_off', 'rest',
        ])


def test_ieeg_psd():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def test_ieeg_compare_percent():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def notest_ieeg_plotelectrodes_measure(qtbot):
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
        '--log', 'debug',
        ])
