from pickle import load
from numpy import NaN
from scipy.stats import ttest_ind

from wonambi.trans import math, concatenate, select
from wonambi.datatype import Data

from bidso.find import find_in_bids
from bidso.utils import replace_underscore


PARAMETERS = {
    'frequency': [
        65,
        95,
        ],
    'method': '1a',
    'measure': 'percent',
    }


def main(analysis_dir):
    for move_file in find_in_bids(analysis_dir, modality='freqmove', extension='.pkl', generator=True):
        with move_file.open('rb') as f:
            dat_move = load(f)
        rest_file = replace_underscore(move_file, 'freqrest.pkl')
        with rest_file.open('rb') as f:
            dat_rest = load(f)

        hfa_move = merge(dat_move)
        hfa_rest = merge(dat_rest)

        if PARAMETERS['measure'] == 'percent':
            ecog_stats = compute_percent(hfa_move, hfa_rest)
        elif PARAMETERS['measure'] == 'zstat':
            ecog_stats = compute_zstat(hfa_move, hfa_rest)

        if hfa_move.data[0].shape[1] > 1:
            pvalues = ttest_ind(hfa_move(trial=0), hfa_rest(trial=0), axis=1).pvalue
        else:
            pvalues = [NaN, ] * ecog_stats.number_of('chan')[0]

        percent_file = replace_underscore(move_file, 'compare.tsv')
        with percent_file.open('w') as f:
            f.write('channel\tmeasure\tpvalue\n')
            for i, chan in enumerate(ecog_stats.chan[0]):
                f.write(f'{chan}\t{ecog_stats(trial=0, chan=chan)}\t{pvalues[i]}\n')


def merge(freq):

    freq = select(freq, freq=PARAMETERS['frequency'])

    if PARAMETERS['method'] == '1a':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif PARAMETERS['method'] == '1b':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='mean', axis='time')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif PARAMETERS['method'] == '1c':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='time')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif PARAMETERS['method'] == '1d':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='dB')
        # only one value
        out = Data(freq.data[0][:, None], freq.s_freq, chan=freq.chan[0], time=(0, ))

    elif PARAMETERS['method'] == '2a':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif PARAMETERS['method'] == '2b':
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif PARAMETERS['method'] == '2c':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='dB')
        freq = math(freq, operator_name='mean', axis='freq')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif PARAMETERS['method'] == '2d':
        freq = math(freq, operator_name='mean', axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        freq = math(freq, operator_name='dB')
        # one value per trial
        out = concatenate(freq, axis='trial')

    elif PARAMETERS['method'] == '3a':
        freq = concatenate(freq, axis='time')
        # values per time point
        out = math(freq, operator_name='mean', axis='freq')

    elif PARAMETERS['method'] == '3b':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='dB')
        # values per time point
        out = math(freq, operator_name='mean', axis='freq')

    elif PARAMETERS['method'] == '3c':
        freq = concatenate(freq, axis='time')
        freq = math(freq, operator_name='mean', axis='freq')
        # values per time point
        out = math(freq, operator_name='dB')

    return out


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
    zstat = ttest_ind(hfa_move.data[0], hfa_rest.data[0], axis=1).statistic

    return Data(zstat, hfa_move.s_freq, chan=hfa_move.chan[0])
