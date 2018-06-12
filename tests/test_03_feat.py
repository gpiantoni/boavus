from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH, FREESURFER_PATH


def notest_main_fsl_feat():

    boavus([
        'fsl',
        'feat',
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def notest_main_fsl_coreg():

    boavus([
        'fsl',
        'coreg',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--log', 'debug',
        ])
