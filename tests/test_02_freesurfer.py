from boavus import boavus

from .paths import BIDS_PATH, FREESURFER_PATH


def test_main_freesurfer_reconall():
    # doesn't run freesurfer because the output folder exists already.

    boavus([
        'freesurfer',
        'reconall',
        '--bids_dir',
        str(BIDS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--log',
        'debug',
        ])
