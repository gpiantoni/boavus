#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser
from subprocess import run
from shutil import rmtree
from os import putenv, environ

PACKAGE = 'boavus'
putenv('CI', 'true')  # make sure putenv is supported


parser = ArgumentParser(prog='make',
                        description=f'Run tests and documentation for {PACKAGE}')
parser.add_argument('-r', '--release', action='store_true',
                    help='create a point release')
parser.add_argument('-m', '--major_release', action='store_true',
                    help='create a major release')
parser.add_argument('-t', '--tests', action='store_true',
                    help='run tests')
parser.add_argument('-d', '--docs', action='store_true',
                    help='create documentations (run tests first)')
parser.add_argument('-c', '--clean', action='store_true',
                    help='clean up docs (including intermediate files)')

args = parser.parse_args()


BASE_PATH = Path(__file__).resolve().parent
PKG_PATH = BASE_PATH / PACKAGE
VER_PATH = PKG_PATH / 'VERSION'
CHANGES_PATH = BASE_PATH / 'CHANGES.rst'

DOCS_PATH = BASE_PATH / 'docs'
BUILD_PATH = DOCS_PATH / 'build'
SOURCE_PATH = DOCS_PATH / 'source'
HTML_PATH = BUILD_PATH / 'html'
API_PATH = SOURCE_PATH / 'api'

TEST_PATH = BASE_PATH / 'tests'
DATA_PATH = TEST_PATH / 'data'
BIDS_PATH = DATA_PATH / 'bids'
DERIVATIVES_PATH = DATA_PATH / 'derivatives'
ANALYSIS_PATH = DERIVATIVES_PATH / 'analysis'
BOAVUS_PATH = DERIVATIVES_PATH / 'boavus'
FREESURFER_PATH = DERIVATIVES_PATH / 'freesurfer'


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


def _tests():

    rmtree(BIDS_PATH, ignore_errors=True)
    rmtree(ANALYSIS_PATH, ignore_errors=True)
    rmtree(BOAVUS_PATH, ignore_errors=True)

    CMD = ['pytest',
           f'--cov={PACKAGE}',
           'tests',
           ]

    output = run(CMD)

    run([
        'coverage',
        'combine',
        ])
    if not environ.get('CI', False):
        run([
            'coverage',
            'html',
            ])

    return output.returncode


def _docs():
    run([
        'sphinx-apidoc',
        '-f',
        '-e',
        '--module-first',
        '-o',
        str(API_PATH),
        str(PKG_PATH),
        ])
    output = run([
        'sphinx-build',
        '-T',
        '-b',
        'html',
        '-d',
        str(BUILD_PATH / 'doctrees'),
        str(SOURCE_PATH),
        str(HTML_PATH),
        ])
    return output.returncode


def _clean_all():
    rmtree(BUILD_PATH, ignore_errors=True)
    rmtree(API_PATH, ignore_errors=True)
    rmtree(BIDS_PATH, ignore_errors=True)
    rmtree(ANALYSIS_PATH, ignore_errors=True)
    rmtree(BOAVUS_PATH, ignore_errors=True)
    rmtree(FREESURFER_PATH, ignore_errors=True)


if __name__ == '__main__':
    returncode = 0

    if args.clean:
        _clean_all()

    if args.tests:
        returncode = _tests()

    if args.docs:
        returncode = _docs()

    if args.release:
        _release('minor')

    if args.major_release:
        _release('major')

    exit(returncode)
