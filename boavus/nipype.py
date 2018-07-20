from nipype import Function


def wrapper_corr(fmri_file, ecog_file, electrodes='', output_dir='', regions=[], PVALUE=0.05, PLOT=False):
    from pathlib import Path
    from boavus.ieeg.corrfmri import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(Path(fmri_file), Path(ecog_file), Path(electrodes), Path(output_dir), regions, PVALUE, PLOT))


function_corr = Function(
    input_names=[
        'fmri_file',
        'ecog_file',
        'electrodes',
        'output_dir',
        'regions',
        'PVALUE',
        'PLOT',
    ],
    output_names=[
        'out_file',
    ],
    function=wrapper_corr,
    )
