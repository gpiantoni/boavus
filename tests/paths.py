from pathlib import Path
from bidso import file_Core


TEST_PATH = Path(__file__).resolve().parent
DATA_PATH = TEST_PATH / 'data'

BIDS_PATH = DATA_PATH / 'bids'
FREESURFER_PATH = DATA_PATH / 'freesurfer'

ANALYSIS_PATH = DATA_PATH / 'analysis'
ANALYSIS_PATH.mkdir(parents=True, exist_ok=True)

subject = 'delft'
task_ieeg = file_Core(
    subject=subject,
    session='UMCUECOGday01',
    modality='ieeg',
    task='motorHandLeft',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )
task_fmri = file_Core(
    subject=subject,
    session='UMCU3Tdaym13',
    modality='bold',
    task='motorHandLeft',
    run='1',
    extension='.nii.gz',
    )
task_anat = file_Core(
    subject=subject,
    session='UMCU3Tdaym13',
    modality='T1w',
    acquisition='wholebrain',
    extension='.nii.gz',
    )
elec = file_Core(
    subject=subject,
    session='UMCUECOGday01',
    modality='electrodes',
    acquisition='clinical',
    extension='.tsv',
    )


parameters = {
    'corr': {
        'pvalue': 0.05,
        },
    'fmri': {
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
        },
    'ieeg': {
        'read': {
            'conditions': {
                'move': [49, ],
                'rest': [48, ],
                },
            'minimalduration': 1,
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
    }
