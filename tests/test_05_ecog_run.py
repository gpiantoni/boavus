from numpy.testing import assert_allclose
from pickle import load
from pytest import fixture

from boavus.ieeg.read import read_ieeg_block
from boavus.ieeg.preprocessing import preprocess_ecog
from boavus.ieeg.psd import compute_powerspectrum

from .paths import BIDS_PATH, task_ieeg, elec_ct, ANALYSIS_PATH, COND, MINIMALDURATION

ieeg = task_ieeg.get_filename(BIDS_PATH)
electrodes = elec_ct.get_filename(BIDS_PATH)


@fixture
def test_ieeg_read():

    out_move, out_rest = read_ieeg_block(ieeg, electrodes, COND, MINIMALDURATION, ANALYSIS_PATH)

    with out_move.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 229309580.97038913)

    with out_rest.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 114692807.74778011)

    return out_move


def test_ieeg_preprocessing_regression():

    out_move = test_ieeg_read()
    out_prepr = preprocess_ecog(out_move, 'regression', 2, ANALYSIS_PATH)

    with out_prepr.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 6944731.825136112)


@fixture
def test_ieeg_preprocessing():

    out_move = test_ieeg_read()
    out_prepr = preprocess_ecog(out_move, 'average', 2, ANALYSIS_PATH)

    with out_prepr.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 6945108.024372008)

    return out_prepr


def test_ieeg_psd_spectrogram():

    out_prepr = test_ieeg_preprocessing()
    out_psd = compute_powerspectrum(out_prepr, 'spectrogram', 'hann', 1, ANALYSIS_PATH)

    with out_psd.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 17443757.375675)


def test_ieeg_psd_dh2012():

    out_prepr = test_ieeg_preprocessing()
    out_psd = compute_powerspectrum(out_prepr, 'dh2012', '', 2, ANALYSIS_PATH)

    with out_psd.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 17938632.464411)


def notest_ieeg_broadband():

    boavus([
        'ieeg',
        'broadband',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--bands', '30-40',
        ])

    with output_broadband.open('rb') as f:
        data = load(f)
    assert_allclose(data.data[0].sum(), 1393445261.229699)
