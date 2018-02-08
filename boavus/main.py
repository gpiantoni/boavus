"""Complex but elegant approach to passing arguments and parameters.

Make sure that the functions are organized in module/function.py. Each .py
file needs a PARAMETERS dict and a main() function. The input of the main()
function should also be specified in the args dictionary below.
"""
from argparse import ArgumentParser, RawTextHelpFormatter
from json import load, dump
from importlib import import_module
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG
from pathlib import Path
from pprint import pformat
from warnings import filterwarnings

filterwarnings('ignore', category=FutureWarning)
lg = getLogger('boavus')


args = dict(
    freesurfer=dict(
        help='freesurfer functions',
        reconall=dict(
            help='run freesurfer recon-all',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                ],
            ),
        ),
    fsl=dict(
        help='fsl functions',
        feat=dict(
            help='run FEAT using the events.tsv information',
            arguments=[
                'bids_dir',
                'analysis_dir',
                ],
            ),
        coreg=dict(
            help='coreg feat with freesurfer',
            arguments=[
                'analysis_dir',
                'freesurfer_dir',
                ],
            ),
        ),
    fmri=dict(
        help='fmri functions',
        compare=dict(
            help='compute percent change of the BOLD signal',
            arguments=[
                'analysis_dir',
                ]
            ),
        ),
    ieeg=dict(
        help='ieeg functions',
        project_electrodes=dict(
            help='project electrodes to brain surface',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                'analysis_dir',
                ]
            ),
        assign_regions=dict(
            help='assign electrodes to brain regions',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                ]
            ),
        plot_electrodes=dict(
            help='plot electrodes onto the brain surface',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                'output_dir',
                ]
            ),
        preprocessing=dict(
            help='read in the data for move and rest',
            arguments=[
                'bids_dir',
                'analysis_dir',
                ]
            ),
        psd=dict(
            help='compute psd for two conditions',
            arguments=[
                'analysis_dir',
                ]
            ),
        compare=dict(
            help='compare the two conditions in percent change or zstat',
            arguments=[
                'analysis_dir',
                ]
            ),
        corrfmri=dict(
            help='find best kernel size for iEEG electrodes based on fMRI',
            arguments=[
                'bids_dir',
                'freesurfer_dir',
                'analysis_dir',
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
        function = list_functions.add_parser(f_k,
                                             help=f_v['help'],  # when in module help
                                             description=f_v['help'],  # when in the function help
                                             formatter_class=RawTextHelpFormatter)
        function.set_defaults(function=f_k)
        function.add_argument('-l', '--log', default='info',
                              help='Logging level: info (default), debug')
        function.add_argument('-p', '--parameters',
                              help='json file containing the parameters. If it does not exist, it simply generates a json file with the default values and exits. If it exists, it runs the function with those parameters.')

        required = function.add_argument_group('required arguments')

        for arg in f_v['arguments']:
            if arg == 'bids_dir':
                required.add_argument('--bids_dir', required=True,
                                      help='test')

            elif arg == 'freesurfer_dir':
                required.add_argument('--freesurfer_dir', required=True,
                                      help='The directory with Freesurfer')

            elif arg == 'analysis_dir':
                required.add_argument('--analysis_dir', required=True,
                                      help='The directory with preprocessed / analyzed data for each subject')

            elif arg == 'output_dir':
                required.add_argument('--output_dir', required=True,
                                      help='The directory with custom output')


def boavus(arguments=None):

    # treat arguments as dict so we can remove keys as we go
    args = vars(parser.parse_args(arguments))

    # log can be info or debug
    DATE_FORMAT = '%H:%M:%S'
    log_level = args.pop('log')
    if log_level[:1].lower() == 'i':
        lg.setLevel(INFO)
        FORMAT = '{asctime:<10}{message}'

    elif log_level[:1].lower() == 'd':
        lg.setLevel(DEBUG)
        FORMAT = '{asctime:<10}{levelname:<10}{filename:<40}(l. {lineno: 6d})/ {funcName:<40}: {message}'

    formatter = Formatter(fmt=FORMAT, datefmt=DATE_FORMAT, style='{')
    handler = StreamHandler()
    handler.setFormatter(formatter)

    lg.handlers = []
    lg.addHandler(handler)

    """
    the user passes two arguments: a module and a function. A module is the
    name of the folder and the function is the name of the .py file.
    Each .py file contains one and ony one main() function, which is what is
    called in general.
    """
    module = import_module('boavus.' + args.pop('module') + '.' + args.pop('function'))

    """
    We also modify the parameters. If the user passes a json file that doesn't
    exist, the program simply writes down the PARAMETERS for the specific .py
    file and exits. If it does exist, then we load the parameters.
    """
    parameters_json = args.pop('parameters')

    if parameters_json is not None:
        parameters_json = _path(parameters_json)

        if parameters_json.exists():
            with parameters_json.open() as f:
                module.PARAMETERS.update(load(f))

            lg.debug(pformat(module.PARAMETERS))

        else:
            with parameters_json.open('w') as f:
                dump(module.PARAMETERS, f, indent='  ')
                lg.debug(f'Default parameters for {module.__name__} written to {str(parameters_json)}\n'
                         'Modify the .json file and run again:\n'
                         f'"{module.__name__.replace(".", " ")}" with the previous arguments (including "-p {str(parameters_json)}")')

                return

    """
    Use the leftover arguments only
    """
    # this only works if all the arguments are paths
    for k, v in args.items():
        args[k] = _path(v)

    """
    Call the actual main function of the specified .py file
    """
    lg.debug(f'Calling main() from {module.__file__} with: ' + ', '.join(f'{k}={v}' for k, v in args.items()))
    module.main(**args)


def _path(dirname):
    """Always use absolute paths, easier to control when working with FSL / Freesurfer"""
    return Path(dirname).resolve()
