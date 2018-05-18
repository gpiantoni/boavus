from os import environ
from boavus import boavus
from bidso.utils import read_tsv, replace_underscore, replace_extension

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    task_fmri,
                    )
from .utils import compute_md5


output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')
output_tsv = replace_extension(output_nii, '.tsv')


def test_fmri_percent():
    if environ.get('FSLDIR') is None:
        return

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    assert compute_md5(output_nii) == 'aeb85f5b34a1498319d1ee8772eec4a8'


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

    tsv = read_tsv(output_tsv)
    assert [x['7'] for x in tsv if x['channel'] == 'grid01'][0] == '59696.5178553907'
