from shutil import copyfile

from boavus.main import boavus
from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog

from .paths import BIDS_PATH, task_ieeg, elec_ct, FREESURFER_PATH, BOAVUS_PATH

from bidso.utils import replace_underscore


ieeg_file = task_ieeg.get_filename(BIDS_PATH)


def test_ieeg_electrodes():
    # TODO: this function should project elec onto surface

    elec_ct_file = elec_ct.get_filename(BIDS_PATH)
    elec_ct.acquisition = 'ctprojectedregions'
    elec_regions_file = elec_ct.get_filename(BIDS_PATH)

    copyfile(elec_ct_file, elec_regions_file)
    copyfile(replace_underscore(elec_ct_file, 'coordframe.json'),
             replace_underscore(elec_regions_file, 'coordframe.json'))


def test_ieeg_dataset():

    d = Dataset(ieeg_file, '*ct')
    data = d.read_data(begsam=10, endsam=20)
    events = d.read_events()


def test_ieeg_preprocessing():

    preprocess_ecog(ieeg_file)


def test_ieeg_plotelectrodes(qtbot):

    boavus([
        'ieeg',
        'plot_electrodes',
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        ])
