from pathlib import Path
from time import sleep

from os import environ
from boavus.fmri.percent import percent_fmri
from boavus.fsl.feat import coreg_feat2freesurfer
from .paths import FREESURFER_PATH

feat_path = Path('tests/data/derivatives/feat/sub-bert/ses-day01/func/sub-bert_ses-day01_task-block_run-00.feat')


def test_fmri_percent():
    if environ.get('FSLDIR') is not None:
        percent_fmri(feat_path)


def test_feat_freesurfer():
    if environ.get('FSLDIR') is not None:
        coreg_feat2freesurfer(feat_path, FREESURFER_PATH)
