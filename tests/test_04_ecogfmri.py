from boavus.ieeg.corr_fmri import _main_to_elec, _read_fmri_val, _read_elec, _read_ecog_val
from os import environ
from bidso.utils import bids_mkdir
from boavus.ieeg import Dataset

from wonambi.attr import Freesurfer

from .paths import BIDS_PATH, FEAT_PATH, FREESURFER_PATH, DERIVATIVES_PATH
from .test_01_simulate import task_ieeg
from .test_09_feat_finished import feat_path

modality_path = bids_mkdir(BIDS_PATH, task_ieeg)
ieeg_file = modality_path / f'sub-{task_ieeg.subject}_ses-{task_ieeg.session}_task-block_run-00_ieeg.bin'


def test_corr_ecogfmri_1():
    output_path = DERIVATIVES_PATH / 'corr_fmri_ecog'
    output_path.mkdir(exist_ok=True)

    img = _read_fmri_val(feat_path, output_path, to_plot=True)
    mri = img.get_data()
    print('fmri done')


def test_corr_ecogfmri_2():

    if environ.get('TRAVIS') is not None:
        pattern = '*'  # in TRAVIS
    else:
        pattern = '*fridge'
    print(pattern)
    d = Dataset(ieeg_file, pattern)

    freesurfer_path = FREESURFER_PATH / d.subject
    fs = Freesurfer(freesurfer_path)
    ecog_val, labels = _read_ecog_val(d)
    elec = _read_elec(d)
    elec = elec(lambda x: x.label in labels)
    print(ecog_val)
