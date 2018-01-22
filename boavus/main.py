from argparse import ArgumentParser, RawTextHelpFormatter
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG
from pathlib import Path

from warnings import filterwarnings

from .fmri.percent import run_fmri_percent
from .fsl.feat import run_fsl_feat
from .ieeg.corr_fmri import run_ieeg_corrfmri
from .ieeg.electrodes import run_ieeg_electrodes


filterwarnings('ignore', category=FutureWarning)
lg = getLogger('boavus')

STEPS = [
    'fmri_percent',
    'fsl_feat',
    'ieeg_corrfmri',
    'ieeg_electrodes',
    ]


parser = ArgumentParser(description='Tools to analyze data structured as BIDS in Python', formatter_class=RawTextHelpFormatter)
"""
subparsers = parser.add_subparsers(title='subcommands', help='sub-command help')

parser_a = subparsers.add_parser('fsl_feat', help='a help')
parser_a.set_defaults(func='fsl_feat')
arg_feat_dir = {'name':'--feat_dir', 'help':'The directory with FSL/feat'}

parser_a.add_argument(**arg_feat_dir)

parser_b = subparsers.add_parser('fmri_percent', help='a help')

parser_c = subparsers.add_parser('ieeg_corrfmri', help='a help')

"""
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument(
    'steps', nargs='+', choices=STEPS, metavar='step',
    help='fsl_feat: run feat (requires feat_dir)\n'
         'fmri_percent: compute the percent change (requires feat_dir, output_dir)\n'
         'ieeg_electrodes: project electrodes to surface (requires bids_dir, freesurfer_dir)\n'
         'ieeg_corrfmri: find kernel size for iEEG based on fMRI (requires feat_dir, freesurfer_dir, output_dir)\n'
    )

parser.add_argument(
    '--feat_dir',
    help='The directory with FSL/feat')
parser.add_argument(
    '-f', '--freesurfer_dir',
    help='The directory with Freesurfer')
parser.add_argument(
    '-o', '--output_dir',
    help='The directory with custom output')
parser.add_argument(
    '-l', '--log', default='info',
    help='Logging level: info (default), debug')


args = parser.parse_args()


def main():
    print(args)

    DATE_FORMAT = '%H:%M:%S'
    if args.log[:1].lower() == 'i':
        lg.setLevel(INFO)
        FORMAT = '{asctime:<10}{message}'

    elif args.log[:1].lower() == 'd':
        lg.setLevel(DEBUG)
        FORMAT = '{asctime:<10}{levelname:<10}{filename:<40}(l. {lineno: 6d})/ {funcName:<40}: {message}'

    formatter = Formatter(fmt=FORMAT, datefmt=DATE_FORMAT, style='{')
    handler = StreamHandler()
    handler.setFormatter(formatter)

    lg.handlers = []
    lg.addHandler(handler)

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

        if step == 'ieeg_corrfmri':
            feat_dir = _path(args.feat_dir)
            freesurfer_dir = _path(args.freesurfer_dir)
            output_dir = _path(args.output_dir)

            run_ieeg_corrfmri(bids_dir, feat_dir, freesurfer_dir, output_dir)

        if step == 'ieeg_electrodes':
            freesurfer_dir = _path(args.freesurfer_dir)

            run_ieeg_electrodes(bids_dir, freesurfer_dir)


def _path(dirname):
    """Always use absolute paths, easier to control when working with FSL / Freesurfer"""
    return Path(dirname).resolve()
