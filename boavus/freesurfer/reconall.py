from os import setpgrp
from subprocess import Popen

from bidso import file_Core
from bidso.find import find_in_bids

from ..utils import ENVIRON


def main(bids_dir, freesurfer_dir):
    """
    run freesurfer recon-all

    Parameters
    ----------
    bids_dir : path

    freesurfer_dir : path

    """

    for mri_path in find_in_bids(bids_dir, generator=True, modality='T1w', extension='.nii.gz'):
        task = file_Core(mri_path)
        run_freesurfer(freesurfer_dir, task)


def run_freesurfer(FREESURFER_PATH, task):

    cmd = ['recon-all',
           '-all',   # '-autorecon1',
           '-cw256',
           '-sd', str(FREESURFER_PATH),
           '-subjid', 'sub-' + task.subject,
           '-i', task.filename,
           ]

    Popen(cmd, env=ENVIRON, preexec_fn=setpgrp)
