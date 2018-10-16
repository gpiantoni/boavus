from boavus.workflow.ieeg import workflow_ieeg

from .paths import ANALYSIS_PATH, BIDS_PATH

d = {
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

    r = w.get_node('read')
    r.inputs.ieeg = str(BIDS_PATH / 'sub-bert/ses-day02/ieeg/sub-bert_ses-day02_task-motor_run-1_acq-clinical_ieeg.eeg')
    r.inputs.electrodes = str(BIDS_PATH / 'sub-bert/ses-day02/ieeg/sub-bert_ses-day02_acq-ct_electrodes.tsv')

    w.run()
