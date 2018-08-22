from numpy import argmax, isnan
from scipy.stats import linregress
from bidso.utils import read_tsv

import plotly.graph_objs as go
from exportimages import export_plotly

from .corrfmri import select_channels

SIZE = int(6 * 96), int(4 * 96)

def compute_corr_ecog_fmri(fmri_file, ecog_file, corr_file, img_dir, PVALUE, image):

    fmri_tsv = read_tsv(fmri_file)
    ecog_tsv = read_tsv(ecog_file)
    fmri_tsv = select_channels(fmri_tsv, ecog_tsv)
    kernel_sizes = fmri_tsv.dtype.names[1:]

    corr_tsv = read_tsv(corr_file)
    best_kernel = kernel_sizes[argmax(corr_tsv['Rsquared'])]
    fig = scatter_single_points(ecog_tsv, fmri_tsv, best_kernel, PVALUE)

    img_dir.mkdir(exist_ok=True, parents=True)
    singlepoints_png = img_dir / (corr_file.stem + '_best.' + image)

    export_plotly(fig, singlepoints_png, width=SIZE[0], height=SIZE[1])

    return singlepoints_png


def scatter_single_points(ecog_val, fmri_val, kernel, pvalue):

    x_ecog = ecog_val['measure']
    y_fmri = fmri_val[kernel]

    mask = ~isnan(x_ecog) & ~isnan(y_fmri) & (ecog_val['pvalue'] <= pvalue)
    lr = linregress(x_ecog[mask], y_fmri[mask])

    traces = [
        go.Scatter(
            name='not significant',
            x=x_ecog[ecog_val['pvalue'] > pvalue],
            y=y_fmri[ecog_val['pvalue'] > pvalue],
            mode='markers',
            marker=go.Marker(
                color='cyan',
                )
            ),
        go.Scatter(
            name='significant',
            x=x_ecog[ecog_val['pvalue'] <= pvalue],
            y=y_fmri[ecog_val['pvalue'] <= pvalue],
            mode='markers',
            marker=go.Marker(
                color='magenta',
                )
            ),
        go.Scatter(
            x=x_ecog,
            y=lr.slope * x_ecog + lr.intercept,
            mode='lines',
            marker=go.Marker(
                color='magenta'
                ),
            name='Fit'
            ),
        ]

    # title=f'Correlation with {float(kernel):.2f}mm kernel size<br />R<sup>2</sup> = {lr.rvalue ** 2:.3f}<br />Y = {lr.slope:.3f}X + {lr.intercept:.3f}',
    layout = go.Layout(
        xaxis=go.XAxis(
            title='ECoG',
            ),
        yaxis=go.YAxis(
            title='fMRI',
            ),
        )
    fig = go.Figure(
        data=traces,
        layout=layout,
        )

    return fig
