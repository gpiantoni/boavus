from logging import getLogger
from shutil import rmtree

from numpy import argmax, array, polyfit, isnan, NaN
from scipy.stats import linregress
from collections import defaultdict
import plotly.graph_objs as go

from exportimages import export_plotly, Webdriver

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import read_tsv, replace_underscore

from ..bidso import find_labels_in_regions

lg = getLogger(__name__)

FMRI_MODALITY = 'bold_compare'
IEEG_MODALITY = 'ieeg_compare'
ZSTAT_DIR = 'corr_ieeg_fmri_zstat'
PNG_DIR = 'corr_ieeg_fmri_png'
SINGLE_POINTS_DIR = 'corr_ieeg_fmri_point'


ATTRIBUTES = [
    'acquisition',
    'task',
    ]
VALUE_TYPES = [
    'peak',
    'r2',
    ]


def main(bids_dir, analysis_dir, output_dir, acquisition='*regions',
         regions=[], pvalue=0.05, plot=False):
    """
    compare fMRI values at electrode locations to ECoG values

    Parameters
    ----------
    bids_dir : path

    analysis_dir : path

    output_dir : path

    acquisition : str

    regions : list

    pvalue : float

    plot : bool

    """
    results_dir = output_dir / ZSTAT_DIR
    rmtree(results_dir, ignore_errors=True)
    results_dir.mkdir(exist_ok=True, parents=True)

    if plot:
        singlepoints_dir = output_dir / SINGLE_POINTS_DIR
        rmtree(singlepoints_dir, ignore_errors=True)
        singlepoints_dir.mkdir(exist_ok=True, parents=True)

    results = []
    for fmri_at_elec_file in find_in_bids(analysis_dir, generator=True, modality=FMRI_MODALITY, extension='.tsv'):
        try:
            one_result = compute_corr_ecog_fmri(file_Core(fmri_at_elec_file),
                                                bids_dir, analysis_dir, output_dir,
                                                acquisition, regions, pvalue, plot)

        except FileNotFoundError as err:
            lg.warning(err)

        else:
            results.append(one_result)

    if plot:
        if len(results) == 0:
            lg.warning('No results were computed, skipping plot')
        else:
            plot_results(results, output_dir)


def compute_corr_ecog_fmri(fmri_file, bids_dir, analysis_dir, output_dir,
                           acquisition, regions, PVALUE, PLOT):
    fmri_tsv = read_tsv(fmri_file.filename)

    electrodes_file = find_in_bids(
        bids_dir,
        wildcard=True,
        subject=fmri_file.subject,
        acquisition=acquisition,
        modality='electrodes',
        extension='.tsv')
    electrodes = Electrodes(electrodes_file)

    ecog_file = find_in_bids(
        analysis_dir,
        subject=fmri_file.subject,
        task=fmri_file.task,
        modality=IEEG_MODALITY,
        extension='.tsv')
    ecog_tsv = read_tsv(ecog_file)
    n_all_elec = len(ecog_tsv)

    # use only values from electrodes which are in the ROI
    labels_in_roi = find_labels_in_regions(electrodes, regions)
    ecog_tsv = list(filter(lambda x: x['channel'] in labels_in_roi, ecog_tsv))
    lg.debug(f'Using {len(ecog_tsv)}/{n_all_elec} electrodes in ROI')

    KERNELS = array([col for col in fmri_tsv[0] if col != 'channel'])

    results_tsv = output_dir / ZSTAT_DIR / replace_underscore(ecog_file.stem, 'bold_r2.tsv')
    with results_tsv.open('w') as f:
        f.write('Kernel\tRsquared\n')

        all_r2 = []
        for KERNEL in KERNELS:
            try:
                ecog_val, p_val, fmri_val = read_measures(ecog_tsv, fmri_tsv, KERNEL)
                r2 = compute_rsquared(ecog_val, fmri_val, p_val, PVALUE)
            except Exception:
                r2 = NaN
            all_r2.append(r2)
            f.write(f'{KERNEL}\t{r2}\n')

    all_r2 = array(all_r2)
    if PLOT:
        best_kernel = KERNELS[argmax(all_r2)]
        fig = plot_single_points(ecog_tsv, fmri_tsv, best_kernel, PVALUE)
        singlepoints_png = output_dir / SINGLE_POINTS_DIR / (results_tsv.stem + '.png')
        export_plotly(fig, singlepoints_png)

    return results_tsv


def plot_single_points(ecog_tsv, fmri_tsv, kernel, pvalue):
    ecog_val, p_val, fmri_val = read_measures(ecog_tsv, fmri_tsv, kernel)
    mask = ~isnan(ecog_val) & ~isnan(fmri_val) & (p_val <= pvalue)
    lr = linregress(ecog_val[mask], fmri_val[mask])

    traces = [
        go.Scatter(
            name='not significant',
            x=ecog_val[p_val > pvalue],
            y=fmri_val[p_val > pvalue],
            mode='markers',
            marker=go.Marker(
                color='cyan',
                )
            ),
        go.Scatter(
            name='significant',
            x=ecog_val[p_val <= pvalue],
            y=fmri_val[p_val <= pvalue],
            mode='markers',
            marker=go.Marker(
                color='magenta',
                )
            ),
        go.Scatter(
            x=ecog_val,
            y=lr.slope * ecog_val + lr.intercept,
            mode='lines',
            marker=go.Marker(
                color='magenta'
                ),
            name='Fit'
            ),
        ]

    layout = go.Layout(
        title=f'Correlation with {float(kernel):.2f}mm kernel size<br />R<sup>2</sup> = {lr.rvalue ** 2:.3f}<br />Y = {lr.slope:.3f}X + {lr.intercept:.3f}',
        xaxis=go.XAxis(
            title='ECoG values',
            ),
        yaxis=go.YAxis(
            title='fMRI values',
            ),
        )
    fig = go.Figure(
        data=traces,
        layout=layout,
        )

    return fig


def compute_rsquared(x, y, p_val, PVALUE):
    mask = ~isnan(x) & ~isnan(y) & (p_val <= PVALUE)

    lr = linregress(x[mask], y[mask])
    return lr.rvalue ** 2


def read_measures(ecog_tsv, fmri_tsv, KERNEL):
    fmri_vals = []
    for one_ecog in ecog_tsv:
        one_val = [float(elec[KERNEL]) for elec in fmri_tsv if elec['channel'] == one_ecog['channel']][0]
        fmri_vals.append(one_val)

    ecog_val = array([float(x['measure']) for x in ecog_tsv])
    p_val = array([float(x['pvalue']) for x in ecog_tsv])
    return ecog_val, p_val, array(fmri_vals)


def plot_results(results_tsv, output_dir):
    img_dir = output_dir / PNG_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True)

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:
            fig = _plot_fit_over_kernel(one_tsv)
            output_png = img_dir / (one_tsv.stem + '.png')
            export_plotly(fig, output_png, driver=d)

        for value_type in VALUE_TYPES:
            for attribute in ATTRIBUTES:
                val_per_group, max_val = read_values_per_group(results_tsv,
                                                               attribute,
                                                               value_type)
                fig = _plot_histogram(val_per_group, max_val, attribute,
                                      value_type)
                output_png = img_dir / f'histogram_{attribute}_{value_type}.png'
                export_plotly(fig, output_png, driver=d)


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
