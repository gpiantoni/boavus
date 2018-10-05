from nipype import Function


def wrapper_corr(fmri_file, ecog_file, output_dir='./corr_values', pvalue=0.05):
    from pathlib import Path
    from boavus.corr.corrfmri import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(
        Path(fmri_file).resolve(),
        Path(ecog_file).resolve(),
        Path(output_dir).resolve(),
        pvalue))

def wrapper_summary(in_files, ecog_files, fmri_files, output_dir='./output'):
    from pathlib import Path
    from boavus.corr.summary import collect_corr

    collect_corr(in_files, ecog_files, fmri_files, Path(output_dir).resolve())


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


function_corr_summary = Function(
    input_names=[
        'in_files',
        'ecog_files',
        'fmri_files',
    ],
    function=wrapper_summary,
    )
