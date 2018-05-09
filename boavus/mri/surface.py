from logging import getLogger
from pathlib import Path
from subprocess import run, DEVNULL
from tempfile import TemporaryDirectory

from nibabel import Nifti1Image
from nibabel import load as niload
from scipy.ndimage.filters import gaussian_filter
from scipy.ndimage.morphology import binary_closing

PARAMETERS = {
    'gaussian_filter': 1,
    'closing_iter': 15,
    'smooth_iteration': 60,
    }

lg = getLogger(__name__)


def fill_surface(surf_in, surf_smooth):

    with TemporaryDirectory() as tmpdir:
        print(tmpdir)
        tmpdir = Path(tmpdir)

        vol_file = tmpdir / 'vol.mgz'
        vol_filled = tmpdir / 'filled.nii.gz'
        surf_filled = tmpdir / 'filled.surf'

        run([
            'mris_fill',
            '-c', '-r', '1',
            str(surf_in),
            str(vol_file),
            ], stdout=DEVNULL, stderr=DEVNULL)

        _close_volume(vol_file, vol_filled)

        run([
            'mri_tessellate',
            str(vol_filled),
            '1',
            str(surf_filled),
            ], stdout=DEVNULL, stderr=DEVNULL)

        run([
            'mris_smooth',
            '-nw',
            '-n', str(PARAMETERS['smooth_iteration']),
            str(surf_filled),
            str(surf_smooth)
            ], stdout=DEVNULL, stderr=DEVNULL)


def _close_volume(vol_file, filled):

    vol = niload(str(vol_file))
    volume = vol.get_data()
    v = gaussian_filter(volume, PARAMETERS['gaussian_filter'])

    # binarize
    v[v <= 25 / 255] = 0
    v[v > 25 / 255] = 1

    closed = binary_closing(v, iterations=PARAMETERS['closing_iter'])
    n = Nifti1Image(closed.astype('float32'), vol.affine)
    n.to_filename(str(filled))

    return filled
