from nipype import Function, Node


def wrapper_prepare_design(analysis_dir, func, anat):
    from pathlib import Path
    from boavus.fsl.feat import prepare_design

    return str(prepare_design(Path(analysis_dir), Path(func), Path(anat)))


FEAT_model = Function(
    input_names=[
        'analysis_dir',
        'func',
        'anat',
    ],
    output_names=[
        'fsf_file',
    ],
    function=wrapper_prepare_design,
    )


node_featdesign = Node(FEAT_model, name='feat_design')
