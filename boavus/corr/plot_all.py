from pathlib import Path
from numpy import argmax, max, gradient
import plotly.graph_objs as go

from bidso import file_Core
from bidso.utils import read_tsv
from exportimages import export_plotly, Webdriver

SIZE = int(6 * 96), int(4 * 96)


SIZE_TITLE = 'kernel size (mm)'
R2_TITLE = 'explained variance (r<sup>2</sup>)'


def plot_corr_all(results_tsv, img_dir, image='png'):

    img_dir.mkdir(exist_ok=True, parents=True)

    rsquared = []
    peaks = []

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:

            one_tsv = Path(one_tsv)
            results = read_tsv(one_tsv)
            results_rsquared = results['Rsquared']
            # results_rsquared = -1 * gradient(gradient(results_rsquared))
            acquisition = file_Core(one_tsv).acquisition

            fig = _plot_fit_over_kernel(results, acquisition)
            output_png = img_dir / (one_tsv.stem + '.' + image)
            export_plotly(fig, output_png, width=SIZE[0], height=SIZE[1], driver=d)

            rsquared.append(
                max(results_rsquared)
                )
            peaks.append(
                results['Kernel'][argmax(results_rsquared)]
                )

        fig = _plot_histogram(rsquared, 'r2', 1)
        png_r2 = img_dir / ('histogram_rsquared.' + image)
        export_plotly(fig, png_r2, width=SIZE[0], height=SIZE[1], driver=d)

        fig = _plot_histogram(peaks, 'peak', max(results['Kernel']) + 1)
        png_peaks = img_dir / ('histogram_peak.' + image)
        export_plotly(fig, png_peaks, width=SIZE[0], height=SIZE[1], driver=d)

    return png_r2, png_peaks


def _plot_fit_over_kernel(results, acquisition):
    k = results['Kernel']
    rsquared = results['Rsquared']
    traces = [{
        'x': k,
        'y': rsquared,
        },
        ]

    # title=acquisition,
    layout = go.Layout(
        xaxis=dict(
            title=SIZE_TITLE,
            range=(min(k), max(k)),
            dtick=4,
            ),
        yaxis=dict(
            title=R2_TITLE,
            rangemode='tozero',
            ),
        )

    fig = go.Figure(data=traces, layout=layout)
    return fig


def _plot_histogram(values, value_type, max_val=1):
    if value_type == 'peak':
        bin_size = 1
        xaxis_title = SIZE_TITLE,
        dtick = 4
    elif value_type == 'r2':
        bin_size = .1
        xaxis_title = R2_TITLE,
        dtick = 0.2

    xbins = dict(
        start=-.5,
        end=max_val,
        size=bin_size,
        )
    traces = [
        go.Histogram(
            x=values,
            xbins=xbins,
            name=value_type,
        )]

    layout = go.Layout(
        xaxis=dict(
            title=xaxis_title,
            range=(0, max_val),
            dtick=dtick,
            ),
        yaxis=dict(
            title='# participants',
            ),
        )

    fig = go.Figure(data=traces, layout=layout)
    return fig
