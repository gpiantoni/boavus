from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog
from bidso.utils import bids_mkdir

from .paths import BIDS_PATH, FEAT_PATH
from .test_01_simulate import task_ieeg


def test_ieeg_dataset():
    modality_path = bids_mkdir(BIDS_PATH, task_ieeg)
    ieeg_file = modality_path / f'sub-{task_ieeg.subject}_ses-{task_ieeg.session}_task-block_run-00_ieeg.bin'
    d = Dataset(ieeg_file)
    data = d.read_data(begsam=10, endsam=20)
    events = d.read_events()


def test_ieeg_preprocessing():

    modality_path = bids_mkdir(BIDS_PATH, task_ieeg)
    ieeg_file = modality_path / f'sub-{task_ieeg.subject}_ses-{task_ieeg.session}_task-block_run-00_ieeg.bin'
    preprocess_ecog(ieeg_file)
