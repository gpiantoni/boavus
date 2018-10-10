from subprocess import run, PIPE
from pytest import raises
from numpy import array
from numpy.testing import assert_array_equal
from bidso.utils import replace_underscore

from boavus.fmri.utils import get_vox2ras_tkr
from boavus.utils import check_subprocess

from .paths import (ANALYSIS_PATH,
                    task_fmri,
                    )

output_nii = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.nii.gz')


def test_subprocess_raises():

    p = run(['sleep', 'a'], stdout=PIPE, stderr=PIPE)
    with raises(RuntimeError):
        check_subprocess(p)


def test_vox2ras_tkr():

    tkr = get_vox2ras_tkr(output_nii)

    p = run([
        'mri_info',
        '--vox2ras-tkr',
        str(output_nii),
        ], stdout=PIPE, stderr=PIPE)

    assert_array_equal(tkr, _read_mri_info(p))


def _read_mri_info(p):
    x = []
    for row in p.stdout.decode().split('\n')[1:5]:
        x.append([float(i) for i in row.split()])

    return array(x)
