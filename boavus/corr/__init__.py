from nipype import Function


def wrapper_corr(fmri_file, ecog_file, output_dir='.', pvalue=0.05):
    from pathlib import Path
    from boavus.corr.corrfmri import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(Path(fmri_file), Path(ecog_file), Path(output_dir), pvalue))


def wrapper_plot(fmri_file, ecog_file, corr_file, images_dir='.', pvalue=0.05):
    from pathlib import Path
    from boavus.corr.plot import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(Path(fmri_file), Path(ecog_file), Path(corr_file), Path(images_dir), pvalue))


def wrapper_plot_all(in_files, images_dir):
    from pathlib import Path
    from boavus.corr.plot_all import plot_corr_all

    png_r2, png_peaks = plot_corr_all(in_files, Path(images_dir))
    return str(png_r2), str(png_peaks)


function_corr = Function(
    input_names=[
        'fmri_file',
        'ecog_file',
        'output_dir',
        'pvalue',
    ],
    output_names=[
        'out_file',
    ],
    function=wrapper_corr,
    )


function_corr_plot = Function(
    input_names=[
        'fmri_file',
        'ecog_file',
        'corr_file',
        'images_dir',
        'pvalue',
    ],
    output_names=[
        'png_scatter',
    ],
    function=wrapper_plot,
    )


function_corr_plot_all = Function(
    input_names=[
        'in_files',
        'images_dir',
    ],
    output_names=[
        'png_rsquared',
        'png_peaks',
    ],
    function=wrapper_plot_all,
    )
