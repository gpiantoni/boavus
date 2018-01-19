from os import environ

from bidso import Task
from boavus.fsl.feat import run_feat

from .paths import BIDS_PATH, FEAT_PATH
from .test_01_simulate import task_fmri


def test_run_feat_dryrun():
    t = Task(task_fmri.get_filename(BIDS_PATH))

    if environ.get('FSLDIR') is not None:
        run_feat(FEAT_PATH, t, dry_run=False)
