from pickle import load, dump
from logging import getLogger
from multiprocessing import Pool
from numpy import empty, array
from scipy.signal import welch

from wonambi.trans import timefrequency
from wonambi.datatype import ChanTimeFreq
from bidso.find import find_in_bids
from bidso.utils import replace_extension

lg = getLogger(__name__)

TAPER = 'dpss'
HALFBANDWIDTH = 2


def main(analysis_dir, method="spectrogram", duration=1, noparallel=False):
    """
    compute psd for two conditions

    Parameters
    ----------
    analysis_dir : path

    method : str
        "spectrogram" or "dh2012"
    duration : float
        duration of the trials
    noparallel : bool
        if it should run serially (i.e. not parallely, mostly for debugging)
    """
    args = []
    for ieeg_file in find_in_bids(analysis_dir, modality='ieegproc', extension='.pkl', generator=True):
        args.append((ieeg_file, method, duration))

    if noparallel:
        for arg in args:
            save_frequency(*arg)
    else:
        with Pool() as p:
            p.starmap(save_frequency, args)


def save_frequency(ieeg_file, method, duration):
    with ieeg_file.open('rb') as f:
        dat = load(f)

    if method == 'spectrogram':
        freq = compute_frequency(dat, duration)
    elif method == 'dh2012':
        freq = compute_welch_dh2012(dat, duration)

    output_file = replace_extension(ieeg_file, 'psd.pkl')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open('wb') as f:
        dump(freq, f)


def compute_frequency(dat, duration):
    """Remove epochs which have very high activity in high-freq range, then
    average over time (only high-freq range) and ALL the frequencies."""

    dat = timefrequency(
        dat,
        method='spectrogram',
        taper=TAPER,
        duration=duration,
        halfbandwidth=HALFBANDWIDTH,
        )

    return dat


def compute_welch_dh2012(data, duration):
    NPERSEG = 102
    NFFT = data.s_freq * duration

    freq = ChanTimeFreq()
    freq.s_freq = data.s_freq
    freq.start_time = data.start_time
    freq.axis['chan'] = data.axis['chan']
    freq.axis['freq'] = empty(data.number_of('trial'), dtype='O')
    freq.axis['time'] = empty(data.number_of('trial'), dtype='O')
    freq.data = empty(data.number_of('trial'), dtype='O')

    for i, x in enumerate(data.data):
        [f, Pxx] = welch(x, window='hamming', fs=data.s_freq, nperseg=NPERSEG,
                         nfft=NFFT, noverlap=0, detrend=False)
        freq.freq[i] = f
        freq.time[i] = array([i, ], dtype='float')
        freq.data[i] = Pxx[:, None, :]

    return freq
