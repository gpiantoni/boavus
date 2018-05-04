from json import dump
from bidso.simulate import simulate_bold, simulate_ieeg, simulate_electrodes, simulate_anat

from .paths import BIDS_PATH, T1_PATH, task_ieeg, task_fmri, task_anat, elec_ct


def test_simulate_root():

    participants_tsv = BIDS_PATH / 'participants.tsv'
    with participants_tsv.open('w') as f:
        f.write('participant_id\tage\tsex\n')

        f.write(f'{task_ieeg.subject}\t30\tF\n')

    d = {
        "Name": "Dataset with simulated data",
        "BIDSVersion": "1.1",
        "Authors": ["Giovanni Piantoni", ],
        }

    with (BIDS_PATH / 'dataset_description.json').open('w') as f:
        dump(d, f, ensure_ascii=False, indent=' ')


def test_simulate_ieeg():
    elec = simulate_electrodes(BIDS_PATH, elec_ct)
    simulate_ieeg(BIDS_PATH, task_ieeg, elec)


def test_simulate_anat():
    simulate_anat(BIDS_PATH, task_anat, T1_PATH)


def test_simulate_fmri():
    simulate_bold(BIDS_PATH, task_fmri, T1_PATH)
