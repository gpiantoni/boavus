from pickle import load, dump
from wonambi.trans import select, math, timefrequency, concatenate
from logging import getLogger
from numpy import mean, array, log10
import plotly.graph_objs as go

from bidso.find import find_in_bids
from bidso.utils import replace_underscore

lg = getLogger(__name__)

PARAMETERS = {
    'duration': 1,
    'taper': 'dpss',
    'frequency': [
        60,
        90,
        ],
    }


def main(output_dir):

    for cond in ('move', 'rest'):
        for ieeg_file in find_in_bids(output_dir, modality=cond, extension='.pkl', generator=True):
            with ieeg_file.open('rb') as f:
                dat = load(f)

            hfa, freq = compute_frequency(dat)

            output_file = replace_underscore(ieeg_file, 'hfa' + cond + '.pkl')
            with output_file.open('wb') as f:
                dump(hfa, f)

            output_file = replace_underscore(ieeg_file, 'freq' + cond + '.pkl')
            with output_file.open('wb') as f:
                dump(freq, f)


def compute_frequency(dat):
    """Remove epochs which have very high activity in high-freq range, then
    average over time (only high-freq range) and ALL the frequencies."""
    TAPER = PARAMETERS['taper']
    DURATION = PARAMETERS['duration']
    FREQ = PARAMETERS['frequency']

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
    FREQ = PARAMETERS['frequency']
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
