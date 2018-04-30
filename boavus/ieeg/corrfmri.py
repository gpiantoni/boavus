from logging import getLogger
from shutil import rmtree

from numpy import argmax, array, polyfit
from scipy.stats import linregress
import plotly.graph_objs as go

from exportimages import export_plotly, Webdriver

from bidso import file_Core, Electrodes
from bidso.find import find_in_bids
from bidso.utils import read_tsv, replace_underscore

from ..bidso import find_labels_in_regions

lg = getLogger(__name__)

ZSTAT_DIR = 'corr_ieeg_fmri_zstat'
PNG_DIR = 'corr_ieeg_fmri_png'


PARAMETERS = {
    'acquisition': '*regions',
    'regions': [],
    'plot': True,
    }


def main(bids_dir, analysis_dir, output_dir):

    results_dir = output_dir / ZSTAT_DIR
    rmtree(results_dir, ignore_errors=True)
    results_dir.mkdir(exist_ok=True, parents=True)

    results = []
    for fmri_at_elec_file in find_in_bids(analysis_dir, generator=True, modality='*elec', extension='.tsv'):
        try:
            one_result = compute_corr_ecog_fmri(file_Core(fmri_at_elec_file),
                                                bids_dir, analysis_dir, results_dir)

        except FileNotFoundError as err:
            lg.warning(err)

        else:
            results.append(one_result)

    if PARAMETERS['plot']:
        if len(results) == 0:
            lg.warning('No results were computed, skipping plot')
        plot_results(results, output_dir)


def compute_corr_ecog_fmri(fmri_file, bids_dir, analysis_dir, results_dir):
    fmri_tsv = read_tsv(fmri_file.filename)

    electrodes_file = find_in_bids(
        bids_dir,
        wildcard=True,
        subject=fmri_file.subject,
        acquisition=PARAMETERS['acquisition'],
        modality='electrodes',
        extension='.tsv')
    electrodes = Electrodes(electrodes_file)

    ecog_file = find_in_bids(
        analysis_dir,
        subject=fmri_file.subject,
        task=fmri_file.task,
        modality='compare',
        extension='.tsv')
    ecog_tsv = read_tsv(ecog_file)
    n_all_elec = len(ecog_tsv)

    # use only values from electrodes which are in the ROI
    labels_in_roi = find_labels_in_regions(electrodes, PARAMETERS['regions'])
    ecog_tsv = list(filter(lambda x: x['channel'] in labels_in_roi, ecog_tsv))
    lg.debug(f'Using {len(ecog_tsv)}/{n_all_elec} electrodes in ROI')

    KERNELS = [col for col in fmri_tsv[0] if col != 'channel']

    results_tsv = results_dir / replace_underscore(fmri_file.get_filename(), fmri_file.modality + '.tsv')
    with results_tsv.open('w') as f:
        f.write('Kernel\tRsquared\n')

        for KERNEL in KERNELS:
            r2 = compute_rsquared(ecog_tsv, fmri_tsv, KERNEL)
            f.write(f'{KERNEL}\t{r2}\n')

    return results_tsv


def compute_rsquared(ecog_tsv, fmri_tsv, KERNEL):
    fmri_vals = []
    for one_ecog in ecog_tsv:
        one_val = [float(elec[KERNEL]) for elec in fmri_tsv if elec['channel'] == one_ecog['channel']][0]
        fmri_vals.append(one_val)

    ecog_val = array([float(x['measure']) for x in ecog_tsv])

    lr = linregress(ecog_val, array(fmri_vals))
    return lr.rvalue ** 2


