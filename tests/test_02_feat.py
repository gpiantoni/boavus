from os import environ

from boavus.main import main

from .paths import BIDS_PATH, FEAT_PATH


def test_main_fsl_feat():

    if environ.get('FSLDIR') is not None:
        main([
            'fsl',
            'feat',
            '--bids_dir',
            str(BIDS_PATH),
            '--feat_dir',
            str(FEAT_PATH),
            ])
