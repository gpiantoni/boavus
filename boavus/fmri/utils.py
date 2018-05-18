"""Various functions, that I don't know where to place
"""
from nibabel import load as nload
from numpy import array

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

def ribbon_to_fmri_space():
    """

    TODO
    ----
    Develop this function
    """
    bids_subj in Path('/Fridge/users/giovanni/projects/dhbm/derivatives/analysis').glob('sub-*')
    freesurfer_path = Path('/Fridge/users/giovanni/projects/dhbm/derivatives/freesurfer')
    mov = freesurfer_path / bids_subj.name / 'mri' / 'ribbon.mgz'
    targ = next(bids_subj.rglob('pe1.nii.gz'))
    o = freesurfer_path / bids_subj.name / 'mri' / 'ribbon_feat.mgz'
    reg = next(bids_subj.rglob('*.feat')) / 'reg'/ 'freesurfer' / 'anat2exf.register.dat'

    c = run([
        'mri_vol2vol',
        '--mov', str(targ),
        '--targ', str(mov),
        '--o', str(o),
        '--inv',
        '--reg', str(reg),
    ])
