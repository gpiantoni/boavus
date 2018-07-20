from nipype import Function

def wrapper_read_ieeg_block(ieeg, electrodes, conditions, minimalduration):
    from pathlib import Path
    from boavus.ieeg.read import read_ieeg_block

    outputs = read_ieeg_block(
        Path(ieeg),
        Path(electrodes),
        conditions,
        minimalduration,
        Path('.').resolve())
    return [str(x) for x in outputs]


def wrapper_preprocess(ieeg, reref, duration):
    from pathlib import Path
    from boavus.ieeg.preprocessing import preprocess_ecog

    output = preprocess_ecog(
        Path(ieeg),
        reref,
        duration,
        Path('.').resolve())
    return str(output)


def wrapper_powerspectrum(ieeg, method, taper, duration):
    from pathlib import Path
    from boavus.ieeg.psd import compute_powerspectrum

    output = compute_powerspectrum(
        Path(ieeg),
        method,
        taper,
        duration,
        Path('.').resolve())
    return str(output)


function_ieeg_read = Function(
    input_names=[
        'ieeg',
        'electrodes',
        'conditions',
        'minimalduration',
    ],
    output_names=[
        'ieeg',
    ],
    function=wrapper_read_ieeg_block,
    )


function_ieeg_preprocess = Function(
    input_names=[
        'ieeg',
        'reref',
        'duration',
    ],
    output_names=[
        'ieeg',
    ],
    function=wrapper_preprocess,
    )


function_ieeg_powerspectrum = Function(
    input_names=[
        'ieeg',
        'method',
        'taper',
        'duration',
    ],
    output_names=[
        'ieeg',
    ],
    function=wrapper_powerspectrum,
    )
