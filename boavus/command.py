"""Complex but elegant approach to passing arguments and parameters.

Make sure that the functions are organized in module/function.py.
"""
from inspect import signature, getdoc
from collections import defaultdict
from argparse import ArgumentParser, RawTextHelpFormatter
from importlib import import_module
from logging import getLogger, StreamHandler, Formatter, INFO, DEBUG
from pathlib import Path
from warnings import filterwarnings

filterwarnings('ignore', category=FutureWarning)
lg = getLogger('boavus')

FOLDERS_DOC = {
    'bids_dir': 'The directory with the raw data organized in the BIDS format',
    'freesurfer_dir': 'The directory with Freesurfer',
    'analysis_dir': 'The directory with preprocessed / analyzed data for each subject',
    'output_dir': 'The directory with custom output',
    }


def __main__():
    import boavus
    all_mod = defaultdict(dict)
    for one in sorted(Path(boavus.__path__[0]).rglob('*.py')):
        mod = import_module(str(one.relative_to(Path(__file__).parents[1])).replace('/', '.')[:-3])
        if hasattr(mod, 'main'):
            mod_name = one.stem
            grp_name = one.parent.stem
            all_mod[grp_name][mod_name] = mod.main

    parser = ArgumentParser(description='Tools to analyze data structured as BIDS in Python', formatter_class=RawTextHelpFormatter)
    list_modules = parser.add_subparsers(title='Modules', help='Modules containing the functions')

    for m_k, m_v in all_mod.items():
        module = list_modules.add_parser(m_k)
        module.set_defaults(module=m_k)
        list_functions = module.add_subparsers(title=f'Functions in {m_k} module')

        for f_k, f_v in m_v.items():
            function = list_functions.add_parser(f_k,
                                                 formatter_class=RawTextHelpFormatter)
            function.set_defaults(function=f_k)
            add_to_parser(function, f_v)
            function.add_argument('-l', '--log', default='info',
                                  help='Logging level: info (default), debug')

    return parser


def add_to_parser(function, main_f):
    doc = getdoc(main_f)
    args = {}
    maindoc, docargs = doc.split('\nParameters\n----------\n')
    docargs = docargs.split('\n')
    for i in range(0, len(docargs), 2):
        a_name, a_type = docargs[i].split(':')
        if i < len(docargs) - 1:
            comment = docargs[i + 1].strip()
        else:
            comment = ''
        args[a_name.strip()] = (a_type.strip(), comment)

    sign = signature(main_f)

    folders_arg = function.add_argument_group('folders arguments')
    optionals_arg = function.add_argument_group('optional arguments')

    for name, param in sign.parameters.items():
        if args[name][0] == 'path':
            one_arg = folders_arg
            help_str = FOLDERS_DOC[name]
            metavar = name.upper()
            action = None
            const = None

        elif args[name][0] == 'bool':
            assert not param.default, f'bool value {name} should be False, otherwise it\'s hard to interpret'
            one_arg = optionals_arg
            help_str = args[name][1]
            metavar = None
            action = 'store_const'
            const = not param.default

        else:
            one_arg = optionals_arg
            help_str = args[name][1]
            metavar = f'"{param.default}"'
            action = None
            const = None

        if param.default == param.empty:
            required = True
        else:
            required = False
        if not required and args[name][0] == 'path':
            help_str = '(optional) ' + help_str

        one_arg.add_argument(
            '--' + param.name,
            required=required,
            help=help_str,
            metavar=metavar,
            action=action,
            const=const,
            default=param.default,
            )


def boavus(arguments=None):

    parser = __main__()

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
    Use the leftover arguments only
    """
    # this only works if all the arguments are paths
    for k, v in args.items():
        if k.endswith('_dir'):
            args[k] = _path(v)

    """
    Call the actual main function of the specified .py file
    """
    lg.debug(f'Calling main() from {module.__file__} with: ' + ', '.join(f'{k}={v}' for k, v in args.items()))
    module.main(**args)


def _path(dirname):
    """Always use absolute paths, easier to control when working with FSL / Freesurfer"""
    if dirname is None:
        return None
    else:
        return Path(dirname).resolve()
