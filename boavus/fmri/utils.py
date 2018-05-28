"""Various functions, that I don't know where to place
"""
from subprocess import run, PIPE

from nibabel import load as nload
from numpy import array, zeros
from nibabel import Nifti1Image

from ..utils import check_subprocess

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


def ribbon_to_feat(freesurfer_path, feat_path):
    """

    """
    o = freesurfer_path / 'mri' / 'ribbon_feat.mgz'

    if not o.exists():
        mov = freesurfer_path / 'mri' / 'ribbon.mgz'
        targ = feat_path / 'stats' / 'pe1.nii.gz'
        reg = feat_path / 'reg' / 'freesurfer' / 'anat2exf.register.dat'

        p = run([
            'mri_vol2vol',
            '--mov', str(targ),
            '--targ', str(mov),
            '--o', str(o),
            '--inv',
            '--reg', str(reg),
        ], stdout=PIPE, stderr=PIPE)
        check_subprocess(p)

    return o


def ribbon_to_graymatter(freesurfer_dir, analysis_dir, subject):
    anat_dir = analysis_dir / ('sub-' + subject) / 'anat'  # TODO: 'anat'
    graymatter_file = anat_dir / 'ribbon_graymatter.nii.gz'

    if graymatter_file.exists():
        nifti = nload(str(graymatter_file))

    else:
        ribbon_file = freesurfer_dir / ('sub-' + subject) / 'mri' / 'ribbon.mgz'
        ribbon = nload(str(ribbon_file))
        ribbon_mri = ribbon.get_data()

        graymatter = zeros(ribbon_mri.shape)
        graymatter[(ribbon_mri == 42) | (ribbon_mri == 3)] = 1
        nifti = Nifti1Image(graymatter, ribbon.affine)
        nifti.to_filename(str(graymatter_file))

    return nifti
