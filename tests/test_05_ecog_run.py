from boavus import boavus
from numpy.testing import assert_allclose
from pickle import load

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    task_ieeg,
                    )

task_ieeg.task += 'move'
task_ieeg.extension = '.pkl'
output_data = task_ieeg.get_filename(ANALYSIS_PATH)
task_ieeg.modality += 'psd'
output_freq = task_ieeg.get_filename(ANALYSIS_PATH, 'ieeg')


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

    with output_data.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 13963593.33152158)


def test_ieeg_psd_spectrogram():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        ])

    with output_freq.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 53484510.01552996)


def test_ieeg_psd_dh2012():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--noparallel',
        '--log', 'info',
        '--method', 'dh2012',
        ])

    with output_freq.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 9024920.18128)


def test_ieeg_psd_parallel():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        ])

    with output_freq.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 53484510.01552996)
