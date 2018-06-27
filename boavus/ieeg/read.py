from pickle import dump
from wonambi.trans import math, filter_
from logging import getLogger
from numpy import array, mean, std, load
from scipy.io import loadmat
from wonambi import Dataset

from bidso import Task, Electrodes
from bidso.find import find_in_bids, find_root

lg = getLogger(__name__)


def main(bids_dir, analysis_dir, task='motor', acquisition='*regions', markers_on='49',
         markers_off='48', minimalduration=20, reject_chan_thresh=3,
         prestim=0.5, poststim=1.5):
    """
    read in the data for move and rest

    Notch filter here

    Parameters
    ----------
    bids_dir : path

    analysis_dir : path

    task : str
        task to read in
    acquisition : str
        (motor) type of electrodes
    markers_on : str
        (motor) marker start
    markers_off : str
        (motor) marker end
    minimalduration : float
        (motor) minimal duration of each block
    reject_chan_thresh : float
        (motor) threshold std to reject channels
    prestim : float
        (bair) prestimulus time
    poststim : float
        (bair) poststimulus time
    """
    for ieeg_file in find_in_bids(bids_dir, task=task, modality='ieeg', extension='.eeg', generator=True):
        lg.debug(f'reading {ieeg_file}')

        output_task = Task(ieeg_file)
        if output_task.task.startswith('motor'):

            try:
                all_data = read_ieeg(
                    ieeg_file, acquisition,
                    markers_on, markers_off, minimalduration, reject_chan_thresh)
            except FileNotFoundError as err:
                lg.warning(err)
            conds = ['move', 'rest']

        elif output_task.task.startswith('bair'):

            prestim = float(prestim)
            poststim = float(poststim)

            d = Dataset(ieeg_file, bids=True)
            events = array([x['start'] for x in d.read_markers()])

            data = d.read_data(
                begtime=list(events - prestim),
                endtime=list(events + poststim + 1 / d.header['s_freq']))
            data.attr['stimuli'] = read_prf_stimuli(d.dataset.task)
            all_data = (data, )
            conds = ['', ]

        else:
            raise ValueError(f'Unknown task "{output_task.task}" for {ieeg_file}')

        for cond, data in zip(conds, all_data):
            output_task = Task(ieeg_file)
            output_task.extension = '.pkl'
            output_task.task += cond
            output_file = output_task.get_filename(analysis_dir)

            output_file.parent.mkdir(exist_ok=True, parents=True)
            with output_file.open('wb') as f:
                dump(data, f)


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


def read_prf_stimuli(task):
    """Read stimuli to compute the PRF

    Parameters
    ----------
    task : instance of bidso.Task
        task containing the events and filename
    """
    stimuli_dir = find_root(task.filename) / 'stimuli'

    stim_file = stimuli_dir / task.events.tsv[0]['stim_file']
    if stim_file.suffix == '.npy':
        stimuli = load(stim_file)

    elif stim_file.suffix == '.mat':
        mat = loadmat(stim_file)
        stimuli = mat['stimulus'][0, 0]['images']

    stim_file_index = array([int(x['stim_file_index']) - 1 for x in task.events.tsv])
    stimuli = stimuli[:, :, stim_file_index]

    return stimuli
