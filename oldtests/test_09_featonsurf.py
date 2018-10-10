from boavus import boavus

from .paths import ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH


def test_main_fsl_feattosurf(qtbot):

    boavus([
        'fsl',
        'feat_on_surf',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--output_dir', str(BOAVUS_PATH),
        '--log', 'debug',
        ])
