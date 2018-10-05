from shutil import copy


def collect_corr(in_files, output_dir):

    output_dir.mkdir(parents=True, exist_ok=True)

    for in_file in in_files:
        copy(in_file, output_dir)
