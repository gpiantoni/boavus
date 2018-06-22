from pickle import load
from logging import getLogger
from multiprocessing import Pool

from bidso.find import find_in_bids
from bidso.utils import replace_extension
from wonambi.trans import select, math, concatenate

from .core.least_squares import fit_analyzePRF
from .core.popeye import fit_popeye

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
    for ieeg_file in find_in_bids(analysis_dir, task=task, modality=input, extension='.pkl', generator=True):
        args.append((ieeg_file, method))

    if noparallel:
        for arg in args:
            estimate_prf(*arg)
    else:
        with Pool() as p:
            p.starmap(estimate_prf, args)


def estimate_prf(ieeg_file, method):
    with ieeg_file.open('rb') as f:
        data = load(f)

    stimuli = data.attr['stimuli']

    data = select(data, freq=(60, 80))
    data = math(data, operator_name='mean', axis='time')
    data = math(data, operator_name='mean', axis='freq')
    data = concatenate(data, 'trial')

    compute_prf(ieeg_file, data.data[0], data.chan[0], stimuli, method)


def compute_prf(input_file, dat, indices, stimuli, method):

    tsv_file = replace_extension(input_file, 'prf.tsv')

    with tsv_file.open('w') as f:
        f.write(f'channel\tx\ty\tsigma\tbeta\n')
        for i, index in enumerate(indices):
            if method == 'analyzePRF':
                result = fit_analyzePRF(stimuli, dat[i, :])
                f.write(f'{index}\t{result.x[0]}\t{result.x[1]}\t{result.x[2]}\t{result.x[3]}\n')

            elif method == 'popeye':
                result = fit_popeye(stimuli, dat[i, :])
                f.write(f'{index}\t{result.estimate[0]}\t{result.estimate[1]}\t{result.estimate[2]}\t{result.estimate[3]}\n')

            f.flush()
