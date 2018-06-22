from json import dump
from bidso.simulate import simulate_bold, simulate_ieeg, simulate_electrodes, simulate_anat
from boavus.prf.core import simulate_prf
from os import environ
from pathlib import Path
from shutil import copytree

from .paths import (BIDS_PATH,
                    T1_PATH,
                    task_ieeg,
                    task_fmri,
                    task_anat,
                    task_prf,
                    elec_ct,
                    FREESURFER_PATH,
                    )


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
    freesurfer_bert = Path(environ['FREESURFER_HOME']) / 'subjects' / 'bert'

    FREESURFER_PATH.mkdir(parents=True, exist_ok=True)
    copytree(freesurfer_bert, FREESURFER_PATH / 'sub-bert')

    simulate_anat(BIDS_PATH, task_anat, T1_PATH)


def test_simulate_fmri():
    simulate_bold(BIDS_PATH, task_fmri, T1_PATH)


def test_simulate_prf():
    prf_file = task_prf.get_filename(BIDS_PATH)
    simulate_prf(prf_file)
