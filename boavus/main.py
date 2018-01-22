from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from .fmri.percent import run_fmri_percent
from .fsl.feat import run_fsl_feat

STEPS = [
    'fmri_percent',
    'fsl_feat',
    'fdsafas',
    ]


parser = ArgumentParser(description='Tools to analyze data structured as BIDS in Python', formatter_class=RawTextHelpFormatter)
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument(
    'steps', nargs='+', choices=STEPS, metavar='step',
    help='fsl_feat: run feat (requires feat_dir)\n'
         'fmri_percent: compute the percent change (requires feat_dir, output_dir)\n'
         'another_one: test')

parser.add_argument(
    '-f', '--feat_dir',
    help='The directory with FSL/feat')
parser.add_argument(
    '-o', '--output_dir',
    help='The directory with custom output')

args = parser.parse_args()


def main():

    print(args)
    bids_dir = _path(args.bids_dir)

    for step in args.steps:

        if step == 'fsl_feat':
            feat_dir = _path(args.feat_dir)
            run_fsl_feat(bids_dir, feat_dir)

        if step == 'fmri_percent':
            feat_dir = _path(args.feat_dir)
            output_dir = _path(args.output_dir)
            run_fmri_percent(feat_dir, output_dir)


def _path(dirname):
    """Always use absolute paths, easier to control when working with FSL / Freesurfer"""
    return Path(dirname).resolve()


if __name__ == '__main__':
    main()
