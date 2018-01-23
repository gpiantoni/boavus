from os import environ
from boavus.main import boavus
from boavus.fsl.feat import coreg_feat2freesurfer

from bidso.utils import replace_extension

from .paths import FREESURFER_PATH, FEAT_PATH, task_fmri, BOAVUS_PATH

feat_path = replace_extension(task_fmri.get_filename(FEAT_PATH), '.feat')


def test_fmri_percent():
    if environ.get('FSLDIR') is not None:
        boavus([
            'fmri',
            'percent',
            '--feat_dir',
            str(FEAT_PATH),
            '--output_dir',
            str(BOAVUS_PATH),
            ])


def test_feat_freesurfer():
    if environ.get('FSLDIR') is not None and False:
        coreg_feat2freesurfer(feat_path, FREESURFER_PATH)
