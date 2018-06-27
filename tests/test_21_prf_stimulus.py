from numpy import load
from numpy.testing import assert_array_equal
from scipy.io import savemat
from wonambi import Dataset

from boavus.ieeg.read import read_prf_stimuli

from .paths import (BIDS_PATH,
                    task_prf,
                    )


def test_read_prf():
    _convert_numpy_to_matlab()

    ieeg_file = task_prf.get_filename(BIDS_PATH)
    d = Dataset(ieeg_file, bids=True)
    numpy_stim = read_prf_stimuli(d.dataset.task)

    task = d.dataset.task
    task.events.tsv[0]['stim_file'] = 'prf.mat'
    mat_stim = read_prf_stimuli(task)

    assert_array_equal(numpy_stim, mat_stim)


def _convert_numpy_to_matlab():

    numpy_stim_file = BIDS_PATH / 'stimuli' / 'prf.npy'
    matlab_stim_file = numpy_stim_file.with_suffix('.mat')

    np_stim = load(numpy_stim_file)
    mat_stim = {'images': np_stim}
    savemat(matlab_stim_file, {'stimulus': mat_stim})
