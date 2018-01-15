from functools import partial

from boavus.ieeg.dataset import Dataset
from boavus.ieeg.preprocessing import preprocess_ecog
from wonambi.attr import Channels, Freesurfer

from numpy import ndindex, NaN, array, exp, stack, isnan, arange
from numpy.linalg import norm
from nibabel import Nifti1Image
from nibabel.affines import apply_affine
from numpy.linalg import inv
from scipy.stats import ttest_ind
from numpy import repeat, diag
from nibabel import load as nload
from multiprocessing import Pool
from scipy.stats import linregress

gauss = lambda x, s: exp(-.5 * (x ** 2 / s ** 2))


def from_chan_to_mrifile(img, fs, xyz):
    return apply_affine(inv(img.affine), xyz + fs.surface_ras_shift).astype(int)

def from_mrifile_to_chan(img, fs, xyz):
    return apply_affine(img.affine, xyz) - fs.surface_ras_shift

def _read_ecog_val(d):
    hfa_move, hfa_rest = preprocess_ecog(d.filename)

    # ecog_stats = percent_ecog(hfa_move, hfa_rest).data[0]
    t = ttest_ind(hfa_move.data[0], hfa_rest.data[0], axis=1).statistic
    return t, hfa_move.chan[0]


def _read_elec(d):
    """TODO: this should be in bidso"""
    labels = [x['name'] for x in d.electrodes.electrodes.tsv]
    mat = array([(float(x['x']), float(x['y']), float(x['z'])) for x in d.electrodes.electrodes.tsv])

    chan = Channels(labels, mat)
    return chan


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


def _read_fmri_val(feat_path, output_dir, to_plot):
    # fmri = percent_fmri(Path('/Fridge/users/giovanni/projects/mofe/derivatives/feat/sub-ommen/ses-daym25/func/sub-ommen_ses-daym25_task-motor-hand-left_run-00.feat'))

    img_lowres = nload(str(feat_path / 'stats' / 'zstat1.nii.gz'))
    upsampled = _upsample(img_lowres)
    if to_plot:
        upsampled.to_filename(str(output_dir / 'upsampled.nii.gz'))

    return upsampled


def _compute_gauss(pos, mri_shape, ndi, gauss_size):
    dist_chan = norm(ndi - pos, axis=1)
    return gauss(dist_chan, gauss_size).reshape(mri_shape)


def _compute_voxmap(chan_xyz, mri_shape, ndi, gauss_size):

    p_compute_gauss = partial(_compute_gauss, mri_shape=mri_shape, ndi=ndi, gauss_size=gauss_size)
    with Pool() as p:
        all_m = p.map(p_compute_gauss, chan_xyz)
    ms = stack(all_m, axis=-1)
    MAX_STD = 3
    ms[ms.max(axis=-1) < gauss(gauss_size * MAX_STD, gauss_size), :] = NaN
    mq = ms / ms.sum(axis=-1)[..., None]

    return mq


def _main(ieeg_file, feat_path, FREESURFER_PATH, DERIVATIVES_PATH, KERNEL_SIZES, to_plot=False):

    output_path = DERIVATIVES_PATH / 'corr_fmri_ecog'
    output_path.mkdir(exist_ok=True)

    d = Dataset(ieeg_file)

    freesurfer_path = FREESURFER_PATH / d.subject
    fs = Freesurfer(freesurfer_path)
    ecog_val, labels = _read_ecog_val(d)
    elec = _read_elec(d)
    elec = elec(lambda x: x.label in labels)
    print(len(elec.return_label()))
    print(len(ecog_val))
    print('ecog done')

    img = _read_fmri_val(feat_path, output_path, to_plot)
    mri = img.get_data()
    print('fmri done')

    chan_xyz = elec.return_xyz()
    nd = array(list(ndindex(mri.shape)))
    ndi = from_mrifile_to_chan(img, fs, nd)
    print('ndindex done')

    r = []

    for gauss_size in KERNEL_SIZES:
        print(gauss_size)
        mq = _compute_voxmap(chan_xyz, mri.shape, ndi, gauss_size)
        if to_plot:
            t_val = arange(chan_xyz.shape[0])
            nifti_data = (mq * t_val[None, None, None, :]).sum(axis=-1)
            nifti = Nifti1Image(nifti_data, img.affine)
            nifti.to_filename(str(DERIVATIVES_PATH / 'trans_example.nii.gz'))

        m = (mq * ecog_val[None, None, None, :]).sum(axis=-1)
        mask = (~isnan(mq[:, :, :, 0])) & (mri != 0)

        if to_plot:
            nifti_data = m.copy()
            nifti_data[~mask] = NaN  # also exclude area outside of fmri
            nifti = Nifti1Image(nifti_data, img.affine)
            nifti.to_filename(str(DERIVATIVES_PATH / 'ecog_to_mri.nii.gz'))

        lr = linregress(m[mask], mri[mask])
        print(lr)

        r.append(lr.rvalue ** 2)

    return r
