from os import environ

from bidso import Task
from bidso.utils import bids_mkdir
from boavus.fsl.feat import run_feat

from .paths import BIDS_PATH, FEAT_PATH
from .test_01_simulate import task_fmri


def test_run_feat_dryrun():
    modality_path = bids_mkdir(BIDS_PATH, task_fmri)
    fmri_file = modality_path / f'sub-{task_fmri.subject}_ses-{task_fmri.session}_task-block_run-00_bold.nii.gz'

    t = Task(fmri_file)
    if environ.get('FSLDIR') is not None:
        run_feat(FEAT_PATH, t, dry_run=False)
