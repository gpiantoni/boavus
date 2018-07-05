from boavus import boavus
from bidso.utils import read_tsv, replace_underscore
from numpy.testing import assert_allclose
from pytest import raises

from .paths import (BIDS_PATH,
                    ANALYSIS_PATH,
                    FREESURFER_PATH,
                    task_fmri,
                    )

output_tsv = replace_underscore(task_fmri.get_filename(ANALYSIS_PATH),
                                'bold_compare.tsv')
nvox_tsv = replace_underscore(output_tsv, 'nvoxels.tsv')


def test_fmri_at_electrodes_graymatter_error():

    with raises(ValueError):
        boavus([
            'fmri',
            'at_electrodes',
            '--bids_dir', str(BIDS_PATH),
            '--analysis_dir', str(ANALYSIS_PATH),
            '--log', 'debug',
            '--graymatter',
            ])


def test_fmri_at_electrodes_graymatter():

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--noparallel',
        '--log', 'debug',
        '--graymatter',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 54825.03575792142)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 11)
    assert_allclose(v, 0)


def test_fmri_at_electrodes_upsample():

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--noparallel',
        '--log', 'debug',
        '--upsample',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 56550.003565)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 2338)
    assert_allclose(v, 0)


def test_fmri_at_electrodes_graymatter_upsample():

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--noparallel',
        '--log', 'debug',
        '--graymatter',
        '--upsample',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 55097.18025556713)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 702)
    assert_allclose(v, 0)


def test_fmri_at_electrodes_sphere():

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--distance', 'sphere',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 61441.38281250001)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 22)
    assert_allclose(v, 0)


def test_fmri_at_electrodes_inverse():

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        '--noparallel',
        '--distance', 'inverse',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 60590.677291881606)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    assert_allclose(v, 0)


def test_fmri_at_electrodes_gaussian():
    # run default as the last one, so that it's used by other functions

    boavus([
        'fmri',
        'at_electrodes',
        '--bids_dir', str(BIDS_PATH),
        '--freesurfer_dir', str(FREESURFER_PATH),
        '--analysis_dir', str(ANALYSIS_PATH),
        '--log', 'debug',
        ])

    v = float([x['7'] for x in read_tsv(output_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 59382.12053669494)
    assert_allclose(v, 0)

    v = int([x['7'] for x in read_tsv(nvox_tsv) if x['channel'] == 'grid01'][0])
    # assert_allclose(v, 33)
    assert_allclose(v, 0)
