from boavus.ieeg.corr_fmri import _main_to_elec
from bidso.utils import replace_extension

from .paths import FREESURFER_PATH, BOAVUS_PATH, task_ieeg, task_fmri, FEAT_PATH, BIDS_PATH


def test_corr_ecogfmri():
    feat_path = replace_extension(task_fmri.get_filename(FEAT_PATH), '.feat')
    ieeg_file = task_ieeg.get_filename(BIDS_PATH)

    KERNEL_SIZES = [5, ]

    output = _main_to_elec(ieeg_file, feat_path, FREESURFER_PATH, BOAVUS_PATH, KERNEL_SIZES, to_plot=False)
    assert output[0] < 0.01
