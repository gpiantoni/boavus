from boavus.workflow.fmri import workflow_fmri

from .paths import ANALYSIS_PATH, BIDS_PATH, FREESURFER_PATH

d = {
    "fmri_compare": {
        "measure": "zstat",
        "normalize_to_mean": True
        },
    "at_elec": {
        "distance": "gaussian",
        "kernel_start": 3,
        "kernel_end": 10,
        "kernel_step": 0.5
        },
    }

def test_workflow_ieeg():

    w = workflow_fmri(ANALYSIS_PATH, d, False, True, FREESURFER_PATH)

    node = w.get_node('freesurfer')
    node.inputs.subject_id = 'bert'
    node.inputs.T1_files = str(BIDS_PATH / 'sub-bert/ses-day01/anat/sub-bert_ses-day01_acq-wholebrain_T1w.nii.gz')

    node = w.get_node('bet')
    node.inputs.in_file = str(BIDS_PATH / 'sub-bert/ses-day01/anat/sub-bert_ses-day01_acq-wholebrain_T1w.nii.gz')

    node = w.get_node('feat_design')
    node.inputs.func = str(BIDS_PATH / 'sub-bert/ses-day01/func/sub-bert_ses-day01_task-motor_run-1_bold.nii.gz')

    node = w.get_node('at_elec')
    node.inputs.electrodes = str(BIDS_PATH / 'sub-bert/ses-day02/ieeg/sub-bert_ses-day02_acq-ct_electrodes.tsv')

    w.run()
