from os import environ

from boavus.main import boavus

from .paths import BIDS_PATH, FEAT_PATH, FREESURFER_PATH


def test_main_fsl_feat():

    if environ.get('FSLDIR') is not None:
        boavus([
            'fsl',
            'feat',
            '--bids_dir',
            str(BIDS_PATH),
            '--feat_dir',
            str(FEAT_PATH),
            ])


def test_main_fsl_coreg():

    if environ.get('FSLDIR') is not None:
        boavus([
            'fsl',
            'coreg',
            '--feat_dir',
            str(FEAT_PATH),
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            ])
