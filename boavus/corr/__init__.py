from nipype import Function


def wrapper_corr(fmri_file, ecog_file, output_dir='', pvalue=0.05):
    from pathlib import Path
    from boavus.corr.corrfmri import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(Path(fmri_file), Path(ecog_file), Path(output_dir), pvalue))


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
