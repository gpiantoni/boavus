from os import environ

from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH, FREESURFER_PATH, BOAVUS_PATH


def test_main_fsl_feat():

    if environ.get('FSLDIR') is not None:
        boavus([
            'fsl',
            'feat',
            '--bids_dir',
            str(BIDS_PATH),
            '--analysis_dir',
            str(ANALYSIS_PATH),
            '--log',
            'debug',
            ])


def test_main_fsl_coreg():

    if environ.get('FSLDIR') is not None:
        boavus([
            'fsl',
            'coreg',
            '--analysis_dir',
            str(ANALYSIS_PATH),
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            '--log',
            'debug',
            ])


def test_main_fsl_feattosurf(qtbot):

    if environ.get('FSLDIR') is not None:
        boavus([
            'fsl',
            'feat_on_surf',
            '--analysis_dir',
            str(ANALYSIS_PATH),
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            '--output_dir',
            str(BOAVUS_PATH),
            '--log',
            'debug',
            ])
