from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog

from .paths import BIDS_PATH
from .test_01_simulate import task_ieeg

ieeg_file = task_ieeg.get_filename(BIDS_PATH)


def test_ieeg_dataset():

    d = Dataset(ieeg_file)
    data = d.read_data(begsam=10, endsam=20)
    events = d.read_events()


def test_ieeg_preprocessing():

    preprocess_ecog(ieeg_file)
