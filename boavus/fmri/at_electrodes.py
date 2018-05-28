from functools import partial
from itertools import product
from logging import getLogger
from math import ceil
from multiprocessing import Pool, Process, cpu_count
import warnings

from numpy import (arange,
                   ndindex,
                   array,
                   sum,
                   power,
                   zeros,
                   repeat,
                   diag,
                   NaN,
                   isfinite,
                   nansum,
                   isnan,
                   where,
                   )
from numpy.linalg import norm, inv
from scipy.stats import norm as normdistr
from nibabel import Nifti1Image
from nibabel.affines import apply_affine
from nibabel import load as nload

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

from .utils import ribbon_to_feat, ribbon_to_graymatter

lg = getLogger(__name__)

COUNT_THRESHOLD = 0.5
# 1 sigma = 0.6065306597126334


def main(bids_dir, analysis_dir, freesurfer_dir=None, graymatter=False,
         distance='gaussian', acquisition='*regions', noparallel=False,
         upsample=False, kernel_start=6, kernel_end=8,
         kernel_step=1):
    """
    Calculate the (weighted) average of fMRI values at electrode locations

    TODO: Make sure that upsample mri and bold are in the same space

    Parameters
    ----------
    bids_dir : path

    analysis_dir : path

    freesurfer_dir : path
        only necessary if you include gray matter
    graymatter : bool

    distance : str

    acquisition : str

    noparallel : bool

    upsample : bool

    kernel_start : int

    kernel_end : int

    kernel_step : float

    """
    n_processes = len(list(find_in_bids(analysis_dir, modality='compare', extension='.nii.gz', generator=True)))
    kernels = arange(kernel_start, kernel_end, kernel_step)

    processes = []
    for measure_nii in find_in_bids(analysis_dir, modality='compare', extension='.nii.gz', generator=True):
        lg.debug(f'adding {measure_nii}')
        if not noparallel:
            n_cpu = ceil(cpu_count() / n_processes) - 1
        else:
            n_cpu = None
        processes.append(Process(target=calc_fmri_at_elec,
                                 args=(measure_nii, bids_dir, freesurfer_dir,
                                       analysis_dir, upsample, acquisition,
                                       kernels, graymatter, distance,
                                       n_cpu),
                                 daemon=False))  # make sure daemon is False, otherwise no children

    [p.start() for p in processes]
    [p.join() for p in processes]


def calc_fmri_at_elec(measure_nii, bids_dir, freesurfer_dir, analysis_dir,
                      upsample, acquisition, kernels, graymatter, distance,
                      n_cpu=None):
    img = nload(str(measure_nii))
    if upsample:
        img = upsample_mri(img)
    mri = img.get_data()
    mri[mri == 0] = NaN

    task_fmri = file_Core(measure_nii)

    try:
        electrodes = Electrodes(find_in_bids(bids_dir, subject=task_fmri.subject, acquisition=acquisition, modality='electrodes', extension='.tsv'))
    except FileNotFoundError as err:
        lg.debug(err)
        return None

    labels = electrodes.electrodes.get(map_lambda=lambda x: x['name'])
    chan_xyz = array(electrodes.get_xyz())

    nd = array(list(ndindex(mri.shape)))
    ndi = from_mrifile_to_chan(img, nd)

    if graymatter:
        if upsample:
            graymatter = ribbon_to_graymatter(freesurfer_dir, analysis_dir,
                                              task_fmri.subject)
            gm_mri = graymatter.get_data().astype(bool)
            mri[~gm_mri] = NaN
        else:
            raise NotImplementedError('graymatter / not upsample')

    lg.debug(f'Computing fMRI values for {measure_nii.name} at {len(labels)} electrodes and {len(kernels)} "{distance}" kernels')
    fmri_vals, n_voxels = compute_kernels(kernels, chan_xyz, mri, ndi, distance, n_cpu)

    # TODO: it might be better to create a separate folder
    for old_tsv in measure_nii.parent.glob(replace_underscore(measure_nii.name, '*.tsv')):
        old_tsv.unlink()

    fmri_vals_tsv = replace_underscore(measure_nii, 'compare.tsv')
    lg.debug(f'Saving {fmri_vals_tsv}')

    with fmri_vals_tsv.open('w') as f:
        f.write('channel\t' + '\t'.join(str(one_k) for one_k in kernels) + '\n')
        for one_label, val_at_elec in zip(labels, fmri_vals):
            f.write(one_label + '\t' + '\t'.join(str(one_val) for one_val in val_at_elec) + '\n')

    n_voxels_tsv = replace_underscore(measure_nii, 'nvoxels.tsv')
    with n_voxels_tsv.open('w') as f:
        f.write('channel\t' + '\t'.join(str(one_k) for one_k in kernels) + '\n')
        for one_label, val_at_elec in zip(labels, n_voxels):
            f.write(one_label + '\t' + '\t'.join(str(one_val) for one_val in val_at_elec) + '\n')


