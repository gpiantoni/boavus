from boavus import boavus
from bidso.utils import replace_underscore
from pytest import raises

from .paths import (ANALYSIS_PATH,
                    task_fmri,
                    )
from .utils import compute_md5


output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')


def test_fmri_compare_error():

    with raises(ValueError):
        boavus([
            'fmri',
            'compare',
            '--analysis_dir', str(ANALYSIS_PATH),
            '--measure', 'xxx',
            ])


def test_fmri_compare_zstat():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--measure', 'zstat',
        ])

    assert compute_md5(output_nii) == '82dccb2547855d0e883be67e3bf19d86'


def test_fmri_compare_normalize():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--normalize_to_mean',
        ])

    assert compute_md5(output_nii) == '6876c3692c5e1bb1596b1f07c7d2455f'


def test_fmri_compare():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    assert compute_md5(output_nii) == '1d64d5bf6f83ba5f9f29c2459e98c307'
