from shutil import rmtree

from boavus.workflow.ieeg import workflow_ieeg
from nipype import config, logging

from .paths import (ANALYSIS_PATH,
                    BIDS_PATH,
                    task_ieeg,
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


def test_workflow_ieeg():

    w = workflow_ieeg(parameters['ieeg'])
    w.base_dir = str(ANALYSIS_PATH)

    node = w.get_node('input')
    node.inputs.ieeg = str(task_ieeg.get_filename(BIDS_PATH))
    node.inputs.electrodes = str(elec.get_filename(BIDS_PATH))

    w.write_graph(
        graph2use='flat',
        )

    rmtree(LOG_PATH, ignore_errors=True)
    LOG_PATH.mkdir()
    logging.update_logging(config)

    w.run()
