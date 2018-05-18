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


def test_ieeg_compare_percent():

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
