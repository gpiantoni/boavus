from os import environ

from boavus.main import main

from .paths import BIDS_PATH, FEAT_PATH


def test_run_feat_dryrun():

    if environ.get('FSLDIR') is not None:
        main([
            'fmri',
            'percent',
            '--bids_dir',
            str(BIDS_PATH),
            '--feat_dir',
            str(FEAT_PATH),
            ])
