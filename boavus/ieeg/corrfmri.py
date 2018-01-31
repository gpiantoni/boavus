from functools import partial
from logging import getLogger
from bidso.find import find_in_bids
from bidso.utils import replace_underscore
from bidso import Task

from boavus.fmri.percent import percent_fmri
from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog
from boavus.ieeg.percent import percent_ecog
from wonambi.attr import Freesurfer

from numpy import ndindex, NaN, array, stack, isnan, arange, nansum, power, zeros
from numpy.linalg import norm
from nibabel import Nifti1Image
from nibabel.affines import apply_affine
from numpy.linalg import inv
from numpy import repeat, diag
from nibabel import load as nload
from multiprocessing import Pool
from scipy.stats import norm as normdistr
from scipy.stats import linregress

lg = getLogger(__name__)


PARAMETERS = {
    'kernels': list(range(1, 10)),
    'measure': 'zstat',
    'distance': 'gaussian',
    'save_nifti': False,
    'parallel': True,
    }


def main(bids_dir, feat_dir, freesurfer_dir, output_dir):

    for ieeg_file in find_in_bids(bids_dir, modality='ieeg', extension='.bin', generator=True):
        try:
            ieeg = Task(ieeg_file)
            feat_path = find_in_bids(feat_dir, subject=ieeg.subject, task=ieeg.task,
                                     modality='bold', extension='.feat')

            output = _main_to_elec(ieeg_file, feat_path, freesurfer_dir, output_dir)

            results = replace_underscore(ieeg.get_filename(output_dir),
                                         PARAMETERS['measure'] + '_' + PARAMETERS['distance'] + '_results.tsv')
            lg.debug(f'Saving results to {str(results)}')

            results.parent.mkdir(exist_ok=True, parents=True)
            with results.open('w') as f:
                f.write(str(output))

        except Exception as err:
            lg.warning(err)


def from_chan_to_mrifile(img, fs, xyz):
    return apply_affine(inv(img.affine), xyz + fs.surface_ras_shift).astype(int)


def from_mrifile_to_chan(img, fs, xyz):
    return apply_affine(img.affine, xyz) - fs.surface_ras_shift


def _read_ecog_val(d):
    hfa_move, hfa_rest = preprocess_ecog(d.filename)

    if PARAMETERS['measure'] == 'percent':
        ecog_stats = percent_ecog(hfa_move, hfa_rest).data[0]
    elif PARAMETERS['measure'] == 'zstat':
        ecog_stats = percent_ecog(hfa_move, hfa_rest).data[0]

    return ecog_stats, hfa_move.chan[0]


def _upsample(img_lowres):
    lowres = img_lowres.get_data()
    r = lowres.copy()
    for i in range(3):
        r = repeat(r, 4, axis=i)

    af = img_lowres.affine.copy()
    af[:3, :3] /= 4
    af[:3, -1] -= diag(af)[:3] * 1.5  # I think it's 4 / 2 - 1 / 2 (not sure about where to get the sign)

    nifti = Nifti1Image(r, af)
    return nifti


def _read_fmri_val(feat_path, output_dir):
    if PARAMETERS['measure'] == 'percent':
        img_lowres = percent_fmri(feat_path)
    elif PARAMETERS['measure'] == 'zstat':
        img_lowres = nload(str(feat_path / 'stats' / 'zstat1.nii.gz'))

    upsampled = _upsample(img_lowres)
    if PARAMETERS['save_nifti']:
        upsampled.to_filename(str(output_dir / 'upsampled.nii.gz'))

    return upsampled


def _compute_each_kernel(KERNEL, chan_xyz, mri, ndi, ecog_val, output=None):
    fmri_val = []
    for pos in chan_xyz:
        dist_chan = norm(ndi - pos, axis=1)

        if PARAMETERS['distance'] == 'gaussian':
            m = normdistr.pdf(dist_chan, scale=KERNEL)

        elif PARAMETERS['distance'] == 'sphere':
            m = zeros(dist_chan.shape)
            m[dist_chan <= KERNEL] = 1

        elif PARAMETERS['distance'] == 'inverse':
            m = power(dist_chan, -1 * KERNEL)

        m /= nansum(m)  # normalize so that the sum is 1
        m = m.reshape(mri.shape)

        if output is not None:
            nifti = Nifti1Image(m, affine)
            nifti.to_filename(str(output))

        mq = m * mri
        fmri_val.append(nansum(mq))

    lr = linregress(ecog_val, array(fmri_val))
    return lr.rvalue ** 2


def _main_to_elec(ieeg_file, feat_path, FREESURFER_PATH, DERIVATIVES_PATH):

    output_path = DERIVATIVES_PATH
    output_path.mkdir(exist_ok=True)

    img = _read_fmri_val(feat_path, output_path)
    mri = img.get_data()
    lg.info('fmri done')

    pattern = '*regions'
    d = Dataset(ieeg_file, pattern)

    freesurfer_path = FREESURFER_PATH / ('sub-' + d.subject)
    fs = Freesurfer(freesurfer_path)
    ecog_val, labels = _read_ecog_val(d)
    lg.debug(ecog_val)
    lg.info('ecog done')

    chan_xyz = array(d.electrodes.get_xyz(labels))
    nd = array(list(ndindex(mri.shape)))
    ndi = from_mrifile_to_chan(img, fs, nd)
    lg.info('ndindex done')

    if PARAMETERS['parallel']:
        p_compute_each_kernel = partial(_compute_each_kernel, chan_xyz=chan_xyz, mri=mri, ndi=ndi, ecog_val=ecog_val)

        KERNEL_SIZES = PARAMETERS['kernels']
        with Pool() as p:
            r = p.map(p_compute_each_kernel, KERNEL_SIZES)

    else:
        r = []
        for KERNEL in PARAMETERS['kernels']:
            r.append(_compute_each_kernel(KERNEL, chan_xyz=chan_xyz, mri=mri,
                                          ndi=ndi, ecog_val=ecog_val))


    return r
