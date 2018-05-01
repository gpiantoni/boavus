from functools import partial
from itertools import product
from logging import getLogger
from math import ceil
from multiprocessing import Pool, Process, cpu_count

from numpy import ndindex, array, nansum, power, zeros, repeat, diag, NaN, nanmean
from numpy.linalg import norm, inv
from scipy.stats import norm as normdistr
from nibabel import Nifti1Image
from nibabel.affines import apply_affine
from nibabel import load as nload

from wonambi.attr import Freesurfer

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

lg = getLogger(__name__)


PARAMETERS = {
    'graymatter': True,
    'kernels': list(range(1, 10)),
    'distance': 'gaussian',
    'acquisition': '*regions',
    'parallel': True,
    'fs_shift': -1,
    'upsample': False,
    'approach': True,
    }


def main(bids_dir, freesurfer_dir, analysis_dir):
    n_processes = len(list(find_in_bids(analysis_dir, modality='compare', extension='.nii.gz', generator=True)))

    processes = []
    for measure_nii in find_in_bids(analysis_dir, modality='compare', extension='.nii.gz', generator=True):
        lg.debug(f'adding {measure_nii}')
        processes.append(Process(target=calc_fmri_at_elec,
                                 args=(measure_nii, bids_dir, freesurfer_dir,
                                       analysis_dir, ceil(cpu_count() / n_processes) - 1),
                                 daemon=False))  # make sure daemon is False, otherwise no children

    [p.start() for p in processes]
    [p.join() for p in processes]


def calc_fmri_at_elec(measure_nii, bids_dir, freesurfer_dir, analysis_dir, n_cpu=None):
    img = nload(str(measure_nii))
    if PARAMETERS['upsample']:
        img = upsample_mri(img)
    mri = img.get_data()
    mri[mri == 0] = NaN

    task_fmri = file_Core(measure_nii)
    freesurfer_path = freesurfer_dir / ('sub-' + task_fmri.subject)
    fs = Freesurfer(freesurfer_path)

    try:
        electrodes = Electrodes(find_in_bids(bids_dir, subject=task_fmri.subject, acquisition=PARAMETERS['acquisition'], modality='electrodes', extension='.tsv'))
    except FileNotFoundError as err:
        lg.debug(err)
        return None

    labels = electrodes.electrodes.get(map_lambda=lambda x: x['name'])
    chan_xyz = array(electrodes.get_xyz())
    if task_fmri.subject == 'maan':
        # convert from RAS to tkRAS
        chan_xyz -= fs.surface_ras_shift

    nd = array(list(ndindex(mri.shape)))
    ndi = from_mrifile_to_chan(img, fs, nd)

    if PARAMETERS['graymatter']:
        i_ndi = _select_graymatter(ndi, fs)
        ndi = ndi[i_ndi, :]
        mri = mri.flatten()[i_ndi]

    kernels = PARAMETERS['kernels']
    lg.debug(f'Computing fMRI values for {measure_nii.name} at {len(labels)} electrodes and {len(kernels)} "{PARAMETERS["distance"]}" kernels')
    fmri_vals_list = compute_kernels(kernels, chan_xyz, mri, ndi, n_cpu)
    fmri_vals = array(fmri_vals_list).reshape(-1, len(kernels))

    fmri_vals_tsv = replace_underscore(measure_nii, PARAMETERS['distance'] + 'elec.tsv')
    lg.debug(f'Saving {fmri_vals_tsv}')

    with fmri_vals_tsv.open('w') as f:
        f.write('channel\t' + '\t'.join(str(one_k) for one_k in kernels) + '\n')
        for one_label, val_at_elec in zip(labels, fmri_vals):
            f.write(one_label + '\t' + '\t'.join(str(one_val) for one_val in val_at_elec) + '\n')


def _select_graymatter(ndi, fs):
    if PARAMETERS['upsample']:
        ribbon_name = 'ribbon.mgz'
    else:
        ribbon_name = 'ribbon_feat.mgz'
    ribbon = nload(str(fs.dir / 'mri' / ribbon_name))
    x = from_chan_to_mrifile(ribbon, fs, ndi)

    r_mri = ribbon.get_data()

    brain = zeros(x.shape[0], dtype=bool)
    for i, i_x in enumerate(x):
        try:
            brain[i] = (r_mri[tuple(i_x)] == 42) or (r_mri[tuple(i_x)] == 3)
        except IndexError:
            continue

    return brain


def from_chan_to_mrifile(img, fs, xyz):
    return apply_affine(inv(img.affine), xyz + fs.surface_ras_shift * PARAMETERS['fs_shift']).astype(int)


def from_mrifile_to_chan(img, fs, xyz):
    return apply_affine(img.affine, xyz) - fs.surface_ras_shift * PARAMETERS['fs_shift']


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


def compute_kernels(kernels, chan_xyz, mri, ndi, n_cpu=None):
    partial_compute_chan = partial(compute_chan, ndi=ndi, mri=mri)

    args = product(chan_xyz, kernels)
    if PARAMETERS['parallel']:
        lg.debug(f'Number of CPU: {n_cpu}')
        with Pool(n_cpu) as p:
            fmri_val = p.starmap(partial_compute_chan, args)
    else:
        fmri_val = [partial_compute_chan(*arg) for arg in args]

    return fmri_val


def compute_chan(pos, KERNEL, ndi, mri):
    dist_chan = norm(ndi - pos, axis=1)

    if PARAMETERS['approach']:
        m = zeros(dist_chan.shape, dtype=bool)
        m[dist_chan <= KERNEL] = True
        m = m.reshape(mri.shape)
        return nanmean(mri[m])

    else:
        if PARAMETERS['distance'] == 'gaussian':
            m = normdistr.pdf(dist_chan, scale=KERNEL)

        elif PARAMETERS['distance'] == 'sphere':
            m = zeros(dist_chan.shape)
            m[dist_chan <= KERNEL] = 1

        elif PARAMETERS['distance'] == 'inverse':
            m = power(dist_chan, -1 * KERNEL)

        m /= nansum(m)  # normalize so that the sum is 1
        m = m.reshape(mri.shape)

        mq = m * mri
        return nansum(mq)
