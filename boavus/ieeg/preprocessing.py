from wonambi.trans import select, montage, math, timefrequency, concatenate
from numpy import mean, std

from boavus.ieeg.wonambi import Dataset


def preprocessing(filename):
    self = Dataset(filename)
    s_freq = float(self.channels.tsv[0]['sampling_frequency'])

    move_times, rest_times = read_markers(self, 'move', 'rest')
    # convert to s_freq
    rest_times = [[int(x0 * s_freq) for x0 in x1] for x1 in rest_times]
    move_times = [[int(x0 * s_freq) for x0 in x1] for x1 in move_times]
    elec_names = [x['name'] for x in self.electrodes.electrodes.tsv]

    data = self.read_data(begsam=rest_times[0][0], endsam=rest_times[1][-1])
    data = select(data, chan=elec_names)
    clean_labels = reject_channels(data)

    data = self.read_data(chan=clean_labels, begsam=move_times[0], endsam=move_times[1])

    dat_move = run_montage(self, move_times, clean_labels)
    dat_rest = run_montage(self, rest_times, clean_labels)

    clean_roi_labels = [x['name'] for x in self.channels.tsv if x['name'].startswith('grid')]

    dat_move = select(dat_move, chan=clean_roi_labels)
    dat_rest = select(dat_rest, chan=clean_roi_labels)

    hfa_move, freq_move = compute_freq(dat_move)
    hfa_rest, freq_rest = compute_freq(dat_rest)


def reject_channels(dat):
    dat_std = math(dat, operator_name='std', axis='time')
    THRESHOLD = 3
    x = dat_std.data[0]
    thres = [mean(x) + THRESHOLD * std(x)]
    clean_labels = list(dat_std.chan[0][dat_std.data[0] < thres])
    return clean_labels


def run_montage(d, times, chan):
    dat = d.read_data(begsam=times[0], endsam=times[1], chan=chan)
    return montage(dat, ref_to_avg=True)


def compute_freq(dat):
    """Remove epochs which have very high activity in high-freq range, then
    average over time (only high-freq range) and ALL the frequencies."""
    DURATION = 1
    TAPER = 'dpss'
    FREQ = (60, 90)

    if TAPER == 'dpss':
        dat = timefrequency(dat, method='spectrogram', taper='dpss',
                            duration=DURATION,
                            halfbandwidth=abs(FREQ[1] - FREQ[0]) / 2)
        dat = concatenate(dat, axis='time')

        FREQ_SELECT = (mean(FREQ) - 1 / (DURATION * 2),
                       mean(FREQ) + 1 / (DURATION * 2))

    else:
        dat = timefrequency(dat, taper=TAPER, method='spectrogram',
                            duration=DURATION)
        dat = concatenate(dat, axis='time')
        FREQ_SELECT = FREQ

    # dat, lg = _remove_outliers(dat)

    freq_f = math(dat, axis='time', operator_name='mean')
    dat = select(dat, freq=FREQ_SELECT)
    freq_t = math(dat, axis='freq', operator_name='mean')

    return freq_t, freq_f


def read_markers(d, marker_on='49', marker_off='48', min_duration=20):
    markers = d.read_events()
    move_start = [mrk['onset'] for mrk in markers if mrk['trial_type'] == marker_on]
    move_end = [mrk['onset'] + mrk['duration'] for mrk in markers if mrk['trial_type'] == marker_on]

    rest_start = [mrk['onset'] for mrk in markers if mrk['trial_type'] == marker_off if mrk['duration'] > min_duration]
    rest_end = [mrk['onset'] + mrk['duration'] for mrk in markers if mrk['trial_type'] == marker_off if mrk['duration'] > min_duration]
    return (move_start, move_end), (rest_start, rest_end)
