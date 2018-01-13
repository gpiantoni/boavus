from pathlib import Path
from time import sleep

from os import environ
from boavus.fmri.percent import percent_fmri


def test_fmri_percent():
    if environ.get('FSLDIR') is not None:
        feat_path = Path('tests/data/derivatives/feat/sub-bert/ses-day01/func/sub-bert_ses-day01_task-block_run-00.feat')
        while True:
            if (feat_path / 'rendered_thresh_zstat1.png').exists():
                break

            sleep(1)

        percent_fmri(feat_path)
