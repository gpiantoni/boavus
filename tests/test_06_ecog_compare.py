from boavus import boavus
from bidso.utils import read_tsv, replace_underscore
from numpy.testing import assert_allclose

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    BOAVUS_PATH,
                    task_ieeg,
                    )

output_tsv = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                'ieeg_compare.tsv')

def test_ieeg_compare_diff():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--measure', 'diff',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    print(v)
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
    print(v)
    assert_allclose(v, 22.123573)


def test_ieeg_compare_dorat():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--measure', 'dora_t',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    print(v)
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
    print(v)
    assert_allclose(v, 0.17740472587278314)


def test_ieeg_compare():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    print(v)
    assert_allclose(v, 0.9309301804179754)


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
        '--measure_modality', 'ieeg_compare',
        '--measure_column', 'measure',
        ])
