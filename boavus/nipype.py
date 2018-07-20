from nipype import Function



def wrapper_frequency(ieeg, method, taper, duration):
    from pathlib import Path
    from boavus.ieeg.psd import save_frequency

    return str(save_frequency(Path(ieeg), method, taper, duration))


def wrapper_ieeg_compare(analysis_dir, in_files, frequency_low=65, frequency_high=96,
                         baseline=False, method='dh2012', measure='dh2012_r2'):
    from pathlib import Path
    from boavus.ieeg.compare import compare_ieeg_freq

    return str(compare_ieeg_freq(Path(in_files[0]), Path(in_files[1]), Path(analysis_dir), frequency_low, frequency_high, baseline, method, measure))


def wrapper_prepare_design(analysis_dir, func, anat):
    from pathlib import Path
    from boavus.fsl.feat import prepare_design

    return str(prepare_design(Path(analysis_dir), Path(func), Path(anat)))


def wrapper_compare_fmri(analysis_dir, feat_path, measure='percent', normalize_to_mean=False):
    from pathlib import Path
    from boavus.fmri.compare import compare_fmri

    return str(compare_fmri(Path(analysis_dir), Path(feat_path), measure, normalize_to_mean))


def wrapper_at_elec(measure_nii, electrodes, freesurfer_dir='', upsample=False, graymatter=False, distance='guassian', kernel_start=6, kernel_end=8, kernel_step=1):
    from pathlib import Path
    from boavus.fmri.at_electrodes import calc_fmri_at_elec
    from numpy import arange

    kernels = arange(kernel_start, kernel_end, kernel_step)

    output = calc_fmri_at_elec(Path(measure_nii), Path(electrodes), Path(freesurfer_dir), upsample, kernels, graymatter, distance)
    return [str(x) for x in output]


def wrapper_corr(fmri_file, ecog_file, electrodes='', output_dir='', regions=[], PVALUE=0.05, PLOT=False):
    from pathlib import Path
    from boavus.ieeg.corrfmri import compute_corr_ecog_fmri

    return str(compute_corr_ecog_fmri(Path(fmri_file), Path(ecog_file), Path(electrodes), Path(output_dir), regions, PVALUE, PLOT))


function_ieeg_compare = Function(
    input_names=[
        'analysis_dir',
        'in_files',
        'frequency_low',
        'frequency_high',
        'baseline',
        'method',
        'measure',
    ],
    output_names=[
        'tsv_compare',
    ],
    function=wrapper_ieeg_compare,
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


function_fmri_compare = Function(
    input_names=[
        'analysis_dir',
        'feat_path',
        'measure',
        'normalize_to_mean',
    ],
    output_names=[
        'out_file',
    ],
    function=wrapper_compare_fmri,
    )


function_fmri_atelec = Function(
    input_names=[
        'measure_nii',
        'electrodes',
        'freesurfer_dir',
        'upsample',
        'graymatter',
        'distance',
        'kernel_start',
        'kernel_end',
        'kernel_step',
    ],
    output_names=[
        'fmri_vals',
        'n_voxels',
    ],
    function=wrapper_at_elec,
    )


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
