from exportimages import export_plotly

from boavus.ieeg.psd import compute_frequency
from boavus.ieeg import psd
from boavus.main import boavus

from .paths import BIDS_PATH, task_ieeg, elec_ct, FREESURFER_PATH, BOAVUS_PATH, PARAMETERS_PATH, SIMULATE_PATH
from .utils import update_parameters


psd.PARAMETERS['markers'].update({'on': 'move', 'off': 'rest', 'minimalduration': 20})
psd.PARAMETERS.update({'regions': ['ctx-lh-supramarginal', 'ctx-rh-superiorfrontal']})


def test_ieeg_freq_percent():
    ieeg_filename = task_ieeg.get_filename(BIDS_PATH)

    fig = compute_frequency(ieeg_filename)

    output_dir = task_ieeg.get_filename(BOAVUS_PATH).parent
    output_dir.mkdir(exist_ok=True, parents=True)
    export_plotly(fig[0][0], output_dir / 'output.png')


def test_ieeg_psd():

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_psd.json'

    boavus([
        'ieeg',
        'psd',
        '--bids_dir',
        str(BIDS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])

    update_parameters(PARAMETERS_JSON, **psd.PARAMETERS)

    boavus([
        'ieeg',
        'psd',
        '--bids_dir',
        str(BIDS_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        ])
