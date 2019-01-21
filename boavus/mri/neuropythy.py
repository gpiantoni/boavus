from nipype import Function


def wrapper_neuropythy_atlas(subject_id):
    from pathlib import Path
    from neuropythy.commands import atlas

    output_path = str(Path('.').resolve() / subject_id)

    atlas.main([
        subject_id,
        '--overwrite',
        '--create-directory',
        '--output-path',
        output_path,
        ])

    return output_path


function_neuropythy_atlas = Function(
    input_names=[
        'subject_id',
    ],
    output_names=[
        'output_dir',
    ],
    function=wrapper_neuropythy_atlas,
    )
