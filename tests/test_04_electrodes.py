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

ieeg_file = task_ieeg.get_filename(BIDS_PATH)


def test_ieeg_projectelectrodes():

    boavus([
        'ieeg',
        'project_electrodes',
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--acquisition', 'ct',
        '--noparallel',
        ])


def test_ieeg_assignregions():

    boavus([
        'ieeg',
        'assign_regions',
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--acquisition', 'ctprojected',
        ])


def test_ieeg_plotelectrodes(qtbot):

    boavus([
        'ieeg',
        'plot_electrodes',
        '--output_dir', str(BOAVUS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--acquisition', 'ctprojected',
        ])
