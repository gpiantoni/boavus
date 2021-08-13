#!/usr/bin/env python3

from argparse import ArgumentParser
from os import environ
from pathlib import Path
from pdoc.cli import parser as pdoc_parser
from pdoc.cli import main as pdoc
from shutil import rmtree
from subprocess import run
from tempfile import mkstemp
from urllib.request import urlopen
from zipfile import ZipFile

PACKAGE = 'boavus'


parser = ArgumentParser(prog='make',
                        description=f'Run tests and documentation for {PACKAGE}')
parser.add_argument('-r', '--release', action='store_true',
                    help='create a point release')
parser.add_argument('-m', '--major_release', action='store_true',
                    help='create a major release')
parser.add_argument('-g', '--get_files', action='store_true',
                    help='download datasets to run tests')
parser.add_argument('-t', '--tests', action='store_true',
                    help='run tests')
parser.add_argument('-d', '--docs', action='store_true',
                    help='create documentations')
parser.add_argument('-c', '--clean', action='store_true',
                    help='clean up docs (including intermediate files)')

args = parser.parse_args()


BASE_PATH = Path(__file__).resolve().parent
PKG_PATH = BASE_PATH / PACKAGE
VER_PATH = PKG_PATH / 'VERSION'
CHANGES_PATH = BASE_PATH / 'CHANGES.rst'

DOCS_PATH = BASE_PATH / 'docs'
API_PATH = BASE_PATH / 'docs' / PACKAGE

TEST_PATH = BASE_PATH / 'tests'
DATA_PATH = TEST_PATH / 'data'
ANALYSIS_PATH = DATA_PATH / 'analysis'


def _new_version(level):

    # read current version (and changelog)
    with VER_PATH.open() as f:
        major, minor = f.read().rstrip('\n').split('.')
        major, minor = int(major), int(minor)

    with CHANGES_PATH.open() as f:
        changes = f.read().split('\n')

    # update version (if major, reset minor)
    if level == 'major':
        major += 1
        minor = 1
    elif level == 'minor':
        minor += 1
    version = '{:d}.{:02d}'.format(major, minor)

    # ask user for comment
    comment = input('Comment for {} release v{}: '.format(level, version))
    if comment == '':
        print('empty comment, aborted')
        return

    # update change log
    ver_comment = '- **' + version + '**: ' + comment

    if level == 'major':
        marker = '=========='
        TO_ADD = ['Version ' + str(major),
                  '----------',
                  ver_comment,
                  '',
                  ]

    elif level == 'minor':
        marker = '----------'
        TO_ADD = [ver_comment,
                  ]

    index = changes.index(marker) + 1
    changes = changes[:index] + TO_ADD + changes[index:]
    with CHANGES_PATH.open('w') as f:
        f.write('\n'.join(changes))

    with VER_PATH.open('w') as f:
        f.write(version + '\n')

    return version, comment


def _release(level):
    """TODO: we should make sure that we are on master release"""

    _docs()

    version, comment = _new_version(level)

    if version is not None:

        run(['git',
             'commit',
             str(VER_PATH.relative_to(BASE_PATH)),
             str(CHANGES_PATH.relative_to(BASE_PATH)),
             '--amend',
             '--no-edit',
             ])
        run(['git',
             'tag',
             '-a',
             'v' + version,
             '-m',
             '"' + comment + '"',
             ])
        run(['git',
             'push',
             'origin',
             '--tags',
             ])
        run(['git',
             'push',
             'origin',
             'master',
             '-f',
             ])


def _get_files():

    url_data = environ.get('DATA_BOAVUS', False)  # raise error if it doesn't exist print('missing URL, please contact developers')
    if not url_data:
        print('You need to specify the environment variable DATA_BOAVUS containing the link to the data repository.')
        print('Contact the developer for the link')
        return 1

    if environ.get('CI', False) and environ.get('DOWNLOADS', False):
        DOWNLOADS_DIR = Path(environ.get('DOWNLOADS'))
        DOWNLOADS_DIR.mkdir(exist_ok=True, parents=True)
        tmp_file = DOWNLOADS_DIR / 'boavus.zip'
    else:
        tmp_file = Path(mkstemp(suffix='.zip')[1])

    if not tmp_file.exists() or tmp_file.stat().st_size == 0:
        with urlopen(url_data) as u, tmp_file.open('wb') as f:
            f.write(u.read())

    with ZipFile(tmp_file) as zf:
        zf.extractall(path=TEST_PATH)

    (TEST_PATH / 'boavus').rename(DATA_PATH)

    return 0


def _tests():

    rmtree(ANALYSIS_PATH, ignore_errors=True)

    CMD = ['pytest',
           f'--cov={PACKAGE}',
           '--disable-warnings',
           '--capture=no',
           'tests',
           ]

    output = run(CMD)

    if environ.get('CI', False):
        codecov_file = Path('codecov.sh')
        with urlopen('https://codecov.io/bash') as u, codecov_file.open('wb') as f:
            f.write(u.read())
        run([
            'bash',
            'codecov.sh',
            ])
    else:
        run([
            'coverage',
            'html',
            ])

    return output.returncode


def _docs():
    rmtree(API_PATH, ignore_errors=True)
    args = pdoc_parser.parse_args([
        PACKAGE,
        '--output-dir',
        str(DOCS_PATH),
        '--html',
        ])
    pdoc(args)

    run(['git',
         'add',
         'docs',
         ])

    return 0


def _clean_all():
    rmtree(API_PATH, ignore_errors=True)
    rmtree(DATA_PATH, ignore_errors=True)
    rmtree(ANALYSIS_PATH, ignore_errors=True)


if __name__ == '__main__':
    returncode = 0

    if args.clean:
        _clean_all()

    if args.get_files:
        returncode = _get_files()

    if args.tests:
        returncode = _tests()

    if args.docs:
        returncode = _docs()

    if args.release:
        _release('minor')

    if args.major_release:
        _release('major')

    exit(returncode)
