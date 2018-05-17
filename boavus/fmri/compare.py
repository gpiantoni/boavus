from logging import getLogger
from numpy import array_equal, errstate, loadtxt, NaN

from nibabel import load as nload
from nibabel import save as nsave
from nibabel import Nifti1Image

from bidso import file_Core
from bidso.find import find_in_bids
from bidso.utils import bids_mkdir

lg = getLogger(__name__)


def main(analysis_dir, measure='percent', normalize_to_mean=False):
    """
    compute percent change of the BOLD signal

    Parameters
    ----------
    analysis_dir : path

    measure : str
        "percent", "zstat"
    normalize_to_mean : bool

    """
    for feat_path in find_in_bids(analysis_dir, generator=True, extension='.feat'):
        lg.debug(f'Reading {feat_path}')

        if measure == 'percent':
            fmri_stat = compute_percent(feat_path)
        elif measure == 'zstat':
            fmri_stat = compute_zstat(feat_path)
        else:
            raise ValueError(f'Unknown measure: {measure}')

        feat = file_Core(feat_path)
        task_path = bids_mkdir(analysis_dir, feat) / (feat.filename.stem + '_compare.nii.gz')
        nsave(fmri_stat, str(task_path))


def compute_percent(feat_path, normalize_to_mean):
    """Calculate percent change for a task.

    Parameters
    ----------

    Returns
    -------
    instance of nibabel.Nifti1Image
        percent change as image
    """
    design = read_design(feat_path)

    pe_mri = nload(str(feat_path / 'stats' / 'pe1.nii.gz'))

    pe = pe_mri.get_data()
    pe[pe == 0] = NaN
    perc = pe * 100 * design.ptp()

    if normalize_to_mean:
        """I'm not sure if this is necessary, but for sure it increases the level
        of noise"""
        mean_mri = nload(str(feat_path / 'mean_func.nii.gz'))
        mean_func = mean_mri.get_data()
        array_equal(pe_mri.affine, mean_mri.affine)
        with errstate(invalid='ignore'):
            perc /= mean_func

    mask_mri = nload(str(feat_path / 'mask.nii.gz'))
    mask = mask_mri.get_data().astype(bool)
    perc[~mask] = NaN

    return Nifti1Image(perc, pe_mri.affine)


def compute_zstat(feat_path):
    return nload(str(feat_path / 'stats' / 'zstat1.nii.gz'))


def read_design(feat_path):
    """TODO: this could be a method of Feat"""
    return loadtxt(str(feat_path / 'design.mat'), skiprows=5)
