from copy import deepcopy
from boavus import boavus
from bidso.utils import read_tsv
from numpy.testing import assert_allclose

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    BOAVUS_PATH,
                    task_ieeg,
                    )

task_compare = deepcopy(task_ieeg)
task_compare.modality = 'ieegprocpsdcompare'
task_compare.extension = '.tsv'
task_compare.task = 'block'
output_tsv = task_compare.get_filename(ANALYSIS_PATH, 'ieeg')


def test_ieeg_compare_diff():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--measure', 'diff',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 1.551890365962599)


def test_ieeg_compare_percent():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--measure', 'percent',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 22.123573)


def test_ieeg_compare_dh2012t():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--measure', 'dh2012_t',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, -62.086533)


def test_ieeg_compare_baseline():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--baseline',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 0.17740472587278314)


def test_ieeg_compare_method():

    METHODS = {
        '1a': 1.0,
        '1b': 1.0,
        '1c': 1.0,
        '1d': 1.0,
        '2a': 0.9786426425543525,
        '2b': 0.9848535661914938,
        '2c': 0.9861305558261255,
        '2d': 0.9881910378725067,
        '3a': 0.9021175058094721,
        '3b': 0.9309301804179754,
        '3c': 0.9389189728427727,
        }

    for method, result in METHODS.items():

        boavus([
            'ieeg',
            'compare',
            '--analysis_dir', str(ANALYSIS_PATH),
            '--log', 'debug',
            '--method', method,
            ])
        print(method)

        v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
        assert_allclose(v, result)


def test_ieeg_compare():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 0.9309301804179754)


def test_ieeg_plotelectrodes_measure(qtbot):

    boavus([
        'electrodes',
        'plot',
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
        '--measure_modality', 'ieeg_compare',
        '--measure_column', 'measure',
        ])
