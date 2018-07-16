from nipype import Function, Node


def wrapper_read_motor_data(analysis_dir, ieeg, electrodes):
    from pathlib import Path
    from boavus.ieeg.read import read_motor_data

    outputs = read_motor_data(Path(analysis_dir), Path(ieeg), Path(electrodes))
    return [str(x) for x in outputs]


def wrapper_preprocess_ecog(ieeg):
    from pathlib import Path
    from boavus.ieeg.preprocessing import preprocess_ecog

    return preprocess_ecog(Path(ieeg))


def wrapper_frequency(ieeg, method, taper, duration):
    from pathlib import Path
    from boavus.ieeg.psd import save_frequency

    return str(save_frequency(Path(ieeg), method, taper, duration))


def wrapper_prepare_design(analysis_dir, func, anat):
    from pathlib import Path
    from boavus.fsl.feat import prepare_design

    return str(prepare_design(Path(analysis_dir), Path(func), Path(anat)))


function_ieeg_read = Function(
    input_names=[
        'analysis_dir',
        'ieeg',
        'electrodes',
    ],
    output_names=[
        'ieeg_files',
    ],
    function=wrapper_read_motor_data,
    )


function_ieeg_preprocess = Function(
    input_names=[
        'ieeg',
    ],
    output_names=[
        'ieeg',
    ],
    function=wrapper_preprocess_ecog,
    )


function_ieeg_frequency = Function(
    input_names=[
        'ieeg',
        'method',
        'taper',
        'duration',
    ],
    output_names=[
        'ieeg',
    ],
    function=wrapper_frequency,
    )


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
