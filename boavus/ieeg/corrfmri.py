from logging import getLogger
from multiprocessing import Pool
from shutil import rmtree

from numpy import ndindex, array, nansum, power, zeros, repeat, diag
from numpy.linalg import norm, inv
from scipy.stats import norm as normdistr
from scipy.stats import linregress
from nibabel import Nifti1Image
from nibabel.affines import apply_affine
from nibabel import load as nload
import plotly.graph_objs as go

from wonambi.attr import Freesurfer
from exportimages import export_plotly, Webdriver

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import read_tsv, replace_underscore

lg = getLogger(__name__)

ZSTAT_DIR = 'corr_ieeg_fmri_zstat'
PNG_DIR = 'corr_ieeg_fmri_png'


PARAMETERS = {
    'kernels': list(range(1, 10)),
    'distance': 'gaussian',
    'parallel': True,
    }


def main(bids_dir, freesurfer_dir, analysis_dir, output_dir):
    args = []
    for measure_nii in find_in_bids(analysis_dir, modality='compare', extension='.nii.gz', generator=True):
        lg.debug(f'adding {measure_nii}')
        args.append((measure_nii, bids_dir, freesurfer_dir, analysis_dir, output_dir))

    if PARAMETERS['parallel']:
        with Pool() as p:
            lg.debug('Starting pool')
            results = p.starmap(save_corrfmri, args)
    else:
        results = [save_corrfmri(*arg) for arg in args]

    plot_results(results, output_dir)


def save_corrfmri(measure_nii, bids_dir, freesurfer_dir, analysis_dir, output_dir):
    img = nload(str(measure_nii))
    img = upsample_mri(img)
    mri = img.get_data()

    task_fmri = file_Core(measure_nii)
    measure_ecog = find_in_bids(analysis_dir, subject=task_fmri.subject, task=task_fmri.task, modality='compare', extension='.tsv')
    freesurfer_path = freesurfer_dir / ('sub-' + task_fmri.subject)
    fs = Freesurfer(freesurfer_path)

    labels = [x['channel'] for x in read_tsv(measure_ecog)]
    ecog_val = array([float(x['measure']) for x in read_tsv(measure_ecog)])  # TODO

    electrodes = Electrodes(find_in_bids(bids_dir, subject=task_fmri.subject, acquisition='*regions', modality='electrodes', extension='.tsv'))

    chan_xyz = array(electrodes.get_xyz(labels))
    nd = array(list(ndindex(mri.shape)))
    ndi = from_mrifile_to_chan(img, fs, nd)

    results_dir = output_dir / ZSTAT_DIR
    rmtree(results_dir, ignore_errors=True)
    results_dir.mkdir(exist_ok=True, parents=True)
    results_tsv = results_dir / replace_underscore(task_fmri.get_filename(), PARAMETERS['distance'] + '.tsv')
    with results_tsv.open('w') as f:
        f.write('Kernel\tRsquared\n')

        for KERNEL in PARAMETERS['kernels']:
            r = compute_each_kernel(KERNEL, chan_xyz=chan_xyz, mri=mri, ndi=ndi, ecog_val=ecog_val)
            f.write(f'{KERNEL}\t{r}\n')
            f.flush()

    return results_tsv


def from_chan_to_mrifile(img, fs, xyz):
    return apply_affine(inv(img.affine), xyz + fs.surface_ras_shift).astype(int)


def from_mrifile_to_chan(img, fs, xyz):
    return apply_affine(img.affine, xyz) - fs.surface_ras_shift


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


def compute_each_kernel(KERNEL, chan_xyz, mri, ndi, ecog_val, output=None):
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

        mq = m * mri
        fmri_val.append(nansum(mq))

    lr = linregress(ecog_val, array(fmri_val))
    return lr.rvalue ** 2


def plot_results(results_tsv, output_dir):
    img_dir = output_dir / PNG_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True)

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:

            results = read_tsv(one_tsv)
            k = [x['Kernel'] for x in results]
            rsquared = [float(x['Rsquared']) for x in results]
            traces = [{
                'x': k,
                'y': rsquared,
                },
                ]

            layout = go.Layout(
                xaxis=dict(
                    title='mm'),
                yaxis=dict(
                    title='r<sup>2</sup>',
                    rangemode='tozero',
                ),
            )

            fig = go.Figure(data=traces, layout=layout)
            output_png = img_dir / (one_tsv.stem + '.png')
            export_plotly(fig, output_png, driver=d)
