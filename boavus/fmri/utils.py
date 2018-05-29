"""Various functions, that I don't know where to place
"""
from nibabel import load as nload
from numpy import array, zeros
from nibabel import Nifti1Image

def get_vox2ras_tkr(filename):
    """This should be identical
    mri_info --vox2ras-tkr filename
    """
    img = nload(str(filename))

    Nc, Nr, Ns = img.shape[:3]
    dC, dR, dS = img.header['pixdim'][1:4]
    vox2ras_tkr = array([
        [-dC, 0, 0, Nc / 2 * dC],
        [0, 0, dS, -Ns / 2 * dS],
        [0, -dR, 0, Nr / 2 * dR],
        [0, 0, 0, 1],
    ])

    return vox2ras_tkr


def ribbon2graymatter(task_fmri, freesurfer_dir):
    ribbon_file = freesurfer_dir / ('sub-' + task_fmri.subject) / 'mri' / 'ribbon.mgz'
    graymatter_file = task_fmri.filename.parents[1] / 'anat' / 'ribbon_graymatter.nii.gz'

    ribbon = nload(str(ribbon_file))
    ribbon_mri = ribbon.get_data()

    graymatter = zeros(ribbon_mri.shape)
    graymatter[(ribbon_mri == 42) | (ribbon_mri == 3)] = 1
    nifti = Nifti1Image(graymatter, ribbon.affine)
    nifti.to_filename(str(graymatter_file))
    return graymatter_file
