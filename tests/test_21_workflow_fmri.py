from boavus.workflow.fmri import workflow_fmri
from nipype import config

from .paths import (ANALYSIS_PATH,
                    BIDS_PATH,
                    FREESURFER_PATH,
                    task_anat,
                    task_fmri,
                    elec,
                    parameters,
                    )


LOG_PATH = ANALYSIS_PATH / 'log'
config.update_config({
    'logging': {
        'log_directory': LOG_PATH,
        'log_to_file': True,
        },
    'execution': {
        'crashdump_dir': LOG_PATH,
        'keep_inputs': 'false',
        'remove_unnecessary_outputs': 'false',
        },
    })


def test_workflow_fmri():

    w = workflow_fmri(parameters['fmri'], FREESURFER_PATH)
    w.base_dir = str(ANALYSIS_PATH)

    node = w.get_node('input')
    node.inputs.subject = 'sub-delft'
    node.inputs.T1w = str(task_anat.get_filename(BIDS_PATH))
    node.inputs.bold = str(task_fmri.get_filename(BIDS_PATH))
    node.inputs.electrodes = str(elec.get_filename(BIDS_PATH))

    w.run()
