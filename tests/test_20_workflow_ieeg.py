from boavus.workflow.ieeg import workflow_ieeg

from .paths import ANALYSIS_PATH, BIDS_PATH, task_ieeg, elec

d = {
    'read': {
        'conditions': {
            'move': [49, ],
            'rest': [48, ],
            },
        },
    'preprocess': {
        'duration': 2,
        'reref': 'average',
        'offset': False,
        },
    'powerspectrum': {
        'method': 'spectrogram',
        'taper': 'hann',
        'duration': 2,
        },
    'ecog_compare': {
        'frequency': [65, 95],
        'baseline': True,
        'measure': 'zstat',
        'method': '3c',
        }
    }


def test_workflow_ieeg():

    w = workflow_ieeg(ANALYSIS_PATH, d)

    node = w.get_node('input')
    node.inputs.ieeg = str(task_ieeg.get_filename(BIDS_PATH))
    node.inputs.electrodes = str(elec.get_filename(BIDS_PATH))

    w.run()
