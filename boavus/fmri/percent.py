from logging import getLogger
from numpy import array_equal, errstate, loadtxt, NaN

from nibabel import load as nload
from nibabel import save as nsave
from nibabel import Nifti1Image

from bidso import file_Core
from bidso.find import find_in_bids
from bidso.utils import bids_mkdir

lg = getLogger(__name__)


def run_fmri_percent(feat_dir, output_dir):
    for feat_path in find_in_bids(feat_dir, generator=True, extension='.feat'):
        lg.debug(f'Reading {feat_path}')

        compute_fmri_percent(feat_path, output_dir)


def compute_fmri_percent(feat_path, output_dir):

    percent_nifti = percent_fmri(feat_path)
    feat = file_Core(feat_path)
    task_path = bids_mkdir(output_dir, feat) / (feat.filename.stem + '_percent.nii.gz')

    nsave(percent_nifti, str(task_path))

    return percent_nifti


def percent_fmri(feat_path):
    """Calculate percent change for a task.

    Parameters
    ----------

    Returns
    -------
    instance of nibabel.Nifti1Image
        percent change as image


    TODO
    ----
    this could be a method of Feat
    """
    design = read_design(feat_path)

    pe_mri = nload(str(feat_path / 'stats' / 'pe1.nii.gz'))
    mean_mri = nload(str(feat_path / 'mean_func.nii.gz'))
    array_equal(pe_mri.affine, mean_mri.affine)

    pe = pe_mri.get_data()
    pe[pe == 0] = NaN
    mean_func = mean_mri.get_data()
    with errstate(invalid='ignore'):
        perc = pe / mean_func * 100 * design.ptp()

    mask_mri = nload(str(feat_path / 'mask.nii.gz'))
    mask = mask_mri.get_data().astype(bool)
    perc[~mask] = NaN

    return Nifti1Image(perc, pe_mri.affine)


def read_design(feat_path):
    """TODO: this could be a method of Feat"""
    return loadtxt(str(feat_path / 'design.mat'), skiprows=5)
