from logging import getLogger

from numpy import argmax, polyfit, isnan, NaN, isin
from numpy.testing import assert_array_equal
from scipy.stats import linregress

from bidso.utils import read_tsv, replace_underscore


lg = getLogger(__name__)

PNG_DIR = 'corr_ieeg_fmri_png'
SINGLE_POINTS_DIR = 'corr_ieeg_fmri_point'


def compute_corr_ecog_fmri(fmri_file, ecog_file, output_dir, PVALUE):
    """
    TODO
    electrodes = Electrodes(electrodes_file)
    n_all_elec = len(ecog_tsv)
    # use only values from electrodes which are in the ROI
    labels_in_roi = find_labels_in_regions(electrodes, regions)
    ecog_tsv = list(filter(lambda x: x['channel'] in labels_in_roi, ecog_tsv))
    lg.debug(f'Using {len(ecog_tsv)}/{n_all_elec} electrodes in ROI')
    """

    fmri_tsv = read_tsv(fmri_file)
    ecog_tsv = read_tsv(ecog_file)
    fmri_tsv = select_channels(fmri_tsv, ecog_tsv)
    kernel_sizes = fmri_tsv.dtype.names[1:]

    results_tsv = output_dir / replace_underscore(ecog_file.stem, 'bold_r2.tsv')
    with results_tsv.open('w') as f:
        f.write('Kernel\tRsquared\n')

        for kernel in kernel_sizes:
            try:
                r2 = compute_rsquared(
                    ecog_tsv['measure'],
                    fmri_tsv[kernel],
                    ecog_tsv['pvalue'],
                    PVALUE)

            except Exception:
                r2 = NaN

            f.write(f'{kernel}\t{r2}\n')

    return results_tsv


def select_channels(fmri_vals, ecog_vals):
    """make sure we're using the same channels and in the same order
    """
    fmri_idx = isin(fmri_vals['channel'], (ecog_vals['channel']))
    fmri_vals = fmri_vals[fmri_idx]
    assert_array_equal(fmri_vals['channel'], ecog_vals['channel'])

    return fmri_vals


def compute_rsquared(x, y, p_val, PVALUE):
    mask = ~isnan(x) & ~isnan(y) & (p_val <= PVALUE)

    lr = linregress(x[mask], y[mask])
    return lr.rvalue ** 2


def read_shape(one_tsv):
    results = read_tsv(one_tsv)
    k = [float(x['Kernel']) for x in results]
    rsquared = [float(x['Rsquared']) for x in results]

    return polyfit(k, rsquared, 2)[0], k[argmax(rsquared)], max(rsquared)
