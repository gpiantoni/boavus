from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH


def test_main_fsl_feat():

    boavus([
        'fsl',
        'feat',
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def test_main_fsl_coreg():

    boavus([
        'fsl',
        'coreg',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--log', 'debug',
        ])


def test_main_fsl_feattosurf(qtbot):

    boavus([
        'fsl',
        'feat_on_surf',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--output_dir', str(BOAVUS_PATH),
        '--log', 'debug',
        ])