def _get_ribbon(freesurfer_path, upsample, feat_path):
    if upsample:
        ribbon = freesurfer_path / 'mri' / 'ribbon.mgz'
    else:
        ribbon = ribbon_to_feat(freesurfer_path, feat_path)
    return ribbon


def from_chan_to_mrifile(img, xyz):
    return apply_affine(inv(img.affine), xyz).astype(int)


def from_mrifile_to_chan(img, xyz):
    return apply_affine(img.affine, xyz)


def upsample_mri(img_lowres):
    lowres = img_lowres.get_data()
    r = lowres.copy()
    for i in range(3):
        r = repeat(r, 4, axis=i)

    af = img_lowres.affine.copy()
    af[:3, :3] /= 4
    af[:3, -1] -= diag(af)[:3] * 1.5  # I think it's 4 / 2 - 1 / 2 (not sure about where to get the sign)

    nifti = Nifti1Image(r, af)
    return nifti


def compute_kernels(kernels, chan_xyz, mri, ndi, distance, n_cpu=None):
    partial_compute_chan = partial(compute_chan, ndi=ndi, mri=mri, distance=distance)

    args = product(chan_xyz, kernels)
    if n_cpu is None:
        output = [partial_compute_chan(*arg) for arg in args]
    else:
        lg.debug(f'Number of CPU: {n_cpu}')
        with Pool(n_cpu) as p:
            output = p.starmap(partial_compute_chan, args)

    fmri_vals = [i[0] for i in output]
    n_voxels = [i[1] for i in output]

    fmri_vals = array(fmri_vals).reshape(-1, len(kernels))
    n_voxels = array(n_voxels).reshape(-1, len(kernels))

    return fmri_vals, n_voxels


def compute_chan(pos, KERNEL, ndi, mri, distance):
    dist_chan = norm(ndi - pos, axis=1)

    if distance == 'gaussian':
        m = normdistr.pdf(dist_chan, scale=KERNEL)
        m /= normdistr.pdf(0, scale=KERNEL)  # normalize so that peak is at 1, so that it's easier to count voxels

    elif distance == 'sphere':
        m = zeros(dist_chan.shape)
        m[dist_chan <= KERNEL] = 1

    elif distance == 'inverse':
        m = power(dist_chan, -1 * KERNEL)

    m = m.reshape(mri.shape)
    m[isnan(mri)] = NaN
    n_vox = _count_voxels(m)

    m /= sum(m[isfinite(m)])  # normalize so that the sum of the finite numbers is 1

    mq = m * mri
    return nansum(mq), n_vox


def _count_voxels(m):
    """Count voxels inside a 3D weight matrix.

    Parameters
    ----------
    m : 3d ndarray
        matrix as same size as mri, where the peak is 1 and each voxel has
        the weight based on the distance parameters

    Returns
    -------
    int
        number of voxels which have a weight higher than COUNT_THRESHOLD

    Notes
    -----
    Suppress RunTimeWarning because of > used against NaN.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        n_vox = len(where(m >= COUNT_THRESHOLD)[0])

    return n_vox
