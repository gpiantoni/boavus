from pathlib import Path
from subprocess import run

from ..utils import ENVIRON, mkdir_task, replace_underscore


def run_bet(BET_PATH, task):
    bet_path = mkdir_task(BET_PATH, task)
    bet_nii = bet_path / replace_underscore(Path(task.filename).name, 'bet.nii.gz')

    cmd = ['bet',
           str(task.filename),
           str(bet_nii),
           '-R',
           '-f', '0.5',
           '-g', '0',
           ]

    run(cmd, env=ENVIRON)

    return bet_nii
