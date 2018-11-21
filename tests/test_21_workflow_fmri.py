from boavus.workflow.fmri import workflow_fmri

from .paths import (ANALYSIS_PATH,
                    BIDS_PATH,
                    FREESURFER_PATH,
                    task_anat,
                    task_fmri,
                    elec,
                    )


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
    "upsample": False,
    "graymatter": True,
    }


def test_workflow_fmri():

    w = workflow_fmri(ANALYSIS_PATH, d, FREESURFER_PATH)

    node = w.get_node('input')
    node.inputs.subject = 'sub-delft'
    node.inputs.T1w = str(task_anat.get_filename(BIDS_PATH))
    node.inputs.bold = str(task_fmri.get_filename(BIDS_PATH))
    node.inputs.electrodes = str(elec.get_filename(BIDS_PATH))

    w.run()
