from pickle import load
from scipy.stats import ttest_ind

from wonambi.trans import math
from wonambi.datatype import Data

from bidso.find import find_in_bids
from bidso.utils import replace_underscore


PARAMETERS = {
    'measure': 'percent',
    }


def main(output_dir):

    for hfa_move_file in find_in_bids(output_dir, modality='hfamove', extension='.pkl', generator=True):
        with hfa_move_file.open('rb') as f:
            hfa_move = load(f)
        hfa_rest_file = replace_underscore(hfa_move_file, 'hfarest.pkl')
        with hfa_rest_file.open('rb') as f:
            hfa_rest = load(f)

        if PARAMETERS['measure'] == 'percent':
            ecog_stats = compute_percent(hfa_move, hfa_rest)
        elif PARAMETERS['measure'] == 'zstat':
            ecog_stats = compute_zstat(hfa_move, hfa_rest)

        percent_file = replace_underscore(hfa_move_file, 'compare.tsv')
        with percent_file.open('w') as f:
            f.write(f'channel\t{PARAMETERS["measure"]}\n')
            for chan in ecog_stats.chan[0]:
                f.write(f'{chan}\t{ecog_stats(trial=0, chan=chan)}\n')

    """
    # it's compute here with all the electrodes (also the non active ones)
    ecog_stats = percent_ecog(hfa_move, hfa_rest)
    all_chan = ecog_stats.chan[0]

    hfa_move, hfa_rest = _select_active(hfa_move, hfa_rest)
    active_chan = hfa_move.chan[0]
    active = ' (todo)'
    all_fig = []
    for chan in all_chan:
        fig = plot_psd(chan, active, freq_move, freq_rest, ecog_stats)
        all_fig.append(fig)

    return all_fig, all_chan
    """


def compute_percent(hfa_move, hfa_rest):
    x_move = math(hfa_move, operator_name='mean', axis='time')
    x_rest = math(hfa_rest, operator_name='mean', axis='time')

    perc = (x_move(trial=0) - x_rest(trial=0)) / x_rest(trial=0) * 100
    data_perc = Data(perc, hfa_move.s_freq, chan=hfa_move.chan[0])

    return data_perc


def compute_zstat(hfa_move, hfa_rest):
    zstat = ttest_ind(hfa_move.data[0], hfa_rest.data[0], axis=1).statistic

    return Data(zstat, hfa_move.s_freq, chan=hfa_move.chan[0])
