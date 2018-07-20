from nipype import Function


def wrapper_fmri_compare(feat_path, measure, normalize_to_mean):
    from pathlib import Path
    from boavus.fmri.compare import compare_fmri

    output = compare_fmri(
        Path(feat_path),
        measure,
        normalize_to_mean,
        Path('.').resolve())
    return str(output)


function_fmri_compare = Function(
    input_names=[
        'feat_path',
        'measure',
        'normalize_to_mean',
    ],
    output_names=[
        'out_file',
    ],
    function=wrapper_fmri_compare,
    )
