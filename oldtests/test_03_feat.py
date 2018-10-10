from boavus.fsl.feat import prepare_design

from .paths import task_anat, task_fmri, ANALYSIS_PATH, BIDS_PATH


def test_main_fsl_feat():

    anat = task_anat.get_filename(BIDS_PATH)
    func = task_fmri.get_filename(BIDS_PATH)

    prepare_design(func, anat, ANALYSIS_PATH)
