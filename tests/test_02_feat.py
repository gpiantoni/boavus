from os import environ

from boavus.fsl.feat import run_fsl_feat

from .paths import BIDS_PATH, FEAT_PATH


def test_run_feat_dryrun():

    if environ.get('FSLDIR') is not None:
        run_fsl_feat(BIDS_PATH, FEAT_PATH)
