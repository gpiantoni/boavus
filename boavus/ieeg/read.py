from logging import getLogger
from numpy import mean, std
from pickle import dump
from wonambi import Dataset
from wonambi.trans import math, filter_, concatenate
from bidso import Task, Electrodes

lg = getLogger(__name__)


def read_ieeg_block(filename, electrode_file, cond, minimalduration, output_dir):
    d = Dataset(filename, bids=True)
    markers = d.read_markers()

    electrodes = Electrodes(electrode_file)
    elec_names = [x['name'] for x in electrodes.electrodes.tsv]
    elec_names = [x for x in elec_names if x in d.header['chan_name']]  # exclude elec location that have no corresponding channel

    clean_labels = _reject_channels(d, elec_names, cond, minimalduration)

    outputs = []
    for cond_name, cond_mrk in cond.items():
        block_beg = []
        block_end = []

        for mrk in markers:

            if mrk['name'] in cond_mrk:
                dur = (mrk['end'] - mrk['start'])
                if dur >= minimalduration:
                    block_beg.append(mrk['start'])
                    block_end.append(mrk['end'])

        data = d.read_data(begtime=block_beg, endtime=block_end, chan=clean_labels)

        output_task = Task(filename)
        output_task.extension = '.pkl'
        output_task.task += cond_name
        output_file = output_dir / output_task.get_filename()
        with output_file.open('wb') as f:
            dump(data, f)
        outputs.append(output_file)

    return outputs


def _reject_channels(d, elec_names, cond, minimalduration):
    markers = d.read_markers()
    block_beg = []
    block_end = []
    for mrk in markers:
        if mrk['name'] in cond.values():
            dur = (mrk['end'] - mrk['start'])
            if dur >= minimalduration:

                block_beg.append(mrk['start'])
                block_end.append(mrk['end'])

    data = d.read_data(chan=elec_names, begtime=block_beg, endtime=block_end)
    data = concatenate(data, 'time')

    clean_labels = reject_channels(data, 3)
    return clean_labels


def read_bids_data(filename, electrode_file, cond):

    all_data = read_ieeg(filename, electrode_file)
    conds = ['move', 'rest']

    outputs = []
    for cond, data in zip(conds, all_data):
        output_task = Task(filename)
        output_task.extension = '.pkl'
        output_task.task += cond
        output_file = output_task.get_filename(analysis_dir)

        output_file.parent.mkdir(exist_ok=True, parents=True)
        with output_file.open('wb') as f:
            dump(data, f)

        outputs.append(output_file)

    return outputs


def read_ieeg(filename, electrode_file, markers_on='49', markers_off='48',
              minimalduration=20, reject_chan_thresh=3):

    d = Dataset(filename, bids=True)
    s_freq = d.header['s_freq']
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
