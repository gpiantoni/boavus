from pickle import load, dump
from logging import getLogger
from multiprocessing import Pool
from numpy import empty
from scipy.signal import welch

from wonambi.trans import timefrequency
from wonambi.datatype import ChanFreq
from bidso.find import find_in_bids
from bidso.utils import replace_underscore

lg = getLogger(__name__)

PARAMETERS = {
    'method': 'spectrogram',
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

    if PARAMETERS['method'] == 'spectrogram':
        freq = compute_frequency(dat)
    elif PARAMETERS['method'] == 'dh2012':
        freq = compute_welch_dh2012(dat)

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


def compute_welch_dh2012(data):
    NPERSEG = 102
    NFFT = 512

    freq = ChanFreq()
    freq.s_freq = data.s_freq
    freq.start_time = data.start_time
    freq.axis['chan'] = data.axis['chan']
    freq.axis['freq'] = empty(data.number_of('trial'), dtype='O')
    freq.data = empty(data.number_of('trial'), dtype='O')

    for i, x in enumerate(data.data):
        [f, Pxx] = welch(x, window='hamming', fs=data.s_freq, nperseg=NPERSEG,
                         nfft=NFFT, noverlap=0, detrend=False)
        freq.freq[i] = f
        freq.data[i] = Pxx

    return freq
