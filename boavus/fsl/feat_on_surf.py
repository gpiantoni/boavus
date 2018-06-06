from logging import getLogger
from shutil import rmtree
from subprocess import Popen, PIPE

from nibabel import load as nload
from wonambi.viz import Viz3
from wonambi.attr import Freesurfer

from bidso import file_Core
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

from ..fmri.utils import mri_nan2zero
from ..utils import ENVIRON, check_subprocess


lg = getLogger(__name__)

SURF_DIR = 'feat_surf'


def main(analysis_dir, freesurfer_dir, output_dir, modality='compare',
         surface='white', surf_fwhm=0):
    """
    map feat values on freesurfer surface',

    Parameters
    ----------
    analysis_dir : path

    freesurfer_dir : path

    output_dir : path

    modality : str
        "compare"
    surface : str
        "white", "pial"
    surf_fwhm : float
        FWHM
    """
    p_all = []
    surfs = []
    for in_vol_file in find_in_bids(analysis_dir, generator=True, extension='.nii.gz', modality=modality):
        in_vol = file_Core(in_vol_file)
        feat_path = find_in_bids(analysis_dir, subject=in_vol.subject, extension='.feat')
        for hemi in ('lh', 'rh'):
            p, out_surf = vol2surf(in_vol, feat_path, freesurfer_dir, hemi, surface, surf_fwhm)
            p_all.append(p)
            surfs.append(out_surf)

    # wait for all processes to run
    [p.wait() for p in p_all]
    [check_subprocess(p) for p in p_all]
    [info['mri_nonan'].unlink() for info in surfs]

    img_dir = output_dir / SURF_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True, parents=True)

    for one_surf in surfs:
        plot_surf(img_dir, freesurfer_dir, one_surf, surface)


def vol2surf(in_vol, feat_path, freesurfer_dir, hemi, surface, surf_fwhm):
    out_surf = replace_underscore(in_vol.filename, in_vol.modality + 'surf' + hemi + '.mgh')
    mri_nonan = mri_nan2zero(in_vol.filename)

    cmd = [
        'mri_vol2surf',
        '--src',
        str(mri_nonan),
        '--srcreg',
        str(feat_path / 'reg/freesurfer/anat2exf.register.dat'),
        '--trgsubject',
        'sub-' + in_vol.subject,  # freesurfer subject
        '--hemi',
        hemi,
        '--out',
        str(out_surf),
        '--surf',
        surface,
        '--surf-fwhm',
        str(surf_fwhm),
        ]

    p = Popen(cmd, env={**ENVIRON, 'SUBJECTS_DIR': str(freesurfer_dir)},
              stdout=PIPE, stderr=PIPE)

    info = {
        "surf": out_surf,
        "hemi": hemi,
        "subject": 'sub-' + in_vol.subject,
        "mri_nonan": mri_nonan,
        }

    return p, info


def plot_surf(img_dir, freesurfer_dir, info, surface):

    fs = Freesurfer(freesurfer_dir / info['subject'])
    surf = getattr(fs.read_brain(surface), info['hemi'])

    surf_img = nload(str(info['surf']))
    surf_val = surf_img.get_data()[:, 0, 0].astype('float64')

    v = Viz3()
    v.add_surf(surf, values=surf_val, limits_c=(-6, 6), colorbar=True)
    v.save(img_dir / (info['surf'].stem + '.png'))
    v.close()
