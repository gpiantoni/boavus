from os import environ
from json import load, dump
from boavus.main import main

from .paths import FREESURFER_PATH, BOAVUS_PATH, FEAT_PATH, BIDS_PATH

PARAMETERS_JSON = BOAVUS_PATH / 'ieeg_corrfmri.json'


def test_main_ieeg_corrfmri_parameters():
    assert not PARAMETERS_JSON.exists()

    main([
        'ieeg',
        'corrfmri',
        '--feat_dir',
        str(FEAT_PATH),
        '--output_dir',
        str(BOAVUS_PATH),
        '--freesurfer_dir',
        str(FREESURFER_PATH),
        '--bids_dir',
        str(BIDS_PATH),
        '--parameters',
        str(PARAMETERS_JSON),
        ])

    assert PARAMETERS_JSON.exists()

    with PARAMETERS_JSON.open() as f:
        PARAMETERS = load(f)
    PARAMETERS['kernels'] = [5, ]
    with PARAMETERS_JSON.open('w') as f:
        dump(PARAMETERS, f, indent='  ')


def test_main_ieeg_corrfmri():
    if environ.get('FSLDIR') is not None:
        main([
            'ieeg',
            'corrfmri',
            '--feat_dir',
            str(FEAT_PATH),
            '--output_dir',
            str(BOAVUS_PATH),
            '--freesurfer_dir',
            str(FREESURFER_PATH),
            '--bids_dir',
            str(BIDS_PATH),
            '--parameters',
            str(PARAMETERS_JSON),
            ])
