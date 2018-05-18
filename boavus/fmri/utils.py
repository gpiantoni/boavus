"""Various functions, that I don't know where to place
"""
from nibabel import load as nload
from numpy import array
from ..utils import check_subprocess
from subprocess import run, PIPE


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
