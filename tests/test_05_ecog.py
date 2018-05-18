from boavus import boavus
from bidso.utils import read_tsv, replace_underscore, replace_extension

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    BOAVUS_PATH,
                    task_ieeg,
                    )
from .utils import compute_md5

output_data = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                 'ieeg_move.pkl')
output_freq = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                 'ieeg_freqmove.pkl')
output_tsv = replace_underscore(task_ieeg.get_filename(ANALYSIS_PATH),
                                'ieeg_compare.tsv')


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

    assert compute_md5(output_data) == 'c595d44bdc2ee5705a349ca89b0b1372'


def test_ieeg_psd():

    boavus([
        'ieeg',
        'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        ])

    assert compute_md5(output_freq) == '4b0c35556789d6956e4337824036621b'


def test_ieeg_compare_percent():

    boavus([
        'ieeg',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    tsv = read_tsv(output_tsv)
    assert [x['measure'] for x in tsv if x['channel'] == 'grid01'][0] == '0.9277588988518676'


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
