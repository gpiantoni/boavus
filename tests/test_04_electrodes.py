from boavus import boavus

from .paths import (BIDS_PATH,
                    task_ieeg,
                    FREESURFER_PATH,
                    BOAVUS_PATH,
                    ANALYSIS_PATH,
                    )

ieeg_file = task_ieeg.get_filename(BIDS_PATH)


def test_ieeg_projectelectrodes():

    boavus([
        'electrodes',
        'project_to_surf',
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--acquisition', 'ct',
        '--noparallel',
        ])


def test_ieeg_assignregions():

    boavus([
        'electrodes',
        'assign_regions',
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--acquisition', 'ctprojected',
        ])


def test_ieeg_plotelectrodes(qtbot):

    boavus([
        'electrodes',
        'plot',
        '--output_dir', str(BOAVUS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--acquisition', 'ctprojected',
        ])
