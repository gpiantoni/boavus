from shutil import copyfile, which

from bidso.utils import replace_underscore
from boavus.main import boavus
from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog

from .paths import BIDS_PATH, task_ieeg, elec_ct, FREESURFER_PATH, BOAVUS_PATH, PARAMETERS_PATH, SIMULATE_PATH
from .utils import update_parameters


ieeg_file = task_ieeg.get_filename(BIDS_PATH)


def test_ieeg_projectelectrodes():
    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_projectelectrodes.json'

    boavus([
        'ieeg',
        'project_electrodes',
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, acquisition=['ct', ])

    if which('matlab') is not None:

        # requires matlab
        boavus([
            'ieeg',
            'project_electrodes',
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            '--bids_dir',
            str(BIDS_PATH),
            '-p',
            str(PARAMETERS_JSON),
            ])

    else:

        elec_ct_file = elec_ct.get_filename(BIDS_PATH)
        elec_ct.acquisition = 'ctprojected'
        elec_projected_file = elec_ct.get_filename(BIDS_PATH)

        # copy previous coordframe.json
        copyfile(replace_underscore(elec_ct_file, 'coordframe.json'),
                 replace_underscore(elec_projected_file, 'coordframe.json'))

        # copy precomputed regions
        copyfile(SIMULATE_PATH / elec_projected_file.name, elec_projected_file)


def test_ieeg_dataset():

    d = Dataset(ieeg_file, '*ct')
    data = d.read_data(begsam=10, endsam=20)
    events = d.read_events()


def test_ieeg_preprocessing():

    preprocess_ecog(ieeg_file)


def test_ieeg_plotelectrodes(qtbot):

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_plotelectrodes.json'

    boavus([
        'ieeg',
        'project_electrodes',
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, acquisition='ctprojected')

    boavus([
        'ieeg',
        'plot_electrodes',
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])
