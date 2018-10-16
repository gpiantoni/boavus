from pathlib import Path
from bidso import file_Core


TEST_PATH = Path(__file__).resolve().parent
DATA_PATH = TEST_PATH / 'data'

BIDS_PATH = DATA_PATH / 'bids'
BIDS_PATH.mkdir(parents=True, exist_ok=True)
FREESURFER_PATH = DATA_PATH / 'freesurfer'
FREESURFER_PATH.mkdir(parents=True, exist_ok=True)

ANALYSIS_PATH = DATA_PATH / 'analysis'
ANALYSIS_PATH.mkdir(parents=True, exist_ok=True)

subject = 'bert'
task_ieeg = file_Core(
    subject=subject,
    session='day02',
    modality='ieeg',
    task='motor',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )
task_prf = file_Core(
    subject=subject,
    session='day04',
    modality='ieeg',
    task='bairprf',
    run='1',
    acquisition='clinical',
    extension='.eeg',
    )
task_fmri = file_Core(
    subject=subject,
    session='day01',
    modality='bold',
    task='motor',
    run='1',
    extension='.nii.gz',
    )
task_anat = file_Core(
    subject=subject,
    session='day01',
    modality='T1w',
    acquisition='wholebrain',
    extension='.nii.gz',
    )
elec_ct = file_Core(
    subject=subject,
    session='day02',
    modality='electrodes',
    acquisition='ct',
    extension='.tsv',
    )


COND = {
    'move': 'move',
    'rest': 'rest',
    }
MINIMALDURATION = 15
