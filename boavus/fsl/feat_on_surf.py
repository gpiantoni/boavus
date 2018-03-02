from logging import getLogger
from shutil import rmtree
from subprocess import Popen, DEVNULL

from nibabel import load as nload
from wonambi.viz import Viz3
from wonambi.attr import Freesurfer

from bidso import file_Core
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

from ..utils import ENVIRON

lg = getLogger(__name__)


PARAMETERS = {
    'modality': 'compare',
    'surface': 'white',
    'surf-fwhm': 0,
    }

SURF_DIR = 'feat_surf'


def main(analysis_dir, freesurfer_dir, output_dir):

    p_all = []
    surfs = []
    for in_vol_file in find_in_bids(analysis_dir, generator=True, extension='.nii.gz', modality=PARAMETERS['modality']):
        in_vol = file_Core(in_vol_file)
        feat_path = find_in_bids(analysis_dir, subject=in_vol.subject, extension='.feat')
        for hemi in ('lh', 'rh'):
            p, out_surf = vol2surf(in_vol, feat_path, freesurfer_dir, hemi)
            p_all.append(p)
            surfs.append(out_surf)

    assert all([p.wait() == 0 for p in p_all]), 'Could not compute vol2surf for some tasks'  # I don't know how to get the error message from Popen

    img_dir = output_dir / SURF_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True, parents=True)

    for one_surf in surfs:
        plot_surf(img_dir, freesurfer_dir, one_surf)


def vol2surf(in_vol, feat_path, freesurfer_dir, hemi):
    out_surf = replace_underscore(in_vol.filename, in_vol.modality + 'surf' + hemi + '.mgh')

    cmd = [
        'mri_vol2surf',
        '--src',
        str(in_vol.filename),
        '--srcreg',
        str(feat_path / 'reg/freesurfer/anat2exf.register.dat'),
        '--trgsubject',
        'sub-' + in_vol.subject,  # freesurfer subject
        '--hemi',
        hemi,
        '--out',
        str(out_surf),
        '--surf',
        PARAMETERS['surface'],
        '--surf-fwhm',
        str(PARAMETERS['surf-fwhm']),
        ]

    p = Popen(cmd, env={**ENVIRON, 'SUBJECTS_DIR': str(freesurfer_dir)},
              stdout=DEVNULL, stderr=DEVNULL)

    info = {
        "surf": out_surf,
        "hemi": hemi,
        "subject": 'sub-' + in_vol.subject,
        }

    return p, info


def plot_surf(img_dir, freesurfer_dir, info):

    fs = Freesurfer(freesurfer_dir / info['subject'])
    surf = getattr(fs.read_brain(PARAMETERS['surface']), info['hemi'])

    surf_img = nload(str(info['surf']))
    surf_val = surf_img.get_data()[:, 0, 0].astype('float64')

    v = Viz3()
    v.add_surf(surf, values=surf_val, limits_c=(-6, 6))
    v.save(img_dir / (info['surf'].stem + '.png'))
