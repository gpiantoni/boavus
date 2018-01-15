from boavus.ieeg.corr_fmri import _main
from bidso.utils import bids_mkdir

from .paths import BIDS_PATH, FEAT_PATH, FREESURFER_PATH, DERIVATIVES_PATH
from .test_01_simulate import task_ieeg
from .test_09_feat_finished import feat_path

modality_path = bids_mkdir(BIDS_PATH, task_ieeg)
ieeg_file = modality_path / f'sub-{task_ieeg.subject}_ses-{task_ieeg.session}_task-block_run-00_ieeg.bin'


def test_corr_ecogfmri():
    _main(ieeg_file, feat_path, FREESURFER_PATH, DERIVATIVES_PATH, [5, ])
