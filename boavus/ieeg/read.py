from pickle import dump
from wonambi.trans import math, filter_
from logging import getLogger
from numpy import mean, std
from wonambi import Dataset

from bidso import Task, Electrodes
from bidso.find import find_in_bids, find_root

lg = getLogger(__name__)


def main(bids_dir, analysis_dir, acquisition='*regions', markers_on='49',
         markers_off='48', minimalduration=20, reject_chan_thresh=3):
    """
    read in the data for move and rest

    Notch filter here

    Parameters
    ----------
    bids_dir : path

    analysis_dir : path

    acquisition : str
        type of electrodes
    markers_on : str
        marker start
    markers_off : str
        marker end
    minimalduration : float
        minimal duration of each block
    reject_chan_thresh : float
        threshold std to reject channels
    """
    for ieeg_file in find_in_bids(bids_dir, modality='ieeg', extension='.eeg', generator=True):
        lg.debug(f'reading {ieeg_file}')
        try:
            dat_move, dat_rest = read_ieeg(
                ieeg_file, acquisition,
                markers_on, markers_off, minimalduration, reject_chan_thresh)
        except FileNotFoundError as err:
            lg.warning(f'Skipping {ieeg_file.stem}: {err}')
            continue

        output_task = Task(ieeg_file)
        output_task.extension = '.pkl'
        output_task.task += 'move'
        output_file = output_task.get_filename(analysis_dir)

        output_file.parent.mkdir(exist_ok=True, parents=True)
        with output_file.open('wb') as f:
            dump(dat_move, f)

        output_task = Task(ieeg_file)
        output_task.extension = '.pkl'
        output_task.task += 'rest'
        output_file = output_task.get_filename(analysis_dir)

        with output_file.open('wb') as f:
            dump(dat_rest, f)


def read_ieeg(filename, acquisition, markers_on, markers_off, minimalduration,
              reject_chan_thresh):
    d = Dataset(filename, bids=True)
    s_freq = d.header['s_freq']

    # this might be in bids or in wonambi
    bids_root = find_root(d.filename)
    electrode_file = find_in_bids(bids_root, subject=d.dataset.task.subject,
                                  acquisition=acquisition,
                                  modality='electrodes', extension='.tsv')
    electrodes = Electrodes(electrode_file)

    move_times, rest_times = read_markers(
        d,
        marker_on=markers_on,
        marker_off=markers_off,
        minimalduration=minimalduration,
        )
    # convert to s_freq
    rest_times = [[int(x0 * s_freq) for x0 in x1] for x1 in rest_times]
    move_times = [[int(x0 * s_freq) for x0 in x1] for x1 in move_times]

    # only channels with electrodes
    elec_names = [x['name'] for x in electrodes.electrodes.tsv]
    elec_names = [x for x in elec_names if x in d.header['chan_name']]  # exclude elec location that have no corresponding channel
    data = d.read_data(chan=elec_names, begsam=rest_times[0][0], endsam=rest_times[1][-1])
    data = filter_(data, ftype='notch')

    clean_labels = reject_channels(data, reject_chan_thresh)
    lg.debug(f'Clean channels {len(clean_labels)} / {len(elec_names)}')

    data = d.read_data(chan=clean_labels, begsam=move_times[0], endsam=move_times[1])
    data = filter_(data, ftype='notch')
    dat_move = d.read_data(begsam=move_times[0], endsam=move_times[1], chan=clean_labels)
    dat_rest = d.read_data(begsam=rest_times[0], endsam=rest_times[1], chan=clean_labels)

    return dat_move, dat_rest


def reject_channels(dat, reject_chan_thresh):
    dat_std = math(dat, operator_name='std', axis='time')
    THRESHOLD = reject_chan_thresh
    x = dat_std.data[0]
    thres = [mean(x) + THRESHOLD * std(x)]
    clean_labels = list(dat_std.chan[0][dat_std.data[0] < thres])
    return clean_labels


def read_markers(d, marker_on, marker_off, minimalduration):
    markers = d.read_markers()
    move_start = [mrk['start'] for mrk in markers if mrk['name'] == marker_on]
    move_end = [mrk['end'] for mrk in markers if mrk['name'] == marker_on]

    rest_start = [mrk['start'] for mrk in markers if mrk['name'] == marker_off if (mrk['end'] - mrk['start']) > minimalduration]
    rest_end = [mrk['end'] for mrk in markers if mrk['name'] == marker_off if (mrk['end'] - mrk['start']) > minimalduration]
    return (move_start, move_end), (rest_start, rest_end)
