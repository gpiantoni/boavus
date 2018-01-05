from os import setpgrp
from subprocess import Popen

from ..utils import ENVIRON


def run_freesurfer(FREESURFER_PATH, task):

    cmd = ['recon-all',
           '-all',
           '-cw256',
           '-sd', str(FREESURFER_PATH),
           '-subjid', 'sub-' + task.subject,
           '-i', task.filename,
           ]

    Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
