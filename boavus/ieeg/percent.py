from wonambi.trans import math
from wonambi.datatype import Data


def percent_ecog(hfa_move, hfa_rest):
    x_move = math(hfa_move, operator_name='mean', axis='time')
    x_rest = math(hfa_rest, operator_name='mean', axis='time')

    perc = (x_move(trial=0) - x_rest(trial=0)) / x_rest(trial=0) * 100
    data_perc = Data(perc, hfa_move.s_freq, chan=hfa_move.chan[0])

    return data_perc
