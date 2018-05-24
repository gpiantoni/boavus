from pickle import load
from numpy import ones, hstack, sign, array, NaN
from numpy import concatenate as np_concatenate
from scipy.stats import ttest_ind, pearsonr

from wonambi.trans import math, concatenate, select
from wonambi.datatype import Data

from bidso.find import find_in_bids
from bidso.utils import replace_underscore


def main(analysis_dir, frequency_low=65, frequency_high=96, baseline=False,
         method='dh2012', measure='dh2012_r2'):
    """
    compare the two conditions in percent change or zstat

    Parameters
    ----------
    analysis_dir : path

    frequency_low : float

    frequency_high : float

    baseline : bool
        if you want to substract baseline
    method : str
        "dh2012"
    measure : str
        "dh2012_r2"
    """
    frequency = [frequency_low, frequency_high]
    for move_file in find_in_bids(analysis_dir, modality='freqmove', extension='.pkl', generator=True):
        with move_file.open('rb') as f:
            dat_move = load(f)
        rest_file = replace_underscore(move_file, 'freqrest.pkl')
        with rest_file.open('rb') as f:
            dat_rest = load(f)

        if baseline:
            dat_move, dat_rest = correct_baseline(dat_move, dat_rest, frequency)

        hfa_move = merge(dat_move, method, frequency)
        hfa_rest = merge(dat_rest, method, frequency)

        if measure == 'diff':
            ecog_stats = compute_diff(hfa_move, hfa_rest)
        elif measure == 'percent':
            ecog_stats = compute_percent(hfa_move, hfa_rest)
        elif measure in ('zstat', 'dh2012_t'):  # identical
            ecog_stats = compute_zstat(hfa_move, hfa_rest)
            if measure == 'dh2012_t':
                ecog_stats.data[0] *= -1  # opposite sign in dh2012's script

        elif measure == 'dh2012_r2':
            ecog_stats = calc_dh2012_values(hfa_move, hfa_rest, measure)

        # need to check pvalues
        if True:
            pvalues = calc_dh2012_values(hfa_move, hfa_rest, 'dh2012_pv')
        else:
            pvalues = [NaN, ] * ecog_stats.number_of('chan')[0]

        percent_file = replace_underscore(move_file, 'compare.tsv')
        with percent_file.open('w') as f:
            f.write('channel\tmeasure\tpvalue\n')
            for i, chan in enumerate(ecog_stats.chan[0]):
                f.write(f'{chan}\t{ecog_stats(trial=0, chan=chan)}\t{pvalues(trial=0, chan=chan)}\n')


def merge(freq, method, frequency):

    freq = select(freq, freq=frequency)

    if method == '1a':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif method == '1b':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='mean', axis='time')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif method == '1c':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='time')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif method == '1d':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='dB')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif method == '2a':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif method == '2b':
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif method == '2c':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif method == '2d':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='dB')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif method == '3a':
        freq = concatenate(freq, axis='time')
        # values per time point
        out = math(freq, operator_name='mean', axis='freq')

    elif method == '3b':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='dB')
        # values per time point
        out = math(freq, operator_name='mean', axis='freq')

    elif method == '3c':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # values per time point
        out = math(freq, operator_name='dB')

    elif method == 'dh2012':
        # identical to 3b, but use log instead of dB
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='log')
        # values per time point
        out = math(freq, operator_name='mean', axis='freq')

    return out


def compute_diff(hfa_move, hfa_rest):
    hfa_move.data[0] -= hfa_rest.data[0]
    return Data(hfa_move.data[0][:, 0], hfa_move.s_freq, chan=hfa_move.chan[0])


def compute_percent(hfa_move, hfa_rest):
    x_move = math(hfa_move, operator_name='mean', axis=hfa_move.list_of_axes[1])
    x_rest = math(hfa_rest, operator_name='mean', axis=hfa_move.list_of_axes[1])

    perc = (x_move(trial=0) - x_rest(trial=0)) / x_rest(trial=0) * 100
    data_perc = Data(perc, hfa_move.s_freq, chan=hfa_move.chan[0])

    return data_perc


def compute_zstat(hfa_move, hfa_rest):
    """
    TODO
    ----
    You can compute zstat by taking diff and then divide by standard deviation
    """
    zstat = ttest_ind(hfa_move.data[0], hfa_rest.data[0], axis=1, equal_var=False).statistic

    return Data(zstat, hfa_move.s_freq, chan=hfa_move.chan[0])


def calc_dh2012_values(hfa_move, hfa_rest, measure):
    """This is the exact translation of dh2012's Matlab code
    """
    ecog = hstack((hfa_move.data[0], hfa_rest.data[0]))
    stim = hstack((ones(hfa_move.data[0].shape[1]), ones(hfa_rest.data[0].shape[1]) * 0))

    val = []
    for ecog_chan in ecog:
        [r, p] = pearsonr(ecog_chan, stim)

        if measure == 'dh2012_r2':
            val.append(r ** 2 * sign(r))

        elif measure == 'dh2012_pv':
            val.append(p)

    return Data(array(val), hfa_move.s_freq, chan=hfa_move.chan[0])


def correct_baseline(freq_move, freq_rest, frequency):
    move = select(freq_move, freq=frequency)
    rest = select(freq_rest, freq=frequency)

    merged = merge_datasets(move, rest)
    merged = concatenate(merged, 'time')
    baseline = math(merged, operator_name='mean', axis='time')

    move.data[0] /= baseline.data[0][:, None, :]
    rest.data[0] /= baseline.data[0][:, None, :]
    return move, rest


def merge_datasets(dat1, dat2):
    both = dat1._copy(axis=False)
    both.data = np_concatenate((dat1.data, dat2.data))
    both.axis['time'] = np_concatenate((dat1.time, dat2.time))
    both.axis['chan'] = np_concatenate((dat1.chan, dat2.chan))
    both.axis['freq'] = np_concatenate((dat1.freq, dat2.freq))
    return both
