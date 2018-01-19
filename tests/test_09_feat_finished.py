from os import environ
from boavus.fmri.percent import percent_fmri
from boavus.fsl.feat import coreg_feat2freesurfer

from bidso.utils import add_extension, remove_underscore

from .paths import FREESURFER_PATH, FEAT_PATH, task_fmri

feat_path = add_extension(remove_underscore(task_fmri.get_filename(FEAT_PATH)), '.feat')


def test_fmri_percent():
    if environ.get('FSLDIR') is not None:
        percent_fmri(feat_path)


def test_feat_freesurfer():
    if environ.get('FSLDIR') is not None:
        coreg_feat2freesurfer(feat_path, FREESURFER_PATH)
