from boavus import boavus

from .paths import BIDS_PATH, ANALYSIS_PATH


def test_prf_read():
    boavus([
        'ieeg', 'read',
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--task', 'bairprf',
        '--prestim', '0',
        '--poststim', '1',
        ])

    """
    with output_data.open('rb') as f:
        data = load(f)
    assert_allclose(abs(data.data[0]).sum(), 229309580.97038913)
    """

    boavus([
        'ieeg', 'psd',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--input', 'ieeg',
        '--noparallel',
        ])


def test_prf_analyzePRF():
    boavus([
        'prf', 'fit',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--input', 'ieegpsd',
        '--method', 'analyzePRF',
        '--noparallel',
    ])


def notest_prf_popeye():
    boavus([
        'prf', 'fit',
        '--analysis_dir', str(ANALYSIS_PATH),
        '--input', 'ieegpsd',
        '--method', 'popeye',
        '--noparallel',
    ])
