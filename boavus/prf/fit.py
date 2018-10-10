from pickle import load
from logging import getLogger
from multiprocessing import Pool

from bidso import Task
from bidso.find import find_in_bids
from bidso.utils import replace_extension
from numpy import where, array, zeros
from wonambi.trans import select, math, concatenate

from nibabel import load as nload
from nibabel.affines import apply_affine
from nibabel import Nifti1Image

from sanajeh.data import data_aparc
from sanajeh.fmri import select_region
from .core.least_squares import fit_analyzePRF
from .core.popeye import fit_popeye
# from ..ieeg.read import read_prf_stimuli

lg = getLogger(__name__)


def main(analysis_dir, method="analyzePRF", task='bairprf', input='ieegprocpsd', noparallel=False):
    """
    compute psd for two conditions

    Parameters
    ----------
    analysis_dir : path

    method : str
        "popeye" or "analyzePRF"
    task : str
        task to analyze
    input : str
        name of the modality of the preceding step
    noparallel : bool
        if it should run serially (i.e. not parallely, mostly for debugging)
    """
    args = []
    for prf_file in find_in_bids(analysis_dir, task=task, modality=input, extension='.pkl', generator=True):
        if input.startswith('ieeg'):
            funct = estimate_ieeg_prf

        elif input.startswith('bold'):
            funct = estimate_bold_prf

        else:
            raise ValueError(f'Unknown modality {input}')

        args.append((funct, prf_file, method))

    if noparallel:
        for arg in args:
            args[0](*arg[1:])
    else:
        with Pool() as p:
            p.starmap(arg[0], arg[1:])


def estimate_ieeg_prf(ieeg_file, method, freq=(60, 80)):
    with ieeg_file.open('rb') as f:
        data = load(f)

    stimuli = data.attr['stimuli']

    data = select(data, freq=freq)
    data = math(data, operator_name='mean', axis='time')
    data = math(data, operator_name='mean', axis='freq')
    data = concatenate(data, 'trial')

    compute_prf(ieeg_file, data.data[0], data.chan[0], stimuli, method)

    return replace_extension(ieeg_file, 'prf.tsv')


def estimate_bold_prf(bold_file, method):
    prf_task = Task(bold_file)
    stimuli = read_prf_stimuli(prf_task)

    region_idx = 11143
    aparc = nload(str(data_aparc))

    img = nload(str(prf_task.filename))
    mri = img.get_data()

    roi = select_region(aparc, lambda x: x == region_idx)
    roi_idx = apply_affine(img.affine, array(where(roi.get_data() > 0)).T)
    roi_str = [f'{xyz[0]:.2f},{xyz[1]:.2f},{xyz[2]:.2f}' for xyz in roi_idx]

    dat = mri[roi.get_data() > 0, :]

    output = compute_prf(bold_file, dat, roi_str, stimuli, method)

    images = ['X', 'Y', 'SIGMA', 'BETA']
    for i in range(len(output)):
        nii_file = replace_extension(bold_file, 'prf' + images[i] + '.nii.gz')

        out = zeros(mri.shape[:3])
        out[roi.get_data() > 0] = output[i]
        x_img = Nifti1Image(out, img.affine)
        x_img.to_filename(str(nii_file))


def compute_prf(input_file, dat, indices, stimuli, method):

    tsv_file = replace_extension(input_file, 'prf.tsv')

    x = []
    y = []
    sigma = []
    beta = []

    with tsv_file.open('w') as f:
        f.write(f'channel\tx\ty\tsigma\tbeta\n')
        for i, index in enumerate(indices):
            if method == 'analyzePRF':
                output = fit_analyzePRF(stimuli, dat[i, :])
                f.write(f'{index}\t{output.x[0]}\t{output.x[1]}\t{output.x[2]}\t{output.x[3]}\n')
                results = output.x

            elif method == 'popeye':
                output = fit_popeye(stimuli, dat[i, :])
                f.write(f'{index}\t{output.estimate[0]}\t{output.estimate[1]}\t{output.estimate[2]}\t{output.estimate[3]}\n')
                results = output.estimate

            x.append(results[0])
            y.append(results[1])
            sigma.append(results[2])
            beta.append(results[3])

            f.flush()

    return array(x), array(y), array(sigma), array(beta)
