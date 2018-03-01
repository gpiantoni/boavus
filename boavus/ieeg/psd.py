from pickle import load, dump
from wonambi.trans import select, math, timefrequency, concatenate
from logging import getLogger
from multiprocessing import Pool
from numpy import mean, array, log10
import plotly.graph_objs as go

from bidso.find import find_in_bids
from bidso.utils import replace_underscore

lg = getLogger(__name__)

PARAMETERS = {
    'duration': 1,
    'taper': 'dpss',
    'halfbandwidth': 2,
    'parallel': True,
    }


def main(analysis_dir):

    args = []
    for cond in ('move', 'rest'):
        for ieeg_file in find_in_bids(analysis_dir, modality=cond, extension='.pkl', generator=True):
            args.append((ieeg_file, cond))

    if PARAMETERS['parallel']:
        with Pool() as p:
            p.starmap(save_frequency, args)
    else:
        for arg in args:
            save_frequency(*arg)


def save_frequency(ieeg_file, cond):
    with ieeg_file.open('rb') as f:
        dat = load(f)

    freq = compute_frequency(dat)

    output_file = replace_underscore(ieeg_file, 'freq' + cond + '.pkl')
    with output_file.open('wb') as f:
        dump(freq, f)


def compute_frequency(dat):
    """Remove epochs which have very high activity in high-freq range, then
    average over time (only high-freq range) and ALL the frequencies."""

    dat = timefrequency(
        dat,
        method='spectrogram',
        taper=PARAMETERS['taper'],
        duration=PARAMETERS['duration'],
        halfbandwidth=PARAMETERS['halfbandwidth'],
        )

    return dat
