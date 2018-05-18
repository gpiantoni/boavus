from boavus import boavus
from bidso.utils import replace_underscore
from numpy.testing import assert_allclose
from pickle import load

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    task_ieeg,
                    )

output_data = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                 'ieeg_move.pkl')
output_freq = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                 'ieeg_freqmove.pkl')


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


def test_ieeg_psd():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    with output_freq.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 53484510.01552996)
