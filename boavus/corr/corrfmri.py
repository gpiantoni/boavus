from logging import getLogger
from shutil import rmtree

from numpy import argmax, array, polyfit, isnan, NaN
from numpy import searchsorted, intersect1d
from scipy.stats import linregress
from collections import defaultdict
import plotly.graph_objs as go

from exportimages import export_plotly, Webdriver

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import read_tsv, replace_underscore


lg = getLogger(__name__)

ZSTAT_DIR = 'corr_ieeg_fmri_zstat'
PNG_DIR = 'corr_ieeg_fmri_png'
SINGLE_POINTS_DIR = 'corr_ieeg_fmri_point'


def compute_corr_ecog_fmri(fmri_file, ecog_file, output_dir, PVALUE):
    fmri_tsv = read_tsv(fmri_file)
    ecog_tsv = read_tsv(ecog_file)

    """
    TODO
    electrodes = Electrodes(electrodes_file)
    n_all_elec = len(ecog_tsv)
    # use only values from electrodes which are in the ROI
    labels_in_roi = find_labels_in_regions(electrodes, regions)
    ecog_tsv = list(filter(lambda x: x['channel'] in labels_in_roi, ecog_tsv))
    lg.debug(f'Using {len(ecog_tsv)}/{n_all_elec} electrodes in ROI')
    """

    fmri_tsv, ecog_tsv = _sort_measures(fmri_tsv, ecog_tsv)
    kernel_sizes = fmri_tsv.dtype.names[1:]

    results_tsv = output_dir / ZSTAT_DIR / replace_underscore(ecog_file.stem, 'bold_r2.tsv')
    with results_tsv.open('w') as f:
        f.write('Kernel\tRsquared\n')

        for kernel in kernel_sizes:
            r2 = compute_rsquared(
                ecog_tsv['measure'],
                fmri_tsv[kernel],
                ecog_tsv['pvalue'],
                PVALUE)

            # except Exception:
            #    r2 = NaN
            f.write(f'{kernel}\t{r2}\n')

    return results_tsv


def _sort_measures(fmri_vals, ecog_vals):
    """make sure we're using the same channels and in the same order
    """
    common_chan = intersect1d(fmri_vals['channel'], ecog_vals['channel'])

    fmri_idx = searchsorted(fmri_vals['channel'], common_chan)
    ecog_idx = searchsorted(ecog_vals['channel'], common_chan)

    fmri_vals = fmri_vals[fmri_idx]
    ecog_vals = ecog_vals[ecog_idx]
    return fmri_vals, ecog_vals


def compute_rsquared(x, y, p_val, PVALUE):
    mask = ~isnan(x) & ~isnan(y) & (p_val <= PVALUE)

    lr = linregress(x[mask], y[mask])
    return lr.rvalue ** 2


def read_shape(one_tsv):
    results = read_tsv(one_tsv)
    k = [float(x['Kernel']) for x in results]
    rsquared = [float(x['Rsquared']) for x in results]

    return polyfit(k, rsquared, 2)[0], k[argmax(rsquared)], max(rsquared)


def read_values_per_group(results_tsv, attribute, value_type):
    groups = defaultdict(list)
    max_val = 0
    for one_tsv in results_tsv:
        name = getattr(file_Core(one_tsv.stem), attribute)
        shape = read_shape(one_tsv)
        if value_type == 'peak':
            if shape[0] >= 0:
                continue
            vals = shape[1]
        elif value_type == 'r2':
            vals = shape[2]
        max_val = max(max_val, vals)
        groups[name].append(vals)

    return groups, max_val


def _plot_fit_over_kernel(one_tsv):
    acquisition = file_Core(one_tsv).acquisition

    results = read_tsv(one_tsv)
    k = [float(x['Kernel']) for x in results]
    rsquared = [float(x['Rsquared']) for x in results]
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


def _plot_histogram(val_per_group, max_val, attribute, value_type):
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
    traces = []
    for name, vals in val_per_group.items():
        traces.append(
            go.Histogram(
                x=vals,
                xbins=xbins,
                name=name,
            ))

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
