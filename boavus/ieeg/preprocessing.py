from multiprocessing import Pool
from logging import getLogger
from pickle import load, dump
from numpy import empty, arange
from wonambi.trans import montage, filter_
from wonambi.trans.select import _create_subepochs

from bidso.find import find_in_bids
from bidso.utils import add_underscore


lg = getLogger(__name__)


def main(analysis_dir, reref='average', noparallel=False):
    """
    read in the data for move and rest

    Parameters
    ----------
    analysis_dir : path

    reref : str
        'average' or 'regression'
    noparallel : bool
        if it should run serially (i.e. not parallely, mostly for debugging)
    """
    args = []
    for ieeg_file in find_in_bids(analysis_dir, modality='ieeg', extension='.eeg', generator=True):
        lg.debug(f'reading {ieeg_file}')
        args.append((ieeg_file, reref))

    if noparallel:
        for arg in args:
            preprocess_ecog(*arg)
    else:
        with Pool() as p:
            p.starmap(preprocess_ecog, args)


def preprocess_ecog(ieeg_file, reref):
    """
    TODO
    ----
    labels_in_roi = find_labels_in_regions(electrodes, regions)
    clean_roi_labels = [label for label in clean_labels if label in labels_in_roi]
    data = select(data, chan=clean_roi_labels)
    """
    with ieeg_file.open('rb') as f:
        data = load(f)

    data = filter_(data, ftype='notch')
    data = montage(data, ref_to_avg=True, method=reref)
    data = make_segments(data)

    output_file = add_underscore(ieeg_file, 'proc.pkl')
    with output_file.open('wb') as f:
        dump(data, f)


def make_segments(dat):
    trials = []
    for d in dat.data:
        v = _create_subepochs(d, 1023, 1023)
        for i in range(v.shape[1]):
            trials.append(v[:, i, :])

    out = dat._copy(axis=False)
    out.data = empty(len(trials), dtype='O')
    out.axis['chan'] = empty(len(trials), dtype='O')
    out.axis['time'] = empty(len(trials), dtype='O')

    for i, trial in enumerate(trials):
        out.data[i] = trial
        out.axis['time'][i] = arange(i * 1023, i * 1023 + 1023) / dat.s_freq
        out.axis['chan'][i] = dat.axis['chan'][0]

    return out
