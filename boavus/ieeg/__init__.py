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
