from functools import namedtuple
from nibabel import load as nload
from nibabel import Nifti1Image

from bidso import Electrodes
from bidso.simulate.ieeg import (create_electrodes,
                                 create_channels,
                                 create_ieeg_info,
                                 create_ieeg_data,
                                 )
from bidso.simulate.fmri import create_bold, create_events
from bidso.utils import add_underscore, replace_underscore, replace_extension, bids_mkdir

from .paths import BIDS_PATH, FREESURFER_PATH

subject = 'bert'
task_fmri = namedtuple('BIDS', ('subject', 'session', 'modality'))(subject, 'day01', 'func')
task_anat = namedtuple('BIDS', ('subject', 'session', 'modality'))(subject, 'day01', 'anat')
task_ieeg = namedtuple('BIDS', ('subject', 'session', 'modality'))(subject, 'day02', 'ieeg')

T1_path = FREESURFER_PATH / 'bert/mri/T1.mgz'


def test_simulate_root():

    participants_tsv = BIDS_PATH / 'participants.tsv'
    with participants_tsv.open('w') as f:
        f.write('participant_id\tage\tsex\n')

        f.write(f'{subject}\t30\tF\n')


def test_simulate_ieeg():
    modality_path = bids_mkdir(BIDS_PATH, task_ieeg)

    sess_path = BIDS_PATH / f'sub-{subject}/ses-{task_ieeg.session}'

    elec_file = sess_path / f'sub-{subject}_ses-{task_ieeg.session}_acq-ct_electrodes.tsv'
    create_electrodes(elec_file)

    base_file = modality_path / f'sub-{subject}_ses-{task_ieeg.session}_task-block_run-00'
    create_events(add_underscore(base_file, 'events.tsv'))

    ieeg_file = add_underscore(base_file, task_ieeg.modality + '.bin')
    elec = Electrodes(elec_file)
    n_elec = len(elec.electrodes.tsv)
    create_ieeg_data(ieeg_file, n_elec)

    create_ieeg_info(replace_extension(ieeg_file, '.json'))
    create_channels(replace_underscore(ieeg_file, 'channels.tsv'), elec)


def test_simulate_anat():
    mri = nload(str(T1_path))
    x = mri.get_data()
    nifti = Nifti1Image(x, mri.affine)

    anat_path = bids_mkdir(BIDS_PATH, task_anat)
    nifti.to_filename(str(anat_path / f'sub-{subject}_T1w.nii.gz'))


def test_simulate_fmri():
    modality_path = bids_mkdir(BIDS_PATH, task_fmri)
    fmri_file = modality_path / f'sub-{subject}_ses-{task_fmri.session}_task-block_run-00'
    mri = nload(str(T1_path))

    create_bold(mri, add_underscore(fmri_file, 'bold.nii.gz'))
    create_events(add_underscore(fmri_file, 'events.tsv'))
