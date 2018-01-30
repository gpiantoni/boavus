from wonambi.trans import select, montage, math, timefrequency, concatenate
from logging import getLogger
from numpy import mean, std, array, log10
import plotly.graph_objs as go
from exportimages import export_plotly, Webdriver

from bidso import Task
from bidso.find import find_in_bids
from bidso.utils import replace_extension
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
    'regions': [],
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


def main(bids_dir, output_dir):

    export_dir = output_dir / 'psd'
    export_dir.mkdir(exist_ok=True, parents=True)
    driver = Webdriver(export_dir)

    for ieeg_file in find_in_bids(bids_dir, modality='ieeg', extension='.bin', generator=True):
        figs, all_chan = compute_frequency(ieeg_file)

        for fig, chan in zip(figs, all_chan):
            export_png = replace_extension(export_dir / Task(ieeg_file).get_filename(), '_' + chan + '.png')
            lg.debug(f'plotting {export_png}')
            export_plotly(fig, export_png, driver)


def compute_frequency(filename):
    dat_move, dat_rest = preprocess_ecog(filename)

    hfa_move, freq_move = compute_freq(dat_move)
    hfa_rest, freq_rest = compute_freq(dat_rest)

    # it's compute here with all the electrodes (also the non active ones)
    ecog_stats = percent_ecog(hfa_move, hfa_rest)
    all_chan = ecog_stats.chan[0]

    """
    hfa_move, hfa_rest = _select_active(hfa_move, hfa_rest)
    active_chan = hfa_move.chan[0]
    """
    active = ' (todo)'
    all_fig = []
    for chan in all_chan:
        fig = plot_psd(chan, active, freq_move, freq_rest, ecog_stats)
        all_fig.append(fig)

    return all_fig, all_chan


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
    FREQ = PARAMETERS['spectrogram']['frequency']
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
