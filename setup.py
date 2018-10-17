from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent
with (here / 'boavus' / 'VERSION').open() as f:
    VERSION = f.read().strip('\n')

with (here / 'README.rst').open(encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='boavus',
    version=VERSION,
    description='Tools to analyze data structured as BIDS in Python',
    long_description=long_description,
    url='https://github.com/gpiantoni/boavus',
    author="Gio Piantoni",
    author_email='boavus@gpiantoni.com',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='bids',
    packages=find_packages(exclude=('test', )),
    install_requires=[
        'bidso',
        'nibabel',
        'wonambi',
        'nipype',
        ],
    extras_require={
        'test': [  # to run tests
            'pytest',
            'pytest-cov',
            'codecov',
            ],
        },
    package_data={
        'boavus': [
            'VERSION',
            ],
    },
    entry_points={
        'console_scripts': [
            'boavus=boavus.command:boavus',
        ],
    },
    )
