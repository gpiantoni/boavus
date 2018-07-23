from boavus import boavus
from bidso.utils import replace_underscore
from pytest import raises

from boavus.fmri.utils import mri_nan2zero

from .paths import (ANALYSIS_PATH,
                    task_fmri,
                    )
from .utils import compute_md5


output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')



def test_fmri_compare_zstat():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--measure', 'zstat',
        ])

    assert compute_md5(output_nii) == '9a3cf6c90aec16145ede7c01341488b3'


def test_fmri_compare_normalize():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--normalize_to_mean',
        ])

    # TODO: this can't be right
    assert compute_md5(output_nii) == '15593cc71aab9f41714aca0146f37228'


def test_fmri_compare():

    boavus([
        'fmri',
        'compare',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    assert compute_md5(output_nii) == '15593cc71aab9f41714aca0146f37228'


def test_mri_nan2zero():

    mri_nozero = mri_nan2zero(output_nii)
    assert compute_md5(mri_nozero) == '45a9c3b719cd3812c7e6c8ea6f174540'
