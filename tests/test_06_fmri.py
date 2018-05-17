from os import environ
from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH, FREESURFER_PATH


def test_fmri_percent():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])


def test_fmri_at_electrodes_gaussian():

    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        ])
