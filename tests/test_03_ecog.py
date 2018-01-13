from boavus.ieeg.dataset import Dataset
from bidso.utils import bids_mkdir

from .paths import BIDS_PATH, FEAT_PATH
from .test_01_simulate import task_ieeg


def test_ieeg_dataset():
    modality_path = bids_mkdir(BIDS_PATH, task_ieeg)
    ieeg_file = modality_path / f'sub-{task_ieeg.subject}_ses-{task_ieeg.session}_task-block_run-00_ieeg.bin'
    d = Dataset(ieeg_file)