def plot_results(results_tsv, output_dir):
    img_dir = output_dir / PNG_DIR
    rmtree(img_dir, ignore_errors=True)
    img_dir.mkdir(exist_ok=True)

    with Webdriver(img_dir) as d:
        for one_tsv in results_tsv:
            if one_tsv is None:
                continue

            results = read_tsv(one_tsv)
            k = [x['Kernel'] for x in results]
            rsquared = [float(x['Rsquared']) for x in results]
            traces = [{
                'x': k,
                'y': rsquared,
                },
                ]

            if ('duiven' in one_tsv.stem) or ('ommen' in one_tsv.stem) or ('vledder' in one_tsv.stem):
                title = 'high-density'
            else:
                title = 'clinical'
            layout = go.Layout(
                title=title,
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
            output_png = img_dir / (one_tsv.stem + '.png')
            export_plotly(fig, output_png, driver=d)

        # histogram
        thumb_val = []
        hand_val = []

        for one_tsv in results_tsv:
            vals = read_shape(one_tsv)
            if vals[0] < 0:
                if 'thumb' in one_tsv.stem:
                    thumb_val.append(vals[1])
                else:
                    hand_val.append(vals[1])

        xbins = dict(
            start=-.5,
            end=9,
            size=1
            )

        traces = [
            go.Histogram(
                x=hand_val,
                xbins=xbins,
                name='hand',
            ),
            go.Histogram(
                x=thumb_val,
                xbins=xbins,
                name='thumb',
            ),
            ]

        layout = go.Layout(
            xaxis=dict(
                title='mm',
                range=(min(k), max(k)),
                ),
            yaxis=dict(
                title='# tasks',
                ),
            )

        fig = go.Figure(data=traces, layout=layout)
        output_png = img_dir / 'histogram_handthumb.png'
        export_plotly(fig, output_png, driver=d)

        # histogram
        thumb_val = []
        hand_val = []

        for one_tsv in results_tsv:
            vals = read_shape(one_tsv)
            if vals[0] < 0:
                if ('duiven' in one_tsv.stem) or ('ommen' in one_tsv.stem) or ('vledder' in one_tsv.stem):
                    thumb_val.append(vals[1])
                else:
                    hand_val.append(vals[1])

        xbins = dict(
            start=-.5,
            end=9,
            size=1
            )

        traces = [
            go.Histogram(
                x=hand_val,
                xbins=xbins,
                name='clinical',
            ),
            go.Histogram(
                x=thumb_val,
                xbins=xbins,
                name='high density',
            ),
            ]
        layout = go.Layout(
            xaxis=dict(
                title='mm',
                range=(min(k), max(k)),
                ),
            yaxis=dict(
                title='# tasks',
                ),
            )

        fig = go.Figure(data=traces, layout=layout)
        output_png = img_dir / 'histogram_gridtype.png'
        export_plotly(fig, output_png, driver=d)

        # histogram
        thumb_val = []
        hand_val = []

        for one_tsv in results_tsv:
            vals = read_shape(one_tsv)
            if vals[0] < 0:
                if ('duiven' in one_tsv.stem) or ('ommen' in one_tsv.stem) or ('vledder' in one_tsv.stem):
                    thumb_val.append(vals[2])
                else:
                    hand_val.append(vals[2])

        xbins = dict(
            start=-.05,
            end=1,
            size=.1
            )

        traces = [
            go.Histogram(
                x=hand_val,
                xbins=xbins,
                name='clinical',
            ),
            go.Histogram(
                x=thumb_val,
                xbins=xbins,
                name='high density',
            ),
            ]
        layout = go.Layout(
            xaxis=dict(
                title='r<sup>2</sup>',
                range=(0, 1),
                ),
            yaxis=dict(
                title='# tasks',
                ),
            )

        fig = go.Figure(data=traces, layout=layout)
        output_png = img_dir / 'histogram_gridtype_rsquared.png'
        export_plotly(fig, output_png, driver=d)


def read_shape(one_tsv):
    results = read_tsv(one_tsv)
    k = [float(x['Kernel']) for x in results]
    rsquared = [float(x['Rsquared']) for x in results]

    return polyfit(k, rsquared, 2)[0], k[argmax(rsquared)], max(rsquared)
