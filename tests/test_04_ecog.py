from shutil import copyfile, which

from exportimages import export_plotly

from bidso.utils import replace_underscore
from boavus.main import boavus
from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog, compute_frequency
from boavus.ieeg import preprocessing

from .paths import BIDS_PATH, task_ieeg, elec_ct, FREESURFER_PATH, BOAVUS_PATH, PARAMETERS_PATH, SIMULATE_PATH
from .utils import update_parameters

preprocessing.PARAMETERS['markers'].update({'on': 'move', 'off': 'rest', 'minimalduration': 20})
preprocessing.PARAMETERS.update({'regions': ['ctx-lh-supramarginal', 'ctx-rh-superiorfrontal']})


def test_ieeg_freq_percent():
    ieeg_filename = task_ieeg.get_filename(BIDS_PATH)

    fig = compute_frequency(ieeg_filename)

    output_dir = task_ieeg.get_filename(BOAVUS_PATH).parent
    output_dir.mkdir(exist_ok=True, parents=True)
    export_plotly(fig, output_dir / 'output.png')


