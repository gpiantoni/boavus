from bidso.utils import replace_underscore
from subprocess import run

from .utils import ENVIRON, mkdir_task


def run_bet(BET_PATH, task):
    bet_path = mkdir_task(BET_PATH, task)
    bet_nii = bet_path / replace_underscore(task.filename.name, 'bet.nii.gz')

    cmd = ['bet',
           str(task.filename),
           str(bet_nii),
           '-R',
           '-f', '0.5',
           '-g', '0',
           ]

    run(cmd, env=ENVIRON)
