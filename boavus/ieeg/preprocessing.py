from wonambi.trans import select, montage, math, timefrequency, concatenate
from logging import getLogger
from numpy import mean, std
from numpy import array, log10
import plotly.graph_objs as go

from boavus.ieeg.dataset import Dataset
from .percent import percent_ecog

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
    'reject': {
        'chan': {
            'threshold_std': 3,
            },
        },
    'spectrogram': {
        'duration': 1,
        'taper': 'dpss',
        'frequency': [
            60,
            90,
            ],
        },
    }

FREQ = (60, 90)


def compute_frequency(filename):
    dat_move, dat_rest = preprocess_ecog(filename)

    hfa_move, freq_move = compute_freq(dat_move)
    hfa_rest, freq_rest = compute_freq(dat_rest)

    # it's compute here with all the electrodes (also the non active ones)
    ecog_stats = percent_ecog(hfa_move, hfa_rest)

    """
    hfa_move, hfa_rest = _select_active(hfa_move, hfa_rest)
    active_chan = hfa_move.chan[0]
    """
    active = ' (todo)'
    all_fig = []
    for chan in ecog_stats.chan[0]:
        fig = plot_psd(chan, active, freq_move, freq_rest, ecog_stats)
        all_fig.append(fig)

    return all_fig


def compute_freq(dat):
    """Remove epochs which have very high activity in high-freq range, then
    average over time (only high-freq range) and ALL the frequencies."""
    TAPER = PARAMETERS['spectrogram']['taper']
    DURATION = PARAMETERS['spectrogram']['duration']
    FREQ = PARAMETERS['spectrogram']['frequency']

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


def plot_psd(chan, active, freq_move, freq_rest, perc):
    mean_move = math(select(freq_move, freq=FREQ), operator_name='mean', axis='freq')(trial=0, chan=chan)
    mean_rest = math(select(freq_rest, freq=FREQ), operator_name='mean', axis='freq')(trial=0, chan=chan)

    YAXIS_RANGE = array([-2, 2], dtype=float)
    FONT_SIZE = (14, 18)

    traces = [
        go.Scatter(
            x=freq_rest.freq[0],
            y=freq_rest(chan=chan, trial=0),
            name='rest',
            line=dict(
                color='red',
                ),
            ),
        go.Scatter(
            x=freq_move.freq[0],
            y=freq_move(chan=chan, trial=0),
            name='move',
            line=dict(
                color='green',
                ),
            ),
        go.Scatter(
            x=FREQ,
            y=array([1, 1]) * mean_rest,
            name='rest (mean)',
            line=dict(
                color='red',
                dash='10px',
                ),
            ),
        go.Scatter(
            x=FREQ,
            y=array([1, 1]) * mean_move,
            name='move (mean)',
            line=dict(
                color='green',
                dash='5px',
                ),
            ),
        go.Scatter(
            x=(FREQ[0], FREQ[0]),
            y=10 ** YAXIS_RANGE,
            line=dict(
                color='gray',
                dash='dot',
                ),
            showlegend=False,
            ),
        go.Scatter(
            x=(FREQ[1], FREQ[1]),
            y=10 ** YAXIS_RANGE,
            line=dict(
                color='gray',
                dash='dot',
                ),
            showlegend=False,
            ),
        ]

    layout = go.Layout(
        title=chan + active,
        xaxis=dict(
            title='Hz',
            titlefont=dict(
                size=FONT_SIZE[1],
                ),
            range=(0, 100),
            tickfont=dict(
                size=FONT_SIZE[0],
                ),
            ),
        yaxis=dict(
            title='μV<sup>2</sup>/Hz',
            titlefont=dict(
                size=FONT_SIZE[1],
                ),
            type='log',
            range=YAXIS_RANGE,
            tickfont=dict(
                size=FONT_SIZE[0],
                ),
            ),
        legend=dict(
            font=dict(
                size=FONT_SIZE[1],
                ),
            ),
        annotations=[
            dict(
                x=FREQ[1],
                y=log10(mean_move),
                ax=50,
                standoff=2,
                text=f'{perc(trial=0, chan=chan).item():0.3f}%',
                font=dict(
                    size=FONT_SIZE[1],
                    ),
                ), ]
        )
    return go.Figure(data=traces, layout=layout)


def preprocess_ecog(filename):
    self = Dataset(filename, PARAMETERS['electrodes']['acquisition'])
    s_freq = float(self.channels.tsv[0]['sampling_frequency'])

    move_times, rest_times = read_markers(
        self,
        marker_on=PARAMETERS['markers']['on'],
        marker_off=PARAMETERS['markers']['off'],
        minimalduration=PARAMETERS['markers']['minimalduration'],
        )
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

    if len(PARAMETERS['regions']) > 0:
        elec = self.electrodes
        labels_in_roi = [x['name'] for x in elec.electrodes.tsv if x['region'] in PARAMETERS['regions']]
        clean_roi_labels = [label for label in clean_labels if label in labels_in_roi]
    else:
        clean_roi_labels = labels_in_roi = clean_labels

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
    markers = d.read_events()
    move_start = [mrk['onset'] for mrk in markers if mrk['trial_type'] == marker_on]
    move_end = [mrk['onset'] + mrk['duration'] for mrk in markers if mrk['trial_type'] == marker_on]

    rest_start = [mrk['onset'] for mrk in markers if mrk['trial_type'] == marker_off if mrk['duration'] > minimalduration]
    rest_end = [mrk['onset'] + mrk['duration'] for mrk in markers if mrk['trial_type'] == marker_off if mrk['duration'] > minimalduration]
    return (move_start, move_end), (rest_start, rest_end)
