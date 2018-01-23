from argparse import ArgumentParser, RawTextHelpFormatter, RawDescriptionHelpFormatter
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

args = dict(
    fsl=dict(
        help='test fsl',
        feat=dict(
            help='run FEAT using the events.tsv information',
            arguments=[
                'bids_dir',
                'feat_dir',
                ],
            ),
        ),
    fmri=dict(
        help='test fmri',
        percent=dict(
            help='compute percent change of the BOLD signal',
            arguments=[
                'feat_dir',
                'output_dir',
                ]
            ),
        ),
    ieeg=dict(
        help='test ieeg',
        electrodes=dict(
            help='project electrodes in fMRI and assign them regions',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                ]
            ),
        corrfmri=dict(
            help='find best kernel size for iEEG electrodes based on fMRI',
            arguments=[
                'bids_dir',
                'feat_dir',
                'freesurfer_dir',
                'output_dir',
                ]
            ),
        )
    )


parser = ArgumentParser(description='Tools to analyze data structured as BIDS in Python', formatter_class=RawTextHelpFormatter)
list_modules = parser.add_subparsers(title='Modules', help='Modules containing the functions')

for m_k, m_v in args.items():
    module = list_modules.add_parser(m_k, help=m_v.pop('help'))
    module.set_defaults(module=m_k)
    list_functions = module.add_subparsers(title=f'Functions in {m_k} module')

    for f_k, f_v in m_v.items():
        function = list_functions.add_parser(f_k, help=f_v.pop('help'))
        function.set_defaults(function=f_k)
        function.add_argument('-l', '--log', default='info',
                              help='Logging level: info (default), debug')

        required = function.add_argument_group('required arguments')

        for arg in f_v['arguments']:
            if arg == 'bids_dir':
                required.add_argument('--bids_dir', required=True,
                                      help='test')

            elif arg == 'freesurfer_dir':
                required.add_argument('--freesurfer_dir', required=True,
                                      help='The directory with Freesurfer')

            elif arg == 'feat_dir':
                required.add_argument('--feat_dir', required=True,
                                      help='The directory with FSL/feat')

            elif arg == 'output_dir':
                required.add_argument('--output_dir', required=True,
                                      help='The directory with custom output')


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

    if args.module == 'fsl':

        if args.function == 'feat':
            bids_dir = _path(args.bids_dir)
            feat_dir = _path(args.feat_dir)
            run_fsl_feat(bids_dir, feat_dir)

    elif args.module == 'fmri':

        if args.function == 'percent':
            feat_dir = _path(args.feat_dir)
            output_dir = _path(args.output_dir)
            run_fmri_percent(feat_dir, output_dir)

    elif args.module == 'ieeg':

        if args.function == 'electrodes':
            bids_dir = _path(args.bids_dir)
            freesurfer_dir = _path(args.freesurfer_dir)
            run_ieeg_electrodes(bids_dir, freesurfer_dir)

        elif args.function == 'corrfmri':
            bids_dir = _path(args.bids_dir)
            feat_dir = _path(args.feat_dir)
            freesurfer_dir = _path(args.freesurfer_dir)
            output_dir = _path(args.output_dir)
            run_ieeg_corrfmri(bids_dir, feat_dir, freesurfer_dir, output_dir)


def _path(dirname):
    """Always use absolute paths, easier to control when working with FSL / Freesurfer"""
    return Path(dirname).resolve()
