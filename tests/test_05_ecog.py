from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH


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
        '--noparallel',
        ])


def test_ieeg_compare_percent():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def test_ieeg_plotelectrodes_measure(qtbot):

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
        '--acquisition', 'ctprojectedregions',
        '--measure_modality', 'compare',
        '--measure_column', 'measure',
        ])
