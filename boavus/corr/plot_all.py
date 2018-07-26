from pathlib import Path
from numpy import argmax, max
import plotly.graph_objs as go

from bidso import file_Core
from bidso.utils import read_tsv
from exportimages import export_plotly, Webdriver

SIZE = int(8 * 96), int(6 * 96)


def plot_corr_all(results_tsv, img_dir, image='png'):

    img_dir.mkdir(exist_ok=True, parents=True)

    rsquared = []
    peaks = []

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:

            one_tsv = Path(one_tsv)
            results = read_tsv(one_tsv)
            acquisition = file_Core(one_tsv).acquisition

            fig = _plot_fit_over_kernel(results, acquisition)
            output_png = img_dir / (one_tsv.stem + '.' + image)
            export_plotly(fig, output_png, driver=d)

            rsquared.append(
                max(results['Rsquared'])
                )
            peaks.append(
                results['Kernel'][argmax(results['Rsquared'])]
                )

        fig = _plot_histogram(rsquared, 'r2', 1)
        png_r2 = img_dir / ('histogram_rsquared.' + image)
        export_plotly(fig, png_r2, width=SIZE[0], height=SIZE[1], driver=d)

        fig = _plot_histogram(peaks, 'peak', max(results['Kernel']))
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

    layout = go.Layout(
        title=acquisition,
        xaxis=dict(
            title='mm',
            range=(min(k), max(k)),
            ),
        yaxis=dict(
            title='r<sup>2</sup>',
            rangemode='tozero',
            ),
        )

    fig = go.Figure(data=traces, layout=layout)
    return fig


def _plot_histogram(values, value_type, max_val=1):
    if value_type == 'peak':
        bin_size = 1
        xaxis_title = 'mm'
    elif value_type == 'r2':
        bin_size = .1
        xaxis_title = 'r<sup>2</sup>'

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
            ),
        yaxis=dict(
            title='# tasks',
            ),
        )

    fig = go.Figure(data=traces, layout=layout)
    return fig
