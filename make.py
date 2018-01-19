#!/usr/bin/env python3

from pathlib import Path
from argparse import ArgumentParser
from subprocess import run
from shutil import rmtree
from os import putenv, environ

PROJECT = 'boavus'
putenv('CI', 'true')  # make sure putenv is supported

BASE_PATH = Path(__file__).resolve().parent

DOCS_PATH = BASE_PATH / 'docs'
BUILD_PATH = DOCS_PATH / 'build'
SOURCE_PATH = DOCS_PATH / 'source'
HTML_PATH = BUILD_PATH / 'html'
API_PATH = SOURCE_PATH / 'api'

TEST_PATH = BASE_PATH / 'tests'
DATA_PATH = TEST_PATH / 'data'
BIDS_PATH = DATA_PATH / 'bids'
DERIVATIVES_PATH = DATA_PATH / 'derivatives'
FEAT_PATH = DERIVATIVES_PATH / 'feat'


parser = ArgumentParser(prog='make boavus',
                        description='Replacement for Makefile')
parser.add_argument('command',
                    help='Command to execute (doc, test, clean)')

args = parser.parse_args()


if args.command == 'doc':
    run([
        'sphinx-build',
        '-T',
        '-b',
        'html', '-d',
        str(BUILD_PATH / 'doctrees'),
        str(SOURCE_PATH),
        str(HTML_PATH),
        ])

elif args.command == 'test':
    rmtree(BIDS_PATH, ignore_errors=True)
    if environ.get('FSLDIR') is not None:
        rmtree(FEAT_PATH, ignore_errors=True)

    run([
        'py.test',
        '-x',
        '--cov=' + PROJECT,
        '--cov-report=html',
        '--cov-report=term',
        str(TEST_PATH),
        ])

elif args.command == 'clean':
    rmtree(BUILD_PATH)
    rmtree(API_PATH)
    rmtree(BIDS_PATH)