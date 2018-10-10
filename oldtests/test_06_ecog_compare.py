from pytest import fixture
from bidso.utils import read_tsv
from numpy.testing import assert_allclose

from boavus.ieeg.read import read_ieeg_block
from boavus.ieeg.psd import compute_powerspectrum
from boavus.ieeg.compare import compare_ieeg_freq

from .paths import BIDS_PATH, task_ieeg, elec_ct, ANALYSIS_PATH, COND, MINIMALDURATION

ieeg = task_ieeg.get_filename(BIDS_PATH)
electrodes = elec_ct.get_filename(BIDS_PATH)


@fixture
def preprocess():

    out_move, out_rest = read_ieeg_block(ieeg, electrodes, COND, MINIMALDURATION, ANALYSIS_PATH)

    psd_move = compute_powerspectrum(out_move, 'spectrogram', 'hann', 1, ANALYSIS_PATH)
    psd_rest = compute_powerspectrum(out_rest, 'spectrogram', 'hann', 1, ANALYSIS_PATH)

    return psd_move, psd_rest


def test_ieeg_compare_diff():

    psd_move, psd_rest = preprocess()
    output_tsv = compare_ieeg_freq(psd_move, psd_rest, (65, 96), False, 'dh2012', 'diff', ANALYSIS_PATH)

    v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 1.551890365962599)


def test_ieeg_compare_percent():

    psd_move, psd_rest = preprocess()
    output_tsv = compare_ieeg_freq(psd_move, psd_rest, (65, 96), False, 'dh2012', 'percent', ANALYSIS_PATH)


def test_ieeg_compare_dh2012t():

    psd_move, psd_rest = preprocess()
    output_tsv = compare_ieeg_freq(psd_move, psd_rest, (65, 96), False, 'dh2012', 'dh2012_t', ANALYSIS_PATH)


def test_ieeg_compare_baseline():

    psd_move, psd_rest = preprocess()
    output_tsv = compare_ieeg_freq(psd_move, psd_rest, (65, 96), True, 'dh2012', 'dh2012_t', ANALYSIS_PATH)


def test_ieeg_compare_method():

    psd_move, psd_rest = preprocess()
    METHODS = {
        '1a': 1.0,
        '1b': 1.0,
        '1c': 1.0,
        '1d': 1.0,
        '2a': 0.9786426425543525,
        '2b': 0.9848535661914938,
        '2c': 0.9861305558261255,
        '2d': 0.9881910378725067,
        '3a': 0.9021175058094721,
        '3b': 0.9309301804179754,
        '3c': 0.9389189728427727,
        }

    for method, result in METHODS.items():

        output_tsv = compare_ieeg_freq(psd_move, psd_rest, (65, 96), False, method, 'diff', ANALYSIS_PATH)

        v = float([x['measure'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
        # assert_allclose(v, result)
