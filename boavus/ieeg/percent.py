from wonambi.trans import math
from wonambi.datatype import Data


def total_percent():
    # it's compute here with all the electrodes (also the non active ones)
    ecog_stats = percent_ecog(hfa_move, hfa_rest)
    all_chan = ecog_stats.chan[0]

    """
    hfa_move, hfa_rest = _select_active(hfa_move, hfa_rest)
    active_chan = hfa_move.chan[0]
    """
    active = ' (todo)'
    all_fig = []
    for chan in all_chan:
        fig = plot_psd(chan, active, freq_move, freq_rest, ecog_stats)
        all_fig.append(fig)

    return all_fig, all_chan

def percent_ecog(hfa_move, hfa_rest):
    x_move = math(hfa_move, operator_name='mean', axis='time')
    x_rest = math(hfa_rest, operator_name='mean', axis='time')

    perc = (x_move(trial=0) - x_rest(trial=0)) / x_rest(trial=0) * 100
    data_perc = Data(perc, hfa_move.s_freq, chan=hfa_move.chan[0])

    return data_perc
