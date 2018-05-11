from pickle import dump
from wonambi.trans import select, montage, math, filter_
from logging import getLogger
from numpy import mean, std
from wonambi import Dataset

from bidso import Task, Electrodes
from bidso.find import find_in_bids, find_root
from bidso.utils import replace_extension

from ..bidso import find_labels_in_regions

lg = getLogger(__name__)

PARAMETERS = {
    'electrodes': {
        'acquisition': '*regions',
        },
    'markers': {
        'on': '49',
        'off': '48',
        'minimalduration': 20,
        },
    'regions': [],
    'reject': {
        'chan': {
            'threshold_std': 3,
            },
        },
    }


def main(bids_dir, analysis_dir):

    for ieeg_file in find_in_bids(bids_dir, modality='ieeg', extension='.eeg', generator=True):
        lg.debug(f'reading {ieeg_file}')
        try:
            dat_move, dat_rest = preprocess_ecog(ieeg_file)
        except FileNotFoundError as err:
            lg.warning(f'Skipping {ieeg_file.stem}: {err}')
            continue

        output_file = replace_extension(Task(ieeg_file).get_filename(analysis_dir), '_move.pkl')
        output_file.parent.mkdir(exist_ok=True, parents=True)
        with output_file.open('wb') as f:
            dump(dat_move, f)
        output_file = replace_extension(Task(ieeg_file).get_filename(analysis_dir), '_rest.pkl')
        with output_file.open('wb') as f:
            dump(dat_rest, f)


def preprocess_ecog(filename):
    d = Dataset(filename, bids=True)
    s_freq = d.header['s_freq']

    # this might be in bids or in wonambi
    bids_root = find_root(d.filename)
    electrode_file = find_in_bids(bids_root, subject=d.dataset.task.subject,
                                  acquisition=PARAMETERS['electrodes']['acquisition'],
                                  modality='electrodes', extension='.tsv')
    electrodes = Electrodes(electrode_file)

    move_times, rest_times = read_markers(
        d,
        marker_on=PARAMETERS['markers']['on'],
        marker_off=PARAMETERS['markers']['off'],
        minimalduration=PARAMETERS['markers']['minimalduration'],
        )
    # convert to s_freq
    rest_times = [[int(x0 * s_freq) for x0 in x1] for x1 in rest_times]
    move_times = [[int(x0 * s_freq) for x0 in x1] for x1 in move_times]

    # only channels with electrodes
    elec_names = [x['name'] for x in electrodes.electrodes.tsv]
    elec_names = [x for x in elec_names if x in d.header['chan_name']]  # exclude elec location that have no corresponding channel
    data = d.read_data(chan=elec_names, begsam=rest_times[0][0], endsam=rest_times[1][-1])
    data = filter_(data, ftype='notch')

    clean_labels = reject_channels(data)
    lg.debug(f'Clean channels {len(clean_labels)} / {len(elec_names)}')

    data = d.read_data(chan=clean_labels, begsam=move_times[0], endsam=move_times[1])
    data = filter_(data, ftype='notch')

    dat_move = run_montage(d, move_times, clean_labels)
    dat_rest = run_montage(d, rest_times, clean_labels)

    labels_in_roi = find_labels_in_regions(electrodes, PARAMETERS['regions'])

    clean_roi_labels = [label for label in clean_labels if label in labels_in_roi]

    dat_move = select(dat_move, chan=clean_roi_labels)
    dat_rest = select(dat_rest, chan=clean_roi_labels)

    return dat_move, dat_rest


def reject_channels(dat):
    dat_std = math(dat, operator_name='std', axis='time')
    THRESHOLD = PARAMETERS['reject']['chan']['threshold_std']
    x = dat_std.data[0]
    thres = [mean(x) + THRESHOLD * std(x)]
    clean_labels = list(dat_std.chan[0][dat_std.data[0] < thres])
    return clean_labels


def run_montage(d, times, chan):
    dat = d.read_data(begsam=times[0], endsam=times[1], chan=chan)
    return montage(dat, ref_to_avg=True)


def read_markers(d, marker_on, marker_off, minimalduration):
    markers = d.read_markers()
    move_start = [mrk['start'] for mrk in markers if mrk['name'] == marker_on]
    move_end = [mrk['end'] for mrk in markers if mrk['name'] == marker_on]

    rest_start = [mrk['start'] for mrk in markers if mrk['name'] == marker_off if (mrk['end'] - mrk['start']) > minimalduration]
    rest_end = [mrk['end'] for mrk in markers if mrk['name'] == marker_off if (mrk['end'] - mrk['start']) > minimalduration]
    return (move_start, move_end), (rest_start, rest_end)
