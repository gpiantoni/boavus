from shutil import copy


def collect_corr(in_files, ecog_files, fmri_files, output_dir):

    rsquared_dir = output_dir / 'rsquared'
    rsquared_dir.mkdir(parents=True, exist_ok=True)

    ecog_dir = output_dir / 'ecog'
    ecog_dir.mkdir(parents=True, exist_ok=True)

    fmri_dir = output_dir / 'fmri'
    fmri_dir.mkdir(parents=True, exist_ok=True)

    for in_file in in_files:
        copy(in_file, output_dir)

    for in_file in ecog_files:
        copy(in_file, ecog_dir)

    for in_file in fmri_files:
        copy(in_file, fmri_dir)
