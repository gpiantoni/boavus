from pickle import load
from wonambi.trans import math
from wonambi.datatype import Data

from bidso.find import find_in_bids
from bidso.utils import replace_underscore


def main(output_dir):

    for hfa_move_file in find_in_bids(output_dir, modality='hfamove', extension='.pkl', generator=True):
        with hfa_move_file.open('rb') as f:
            hfa_move = load(f)
        hfa_rest_file = replace_underscore(hfa_move_file, 'hfarest.pkl')
        with hfa_rest_file.open('rb') as f:
            hfa_rest = load(f)

        ecog_stats = compute_zstat(hfa_move, hfa_rest)

        percent_file = replace_underscore(hfa_move_file, 'percent.tsv')
        with percent_file.open('w') as f:
            f.write('channel\tzstat\n')
            for chan in ecog_stats.chan[0]:
                f.write(f'{chan}\t{ecog_stats(trial=0, chan=chan)}\n')


def compute_zstat(hfa_move, hfa_rest):
    ecog_stats = ttest_ind(hfa_move.data[0], hfa_rest.data[0], axis=1).statistic
