from pickle import load
from scipy.stats import ttest_ind

from wonambi.trans import math
from wonambi.datatype import Data

from bidso.find import find_in_bids
from bidso.utils import replace_underscore


PARAMETERS = {
    'log': False,
    'measure': 'percent',
    }


def main(analysis_dir):
    """
    TODO
    ----
    When computing hfa, you can:
    1) log, then mean over frequency band
    2) mean over frequency band, then log

    We now use 2) but we should implement 1)
    """
    for hfa_move_file in find_in_bids(analysis_dir, modality='hfamove', extension='.pkl', generator=True):
        with hfa_move_file.open('rb') as f:
            hfa_move = load(f)
        hfa_rest_file = replace_underscore(hfa_move_file, 'hfarest.pkl')
        with hfa_rest_file.open('rb') as f:
            hfa_rest = load(f)

        if PARAMETERS['log']:
            hfa_move = math(hfa_move, operator_name='log')
            hfa_rest = math(hfa_rest, operator_name='log')

        if PARAMETERS['measure'] == 'percent':
            ecog_stats = compute_percent(hfa_move, hfa_rest)
        elif PARAMETERS['measure'] == 'zstat':
            ecog_stats = compute_zstat(hfa_move, hfa_rest)

        pvalues = ttest_ind(hfa_move(trial=0), hfa_rest(trial=0), axis=1).pvalue

        percent_file = replace_underscore(hfa_move_file, 'compare.tsv')
        with percent_file.open('w') as f:
            f.write('channel\tmeasure\tpvalue\n')
            for i, chan in enumerate(ecog_stats.chan[0]):
                f.write(f'{chan}\t{ecog_stats(trial=0, chan=chan)}\t{pvalues[i]}\n')


def compute_percent(hfa_move, hfa_rest):
    x_move = math(hfa_move, operator_name='mean', axis='time')
    x_rest = math(hfa_rest, operator_name='mean', axis='time')

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
