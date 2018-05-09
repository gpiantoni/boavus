from shutil import copyfile, which

from bidso.utils import replace_underscore
from boavus import boavus

from .paths import (BIDS_PATH,
                    task_ieeg,
                    elec_ct,
                    FREESURFER_PATH,
                    BOAVUS_PATH,
                    PARAMETERS_PATH,
                    ANALYSIS_PATH,
                    SIMULATE_PATH,
                    )
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
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
        ])

    update_parameters(PARAMETERS_JSON, acquisition='ct', parallel=False)

    boavus([
        'ieeg',
        'project_electrodes',
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
        ])


def test_ieeg_assignregions():
    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_assignregions.json'
    update_parameters(PARAMETERS_JSON, parallel=False)

    boavus([
        'ieeg',
        'assign_regions',
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
        ])


def test_ieeg_plotelectrodes(qtbot):

    PARAMETERS_JSON = PARAMETERS_PATH / 'ieeg_plotelectrodes.json'
    boavus([
        'ieeg',
        'plot_electrodes',
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
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
        '--analysis_dir',
        str(ANALYSIS_PATH),
        '-p',
        str(PARAMETERS_JSON),
        '--log',
        'debug',
        ])
