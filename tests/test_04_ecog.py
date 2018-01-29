from shutil import copyfile, which

from bidso.utils import replace_underscore
from boavus.main import boavus
from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog

from .paths import BIDS_PATH, task_ieeg, elec_ct, FREESURFER_PATH, BOAVUS_PATH, PARAMETERS_PATH, SIMULATE_PATH
from .utils import update_parameters



def test_ieeg_data():
    assert True
