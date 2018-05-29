from pathlib import Path
from shutil import copyfile
from subprocess import run
from tempfile import mkstemp

from bidso.utils import bids_mkdir, replace_underscore

from ..utils import ENVIRON


def run_bet(BET_PATH, task):
    bet_path = bids_mkdir(BET_PATH, task)
    bet_nii = bet_path / replace_underscore(Path(task.filename).name, 'bet.nii.gz')

    cmd = [
        'bet',
        str(task.filename),
        str(bet_nii),
        '-R',
        '-f', '0.5',
        '-g', '0',
        ]

    run(cmd, env=ENVIRON)

    return bet_nii


def run_reorient2std(nii):
    """This function simply reorients nifti, so that FSL can work with it
    more easily (reg works much better after running this function).
    """
    tmp_nii = mkstemp(suffix='.nii.gz')[1]
    cmd = [
        'fslreorient2std',
        str(nii),
        tmp_nii,
        ]
    run(cmd, env=ENVIRON)
    copyfile(tmp_nii, nii)
    Path(tmp_nii).unlink()


def run_flirt_resample(nii_in, nii_out, target_resolution):
    """Downsample and upsample mri
    """
    cmd = [
        'flirt',
        '-in', str(nii_in),
        '-ref', str(nii_in),
        '-out', str(nii_out),
        '-applyisoxfm', str(target_resolution),
        ]
    run(cmd, env=ENVIRON)
