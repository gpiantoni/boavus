from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from .fmri.percent import run_fmri_percent

STEPS = [
    'fmri_percent',
    'fasdfas',
    'fdsafas',
    ]


parser = ArgumentParser(description='Tools to analyze data structured as BIDS in Python', formatter_class=RawTextHelpFormatter)
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('output_dir', help='The directory where the output files '
                    'will be stored.')
parser.add_argument(
    'steps', nargs='+', choices=STEPS, metavar='step',
    help='fmri_percent: compute the percent change, requires feat_dir\n'
         'another_one: test')
parser.add_argument('--feat_dir', help='The directory with FSL/feat output')

args = parser.parse_args()


def main():

    print(args)
    output_dir = Path(args.output_dir)

    for step in args.steps:

        if step == 'fmri_percent':
            feat_dir = Path(args.feat_dir)
            run_fmri_percent(feat_dir, output_dir)


if __name__ == '__main__':
    main()
