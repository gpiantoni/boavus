
def plot_single_points(ecog_tsv, fmri_tsv):
    best_kernel = KERNELS[argmax(all_r2)]
    fig = scatter_single_points(ecog_tsv, fmri_tsv, best_kernel, PVALUE)
    singlepoints_png = output_dir / SINGLE_POINTS_DIR / (results_tsv.stem + '.png')
    export_plotly(fig, singlepoints_png)

def scatter_single_points(ecog_tsv, fmri_tsv, kernel, pvalue):
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


